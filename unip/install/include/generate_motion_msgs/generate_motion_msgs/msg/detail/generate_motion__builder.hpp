// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from generate_motion_msgs:msg/GenerateMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "generate_motion_msgs/msg/generate_motion.hpp"


#ifndef GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__BUILDER_HPP_
#define GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "generate_motion_msgs/msg/detail/generate_motion__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace generate_motion_msgs
{

namespace msg
{

namespace builder
{

class Init_GenerateMotion_grasp_prepose_motion
{
public:
  explicit Init_GenerateMotion_grasp_prepose_motion(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  ::generate_motion_msgs::msg::GenerateMotion grasp_prepose_motion(::generate_motion_msgs::msg::GenerateMotion::_grasp_prepose_motion_type arg)
  {
    msg_.grasp_prepose_motion = std::move(arg);
    return std::move(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_cylinder_pose
{
public:
  explicit Init_GenerateMotion_cylinder_pose(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  Init_GenerateMotion_grasp_prepose_motion cylinder_pose(::generate_motion_msgs::msg::GenerateMotion::_cylinder_pose_type arg)
  {
    msg_.cylinder_pose = std::move(arg);
    return Init_GenerateMotion_grasp_prepose_motion(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_cylinder_height
{
public:
  explicit Init_GenerateMotion_cylinder_height(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  Init_GenerateMotion_cylinder_pose cylinder_height(::generate_motion_msgs::msg::GenerateMotion::_cylinder_height_type arg)
  {
    msg_.cylinder_height = std::move(arg);
    return Init_GenerateMotion_cylinder_pose(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_cylinder_radius
{
public:
  explicit Init_GenerateMotion_cylinder_radius(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  Init_GenerateMotion_cylinder_height cylinder_radius(::generate_motion_msgs::msg::GenerateMotion::_cylinder_radius_type arg)
  {
    msg_.cylinder_radius = std::move(arg);
    return Init_GenerateMotion_cylinder_height(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_detach_after_index
{
public:
  explicit Init_GenerateMotion_detach_after_index(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  Init_GenerateMotion_cylinder_radius detach_after_index(::generate_motion_msgs::msg::GenerateMotion::_detach_after_index_type arg)
  {
    msg_.detach_after_index = std::move(arg);
    return Init_GenerateMotion_cylinder_radius(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_attach_after_index
{
public:
  explicit Init_GenerateMotion_attach_after_index(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  Init_GenerateMotion_detach_after_index attach_after_index(::generate_motion_msgs::msg::GenerateMotion::_attach_after_index_type arg)
  {
    msg_.attach_after_index = std::move(arg);
    return Init_GenerateMotion_detach_after_index(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_attach_cylinder
{
public:
  explicit Init_GenerateMotion_attach_cylinder(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  Init_GenerateMotion_attach_after_index attach_cylinder(::generate_motion_msgs::msg::GenerateMotion::_attach_cylinder_type arg)
  {
    msg_.attach_cylinder = std::move(arg);
    return Init_GenerateMotion_attach_after_index(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_linear_axes
{
public:
  explicit Init_GenerateMotion_linear_axes(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  Init_GenerateMotion_attach_cylinder linear_axes(::generate_motion_msgs::msg::GenerateMotion::_linear_axes_type arg)
  {
    msg_.linear_axes = std::move(arg);
    return Init_GenerateMotion_attach_cylinder(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_segment_modes
{
public:
  explicit Init_GenerateMotion_segment_modes(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  Init_GenerateMotion_linear_axes segment_modes(::generate_motion_msgs::msg::GenerateMotion::_segment_modes_type arg)
  {
    msg_.segment_modes = std::move(arg);
    return Init_GenerateMotion_linear_axes(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_pose_lists
{
public:
  explicit Init_GenerateMotion_pose_lists(::generate_motion_msgs::msg::GenerateMotion & msg)
  : msg_(msg)
  {}
  Init_GenerateMotion_segment_modes pose_lists(::generate_motion_msgs::msg::GenerateMotion::_pose_lists_type arg)
  {
    msg_.pose_lists = std::move(arg);
    return Init_GenerateMotion_segment_modes(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

class Init_GenerateMotion_robot_file
{
public:
  Init_GenerateMotion_robot_file()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_GenerateMotion_pose_lists robot_file(::generate_motion_msgs::msg::GenerateMotion::_robot_file_type arg)
  {
    msg_.robot_file = std::move(arg);
    return Init_GenerateMotion_pose_lists(msg_);
  }

private:
  ::generate_motion_msgs::msg::GenerateMotion msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::generate_motion_msgs::msg::GenerateMotion>()
{
  return generate_motion_msgs::msg::builder::Init_GenerateMotion_robot_file();
}

}  // namespace generate_motion_msgs

#endif  // GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__BUILDER_HPP_
