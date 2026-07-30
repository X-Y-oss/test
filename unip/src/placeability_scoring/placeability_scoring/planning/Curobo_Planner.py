# Third Party
import numpy as np
import open3d as o3d
import time

# CuRobo
from curobo.geom.sdf.world import CollisionCheckerType
from curobo.geom.types import Cuboid, Mesh, WorldConfig
from curobo.rollout.cost.pose_cost import PoseCostMetric
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.util.logger import log_error, setup_curobo_logger
from curobo.util_file import get_robot_configs_path, join_path, load_yaml
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig, MotionGenPlanConfig
try:
    from placeability_scoring.planning.Curobo_usd_plotting import export_curobo_trajectory_to_usd
except ImportError:
    from Curobo_usd_plotting import export_curobo_trajectory_to_usd


def _path_constraint_for_axis(axis: int, constrain_orientation: bool = False):
    if axis not in (0, 1, 2):
        raise ValueError("axis must be 0 (X), 1 (Y), or 2 (Z)")
    if constrain_orientation:
        constraint = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
    else:
        constraint = [0.0, 0.0, 0.0, 0.1, 0.1, 0.1]
    constraint[3 + axis] = 0.0
    return constraint


def _pose_goalset_from_list(pose_list, tensor_args):
    pos = np.asarray(pose_list[:3], dtype=float).reshape(1, 1, 3)
    quat = np.asarray(pose_list[3:], dtype=float).reshape(1, 1, 4)
    pos_t = tensor_args.to_device(pos)
    quat_t = tensor_args.to_device(quat)
    return Pose(position=pos_t, quaternion=quat_t)


def _pose_goalset_from_poses(pose_lists, tensor_args):
    poses = np.asarray(pose_lists, dtype=float)
    if poses.ndim != 2 or poses.shape[1] != 7:
        raise ValueError(
            "Goalset segment (mode 4) expects a sequence of poses with shape [N, 7]"
        )
    pos_t = tensor_args.to_device(poses[:, :3].reshape(1, -1, 3))
    quat_t = tensor_args.to_device(poses[:, 3:].reshape(1, -1, 4))
    return Pose(position=pos_t, quaternion=quat_t)


def _pose_batch_from_poses(pose_lists, tensor_args):
    poses = np.asarray(pose_lists, dtype=float)
    if poses.ndim != 2 or poses.shape[1] != 7:
        raise ValueError("Batch segment (mode 5) expects a sequence of poses with shape [N, 7]")
    pos_t = tensor_args.to_device(poses[:, :3].reshape(-1, 1, 3))
    quat_t = tensor_args.to_device(poses[:, 3:].reshape(-1, 1, 4))
    return Pose(position=pos_t, quaternion=quat_t)


def _is_pose7(candidate):
    try:
        pose = np.asarray(candidate, dtype=float)
    except Exception:
        return False
    return pose.ndim == 1 and pose.shape[0] == 7


def _normalize_pose_lists_for_modes(pose_lists, segment_modes):
    """
    Normalize common shorthand input shapes.
    For mode 4/5/6, allow passing pose_lists=[pose1, pose2, ...] and wrap to one segment.
    """
    if pose_lists is None or segment_modes is None:
        return pose_lists
    if len(segment_modes) == 1 and segment_modes[0] in (4, 5, 6) and len(pose_lists) > 0:
        if _is_pose7(pose_lists[0]):
            return [pose_lists]
    return pose_lists


def _is_joint6(candidate):
    try:
        arr = np.asarray(candidate, dtype=float)
    except Exception:
        return False
    return arr.ndim == 1 and arr.shape[0] == 6


def _is_joint6_list(candidates):
    if not isinstance(candidates, (list, tuple)) or len(candidates) == 0:
        return False
    return all(_is_joint6(c) for c in candidates)


def _parse_mode5_entry(mode5_entry, mode_name: str = "mode 5"):
    """
    Parse mode 5 input.
    Accepted:
    1) [goal_pose_0, goal_pose_1, ...]                          (start replicated)
    2) [start_joint_or_list, [goal_pose_0, goal_pose_1, ...]]   (explicit starts)
       start_joint_or_list can be [6] or [[6], [6], ...].
    """
    explicit_starts = None
    goals = mode5_entry
    if (
        isinstance(mode5_entry, (list, tuple))
        and len(mode5_entry) == 2
        and (
            _is_joint6(mode5_entry[0])
            or _is_joint6_list(mode5_entry[0])
            or (isinstance(mode5_entry[0], np.ndarray) and np.asarray(mode5_entry[0]).shape[-1] == 6)
        )
    ):
        explicit_starts = np.asarray(mode5_entry[0], dtype=float)
        goals = mode5_entry[1]
    goals_np = np.asarray(goals, dtype=float)
    if goals_np.ndim != 2 or goals_np.shape[1] != 7:
        raise ValueError(
            f"{mode_name} expects goals as a sequence of poses with shape [N, 7], "
            "or input [[start_joints], [goal_poses]] where start_joints are [6] or [N,6]"
        )
    return explicit_starts, goals_np


def _expand_pose_entry_for_viz(entry):
    if _is_pose7(entry):
        return [list(entry)]
    if isinstance(entry, (list, tuple)) and len(entry) > 0 and all(_is_pose7(p) for p in entry):
        return [list(p) for p in entry]
    if (
        isinstance(entry, (list, tuple))
        and len(entry) == 2
        and isinstance(entry[1], (list, tuple))
        and len(entry[1]) > 0
        and all(_is_pose7(p) for p in entry[1])
    ):
        return [list(p) for p in entry[1]]
    return []


def _prepare_visualization_poses(pose_lists):
    if not pose_lists:
        return None, []
    extras = []
    for entry in pose_lists[:-1]:
        extras.extend(_expand_pose_entry_for_viz(entry))
    last_candidates = _expand_pose_entry_for_viz(pose_lists[-1])
    if not last_candidates:
        all_candidates = []
        for entry in pose_lists:
            all_candidates.extend(_expand_pose_entry_for_viz(entry))
        if not all_candidates:
            return None, extras
        return all_candidates[-1], all_candidates[:-1]
    goal_pose = last_candidates[-1]
    extras.extend(last_candidates[:-1])
    return goal_pose, extras


def _quat_multiply(q1, q2):
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array(
        [
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        ],
        dtype=float,
    )


def rotate_pose_local(pose_list, axis_xyz, angle_deg):
    """Rotate pose orientation about a local axis (post-multiply)."""
    axis = np.asarray(axis_xyz, dtype=float)
    axis_norm = np.linalg.norm(axis)
    if axis_norm < 1e-8:
        raise ValueError("axis_xyz must be non-zero")
    axis = axis / axis_norm
    angle_rad = np.deg2rad(angle_deg)
    half = 0.5 * angle_rad
    q_rot = np.array([np.cos(half), *(np.sin(half) * axis)], dtype=float)
    q_pose = np.asarray(pose_list[3:], dtype=float)
    q_new = _quat_multiply(q_pose, q_rot)
    return [pose_list[0], pose_list[1], pose_list[2], q_new[0], q_new[1], q_new[2], q_new[3]]


