// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from gpd_ros_messages:msg/CloudIndexed.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "gpd_ros_messages/msg/detail/cloud_indexed__rosidl_typesupport_introspection_c.h"
#include "gpd_ros_messages/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "gpd_ros_messages/msg/detail/cloud_indexed__functions.h"
#include "gpd_ros_messages/msg/detail/cloud_indexed__struct.h"


// Include directives for member types
// Member `cloud_sources`
#include "gpd_ros_messages/msg/cloud_sources.h"
// Member `cloud_sources`
#include "gpd_ros_messages/msg/detail/cloud_sources__rosidl_typesupport_introspection_c.h"
// Member `indices`
#include "std_msgs/msg/int64.h"
// Member `indices`
#include "std_msgs/msg/detail/int64__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  gpd_ros_messages__msg__CloudIndexed__init(message_memory);
}

void gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_fini_function(void * message_memory)
{
  gpd_ros_messages__msg__CloudIndexed__fini(message_memory);
}

size_t gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__size_function__CloudIndexed__indices(
  const void * untyped_member)
{
  const std_msgs__msg__Int64__Sequence * member =
    (const std_msgs__msg__Int64__Sequence *)(untyped_member);
  return member->size;
}

const void * gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__get_const_function__CloudIndexed__indices(
  const void * untyped_member, size_t index)
{
  const std_msgs__msg__Int64__Sequence * member =
    (const std_msgs__msg__Int64__Sequence *)(untyped_member);
  return &member->data[index];
}

void * gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__get_function__CloudIndexed__indices(
  void * untyped_member, size_t index)
{
  std_msgs__msg__Int64__Sequence * member =
    (std_msgs__msg__Int64__Sequence *)(untyped_member);
  return &member->data[index];
}

void gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__fetch_function__CloudIndexed__indices(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const std_msgs__msg__Int64 * item =
    ((const std_msgs__msg__Int64 *)
    gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__get_const_function__CloudIndexed__indices(untyped_member, index));
  std_msgs__msg__Int64 * value =
    (std_msgs__msg__Int64 *)(untyped_value);
  *value = *item;
}

void gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__assign_function__CloudIndexed__indices(
  void * untyped_member, size_t index, const void * untyped_value)
{
  std_msgs__msg__Int64 * item =
    ((std_msgs__msg__Int64 *)
    gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__get_function__CloudIndexed__indices(untyped_member, index));
  const std_msgs__msg__Int64 * value =
    (const std_msgs__msg__Int64 *)(untyped_value);
  *item = *value;
}

bool gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__resize_function__CloudIndexed__indices(
  void * untyped_member, size_t size)
{
  std_msgs__msg__Int64__Sequence * member =
    (std_msgs__msg__Int64__Sequence *)(untyped_member);
  std_msgs__msg__Int64__Sequence__fini(member);
  return std_msgs__msg__Int64__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_member_array[2] = {
  {
    "cloud_sources",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(gpd_ros_messages__msg__CloudIndexed, cloud_sources),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "indices",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(gpd_ros_messages__msg__CloudIndexed, indices),  // bytes offset in struct
    NULL,  // default value
    gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__size_function__CloudIndexed__indices,  // size() function pointer
    gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__get_const_function__CloudIndexed__indices,  // get_const(index) function pointer
    gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__get_function__CloudIndexed__indices,  // get(index) function pointer
    gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__fetch_function__CloudIndexed__indices,  // fetch(index, &value) function pointer
    gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__assign_function__CloudIndexed__indices,  // assign(index, value) function pointer
    gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__resize_function__CloudIndexed__indices  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_members = {
  "gpd_ros_messages__msg",  // message namespace
  "CloudIndexed",  // message name
  2,  // number of fields
  sizeof(gpd_ros_messages__msg__CloudIndexed),
  false,  // has_any_key_member_
  gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_member_array,  // message members
  gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_init_function,  // function to initialize message memory (memory has to be allocated)
  gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_type_support_handle = {
  0,
  &gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_members,
  get_message_typesupport_handle_function,
  &gpd_ros_messages__msg__CloudIndexed__get_type_hash,
  &gpd_ros_messages__msg__CloudIndexed__get_type_description,
  &gpd_ros_messages__msg__CloudIndexed__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_gpd_ros_messages
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, gpd_ros_messages, msg, CloudIndexed)() {
  gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, gpd_ros_messages, msg, CloudSources)();
  gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Int64)();
  if (!gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_type_support_handle.typesupport_identifier) {
    gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &gpd_ros_messages__msg__CloudIndexed__rosidl_typesupport_introspection_c__CloudIndexed_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
