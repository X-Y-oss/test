/*
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2018, Andreas ten Pas
 *  All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions
 *  are met:
 *
 *   * Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 *   * Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the following
 *     disclaimer in the documentation and/or other materials provided
 *     with the distribution.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 *  FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 *  COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 *  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 *  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 *  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 *  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 *  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 *  POSSIBILITY OF SUCH DAMAGE.
 */

 #ifndef GRASP_DETECTION_NODE_H_
 #define GRASP_DETECTION_NODE_H_
 
 // system
 #include <algorithm>
 #include <memory>
 #include <vector>
 
 // ROS 2
 #include <rclcpp/rclcpp.hpp>
 #include <sensor_msgs/msg/point_cloud2.hpp>
 #include <pcl/common/common.h>
 #include <pcl/point_cloud.h>
 #include <visualization_msgs/msg/marker.hpp>
 #include <visualization_msgs/msg/marker_array.hpp>
 
 // PCL
 #include <pcl/point_types.h>
 #include <pcl_conversions/pcl_conversions.h>
 
 // GPD
 #include <gpd/util/cloud.h>
 #include <gpd/grasp_detector.h>
 #include <gpd/sequential_importance_sampling.h>
 
 // this project (messages)
 #include <gpd_ros_messages/msg/cloud_indexed.hpp>
 #include <gpd_ros_messages/msg/cloud_samples.hpp>
 #include <gpd_ros_messages/msg/cloud_sources.hpp>
 #include <gpd_ros_messages/msg/grasp_config.hpp>
 #include <gpd_ros_messages/msg/grasp_config_list.hpp>
 #include <gpd_ros_messages/msg/samples_msg.hpp>
 
 // this project (headers)
 #include <gpd_ros/grasp_messages.hpp>
 //#include <gpd_ros/grasp_plotter.hpp> // TODO
 
 typedef pcl::PointCloud<pcl::PointXYZRGBA> PointCloudRGBA;
 typedef pcl::PointCloud<pcl::PointNormal> PointCloudPointNormal;
 
 /** GraspDetectionNode class
  *
  * \brief A ROS 2 node that can detect grasp poses in a point cloud.
  *
  * This class is a ROS 2 node that handles all the ROS topics.
  */
 class GraspDetectionNode : public rclcpp::Node {
  public:
      GraspDetectionNode();
      ~GraspDetectionNode()
      {
        delete cloud_camera_;
        //delete grasp_detector_;
        //delete rviz_plotter_;
      }
      void run();
      std::vector<std::unique_ptr<gpd::candidate::Hand>> detectGraspPoses();
 
    private:
        std::vector<int> getSamplesInBall(const PointCloudRGBA::Ptr& cloud, const pcl::PointXYZRGBA& centroid, float radius);
        // void cloud_callback(const sensor_msgs::msg::PointCloud2::SharedPtr msg);
        void cloud_indexed_callback(const gpd_ros_messages::msg::CloudIndexed::SharedPtr msg);
        void cloud_samples_callback(const gpd_ros_messages::msg::CloudSamples::SharedPtr msg);
        void initCloudCamera(const gpd_ros_messages::msg::CloudSources::SharedPtr msg);
        void samples_callback(const gpd_ros_messages::msg::SamplesMsg::SharedPtr msg);
        // Eigen::Matrix3Xd fillMatrixFromFile(const std::string& filename, int num_normals);
      
        Eigen::Vector3d view_point_;
        std_msgs::msg::Header cloud_camera_header_;
        gpd::util::Cloud* cloud_camera_;
        int size_left_cloud_;
        bool has_cloud_, has_normals_, has_samples_;
        std::string frame_;
        
        rclcpp::SubscriptionBase::SharedPtr cloud_sub_;
        rclcpp::Subscription<gpd_ros_messages::msg::SamplesMsg>::SharedPtr samples_sub_;
        rclcpp::Publisher<gpd_ros_messages::msg::GraspConfigList>::SharedPtr grasps_pub_;
        rclcpp::Publisher<visualization_msgs::msg::MarkerArray>::SharedPtr grasps_rviz_pub_;
        
        bool use_rviz_;
        //std::vector<double> workspace_;
      
        std::shared_ptr<gpd::GraspDetector> grasp_detector_;
        //GraspPlotter* rviz_plotter_;
  };
 
 #endif /* GRASP_DETECTION_NODE_H_ */
 