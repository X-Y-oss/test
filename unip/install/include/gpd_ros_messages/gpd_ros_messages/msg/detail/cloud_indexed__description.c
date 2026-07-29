// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from gpd_ros_messages:msg/CloudIndexed.idl
// generated code does not contain a copyright notice

#include "gpd_ros_messages/msg/detail/cloud_indexed__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_gpd_ros_messages
const rosidl_type_hash_t *
gpd_ros_messages__msg__CloudIndexed__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x43, 0xd1, 0xf3, 0x5e, 0xd8, 0x20, 0x01, 0x28,
      0xef, 0x5f, 0x62, 0xe7, 0x00, 0x49, 0x2b, 0x57,
      0x94, 0x82, 0x9f, 0xed, 0x01, 0x7d, 0x5a, 0x5a,
      0x64, 0x23, 0x8e, 0x6e, 0xe2, 0x71, 0xe9, 0xa9,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "std_msgs/msg/detail/int64__functions.h"
#include "geometry_msgs/msg/detail/point__functions.h"
#include "sensor_msgs/msg/detail/point_field__functions.h"
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "sensor_msgs/msg/detail/point_cloud2__functions.h"
#include "std_msgs/msg/detail/header__functions.h"
#include "gpd_ros_messages/msg/detail/cloud_sources__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t geometry_msgs__msg__Point__EXPECTED_HASH = {1, {
    0x69, 0x63, 0x08, 0x48, 0x42, 0xa9, 0xb0, 0x44,
    0x94, 0xd6, 0xb2, 0x94, 0x1d, 0x11, 0x44, 0x47,
    0x08, 0xd8, 0x92, 0xda, 0x2f, 0x4b, 0x09, 0x84,
    0x3b, 0x9c, 0x43, 0xf4, 0x2a, 0x7f, 0x68, 0x81,
  }};
static const rosidl_type_hash_t gpd_ros_messages__msg__CloudSources__EXPECTED_HASH = {1, {
    0x38, 0xc4, 0xfa, 0x9c, 0xb0, 0x43, 0x5a, 0x8d,
    0x43, 0xe7, 0x62, 0xde, 0x64, 0xe3, 0xcf, 0x15,
    0x89, 0xdb, 0x30, 0xf5, 0xc0, 0x8e, 0x74, 0x2e,
    0x3c, 0xcc, 0x19, 0x8f, 0x2d, 0xde, 0xb0, 0x7f,
  }};
static const rosidl_type_hash_t sensor_msgs__msg__PointCloud2__EXPECTED_HASH = {1, {
    0x91, 0x98, 0xca, 0xbf, 0x7d, 0xa3, 0x79, 0x6a,
    0xe6, 0xfe, 0x19, 0xc4, 0xcb, 0x3b, 0xdd, 0x35,
    0x25, 0x49, 0x29, 0x88, 0xc7, 0x05, 0x22, 0x62,
    0x8a, 0xf5, 0xda, 0xa1, 0x24, 0xba, 0xe2, 0xb5,
  }};
static const rosidl_type_hash_t sensor_msgs__msg__PointField__EXPECTED_HASH = {1, {
    0x5c, 0x6a, 0x47, 0x50, 0x72, 0x8c, 0x2b, 0xcf,
    0xbb, 0xf7, 0x03, 0x72, 0x25, 0xb2, 0x0b, 0x02,
    0xd4, 0x42, 0x96, 0x34, 0x73, 0x21, 0x46, 0xb7,
    0x42, 0xde, 0xe1, 0x72, 0x66, 0x37, 0xef, 0x01,
  }};
static const rosidl_type_hash_t std_msgs__msg__Header__EXPECTED_HASH = {1, {
    0xf4, 0x9f, 0xb3, 0xae, 0x2c, 0xf0, 0x70, 0xf7,
    0x93, 0x64, 0x5f, 0xf7, 0x49, 0x68, 0x3a, 0xc6,
    0xb0, 0x62, 0x03, 0xe4, 0x1c, 0x89, 0x1e, 0x17,
    0x70, 0x1b, 0x1c, 0xb5, 0x97, 0xce, 0x6a, 0x01,
  }};