def _load_robot_cfg_with_attached_object(
    robot_file: str,
    parent_link_name: str = "grasp_frame",
    link_name: str = "attached_object",
    n_spheres: int = 20,
):
    cfg = load_yaml(join_path(get_robot_configs_path(), robot_file))
    if "robot_cfg" in cfg:
        cfg = cfg["robot_cfg"]
    kin = cfg["kinematics"]
    if kin.get("extra_links") is None:
        kin["extra_links"] = {}
    else:
        kin.setdefault("extra_links", {})
    kin["extra_links"][link_name] = {
        "parent_link_name": parent_link_name,
        "link_name": link_name,
        "fixed_transform": [0, 0, 0, 1, 0, 0, 0],
        "joint_type": "FIXED",
        "joint_name": "attach_joint",
    }
    if kin.get("extra_collision_spheres") is None:
        kin["extra_collision_spheres"] = {}
    else:
        kin.setdefault("extra_collision_spheres", {})
    kin["extra_collision_spheres"][link_name] = n_spheres
    kin.setdefault("collision_link_names", [])
    if link_name not in kin["collision_link_names"]:
        kin["collision_link_names"].append(link_name)
    kin.setdefault("self_collision_buffer", {})
    if link_name not in kin["self_collision_buffer"]:
        kin["self_collision_buffer"][link_name] = 0.0
    # add attached_object to self-collision ignore lists for gripper links if present
    gripper_links = [
        "tool0",
        "robotiq_arg2f_base_link",
        "left_outer_knuckle",
        "left_inner_knuckle",
        "left_outer_finger",
        "left_inner_finger",
        "left_inner_finger_pad",
        "right_outer_knuckle",
        "right_inner_knuckle",
        "right_outer_finger",
        "right_inner_finger",
        "right_inner_finger_pad",
    ]
    kin.setdefault("self_collision_ignore", {})
    for ln in gripper_links:
        if ln in kin["self_collision_ignore"]:
            if link_name not in kin["self_collision_ignore"][ln]:
                kin["self_collision_ignore"][ln].append(link_name)
    return cfg


def _attach_box_to_robot(
    motion_gen: MotionGen,
    joint_state: JointState,
    dims,
    offset_pose_list,
    link_name: str = "attached_object",
):
    dims = np.asarray(dims, dtype=float).reshape(-1)
    if dims.shape[0] != 3:
        raise ValueError("box_dims must contain exactly three values: [x, y, z]")
    if np.any(dims <= 0.0):
        raise ValueError("box_dims must be strictly positive")

    ee_pose = motion_gen.compute_kinematics(joint_state).ee_pose
    offset_pose = Pose.from_list(list(offset_pose_list), tensor_args=motion_gen.tensor_args)
    obj_pose = ee_pose.multiply(offset_pose)
    box = Cuboid(
        name="attached_box",
        dims=dims.tolist(),
        pose=obj_pose.tolist(),
        color=[0.2, 0.8, 0.2, 1.0],
    )
    motion_gen.attach_external_objects_to_robot(
        joint_state=joint_state,
        external_objects=[box],
        link_name=link_name,
    )

def _stack_trajectories(prev_traj, next_traj, snap=True, snap_tol=1e-4):
    if prev_traj is None:
        return next_traj
    if next_traj is None:
        return prev_traj
    if next_traj.position.shape[-2] == 0:
        return prev_traj

    last_prev = prev_traj.position[-1]
    first_next = next_traj.position[0]
    delta = (first_next - last_prev).abs().max().item()
    if delta > snap_tol:
        print(f"[warn] segment boundary jump (max |dq|={delta:.6f}), snapping first point")
        if snap:
            next_traj = next_traj.clone()
            next_traj.position[0] = last_prev
            if next_traj.velocity is not None:
                next_traj.velocity[0] = 0.0
            if next_traj.acceleration is not None:
                next_traj.acceleration[0] = 0.0
            if next_traj.jerk is not None:
                next_traj.jerk[0] = 0.0
    else:
        # drop duplicate first point to keep smoothness
        if next_traj.position.shape[-2] > 1:
            next_traj = next_traj.trim_trajectory(1, None)

    return prev_traj.stack(next_traj)


