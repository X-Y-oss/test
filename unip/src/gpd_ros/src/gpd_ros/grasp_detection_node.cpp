#include <rclcpp/rclcpp.hpp>
#include "gpd_ros/grasp_detection_node.hpp"


GraspDetectionNode::GraspDetectionNode()
: Node("grasp_detection_node"),
  size_left_cloud_(0),           // Initialize size_left_cloud_ first
  has_cloud_(false),             // Initialize has_cloud_ second
  has_normals_(false),           // Initialize has_normals_ third
  has_samples_(true),            // Initialize has_samples_ fourth
  frame_("")                  // Initialize frame_ fifth
{
  RCLCPP_INFO(this->get_logger(), "Initializing GraspDetectionNode...");


  // static constexpr int POINT_CLOUD_2 = 0; ///< sensor_msgs/PointCloud2
  static constexpr int CLOUD_INDEXED = 1; ///< cloud with indices
  static constexpr int CLOUD_SAMPLES = 2; ///< cloud with (x,y,z) samples


  cloud_camera_ = nullptr;

  // Declare parameters with default values
  this->declare_parameter<std::string>("config_file", "");
  this->declare_parameter<int>("cloud_type", CLOUD_SAMPLES);
  this->declare_parameter<std::string>("cloud_topic", "/camera/depth_registered/points");
  this->declare_parameter<std::string>("samples_topic", "");
  this->declare_parameter<std::string>("rviz_topic", "plot_grasps");

  // Get parameters
  std::string cfg_file = this->get_parameter("config_file").as_string();
  int cloud_type = this->get_parameter("cloud_type").as_int();
  std::string cloud_topic = this->get_parameter("cloud_topic").as_string();
  std::string samples_topic = this->get_parameter("samples_topic").as_string();
  std::string rviz_topic = this->get_parameter("rviz_topic").as_string();

  // Initialize GPD grasp detector
  grasp_detector_ = std::make_shared<gpd::GraspDetector>(cfg_file);
  // grasp_detector_ = new gpd::GraspDetector(cfg_file);
  RCLCPP_INFO(this->get_logger(), "Created GPD Grasp Detector");

  // Create RViz publisher if topic is set
  if (!rviz_topic.empty()) {
      //grasps_rviz_pub_ = this->create_publisher<visualization_msgs::msg::MarkerArray>(rviz_topic, 1);
      use_rviz_ = true;
  } else {
      use_rviz_ = false;
  }

  // Subscribe to input point cloud topic
  // PointCloud2 might not be correct here - Benno
  // if (cloud_type == POINT_CLOUD_2) {
  //     cloud_sub_ = this->create_subscription<sensor_msgs::msg::PointCloud2>(
  //         cloud_topic, 1, std::bind(&GraspDetectionNode::cloud_callback, this, std::placeholders::_1));
  // }
  if (cloud_type == CLOUD_INDEXED) {
      RCLCPP_INFO(this->get_logger(), "Using Cloud Indexed");
      cloud_sub_ = this->create_subscription<gpd_ros_messages::msg::CloudIndexed>(
          cloud_topic, 1, std::bind(&GraspDetectionNode::cloud_indexed_callback, this, std::placeholders::_1));
  }
  else if (cloud_type == CLOUD_SAMPLES) {
      RCLCPP_INFO(this->get_logger(), "Using Cloud Samples");
      cloud_sub_ = this->create_subscription<gpd_ros_messages::msg::CloudSamples>(
          cloud_topic, 1, std::bind(&GraspDetectionNode::cloud_samples_callback, this, std::placeholders::_1));
      has_samples_ = false;
  }

  // Subscribe to input samples topic
  if (!samples_topic.empty()) {
      RCLCPP_INFO(this->get_logger(), "Samples topic should not be here");
      samples_sub_ = this->create_subscription<gpd_ros_messages::msg::SamplesMsg>(
      samples_topic, 1, std::bind(&GraspDetectionNode::samples_callback, this, std::placeholders::_1));
      has_samples_ = false;
  }

  // Publisher for grasp configurations
  grasps_pub_ = this->create_publisher<gpd_ros_messages::msg::GraspConfigList>("clustered_grasps", 10);

  // Not sure if needed for funcionality - Benno
  // TODO
  //rviz_plotter_ = std::make_shared<GraspPlotter>(this, grasp_detector_->getHandSearchParameters().hand_geometry_);

  RCLCPP_INFO(this->get_logger(), "GraspDetectionNode successfully initialized.");
}