static const rosidl_type_hash_t std_msgs__msg__Int64__EXPECTED_HASH = {1, {
    0x8c, 0xd1, 0x04, 0x8c, 0x2f, 0x18, 0x6b, 0x6b,
    0xd9, 0xa9, 0x24, 0x72, 0xdc, 0x1c, 0xe5, 0x17,
    0x23, 0xc0, 0x83, 0x3a, 0x22, 0x1e, 0x2b, 0x7a,
    0xec, 0xff, 0xf1, 0x11, 0x77, 0x4f, 0x4b, 0x49,
  }};
#endif

static char gpd_ros_messages__msg__CloudIndexed__TYPE_NAME[] = "gpd_ros_messages/msg/CloudIndexed";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char geometry_msgs__msg__Point__TYPE_NAME[] = "geometry_msgs/msg/Point";
static char gpd_ros_messages__msg__CloudSources__TYPE_NAME[] = "gpd_ros_messages/msg/CloudSources";
static char sensor_msgs__msg__PointCloud2__TYPE_NAME[] = "sensor_msgs/msg/PointCloud2";
static char sensor_msgs__msg__PointField__TYPE_NAME[] = "sensor_msgs/msg/PointField";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";
static char std_msgs__msg__Int64__TYPE_NAME[] = "std_msgs/msg/Int64";

// Define type names, field names, and default values
static char gpd_ros_messages__msg__CloudIndexed__FIELD_NAME__cloud_sources[] = "cloud_sources";
static char gpd_ros_messages__msg__CloudIndexed__FIELD_NAME__indices[] = "indices";

static rosidl_runtime_c__type_description__Field gpd_ros_messages__msg__CloudIndexed__FIELDS[] = {
  {
    {gpd_ros_messages__msg__CloudIndexed__FIELD_NAME__cloud_sources, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {gpd_ros_messages__msg__CloudSources__TYPE_NAME, 33, 33},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__CloudIndexed__FIELD_NAME__indices, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_UNBOUNDED_SEQUENCE,
      0,
      0,
      {std_msgs__msg__Int64__TYPE_NAME, 18, 18},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription gpd_ros_messages__msg__CloudIndexed__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__CloudSources__TYPE_NAME, 33, 33},
    {NULL, 0, 0},
  },
  {
    {sensor_msgs__msg__PointCloud2__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {sensor_msgs__msg__PointField__TYPE_NAME, 26, 26},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Int64__TYPE_NAME, 18, 18},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
gpd_ros_messages__msg__CloudIndexed__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {gpd_ros_messages__msg__CloudIndexed__TYPE_NAME, 33, 33},
      {gpd_ros_messages__msg__CloudIndexed__FIELDS, 2, 2},
    },
    {gpd_ros_messages__msg__CloudIndexed__REFERENCED_TYPE_DESCRIPTIONS, 7, 7},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__CloudSources__EXPECTED_HASH, gpd_ros_messages__msg__CloudSources__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = gpd_ros_messages__msg__CloudSources__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__PointCloud2__EXPECTED_HASH, sensor_msgs__msg__PointCloud2__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = sensor_msgs__msg__PointCloud2__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__PointField__EXPECTED_HASH, sensor_msgs__msg__PointField__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = sensor_msgs__msg__PointField__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[5].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Int64__EXPECTED_HASH, std_msgs__msg__Int64__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[6].fields = std_msgs__msg__Int64__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# This message holds a point cloud and a list of indices into the point cloud \n"
  "# at which to sample grasp candidates.\n"
  "\n"
  "# The point cloud.\n"
  "gpd_ros_messages/CloudSources cloud_sources\n"
  "\n"
  "# The indices into the point cloud at which to sample grasp candidates.\n"
  "std_msgs/Int64[] indices";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
gpd_ros_messages__msg__CloudIndexed__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {gpd_ros_messages__msg__CloudIndexed__TYPE_NAME, 33, 33},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 280, 280},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
gpd_ros_messages__msg__CloudIndexed__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[8];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 8, 8};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *gpd_ros_messages__msg__CloudIndexed__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[3] = *gpd_ros_messages__msg__CloudSources__get_individual_type_description_source(NULL);
    sources[4] = *sensor_msgs__msg__PointCloud2__get_individual_type_description_source(NULL);
    sources[5] = *sensor_msgs__msg__PointField__get_individual_type_description_source(NULL);
    sources[6] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    sources[7] = *std_msgs__msg__Int64__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