def _cartesian_hold_metric(
    motion_gen: MotionGen,
    start_pose: Pose,
    goal_pose: Pose,
    hold_orientation: bool = False,
    axis_tol: float = 1e-4,
):
    hold = motion_gen.tensor_args.to_device([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    if hold_orientation:
        hold[:3] = 1.0
    delta = (goal_pose.position - start_pose.position).abs()
    for ax in range(3):
        if delta[..., ax].max().item() <= axis_tol:
            hold[3 + ax] = 1.0
    if float(hold.sum()) == 0.0:
        return None
    return PoseCostMetric(
        hold_partial_pose=True,
        hold_vec_weight=hold,
        project_to_goal_frame=False,
    )


def _batch_axis_constraint_metric(
    motion_gen: MotionGen,
    free_axis: int,
    hold_orientation: bool = False,
    project_to_goal_frame: bool = False,
    hold_weight: float = 0.8,
    skip_strict_validity_check: bool = True,
):
    hold_vec = np.asarray(
        _path_constraint_for_axis(free_axis, constrain_orientation=hold_orientation), dtype=float
    )
    if hold_weight < 0.0:
        raise ValueError("hold_weight must be >= 0.0")
    hold_vec[hold_vec > 0.0] = hold_weight
    return PoseCostMetric(
        hold_partial_pose=True,
        hold_vec_weight=motion_gen.tensor_args.to_device(hold_vec),
        project_to_goal_frame=project_to_goal_frame,
        # CuRobo checks strict held-axis equality (5mm) only when offset_tstep_fraction < 0.
        # For batched constrained segments we relax this pre-check and let trajopt handle costs.
        offset_tstep_fraction=(0.0 if skip_strict_validity_check else -1.0),
    )

def plan_mixed_segments(
    motion_gen: MotionGen,
    pose_lists,
    segment_modes,
    project_to_goal_frame=False,
    constrain_orientation=False,
    cartesian_step=0.01,
    cartesian_hold_axes=True,
    constrained_batch_axis=2,
    constrained_batch_project_to_goal_frame=None,
    start_state: JointState | None = None,
    grasp_retract_offset=None,
    grasp_retract_offsets=None,
    grasp_retract_constraint_in_goal_frame=True,
    grasp_approach_offset=None,
    grasp_approach_constraint_in_goal_frame=True,
    grasp_approach_path_constraint=(0.1, 0.1, 0.1, 0.0, 0.1, 0.1),
    retract_path_constraint=(0.1, 0.1, 0.1, 0.0, 0.1, 0.1),
    snap_stack=True,
    snap_tol=1e-4,
    grasp_prepose_motion=False,
    debug_jumps=False,
    attach_box=False,
    attach_after_index=None,
    detach_after_index=None,
    box_dims=(0.05, 0.05, 0.10),
    box_offset_pose=(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0),
    attach_link_name="attached_object",
    # Backward compatibility with older cylinder API:
    attach_cylinder=None,
    cylinder_radius=None,
    cylinder_height=None,
    cylinder_offset_pose=None,
    metadata_out=None,
):
    if metadata_out is not None:
        metadata_out.clear()
        metadata_out["goal_indices_global"] = None

    if attach_cylinder is not None:
        attach_box = bool(attach_cylinder)
    if (cylinder_radius is None) ^ (cylinder_height is None):
        raise ValueError("cylinder_radius and cylinder_height must be provided together")
    if cylinder_radius is not None:
        box_dims = (
            2.0 * float(cylinder_radius),
            2.0 * float(cylinder_radius),
            float(cylinder_height),
        )
    if cylinder_offset_pose is not None:
        box_offset_pose = cylinder_offset_pose

    pose_lists = _normalize_pose_lists_for_modes(pose_lists, segment_modes)

    if len(pose_lists) < 1:
        raise ValueError("pose_lists must contain at least one target pose")
    if len(segment_modes) != len(pose_lists):
        raise ValueError("segment_modes must be same length as pose_lists")
    if any(m == 7 for m in segment_modes):
        raise ValueError(
            "Modes were remapped. Use mode 4 for goalset (old 6), mode 5 for batch (old 7), "
            "and mode 6 for constrained batch."
        )

    # Constrained batch axis can be:
    # - int: one axis for all mode-6 segments
    # - sequence len == len(segment_modes): axis per segment index
    # - sequence len == count(mode==6): axis per constrained-batch segment, in order
    mode6_indices = [idx for idx, m in enumerate(segment_modes) if m == 6]
    scalar_axis = None
    per_segment_axes = None
    per_mode6_axes = None
    if isinstance(constrained_batch_axis, (list, tuple, np.ndarray)):
        axis_arr = np.asarray(constrained_batch_axis).reshape(-1)
        if axis_arr.size == len(segment_modes):
            per_segment_axes = [int(a) for a in axis_arr.tolist()]
        elif axis_arr.size == len(mode6_indices):
            per_mode6_axes = {
                seg_idx: int(axis_arr[k]) for k, seg_idx in enumerate(mode6_indices)
            }
        else:
            raise ValueError(
                "constrained_batch_axis sequence length must be either "
                f"len(segment_modes)={len(segment_modes)} or "
                f"number_of_mode6_segments={len(mode6_indices)}"
            )
    else:
        scalar_axis = int(constrained_batch_axis)

    def _axis_for_segment(seg_idx: int) -> int:
        if per_segment_axes is not None:
            axis = int(per_segment_axes[seg_idx])
        elif per_mode6_axes is not None:
            if seg_idx not in per_mode6_axes:
                raise ValueError(
                    f"Missing constrained_batch_axis entry for mode-6 segment index {seg_idx}"
                )
            axis = int(per_mode6_axes[seg_idx])
        else:
            axis = int(scalar_axis)
        if axis not in (0, 1, 2):
            raise ValueError(
                f"constrained_batch_axis for segment index {seg_idx} must be 0, 1, or 2; got {axis}"
            )
        return axis

    # Constrained-batch frame projection can be:
    # - None: use project_to_goal_frame for all mode-6 segments
    # - bool: one value for all mode-6 segments
    # - sequence len == len(segment_modes): value per segment index
    # - sequence len == count(mode==6): value per mode-6 segment, in order
    scalar_project_to_goal_frame = bool(project_to_goal_frame)
    per_segment_project_to_goal_frame = None
    per_mode6_project_to_goal_frame = None
    if constrained_batch_project_to_goal_frame is not None:
        if isinstance(constrained_batch_project_to_goal_frame, (list, tuple, np.ndarray)):
            project_arr = np.asarray(constrained_batch_project_to_goal_frame).reshape(-1)
            if project_arr.size == len(segment_modes):
                per_segment_project_to_goal_frame = [bool(v) for v in project_arr.tolist()]
            elif project_arr.size == len(mode6_indices):
                per_mode6_project_to_goal_frame = {
                    seg_idx: bool(project_arr[k]) for k, seg_idx in enumerate(mode6_indices)
                }
            elif project_arr.size == 1:
                scalar_project_to_goal_frame = bool(project_arr[0])
            else:
                raise ValueError(
                    "constrained_batch_project_to_goal_frame sequence length must be either "
                    f"len(segment_modes)={len(segment_modes)} or "
                    f"number_of_mode6_segments={len(mode6_indices)}"
                )
        else:
            scalar_project_to_goal_frame = bool(constrained_batch_project_to_goal_frame)

    def _project_to_goal_frame_for_segment(seg_idx: int) -> bool:
        if per_segment_project_to_goal_frame is not None:
            return bool(per_segment_project_to_goal_frame[seg_idx])
        if per_mode6_project_to_goal_frame is not None:
            if seg_idx not in per_mode6_project_to_goal_frame:
                raise ValueError(
                    f"Missing constrained_batch_project_to_goal_frame entry for mode-6 segment index {seg_idx}"
                )
            return bool(per_mode6_project_to_goal_frame[seg_idx])
        return bool(scalar_project_to_goal_frame)

    full_traj = None
    segment_end_indices = []
    curr_state = None
    attach_indices = []
    detach_indices = []
    if attach_after_index is not None:
        attach_indices = (
            list(attach_after_index)
            if isinstance(attach_after_index, (list, tuple))
            else [attach_after_index]
        )
    if detach_after_index is not None:
        detach_indices = (
            list(detach_after_index)
            if isinstance(detach_after_index, (list, tuple))
            else [detach_after_index]
        )

    for i, pose_list in enumerate(pose_lists):
        mode = segment_modes[i]

        if i == 0 and curr_state is None:
            if start_state is not None:
                curr_state = start_state
            else:
                retract_cfg = motion_gen.get_retract_config()
                curr_state = JointState.from_position(retract_cfg.view(1, -1).clone())

        if mode == 0:
            target = np.asarray(pose_list, dtype=float).reshape(-1)
            plan_cfg = MotionGenPlanConfig(max_attempts=3)
            if target.shape[0] == 7:
                goal_pose = Pose.from_list(target.tolist(), tensor_args=motion_gen.tensor_args)
                result = motion_gen.plan_single(curr_state, goal_pose, plan_cfg)
                if not result.success:
                    print(f"Normal segment failed: {result.status}")
                    return None, None
                seg_traj = result.get_interpolated_plan()
            elif target.shape[0] == 6:
                goal_state = JointState.from_position(
                    motion_gen.tensor_args.to_device(target.reshape(1, -1)),
                    joint_names=motion_gen.joint_names,
                )
                result = motion_gen.plan_single_js(curr_state, goal_state, plan_cfg)
                if not result.success:
                    print(f"Joint segment failed: {result.status}")
                    return None, None
                seg_traj = result.get_interpolated_plan()
            else:
                raise ValueError("Mode 0 expects either a 7-element pose or a 6-element joint goal")
        elif mode == 1:
            goal_pose = Pose.from_list(list(pose_list), tensor_args=motion_gen.tensor_args)
            # if i == 0:
            #     log_error("Cartesian segment cannot be the first segment")
            #     return None, None
            start_pose = motion_gen.rollout_fn.compute_kinematics(curr_state).ee_pose
            metric = None
            if cartesian_hold_axes:
                metric = _cartesian_hold_metric(
                    motion_gen,
                    start_pose,
                    goal_pose,
                    hold_orientation=constrain_orientation,
                    axis_tol=1e-4,
                )
            plan_cfg = MotionGenPlanConfig(
                max_attempts=3,
                enable_finetune_trajopt=False,
                pose_cost_metric=metric,
            )
            result = motion_gen.plan_single(curr_state, goal_pose, plan_cfg)
            if not result.success:
                print(f"Cartesian segment failed: {result.status}")
                return None, None
            seg_traj = result.get_interpolated_plan()
        elif mode == 2 or mode == 3:
            goal_pose = Pose.from_list(list(pose_list), tensor_args=motion_gen.tensor_args)
            plan_cfg = MotionGenPlanConfig(False, True, max_attempts=3)
            goal_pose_goalset = _pose_goalset_from_list(pose_list, motion_gen.tensor_args)
            if grasp_approach_offset is not None:
                approach_offset = Pose.from_list(
                    list(grasp_approach_offset), tensor_args=motion_gen.tensor_args
                )
            else:
                approach_offset = Pose.from_list(
                    [-0.10, 0, 0.0, 1, 0, 0, 0], tensor_args=motion_gen.tensor_args
                )
            # per-grasp retract override
            if grasp_retract_offsets is not None and grasp_retract_offsets[i] is not None:
                effective_retract_offset = grasp_retract_offsets[i]
            else:
                effective_retract_offset = grasp_retract_offset
            if mode == 3 and effective_retract_offset is None:
                effective_retract_offset = [0.0, 0.0, -0.10, 1.0, 0.0, 0.0, 0.0]
            # Optionally insert an explicit normal-motion pre-grasp segment
            if grasp_prepose_motion:
                if grasp_approach_constraint_in_goal_frame:
                    approach_pose = goal_pose.clone().multiply(approach_offset)
                else:
                    approach_pose = approach_offset.clone().multiply(goal_pose.clone())
                pre_cfg = MotionGenPlanConfig(max_attempts=3)
                pre_result = motion_gen.plan_single(curr_state, approach_pose, pre_cfg)
                if not pre_result.success:
                    print(f"Pre-grasp segment failed: {pre_result.status}")
                    return None, None
                pre_traj = pre_result.get_interpolated_plan()
                if full_traj is None:
                    full_traj = pre_traj
                else:
                    full_traj = _stack_trajectories(
                        full_traj, pre_traj, snap=snap_stack, snap_tol=snap_tol
                    )
                last_pos = pre_traj.position[-1].view(1, -1)
                curr_state = JointState.from_position(last_pos, joint_names=pre_traj.joint_names)
            result = motion_gen.plan_grasp(
                curr_state,
                goal_pose_goalset,
                plan_cfg,
                grasp_approach_offset=approach_offset,
                grasp_approach_path_constraint=list(grasp_approach_path_constraint),
                grasp_approach_constraint_in_goal_frame=grasp_approach_constraint_in_goal_frame,
                plan_grasp_to_retract=effective_retract_offset is not None,
                retract_offset=(
                    Pose.from_list(list(effective_retract_offset), tensor_args=motion_gen.tensor_args)
                    if effective_retract_offset is not None
                    else None
                ),
                retract_path_constraint=list(retract_path_constraint),
                retract_constraint_in_goal_frame=grasp_retract_constraint_in_goal_frame,
            )
            if not result.success.item():
                print(f"Grasp segment failed: {result.status}")
                return None, None
            if (
                effective_retract_offset is not None
                and result.retract_interpolated_trajectory is not None
            ):
                seg_traj = result.grasp_interpolated_trajectory.stack(
                    result.retract_interpolated_trajectory
                )
            else:
                seg_traj = result.grasp_interpolated_trajectory
        elif mode == 4:
            plan_cfg = MotionGenPlanConfig(max_attempts=3)
            goal_pose_goalset = _pose_goalset_from_poses(pose_list, motion_gen.tensor_args)
            result = motion_gen.plan_goalset(curr_state, goal_pose_goalset, plan_cfg)
            success = result.success.item() if hasattr(result.success, "item") else bool(result.success)
            if not success:
                print(f"Goalset segment failed: {result.status}")
                return None, None
            seg_traj = result.get_interpolated_plan()
        elif mode == 5 or mode == 6:
            constrained_batch = mode == 6
            mode_label = "mode 6" if constrained_batch else "mode 5"
            plan_cfg = MotionGenPlanConfig(max_attempts=3)
            if constrained_batch:
                axis_i = _axis_for_segment(i)
                plan_cfg.pose_cost_metric = _batch_axis_constraint_metric(
                    motion_gen,
                    free_axis=axis_i,
                    hold_orientation=constrain_orientation,
                    project_to_goal_frame=_project_to_goal_frame_for_segment(i),
                )
            explicit_starts, goals_np = _parse_mode5_entry(pose_list, mode_name=mode_label)
            goal_pose_batch = _pose_batch_from_poses(goals_np, motion_gen.tensor_args)
            goal_count = int(goal_pose_batch.batch)

            start_pos = curr_state.position
            if start_pos.ndim == 1:
                start_pos = start_pos.view(1, -1)

            if explicit_starts is not None:
                start_np = np.asarray(explicit_starts, dtype=float)
                if start_np.ndim == 1:
                    if start_np.shape[0] != 6:
                        raise ValueError(f"{mode_label} explicit start joints must have 6 values")
                    start_np = start_np.reshape(1, 6)
                elif start_np.ndim == 2 and start_np.shape[1] == 6:
                    pass
                else:
                    raise ValueError(f"{mode_label} explicit start joints must be [6] or [N,6]")
                if start_np.shape[0] == 1:
                    start_pos = motion_gen.tensor_args.to_device(start_np).repeat(goal_count, 1)
                elif start_np.shape[0] == goal_count:
                    start_pos = motion_gen.tensor_args.to_device(start_np)
                else:
                    raise ValueError(
                        f"{mode_label} start joint count ({start_np.shape[0]}) must be 1 or match goals ({goal_count})"
                    )
            elif start_pos.shape[0] == 1:
                start_pos = start_pos.repeat(goal_count, 1)
            elif start_pos.shape[0] != goal_count:
                raise ValueError(
                    f"{mode_label} start state batch ({start_pos.shape[0]}) must match goal batch ({goal_count})"
                )
            batch_start = JointState.from_position(start_pos, joint_names=curr_state.joint_names)
            print(
                f"[{mode_label}] plan_batch: start_batch={tuple(batch_start.position.shape)}, "
                f"goal_pos_batch={tuple(goal_pose_batch.position.shape)}, "
                f"goal_quat_batch={tuple(goal_pose_batch.quaternion.shape)}"
            )
            result = motion_gen.plan_batch(batch_start, goal_pose_batch, plan_cfg)
            success_mask = result.success.view(-1)
            if int(success_mask.sum().item()) == 0:
                print(f"Batch segment failed: {result.status}")
                return None, None
            #all_paths = result.get_paths()
            if goal_count == 1:
                all_paths = [result.get_interpolated_plan()]
            else:
                all_paths = result.get_paths()
            success_indices_global = [
                idx for idx in range(len(all_paths)) if bool(success_mask[idx].item())
            ]
            print(f"[batch-index] segment {i} success global indices: {success_indices_global}")
            batch_paths = [all_paths[idx] for idx in success_indices_global]
            if len(batch_paths) == 0:
                print("Batch segment produced no successful paths")
                return None, None

            head_paths = []
            head_seg_indices = []
            for path in batch_paths:
                if full_traj is None:
                    combined = path
                else:
                    combined = _stack_trajectories(
                        full_traj, path, snap=snap_stack, snap_tol=snap_tol
                    )
                head_paths.append(combined)
                head_seg_indices.append(
                    list(segment_end_indices) + [combined.position.shape[-2] - 1]
                )

            # Track indices w.r.t. original M goals from the first batch segment.
            # This is kept aligned with head_paths order.
            head_goal_indices_global = list(success_indices_global)

            if i == len(pose_lists) - 1:
                if metadata_out is not None:
                    metadata_out["goal_indices_global"] = list(head_goal_indices_global)
                return head_paths, head_seg_indices

            # Non-recursive chaining for later batch segments: keep batch index pairing.
            curr_paths = head_paths
            curr_seg_indices = head_seg_indices
            curr_goal_indices_global = head_goal_indices_global
            base_goal_count = goal_count
            for j in range(i + 1, len(pose_lists)):
                next_mode = segment_modes[j]
                if next_mode not in (5, 6):
                    raise ValueError(
                        f"After {mode_label}, only mode 5 or mode 6 is supported in non-recursive batching"
                    )
                next_mode_label = "mode 6" if next_mode == 6 else "mode 5"
                next_constrained = next_mode == 6

                next_plan_cfg = MotionGenPlanConfig(max_attempts=3)
                if next_constrained:
                    axis_j = _axis_for_segment(j)
                    next_plan_cfg.pose_cost_metric = _batch_axis_constraint_metric(
                        motion_gen,
                        free_axis=axis_j,
                        hold_orientation=constrain_orientation,
                        project_to_goal_frame=_project_to_goal_frame_for_segment(j),
                    )
                next_explicit_starts, next_goals_np = _parse_mode5_entry(
                    pose_lists[j], mode_name=next_mode_label
                )
                next_goal_count_full = int(next_goals_np.shape[0])
                if next_goal_count_full != base_goal_count:
                    raise ValueError(
                        f"{next_mode_label} expects full goal count M={base_goal_count}, "
                        f"got {next_goal_count_full}"
                    )
                curr_count = len(curr_paths)

                if curr_count == 0:
                    print("No batch paths available for chained batch planning")
                    return None, None

                # Select goals by the currently surviving global indices.
                # This preserves alignment across chained mode 5/6 segments.
                selected_goals_np = next_goals_np[curr_goal_indices_global]
                next_goal_pose_batch = _pose_batch_from_poses(selected_goals_np, motion_gen.tensor_args)
                selected_goal_count = int(next_goal_pose_batch.batch)
                if selected_goal_count != curr_count:
                    raise ValueError(
                        f"{next_mode_label} internal mismatch: selected goals ({selected_goal_count}) "
                        f"must match current survivors ({curr_count})"
                    )
                print(
                    f"[batch-index] segment {j} using global indices: {curr_goal_indices_global}"
                )

                if next_explicit_starts is not None:
                    start_np = np.asarray(next_explicit_starts, dtype=float)
                    if start_np.ndim == 1:
                        if start_np.shape[0] != 6:
                            raise ValueError(f"{next_mode_label} explicit start joints must have 6 values")
                        start_np = start_np.reshape(1, 6)
                    elif start_np.ndim == 2 and start_np.shape[1] == 6:
                        pass
                    else:
                        raise ValueError(f"{next_mode_label} explicit start joints must be [6] or [N,6]")

                    if start_np.shape[0] == 1:
                        next_start_pos = motion_gen.tensor_args.to_device(start_np).repeat(
                            curr_count, 1
                        )
                    elif start_np.shape[0] == curr_count:
                        # Already aligned with currently surviving candidates.
                        next_start_pos = motion_gen.tensor_args.to_device(start_np)
                    elif start_np.shape[0] == base_goal_count:
                        # Full-M explicit starts: select current survivors by global indices.
                        next_start_pos = motion_gen.tensor_args.to_device(
                            start_np[curr_goal_indices_global]
                        )
                    else:
                        raise ValueError(
                            f"{next_mode_label} explicit start count ({start_np.shape[0]}) must be 1, "
                            f"current survivors ({curr_count}), or full M ({base_goal_count})"
                        )
                else:
                    # Default: continue one-to-one from previous surviving paths.
                    start_np = np.stack(
                        [
                            p.position[-1].detach().cpu().numpy()
                            for p in curr_paths
                        ],
                        axis=0,
                    )
                    next_start_pos = motion_gen.tensor_args.to_device(start_np)

                next_batch_start = JointState.from_position(
                    next_start_pos, joint_names=curr_paths[0].joint_names
                )
                print(
                    f"[{next_mode_label}] chained plan_batch: start_batch={tuple(next_batch_start.position.shape)}, "
                    f"goal_pos_batch={tuple(next_goal_pose_batch.position.shape)}, "
                    f"goal_quat_batch={tuple(next_goal_pose_batch.quaternion.shape)}"
                )
                # next_result = motion_gen.plan_batch(
                #     next_batch_start, next_goal_pose_batch, next_plan_cfg
                # )
                try:
                    next_result = motion_gen.plan_batch(next_batch_start, next_goal_pose_batch, next_plan_cfg)
                except RuntimeError as e:
                    msg = str(e)
                    if "shape mismatch" in msg and "cannot be broadcast" in msg:
                        print(f"Batch replanning mismatch: {e}")
                        return None, None
                    raise
                next_success_mask = next_result.success.view(-1)
                if int(next_success_mask.sum().item()) == 0:
                    print(f"Batch segment failed: {next_result.status}")
                    return None, None

                #next_all_paths = next_result.get_paths()
                print(f"selected_goal_count: {selected_goal_count}")
                if selected_goal_count == 1:
                    next_all_paths = [next_result.get_interpolated_plan()]
                else:
                    next_all_paths = next_result.get_paths()
                next_paths = []
                next_seg_indices = []
                next_goal_indices_global = []
                for k in range(min(len(next_all_paths), curr_count)):
                    if not bool(next_success_mask[k].item()):
                        continue
                    combined = _stack_trajectories(
                        curr_paths[k], next_all_paths[k], snap=snap_stack, snap_tol=snap_tol
                    )
                    next_paths.append(combined)
                    next_seg_indices.append(
                        list(curr_seg_indices[k]) + [combined.position.shape[-2] - 1]
                    )
                    next_goal_indices_global.append(curr_goal_indices_global[k])

                if len(next_paths) == 0:
                    print("Batch segment produced no successful paired paths")
                    return None, None
                print(
                    f"[batch-index] segment {j} survived global indices: {next_goal_indices_global}"
                )
                curr_paths = next_paths
                curr_seg_indices = next_seg_indices
                curr_goal_indices_global = next_goal_indices_global

            if metadata_out is not None:
                metadata_out["goal_indices_global"] = list(curr_goal_indices_global)
            return curr_paths, curr_seg_indices
        else:
            raise ValueError(
                "segment_modes must be 0 (pose/joint), 1 (cartesian), 2 (grasp), "
                "3 (grasp+retreat), 4 (goalset), 5 (batch), or 6 (constrained batch)"
            )

        if full_traj is None:
            full_traj = seg_traj
        else:
            full_traj = _stack_trajectories(
                full_traj, seg_traj, snap=snap_stack, snap_tol=snap_tol
            )

        last_pos = seg_traj.position[-1].view(1, -1)
        curr_state = JointState.from_position(last_pos, joint_names=seg_traj.joint_names)
        segment_end_indices.append(full_traj.position.shape[-2] - 1)

        # attach/detach after reaching a pose index
        if attach_box and i in attach_indices:
            _attach_box_to_robot(
                motion_gen,
                curr_state,
                dims=box_dims,
                offset_pose_list=box_offset_pose,
                link_name=attach_link_name,
            )
        if attach_box and i in detach_indices:
            motion_gen.detach_object_from_robot(link_name=attach_link_name)

    if debug_jumps and full_traj is not None:
        dq = (full_traj.position[1:] - full_traj.position[:-1]).abs().max(dim=-1).values
        max_dq = dq.max().item()
        idx = int(dq.argmax().item())
        print(f"[debug] max joint step = {max_dq:.6f} at index {idx}")

    return full_traj, segment_end_indices


def _quat_wxyz_to_rotmat(qw, qx, qy, qz):
    xx = qx * qx
    yy = qy * qy
    zz = qz * qz
    xy = qx * qy
    xz = qx * qz
    yz = qy * qz
    wx = qw * qx
    wy = qw * qy
    wz = qw * qz
    return np.array(
        [
            [1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz), 2.0 * (xz + wy)],
            [2.0 * (xy + wz), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx)],
            [2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (xx + yy)],
        ],
        dtype=float,
    )


