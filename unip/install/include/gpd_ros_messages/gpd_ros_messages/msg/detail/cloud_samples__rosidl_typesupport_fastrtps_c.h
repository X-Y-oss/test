// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from gpd_ros_messages:msg/CloudSamples.idl
// generated code does not contain a copyright notice
#ifndef GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SAMPLES__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SAMPLES__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "gpd_ros_messages/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "gpd_ros_messages/msg/detail/cloud_samples__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gpd_ros_messages
bool cdr_serialize_gpd_ros_messages__msg__CloudSamples(
  const gpd_ros_messages__msg__CloudSamples * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gpd_ros_messages
bool cdr_deserialize_gpd_ros_messages__msg__CloudSamples(
  eprosima::fastcdr::Cdr &,
  gpd_ros_messages__msg__CloudSamples * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gpd_ros_messages
size_t get_serialized_size_gpd_ros_messages__msg__CloudSamples(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gpd_ros_messages
size_t max_serialized_size_gpd_ros_messages__msg__CloudSamples(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gpd_ros_messages
bool cdr_serialize_key_gpd_ros_messages__msg__CloudSamples(
  const gpd_ros_messages__msg__CloudSamples * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gpd_ros_messages
size_t get_serialized_size_key_gpd_ros_messages__msg__CloudSamples(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gpd_ros_messages
size_t max_serialized_size_key_gpd_ros_messages__msg__CloudSamples(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_gpd_ros_messages
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, gpd_ros_messages, msg, CloudSamples)();

#ifdef __cplusplus
}
#endif

#endif  // GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SAMPLES__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
