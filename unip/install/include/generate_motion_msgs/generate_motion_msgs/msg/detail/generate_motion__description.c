// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from generate_motion_msgs:msg/GenerateMotion.idl
// generated code does not contain a copyright notice

#include "generate_motion_msgs/msg/detail/generate_motion__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
const rosidl_type_hash_t *
generate_motion_msgs__msg__GenerateMotion__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x0d, 0x67, 0x05, 0x77, 0x31, 0xe6, 0xbc, 0x9b,
      0x71, 0x0d, 0x19, 0x1d, 0x4a, 0xf7, 0xc5, 0x12,
      0x74, 0x8b, 0xdf, 0xec, 0x4a, 0x6f, 0xf0, 0x8b,
      0xda, 0xdc, 0xa4, 0xf8, 0xf8, 0x91, 0x24, 0xa3,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char generate_motion_msgs__msg__GenerateMotion__TYPE_NAME[] = "generate_motion_msgs/msg/GenerateMotion";

// Define type names, field names, and default values
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__robot_file[] = "robot_file";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__pose_lists[] = "pose_lists";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__segment_modes[] = "segment_modes";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__linear_axes[] = "linear_axes";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__attach_cylinder[] = "attach_cylinder";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__attach_after_index[] = "attach_after_index";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__detach_after_index[] = "detach_after_index";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__cylinder_radius[] = "cylinder_radius";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__cylinder_height[] = "cylinder_height";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__cylinder_pose[] = "cylinder_pose";
static char generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__grasp_prepose_motion[] = "grasp_prepose_motion";

static rosidl_runtime_c__type_description__Field generate_motion_msgs__msg__GenerateMotion__FIELDS[] = {
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__robot_file, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__pose_lists, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__segment_modes, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__linear_axes, 11, 11},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__attach_cylinder, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__attach_after_index, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__detach_after_index, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_INT32_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__cylinder_radius, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__cylinder_height, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__cylinder_pose, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_DOUBLE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {generate_motion_msgs__msg__GenerateMotion__FIELD_NAME__grasp_prepose_motion, 20, 20},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
generate_motion_msgs__msg__GenerateMotion__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {generate_motion_msgs__msg__GenerateMotion__TYPE_NAME, 39, 39},
      {generate_motion_msgs__msg__GenerateMotion__FIELDS, 11, 11},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "string robot_file\n"
  "float64[] pose_lists\n"
  "int32[] segment_modes\n"
  "int32[] linear_axes\n"
  "bool attach_cylinder\n"
  "int32[] attach_after_index\n"
  "int32[] detach_after_index\n"
  "float64 cylinder_radius\n"
  "float64 cylinder_height\n"
  "float64[] cylinder_pose\n"
  "bool grasp_prepose_motion";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
generate_motion_msgs__msg__GenerateMotion__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {generate_motion_msgs__msg__GenerateMotion__TYPE_NAME, 39, 39},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 254, 254},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
generate_motion_msgs__msg__GenerateMotion__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *generate_motion_msgs__msg__GenerateMotion__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