def _pose_list_to_matrix(pose_list):
    if len(pose_list) != 7:
        raise ValueError("Expected pose list [x,y,z,qw,qx,qy,qz]")
    x, y, z, qw, qx, qy, qz = pose_list
    rot = _quat_wxyz_to_rotmat(qw, qx, qy, qz)
    mat = np.eye(4, dtype=float)
    mat[:3, :3] = rot
    mat[:3, 3] = [x, y, z]
    return mat


def visualize_goal(
    goal_pose_list,
    frame_size=0.1,
    extra_pose_lists=None,
):

    world_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=frame_size)

    geoms = [world_frame]

    def add_pose_frame(pose_list, color):
        pose_mat = _pose_list_to_matrix(pose_list)
        frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=frame_size)
        frame.transform(pose_mat)
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=frame_size * 0.2)
        sphere.paint_uniform_color(color)
        sphere.translate(pose_mat[:3, 3])
        geoms.extend([frame, sphere])

    # goal in red
    add_pose_frame(goal_pose_list, [1.0, 0.2, 0.2])
    if extra_pose_lists:
        colors = [
            [0.2, 1.0, 0.2],
            [0.2, 0.6, 1.0],
            [1.0, 0.6, 0.2],
            [0.8, 0.2, 1.0],
        ]
        for i, pose_list in enumerate(extra_pose_lists):
            add_pose_frame(pose_list, colors[i % len(colors)])

    o3d.visualization.draw_geometries(geoms)


