// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from gpd_ros_messages:msg/GraspConfigList.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "gpd_ros_messages/msg/detail/grasp_config_list__functions.h"
#include "gpd_ros_messages/msg/detail/grasp_config_list__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace gpd_ros_messages
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void GraspConfigList_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) gpd_ros_messages::msg::GraspConfigList(_init);
}

void GraspConfigList_fini_function(void * message_memory)
{
  auto typed_message = static_cast<gpd_ros_messages::msg::GraspConfigList *>(message_memory);
  typed_message->~GraspConfigList();
}

size_t size_function__GraspConfigList__grasps(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<gpd_ros_messages::msg::GraspConfig> *>(untyped_member);
  return member->size();
}

const void * get_const_function__GraspConfigList__grasps(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<gpd_ros_messages::msg::GraspConfig> *>(untyped_member);
  return &member[index];
}

void * get_function__GraspConfigList__grasps(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<gpd_ros_messages::msg::GraspConfig> *>(untyped_member);
  return &member[index];
}

void fetch_function__GraspConfigList__grasps(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const gpd_ros_messages::msg::GraspConfig *>(
    get_const_function__GraspConfigList__grasps(untyped_member, index));
  auto & value = *reinterpret_cast<gpd_ros_messages::msg::GraspConfig *>(untyped_value);
  value = item;
}

void assign_function__GraspConfigList__grasps(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<gpd_ros_messages::msg::GraspConfig *>(
    get_function__GraspConfigList__grasps(untyped_member, index));
  const auto & value = *reinterpret_cast<const gpd_ros_messages::msg::GraspConfig *>(untyped_value);
  item = value;
}

void resize_function__GraspConfigList__grasps(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<gpd_ros_messages::msg::GraspConfig> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember GraspConfigList_message_member_array[2] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(gpd_ros_messages::msg::GraspConfigList, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "grasps",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<gpd_ros_messages::msg::GraspConfig>(),  // members of sub message
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(gpd_ros_messages::msg::GraspConfigList, grasps),  // bytes offset in struct
    nullptr,  // default value
    size_function__GraspConfigList__grasps,  // size() function pointer
    get_const_function__GraspConfigList__grasps,  // get_const(index) function pointer
    get_function__GraspConfigList__grasps,  // get(index) function pointer
    fetch_function__GraspConfigList__grasps,  // fetch(index, &value) function pointer
    assign_function__GraspConfigList__grasps,  // assign(index, value) function pointer
    resize_function__GraspConfigList__grasps  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers GraspConfigList_message_members = {
  "gpd_ros_messages::msg",  // message namespace
  "GraspConfigList",  // message name
  2,  // number of fields
  sizeof(gpd_ros_messages::msg::GraspConfigList),
  false,  // has_any_key_member_
  GraspConfigList_message_member_array,  // message members
  GraspConfigList_init_function,  // function to initialize message memory (memory has to be allocated)
  GraspConfigList_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t GraspConfigList_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &GraspConfigList_message_members,
  get_message_typesupport_handle_function,
  &gpd_ros_messages__msg__GraspConfigList__get_type_hash,
  &gpd_ros_messages__msg__GraspConfigList__get_type_description,
  &gpd_ros_messages__msg__GraspConfigList__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace gpd_ros_messages


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<gpd_ros_messages::msg::GraspConfigList>()
{
  return &::gpd_ros_messages::msg::rosidl_typesupport_introspection_cpp::GraspConfigList_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, gpd_ros_messages, msg, GraspConfigList)() {
  return &::gpd_ros_messages::msg::rosidl_typesupport_introspection_cpp::GraspConfigList_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
