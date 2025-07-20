/*********************************************************************
 *
 * Software License Agreement (BSD License)
 *
 *  Copyright (c) 2008, Robert Bosch LLC.
 *  Copyright (c) 2015-2016, Jiri Horner.
 *  Copyright (c) 2021, Carlos Alvarez, Juan Galvis.
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
 *   * Neither the name of the Jiri Horner nor the names of its
 *     contributors may be used to endorse or promote products derived
 *     from this software without specific prior written permission.
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
 *
 *********************************************************************/

#include <explore/explore.h>

#include <thread>

// ADDED: Include for quaternion math
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

// ADDED: For AprilTag detection and TF transforms
#include <apriltag_msgs/msg/april_tag_detection_array.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <set>
#include <atomic>

#include <opencv2/imgproc.hpp>

#include <angles/angles.h> // <--- ADD THIS LINE

inline static bool same_point(const geometry_msgs::msg::Point& one,
                              const geometry_msgs::msg::Point& two)
{
  double dx = one.x - two.x;
  double dy = one.y - two.y;
  double dist = sqrt(dx * dx + dy * dy);
  return dist < 0.01;
}

namespace explore
{
// MODIFIED: Constructor to initialize new components conditionally
Explore::Explore()
  : Node("explore_node")
  , tf_buffer_(this->get_clock())
  , tf_listener_(tf_buffer_)
  , costmap_client_(*this, &tf_buffer_)
  , prev_distance_(0)
  , last_markers_count_(0)
  , goal_active_(false)
  , initial_pose_set_(false)
  , apriltag_goal_active_(false)
  , record_path_mode_(false)
  , current_state_(State::EXPLORING) // NEW: Initialize state machine
{
  double timeout;
  double min_frontier_size;
  this->declare_parameter<float>("planner_frequency", 1.0);
  this->declare_parameter<float>("progress_timeout", 30.0);
  this->declare_parameter<bool>("visualize", false);
  this->declare_parameter<float>("potential_scale", 1e-3);
  this->declare_parameter<float>("orientation_scale", 0.0);
  this->declare_parameter<float>("gain_scale", 1.0);
  this->declare_parameter<float>("min_frontier_size", 0.5);
  this->declare_parameter<bool>("return_to_init", false);
  this->declare_parameter<bool>("detect_apriltag", false);
  // Using an existing string param, assuming it's declared
  // this->declare_parameter<std::string>("robot_base_frame", "base_link");


  this->get_parameter("planner_frequency", planner_frequency_);
  this->get_parameter("progress_timeout", timeout);
  this->get_parameter("visualize", visualize_);
  this->get_parameter("potential_scale", potential_scale_);
  this->get_parameter("orientation_scale", orientation_scale_);
  this->get_parameter("gain_scale", gain_scale_);
  this->get_parameter("min_frontier_size", min_frontier_size);
  this->get_parameter("return_to_init", return_to_init_);
  this->get_parameter("robot_base_frame", robot_base_frame_);
  this->get_parameter("detect_apriltag", detect_apriltag_);

  RCLCPP_INFO(logger_, "Init condition: return_to_init_=%d, detect_apriltag_=%d",
              return_to_init_, detect_apriltag_);

  progress_timeout_ = timeout;
  move_base_client_ =
      rclcpp_action::create_client<nav2_msgs::action::NavigateToPose>(
          this, ACTION_NAME);

  // NEW: Conditionally create the path computation client
  if (detect_apriltag_) {
    compute_path_client_ = 
        rclcpp_action::create_client<nav2_msgs::action::ComputePathToPose>(
            this, "compute_path_to_pose");
  }

  search_ = frontier_exploration::FrontierSearch(costmap_client_.getCostmap(),
                                                 potential_scale_, gain_scale_,
                                                 min_frontier_size);

  if (visualize_) {
    marker_array_publisher_ =
        this->create_publisher<visualization_msgs::msg::MarkerArray>("explore/frontiers", 10);
  }

  resume_subscription_ = this->create_subscription<std_msgs::msg::Bool>(
      "explore/resume", 10,
      std::bind(&Explore::resumeCallback, this, std::placeholders::_1));

  RCLCPP_INFO(logger_, "Waiting to connect to move_base nav2 server");
  move_base_client_->wait_for_action_server();
  RCLCPP_INFO(logger_, "Connected to move_base nav2 server");
  
  // NEW: Conditionally wait for the path computation server
  if (detect_apriltag_) {
    RCLCPP_INFO(logger_, "Waiting to connect to compute_path_to_pose server");
    compute_path_client_->wait_for_action_server();
    RCLCPP_INFO(logger_, "Connected to compute_path_to_pose server");
  }

  if (return_to_init_) {
    RCLCPP_INFO(logger_, "Getting initial pose of the robot");
    geometry_msgs::msg::TransformStamped transformStamped;
    std::string map_frame = costmap_client_.getGlobalFrameID();
    try {
      transformStamped = tf_buffer_.lookupTransform(
          map_frame, robot_base_frame_, tf2::TimePointZero);
      initial_pose_.position.x = transformStamped.transform.translation.x;
      initial_pose_.position.y = transformStamped.transform.translation.y;
      initial_pose_.orientation = transformStamped.transform.rotation;
      initial_pose_set_ = true;
      RCLCPP_INFO(logger_, "Initial pose saved.");
      
      // NEW: If we are in apriltag mode, store the initial pose as the first safe spot
      if (detect_apriltag_) {
        geometry_msgs::msg::PoseStamped initial_pose_stamped;
        initial_pose_stamped.header.frame_id = map_frame;
        initial_pose_stamped.header.stamp = this->now();
        initial_pose_stamped.pose = initial_pose_;
        goal_history_.push_back(initial_pose_stamped);
      }
    } catch (tf2::TransformException& ex) {
      RCLCPP_ERROR(logger_, "Couldn't find transform from %s to %s: %s",
                   map_frame.c_str(), robot_base_frame_.c_str(), ex.what());
      RCLCPP_WARN(logger_, "Cannot return to initial position if it is not known.");
      initial_pose_set_ = false;
    }
    
  }
  

  if (detect_apriltag_) {
    RCLCPP_INFO(logger_, "AprilTag detection is enabled. FORWARD-ONLY navigation is active.");
    target_apriltag_ids_ = {992, 993, 994, 995, 996, 997};
    apriltag_sub_ = std::make_shared<message_filters::Subscriber<DetectionMsg>>(this, "/apriltag_detections");
    image_sub_ = std::make_shared<message_filters::Subscriber<ImageMsg>>(this, "/ascamera/camera_publisher/rgb0/image");
    sync_ = std::make_shared<Synchronizer>(SyncPolicy(10), *apriltag_sub_, *image_sub_);
    sync_->registerCallback(std::bind(&Explore::detectionAndImageCallback, this, std::placeholders::_1, std::placeholders::_2));
    RCLCPP_INFO(logger_, "Synchronized to /apriltag_detections and image topic.");
  }

  record_path_mode_ = !detect_apriltag_ && !return_to_init_;
  if (record_path_mode_) {
    RCLCPP_INFO(logger_, "Path recording is ENABLED.");
    path_publisher_ = this->create_publisher<nav_msgs::msg::Path>(
        "explore/recorded_path", rclcpp::SystemDefaultsQoS().transient_local());
    recorded_path_.header.frame_id = costmap_client_.getGlobalFrameID();
    path_recording_timer_ = this->create_wall_timer(
        std::chrono::milliseconds(500), std::bind(&Explore::recordCurrentPose, this));
  } else {
    RCLCPP_INFO(logger_, "Path recording is DISABLED.");
  }

  exploring_timer_ = this->create_wall_timer(
      std::chrono::milliseconds((uint16_t)(1000.0 / planner_frequency_)),
      [this]() { 
        // The timer's job is to kick-start planning if we are idle.
        // It will call makePlan, which will do nothing if a goal is active.
        makePlan(); 
      });
  
  RCLCPP_INFO(logger_, "Start exploration right away");
  makePlan();
}

Explore::~Explore()
{
  stop();
}
// void Explore::apriltagCallback(const apriltag_msgs::msg::AprilTagDetectionArray::SharedPtr msg)
// {
//     // If we have already triggered the "go home" process, do nothing.
//     if (apriltag_goal_active_.load()) {
//         return;
//     }

//     const apriltag_msgs::msg::AprilTagDetection* target_detection = nullptr;

//     // Check if any of the detected tags are our target tags
//     for (const auto& detection : msg->detections) {
//         if (target_apriltag_ids_.count(detection.id)) {
//             target_detection = &detection;
//             break;
//         }
//     }

//     if (target_detection) {
//         // A target tag is in view. Let's get its precise pose from TF.
//         std::string camera_frame = msg->header.frame_id;
//         std::string tag_frame = target_detection->family + ":" + std::to_string(target_detection->id);
        
//         try {
//             // Look up the transform from the camera to the tag
//             geometry_msgs::msg::TransformStamped t_stamped = tf_buffer_.lookupTransform(
//                 camera_frame, tag_frame, tf2::TimePointZero);

//             // If the lookup succeeds, we are sure the tag is there.
//             // Set the flag to prevent this callback from re-triggering.
//             apriltag_goal_active_.store(true);
//             RCLCPP_INFO(logger_, "Target AprilTag with ID %d detected!", target_detection->id);

//             // --- Corrected Distance Calculation ---
//             // The distance is the magnitude of the translation vector in the transform.
//             const auto& translation = t_stamped.transform.translation;
//             double distance = std::sqrt(
//                 pow(translation.x, 2) + 
//                 pow(translation.y, 2) + 
//                 pow(translation.z, 2));
//             RCLCPP_INFO(logger_, "Distance to tag from camera: %.2f meters.", distance);
            
//             // Log the global location of the AprilTag (this part was already correct)
//             std::string map_frame = costmap_client_.getGlobalFrameID();
//             geometry_msgs::msg::PoseStamped tag_pose_camera;
//             tag_pose_camera.header.frame_id = camera_frame;
//             tag_pose_camera.header.stamp = t_stamped.header.stamp;
//             // tf2::fromMsg(t_stamped.transform, tag_pose_camera.pose);
//             // Manual conversion from Transform to Pose
//             tag_pose_camera.pose.position.x = t_stamped.transform.translation.x;
//             tag_pose_camera.pose.position.y = t_stamped.transform.translation.y;
//             tag_pose_camera.pose.position.z = t_stamped.transform.translation.z;
//             tag_pose_camera.pose.orientation = t_stamped.transform.rotation;
            
//             geometry_msgs::msg::PoseStamped tag_pose_map = tf_buffer_.transform(tag_pose_camera, map_frame);
//             RCLCPP_INFO(logger_, "AprilTag global location in '%s' frame: [x: %.2f, y: %.2f]",
//                         map_frame.c_str(),
//                         tag_pose_map.pose.position.x,
//                         tag_pose_map.pose.position.y);

//             // Stop exploration and return to initial pose (if enabled).
//             RCLCPP_INFO(logger_, "Stopping exploration to return home.");
//             stop(true);

//         } catch (const tf2::TransformException &ex) {
//             // This can happen if the TF message is not yet available.
//             // We log the error and do nothing, waiting for the next callback.
//             RCLCPP_WARN(logger_, "Could not get transform from %s to %s: %s",
//                          camera_frame.c_str(), tag_frame.c_str(), ex.what());
//         }
//     }
// }

