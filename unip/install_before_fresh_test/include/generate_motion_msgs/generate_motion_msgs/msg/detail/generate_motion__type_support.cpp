// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from generate_motion_msgs:msg/GenerateMotion.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "generate_motion_msgs/msg/detail/generate_motion__functions.h"
#include "generate_motion_msgs/msg/detail/generate_motion__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace generate_motion_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void GenerateMotion_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) generate_motion_msgs::msg::GenerateMotion(_init);
}

void GenerateMotion_fini_function(void * message_memory)
{
  auto typed_message = static_cast<generate_motion_msgs::msg::GenerateMotion *>(message_memory);
  typed_message->~GenerateMotion();
}

size_t size_function__GenerateMotion__pose_lists(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<double> *>(untyped_member);
  return member->size();
}

const void * get_const_function__GenerateMotion__pose_lists(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<double> *>(untyped_member);
  return &member[index];
}

void * get_function__GenerateMotion__pose_lists(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<double> *>(untyped_member);
  return &member[index];
}

void fetch_function__GenerateMotion__pose_lists(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const double *>(
    get_const_function__GenerateMotion__pose_lists(untyped_member, index));
  auto & value = *reinterpret_cast<double *>(untyped_value);
  value = item;
}

void assign_function__GenerateMotion__pose_lists(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<double *>(
    get_function__GenerateMotion__pose_lists(untyped_member, index));
  const auto & value = *reinterpret_cast<const double *>(untyped_value);
  item = value;
}

void resize_function__GenerateMotion__pose_lists(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<double> *>(untyped_member);
  member->resize(size);
}

