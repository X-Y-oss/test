// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from gpd_ros_messages:msg/GraspConfig.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "gpd_ros_messages/msg/grasp_config.h"


#ifndef GPD_ROS_MESSAGES__MSG__DETAIL__GRASP_CONFIG__STRUCT_H_
#define GPD_ROS_MESSAGES__MSG__DETAIL__GRASP_CONFIG__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'position'
// Member 'sample'
#include "geometry_msgs/msg/detail/point__struct.h"
// Member 'approach'
// Member 'binormal'
// Member 'axis'
#include "geometry_msgs/msg/detail/vector3__struct.h"
// Member 'width'
// Member 'score'
#include "std_msgs/msg/detail/float32__struct.h"

/// Struct defined in msg/GraspConfig in the package gpd_ros_messages.
/**
  * This message describes a 2-finger grasp configuration by its 6-DOF pose,
  * consisting of a 3-DOF position and 3-DOF orientation, and the opening
  * width of the robot hand.
 */
typedef struct gpd_ros_messages__msg__GraspConfig
{
  /// Position
  /// grasp position (bottom/base center of robot hand)
  geometry_msgs__msg__Point position;
  /// Orientation represented as three axis (R =)
  /// grasp approach direction
  geometry_msgs__msg__Vector3 approach;
  /// hand closing direction
  geometry_msgs__msg__Vector3 binormal;
  /// hand axis
  geometry_msgs__msg__Vector3 axis;
  /// Required aperture (opening width) of the robot hand
  std_msgs__msg__Float32 width;
  /// Score assigned to the grasp by the classifier
  std_msgs__msg__Float32 score;
  /// point at which the grasp was found
  geometry_msgs__msg__Point sample;
} gpd_ros_messages__msg__GraspConfig;

// Struct for a sequence of gpd_ros_messages__msg__GraspConfig.
typedef struct gpd_ros_messages__msg__GraspConfig__Sequence
{
  gpd_ros_messages__msg__GraspConfig * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} gpd_ros_messages__msg__GraspConfig__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GPD_ROS_MESSAGES__MSG__DETAIL__GRASP_CONFIG__STRUCT_H_