  // ADDED: New method to record the robot's current pose.
void Explore::recordCurrentPose()
{
    geometry_msgs::msg::PoseStamped current_pose;
    try {
        // Get the transform from map to robot's base frame
        auto tf = tf_buffer_.lookupTransform(
            costmap_client_.getGlobalFrameID(), robot_base_frame_, tf2::TimePointZero);

        current_pose.header = tf.header;
        current_pose.pose.position.x = tf.transform.translation.x;
        current_pose.pose.position.y = tf.transform.translation.y;
        current_pose.pose.position.z = tf.transform.translation.z;
        current_pose.pose.orientation = tf.transform.rotation;

        // Only add the pose if it's different from the last one to avoid redundant points
        if (recorded_path_.poses.empty() || !same_point(current_pose.pose.position, recorded_path_.poses.back().pose.position)) {
             recorded_path_.poses.push_back(current_pose);
        }

    } catch (const tf2::TransformException &ex) {
        RCLCPP_WARN(logger_, "Could not get robot pose for path recording: %s", ex.what());
    }
}


void Explore::detectionAndImageCallback(
    const apriltag_msgs::msg::AprilTagDetectionArray::ConstSharedPtr& detection_msg,
    const sensor_msgs::msg::Image::ConstSharedPtr& image_msg)
{
    if (apriltag_goal_active_.load()) {
        return;
    }

    const apriltag_msgs::msg::AprilTagDetection* target_detection = nullptr;
    for (const auto& detection : detection_msg->detections) {
        if (target_apriltag_ids_.count(detection.id)) {
            target_detection = &detection;
            break;
        }
    }

    if (target_detection) {
        // ---- NEW: Color Detection Logic ----
        // Convert ROS Image message to OpenCV Mat
        cv_bridge::CvImagePtr cv_ptr;
        try {
            cv_ptr = cv_bridge::toCvCopy(image_msg, sensor_msgs::image_encodings::BGR8);
        } catch (cv_bridge::Exception& e) {
            RCLCPP_ERROR(logger_, "cv_bridge exception: %s", e.what());
            return;
        }

        // Call our helper function to get the color
        std::string detected_color = detectCubeColor(cv_ptr->image, *target_detection);

        // ---- End of New Logic ----


        // Use the rest of your existing logic
        std::string camera_frame = detection_msg->header.frame_id;
        std::string tag_frame = target_detection->family + ":" + std::to_string(target_detection->id);
        
        try {
            // Look up the transform from the camera to the tag
            geometry_msgs::msg::TransformStamped t_stamped = tf_buffer_.lookupTransform(
                camera_frame, tag_frame, tf2::TimePointZero);

            // If the lookup succeeds, we are sure the tag is there.
            // Set the flag to prevent this callback from re-triggering.
            apriltag_goal_active_.store(true);
            RCLCPP_INFO(logger_, "Target AprilTag with ID %d detected!", target_detection->id);

            // --- Corrected Distance Calculation ---
            // The distance is the magnitude of the translation vector in the transform.
            const auto& translation = t_stamped.transform.translation;
            double distance = std::sqrt(
                pow(translation.x, 2) + 
                pow(translation.y, 2) + 
                pow(translation.z, 2));
            RCLCPP_INFO(logger_, "Distance to tag from camera: %.2f meters.", distance);
            
            // Log the global location of the AprilTag (this part was already correct)
            std::string map_frame = costmap_client_.getGlobalFrameID();
            geometry_msgs::msg::PoseStamped tag_pose_camera;
            tag_pose_camera.header.frame_id = camera_frame;
            tag_pose_camera.header.stamp = t_stamped.header.stamp;
            // tf2::fromMsg(t_stamped.transform, tag_pose_camera.pose);
            // Manual conversion from Transform to Pose
            tag_pose_camera.pose.position.x = t_stamped.transform.translation.x - 0.04;
            tag_pose_camera.pose.position.y = t_stamped.transform.translation.y;
            tag_pose_camera.pose.position.z = t_stamped.transform.translation.z;
            tag_pose_camera.pose.orientation = t_stamped.transform.rotation;
            
            geometry_msgs::msg::PoseStamped tag_pose_map = tf_buffer_.transform(tag_pose_camera, map_frame);
            RCLCPP_INFO(logger_, "AprilTag global location in '%s' frame: [x: %.2f, y: %.2f]",
                        map_frame.c_str(),
                        tag_pose_map.pose.position.x,
                        tag_pose_map.pose.position.y);
            RCLCPP_INFO(logger_, "Detected cube color: %s", detected_color.c_str());

            // Stop exploration and return to initial pose (if enabled).
            RCLCPP_INFO(logger_, "Stopping exploration to return home.");
            stop(true);

        } catch (const tf2::TransformException &ex) {
            // This can happen if the TF message is not yet available.
            // We log the error and do nothing, waiting for the next callback.
            RCLCPP_WARN(logger_, "Could not get transform from %s to %s: %s",
                         camera_frame.c_str(), tag_frame.c_str(), ex.what());
        }
    }
}

std::string Explore::detectCubeColor(const cv::Mat& image, const apriltag_msgs::msg::AprilTagDetection& detection)
{
    // --- 1. Rectify the Tag Region using Perspective Warp ---

    // Define the destination size for our rectified, front-on view of the tag.
    // Matched to the Python script for consistency.
    const int RECTIFIED_SIZE = 40;
    cv::Size rectified_size(RECTIFIED_SIZE, RECTIFIED_SIZE);

    // The corners of the tag as detected in the image (source points for the warp).
    // The order MUST match the destination points: TL, TR, BR, BL
    std::vector<cv::Point2f> src_points;
    src_points.push_back(cv::Point2f(detection.corners[0].x, detection.corners[0].y)); // Top-left
    src_points.push_back(cv::Point2f(detection.corners[1].x, detection.corners[1].y)); // Top-right
    src_points.push_back(cv::Point2f(detection.corners[2].x, detection.corners[2].y)); // Bottom-right
    src_points.push_back(cv::Point2f(detection.corners[3].x, detection.corners[3].y)); // Bottom-left

    // The corners of our desired output image (a perfect square).
    std::vector<cv::Point2f> dst_points;
    dst_points.push_back(cv::Point2f(0, 0));
    dst_points.push_back(cv::Point2f(rectified_size.width - 1, 0));
    dst_points.push_back(cv::Point2f(rectified_size.width - 1, rectified_size.height - 1));
    dst_points.push_back(cv::Point2f(0, rectified_size.height - 1));

    // Calculate the perspective transformation matrix and warp the image.
    cv::Mat M = cv::getPerspectiveTransform(src_points, dst_points);
    cv::Mat rectified_tag;
    cv::warpPerspective(image, rectified_tag, M, rectified_size);

    // --- 2. Isolate Colored Pixels and Find the Brightest One ---

    // Convert the rectified tag to HSV color space for easier color analysis.
    cv::Mat rectified_hsv;
    cv::cvtColor(rectified_tag, rectified_hsv, cv::COLOR_BGR2HSV);

    // Create a mask of all non-black pixels (Value > 50).
    cv::Mat mask;
    cv::inRange(rectified_hsv, cv::Scalar(0, 0, 50), cv::Scalar(180, 255, 255), mask);

    // Erode the mask to remove pixels at the edge of the colored areas,
    // which can be affected by anti-aliasing.
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(3, 3));
    cv::Mat clean_mask;
    cv::erode(mask, clean_mask, kernel);

