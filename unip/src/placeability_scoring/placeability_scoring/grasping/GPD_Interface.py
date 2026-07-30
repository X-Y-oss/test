import numpy as np
import rclpy
from rclpy.node import Node

from gpd_ros_messages.msg import CloudIndexed, CloudSources
from gpd_ros_messages.msg import GraspConfigList
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
import sensor_msgs_py.point_cloud2 as pc2
from std_msgs.msg import Int64
from geometry_msgs.msg import Point
import time


def GPD_grasp_to_transform(grasp_values):
    """
    Convert GPD grasp values to a 4x4 homogeneous transform.
    Args: grasp_values (list): List of 17 values as defined by GPD.
    Returns: np.ndarray: 4x4 homogeneous transformation matrix.
    """
    assert len(grasp_values) >= 17, "Expected at least 17 values from GPD"

    # Extract components
    position = np.array(grasp_values[0:3])
    approach = np.array(grasp_values[3:6])     # X-axis
    binormal = np.array(grasp_values[6:9])     # Y-axis
    axis = np.array(grasp_values[9:12])        # Z-axis

    # Normalize to be safe
    x_axis = approach / np.linalg.norm(approach)
    y_axis = binormal / np.linalg.norm(binormal)
    z_axis = axis / np.linalg.norm(axis)

    # Build rotation matrix (columns = [x y z])
    R = np.column_stack((x_axis, y_axis, z_axis))

    # Assemble full transform
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = position

    return T, grasp_values[13] #T, score

class GPD_Interface():
    def __init__(self, node: Node):
        self.node = node
        
        self.shift = np.array([0.0, 0.0, 0.0])
        
        # Create a publisher
        self.publisher = self.node.create_publisher(CloudIndexed, '/cloud_stitched', 1)
        self.publisher_point_cloud = self.node.create_publisher(PointCloud2, '/object_pointcloud', 1)
        self.node.get_logger().info('gpd_pointcloud_publisher started')
        
        # Get the downsampled points
        self.grasps = np.empty((0, 17))
        
        self.grasp_subscriber = self.node.create_subscription(
            GraspConfigList,  # The message type is GraspConfigList
            '/clustered_grasps',  # The topic name
            self.grasp_callback,
            1  # QoS (Quality of Service) depth
        )
        
    def wait_for_grasps(self):
        last_publish_time = time.time()
        while rclpy.ok():
            if(self.grasps.shape[0] != 0):
                self.node.get_logger().info("Pose reached.")
                return self.grasps
            
            current_time = time.time()
            if current_time - last_publish_time >= 10.0:
                #self.publisher.publish(self.msg)
                #print("Publishing again, due to no received grasps")
                print("Waiting for grasps")
                last_publish_time = current_time
            rclpy.spin_once(self.node, timeout_sec=0.1)
        
    def publish_cloud_indexed(self, target, indices, use_all=True):
        # --- sanitize ---
        if(use_all==False):
            target = np.asarray(target, dtype=np.float32).reshape(-1, 3)
            indices = np.asarray(indices, dtype=np.int64).ravel()
            assert len(target) > 0, "target is empty"
            assert (indices >= 0).all() and (indices < len(target)).all(), "indices out of bounds"
            # Optional: enforce unique, stable order
            # indices = np.unique(indices)

            # --- cut down to selected points only ---
            target = target[indices]                 # shape (N', 3)
            N_sel = len(target)
            if N_sel == 0:
                self.node.get_logger().warn("No points selected; not publishing.")
                return
        
        # Create CloudIndexed message
        self.msg = CloudIndexed()
        # Create dummy CloudSources message
        cloud_sources_msg = CloudSources()
        # Populate sensor_msgs/PointCloud2 with dummy data
        cloud_msg = PointCloud2()
        header = Header()
        header.stamp = self.node.get_clock().now().to_msg()
        header.frame_id = "world"
        cloud_msg.fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1)
        ]
        cloud_msg = pc2.create_cloud(header, 
                             fields=[PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
                                     PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
                                     PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1)],
                             points=zip(target[:,0], target[:,1], target[:,2]))
        #self.publisher_point_cloud.publish(cloud_msg)
        cloud_sources_msg.cloud = cloud_msg
        # Create a list of camera indices #currently all 0
        cloud_sources_msg.camera_source = [Int64(data=0) for i in range(len(target))]
        # Create dummy view points (positions of cameras)
        cloud_sources_msg.view_points = [Point(x=0.3, y=0.3, z=0.3)]
        # Assign CloudSources to CloudIndexed message
        self.msg.cloud_sources = cloud_sources_msg
        # all indices for sampling grasp candidates
        if(use_all==True):
            self.msg.indices = [Int64(data=int(i)) for i in range(len(target))]
        else:
            self.msg.indices = [Int64(data=int(i)) for i in indices]

        # Publish the message
        self.publisher.publish(self.msg)
        self.node.get_logger().info(f"Published CloudIndexed message")
        
        
    def grasp_callback(self, msg):
        """Takes output from gpd and saves it in get_grasps so it can be accessed.
        Args:
            msg (GraspConfigList): gpd grasps
        """
        grasps_data = []
        for grasp in msg.grasps:
            position = grasp.position
            approach = grasp.approach
            binormal = grasp.binormal
            axis = grasp.axis
            width = grasp.width.data  # Convert from std_msgs.msg.Float32
            score = grasp.score.data  # Convert from std_msgs.msg.Float32
            sample = grasp.sample

            # Extracting values and appending to the list
            grasp_values = [
                position.x + self.shift[0], position.y + self.shift[1], position.z + self.shift[2],  # Position
                approach.x, approach.y, approach.z,  # Approach
                binormal.x, binormal.y, binormal.z,  # Binormal
                axis.x, axis.y, axis.z,              # Axis
                width,                               # Width
                score,                               # Score
                sample.x, sample.y, sample.z         # Sample
            ]
            grasps_data.append(grasp_values)
        # Convert the list of grasps data into a numpy array
        self.grasps = np.array(grasps_data)
        print("Received Grasps")
   
def main():
    rclpy.init()
    node = Node("gpd_cloud_launcher")
    abl = GPD_Interface(node)

    # load Nx3 point cloud
    points = np.load("ooo.npy").astype(np.float32)

    # publish all points with local indices 0..N-1
    indices = np.arange(points.shape[0], dtype=np.int64)
    abl.publish_cloud_indexed(points, indices)

    rclpy.spin_once(node, timeout_sec=0.5)  # let publisher send
    node.destroy_node()
    rclpy.shutdown()
        
if __name__ == "__main__":
    main()