void GraspDetectionNode::run()
{
  rclcpp::Rate rate(100);  // ROS 2 uses rclcpp::Rate instead of ros::Rate
  RCLCPP_INFO(this->get_logger(), "Waiting for point cloud to arrive ...");

  while (rclcpp::ok()) {  // ROS 2 uses rclcpp::ok() instead of ros::ok()
    if (has_cloud_) {
      // Detect grasps in point cloud.
      std::vector<std::unique_ptr<gpd::candidate::Hand>> grasps = detectGraspPoses();

      // Visualize the detected grasps in rviz.
      // if (use_rviz_) {
      //   rviz_plotter_->drawGrasps(grasps, frame_);
      // }

      // Reset the system.
      has_cloud_ = false;
      has_samples_ = false;
      has_normals_ = false;
      RCLCPP_INFO(this->get_logger(), "Waiting for point cloud to arrive ...");
    }

    rclcpp::spin_some(shared_from_this());  // This is the ROS 2 equivalent of ros::spinOnce()
    rate.sleep();
  }
}


std::vector<std::unique_ptr<gpd::candidate::Hand>> GraspDetectionNode::detectGraspPoses()
{
  std::vector<std::unique_ptr<gpd::candidate::Hand>> grasps;

  // Preprocess the point cloud
  grasp_detector_->preprocessPointCloud(*cloud_camera_);

  // Detect grasps in the point cloud
  grasps = grasp_detector_->detectGrasps(*cloud_camera_);

  // Publish the selected grasps
  gpd_ros_messages::msg::GraspConfigList selected_grasps_msg = GraspMessages::createGraspListMsg(grasps, cloud_camera_header_);
  grasps_pub_->publish(selected_grasps_msg);
  RCLCPP_INFO_STREAM(this->get_logger(), "Published " + std::to_string(selected_grasps_msg.grasps.size()) + " highest-scoring grasps.");


  return grasps;
}

// Function to get samples in a ball around the centroid
std::vector<int> GraspDetectionNode::getSamplesInBall(const pcl::PointCloud<pcl::PointXYZRGBA>::Ptr& cloud,
  const pcl::PointXYZRGBA& centroid, float radius)
{
  std::vector<int> indices;
  std::vector<float> dists;
  pcl::KdTreeFLANN<pcl::PointXYZRGBA> kdtree;
  kdtree.setInputCloud(cloud);
  kdtree.radiusSearch(centroid, radius, indices, dists);
  return indices;
}

// void GraspDetectionNode::cloud_callback(const sensor_msgs::PointCloud2& msg)
// {
//   if (!has_cloud_)
//   {
//     // Instead of manually deleting, handle memory via smart pointers
//     cloud_camera_ = nullptr;

//     Eigen::Matrix3Xd view_points(3,1);
//     view_points.col(0) = view_point_;

//     // Check for fields in the message
//     if (msg->fields.size() == 6 && msg->fields[3].name == "normal_x" &&
//         msg->fields[4].name == "normal_y" && msg->fields[5].name == "normal_z")
//     {
//       PointCloudPointNormal::Ptr cloud(new PointCloudPointNormal);
//       pcl::fromROSMsg(*msg, *cloud);
//       cloud_camera_ = std::make_shared<gpd::util::Cloud>(cloud, 0, view_points);
//       cloud_camera_header_ = msg->header;
//       RCLCPP_INFO_STREAM(this->get_logger(), "Received cloud with " << cloud_camera_->getCloudProcessed()->size() << " points and normals.");
//     }
//     else
//     {
//       PointCloudRGBA::Ptr cloud(new PointCloudRGBA);
//       pcl::fromROSMsg(*msg, *cloud);
//       cloud_camera_ = std::make_shared<gpd::util::Cloud>(cloud, 0, view_points);
//       cloud_camera_header_ = msg->header;
//       RCLCPP_INFO_STREAM(this->get_logger(), "Received cloud with " << cloud_camera_->getCloudProcessed()->size() << " points.");
//     }

//     has_cloud_ = true;
//     frame_ = msg.header.frame_id;
//   }
// }


void GraspDetectionNode::cloud_indexed_callback(const gpd_ros_messages::msg::CloudIndexed::SharedPtr msg)
{
  if (!has_cloud_)
  {
    initCloudCamera(std::make_shared<gpd_ros_messages::msg::CloudSources>(msg->cloud_sources));

    // Set the indices at which to sample grasp candidates.
    std::vector<int> indices(msg->indices.size());
    // for (size_t i = 0; i < indices.size(); i++)
    // {
    //   indices[i] = msg->indices[i].data;
    // }
    for (size_t i = 0; i < msg->indices.size(); i++) {
      indices[i] = static_cast<int>(msg->indices[i].data);  // cast if your API wants int
    }
    cloud_camera_->setSampleIndices(indices);

    has_cloud_ = true;
    frame_ = msg->cloud_sources.cloud.header.frame_id;

    RCLCPP_INFO_STREAM(this->get_logger(), "Received cloud with " << cloud_camera_->getCloudProcessed()->size() << " points, and "
        << msg->indices.size() << " samples");
  }
  else{
    RCLCPP_INFO_STREAM(this->get_logger(), "Cloud indice callback, but cloud was empty!");
  }
}