    int brightest_h = 0, brightest_s = 0, brightest_v = -1;
    int pixel_count = 0;

    // Iterate through the image to find the pixel with the maximum Value (brightness)
    // within our cleaned mask.
    for (int y = 0; y < rectified_hsv.rows; ++y) {
        for (int x = 0; x < rectified_hsv.cols; ++x) {
            if (clean_mask.at<uchar>(y, x) > 0) {
                pixel_count++;
                cv::Vec3b current_pixel_hsv = rectified_hsv.at<cv::Vec3b>(y, x);
                int current_v = current_pixel_hsv[2];

                if (current_v > brightest_v) {
                    brightest_v = current_v;
                    brightest_h = current_pixel_hsv[0];
                    brightest_s = current_pixel_hsv[1];
                }
            }
        }
    }

    // If no non-black pixels were found, the tag is likely all black.
    if (pixel_count == 0) {
        return "black";
    }

    // --- 3. Classify the Color of the Brightest Pixel ---

    int h = brightest_h;
    int s = brightest_s;
    int v = brightest_v;

    // This logic is a direct translation of the Python `classify_color` function.
    // OpenCV Hue is 0-179, Saturation is 0-255, Value is 0-255.
    if (v < 100) {
        return "black";
    } else if (s < 30 && v > 200) {
        return "white";
    } else if (s < 30 && v >= 50) {
        return "gray";
    } else if ((h < 6) || (h >= 160)) { // Red hue range wraps around
        if (s < 155 && v > 150) {
            return "pink";
        } else {
            return "red";
        }
    } else if (h >= 8 && h < 30) {
        if (s > 100 && v < 170) {
            return "brown";
        } else {
            return "orange";
        }
    } else if (h >= 30 && h < 45) {
        return "yellow";
    // } else if (h >= 20 && h < 30) {
    //     if (s > 100 && v > 150) {
    //         return "gold";
    //     } else {
    //         return "beige";
    //     }
    
    } else if (h >= 45 && h < 85) {
        return "green";
    } else if (h >= 85 && h < 120) {
        return "blue";
    } else if (h >= 120 && h < 160) {
        return "purple";
    }