def o3dmesh_to_curobomesh(o3d_mesh, name="o3d_world_mesh", pose=None, color=(0.6, 0.6, 0.9, 1.0)):
    """Convert an Open3D TriangleMesh into a CuRobo Mesh obstacle."""
    if o3d_mesh is None or o3d_mesh.is_empty():
        raise ValueError("Open3D mesh is empty.")
    if not o3d_mesh.has_triangles():
        raise ValueError("Open3D mesh has no triangles.")
    if not o3d_mesh.has_vertex_normals():
        o3d_mesh.compute_vertex_normals()

    vertices = np.asarray(o3d_mesh.vertices, dtype=float)
    faces = np.asarray(o3d_mesh.triangles, dtype=np.int32)
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError(f"Expected mesh vertices shape [N,3], got {vertices.shape}")
    if faces.ndim != 2 or faces.shape[1] != 3:
        raise ValueError(f"Expected mesh triangles shape [M,3], got {faces.shape}")

    return Mesh(
        name=name,
        pose=[0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0] if pose is None else list(pose),
        vertices=vertices,
        faces=faces,
        color=list(color),
    )


def build_world_from_open3d_mesh(o3d_mesh, name="o3d_world", pose=None):
    """Build a CuRobo WorldConfig from an Open3D TriangleMesh."""
    if not o3d_mesh.has_vertex_normals():
        o3d_mesh.compute_vertex_normals()
    curobo_mesh = o3dmesh_to_curobomesh(o3d_mesh, name=name, pose=pose)
    verts = np.asarray(o3d_mesh.vertices, dtype=float)
    return WorldConfig(mesh=[curobo_mesh]), verts


