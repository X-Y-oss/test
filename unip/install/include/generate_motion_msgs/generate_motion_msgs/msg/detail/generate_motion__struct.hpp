// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from generate_motion_msgs:msg/GenerateMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "generate_motion_msgs/msg/generate_motion.hpp"


#ifndef GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__STRUCT_HPP_
#define GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__generate_motion_msgs__msg__GenerateMotion __attribute__((deprecated))
#else
# define DEPRECATED__generate_motion_msgs__msg__GenerateMotion __declspec(deprecated)
#endif

namespace generate_motion_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct GenerateMotion_
{
  using Type = GenerateMotion_<ContainerAllocator>;

  explicit GenerateMotion_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->robot_file = "";
      this->attach_cylinder = false;
      this->cylinder_radius = 0.0;
      this->cylinder_height = 0.0;
      this->grasp_prepose_motion = false;
    }
  }

  explicit GenerateMotion_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : robot_file(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->robot_file = "";
      this->attach_cylinder = false;
      this->cylinder_radius = 0.0;
      this->cylinder_height = 0.0;
      this->grasp_prepose_motion = false;
    }
  }

  // field types and members
  using _robot_file_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _robot_file_type robot_file;
  using _pose_lists_type =
    std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>>;
  _pose_lists_type pose_lists;
  using _segment_modes_type =
    std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>>;
  _segment_modes_type segment_modes;
  using _linear_axes_type =
    std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>>;
  _linear_axes_type linear_axes;
  using _attach_cylinder_type =
    bool;
  _attach_cylinder_type attach_cylinder;
  using _attach_after_index_type =
    std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>>;
  _attach_after_index_type attach_after_index;
  using _detach_after_index_type =
    std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>>;
  _detach_after_index_type detach_after_index;
  using _cylinder_radius_type =
    double;
  _cylinder_radius_type cylinder_radius;
  using _cylinder_height_type =
    double;
  _cylinder_height_type cylinder_height;
  using _cylinder_pose_type =
    std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>>;
  _cylinder_pose_type cylinder_pose;
  using _grasp_prepose_motion_type =
    bool;
  _grasp_prepose_motion_type grasp_prepose_motion;

  // setters for named parameter idiom
  Type & set__robot_file(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->robot_file = _arg;
    return *this;
  }
  Type & set__pose_lists(
    const std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>> & _arg)
  {
    this->pose_lists = _arg;
    return *this;
  }
  Type & set__segment_modes(
    const std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>> & _arg)
  {
    this->segment_modes = _arg;
    return *this;
  }
  Type & set__linear_axes(
    const std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>> & _arg)
  {
    this->linear_axes = _arg;
    return *this;
  }
  Type & set__attach_cylinder(
    const bool & _arg)
  {
    this->attach_cylinder = _arg;
    return *this;
  }
  Type & set__attach_after_index(
    const std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>> & _arg)
  {
    this->attach_after_index = _arg;
    return *this;
  }
  Type & set__detach_after_index(
    const std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>> & _arg)
  {
    this->detach_after_index = _arg;
    return *this;
  }
  Type & set__cylinder_radius(
    const double & _arg)
  {
    this->cylinder_radius = _arg;
    return *this;
  }
  Type & set__cylinder_height(
    const double & _arg)
  {
    this->cylinder_height = _arg;
    return *this;
  }
  Type & set__cylinder_pose(
    const std::vector<double, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<double>> & _arg)
  {
    this->cylinder_pose = _arg;
    return *this;
  }
  Type & set__grasp_prepose_motion(
    const bool & _arg)
  {
    this->grasp_prepose_motion = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator> *;
  using ConstRawPtr =
    const generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__generate_motion_msgs__msg__GenerateMotion
    std::shared_ptr<generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__generate_motion_msgs__msg__GenerateMotion
    std::shared_ptr<generate_motion_msgs::msg::GenerateMotion_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const GenerateMotion_ & other) const
  {
    if (this->robot_file != other.robot_file) {
      return false;
    }
    if (this->pose_lists != other.pose_lists) {
      return false;
    }
    if (this->segment_modes != other.segment_modes) {
      return false;
    }
    if (this->linear_axes != other.linear_axes) {
      return false;
    }
    if (this->attach_cylinder != other.attach_cylinder) {
      return false;
    }
    if (this->attach_after_index != other.attach_after_index) {
      return false;
    }
    if (this->detach_after_index != other.detach_after_index) {
      return false;
    }
    if (this->cylinder_radius != other.cylinder_radius) {
      return false;
    }
    if (this->cylinder_height != other.cylinder_height) {
      return false;
    }
    if (this->cylinder_pose != other.cylinder_pose) {
      return false;
    }
    if (this->grasp_prepose_motion != other.grasp_prepose_motion) {
      return false;
    }
    return true;
  }
  bool operator!=(const GenerateMotion_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct GenerateMotion_

// alias to use template instance with default allocator
using GenerateMotion =
  generate_motion_msgs::msg::GenerateMotion_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace generate_motion_msgs

#endif  // GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__STRUCT_HPP_
