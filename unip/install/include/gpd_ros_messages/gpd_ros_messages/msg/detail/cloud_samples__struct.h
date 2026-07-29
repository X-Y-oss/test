// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from gpd_ros_messages:msg/CloudSamples.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "gpd_ros_messages/msg/cloud_samples.h"


#ifndef GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SAMPLES__STRUCT_H_
#define GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SAMPLES__STRUCT_H_

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
// Member 'samples'
#include "geometry_msgs/msg/detail/point__struct.h"

/// Struct defined in msg/CloudSamples in the package gpd_ros_messages.
/**
  * This message holds a point cloud and a list of samples at which the grasp 
  * detector should search for grasp candidates.
 */
typedef struct gpd_ros_messages__msg__CloudSamples
{
  /// The point cloud.
  gpd_ros_messages__msg__CloudSources cloud_sources;
  /// The samples, as (x,y,z) points, at which to search for grasp candidates.
  geometry_msgs__msg__Point__Sequence samples;
} gpd_ros_messages__msg__CloudSamples;

// Struct for a sequence of gpd_ros_messages__msg__CloudSamples.
typedef struct gpd_ros_messages__msg__CloudSamples__Sequence
{
  gpd_ros_messages__msg__CloudSamples * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} gpd_ros_messages__msg__CloudSamples__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SAMPLES__STRUCT_H_