def build_world_from_open3d_mesh_file(mesh_path, name="o3d_world", pose=None):
    """Load an Open3D mesh file and convert it into a CuRobo planning world."""
    o3d_mesh = o3d.io.read_triangle_mesh(mesh_path)
    if o3d_mesh is None or o3d_mesh.is_empty():
        raise ValueError(f"Failed to load mesh or mesh is empty: {mesh_path}")
    if not o3d_mesh.has_vertex_normals():
        o3d_mesh.compute_vertex_normals()
    return build_world_from_open3d_mesh(o3d_mesh, name=name, pose=pose)


class Curobo_Planner:
    def __init__(
        self,
        world_cfg: WorldConfig,
        robot_file: str = "ur5e_robotiq_2f_85.yml",
        attach_box: bool = False,
        attach_link_name: str = "attached_object",
        interpolation_dt: float = 0.01,
        use_cuda_graph: bool = False,
        # Backward compatibility:
        attach_cylinder: bool | None = None,
    ):
        if attach_cylinder is not None:
            attach_box = bool(attach_cylinder)
        self.world_cfg = world_cfg
        self.robot_file = robot_file
        self.interpolation_dt = interpolation_dt
        self.attach_box = attach_box
        self.attach_cylinder = attach_box  # legacy alias
        self.attach_link_name = attach_link_name
        self._current_joint_pos = None
        self._current_joint_names = None
        if attach_box:
            robot_cfg = _load_robot_cfg_with_attached_object(
                robot_file, parent_link_name="grasp_frame", link_name=attach_link_name
            )
        else:
            robot_cfg = robot_file
            
        start = time.time()
        self.motion_gen_config = MotionGenConfig.load_from_robot_config(
            robot_cfg,
            world_cfg,
            collision_checker_type=CollisionCheckerType.MESH,
            interpolation_dt=interpolation_dt,
            use_cuda_graph=use_cuda_graph,
        )
        self.motion_gen = MotionGen(self.motion_gen_config)
        self.motion_gen.warmup()
        print(f"Motion_gen warmup time: {time.time() - start}")
        # Keep last raw CuRobo plan so callers can export a selected batch index later.
        self._last_traj = None
        self._last_seg_end_indices = None
        self._last_goal_indices_global = None
        self._last_export_original_goal_index = None
        self._last_visual_box_export_cfg = None

    def set_current_joint_state(self, joint_positions, joint_names=None):
        """Set current joint angles (radians) to use as the planning start state."""
        pos = np.asarray(joint_positions, dtype=float).reshape(1, -1)
        self._current_joint_pos = pos
        self._current_joint_names = joint_names
        
    def get_current_joint_state(self):
        return self._current_joint_pos

    def _get_start_state(self) -> JointState:
        if self._current_joint_pos is not None:
            pos_t = self.motion_gen.tensor_args.to_device(self._current_joint_pos)
            return JointState.from_position(pos_t, joint_names=self._current_joint_names)
        retract_cfg = self.motion_gen.get_retract_config()
        return JointState.from_position(retract_cfg.view(1, -1).clone())

    def assign_world(self, world_cfg: WorldConfig):
        """Assign a new collision world to the planner."""
        self.world_cfg = world_cfg
        self.motion_gen.update_world(world_cfg)

    def load_open3d_mesh_world(
        self,
        mesh_path="/home/ws/src/placeability_scoring/placeability_scoring/test_data/place_mesh.ply",
        name="o3d_world",
        pose=None,
    ):
        """
        Load a mesh file through Open3D, convert to CuRobo WorldConfig, and update
        the active planner collision world.
        """
        world_cfg, verts = build_world_from_open3d_mesh_file(mesh_path, name=name, pose=pose)
        self.assign_world(world_cfg)
        return world_cfg, verts

    def get_last_plan_raw(self):
        """
        Return last raw CuRobo planning output.

        Returns:
            (traj, seg_end_indices)
            - traj: CuRobo trajectory object or list of trajectory objects (batch)
            - seg_end_indices: segment boundary indices matching traj
        """
        return self._last_traj, self._last_seg_end_indices

    def get_last_goal_indices_global(self):
        """
        Return mapping from returned batch trajectory index -> original goal index.
        Returns None for non-batched plans.
        """
        return self._last_goal_indices_global

    def export_last_plan_to_usd(
        self,
        trajectory_index: int = 0,
        save_path: str = "/home/ws/curobo_plan.usd",
        dt: float = None,
        return_original_goal_index: bool = False,
        visual_box_dims=None,
        visual_box_offset_pose=None,
        visual_attach_after_index=None,
        visual_detach_after_index=None,
        visual_box_parent_link: str = "grasp_frame",
        visual_box_robot_frame: str = "attached_object",
        visual_box_color=(0.2, 0.8, 0.2, 1.0),
    ):
        """
        Export cached raw plan to USD, selecting one trajectory if the cached plan is batched.
        """
        if self._last_traj is None:
            raise ValueError("No cached trajectory available. Run plan(...) first.")
        if dt is None:
            dt = self.interpolation_dt
        if self._last_visual_box_export_cfg is not None:
            if visual_box_dims is None:
                visual_box_dims = self._last_visual_box_export_cfg.get("visual_box_dims")
            if visual_box_offset_pose is None:
                visual_box_offset_pose = self._last_visual_box_export_cfg.get("visual_box_offset_pose")
            if visual_attach_after_index is None:
                visual_attach_after_index = self._last_visual_box_export_cfg.get("visual_attach_after_index")
            if visual_detach_after_index is None:
                visual_detach_after_index = self._last_visual_box_export_cfg.get("visual_detach_after_index")
            if visual_box_parent_link == "grasp_frame":
                visual_box_parent_link = self._last_visual_box_export_cfg.get(
                    "visual_box_parent_link", visual_box_parent_link
                )
            if visual_box_robot_frame == "attached_object":
                visual_box_robot_frame = self._last_visual_box_export_cfg.get(
                    "visual_box_robot_frame", visual_box_robot_frame
                )
            if visual_box_color == (0.2, 0.8, 0.2, 1.0):
                visual_box_color = self._last_visual_box_export_cfg.get(
                    "visual_box_color", visual_box_color
                )
        original_goal_index = None
        if (
            self._last_goal_indices_global is not None
            and trajectory_index >= 0
            and trajectory_index < len(self._last_goal_indices_global)
        ):
            original_goal_index = int(self._last_goal_indices_global[trajectory_index])
            print(
                f"[export] trajectory_index={trajectory_index} maps to original_goal_index={original_goal_index}"
            )
        self._last_export_original_goal_index = original_goal_index
        selected_seg_end_indices = self._last_seg_end_indices
        if isinstance(self._last_traj, list) and self._last_seg_end_indices is not None:
            if trajectory_index < 0 or trajectory_index >= len(self._last_traj):
                raise ValueError(
                    f"trajectory_index {trajectory_index} is out of range for {len(self._last_traj)} trajectories"
                )
            if (
                isinstance(self._last_seg_end_indices, list)
                and len(self._last_seg_end_indices) > 0
                and isinstance(self._last_seg_end_indices[0], (list, tuple, np.ndarray))
            ):
                selected_seg_end_indices = self._last_seg_end_indices[trajectory_index]
        exported_path = export_curobo_trajectory_to_usd(
            trajectory=self._last_traj,
            world_cfg=self.world_cfg,
            robot_file=self.robot_file,
            save_path=save_path,
            dt=dt,
            trajectory_index=trajectory_index,
            motion_gen=self.motion_gen,
            seg_end_indices=selected_seg_end_indices,
            visual_box_dims=visual_box_dims,
            visual_box_offset_pose=visual_box_offset_pose,
            visual_attach_after_index=visual_attach_after_index,
            visual_detach_after_index=visual_detach_after_index,
            visual_box_parent_link=visual_box_parent_link,
            visual_box_robot_frame=visual_box_robot_frame,
            visual_box_color=visual_box_color,
        )
        if return_original_goal_index:
            return exported_path, original_goal_index
        return exported_path

    def plan(
        self,
        pose_lists=None,
        segment_modes=None,
        visualize_frames=False,
        constrain_orientation=False,
        cartesian_hold_axes=True,
        constrained_batch_axis=2,
        constrained_batch_project_to_goal_frame=None,
        grasp_retract_offset=None,
        grasp_retract_offsets=None,
        grasp_retract_constraint_in_goal_frame=True,
        grasp_approach_offset=None,
        grasp_approach_constraint_in_goal_frame=True,
        grasp_approach_path_constraint=(0.5, 0.5, 0.5, 0.0, 0.5, 0.5),
        retract_path_constraint=(0.1, 0.1, 0.1, 0.0, 0.1, 0.1),
        project_to_goal_frame=True,
        snap_stack=True,
        snap_tol=1e-4,
        grasp_prepose_motion=False,
        debug_jumps=False,
        attach_box=None,
        attach_after_index=None,
        detach_after_index=None,
        box_dims=(0.05, 0.05, 0.10),
        box_offset_pose=(0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0),
        # Backward compatibility:
        attach_cylinder=None,
        cylinder_radius=None,
        cylinder_height=None,
        cylinder_offset_pose=None,
        export_usd=False,
        usd_save_path="/home/ws/curobo_plan.usd",
        usd_trajectory_index=0,
    ):
        if attach_cylinder is not None:
            if attach_box is None:
                attach_box = bool(attach_cylinder)
            elif bool(attach_cylinder) != bool(attach_box):
                raise ValueError("attach_box and attach_cylinder disagree")
        if attach_box is None:
            attach_box = self.attach_box
        if attach_box != self.attach_box:
            raise ValueError(
                "attach_box must match the value used to initialize Curobo_Planner"
            )
        if (cylinder_radius is None) ^ (cylinder_height is None):
            raise ValueError("cylinder_radius and cylinder_height must be provided together")
        if cylinder_radius is not None:
            box_dims = (
                2.0 * float(cylinder_radius),
                2.0 * float(cylinder_radius),
                float(cylinder_height),
            )
        if cylinder_offset_pose is not None:
            box_offset_pose = cylinder_offset_pose
        if attach_box and attach_after_index is not None:
            self._last_visual_box_export_cfg = {
                "visual_box_dims": list(np.asarray(box_dims, dtype=float).reshape(-1)),
                "visual_box_offset_pose": list(box_offset_pose),
                "visual_attach_after_index": attach_after_index,
                "visual_detach_after_index": detach_after_index,
                "visual_box_parent_link": "grasp_frame",
                "visual_box_robot_frame": self.attach_link_name,
                "visual_box_color": (0.2, 0.8, 0.2, 1.0),
            }
        else:
            self._last_visual_box_export_cfg = None

        if visualize_frames and pose_lists:
            goal_pose_list, extra_pose_lists = _prepare_visualization_poses(pose_lists)
            if goal_pose_list is not None:
                visualize_goal(
                    goal_pose_list,
                    extra_pose_lists=extra_pose_lists if extra_pose_lists else None,
                )

        start_state = self._get_start_state()
        plan_metadata = {}
        traj, seg_end_indices = plan_mixed_segments(
            self.motion_gen,
            pose_lists=pose_lists,
            segment_modes=segment_modes,
            project_to_goal_frame=project_to_goal_frame,
            constrain_orientation=constrain_orientation,
            cartesian_hold_axes=cartesian_hold_axes,
            constrained_batch_axis=constrained_batch_axis,
            constrained_batch_project_to_goal_frame=constrained_batch_project_to_goal_frame,
            start_state=start_state,
            grasp_retract_offset=grasp_retract_offset,
            grasp_retract_offsets=grasp_retract_offsets,
            grasp_retract_constraint_in_goal_frame=grasp_retract_constraint_in_goal_frame,
            grasp_approach_offset=grasp_approach_offset,
            grasp_approach_constraint_in_goal_frame=grasp_approach_constraint_in_goal_frame,
            grasp_approach_path_constraint=grasp_approach_path_constraint,
            retract_path_constraint=retract_path_constraint,
            snap_stack=snap_stack,
            snap_tol=snap_tol,
            grasp_prepose_motion=grasp_prepose_motion,
            debug_jumps=debug_jumps,
            attach_box=attach_box,
            attach_after_index=attach_after_index,
            detach_after_index=detach_after_index,
            box_dims=box_dims,
            box_offset_pose=box_offset_pose,
            attach_link_name=self.attach_link_name,
            attach_cylinder=attach_cylinder,
            cylinder_radius=cylinder_radius,
            cylinder_height=cylinder_height,
            cylinder_offset_pose=cylinder_offset_pose,
            metadata_out=plan_metadata,
        )
        if traj is None:
            print("No trajectory to save.")
            self._last_traj = None
            self._last_seg_end_indices = None
            self._last_goal_indices_global = None
            self._last_export_original_goal_index = None
            return None, None
        self._last_traj = traj
        self._last_seg_end_indices = seg_end_indices
        self._last_goal_indices_global = plan_metadata.get("goal_indices_global")
        self._last_export_original_goal_index = None
        if export_usd:
            visual_cfg = self._last_visual_box_export_cfg or {}
            export_curobo_trajectory_to_usd(
                trajectory=traj,
                world_cfg=self.world_cfg,
                robot_file=self.robot_file,
                save_path=usd_save_path,
                dt=self.interpolation_dt,
                trajectory_index=usd_trajectory_index,
                motion_gen=self.motion_gen,
                seg_end_indices=(
                    seg_end_indices[usd_trajectory_index]
                    if (
                        isinstance(traj, list)
                        and isinstance(seg_end_indices, list)
                        and len(seg_end_indices) > 0
                        and isinstance(seg_end_indices[0], (list, tuple, np.ndarray))
                    )
                    else seg_end_indices
                ),
                visual_box_dims=visual_cfg.get("visual_box_dims"),
                visual_box_offset_pose=visual_cfg.get("visual_box_offset_pose"),
                visual_attach_after_index=visual_cfg.get("visual_attach_after_index"),
                visual_detach_after_index=visual_cfg.get("visual_detach_after_index"),
                visual_box_parent_link=visual_cfg.get("visual_box_parent_link", "grasp_frame"),
                visual_box_robot_frame=visual_cfg.get("visual_box_robot_frame", self.attach_link_name),
                visual_box_color=visual_cfg.get("visual_box_color", (0.2, 0.8, 0.2, 1.0)),
            )
        return traj, seg_end_indices