void GraspDetectionNode::cloud_samples_callback(const gpd_ros_messages::msg::CloudSamples::SharedPtr msg)
{
  if (!has_cloud_)
  {
    initCloudCamera(std::make_shared<gpd_ros_messages::msg::CloudSources>(msg->cloud_sources));

    // Set the samples at which to sample grasp candidates.
    Eigen::Matrix3Xd samples(3, msg->samples.size());
    for (size_t i = 0; i < msg->samples.size(); i++)
    {
      samples.col(i) << msg->samples[i].x, msg->samples[i].y, msg->samples[i].z;
    }
    cloud_camera_->setSamples(samples);

    has_cloud_ = true;
    has_samples_ = true;
    frame_ = msg->cloud_sources.cloud.header.frame_id;

    RCLCPP_INFO_STREAM(this->get_logger(), "Received cloud with " << cloud_camera_->getCloudProcessed()->size() << " points, and "
        << cloud_camera_->getSamples().cols() << " samples");
  }
  else{
    RCLCPP_INFO_STREAM(this->get_logger(), "Cloud sample callback, but cloud was empty!");
  }
}


void GraspDetectionNode::samples_callback(const gpd_ros_messages::msg::SamplesMsg::SharedPtr msg)
{
  if (!has_samples_)
  {
    Eigen::Matrix3Xd samples(3, msg->samples.size());

    for (size_t i = 0; i < msg->samples.size(); i++)
    {
      samples.col(i) << msg->samples[i].x, msg->samples[i].y, msg->samples[i].z;
    }

    cloud_camera_->setSamples(samples);
    has_samples_ = true;

    RCLCPP_INFO_STREAM(this->get_logger(), "Received grasp samples message with " << msg->samples.size() << " samples");
  }
}


void GraspDetectionNode::initCloudCamera(const gpd_ros_messages::msg::CloudSources::SharedPtr msg)
{
  // No need for delete; smart pointer takes care of cleanup
  cloud_camera_ = nullptr;

  // Set view points.
  Eigen::Matrix3Xd view_points(3, msg->view_points.size());
  for (size_t i = 0; i < msg->view_points.size(); i++)
  {
    view_points.col(i) << msg->view_points[i].x, msg->view_points[i].y, msg->view_points[i].z;
  }

  // Set point cloud.
  if (msg->cloud.fields.size() == 6 && msg->cloud.fields[3].name == "normal_x"
    && msg->cloud.fields[4].name == "normal_y" && msg->cloud.fields[5].name == "normal_z")
  {
    // Create a PointCloud container with normals
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud(new pcl::PointCloud<pcl::PointNormal>);

    // Convert ROS2 PointCloud2 to PCL PointCloud with normals
    pcl::fromROSMsg(msg->cloud, *cloud);

    // TODO: multiple cameras can see the same point
    Eigen::MatrixXi camera_source = Eigen::MatrixXi::Zero(view_points.cols(), cloud->size());
    for (size_t i = 0; i < msg->camera_source.size(); i++)
    {
      camera_source(msg->camera_source[i].data, i) = 1;
    }

    cloud_camera_ = new gpd::util::Cloud(cloud, camera_source, view_points);
  }
  else
  {
    // Create a PointCloud container with normals
    pcl::PointCloud<pcl::PointNormal>::Ptr cloud(new pcl::PointCloud<pcl::PointNormal>);

    // Convert ROS2 PointCloud2 to PCL PointCloud with normals
    pcl::fromROSMsg(msg->cloud, *cloud);

    // TODO: multiple cameras can see the same point
    Eigen::MatrixXi camera_source = Eigen::MatrixXi::Zero(view_points.cols(), cloud->size());
    for (size_t i = 0; i < msg->camera_source.size(); i++)
    {
      camera_source(msg->camera_source[i].data, i) = 1;
    }

    cloud_camera_ = new gpd::util::Cloud(cloud, camera_source, view_points);
    std::cout << "view_points:\n" << view_points << "\n";
  }
}

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);

  // Create the GraspDetectionNode shared pointer
  auto grasp_detection_node = std::make_shared<GraspDetectionNode>();
  
  grasp_detection_node->run(); //spinning is inside run

  rclcpp::shutdown();
  return 0;
}