    // If no other color matched
    return "unknown";
}

void Explore::resumeCallback(const std_msgs::msg::Bool::SharedPtr msg)
{
  if (msg->data) {
    resume();
  } else {
    stop();
  }
}

void Explore::visualizeFrontiers(
    const std::vector<frontier_exploration::Frontier>& frontiers)
{
  std_msgs::msg::ColorRGBA blue;
  blue.r = 0;
  blue.g = 0;
  blue.b = 1.0;
  blue.a = 1.0;
  std_msgs::msg::ColorRGBA red;
  red.r = 1.0;
  red.g = 0;
  red.b = 0;
  red.a = 1.0;
  std_msgs::msg::ColorRGBA green;
  green.r = 0;
  green.g = 1.0;
  green.b = 0;
  green.a = 1.0;

  // RCLCPP_INFO(logger_, "inside visualizing function");
  // RCLCPP_DEBUG(logger_, "visualising %lu frontiers", frontiers.size());
  visualization_msgs::msg::MarkerArray markers_msg;
  std::vector<visualization_msgs::msg::Marker>& markers = markers_msg.markers;
  visualization_msgs::msg::Marker m;

  m.header.frame_id = costmap_client_.getGlobalFrameID();
  m.header.stamp = this->now();
  m.ns = "frontiers";
  m.scale.x = 1.0;
  m.scale.y = 1.0;
  m.scale.z = 1.0;
  m.color.r = 0;
  m.color.g = 0;
  m.color.b = 255;
  m.color.a = 255;
  // lives forever
#ifdef ELOQUENT
  m.lifetime = rclcpp::Duration(0);  // deprecated in galactic warning
#elif DASHING
  m.lifetime = rclcpp::Duration(0);  // deprecated in galactic warning
#else
  m.lifetime = rclcpp::Duration::from_seconds(0);  // foxy onwards
#endif
  // m.lifetime = rclcpp::Duration::from_nanoseconds(0); // suggested in
  // galactic
  m.frame_locked = true;

  // weighted frontiers are always sorted
  double min_cost = frontiers.empty() ? 0. : frontiers.front().cost;

  m.action = visualization_msgs::msg::Marker::ADD;
  size_t id = 0;
  for (auto& frontier : frontiers) {
    m.type = visualization_msgs::msg::Marker::POINTS;
    m.id = int(id);
    // m.pose.position = {}; // compile warning
    m.scale.x = 0.1;
    m.scale.y = 0.1;
    m.scale.z = 0.1;
    m.points = frontier.points;
    if (goalOnBlacklist(frontier.centroid)) {
      m.color = red;
    } else {
      m.color = blue;
    }
    markers.push_back(m);
    ++id;
    m.type = visualization_msgs::msg::Marker::SPHERE;
    m.id = int(id);
    m.pose.position = frontier.initial;
    // scale frontier according to its cost (costier frontiers will be smaller)
    // double scale = std::min(std::abs(min_cost * 0.4 / frontier.cost), 0.5);
    double scale = std::min(std::abs(min_cost * 0.2 / frontier.cost), 0.2);
    m.scale.x = scale;
    m.scale.y = scale;
    m.scale.z = scale;
    m.points = {};
    m.color = green;
    markers.push_back(m);
    ++id;
  }
  size_t current_markers_count = markers.size();

  // delete previous markers, which are now unused
  m.action = visualization_msgs::msg::Marker::DELETE;
  for (; id < last_markers_count_; ++id) {
    m.id = int(id);
    markers.push_back(m);
  }

  last_markers_count_ = current_markers_count;
  marker_array_publisher_->publish(markers_msg);
}

