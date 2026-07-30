from sensor_msgs.msg import JointState
import numpy as np
import time
from scipy.spatial.transform import Rotation as R
from rclpy.action import ActionClient
from control_msgs.action import GripperCommand

import rclpy

from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from control_msgs.action import FollowJointTrajectory
from builtin_interfaces.msg import Duration

from rclpy.duration import Duration as durationsuper
from rclpy.action import ActionClient

import toppra as ta, toppra.algorithm as algo, toppra.constraint as constraint
from moveit_msgs.msg import RobotTrajectory

from placeability_scoring.planning.Curobo_Planner import Curobo_Planner, o3dmesh_to_curobomesh
from placeability_scoring.planning.environment import make_shelf, make_table, merge_meshes
from curobo.geom.types import WorldConfig

from scipy.spatial.transform import Rotation as R

def transform_to_curobo_pose(T):
    """
    T: (4,4) or (...,4,4)
    returns:
      - (7,) if input was (4,4)
      - (...,7) otherwise
    pose format: [x, y, z, qw, qx, qy, qz]
    """
    T = np.asarray(T)
    assert T.shape[-2:] == (4, 4)

    single = (T.ndim == 2)
    if single:
        T = T[None, ...]  # (1,4,4)

    t  = T[..., :3, 3]    # (...,3)
    Rm = T[..., :3, :3]   # (...,3,3)

    U, _, Vt = np.linalg.svd(Rm)
    Rfix = U @ Vt

    det = np.linalg.det(Rfix)            # (...)
    mask = det < 0

    if np.any(mask):
        U2 = U.copy()
        # Multiply last column by -1 where mask==True (broadcast-safe for any batch shape)
        U2[..., :, -1] *= (1.0 - 2.0 * mask.astype(U2.dtype))[..., None]
        Rfix = U2 @ Vt

    quat_xyzw = R.from_matrix(Rfix).as_quat()      # (...,4) x,y,z,w
    quat_wxyz = quat_xyzw[..., [3, 0, 1, 2]]       # (...,4) w,x,y,z

    pose = np.concatenate([t, quat_wxyz], axis=-1) # (...,7)

    return pose[0] if single else pose


