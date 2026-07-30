import numpy as np

from curobo.geom.types import Cuboid, WorldConfig
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.util.usd_helper import UsdHelper


def export_curobo_trajectory_to_usd(
    trajectory,
    world_cfg,
    robot_file: str,
    save_path: str = "curobo_plan.usd",
    dt: float = 0.01,
    trajectory_index: int = 0,
    base_frame: str = "/world",
    flatten_usd: bool = True,
    motion_gen=None,
    seg_end_indices=None,
    visual_box_dims=None,
    visual_box_offset_pose=None,
    visual_attach_after_index=None,
    visual_detach_after_index=None,
    visual_box_parent_link: str = "grasp_frame",
    visual_box_robot_frame: str = "attached_object",
    visual_box_color=(0.2, 0.8, 0.2, 1.0),
):
    """
    Export one planned CuRobo trajectory to USD.

    If `trajectory` is a list (batch output), `trajectory_index` selects which
    one to export.
    """
    if trajectory is None:
        return None

    traj_to_export = trajectory
    if isinstance(trajectory, list):
        if len(trajectory) == 0:
            return None
        if trajectory_index < 0 or trajectory_index >= len(trajectory):
            raise ValueError(
                f"trajectory_index {trajectory_index} is out of range for {len(trajectory)} trajectories"
            )
        traj_to_export = trajectory[trajectory_index]

    start_state = JointState.from_position(
        traj_to_export.position[0].view(1, -1),
        joint_names=traj_to_export.joint_names,
    )
    q_traj = traj_to_export.clone()
    q_traj.position = q_traj.position.contiguous()
    if q_traj.velocity is not None:
        q_traj.velocity = q_traj.velocity.contiguous()
    if q_traj.acceleration is not None:
        q_traj.acceleration = q_traj.acceleration.contiguous()
    if q_traj.jerk is not None:
        q_traj.jerk = q_traj.jerk.contiguous()

    UsdHelper.write_trajectory_animation_with_robot_usd(
        robot_file,
        world_cfg,
        start_state,
        q_traj,
        dt=dt,
        save_path=save_path,
        base_frame=base_frame,
        flatten_usd=flatten_usd,
    )

    # Optional: add a visual-only animated attached box to the USD.
    if (
        motion_gen is not None
        and seg_end_indices is not None
        and visual_box_dims is not None
        and visual_box_offset_pose is not None
        and visual_attach_after_index is not None
    ):
        box_dims = np.asarray(visual_box_dims, dtype=float).reshape(-1)
        if box_dims.shape[0] != 3 or np.any(box_dims <= 0.0):
            raise ValueError("visual_box_dims must be 3 strictly positive values [x, y, z]")

        seg_end_indices = list(seg_end_indices)
        attach_indices = (
            list(visual_attach_after_index)
            if isinstance(visual_attach_after_index, (list, tuple))
            else [visual_attach_after_index]
        )
        detach_indices = (
            list(visual_detach_after_index)
            if isinstance(visual_detach_after_index, (list, tuple))
            else ([visual_detach_after_index] if visual_detach_after_index is not None else [])
        )
        if len(attach_indices) == 0:
            attach_indices = [0]
        if any(i < 0 or i >= len(seg_end_indices) for i in attach_indices):
            raise ValueError("visual_attach_after_index contains an out-of-range segment index")
        if any(i < 0 or i >= len(seg_end_indices) for i in detach_indices):
            raise ValueError("visual_detach_after_index contains an out-of-range segment index")

        attach_steps = [int(seg_end_indices[i]) for i in attach_indices]
        detach_steps = [int(seg_end_indices[i]) for i in detach_indices] if detach_indices else []

        link_poses = motion_gen.kinematics.get_link_poses(
            q_traj.position, [visual_box_parent_link]
        )
        offset_pose = Pose.from_list(list(visual_box_offset_pose), tensor_args=motion_gen.tensor_args)

        pos_seq = []
        quat_seq = []
        for t in range(q_traj.position.shape[0]):
            visible = False
            for k, a_step in enumerate(attach_steps):
                d_step = detach_steps[k] if k < len(detach_steps) else None
                if t >= a_step and (d_step is None or t <= d_step):
                    visible = True
                    break
            if not visible:
                pos_seq.append([0.0, 0.0, -10.0])
                quat_seq.append([1.0, 0.0, 0.0, 0.0])
            else:
                ee_pose = Pose(
                    link_poses.position[t, 0, :],
                    link_poses.quaternion[t, 0, :],
                    normalize_rotation=False,
                )
                obj_pose = ee_pose.multiply(offset_pose)
                pos_seq.append(obj_pose.position.squeeze().cpu().tolist())
                quat_seq.append(obj_pose.quaternion.squeeze().cpu().tolist())

        pos_t = motion_gen.tensor_args.to_device(np.asarray(pos_seq)).view(-1, 1, 3)
        quat_t = motion_gen.tensor_args.to_device(np.asarray(quat_seq)).view(-1, 1, 4)
        pose_traj = Pose(position=pos_t, quaternion=quat_t, normalize_rotation=False)

        box = Cuboid(
            name="attached_box_visual",
            dims=box_dims.tolist(),
            pose=[pos_seq[0][0], pos_seq[0][1], pos_seq[0][2], *quat_seq[0]],
            color=list(visual_box_color),
        )

        usd_helper = UsdHelper()
        usd_helper.load_stage_from_file(save_path)
        usd_helper.interpolation_steps = 1
        usd_helper.dt = dt
        usd_helper.create_animation(
            WorldConfig(objects=[box]),
            pose_traj,
            base_frame=base_frame,
            robot_frame=visual_box_robot_frame,
            dt=dt,
        )
        usd_helper.write_stage_to_file(save_path, flatten=True)

    print(f"Wrote: {save_path}")
    return save_path