// void Explore::makePlan()
// {
//   // MODIFIED: Only plan if we are not currently executing a goal.
//   // This is the core change to prevent harsh, stepwise movement.
//   if (goal_active_) {
//     RCLCPP_INFO_THROTTLE(logger_, *this->get_clock(), 5000, "Goal is active, waiting for completion...");
//     return;
//   }
  
//   // find frontiers
//   auto pose = costmap_client_.getRobotPose();
//   // get frontiers sorted according to cost
//   auto frontiers = search_.searchFrom(pose.position);
//   RCLCPP_DEBUG(logger_, "found %lu frontiers", frontiers.size());

//   if (frontiers.empty()) {
//     RCLCPP_WARN(logger_, "No frontiers found, stopping.");
//     stop(true);
//     return;
//   }

//   // publish frontiers as visualization markers
//   if (visualize_) {
//     visualizeFrontiers(frontiers);
//   }

//   // find non blacklisted frontier
//   auto frontier =
//       std::find_if_not(frontiers.begin(), frontiers.end(),
//                        [this](const frontier_exploration::Frontier& f) {
//                          return goalOnBlacklist(f.centroid);
//                        });
//   if (frontier == frontiers.end()) {
//     RCLCPP_WARN(logger_, "All frontiers traversed/tried out, stopping.");
//     stop(true);
//     return;
//   }
//   geometry_msgs::msg::Point target_position = frontier->centroid;

//   // time out if we are not making any progress
//   bool same_goal = same_point(prev_goal_, target_position);
//   prev_goal_ = target_position;

//   if (!same_goal || prev_distance_ > frontier->min_distance) {
//     // we have different goal or we made some progress
//     last_progress_ = this->now();
//     prev_distance_ = frontier->min_distance;
//   }
//   // black list if we've made no progress for a long time
//   if ((this->now() - last_progress_ >
//       tf2::durationFromSec(progress_timeout_))) {
//     frontier_blacklist_.push_back(target_position);
//     RCLCPP_DEBUG(logger_, "Adding current goal to black list due to timeout");
//     makePlan();
//     return;
//   }
  
//   // MODIFIED: This check is no longer needed because of the goal_active_ flag
//   // The robot will only reach this point if the previous goal is complete.
//   /*
//   // we don't need to do anything if we still pursuing the same goal
//   if (same_goal) {
//     return;
//   }
//   */

//   RCLCPP_INFO(logger_, "Found new frontier to explore. Sending goal.");

//   // send goal to move_base
//   auto goal = nav2_msgs::action::NavigateToPose::Goal();
//   goal.pose.pose.position = target_position;

//   // --- MODIFIED: Calculate a more intelligent orientation ---
//   // The robot will face towards the frontier centroid
//   double dx = target_position.x - pose.position.x;
//   double dy = target_position.y - pose.position.y;
//   double yaw = atan2(dy, dx);
//   tf2::Quaternion q;
//   q.setRPY(0, 0, yaw);
//   goal.pose.pose.orientation = tf2::toMsg(q);
//   // --- End of orientation modification ---

//   goal.pose.header.frame_id = costmap_client_.getGlobalFrameID();
//   goal.pose.header.stamp = this->now();

//   auto send_goal_options =
//       rclcpp_action::Client<nav2_msgs::action::NavigateToPose>::SendGoalOptions();
//   send_goal_options.result_callback =
//       [this,
//        target_position](const NavigationGoalHandle::WrappedResult& result) {
//         reachedGoal(result, target_position);
//       };

//   // ADDED: Set the flag to true, as we are about to send a new goal
//   goal_active_ = true;
//   move_base_client_->async_send_goal(goal, send_goal_options);
// }

