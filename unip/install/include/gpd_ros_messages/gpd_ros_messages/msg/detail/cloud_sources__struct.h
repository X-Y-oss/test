// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from gpd_ros_messages:msg/CloudSources.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "gpd_ros_messages/msg/cloud_sources.h"


#ifndef GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SOURCES__STRUCT_H_
#define GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SOURCES__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'cloud'
#include "sensor_msgs/msg/detail/point_cloud2__struct.h"
// Member 'camera_source'
#include "std_msgs/msg/detail/int64__struct.h"
// Member 'view_points'
#include "geometry_msgs/msg/detail/point__struct.h"

/// Struct defined in msg/CloudSources in the package gpd_ros_messages.
/**
  * This message holds a point cloud that can be a combination of point clouds 
  * from different camera sources (at least one). For each point in the cloud, 
  * this message also stores the index of the camera that produced the point.
 */
typedef struct gpd_ros_messages__msg__CloudSources
{
  /// The point cloud.
  sensor_msgs__msg__PointCloud2 cloud;
  /// For each point in the cloud, the index of the camera that acquired the point.
  std_msgs__msg__Int64__Sequence camera_source;
  /// A list of camera positions at which the point cloud was acquired.
  geometry_msgs__msg__Point__Sequence view_points;
} gpd_ros_messages__msg__CloudSources;

// Struct for a sequence of gpd_ros_messages__msg__CloudSources.
typedef struct gpd_ros_messages__msg__CloudSources__Sequence
{
  gpd_ros_messages__msg__CloudSources * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} gpd_ros_messages__msg__CloudSources__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SOURCES__STRUCT_H_
