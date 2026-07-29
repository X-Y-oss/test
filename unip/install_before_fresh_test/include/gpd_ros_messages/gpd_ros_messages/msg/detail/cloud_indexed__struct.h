// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from gpd_ros_messages:msg/CloudIndexed.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "gpd_ros_messages/msg/cloud_indexed.h"


#ifndef GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_INDEXED__STRUCT_H_
#define GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_INDEXED__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'cloud_sources'
#include "gpd_ros_messages/msg/detail/cloud_sources__struct.h"
// Member 'indices'
#include "std_msgs/msg/detail/int64__struct.h"

/// Struct defined in msg/CloudIndexed in the package gpd_ros_messages.
/**
  * This message holds a point cloud and a list of indices into the point cloud 
  * at which to sample grasp candidates.
 */
typedef struct gpd_ros_messages__msg__CloudIndexed
{
  /// The point cloud.
  gpd_ros_messages__msg__CloudSources cloud_sources;
  /// The indices into the point cloud at which to sample grasp candidates.
  std_msgs__msg__Int64__Sequence indices;
} gpd_ros_messages__msg__CloudIndexed;

// Struct for a sequence of gpd_ros_messages__msg__CloudIndexed.
typedef struct gpd_ros_messages__msg__CloudIndexed__Sequence
{
  gpd_ros_messages__msg__CloudIndexed * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} gpd_ros_messages__msg__CloudIndexed__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_INDEXED__STRUCT_H_
