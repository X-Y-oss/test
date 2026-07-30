import open3d as o3d
import numpy as np
from klampt import Geometry3D
from klampt.model.create import box
from utils.o3d_klampt_conversions import klampt_geom_to_open3d, o3d_mesh_to_klampt_geom

class Gripper_CollisionValidation():
    def __init__(self):
        self.environment = None
        
        # Gripper dimensions
        self.finger_len = 0.075
        self.finger_thickness = 0.02
        self.finger_depth = 0.02
        self.palm_width = 0.05
        self.palm_height = 0.085
        self.palm_depth = 0.10
        self.arm_length = 0.25
        self.arm_width = 0.1
        
        # camera
        self.camera_height = 0.135
        self.camera_offset = 0.05
        self.camera_width = 0.05
        
        self.gripper_parts = self.make_gripper_geometries()
    
    def setMesh(self, mesh):
        """Expects open3d mesh to transform it for collision checking
        Args:
            mesh (o3d_mesh): Environment to be checked against
        """
        self.environment = o3d_mesh_to_klampt_geom(mesh)
        
    def create_box_geometry(self, size):
        mesh = box(size[0], size[1], size[2])
        return Geometry3D(mesh)
        
    def make_gripper_geometries(self):
        """Creates gripper with geometries set.
        Returns:
            Gripper parts 3x(mesh, T): Gripper is split into 3 meshes
        """
        R_z_to_x = np.array([
            [0, 0, 1],
            [0, 1, 0],
            [-1, 0, 0]
        ])
        
        arm = self.create_box_geometry((self.arm_length, self.arm_width, self.arm_width))
        arm_T = palm_T = np.eye(4)
        arm_T[:3, 3] = [-self.palm_depth * 2, 0, 0]
        
        palm = self.create_box_geometry((self.palm_width, self.palm_height + self.finger_thickness*2, self.palm_depth))
        palm_T = np.eye(4)
        palm_T[:3, :3] = R_z_to_x
        palm_T[:3, 3] = [-self.palm_depth / 2, 0, 0]
        # Fingers now point in Z direction
        finger = self.create_box_geometry((self.finger_depth, self.finger_thickness, self.finger_len))
        
        # Offset in Y for aperture, and Z to bring fingers in front of palm
        y_offset = (self.palm_height / 2) + (self.finger_thickness / 2)
        x_offset = (self.finger_len / 2)
        # No rotation needed if finger already built pointing in Z
        # Finger transforms as full 4x4 matrices
        finger1_T = np.eye(4)
        finger1_T[:3, :3] = R_z_to_x
        # finger1_T[:3, 3] = [0, y_offset, z_offset]
        finger1_T[:3, 3] = [x_offset, y_offset, 0]
        finger2_T = np.eye(4)
        finger2_T[:3, :3] = R_z_to_x
        # finger2_T[:3, 3] = [0, -y_offset, z_offset]
        finger2_T[:3, 3] = [x_offset, -y_offset, 0]
        
        
        #### Camera prior
        camera = self.create_box_geometry((self.camera_offset, self.camera_width, self.camera_height))
        camera_T = np.eye(4)
        camera_T[:3, 3] = [-self.palm_width - self.camera_offset/2, 0, self.camera_height/2]
        
        
        return [
            (arm, arm_T),
            (palm, palm_T),
            (finger, finger1_T),
            (finger, finger2_T),
            (camera, camera_T)
        ]
        
    def validate_collisions(self, Transforms: np.array, plotting=False, max_amount=100, pcd=None, show_colliding=True):
        """Validates whether the gripper collides with the environment
        Args:
            Transforms (np.array): Transforms to be evaluated on mesh
            plotting (bool): Whether result should be plotted
            max_amount (int): Of grasps shown in plot
            pcd (o3d.io.read_point_cloud) if wanting to plot it
        Returns:
            np.array (boolean): if collisions with environment occur for every Transform given
        """
        if not (self.environment):
            print("Set environment mesh first.")
            return
        
        results_arm    = Transforms @ self.gripper_parts[0][1]
        results_palm    = Transforms @ self.gripper_parts[1][1]
        results_finger1 = Transforms @ self.gripper_parts[2][1]
        results_finger2 = Transforms @ self.gripper_parts[3][1]
        results_camera = Transforms @ self.gripper_parts[4][1]

        arm, palm, finger, finger, camera = self.gripper_parts[0][0], self.gripper_parts[1][0], self.gripper_parts[2][0], self.gripper_parts[3][0], self.gripper_parts[4][0]
        collision_flags = []

        for i in range(Transforms.shape[0]):
            is_colliding = False
            for geom, result in zip(
                [arm, palm, finger, finger, camera],
                [results_arm[i], results_palm[i], results_finger1[i], results_finger2[i], results_camera[i]]
            ):
                #R = result[:3, :3].ravel().tolist()  # Faster than reshape(-1)
                R = result[:3, :3].T.flatten()  # Faster than reshape(-1)
                t = result[:3, 3].tolist()
                geom.setCurrentTransform(R, t)
                if geom.collides(self.environment):
                    is_colliding = True
                    break
            collision_flags.append(is_colliding)
        
        if(plotting == True):
            o3d_meshes = []
            N = min(max_amount,results_palm.shape[0])
            i, shown = 0, 0
            max_col = 200
            while i<results_palm.shape[0] and shown<N:
                mesh_list = []
                collision = False
                for T, geom in [
                    (results_arm[i], arm),
                    (results_palm[i], palm),      # Blue-ish for palm
                    (results_finger1[i], finger),  # Green-ish for finger1
                    (results_finger2[i], finger),  # Green-ish for finger2
                    (results_camera[i], camera),  # Green-ish for finger2
                ]:
                    if(collision_flags[i]==True):
                        mesh_o3d = klampt_geom_to_open3d(geom, T=T, color=[1.0, 0.0, 0.0])
                        mesh_list.append(mesh_o3d)
                        collision = True
                    else:
                        mesh_o3d = klampt_geom_to_open3d(geom, T=T, color=[0.1, 0.8, 0.1])
                        mesh_list.append(mesh_o3d)
                        
                if(not collision or show_colliding==True):
                    if(show_colliding==True and collision==True):
                        if(max_col==0):
                            i+=1
                            continue
                        else:max_col-=1
                    o3d_meshes += mesh_list
                    axes = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2, origin=[0, 0, 0])
                    axes.transform(results_palm[i])
                    #o3d_meshes.append(axes)
                    shown+=1
                i+=1
                    
            o3d_mesh_env = klampt_geom_to_open3d(self.environment, np.eye(4), color=[0.0, 0.0, 0.6])
            if(pcd is not None):
                o3d.visualization.draw_geometries(o3d_meshes + [o3d_mesh_env] + [pcd])
            else:
                o3d.visualization.draw_geometries(o3d_meshes + [o3d_mesh_env])
        
        return np.array(collision_flags, dtype=bool)
    
    def plot_scored_grasps(self, transforms: np.array, scores: np.array):
        """Plot gripper meshes for each transform, colored by normalized score.
        Args:
            transforms (np.array): Grasp transforms of shape (N, 4, 4)
            scores (np.array): Score per grasp of shape (N,)
        """
        transforms = np.asarray(transforms)
        scores = np.asarray(scores).reshape(-1)
        
        if transforms.ndim != 3 or transforms.shape[1:] != (4, 4):
            print(f"Invalid transforms shape: {transforms.shape}, expected (N, 4, 4).")
            return
        if transforms.shape[0] != scores.shape[0]:
            print(f"Shape mismatch: transforms={transforms.shape[0]}, scores={scores.shape[0]}")
            return
        if transforms.shape[0] == 0:
            print("No transforms to plot.")
            return
        
        finite_scores = scores[np.isfinite(scores)]
        if finite_scores.size == 0:
            print("Scores contain no finite values.")
            return
        
        s_min = float(np.min(finite_scores))
        s_max = float(np.max(finite_scores))
        if s_max - s_min < 1e-12:
            norm_scores = np.ones_like(scores, dtype=float)
        else:
            norm_scores = (scores - s_min) / (s_max - s_min)
        norm_scores = np.nan_to_num(norm_scores, nan=0.0, posinf=1.0, neginf=0.0)
        norm_scores = np.clip(norm_scores, 0.0, 1.0)
        
        o3d_meshes = []
        for i in range(transforms.shape[0]):
            s = float(norm_scores[i])
            color = [1.0 - s, s, 0.0]
            for geom, T_local in self.gripper_parts:
                T_world = transforms[i] @ T_local
                mesh_o3d = klampt_geom_to_open3d(geom, T=T_world, color=color)
                o3d_meshes.append(mesh_o3d)
        
        draw_list = o3d_meshes
        if self.environment is not None:
            env_mesh = klampt_geom_to_open3d(self.environment, np.eye(4), color=[0.0, 0.0, 0.6])
            draw_list = draw_list + [env_mesh]
        
        world_axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])
        draw_list.append(world_axis)
        o3d.visualization.draw_geometries(draw_list, window_name="Scored grasps (red=low, green=high)")
    
    def plot_gripper_geoms(self):
        mesh_list = []
        for x in range(len(self.gripper_parts)):
            geom = self.gripper_parts[x][0]
            T = self.gripper_parts[x][1]
            mesh_o3d = klampt_geom_to_open3d(geom, T=T, color=[1.0, 0.0, 0.0])
            mesh_list.append(mesh_o3d)
            
        # Add global/world coordinate frame
        world_axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.05, origin=[0, 0, 0])

        # Visualize all
        o3d.visualization.draw_geometries(mesh_list + [world_axis])
    
    def plot_grasp_feasibility(self, transforms, feasible_mask, T_armbase_to_world, max_total=1000, max_infeasible=1000, pcd=None, mesh=None):
        feasible_mask = np.asarray(feasible_mask).reshape(-1).astype(bool)
        if transforms is None or feasible_mask is None:
            print("[feas-plot] Missing inputs.")
            return
        if transforms.shape[0] != feasible_mask.shape[0]:
            print(f"[feas-plot] Shape mismatch: transforms={transforms.shape[0]}, mask={feasible_mask.shape[0]}")
            return
        if self.environment is None:
            print("[feas-plot] Environment not set on hand_collider.")
            return

        o3d_meshes = [] if mesh is None else [mesh]
        shown = 0
        shown_bad = 0

        for i in range(transforms.shape[0]):
            if shown >= max_total:
                break

            is_feasible = bool(feasible_mask[i])
            if (not is_feasible) and (shown_bad >= max_infeasible):
                continue

            color = [0.1, 0.8, 0.1] if is_feasible else [1.0, 0.0, 0.0]

            for geom, T_local in self.gripper_parts:
                T_world = transforms[i] @ T_local
                mesh_o3d = klampt_geom_to_open3d(geom, T=T_world, color=color)
                o3d_meshes.append(mesh_o3d)

            if not is_feasible:
                shown_bad += 1
            shown += 1

        env_mesh = klampt_geom_to_open3d(self.environment, np.eye(4), color=[0.0, 0.0, 0.6])
        world_axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.12, origin=[0, 0, 0])
        robot_axis = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.12, origin=[0, 0, 0]); robot_axis.transform(np.linalg.inv(T_armbase_to_world))

        draw_list = o3d_meshes + [env_mesh, world_axis, robot_axis]
        if pcd is not None:
            draw_list.append(pcd)

        o3d.visualization.draw_geometries(
            draw_list,
            window_name="Grasp feasibility (green=feasible, red=infeasible)",
        )
    
    
if __name__ == "__main__":
    collide_test = Gripper_CollisionValidation()
    collide_test.plot_gripper_geoms()