// MODIFIED: Re-integrated the "too close" check to prevent goal spamming.
void Explore::makePlan()
{
  // This initial check is common to both modes
  if (goal_active_ || (detect_apriltag_ && current_state_ == State::RETREATING)) {
    if (detect_apriltag_ && current_state_ == State::RETREATING) {
        RCLCPP_INFO_THROTTLE(logger_, *this->get_clock(), 5000, "Currently in RETREAT state, waiting...");
    } else {
        RCLCPP_INFO_THROTTLE(logger_, *this->get_clock(), 5000, "Goal is active, waiting...");
    }
    return;
  }
  
  // This setup is also common to both modes
  geometry_msgs::msg::Pose robot_pose;
  try {
      robot_pose = costmap_client_.getRobotPose();
  } catch (const tf2::TransformException &ex) {
      RCLCPP_ERROR(logger_, "Could not get robot pose to make a plan: %s. Will retry.", ex.what());
      return;
  }

  auto frontiers = search_.searchFrom(robot_pose.position);
  RCLCPP_DEBUG(logger_, "found %lu frontiers", frontiers.size());

  if (frontiers.empty()) {
    RCLCPP_WARN(logger_, "No frontiers found, stopping.");
    stop(true);
    return;
  }

  if (visualize_) {
    visualizeFrontiers(frontiers);
  }

  auto frontier_it =
      std::find_if_not(frontiers.begin(), frontiers.end(),
                       [this](const frontier_exploration::Frontier& f) {
                         return goalOnBlacklist(f.centroid);
                       });

  if (frontier_it == frontiers.end()) {
    RCLCPP_WARN(logger_, "All available frontiers are on blacklist, stopping.");
    stop(true);
    return;
  }

  // =========================================================================
  // NEW "TOO CLOSE" CHECK - THIS IS THE FIX
  // =========================================================================
  geometry_msgs::msg::Point target_position = frontier_it->centroid;
  double dx_robot_to_goal = robot_pose.position.x - target_position.x;
  double dy_robot_to_goal = robot_pose.position.y - target_position.y;
  double robot_to_goal_dist = std::sqrt(dx_robot_to_goal * dx_robot_to_goal + dy_robot_to_goal * dy_robot_to_goal);

  // Use a threshold slightly larger than Nav2's xy_goal_tolerance. 0.25m is a safe default.
  double too_close_threshold = 0.25; 
  if (robot_to_goal_dist < too_close_threshold) {
    RCLCPP_INFO(logger_, "Chosen frontier is too close to the robot (%.2fm). Blacklisting and re-planning.", robot_to_goal_dist);
    frontier_blacklist_.push_back(target_position);
    makePlan(); // Recursively call to find the *next* best frontier
    return;
  }
  // =========================================================================

  // BEHAVIORAL SWITCH based on detect_apriltag_ parameter
  if (detect_apriltag_) {
    RCLCPP_DEBUG(logger_, "AprilTag detection is ON. Validating path before moving.");
    validateAndNavigateToFrontier(frontiers, frontier_it);

  } else {
    RCLCPP_DEBUG(logger_, "AprilTag detection is OFF. Navigating directly to frontier.");
    
    // Timeout logic for progress
    bool same_goal = same_point(prev_goal_, target_position);
    prev_goal_ = target_position;
    if (!same_goal || prev_distance_ > frontier_it->min_distance) {
      last_progress_ = this->now();
      prev_distance_ = frontier_it->min_distance;
    }
    if ((this->now() - last_progress_) > rclcpp::Duration::from_seconds(progress_timeout_)) {
      frontier_blacklist_.push_back(target_position);
      RCLCPP_WARN(logger_, "Adding current goal to black list due to timeout. Re-planning.");
      makePlan();
      return;
    }
    
    // Send goal directly to move_base
    auto goal = nav2_msgs::action::NavigateToPose::Goal();
    goal.pose.pose.position = target_position;
    double yaw = atan2(target_position.y - robot_pose.position.y, target_position.x - robot_pose.position.x);
    tf2::Quaternion q;
    q.setRPY(0, 0, yaw);
    goal.pose.pose.orientation = tf2::toMsg(q);
    goal.pose.header.frame_id = costmap_client_.getGlobalFrameID();
    goal.pose.header.stamp = this->now();

    auto send_goal_options =
        rclcpp_action::Client<nav2_msgs::action::NavigateToPose>::SendGoalOptions();
    send_goal_options.result_callback =
        [this, target_position](const NavigationGoalHandle::WrappedResult& result) {
          reachedGoal(result, target_position);
        };
    
    goal_active_ = true;
    move_base_client_->async_send_goal(goal, send_goal_options);
  }
}


void Explore::returnToInitialPose()
{
  // ADDED: A safety check to ensure we don't try to send a goal with an uninitialized pose.
  if (!initial_pose_set_) {
    RCLCPP_ERROR(logger_, "Attempted to return to initial pose, but it was not set!");
    return;
  }

  // Add more detail to the log messages
  if (apriltag_goal_active_.load()) {
    RCLCPP_INFO(logger_, ">>> AprilTag detected. Sending goal to return to initial pose.");
  } else {
    RCLCPP_INFO(logger_, ">>> Exploration complete. Sending goal to return to initial pose.");
  }
  RCLCPP_INFO(logger_, ">>> Initial Pose Goal: [x: %.2f, y: %.2f]",
              initial_pose_.position.x, initial_pose_.position.y);

  if (apriltag_goal_active_.load()) {
    RCLCPP_INFO(logger_, "Returning to initial pose due to AprilTag detection.");
  } else {
    RCLCPP_INFO(logger_, "Exploration done, returning to initial pose.");
  }

  auto goal = nav2_msgs::action::NavigateToPose::Goal();
  goal.pose.pose.position = initial_pose_.position;
  goal.pose.pose.orientation = initial_pose_.orientation;
  goal.pose.header.frame_id = costmap_client_.getGlobalFrameID();
  goal.pose.header.stamp = this->now();

  auto send_goal_options =
      rclcpp_action::Client<nav2_msgs::action::NavigateToPose>::SendGoalOptions();
  move_base_client_->async_send_goal(goal, send_goal_options);
}

bool Explore::goalOnBlacklist(const geometry_msgs::msg::Point& goal)
{
  constexpr static size_t tolerace = 5;
  nav2_costmap_2d::Costmap2D* costmap2d = costmap_client_.getCostmap();

  // check if a goal is on the blacklist for goals that we're pursuing
  for (auto& frontier_goal : frontier_blacklist_) {
    double x_diff = fabs(goal.x - frontier_goal.x);
    double y_diff = fabs(goal.y - frontier_goal.y);

    if (x_diff < tolerace * costmap2d->getResolution() &&
        y_diff < tolerace * costmap2d->getResolution())
      return true;
  }
  return false;
}

