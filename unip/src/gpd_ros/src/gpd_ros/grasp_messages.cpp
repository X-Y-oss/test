#include "gpd_ros/grasp_messages.hpp"
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>  // Include for tf2 support

gpd_ros_messages::msg::GraspConfigList GraspMessages::createGraspListMsg(const std::vector<std::unique_ptr<gpd::candidate::Hand>>& hands, const std_msgs::msg::Header& header)
{
  gpd_ros_messages::msg::GraspConfigList msg;

  for (size_t i = 0; i < hands.size(); i++) {
    msg.grasps.push_back(convertToGraspMsg(*hands[i]));
  }

  msg.header = header;

  return msg;
}

gpd_ros_messages::msg::GraspConfig GraspMessages::convertToGraspMsg(const gpd::candidate::Hand& hand)
{
  gpd_ros_messages::msg::GraspConfig msg;
  // Convert Eigen::Vector3d (or Eigen::Vector3f) to geometry_msgs::msg::Point
  msg.position = tf2::toMsg(hand.getPosition());

  Eigen::Vector3d approach_vec = hand.getApproach();
  msg.approach.x = approach_vec.x();
  msg.approach.y = approach_vec.y();
  msg.approach.z = approach_vec.z();

  Eigen::Vector3d binormal_vec = hand.getBinormal();
  msg.binormal.x = binormal_vec.x();
  msg.binormal.y = binormal_vec.y();
  msg.binormal.z = binormal_vec.z();

  Eigen::Vector3d axis_vec = hand.getAxis();
  msg.axis.x = axis_vec.x();
  msg.axis.y = axis_vec.y();
  msg.axis.z = axis_vec.z();


  msg.width.data = hand.getGraspWidth();
  msg.score.data = hand.getScore();

  // Convert Eigen::Vector3d (or Eigen::Vector3f) to geometry_msgs::msg::Point
  msg.sample = tf2::toMsg(hand.getSample());
  return msg;
}