if __name__ == "__main__":
    setup_curobo_logger("error")
    
    try:
        from placeability_scoring.planning.environment import make_shelf
    except ImportError:
        from environment import make_shelf
    from scipy.spatial.transform import Rotation as R

    shelf_mesh, _, _, _ = make_shelf()
    T_armbase_to_world = np.array(
        [
            [0.0, 1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, -0.720],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    t = T_armbase_to_world[:3, 3]
    quat_xyzw = R.from_matrix(T_armbase_to_world[:3, :3]).as_quat()
    scene_pose = [t[0], t[1], t[2], quat_xyzw[3], quat_xyzw[0], quat_xyzw[1], quat_xyzw[2]]
    scene_mesh = o3dmesh_to_curobomesh(shelf_mesh, name="shelf_world", pose=scene_pose)
    
    planner = Curobo_Planner(
        WorldConfig(mesh=[scene_mesh]),
        robot_file="ur5e_robotiq_2f_85.yml",
        attach_box=False,
        attach_link_name="attached_object",
    )
    
    #trajectory, segments = planner.plan(pose_lists=[[0.0, -1.5707963267948966, 0.0, 0.0, 0.0, 0.0]], segment_modes=(0,))
    
    # trajectory, segments = planner.plan(
    #     pose_lists=[
    #         [0.0, 0.5, 0.72, -0.5, 0.5, 0.5, 0.5],  # mode 0
    #         [
    #             [0.1, 0.4, 0.72, -0.5, 0.5, 0.5, 0.5],
    #             [0.2, 0.5, 0.72, -0.5, 0.5, 0.5, 0.5],
    #             [0.0, 0.7, 0.72, -0.5, 0.5, 0.5, 0.5],
    #         ],
    #         [
    #             [0.0, 0.5, 0.73, -0.5, 0.5, 0.5, 0.5],
    #             [0.0, 0.6, 0.72, -0.5, 0.5, 0.5, 0.5],
    #             [0.0, 0.4, 0.74, -0.5, 0.5, 0.5, 0.5],
    #         ],
    #     ],
    #     segment_modes=(0,5,5,),
    #     export_usd=True,
    # )
    
    
    # BENNO
    
    pose_lists = [
    [ 0.41059477,  0.08136146,  0.09680379, -0.08364487, -0.1730759 ,  0.98133419,  0.00560997],
    [ 0.31798512,  0.04729855,  0.11302631, -0.08364487, -0.1730759 ,  0.98133419,  0.00560997],
    [ 0.31798512,  0.04729855,  0.16302631, -0.08364487, -0.1730759 , 0.98133419,  0.00560997]
    ]
    pose_lists = [
        [0.5532815 , -0.05556601,  0.14578822,  0.05795722, -0.21381614, 0.9748617 , -0.0238388 ],
        [ 0.64346623, -0.01360145,  0.15606885,  0.05795722, -0.21381614, 0.9748617 , -0.0238388 ],
        [ 0.64346623, -0.01360145,  0.20606885,  0.05795722, -0.21381614, 0.9748617 , -0.0238388 ]]

    # towards bottle, x forward, z up, y right, camera downward direciton
    pose_lists = [[ 0.56168133, -0.07128069,  0.14536684,  0.05997077, -0.25833315,
        0.96396343, -0.02102352], [ 0.64761483, -0.02122379,  0.15584256,  0.05997077, -0.25833315,
        0.96396343, -0.02102352], [ 0.64761483, -0.02122379,  0.20584256,  0.05997077, -0.25833315,
        0.96396343, -0.02102352]]
    
    pose_lists = [np.array([[-0.85230134, -0.51508035,  0.09096513,  0.49285624],
                [-0.50840007,  0.85667728  ,0.08736939  ,0.1112125 ],
                [ 0.12293002, -0.02821837 , 0.99201408 , 0.12256133],
                [ 0.    ,      0.     ,     0.  ,        1.        ]]),
                np.array([[-0.85230134, -0.51508035 ,  0.09096513 , 0.4076261 ],
                [-0.50840007,  0.85667728  ,0.08736939  ,0.0603725 ],
                [ 0.12293002, -0.02821837,  0.99201408,   0.13485433],
                [ 0.    ,      0.   ,       0.    ,      1.        ]]),
                np.array([[-0.85230134, -0.51508035 ,  0.09096513 , 0.4076261 ],
                [-0.50840007,  0.85667728  ,0.08736939  ,0.0603725 ],
                [ 0.12293002, -0.02821837 , 0.99201408 , 0.18485433],
                [ 0.        ,  0.      ,    0.   ,       1.        ]])]

    def fix_y_left_from_T(T):
        T = T.copy()
        R = T[:3, :3]

        # flip local +Y axis (2nd column)
        R[:, 1] *= -1

        # optional sanity: ensure proper rotation
        if np.linalg.det(R) < 0:
            raise ValueError("Still left-handed after flip (check your convention: columns vs rows).")

        T[:3, :3] = R
        return T
    
    def transform_to_curobo_pose(T):
        """
        Convert 4x4 transform matrix to cuRobo pose:
        [x, y, z, w, qx, qy, qz]
        """

        # --- Extract translation ---
        t = T[:3, 3]

        # --- Extract rotation ---
        Rm = T[:3, :3]

        # --- Orthonormalize rotation (SVD projection to SO(3)) ---
        U, _, Vt = np.linalg.svd(Rm)
        Rfix = U @ Vt

        if np.linalg.det(Rfix) < 0:
            U[:, -1] *= -1
            Rfix = U @ Vt

        # --- Convert to quaternion ---
        # scipy returns (x, y, z, w)
        quat_xyzw = R.from_matrix(Rfix).as_quat()

        # Reorder to cuRobo format (w, x, y, z)
        quat_wxyz = quat_xyzw[[3, 0, 1, 2]]

        # --- Concatenate to 7D pose ---
        pose = np.concatenate([t, quat_wxyz])

        return pose

                
    pose_list = [fix_y_left_from_T(p) for p in pose_lists]
    pose_list = [transform_to_curobo_pose(p) for p in pose_list]
    
    # Rotate each pose orientation by +90 deg about local Y
    pose_lists_rot_y90 = [rotate_pose_local(p, axis_xyz=[1, 0, 0], angle_deg=180.0) for p in pose_list]
    
    #pose_lists_rot_y90 = [rotate_pose_local(p, axis_xyz=[0, 1, 0], angle_deg=90.0) for p in pose_lists]
    #pose_lists_rot_y90 = [rotate_pose_local(p, axis_xyz=[0, 0, 1], angle_deg=180.0) for p in pose_lists]
    
    
    
    trajectory, segments = planner.plan(
        visualize_frames=True,
        pose_lists=pose_lists_rot_y90,
        segment_modes=(0, 0, 0,),
        grasp_prepose_motion=True,
        export_usd=True,
    )
    
    
    
    # trajectory, segments = planner.plan(
    #     pose_lists=[
    #         [0.0, -1.5707963267948966, 0.0, 0.0, 0.0, 0.0],  # mode 0
    #         [-1.843067690106012, -2.038544566329377, -1.7976891295541595, 4.007275962578981, 0.8883725892651138, -0.1117010721276371],
    #         [0.0, -2.5254914276357945, 2.230705316973953, 0.7297221602588292, 1.7598154847858825, 0.13526301702956053],
    #     ],
    #     segment_modes=(0,0,0),
    #     grasp_prepose_motion=True,
    #     attach_after_index=[],
    #     detach_after_index=[],
    #     cylinder_radius=0.05,
    #     export_usd=True,
    #     cylinder_height=0.15,
    #     cylinder_offset_pose=rotate_pose_local(
    #         (0, 0, 0.0, 1, 0, 0, 0),
    #         axis_xyz=(0, 1, 0),
    #         angle_deg=90,
    #     ),
    # )
    # print(type(trajectory))
    # if isinstance(trajectory, list):
    #     print("num trajectories:", len(trajectory))
    #     if trajectory:
    #         print("first traj position shape:", trajectory[0].position.shape)
    # else:
    #     print("position shape:", trajectory.position.shape)
    # print(f"Total time: {time.time() - start}")