void Explore::reachedGoal(const NavigationGoalHandle::WrappedResult& result,
                          const geometry_msgs::msg::Point& frontier_goal)
{
  goal_active_ = false;

  switch (result.code) {
    case rclcpp_action::ResultCode::SUCCEEDED:
      RCLCPP_INFO(logger_, "Goal reached successfully!");
      if (detect_apriltag_) {
        try {
          geometry_msgs::msg::PoseStamped current_pose_stamped;
          current_pose_stamped.header.stamp = this->now();
          current_pose_stamped.header.frame_id = costmap_client_.getGlobalFrameID();
          current_pose_stamped.pose = costmap_client_.getRobotPose();
          goal_history_.push_back(current_pose_stamped);
        } catch (const tf2::TransformException &ex) {
          RCLCPP_WARN(logger_, "Could not get robot pose to update goal history: %s", ex.what());
        }
      }
      break;
    case rclcpp_action::ResultCode::ABORTED:
      RCLCPP_WARN(logger_, "Goal was aborted. Blacklisting and re-planning.");
      frontier_blacklist_.push_back(frontier_goal);
      break;
    case rclcpp_action::ResultCode::CANCELED:
      RCLCPP_INFO(logger_, "Goal was canceled.");
      // If we cancel, we probably don't want to immediately start a new plan.
      // The user can call resume() which will restart the timer.
      return; 
    default:
      RCLCPP_WARN(logger_, "Unknown result code from move base nav2");
      break;
  }
  
  // THIS IS THE KEY CHANGE
  // Instead of just printing, we now trigger the next planning cycle directly.
  RCLCPP_INFO(logger_, "Previous goal complete. Triggering new plan.");
  makePlan();
}
// =========================================================================
// NEW "STRATEGIC RETREAT" METHODS
// =========================================================================

// NEW: Starts the process of checking a path to a frontier.
// MODIFIED: Correctly gets the robot pose and manually builds the PoseStamped message.
void Explore::validateAndNavigateToFrontier(
    const std::vector<frontier_exploration::Frontier>& frontiers,
    std::vector<frontier_exploration::Frontier>::const_iterator current_frontier_it)
{
    pending_frontier_ = *current_frontier_it;

    auto path_goal = nav2_msgs::action::ComputePathToPose::Goal();
    path_goal.goal.header.frame_id = costmap_client_.getGlobalFrameID();
    path_goal.goal.header.stamp = this->now();
    path_goal.goal.pose.position = pending_frontier_->centroid;

    // CORRECTED: Manually construct the PoseStamped for the start pose.
    geometry_msgs::msg::PoseStamped start_pose;
    start_pose.header.frame_id = costmap_client_.getGlobalFrameID();
    start_pose.header.stamp = this->now();
    try {
        start_pose.pose = costmap_client_.getRobotPose();
    } catch (const tf2::TransformException &ex) {
        RCLCPP_ERROR(logger_, "Could not get robot pose for path validation: %s. Aborting plan.", ex.what());
        return; // Can't validate without a start pose, so we must abort.
    }
    
    double dx = pending_frontier_->centroid.x - start_pose.pose.position.x;
    double dy = pending_frontier_->centroid.y - start_pose.pose.position.y;
    tf2::Quaternion q;
    q.setRPY(0, 0, atan2(dy, dx));
    path_goal.goal.pose.orientation = tf2::toMsg(q);

    path_goal.use_start = true;
    path_goal.start = start_pose; // Now this is a correctly formed PoseStamped

    RCLCPP_INFO(logger_, "Checking path to frontier at (%.2f, %.2f)", 
                pending_frontier_->centroid.x, pending_frontier_->centroid.y);

    auto send_goal_options = rclcpp_action::Client<nav2_msgs::action::ComputePathToPose>::SendGoalOptions();
    send_goal_options.result_callback =
        std::bind(&Explore::computedPathCallback, this, std::placeholders::_1, frontiers, current_frontier_it);
    
    compute_path_client_->async_send_goal(path_goal, send_goal_options);
}
// NEW: Callback for path computation. Implements "Strategic Retreat".
// In explore.cpp

// MODIFIED: Correctly gets the robot pose and uses the angles library.
void Explore::computedPathCallback(
    const rclcpp_action::ClientGoalHandle<nav2_msgs::action::ComputePathToPose>::WrappedResult& result,
    const std::vector<frontier_exploration::Frontier>& frontiers,
    std::vector<frontier_exploration::Frontier>::const_iterator last_checked_frontier_it)
{
    if (result.code != rclcpp_action::ResultCode::SUCCEEDED || result.result->path.poses.size() < 2) {
        RCLCPP_WARN(logger_, "Path computation failed. Blacklisting frontier and trying next.");
        frontier_blacklist_.push_back(pending_frontier_->centroid);
        auto next_it = std::next(last_checked_frontier_it);
        // Find the next non-blacklisted frontier to try
        auto next_valid_it = std::find_if_not(next_it, frontiers.end(),
                                               [this](const auto& f){ return goalOnBlacklist(f.centroid); });

        if (next_valid_it != frontiers.end()) {
            validateAndNavigateToFrontier(frontiers, next_valid_it);
        } else {
            RCLCPP_WARN(logger_, "No more valid frontiers to check. Stopping.");
            stop(true);
        }
        return;
    }

    // CORRECTED: Manually construct the PoseStamped for the robot pose.
    double robot_yaw;
    try {
        geometry_msgs::msg::Pose robot_pose = costmap_client_.getRobotPose();
        robot_yaw = tf2::getYaw(robot_pose.orientation);
    } catch (const tf2::TransformException &ex) {
        RCLCPP_ERROR(logger_, "Could not get robot pose for angle check: %s. Aborting plan.", ex.what());
        return;
    }

    const auto& p1 = result.result->path.poses[0].pose.position;
    const auto& p2 = result.result->path.poses[1].pose.position;
    double path_yaw = atan2(p2.y - p1.y, p2.x - p1.x);

    double angle_diff = angles::normalize_angle(path_yaw - robot_yaw);
    const double FORWARD_ANGLE_THRESHOLD = 1.8; // M_PI / 2.0 ; // 90 degrees

    if (std::abs(angle_diff) < FORWARD_ANGLE_THRESHOLD) {
        RCLCPP_INFO(logger_, "Forward path found (angle diff: %.1f deg). Sending goal to frontier.", angles::to_degrees(angle_diff));
        
        auto nav_goal = nav2_msgs::action::NavigateToPose::Goal();
        nav_goal.pose = result.result->path.poses.back();
        nav_goal.pose.header.stamp = this->now();

        auto send_goal_options = rclcpp_action::Client<nav2_msgs::action::NavigateToPose>::SendGoalOptions();
        send_goal_options.result_callback =
            [this, frontier_goal = pending_frontier_->centroid](const NavigationGoalHandle::WrappedResult& res) {
                reachedGoal(res, frontier_goal);
            };

        goal_active_ = true;
        move_base_client_->async_send_goal(nav_goal, send_goal_options);
    } else {
        RCLCPP_WARN(logger_, "Path requires reversing (angle diff: %.1f deg). INITIATING STRATEGIC RETREAT.", angles::to_degrees(angle_diff));
        startRetreat();
    }
}

