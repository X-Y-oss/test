import rclpy
from rclpy.node import Node
from rclpy.task import Future
from sensor_msgs.msg import Image
from functools import partial
from cv_bridge import CvBridge
import numpy as np
from placeability_scoring.mapping.mapping_Marques.reconstruction import Reconstruction
import open3d as o3d
from scipy.spatial.transform import Rotation as R
from sensor_msgs.msg import CameraInfo
from tf2_ros import Buffer, TransformListener
from rclpy.duration import Duration
import os


class PlacingAreaReconstruction_Interface():
    def __init__(self, 
                 node: Node, 
                 simulation = False, 
                 topics: dict = {"wrist_camera_rgb_topic": '/wrist_camera/color/image_raw',
                                                "wrist_camera_segmentation_topic": '/wrist_camera/color/segmentation',
                                                 "wrist_camera_depth_topic": '/wrist_camera/depth/image_raw',
                                                 "wrist_camera_camera_info_topic": '/wrist_camera/camera_info'}, 
                 rgb_used=True,
                 camera_links = {"wrist": "wrist_3_link",
                                 "static": "base_link"},
                 extrinsics_save_dir = "/home/ws/src/placeability_scoring/placeability_scoring/camera_extrinsics/"
                 ):
        self.node = node
        
        self.T_wrist_cam = np.load(f"{extrinsics_save_dir}/T_wrist_cam.npy")
        
        
        try:
            self.tf_buffer = self.node.tf_buffer
            self.tf_listener = self.node.tf_listener
        except:
            self.tf_buffer = Buffer()
            self.tf_listener = TransformListener(self.tf_buffer, node)
        
        self.rgb_used = rgb_used
        if(self.rgb_used==False):
            self.segmentation_topic = topics['wrist_camera_segmentation_topic']
        self.rgb_topic = topics['wrist_camera_rgb_topic']
        self.depth_topic = topics['wrist_camera_depth_topic']
        self.camera_info_topic = topics['wrist_camera_camera_info_topic']
        
        
        
        self.simulation = simulation
        
        self.camera_link = camera_links["wrist"] #"wrist_3_link" -> "camera_color_optical_frame"
        
        # reconstruction parameters
        voxel_size = 0.005
        res = 8
        depth_scale = 1000.0
        depth_max = 1.3
        weight_threshold = 0.1
        block_count = 100000
        self.label_n = 12
        
        self.reconstruction = Reconstruction(
            depth_scale = depth_scale,
            depth_max=depth_max,
            res = res,
            voxel_size = voxel_size,
            #n_labels = self.label_n,
            integrate_color = True,
            device = o3d.core.Device('CPU:0'), #CUDA:0 -> Faster, CPU:0 -> more memory
            miu = 0.001, # Laplace smoothing factor
            weight_threshold=weight_threshold,
            block_count=block_count
        )
        
        self.reset_data()
        self.make_subscriber()

        self.camera_color_image_raw = None
        self.camera_depth_image_raw = None
        self.camera_intrinsics = None
        
        
        # Create the CvBridge object to convert the ROS Image message to OpenCV
        self.bridge = CvBridge()
        
        print("Init placing area done")
        
    def lookup_transform(self, source=""):
        while rclpy.ok():
            transform = self.tf_buffer.lookup_transform(
                    'world', source, rclpy.time.Time(),
                    timeout=Duration(seconds=0.5)
                )
            self.node.get_logger().info(f"Transform:\n{transform}")
            
            # make it matrix
            t = transform.transform.translation
            q = transform.transform.rotation    
            r = R.from_quat([q.x, q.y, q.z, q.w]).as_matrix()
            flip_y = np.diag([1, -1, 1])
            r = r @ flip_y
            flip_x = np.diag([-1, 1, 1])
            r = r @ flip_x
            T = np.eye(4)
            T[0:3, 0:3] = r
            T[0:3, 3] = [t.x, t.y, t.z]
            return T
            

    def reset_data(self):
        self.camera_color_future = Future()
        self.camera_color_image_raw = None
        self.camera_depth_image_raw = None
        self.camera_intrinsics = None
        self.camera_depth_future = Future()
        self.camera_intrinsics_future = Future()
        self.camera_pose = None

    def make_subscriber(self):
        # Subscriber
        if(self.rgb_used==True):
            self.image_sub_1 = self.node.create_subscription(
                Image,
                self.rgb_topic,
                partial(self._image_callback, camera='camera', depth=False),
                1
            )
        else:
            self.image_sub_1 = self.node.create_subscription(
                Image,
                self.segmentation_topic,
                partial(self._image_callback, camera='camera', depth=False),
                1
            )
        self.depth_sub_1 = self.node.create_subscription(
            Image,
            self.depth_topic,
            partial(self._image_callback, camera='camera', depth=True),
            1
        )
        self.info_sub_1 = self.node.create_subscription(
            CameraInfo,
            self.camera_info_topic,
            partial(self._camera_info_cb, camera='camera'),
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
            if camera == 'camera' and not self.camera_color_future.done():
                self.camera_color_image_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='rgb8')
                
                # camera_image_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='mono8')
                
                # self.camera_image_raw = camera_image_raw.copy()
                
                # # One-hot encode using NumPy
                # self.camera_semantic_image_raw = np.eye(self.label_n, dtype=np.float32)[self.camera_image_raw]
                
                # # get color
                # self.camera_color_image_raw = color_map[self.camera_image_raw]
                
                if not (self.check_message(self.camera_color_image_raw)): return
                self.camera_color_future.set_result(True)
                #self.node.destroy_subscription(self.image_sub_1)
                self.node.get_logger().info("Received image")

        if depth:
            if camera == 'camera' and not self.camera_depth_future.done():
                #self.camera_depth_image_raw = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')
                depth_float32 = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
                depth_float32 = np.ascontiguousarray(depth_float32)  # already float32
                #depth_float32 = cv2.flip(depth_float32, -1)
                if(self.simulation):
                    self.camera_depth_image_raw = (depth_float32 * 1000).astype(np.uint16)
                else:
                    self.camera_depth_image_raw = (depth_float32).astype(np.uint16)
                    
                
                if not (self.check_message(self.camera_depth_image_raw)):
                    return
                

                self.camera_pose = self.lookup_transform(source=self.camera_link)
                if(self.camera_pose is not None):
                    print("TRANSFORM: ",self.camera_pose)
                    self.camera_depth_future.set_result(True)
                    #self.node.destroy_subscription(self.depth_sub_1)
                    self.node.get_logger().info("Received depth image")
                    
                    Tz180 = np.eye(4)
                    Tz180[:3, :3] = R.from_euler('z', 180, degrees=True).as_matrix()
                    # Apply rotation in wrist's local frame
                    self.camera_pose = self.camera_pose @ Tz180


    def _camera_info_cb(self, msg, camera):
        if camera == 'camera' and not self.camera_intrinsics_future.done():
            K = np.array(msg.k, dtype=np.float32).reshape((3, 3))
            self.camera_intrinsics = K
            self.camera_intrinsics_future.set_result(True)
            #self.node.destroy_subscription(self.info_sub_1)
            self.node.get_logger().info("Received camera info")

    def _wait_for_images(self):
        while rclpy.ok():
            # Evaluate camera condition only if it's specified
            cond = (
                not self.camera_color_future.done() or
                not self.camera_depth_future.done() or
                not self.camera_intrinsics_future.done() or
                self.camera_pose is None
            )

            # If all required conditions are met, break the loop
            if not cond:
                break
            
            #self.node.get_logger().info("Waiting")
            rclpy.spin_once(self.node, timeout_sec=0.1)  # Spins once to process messages but won't exit the loop until both are received

        self.node.get_logger().info("Got both images!")
    
    def update_map(self):
        pose = self.camera_pose @ self.T_wrist_cam
        #self.reconstruction.update_vbg(self.camera_depth_image_raw, intrinsic=self.camera_intrinsics[:3,:3], pose=pose, color=self.camera_color_image_raw, semantic_label=self.camera_semantic_image_raw.astype(np.float32))
        self.reconstruction.update_vbg(self.camera_depth_image_raw, intrinsic=self.camera_intrinsics[:3,:3], pose=pose, color=self.camera_color_image_raw)

    def extract_pointcloud(self):
        pointcloud, labels = self.reconstruction.extract_point_cloud()
        if(self.rgb_used==True):
            labeled_pointcloud = None
        else:
            print("labels shape  ",labels.shape)
            assigned_labels = np.argmax(labels, axis=1)
            labeled_pointcloud = assigned_labels.astype(np.float32)
        
        return pointcloud, labeled_pointcloud

    def extract_mesh(self):
        mesh, label = self.reconstruction.extract_triangle_mesh()
        return mesh
    
    def free_contruction_memory(self):
        # deletes the reconstruction - frees memory on gpu / (cpu if specified)
        del self.reconstruction
        
    def process_new_data(self, returning=True, dummy="0", save_dir=""):
        
        self.reset_data()
        
        self._wait_for_images()
        
        self.update_map()
        
        if(save_dir!=""):
            os.makedirs(save_dir, exist_ok=True)   # ✅ ensures directory exists
            
            depth_path = f"{save_dir}placement_depth_{dummy}.npy"
            rgb_path= f"{save_dir}placement_rgb_{dummy}.npy"
            intr_path = f"{save_dir}placement_intrinsics_{dummy}.npy"
            pose_path = f"{save_dir}placement_pose_{dummy}.npy"

            np.save(depth_path, self.camera_depth_image_raw)
            np.save(rgb_path, self.camera_color_image_raw)
            np.save(intr_path, self.camera_intrinsics[:3, :3])
            np.save(pose_path, self.camera_pose)
            print(f"Saved placement rgb, depth, intrinsics & pose to {save_dir}")
        
        
        
        if(returning==True):
            pointcloud, labeled_pointcloud = self.extract_pointcloud()
            mesh = self.extract_mesh()
            return pointcloud, labeled_pointcloud, mesh
    

##################################### TEST ######################################
def main(args=None):
    rclpy.init(args=args)
    
    node = Node('placing_area_reconstruction')
    tf_buffer = Buffer()
    tf_listener = TransformListener(tf_buffer, node)
    
    
    topics = {"wrist_camera_rgb_topic": '/camera/color/segmentation',
                "wrist_camera_depth_topic": '/camera/aligned_depth_to_color/image_raw',
                "wrist_camera_camera_info_topic": '/camera/aligned_depth_to_color/camera_info'}
    
    
    placer = PlacingAreaReconstruction_Interface(node, topics=topics)

    pointcloud, labeled_pointcloud, mesh = placer.process_new_data(returning=True)
    
    
    print("done")
    o3d.visualization.draw_geometries([pointcloud])
    o3d.visualization.draw_geometries([mesh])

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