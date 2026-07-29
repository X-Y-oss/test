// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from generate_motion_msgs:msg/GenerateMotion.idl
// generated code does not contain a copyright notice
#ifndef GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "generate_motion_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "generate_motion_msgs/msg/detail/generate_motion__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_generate_motion_msgs
bool cdr_serialize_generate_motion_msgs__msg__GenerateMotion(
  const generate_motion_msgs__msg__GenerateMotion * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_generate_motion_msgs
bool cdr_deserialize_generate_motion_msgs__msg__GenerateMotion(
  eprosima::fastcdr::Cdr &,
  generate_motion_msgs__msg__GenerateMotion * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_generate_motion_msgs
size_t get_serialized_size_generate_motion_msgs__msg__GenerateMotion(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_generate_motion_msgs
size_t max_serialized_size_generate_motion_msgs__msg__GenerateMotion(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_generate_motion_msgs
bool cdr_serialize_key_generate_motion_msgs__msg__GenerateMotion(
  const generate_motion_msgs__msg__GenerateMotion * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_generate_motion_msgs
size_t get_serialized_size_key_generate_motion_msgs__msg__GenerateMotion(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_generate_motion_msgs
size_t max_serialized_size_key_generate_motion_msgs__msg__GenerateMotion(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_generate_motion_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, generate_motion_msgs, msg, GenerateMotion)();

#ifdef __cplusplus
}
#endif

#endif  // GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