// NEW: Handles the logic to back up into a known-safe area.
void Explore::startRetreat()
{
    if (goal_history_.size() <= 1) {
        RCLCPP_ERROR(logger_, "Retreat failed: No previous safe locations to retreat to. Stopping exploration.");
        stop(true);
        return;
    }

    current_state_ = State::RETREATING;
    goal_active_ = true;

    // The last element is our current (stuck) position, the one before is where we want to go.
    // goal_history_.pop_back(); 
    geometry_msgs::msg::PoseStamped retreat_target = goal_history_.back();

    RCLCPP_INFO(logger_, "Initiating retreat to previous location (%.2f, %.2f)",
                retreat_target.pose.position.x, retreat_target.pose.position.y);

    auto retreat_goal = nav2_msgs::action::NavigateToPose::Goal();
    retreat_goal.pose = retreat_target;

    auto send_goal_options = rclcpp_action::Client<nav2_msgs::action::NavigateToPose>::SendGoalOptions();
    send_goal_options.result_callback =
        std::bind(&Explore::retreatGoalDone, this, std::placeholders::_1);
    
    move_base_client_->async_send_goal(retreat_goal, send_goal_options);
}

void Explore::retreatGoalDone(const rclcpp_action::ClientGoalHandle<nav2_msgs::action::NavigateToPose>::WrappedResult& result)
{
    goal_active_ = false;
    current_state_ = State::EXPLORING;

    if (result.code == rclcpp_action::ResultCode::SUCCEEDED) {
        RCLCPP_INFO(logger_, "Retreat successful. Resuming exploration planning.");
        // We successfully moved away from the "stuck" pose. Now it's safe to remove it.
        // The pose we retreated FROM is still at the back of the history.
        if (!goal_history_.empty()) { // Safety check
            goal_history_.pop_back();
        }
    } else {
        RCLCPP_WARN(logger_, "Retreat goal failed or was aborted. Will try to replan from current position.");
        // We failed to retreat, so we are still at the "stuck" pose.
        // DO NOT pop the history, so we can try retreating again.
    }
    
    makePlan();
}


void Explore::start()
{
  RCLCPP_INFO(logger_, "Exploration started.");
  goal_active_ = false;
  exploring_timer_->reset();

  // NEW: Reset the state machine to ensure we begin by exploring.
  current_state_ = State::EXPLORING; 

  // Reset path recording timer if it exists.
  if (record_path_mode_ && path_recording_timer_) {
    path_recording_timer_->reset();
  }
}

void Explore::stop(bool finished_exploring)
{
  if (!apriltag_goal_active_.load()) {
    RCLCPP_INFO(logger_, "Exploration stopped.");
  }

  // Set goal_active_ to false and cancel the timer. This prevents any new
  // exploration plans from being made.
  goal_active_ = false;
  exploring_timer_->cancel();

  // ADDED: Cancel path recording timer and publish the path if conditions are met.
  if (record_path_mode_) {
    if (path_recording_timer_) {
      path_recording_timer_->cancel();
    }
    // Check if exploration is complete and we are in the correct mode.
    if (finished_exploring) {
        // Stamp the path with the final time and publish it.
        recorded_path_.header.stamp = this->now();
        RCLCPP_INFO(logger_, "Exploration complete. Publishing recorded path with %zu poses to topic '%s'.",
                    recorded_path_.poses.size(), path_publisher_->get_topic_name());
        path_publisher_->publish(recorded_path_);
    }
  }

  // Determine if we should be returning to the initial pose.
  // This is true if exploration is "finished" (either by finding no more
  // frontiers or by detecting an AprilTag) AND a valid initial pose exists.
  bool should_return_home = finished_exploring && initial_pose_set_ &&
                             (apriltag_goal_active_.load() || return_to_init_);

  // --- ADD THIS LOGGING BLOCK ---
  RCLCPP_INFO(logger_, "Stop condition check: finished_exploring=%d, initial_pose_set_=%d, apriltag_goal_active_=%d, return_to_init_=%d -> should_return_home=%d",
              finished_exploring, initial_pose_set_, (bool)apriltag_goal_active_.load(), return_to_init_, should_return_home);
  // --- END OF ADDED BLOCK ---

  if (should_return_home) {
    // If we are returning home, send the goal. The Nav2 action server will
    // handle preempting/canceling the previous exploration goal.
    // We DO NOT call async_cancel_all_goals() here, as that is the source of the bug.
    returnToInitialPose();
  } else {
    // If we are just stopping (e.g., from a ROS topic call) and not returning
    // home, then it's safe to cancel any active goals.
    move_base_client_->async_cancel_all_goals();
  }
}

void Explore::resume()
{
  RCLCPP_INFO(logger_, "Exploration resuming.");
  goal_active_ = false;
  exploring_timer_->reset();

  // NEW: Also reset the state machine on resume.
  current_state_ = State::EXPLORING;

  // Resume the path recording timer if it exists.
  if (record_path_mode_ && path_recording_timer_) {
      path_recording_timer_->reset();
      RCLCPP_INFO(logger_, "Path recording resumed.");
  }
}

}  // namespace explore

int main(int argc, char** argv)
{
  rclcpp::init(argc, argv);
  // ROS1 code
  /*
  if (ros::console::set_logger_level(ROSCONSOLE_DEFAULT_NAME,
                                     ros::console::levels::Debug)) {
    ros::console::notifyLoggerLevelsChanged();
  } */
  rclcpp::spin(
      std::make_shared<explore::Explore>());  // std::move(std::make_unique)?
  rclcpp::shutdown();
  return 0;
}
