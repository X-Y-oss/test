import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package="gpd_ros",
            executable="detect_grasps",
            name="detect_grasps",
            output="screen",
            parameters=[{
                "cloud_type": 1,  # 0: PointCloud2, 1: CloudIndexed, 2: CloudSamples
                "cloud_topic": "/cloud_stitched",
                "samples_topic": "",
                "config_file": "/home/ws/gpd/cfg/ros_eigen_params.cfg",
                "rviz_topic": "plot_grasps",
            }],
        )
    ])