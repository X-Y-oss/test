import rclpy
from rclpy.node import Node
from rclpy.task import Future
from sensor_msgs.msg import Image
from functools import partial
import os
from cv_bridge import CvBridge
import numpy as np
from placeability_scoring.mapping.mapping_Marques.reconstruction import Reconstruction
import open3d as o3d
from scipy.spatial.transform import Rotation as R
from sensor_msgs.msg import CameraInfo
from rclpy.duration import Duration

from tf2_ros import Buffer, TransformListener
import tf2_ros

class GraspingAreaReconstruction_Interface():
    def __init__(self, 
                 node: Node,
                 simulation = False,
                 selected_cameras=["wrist"], 
                 topics: dict = {"wrist_camera_rgb_topic": '/wrist_camera/color/segmentation',
                                                                                "wrist_camera_depth_topic": '/wrist_camera/depth/image_raw',
                                                                                "wrist_camera_camera_info_topic": '/wrist_camera/camera_info'},
                 camera_links = {"wrist": "wrist_3_link",
                                 "static": "base_link"},
                 extrinsics_save_dir = "/home/ws/src/placeability_scoring/placeability_scoring/camera_extrinsics/"
                 ):
        self.node = node
        self.tf_buffer = self.node.tf_buffer
        self.tf_listener = self.node.tf_listener
        self.topics = topics
        
        self.simulation = simulation

        self.wrist_camera_link = camera_links["wrist"] #"wrist_3_link"
        self.static_camera_link = camera_links["static"] #"base_link"
        
        # reconstruction parameters
        self.voxel_size = 0.0025
        self.res = 8
        self.depth_scale = 1000.0
        self.depth_max = 1.3
        self.weight_threshold = 0.1
        self.block_count = 50000
        #self.label_n = 12
        
        self.make_subscriber(selected_cameras=selected_cameras)
        
        self.reconstruction = Reconstruction(
            depth_scale = self.depth_scale,
            depth_max=self.depth_max,
            res = self.res,
            voxel_size = self.voxel_size,
            device = o3d.core.Device('CPU:0'), #CUDA:0 -> Faster
            miu = 0.001, # Laplace smoothing factor
            integrate_color=True,
            weight_threshold=self.weight_threshold,
            block_count=self.block_count
        )
        ## CAMERAS
        self.extrinsics_save_dir = extrinsics_save_dir

        self.open_checks = []
        self.static_camera_color_image_raw = None
        self.wrist_camera_color_image_raw = None
        self.static_camera_depth_image_raw = None
        self.wrist_camera_depth_image_raw = None
        self.static_camera_intrinsics = None
        self.wrist_camera_intrinsics = None
        self.static_camera_color_future = Future()
        self.wrist_camera_color_future = Future()
        self.static_camera_depth_future = Future()
        self.wrist_camera_depth_future = Future()
        self.static_camera_intrinsics_future = Future()
        self.wrist_camera_intrinsics_future = Future()
        
        self.static_camera_pose = None
        self.wrist_camera_pose = None
        
        # Create the CvBridge object to convert the ROS Image message to OpenCV
        self.bridge = CvBridge()
        
        
        print("Init grasping area done")
        
    def lookup_transform(self, source=""):
        while rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.3)  # let TF callbacks run
            try:
                #rclpy.spin_once(self.node, timeout_sec=0.1)
                transform = self.tf_buffer.lookup_transform(
                        'world', source, rclpy.time.Time(),
                        timeout=Duration(seconds=0.5)
                    )
                self.node.get_logger().info(f"Transform:\n{transform}")
                
                # make it matrix
                t = transform.transform.translation
                q = transform.transform.rotation    
                r = R.from_quat([q.x, q.y, q.z, q.w]).as_matrix()
                #rotation = R.from_euler('y', 180, degrees=True).as_matrix()
                #r = rotation @ r.T
                #rotation = R.from_euler('x', 180, degrees=True).as_matrix()
                #r = rotation @ r.T
                flip_y = np.diag([1, -1, 1])
                r = r @ flip_y
                flip_x = np.diag([-1, 1, 1])
                r = r @ flip_x
                T = np.eye(4)
                T[0:3, 0:3] = r
                T[0:3, 3] = [t.x, t.y, t.z]
                return T
            
            except tf2_ros.LookupException:
                self.node.get_logger().warn(f"Transform from 'world' to {source} not found")
            except tf2_ros.ConnectivityException:
                self.node.get_logger().warn("grasp Connectivity error")
            except tf2_ros.ExtrapolationException:
                self.node.get_logger().warn("Extrapolation error")
            
        

    def make_subscriber(self, selected_cameras = ["static", "wrist"]):
        # Subscriber
        if("static" in selected_cameras):
            self.image_sub_1 = self.node.create_subscription(
                Image,
                self.topics['static_camera_rgb_topic'],
                partial(self._image_callback, camera='static_camera', depth=False),
                1
            )
            self.depth_sub_1 = self.node.create_subscription(
                Image,
                self.topics['static_camera_depth_topic'],
                partial(self._image_callback, camera='static_camera', depth=True),
                1
            )
            self.info_sub_1 = self.node.create_subscription(
                CameraInfo,
                self.topics['static_camera_camera_info_topic'],
                partial(self._camera_info_cb, camera='static_camera'),
                1
            )

        if("wrist" in selected_cameras):
            self.image_sub_2 = self.node.create_subscription(
                Image,
                self.topics['wrist_camera_rgb_topic'],
                partial(self._image_callback, camera='wrist_camera', depth=False),
                1
            )
            self.depth_sub_2 = self.node.create_subscription(
                Image,
                self.topics['wrist_camera_depth_topic'],
                partial(self._image_callback, camera='wrist_camera', depth=True),
                1
            )
            self.info_sub_2 = self.node.create_subscription(
                CameraInfo,
                self.topics['wrist_camera_camera_info_topic'],
                partial(self._camera_info_cb, camera='wrist_camera'),
                1
            )
    
    def check_message(self, np_array):
        """
        Returns True if message is valid

        Args:
            np_array (np.array): input array to be checked
        Output: bool
        """
        # Check if the input is a NumPy array
        if not isinstance(np_array, np.ndarray): 
            return False
        
        # Check if any dimension is zero (empty array)
        if np_array.size == 0:  # np_array.size returns the total number of elements
            return False
        
        return True

    def _image_callback(self, msg, camera, depth=False):
        if not depth:
            if camera == 'static_camera' and not self.static_camera_color_future.done():
                self.static_camera_color_image_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8') #bgr8
                #static_camera_image_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='mono8')
                
                if not (self.check_message(self.static_camera_color_image_raw)): return
                self.static_camera_color_future.set_result(True)
                self.node.get_logger().info("Received static image")

            elif camera == 'wrist_camera' and not self.wrist_camera_color_future.done():
                self.wrist_camera_color_image_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8') #bgr8
                #self.wrist_camera_image_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='mono8')

                
                if not (self.check_message(self.wrist_camera_color_image_raw)): return
                self.wrist_camera_color_future.set_result(True)
                self.node.get_logger().info("Received wrist image")
        if depth:
            if camera == 'static_camera' and not self.static_camera_depth_future.done():
                #self.static_camera_depth_image_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')
                depth_float32 = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                depth_float32 = np.ascontiguousarray(depth_float32)  # already float32
                #depth_float32 = cv2.flip(depth_float32, -1)
                if(self.simulation==True):
                    self.static_camera_depth_image_raw = (depth_float32 * 1000).astype(np.uint16)
                else:
                    self.static_camera_depth_image_raw = (depth_float32).astype(np.uint16)
                    
                    
                if not (self.check_message(self.static_camera_depth_image_raw)):
                    return
                
                self.static_camera_pose = self.lookup_transform(source=self.static_camera_link)
                if(self.static_camera_pose is not None):
                    print("TRANSFORM: ",self.static_camera_pose)
                    self.static_camera_depth_future.set_result(True)
                    self.node.get_logger().info("Received static depth image")
                    
                    #mabye? TODO check
                    Tz180 = np.eye(4)
                    Tz180[:3, :3] = R.from_euler('z', 180, degrees=True).as_matrix()
                    # Apply rotation in wrist's local frame
                    self.static_camera_pose = self.static_camera_pose @ Tz180

            elif camera == 'wrist_camera' and not self.wrist_camera_depth_future.done():
                #self.wrist_camera_depth_image_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')
                depth_float32 = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                depth_float32 = np.ascontiguousarray(depth_float32)  # already float32
                #depth_float32 = cv2.flip(depth_float32, -1)
                # Expect HxW = 1080x1920
                #if depth_float32.ndim != 2 or depth_float32.shape != (1080, 1920):
                if depth_float32.ndim != 2 or depth_float32.shape != (720, 1280):
                    print(f"DEPTH FLOAT SHAPE BAD: {depth_float32.shape}")
                    self.node.get_logger().warn(
                        f"Discarding wrist depth frame with shape {depth_float32.shape}, expected (1080, 1920)"
                    )
                    return
                else:
                    print(f"DEPTH FLOAT SHAPE: {depth_float32.shape}")
                
                
                if(self.simulation==True):
                    self.wrist_camera_depth_image_raw = (depth_float32 * 1000).astype(np.uint16)
                else:
                    self.wrist_camera_depth_image_raw = (depth_float32).astype(np.uint16)
                    
                if not (self.check_message(self.wrist_camera_depth_image_raw)): return
                
                self.wrist_camera_pose = self.lookup_transform(source=self.wrist_camera_link)
                if(self.wrist_camera_pose is not None):
                    self.wrist_camera_depth_future.set_result(True)
                    self.node.get_logger().info("Received wrist depth image")
                    
                    Tz180 = np.eye(4)
                    Tz180[:3, :3] = R.from_euler('z', 180, degrees=True).as_matrix()
                    # Apply rotation in wrist's local frame
                    self.wrist_camera_pose = self.wrist_camera_pose @ Tz180
                else:
                    print("No wrist transform found")
                
    def _camera_info_cb(self, msg, camera):
        if camera == 'static_camera' and not self.static_camera_intrinsics_future.done():
            K = np.array(msg.k, dtype=np.float32).reshape((3, 3))
            self.static_camera_intrinsics = K
            self.static_camera_intrinsics_future.set_result(True)
            self.node.get_logger().info("Received static camera info")
        elif camera == 'wrist_camera' and not self.wrist_camera_intrinsics_future.done():
            K = np.array(msg.k, dtype=np.float32).reshape((3, 3))
            self.wrist_camera_intrinsics = K
            self.wrist_camera_intrinsics_future.set_result(True)
            self.node.get_logger().info("Received wrist camera info")

    def _wait_for_images(self, selected_camera="wrist"):
        while rclpy.ok():
            # Evaluate static condition only if it's specified
            if (selected_camera=="static"):
                if(
                    self.static_camera_color_future.done() and
                    self.static_camera_depth_future.done() and
                    self.static_camera_intrinsics_future.done()
                    ):
                    break

            # Evaluate wrist condition only if it's specified
            if (selected_camera=="wrist"):
                if(
                    self.wrist_camera_color_future.done() and
                    self.wrist_camera_depth_future.done() and
                    self.wrist_camera_intrinsics_future.done()
                    ):
                    break
            # print("WRIST: intrincics: ",self.wrist_camera_intrinsics_future.done())
            # print("WRIST: depth: ",self.wrist_camera_depth_future.done())
            # print("WRIST: rgb: ",self.wrist_camera_color_future.done())
            # print("STATIC: intrincics: ",self.static_camera_intrinsics_future.done())
            # print("STATIC: depth: ",self.static_camera_depth_future.done())
            # print("STATIC: rgb: ",self.static_camera_color_future.done())
            
            #self.node.get_logger().info("Waiting")
            rclpy.spin_once(self.node, timeout_sec=0.1)  # Spins once to process messages but won't exit the loop until both are received

        self.node.get_logger().info("Got both images!")
    
    def update_map_static(self):
        T_path = f"{self.extrinsics_save_dir}T_static_cam.npy"
        T_static_cam = np.load(T_path)
        pose = self.static_camera_pose @ T_static_cam
        self.reconstruction.update_vbg(depth=self.static_camera_depth_image_raw, intrinsic=self.static_camera_intrinsics[:3,:3], pose=pose, color=self.static_camera_color_image_raw)

    def update_map_wrist(self):
        T_path = f"{self.extrinsics_save_dir}T_wrist_cam.npy"
        T_wrist_cam = np.load(T_path)
        pose = self.wrist_camera_pose @ T_wrist_cam
        self.reconstruction.update_vbg(depth=self.wrist_camera_depth_image_raw, intrinsic=self.wrist_camera_intrinsics[:3,:3], pose=pose, color=self.wrist_camera_color_image_raw)
    
    def extract_pcl(self, show=False):
        mesh, label = self.reconstruction.extract_triangle_mesh()
        mypcl, labels, weights = self.reconstruction.extract_point_cloud(return_weight=True)
        
        self.points = mypcl
        
        if(show):
            world_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.3, origin=[0, 0, 0])
            which_to_plot = []
            if(self.static_camera_pose is not None):
                camera_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2)
                camera_frame.transform(self.static_camera_pose)
                which_to_plot.append("static")
            if(self.wrist_camera_pose is not None):
                camera_frame2 = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.2)
                camera_frame2.transform(self.wrist_camera_pose)
                which_to_plot.append("wrist")
                
            if("static" in which_to_plot and "wrist" in which_to_plot):
                o3d.visualization.draw_geometries([mesh, world_frame, camera_frame, camera_frame2])
            elif("static" in which_to_plot):
                o3d.visualization.draw_geometries([mesh, world_frame, camera_frame]) 
            elif("wrist" in which_to_plot):
                o3d.visualization.draw_geometries([mesh, world_frame, camera_frame2])
            
        return mesh, weights
    
    def free_contruction_memory(self):
        # deletes the reconstruction - frees memory on gpu / (cpu if specified)
        del self.reconstruction
        
    def process_new_data(self, selected_camera="wrist",show=True, dummy="0", save_dir=""):
        if(selected_camera == "wrist"):
            self.wrist_camera_color_future = Future()
            self.wrist_camera_color_image_raw = None
            self.wrist_camera_depth_future = Future()
            self.wrist_camera_depth_image_raw = None
            self.wrist_camera_intrinsics_future = Future()
            self.wrist_camera_pose = None
            self.wrist_camera_intrinsics = None
        elif(selected_camera == "static"):
            self.static_camera_color_future = Future()
            self.static_camera_color_image_raw = None
            self.static_camera_depth_future = Future()
            self.static_camera_depth_image_raw = None
            self.static_camera_intrinsics_future = Future()
            self.static_camera_pose = None
            self.static_camera_intrinsics = None
        
        self._wait_for_images(selected_camera=selected_camera)
        
        if(selected_camera == "static"):
            self.update_map_static()
            if(save_dir!=""):
                depth_path = f"{save_dir}depth_static.npy"
                rgb_path= f"{save_dir}rgb_static.npy"
                intr_path = f"{save_dir}intrinsics_static.npy"
                pose_path = f"{save_dir}pose_static.npy"

                np.save(depth_path, self.static_camera_depth_image_raw)
                np.save(rgb_path, self.static_camera_color_image_raw)
                np.save(intr_path, self.static_camera_intrinsics[:3, :3])
                np.save(pose_path, self.static_camera_pose)
                print(f"Saved wrist depth, intrinsics & pose to {depth_path}, {intr_path}, {pose_path}")
                
            print("updated static")
        if(selected_camera == "wrist"):
            self.update_map_wrist()
            if(save_dir!=""):
                os.makedirs(save_dir, exist_ok=True)   # ✅ ensures directory exists
                
                depth_path = f"{save_dir}depth_wrist_{dummy}.npy"
                rgb_path= f"{save_dir}rgb_wrist_{dummy}.npy"
                intr_path = f"{save_dir}intrinsics_wrist_{dummy}.npy"
                pose_path = f"{save_dir}pose_wrist_{dummy}.npy"

                np.save(depth_path, self.wrist_camera_depth_image_raw)
                np.save(rgb_path, self.wrist_camera_color_image_raw)
                np.save(intr_path, self.wrist_camera_intrinsics[:3, :3])
                np.save(pose_path, self.wrist_camera_pose)
                print(f"Saved wrist depth, intrinsics & pose to {depth_path}, {intr_path}, {pose_path}")
            
            print("updated wrist")
        
        mesh, weights = self.extract_pcl(show=show)
        return self.points, mesh, weights
        


def main(args=None):
    rclpy.init(args=args)
    
    node = Node('grasping_area_reconstruction')
    tf_buffer = Buffer()
    tf_listener = TransformListener(tf_buffer, node)
    grasper = GraspingAreaReconstruction_Interface(node, tf_buffer, tf_listener)

    try:
        while rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()