class UR5e_Interface():
    def __init__(self, 
                node,
                robot_file = "ur5e_robotiq_2f_85.yml",
                arm_speed = "slow",
                T_armbase_to_world=None,
                ):
        self.node = node
        
        # To keep track of the arm
        self.ur5e_joint_names = [
            f'shoulder_pan_joint',
            f'shoulder_lift_joint',
            f'elbow_joint',
            f'wrist_1_joint',
            f'wrist_2_joint',
            f'wrist_3_joint'
        ]
        print("Joint names: ",self.ur5e_joint_names)
        self.current_joint_positions = np.zeros(6)
        self.current_joint_positions[1] = -1.57
        
        self.gripper_status = 0.0
        self.received = False
        
        self.set_planning_mode(arm_speed)
        self.curobo_planner = None
        self.curobo_world_cfg = None
        if T_armbase_to_world is None:
            self.T_armbase_to_world = np.array([
                [0.0, 1.0, 0.0, 0.0],
                [-1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, -0.720],
                [0.0, 0.0, 0.0, 1.0],
            ], dtype=float)
        else:
            self.T_armbase_to_world = np.asarray(T_armbase_to_world, dtype=float)
        
        
        
        self.arm_joint_publisher = self.node.create_publisher(JointTrajectory,'/joint_trajectory_controller/joint_trajectory', 1)
        self.arm_client = ActionClient(self.node, FollowJointTrajectory, '/joint_trajectory_controller/follow_joint_trajectory')
        self.arm_joint_subscriber = self.node.create_subscription(JointState, '/joint_states', self.arm_joint_callback, 1)
            

        self._action_client = ActionClient(
                self.node,
                GripperCommand,
                '/robotiq_gripper_controller/gripper_cmd'
            )
        
        # these will be set when you call move_smooth()
        self._interp_points = []
        self._current_idx = 0
        self._timer = None
        
        
        self.curobo_planner = self.init_curobo_planner(
            robot_file=robot_file,
        )
        
        
    def set_joint_state(self, joint_state):
        self.curobo_planner.set_current_joint_state(joint_state)
        
    def get_joint_state(self):
        return self.curobo_planner.get_current_joint_state() 

    def sync_planner_joint_states(self):
        if self.curobo_planner is None:
            raise RuntimeError("Curobo planner is not initialized.")
        current = self.get_joint_positions()
        print(current)
        self.curobo_planner.set_current_joint_state(current)

        

    def init_curobo_planner(
        self,
        robot_file="ur5e_robotiq_2f_85.yml",
        attach_box=True,
        attach_link_name="attached_object",
        world_name="pc_world",
        # Backward compatibility:
        attach_cylinder=None,
    ):
        if attach_cylinder is not None:
            attach_box = bool(attach_cylinder)
        start = time.time()
        shelf_mesh, _ = make_shelf()
        table_bbox = np.array(
            [
                [-1.0, -1.0, 0.70],
                [1.0, 1.0, 0.72],
            ],
            dtype=float,
        )
        table_mesh, _ = make_table(
            bounding_box=table_bbox,
            thickness=0.02,
        )
        combined_mesh = merge_meshes([shelf_mesh, table_mesh])
        scene_pose = transform_to_curobo_pose(self.T_armbase_to_world)
        scene_mesh = o3dmesh_to_curobomesh(combined_mesh, name=world_name, pose=scene_pose)
        world_cfg = WorldConfig(mesh=[scene_mesh])
        print(f"Mesh time: {time.time() - start}")

        start = time.time()
        planner = Curobo_Planner(
            world_cfg,
            robot_file=robot_file,
            attach_box=attach_box,
            attach_link_name=attach_link_name,
        )
        print(f"Setup time: {time.time() - start}")

        self.curobo_world_cfg = world_cfg
        self.curobo_planner = planner
        return planner

    def set_curobo_collision_mesh(self, o3d_mesh, world_name="pc_world_dynamic"):
        if self.curobo_planner is None:
            raise RuntimeError("Curobo planner is not initialized.")
        if o3d_mesh is None or o3d_mesh.is_empty():
            raise ValueError("Collision mesh is empty.")

        scene_pose = transform_to_curobo_pose(self.T_armbase_to_world)
        scene_mesh = o3dmesh_to_curobomesh(o3d_mesh, name=world_name, pose=scene_pose)
        world_cfg = WorldConfig(mesh=[scene_mesh])
        self.curobo_planner.assign_world(world_cfg)
        self.curobo_world_cfg = world_cfg
        return world_cfg
        
    def set_planning_mode(self, mode):
        if(mode=="fast"):
            self.arm_joint_vel_limits = [1.57,1.57,1.57,1.57,1.57,1.57]
            self.arm_joint_acc_limits = [1.57,1.57,1.57,1.57,1.57,1.57]
        elif(mode=="cam_fast"):
            self.arm_joint_vel_limits = [1.,1.,1.,1.,1.,1.]
            self.arm_joint_acc_limits = [1.,1.,1.,1.,1.,1.]
        elif(mode=="medium"):
            self.arm_joint_vel_limits = [0.5,0.5,0.5,0.5,0.5,0.5]
            self.arm_joint_acc_limits = [0.5,0.5,0.5,0.5,0.5,0.5]
        elif(mode=="slow"):
            self.arm_joint_vel_limits = [0.25,0.25,0.25,0.25,0.25,0.25]
            self.arm_joint_acc_limits = [0.25,0.25,0.25,0.25,0.25,0.25]
        elif(mode=="superslow"):
            self.arm_joint_vel_limits = [0.1,0.1,0.1,0.1,0.1,0.1]
            self.arm_joint_acc_limits = [0.1,0.1,0.1,0.1,0.1,0.1]
        
    def get_approach_offset_matrix(self, offset=0.05):
        T_offset = np.eye(4)
        T_offset[0, 3] = -offset
        return T_offset
    
    def from_matrix_lenient(self, Rm):
        U, _, Vt = np.linalg.svd(Rm)
        Rfix = U @ Vt
        if np.linalg.det(Rfix) < 0:
            U[:, -1] *= -1
            Rfix = U @ Vt
        return R.from_matrix(Rfix)
    
    def plan_arm_to_pose(self, config, start_config = None, mode=0):
        """Planning to pose or joint configuration

        Args:
            config (list of tuples): [(config),(config)/(pose),(pose)]
            start_config (config): If planning from different start config, Defaults to None.
            mode (int, optional): Mode of Planning. Defaults to 0.

        Returns:
            trajectory: Motion Trajectory of plan
        """
        # Save current config
        if(start_config is not None):
            initial = self.get_joint_state()
            self.set_joint_state(start_config)
        
        # get trajectory between start and quaternion
        trajectory, seg_end_indices = self.curobo_planner.plan(
            pose_lists=config,
            segment_modes=(mode,),
            grasp_prepose_motion=True,
        )
        
        # set back
        if(start_config is not None):
            self.set_joint_state(initial)
        
        return trajectory, seg_end_indices
    
    def fix_y_left_from_T(self, T, verbose: bool = False):
        T = T.copy()
        Rm = T[:3, :3]
        det_in = np.linalg.det(Rm)
        if verbose:
            print(f"[fix_y_left_from_T] input det={det_in:.6f}")

        # Only flip if the input is actually left-handed.
        # Flipping an already right-handed basis makes it invalid (det < 0).
        if det_in < 0:
            R_try = Rm.copy()
            # Common case: basis vectors are stored as columns.
            R_try[:, 1] *= -1
            if np.linalg.det(R_try) < 0:
                # Fallback for row-vector conventions.
                R_try = Rm.copy()
                R_try[1, :] *= -1
                if verbose:
                    print("[fix_y_left_from_T] left-handed input, applied row-y flip")
            elif verbose:
                print("[fix_y_left_from_T] left-handed input, applied column-y flip")
            Rm = R_try
        elif verbose:
            print("[fix_y_left_from_T] input already right-handed, no y-flip applied")

        # Project to nearest proper rotation to remove numeric drift and
        # guarantee SciPy quaternion conversion gets a valid SO(3) matrix.
        U, _, Vt = np.linalg.svd(Rm)
        Rm = U @ Vt
        if np.linalg.det(Rm) < 0:
            U[:, -1] *= -1
            Rm = U @ Vt
            if verbose:
                print("[fix_y_left_from_T] SVD projection produced det<0, fixed via last singular vector")

        if verbose:
            det_out = np.linalg.det(Rm)
            print(f"[fix_y_left_from_T] output det={det_out:.6f}")

        T[:3, :3] = Rm
        return T
    
    def plan(self,
                pose_list=None, segment_modes=(0,),
                start_config = None,
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
                export_usd=False,
                usd_save_path="/home/ws/curobo_plan.usd",
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
             ):
        """Planning to pose or joint configuration

        Args:
            pose_lists (list of tuples): [(config),(config)/(pose),(pose)]
            start_config (config): If planning from different start config, Defaults to None.
            segment_modes (int, optional): Mode of Planning. Defaults to 0.

        Returns:
            trajectory: Motion Trajectory of plan
        """
        # Save current config
        if(start_config is not None):
            initial = self.get_joint_state()
            self.set_joint_state(start_config)
        else:
            self.sync_planner_joint_states()
        
        # get trajectory between start and quaternion
        trajectory, seg_end_indices = self.curobo_planner.plan(
            pose_lists=pose_list,
            segment_modes=segment_modes,
            visualize_frames=visualize_frames,
            constrain_orientation=constrain_orientation,
            cartesian_hold_axes=cartesian_hold_axes,
            constrained_batch_axis=constrained_batch_axis,
            constrained_batch_project_to_goal_frame=constrained_batch_project_to_goal_frame,
            grasp_retract_offset=grasp_retract_offset,
            grasp_retract_offsets=grasp_retract_offsets,
            grasp_retract_constraint_in_goal_frame=grasp_retract_constraint_in_goal_frame,
            grasp_approach_offset=grasp_approach_offset,
            grasp_approach_constraint_in_goal_frame=grasp_approach_constraint_in_goal_frame,
            grasp_approach_path_constraint=grasp_approach_path_constraint,
            retract_path_constraint=retract_path_constraint,
            project_to_goal_frame=project_to_goal_frame,
            snap_stack=snap_stack,
            snap_tol=snap_tol,
            export_usd=export_usd,
            usd_save_path=usd_save_path,
            grasp_prepose_motion=grasp_prepose_motion,
            debug_jumps=debug_jumps,
            attach_box=attach_box,
            attach_after_index=attach_after_index,
            detach_after_index=detach_after_index,
            box_dims=box_dims,
            box_offset_pose=box_offset_pose,
            attach_cylinder=attach_cylinder,
            cylinder_radius=cylinder_radius,
            cylinder_height=cylinder_height,
            cylinder_offset_pose=cylinder_offset_pose,
        )
        
        # set back
        if(start_config is not None):
            self.set_joint_state(initial)
            
        
        if trajectory is None:
            return [], None
        elif isinstance(trajectory, list):
            if len(trajectory) == 0:
                return [], None
            else:
                # list of arrays:
                return [t.position.detach().cpu().numpy() for t in trajectory], seg_end_indices
        else:
            return [trajectory.position.detach().cpu().numpy()], seg_end_indices
        
    
    def move_arm_to_pose(self, T, link_name="gripper_virtual_link"):
        """Go to pregrasp

        Args:
            T (numpy 4x4 matrix): Translation matrix to move to
        """
        path, _ = self.plan_arm_to_pose(T=T, link_name=link_name)
        if(path == []): return False
        
        print("Sliced path: ",path)
        
        self.send_trajectory_with_moveit(path.tolist())
            
        return True
    
    #################################################################################################################################
    ############################################ TOPPRA  ############################################################################
    #################################################################################################################################
    def sparse_path_to_dense_trajectory(self, sparse_path, joint_names= None, dt=0.01):
        path = ta.SplineInterpolator(np.linspace(0, 1, len(sparse_path)), np.array(sparse_path))
        vc = constraint.JointVelocityConstraint(np.array(self.arm_joint_vel_limits))
        ac = constraint.JointAccelerationConstraint(np.array(self.arm_joint_acc_limits))
        
        traj = algo.TOPPRA([vc, ac], path, solver_wrapper='seidel').compute_trajectory()
            
        #traj = algo.TOPPRA([vc], path, solver_wrapper='seidel').compute_trajectory()
        if traj is None:
            traj = algo.TOPPRA([vc], path, solver_wrapper='seidel').compute_trajectory()
            
        if traj is None:
            print(sparse_path)
            print(type(path))
            print(traj)
            input("Toppra failed Runtime error, pres enter.")
            raise RuntimeError("TOPP-RA failed")

        duration = float(traj.duration)

        ts = np.arange(0.0, duration, dt)  # regular grid
        if ts.size == 0 or (duration - ts[-1]) > 1e-9:
            ts = np.append(ts, duration)    # force exact endpoint
        else:
            ts[-1] = duration               # avoid tiny float mismatch

        qs, qds, qdds = traj(ts), traj(ts, 1), traj(ts, 2)
        # Force stationary start (controller sees zero vel/acc at first waypoint)
        qs[0] = np.asarray(sparse_path[0], dtype=float)
        qds[0, :] = 0.0
        qdds[0, :] = 0.0
        
        rt = RobotTrajectory()
        rt.joint_trajectory.joint_names = self.ur5e_joint_names if joint_names is None else joint_names
        rt.joint_trajectory.points = [
            JointTrajectoryPoint(positions=qs[i].tolist(),
                                velocities=qds[i].tolist(),
                                accelerations=qdds[i].tolist(),
                                time_from_start = Duration(sec=int(float(ts[i])), nanosec=int(round((float(ts[i]) - int(float(ts[i]))) * 1e9))))
            for i in range(len(ts))
        ]
        return rt
    
    #################################################################################################################################
    ############################################ MOVE-IT Publisher  ############################################################################
    #################################################################################################################################
    def send_trajectory_with_moveit(self, traj):
        traj_rounded = np.round(np.asarray(traj, dtype=float), 4)
        _, idx2 = np.unique(traj_rounded, axis=0, return_index=True)
        trajectory = np.asarray(traj)[np.sort(idx2)]
        
        rt = self.sparse_path_to_dense_trajectory(sparse_path=np.array(trajectory))
        rt.joint_trajectory.header.stamp = (
            self.node.get_clock().now() + durationsuper(seconds=2)
        ).to_msg()
        
        traj_np = np.array([p.positions for p in rt.joint_trajectory.points], dtype=float)

        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory = rt.joint_trajectory

        send_future = self.arm_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self.node, send_future)

        goal_handle = send_future.result()
        if goal_handle is None or not goal_handle.accepted:
            self.node.get_logger().error("Trajectory goal was rejected")
            return False

        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self.node, result_future)

        result = result_future.result()
        if result is None:
            self.node.get_logger().error("No trajectory result received")
            return False
        else: print("Motion done")

        # Optional: result.result.error_code check here
        self.sync_planner_joint_states()
        return True
            
        
        
    def arm_joint_callback(self, msg: JointState):
        joint_name_to_index = {name: i for i, name in enumerate(msg.name)}
        try:
            self.current_joint_positions = np.array([
                msg.position[joint_name_to_index[name]] for name in self.ur5e_joint_names
            ])
            
            if(self.received==False):print("received joint states")
            self.received = True
            
            
        except KeyError as e:
            print(f"Joint name {e} not found in JointState message.")
            
    
    def get_joint_positions(self):
        while(self.received==False):
            print("Joint positions did not arrive yet")
            rclpy.spin_once(self.node, timeout_sec=0.1)
        return self.current_joint_positions
    
    def send_goal(self, position: float, max_effort: float):
        goal_msg = GripperCommand.Goal()
        goal_msg.command.position = position
        goal_msg.command.max_effort = max_effort

        self.node.get_logger().info(f'Sending goal: position={position}, max_effort={max_effort}')

        self._action_client.wait_for_server()

        return self._action_client.send_goal_async(goal_msg)    
    
    def gripper_cmd(self, status="open"):
        if(status=="open"):
            future = self.send_goal(0.0, 1.0)
        else:
            future = self.send_goal(0.8, 1.0)
            
        rclpy.spin_until_future_complete(self.node, future)

        if future.result() is not None:
            goal_handle = future.result()
            self.node.get_logger().info("Goal sent successfully")

            # Optionally wait for the result
            result_future = goal_handle.get_result_async()
            rclpy.spin_until_future_complete(self.node, result_future)
            if result_future.result() is not None:
                self.node.get_logger().info(f"Result: {result_future.result().result}")
        else:
            self.node.get_logger().error("Failed to send goal")
    
    def close_gripper(self):
        self.gripper_cmd("close")
        
            
    def open_gripper(self):
        self.gripper_cmd("open")
    

    def move_arm(self, traj, add_curr:bool=False):
        if(add_curr):
            traj.insert(0, self.current_joint_positions)
        
        self.send_trajectory_with_moveit(trajectory=traj)