size_t size_function__GenerateMotion__segment_modes(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__GenerateMotion__segment_modes(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void * get_function__GenerateMotion__segment_modes(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__GenerateMotion__segment_modes(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int32_t *>(
    get_const_function__GenerateMotion__segment_modes(untyped_member, index));
  auto & value = *reinterpret_cast<int32_t *>(untyped_value);
  value = item;
}

void assign_function__GenerateMotion__segment_modes(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int32_t *>(
    get_function__GenerateMotion__segment_modes(untyped_member, index));
  const auto & value = *reinterpret_cast<const int32_t *>(untyped_value);
  item = value;
}

void resize_function__GenerateMotion__segment_modes(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  member->resize(size);
}

size_t size_function__GenerateMotion__linear_axes(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__GenerateMotion__linear_axes(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void * get_function__GenerateMotion__linear_axes(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__GenerateMotion__linear_axes(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int32_t *>(
    get_const_function__GenerateMotion__linear_axes(untyped_member, index));
  auto & value = *reinterpret_cast<int32_t *>(untyped_value);
  value = item;
}

void assign_function__GenerateMotion__linear_axes(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int32_t *>(
    get_function__GenerateMotion__linear_axes(untyped_member, index));
  const auto & value = *reinterpret_cast<const int32_t *>(untyped_value);
  item = value;
}

void resize_function__GenerateMotion__linear_axes(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  member->resize(size);
}

size_t size_function__GenerateMotion__attach_after_index(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__GenerateMotion__attach_after_index(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void * get_function__GenerateMotion__attach_after_index(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__GenerateMotion__attach_after_index(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int32_t *>(
    get_const_function__GenerateMotion__attach_after_index(untyped_member, index));
  auto & value = *reinterpret_cast<int32_t *>(untyped_value);
  value = item;
}

void assign_function__GenerateMotion__attach_after_index(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int32_t *>(
    get_function__GenerateMotion__attach_after_index(untyped_member, index));
  const auto & value = *reinterpret_cast<const int32_t *>(untyped_value);
  item = value;
}

void resize_function__GenerateMotion__attach_after_index(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  member->resize(size);
}

size_t size_function__GenerateMotion__detach_after_index(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__GenerateMotion__detach_after_index(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void * get_function__GenerateMotion__detach_after_index(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__GenerateMotion__detach_after_index(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int32_t *>(
    get_const_function__GenerateMotion__detach_after_index(untyped_member, index));
  auto & value = *reinterpret_cast<int32_t *>(untyped_value);
  value = item;
}

void assign_function__GenerateMotion__detach_after_index(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int32_t *>(
    get_function__GenerateMotion__detach_after_index(untyped_member, index));
  const auto & value = *reinterpret_cast<const int32_t *>(untyped_value);
  item = value;
}

void resize_function__GenerateMotion__detach_after_index(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  member->resize(size);
}

size_t size_function__GenerateMotion__cylinder_pose(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<double> *>(untyped_member);
  return member->size();
}

const void * get_const_function__GenerateMotion__cylinder_pose(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<double> *>(untyped_member);
  return &member[index];
}

void * get_function__GenerateMotion__cylinder_pose(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<double> *>(untyped_member);
  return &member[index];
}

void fetch_function__GenerateMotion__cylinder_pose(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const double *>(
    get_const_function__GenerateMotion__cylinder_pose(untyped_member, index));
  auto & value = *reinterpret_cast<double *>(untyped_value);
  value = item;
}

void assign_function__GenerateMotion__cylinder_pose(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<double *>(
    get_function__GenerateMotion__cylinder_pose(untyped_member, index));
  const auto & value = *reinterpret_cast<const double *>(untyped_value);
  item = value;
}

void resize_function__GenerateMotion__cylinder_pose(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<double> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember GenerateMotion_message_member_array[11] = {
  {
    "robot_file",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, robot_file),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "pose_lists",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, pose_lists),  // bytes offset in struct
    nullptr,  // default value
    size_function__GenerateMotion__pose_lists,  // size() function pointer
    get_const_function__GenerateMotion__pose_lists,  // get_const(index) function pointer
    get_function__GenerateMotion__pose_lists,  // get(index) function pointer
    fetch_function__GenerateMotion__pose_lists,  // fetch(index, &value) function pointer
    assign_function__GenerateMotion__pose_lists,  // assign(index, value) function pointer
    resize_function__GenerateMotion__pose_lists  // resize(index) function pointer
  },
  {
    "segment_modes",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, segment_modes),  // bytes offset in struct
    nullptr,  // default value
    size_function__GenerateMotion__segment_modes,  // size() function pointer
    get_const_function__GenerateMotion__segment_modes,  // get_const(index) function pointer
    get_function__GenerateMotion__segment_modes,  // get(index) function pointer
    fetch_function__GenerateMotion__segment_modes,  // fetch(index, &value) function pointer
    assign_function__GenerateMotion__segment_modes,  // assign(index, value) function pointer
    resize_function__GenerateMotion__segment_modes  // resize(index) function pointer
  },
  {
    "linear_axes",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, linear_axes),  // bytes offset in struct
    nullptr,  // default value
    size_function__GenerateMotion__linear_axes,  // size() function pointer
    get_const_function__GenerateMotion__linear_axes,  // get_const(index) function pointer
    get_function__GenerateMotion__linear_axes,  // get(index) function pointer
    fetch_function__GenerateMotion__linear_axes,  // fetch(index, &value) function pointer
    assign_function__GenerateMotion__linear_axes,  // assign(index, value) function pointer
    resize_function__GenerateMotion__linear_axes  // resize(index) function pointer
  },
  {
    "attach_cylinder",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, attach_cylinder),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "attach_after_index",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, attach_after_index),  // bytes offset in struct
    nullptr,  // default value
    size_function__GenerateMotion__attach_after_index,  // size() function pointer
    get_const_function__GenerateMotion__attach_after_index,  // get_const(index) function pointer
    get_function__GenerateMotion__attach_after_index,  // get(index) function pointer
    fetch_function__GenerateMotion__attach_after_index,  // fetch(index, &value) function pointer
    assign_function__GenerateMotion__attach_after_index,  // assign(index, value) function pointer
    resize_function__GenerateMotion__attach_after_index  // resize(index) function pointer
  },
  {
    "detach_after_index",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, detach_after_index),  // bytes offset in struct
    nullptr,  // default value
    size_function__GenerateMotion__detach_after_index,  // size() function pointer
    get_const_function__GenerateMotion__detach_after_index,  // get_const(index) function pointer
    get_function__GenerateMotion__detach_after_index,  // get(index) function pointer
    fetch_function__GenerateMotion__detach_after_index,  // fetch(index, &value) function pointer
    assign_function__GenerateMotion__detach_after_index,  // assign(index, value) function pointer
    resize_function__GenerateMotion__detach_after_index  // resize(index) function pointer
  },
  {
    "cylinder_radius",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, cylinder_radius),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "cylinder_height",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, cylinder_height),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "cylinder_pose",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_DOUBLE,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, cylinder_pose),  // bytes offset in struct
    nullptr,  // default value
    size_function__GenerateMotion__cylinder_pose,  // size() function pointer
    get_const_function__GenerateMotion__cylinder_pose,  // get_const(index) function pointer
    get_function__GenerateMotion__cylinder_pose,  // get(index) function pointer
    fetch_function__GenerateMotion__cylinder_pose,  // fetch(index, &value) function pointer
    assign_function__GenerateMotion__cylinder_pose,  // assign(index, value) function pointer
    resize_function__GenerateMotion__cylinder_pose  // resize(index) function pointer
  },
  {
    "grasp_prepose_motion",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(generate_motion_msgs::msg::GenerateMotion, grasp_prepose_motion),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers GenerateMotion_message_members = {
  "generate_motion_msgs::msg",  // message namespace
  "GenerateMotion",  // message name
  11,  // number of fields
  sizeof(generate_motion_msgs::msg::GenerateMotion),
  false,  // has_any_key_member_
  GenerateMotion_message_member_array,  // message members
  GenerateMotion_init_function,  // function to initialize message memory (memory has to be allocated)
  GenerateMotion_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t GenerateMotion_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &GenerateMotion_message_members,
  get_message_typesupport_handle_function,
  &generate_motion_msgs__msg__GenerateMotion__get_type_hash,
  &generate_motion_msgs__msg__GenerateMotion__get_type_description,
  &generate_motion_msgs__msg__GenerateMotion__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace generate_motion_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<generate_motion_msgs::msg::GenerateMotion>()
{
  return &::generate_motion_msgs::msg::rosidl_typesupport_introspection_cpp::GenerateMotion_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, generate_motion_msgs, msg, GenerateMotion)() {
  return &::generate_motion_msgs::msg::rosidl_typesupport_introspection_cpp::GenerateMotion_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
