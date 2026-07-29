// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from generate_motion_msgs:msg/GenerateMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "generate_motion_msgs/msg/generate_motion.h"


#ifndef GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__STRUCT_H_
#define GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

// Include directives for member types
// Member 'robot_file'
#include "rosidl_runtime_c/string.h"
// Member 'pose_lists'
// Member 'segment_modes'
// Member 'linear_axes'
// Member 'attach_after_index'
// Member 'detach_after_index'
// Member 'cylinder_pose'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/GenerateMotion in the package generate_motion_msgs.
typedef struct generate_motion_msgs__msg__GenerateMotion
{
  rosidl_runtime_c__String robot_file;
  rosidl_runtime_c__double__Sequence pose_lists;
  rosidl_runtime_c__int32__Sequence segment_modes;
  rosidl_runtime_c__int32__Sequence linear_axes;
  bool attach_cylinder;
  rosidl_runtime_c__int32__Sequence attach_after_index;
  rosidl_runtime_c__int32__Sequence detach_after_index;
  double cylinder_radius;
  double cylinder_height;
  rosidl_runtime_c__double__Sequence cylinder_pose;
  bool grasp_prepose_motion;
} generate_motion_msgs__msg__GenerateMotion;

// Struct for a sequence of generate_motion_msgs__msg__GenerateMotion.
typedef struct generate_motion_msgs__msg__GenerateMotion__Sequence
{
  generate_motion_msgs__msg__GenerateMotion * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} generate_motion_msgs__msg__GenerateMotion__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__STRUCT_H_
