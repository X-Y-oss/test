// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from gpd_ros_messages:msg/GraspConfig.idl
// generated code does not contain a copyright notice

#include "gpd_ros_messages/msg/detail/grasp_config__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_gpd_ros_messages
const rosidl_type_hash_t *
gpd_ros_messages__msg__GraspConfig__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x0e, 0x5c, 0x5e, 0xf4, 0x08, 0xbb, 0x03, 0xf9,
      0x77, 0xcb, 0xe8, 0x1b, 0x1b, 0x09, 0x7e, 0x87,
      0x16, 0x0e, 0x27, 0x42, 0x9d, 0x48, 0x9a, 0x1e,
      0xbb, 0xfc, 0x25, 0xc6, 0x9f, 0x96, 0x15, 0x89,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "geometry_msgs/msg/detail/point__functions.h"
#include "geometry_msgs/msg/detail/vector3__functions.h"
#include "std_msgs/msg/detail/float32__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t geometry_msgs__msg__Point__EXPECTED_HASH = {1, {
    0x69, 0x63, 0x08, 0x48, 0x42, 0xa9, 0xb0, 0x44,
    0x94, 0xd6, 0xb2, 0x94, 0x1d, 0x11, 0x44, 0x47,
    0x08, 0xd8, 0x92, 0xda, 0x2f, 0x4b, 0x09, 0x84,
    0x3b, 0x9c, 0x43, 0xf4, 0x2a, 0x7f, 0x68, 0x81,
  }};
static const rosidl_type_hash_t geometry_msgs__msg__Vector3__EXPECTED_HASH = {1, {
    0xcc, 0x12, 0xfe, 0x83, 0xe4, 0xc0, 0x27, 0x19,
    0xf1, 0xce, 0x80, 0x70, 0xbf, 0xd1, 0x4a, 0xec,
    0xd4, 0x0f, 0x75, 0xa9, 0x66, 0x96, 0xa6, 0x7a,
    0x2a, 0x1f, 0x37, 0xf7, 0xdb, 0xb0, 0x76, 0x5d,
  }};
static const rosidl_type_hash_t std_msgs__msg__Float32__EXPECTED_HASH = {1, {
    0x71, 0x70, 0xd3, 0xd8, 0xf8, 0x41, 0xf7, 0xbe,
    0x31, 0x72, 0xce, 0x5f, 0x4f, 0x59, 0xf3, 0xa4,
    0xd7, 0xf6, 0x3b, 0x04, 0x47, 0xe8, 0xb3, 0x33,
    0x27, 0x60, 0x1a, 0xd6, 0x4d, 0x83, 0xd6, 0xe2,
  }};
#endif

static char gpd_ros_messages__msg__GraspConfig__TYPE_NAME[] = "gpd_ros_messages/msg/GraspConfig";
static char geometry_msgs__msg__Point__TYPE_NAME[] = "geometry_msgs/msg/Point";
static char geometry_msgs__msg__Vector3__TYPE_NAME[] = "geometry_msgs/msg/Vector3";
static char std_msgs__msg__Float32__TYPE_NAME[] = "std_msgs/msg/Float32";

// Define type names, field names, and default values
static char gpd_ros_messages__msg__GraspConfig__FIELD_NAME__position[] = "position";
static char gpd_ros_messages__msg__GraspConfig__FIELD_NAME__approach[] = "approach";
static char gpd_ros_messages__msg__GraspConfig__FIELD_NAME__binormal[] = "binormal";
static char gpd_ros_messages__msg__GraspConfig__FIELD_NAME__axis[] = "axis";
static char gpd_ros_messages__msg__GraspConfig__FIELD_NAME__width[] = "width";
static char gpd_ros_messages__msg__GraspConfig__FIELD_NAME__score[] = "score";
static char gpd_ros_messages__msg__GraspConfig__FIELD_NAME__sample[] = "sample";

static rosidl_runtime_c__type_description__Field gpd_ros_messages__msg__GraspConfig__FIELDS[] = {
  {
    {gpd_ros_messages__msg__GraspConfig__FIELD_NAME__position, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfig__FIELD_NAME__approach, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfig__FIELD_NAME__binormal, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfig__FIELD_NAME__axis, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfig__FIELD_NAME__width, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Float32__TYPE_NAME, 20, 20},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfig__FIELD_NAME__score, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Float32__TYPE_NAME, 20, 20},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfig__FIELD_NAME__sample, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription gpd_ros_messages__msg__GraspConfig__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Float32__TYPE_NAME, 20, 20},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
gpd_ros_messages__msg__GraspConfig__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {gpd_ros_messages__msg__GraspConfig__TYPE_NAME, 32, 32},
      {gpd_ros_messages__msg__GraspConfig__FIELDS, 7, 7},
    },
    {gpd_ros_messages__msg__GraspConfig__REFERENCED_TYPE_DESCRIPTIONS, 3, 3},
  };
  if (!constructed) {
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Vector3__EXPECTED_HASH, geometry_msgs__msg__Vector3__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Vector3__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Float32__EXPECTED_HASH, std_msgs__msg__Float32__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = std_msgs__msg__Float32__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# This message describes a 2-finger grasp configuration by its 6-DOF pose,\n"
  "# consisting of a 3-DOF position and 3-DOF orientation, and the opening\n"
  "# width of the robot hand.\n"
  "\n"
  "# Position\n"
  "geometry_msgs/Point position # grasp position (bottom/base center of robot hand)\n"
  "\n"
  "# Orientation represented as three axis (R = [approach binormal axis])\n"
  "geometry_msgs/Vector3 approach # grasp approach direction\n"
  "geometry_msgs/Vector3 binormal # hand closing direction\n"
  "geometry_msgs/Vector3 axis # hand axis\n"
  "\n"
  "std_msgs/Float32 width # Required aperture (opening width) of the robot hand\n"
  "\n"
  "std_msgs/Float32 score # Score assigned to the grasp by the classifier\n"
  "\n"
  "geometry_msgs/Point sample # point at which the grasp was found";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
gpd_ros_messages__msg__GraspConfig__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {gpd_ros_messages__msg__GraspConfig__TYPE_NAME, 32, 32},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 707, 707},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
gpd_ros_messages__msg__GraspConfig__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[4];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 4, 4};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *gpd_ros_messages__msg__GraspConfig__get_individual_type_description_source(NULL),
    sources[1] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Vector3__get_individual_type_description_source(NULL);
    sources[3] = *std_msgs__msg__Float32__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
