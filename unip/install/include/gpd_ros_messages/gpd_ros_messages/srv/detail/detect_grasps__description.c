// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from gpd_ros_messages:srv/DetectGrasps.idl
// generated code does not contain a copyright notice

#include "gpd_ros_messages/srv/detail/detect_grasps__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_gpd_ros_messages
const rosidl_type_hash_t *
gpd_ros_messages__srv__DetectGrasps__get_type_hash(
  const rosidl_service_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x55, 0xe6, 0xda, 0x9d, 0x11, 0x5e, 0x9d, 0x50,
      0x74, 0xc1, 0x43, 0x29, 0x03, 0x38, 0xec, 0x83,
      0xc8, 0x2a, 0x9a, 0xde, 0x6e, 0x7b, 0xb7, 0x3c,
      0xf1, 0x63, 0x3a, 0x98, 0x11, 0xd1, 0x13, 0x26,
    }};
  return &hash;
}

ROSIDL_GENERATOR_C_PUBLIC_gpd_ros_messages
const rosidl_type_hash_t *
gpd_ros_messages__srv__DetectGrasps_Request__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x6c, 0x02, 0xd9, 0xda, 0x3f, 0xd6, 0x83, 0x59,
      0x10, 0x48, 0x8a, 0x4d, 0x7e, 0x72, 0x32, 0xa0,
      0x5b, 0x13, 0xfd, 0xa2, 0x29, 0x26, 0xf6, 0x3f,
      0x58, 0x94, 0xb3, 0x69, 0x95, 0xd7, 0xda, 0xc7,
    }};
  return &hash;
}

ROSIDL_GENERATOR_C_PUBLIC_gpd_ros_messages
const rosidl_type_hash_t *
gpd_ros_messages__srv__DetectGrasps_Response__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x85, 0x8f, 0xfa, 0x42, 0xeb, 0xe8, 0x59, 0x79,
      0xad, 0x59, 0xc7, 0x6b, 0x00, 0x70, 0x9a, 0x87,
      0xfb, 0x79, 0x49, 0xc6, 0x3e, 0x6a, 0x79, 0x99,
      0x6a, 0x25, 0x22, 0x8a, 0x37, 0x82, 0xe5, 0x1d,
    }};
  return &hash;
}

ROSIDL_GENERATOR_C_PUBLIC_gpd_ros_messages
const rosidl_type_hash_t *
gpd_ros_messages__srv__DetectGrasps_Event__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x7c, 0x4f, 0x63, 0x22, 0x40, 0x73, 0xba, 0x43,
      0xc6, 0xf2, 0x41, 0x82, 0x82, 0x7c, 0x98, 0x88,
      0xad, 0x88, 0x34, 0xc9, 0x43, 0x05, 0xb0, 0x12,
      0xc8, 0x5b, 0x97, 0xfc, 0xe7, 0x27, 0x3f, 0xe1,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "std_msgs/msg/detail/header__functions.h"
#include "gpd_ros_messages/msg/detail/cloud_indexed__functions.h"
#include "std_msgs/msg/detail/int64__functions.h"
#include "geometry_msgs/msg/detail/point__functions.h"
#include "sensor_msgs/msg/detail/point_field__functions.h"
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "geometry_msgs/msg/detail/vector3__functions.h"
#include "gpd_ros_messages/msg/detail/grasp_config_list__functions.h"
#include "service_msgs/msg/detail/service_event_info__functions.h"
#include "gpd_ros_messages/msg/detail/grasp_config__functions.h"
#include "sensor_msgs/msg/detail/point_cloud2__functions.h"
#include "std_msgs/msg/detail/float32__functions.h"
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
static const rosidl_type_hash_t geometry_msgs__msg__Vector3__EXPECTED_HASH = {1, {
    0xcc, 0x12, 0xfe, 0x83, 0xe4, 0xc0, 0x27, 0x19,
    0xf1, 0xce, 0x80, 0x70, 0xbf, 0xd1, 0x4a, 0xec,
    0xd4, 0x0f, 0x75, 0xa9, 0x66, 0x96, 0xa6, 0x7a,
    0x2a, 0x1f, 0x37, 0xf7, 0xdb, 0xb0, 0x76, 0x5d,
  }};
static const rosidl_type_hash_t gpd_ros_messages__msg__CloudIndexed__EXPECTED_HASH = {1, {
    0x43, 0xd1, 0xf3, 0x5e, 0xd8, 0x20, 0x01, 0x28,
    0xef, 0x5f, 0x62, 0xe7, 0x00, 0x49, 0x2b, 0x57,
    0x94, 0x82, 0x9f, 0xed, 0x01, 0x7d, 0x5a, 0x5a,
    0x64, 0x23, 0x8e, 0x6e, 0xe2, 0x71, 0xe9, 0xa9,
  }};
static const rosidl_type_hash_t gpd_ros_messages__msg__CloudSources__EXPECTED_HASH = {1, {
    0x38, 0xc4, 0xfa, 0x9c, 0xb0, 0x43, 0x5a, 0x8d,
    0x43, 0xe7, 0x62, 0xde, 0x64, 0xe3, 0xcf, 0x15,
    0x89, 0xdb, 0x30, 0xf5, 0xc0, 0x8e, 0x74, 0x2e,
    0x3c, 0xcc, 0x19, 0x8f, 0x2d, 0xde, 0xb0, 0x7f,
  }};
static const rosidl_type_hash_t gpd_ros_messages__msg__GraspConfig__EXPECTED_HASH = {1, {
    0x0e, 0x5c, 0x5e, 0xf4, 0x08, 0xbb, 0x03, 0xf9,
    0x77, 0xcb, 0xe8, 0x1b, 0x1b, 0x09, 0x7e, 0x87,
    0x16, 0x0e, 0x27, 0x42, 0x9d, 0x48, 0x9a, 0x1e,
    0xbb, 0xfc, 0x25, 0xc6, 0x9f, 0x96, 0x15, 0x89,
  }};
static const rosidl_type_hash_t gpd_ros_messages__msg__GraspConfigList__EXPECTED_HASH = {1, {
    0xc8, 0x52, 0xac, 0xd1, 0x9e, 0x36, 0x30, 0x90,
    0x69, 0x14, 0x9c, 0x03, 0xc7, 0xe3, 0xbb, 0x61,
    0x97, 0xba, 0xde, 0x0f, 0xe1, 0xc4, 0xb4, 0x58,
    0xea, 0x93, 0x77, 0x19, 0x23, 0x50, 0x7f, 0xea,
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
static const rosidl_type_hash_t service_msgs__msg__ServiceEventInfo__EXPECTED_HASH = {1, {
    0x41, 0xbc, 0xbb, 0xe0, 0x7a, 0x75, 0xc9, 0xb5,
    0x2b, 0xc9, 0x6b, 0xfd, 0x5c, 0x24, 0xd7, 0xf0,
    0xfc, 0x0a, 0x08, 0xc0, 0xcb, 0x79, 0x21, 0xb3,
    0x37, 0x3c, 0x57, 0x32, 0x34, 0x5a, 0x6f, 0x45,
  }};
static const rosidl_type_hash_t std_msgs__msg__Float32__EXPECTED_HASH = {1, {
    0x71, 0x70, 0xd3, 0xd8, 0xf8, 0x41, 0xf7, 0xbe,
    0x31, 0x72, 0xce, 0x5f, 0x4f, 0x59, 0xf3, 0xa4,
    0xd7, 0xf6, 0x3b, 0x04, 0x47, 0xe8, 0xb3, 0x33,
    0x27, 0x60, 0x1a, 0xd6, 0x4d, 0x83, 0xd6, 0xe2,
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

static char gpd_ros_messages__srv__DetectGrasps__TYPE_NAME[] = "gpd_ros_messages/srv/DetectGrasps";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char geometry_msgs__msg__Point__TYPE_NAME[] = "geometry_msgs/msg/Point";
static char geometry_msgs__msg__Vector3__TYPE_NAME[] = "geometry_msgs/msg/Vector3";
static char gpd_ros_messages__msg__CloudIndexed__TYPE_NAME[] = "gpd_ros_messages/msg/CloudIndexed";
static char gpd_ros_messages__msg__CloudSources__TYPE_NAME[] = "gpd_ros_messages/msg/CloudSources";
static char gpd_ros_messages__msg__GraspConfig__TYPE_NAME[] = "gpd_ros_messages/msg/GraspConfig";
static char gpd_ros_messages__msg__GraspConfigList__TYPE_NAME[] = "gpd_ros_messages/msg/GraspConfigList";
static char gpd_ros_messages__srv__DetectGrasps_Event__TYPE_NAME[] = "gpd_ros_messages/srv/DetectGrasps_Event";
static char gpd_ros_messages__srv__DetectGrasps_Request__TYPE_NAME[] = "gpd_ros_messages/srv/DetectGrasps_Request";
static char gpd_ros_messages__srv__DetectGrasps_Response__TYPE_NAME[] = "gpd_ros_messages/srv/DetectGrasps_Response";
static char sensor_msgs__msg__PointCloud2__TYPE_NAME[] = "sensor_msgs/msg/PointCloud2";
static char sensor_msgs__msg__PointField__TYPE_NAME[] = "sensor_msgs/msg/PointField";
static char service_msgs__msg__ServiceEventInfo__TYPE_NAME[] = "service_msgs/msg/ServiceEventInfo";
static char std_msgs__msg__Float32__TYPE_NAME[] = "std_msgs/msg/Float32";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";
static char std_msgs__msg__Int64__TYPE_NAME[] = "std_msgs/msg/Int64";

// Define type names, field names, and default values
static char gpd_ros_messages__srv__DetectGrasps__FIELD_NAME__request_message[] = "request_message";
static char gpd_ros_messages__srv__DetectGrasps__FIELD_NAME__response_message[] = "response_message";
static char gpd_ros_messages__srv__DetectGrasps__FIELD_NAME__event_message[] = "event_message";

static rosidl_runtime_c__type_description__Field gpd_ros_messages__srv__DetectGrasps__FIELDS[] = {
  {
    {gpd_ros_messages__srv__DetectGrasps__FIELD_NAME__request_message, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {gpd_ros_messages__srv__DetectGrasps_Request__TYPE_NAME, 41, 41},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__srv__DetectGrasps__FIELD_NAME__response_message, 16, 16},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {gpd_ros_messages__srv__DetectGrasps_Response__TYPE_NAME, 42, 42},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__srv__DetectGrasps__FIELD_NAME__event_message, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {gpd_ros_messages__srv__DetectGrasps_Event__TYPE_NAME, 39, 39},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription gpd_ros_messages__srv__DetectGrasps__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__CloudIndexed__TYPE_NAME, 33, 33},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__CloudSources__TYPE_NAME, 33, 33},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfig__TYPE_NAME, 32, 32},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfigList__TYPE_NAME, 36, 36},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__srv__DetectGrasps_Event__TYPE_NAME, 39, 39},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__srv__DetectGrasps_Request__TYPE_NAME, 41, 41},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__srv__DetectGrasps_Response__TYPE_NAME, 42, 42},
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
    {service_msgs__msg__ServiceEventInfo__TYPE_NAME, 33, 33},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Float32__TYPE_NAME, 20, 20},
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
gpd_ros_messages__srv__DetectGrasps__get_type_description(
  const rosidl_service_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {gpd_ros_messages__srv__DetectGrasps__TYPE_NAME, 33, 33},
      {gpd_ros_messages__srv__DetectGrasps__FIELDS, 3, 3},
    },
    {gpd_ros_messages__srv__DetectGrasps__REFERENCED_TYPE_DESCRIPTIONS, 16, 16},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Vector3__EXPECTED_HASH, geometry_msgs__msg__Vector3__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = geometry_msgs__msg__Vector3__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__CloudIndexed__EXPECTED_HASH, gpd_ros_messages__msg__CloudIndexed__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = gpd_ros_messages__msg__CloudIndexed__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__CloudSources__EXPECTED_HASH, gpd_ros_messages__msg__CloudSources__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = gpd_ros_messages__msg__CloudSources__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__GraspConfig__EXPECTED_HASH, gpd_ros_messages__msg__GraspConfig__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[5].fields = gpd_ros_messages__msg__GraspConfig__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__GraspConfigList__EXPECTED_HASH, gpd_ros_messages__msg__GraspConfigList__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[6].fields = gpd_ros_messages__msg__GraspConfigList__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[7].fields = gpd_ros_messages__srv__DetectGrasps_Event__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[8].fields = gpd_ros_messages__srv__DetectGrasps_Request__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[9].fields = gpd_ros_messages__srv__DetectGrasps_Response__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__PointCloud2__EXPECTED_HASH, sensor_msgs__msg__PointCloud2__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[10].fields = sensor_msgs__msg__PointCloud2__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__PointField__EXPECTED_HASH, sensor_msgs__msg__PointField__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[11].fields = sensor_msgs__msg__PointField__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&service_msgs__msg__ServiceEventInfo__EXPECTED_HASH, service_msgs__msg__ServiceEventInfo__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[12].fields = service_msgs__msg__ServiceEventInfo__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Float32__EXPECTED_HASH, std_msgs__msg__Float32__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[13].fields = std_msgs__msg__Float32__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[14].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Int64__EXPECTED_HASH, std_msgs__msg__Int64__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[15].fields = std_msgs__msg__Int64__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}
// Define type names, field names, and default values
static char gpd_ros_messages__srv__DetectGrasps_Request__FIELD_NAME__cloud_indexed[] = "cloud_indexed";

static rosidl_runtime_c__type_description__Field gpd_ros_messages__srv__DetectGrasps_Request__FIELDS[] = {
  {
    {gpd_ros_messages__srv__DetectGrasps_Request__FIELD_NAME__cloud_indexed, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {gpd_ros_messages__msg__CloudIndexed__TYPE_NAME, 33, 33},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription gpd_ros_messages__srv__DetectGrasps_Request__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__CloudIndexed__TYPE_NAME, 33, 33},
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
gpd_ros_messages__srv__DetectGrasps_Request__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {gpd_ros_messages__srv__DetectGrasps_Request__TYPE_NAME, 41, 41},
      {gpd_ros_messages__srv__DetectGrasps_Request__FIELDS, 1, 1},
    },
    {gpd_ros_messages__srv__DetectGrasps_Request__REFERENCED_TYPE_DESCRIPTIONS, 8, 8},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__CloudIndexed__EXPECTED_HASH, gpd_ros_messages__msg__CloudIndexed__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = gpd_ros_messages__msg__CloudIndexed__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__CloudSources__EXPECTED_HASH, gpd_ros_messages__msg__CloudSources__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = gpd_ros_messages__msg__CloudSources__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__PointCloud2__EXPECTED_HASH, sensor_msgs__msg__PointCloud2__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = sensor_msgs__msg__PointCloud2__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__PointField__EXPECTED_HASH, sensor_msgs__msg__PointField__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[5].fields = sensor_msgs__msg__PointField__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[6].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Int64__EXPECTED_HASH, std_msgs__msg__Int64__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[7].fields = std_msgs__msg__Int64__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}
// Define type names, field names, and default values
static char gpd_ros_messages__srv__DetectGrasps_Response__FIELD_NAME__grasp_configs[] = "grasp_configs";

static rosidl_runtime_c__type_description__Field gpd_ros_messages__srv__DetectGrasps_Response__FIELDS[] = {
  {
    {gpd_ros_messages__srv__DetectGrasps_Response__FIELD_NAME__grasp_configs, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {gpd_ros_messages__msg__GraspConfigList__TYPE_NAME, 36, 36},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription gpd_ros_messages__srv__DetectGrasps_Response__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfig__TYPE_NAME, 32, 32},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfigList__TYPE_NAME, 36, 36},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Float32__TYPE_NAME, 20, 20},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
gpd_ros_messages__srv__DetectGrasps_Response__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {gpd_ros_messages__srv__DetectGrasps_Response__TYPE_NAME, 42, 42},
      {gpd_ros_messages__srv__DetectGrasps_Response__FIELDS, 1, 1},
    },
    {gpd_ros_messages__srv__DetectGrasps_Response__REFERENCED_TYPE_DESCRIPTIONS, 7, 7},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Vector3__EXPECTED_HASH, geometry_msgs__msg__Vector3__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = geometry_msgs__msg__Vector3__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__GraspConfig__EXPECTED_HASH, gpd_ros_messages__msg__GraspConfig__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = gpd_ros_messages__msg__GraspConfig__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__GraspConfigList__EXPECTED_HASH, gpd_ros_messages__msg__GraspConfigList__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = gpd_ros_messages__msg__GraspConfigList__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Float32__EXPECTED_HASH, std_msgs__msg__Float32__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[5].fields = std_msgs__msg__Float32__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[6].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}
// Define type names, field names, and default values
static char gpd_ros_messages__srv__DetectGrasps_Event__FIELD_NAME__info[] = "info";
static char gpd_ros_messages__srv__DetectGrasps_Event__FIELD_NAME__request[] = "request";
static char gpd_ros_messages__srv__DetectGrasps_Event__FIELD_NAME__response[] = "response";

static rosidl_runtime_c__type_description__Field gpd_ros_messages__srv__DetectGrasps_Event__FIELDS[] = {
  {
    {gpd_ros_messages__srv__DetectGrasps_Event__FIELD_NAME__info, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {service_msgs__msg__ServiceEventInfo__TYPE_NAME, 33, 33},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__srv__DetectGrasps_Event__FIELD_NAME__request, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_BOUNDED_SEQUENCE,
      1,
      0,
      {gpd_ros_messages__srv__DetectGrasps_Request__TYPE_NAME, 41, 41},
    },
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__srv__DetectGrasps_Event__FIELD_NAME__response, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE_BOUNDED_SEQUENCE,
      1,
      0,
      {gpd_ros_messages__srv__DetectGrasps_Response__TYPE_NAME, 42, 42},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription gpd_ros_messages__srv__DetectGrasps_Event__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Vector3__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__CloudIndexed__TYPE_NAME, 33, 33},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__CloudSources__TYPE_NAME, 33, 33},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfig__TYPE_NAME, 32, 32},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__msg__GraspConfigList__TYPE_NAME, 36, 36},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__srv__DetectGrasps_Request__TYPE_NAME, 41, 41},
    {NULL, 0, 0},
  },
  {
    {gpd_ros_messages__srv__DetectGrasps_Response__TYPE_NAME, 42, 42},
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
    {service_msgs__msg__ServiceEventInfo__TYPE_NAME, 33, 33},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Float32__TYPE_NAME, 20, 20},
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
gpd_ros_messages__srv__DetectGrasps_Event__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {gpd_ros_messages__srv__DetectGrasps_Event__TYPE_NAME, 39, 39},
      {gpd_ros_messages__srv__DetectGrasps_Event__FIELDS, 3, 3},
    },
    {gpd_ros_messages__srv__DetectGrasps_Event__REFERENCED_TYPE_DESCRIPTIONS, 15, 15},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Vector3__EXPECTED_HASH, geometry_msgs__msg__Vector3__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = geometry_msgs__msg__Vector3__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__CloudIndexed__EXPECTED_HASH, gpd_ros_messages__msg__CloudIndexed__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = gpd_ros_messages__msg__CloudIndexed__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__CloudSources__EXPECTED_HASH, gpd_ros_messages__msg__CloudSources__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = gpd_ros_messages__msg__CloudSources__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__GraspConfig__EXPECTED_HASH, gpd_ros_messages__msg__GraspConfig__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[5].fields = gpd_ros_messages__msg__GraspConfig__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&gpd_ros_messages__msg__GraspConfigList__EXPECTED_HASH, gpd_ros_messages__msg__GraspConfigList__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[6].fields = gpd_ros_messages__msg__GraspConfigList__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[7].fields = gpd_ros_messages__srv__DetectGrasps_Request__get_type_description(NULL)->type_description.fields;
    description.referenced_type_descriptions.data[8].fields = gpd_ros_messages__srv__DetectGrasps_Response__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__PointCloud2__EXPECTED_HASH, sensor_msgs__msg__PointCloud2__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[9].fields = sensor_msgs__msg__PointCloud2__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&sensor_msgs__msg__PointField__EXPECTED_HASH, sensor_msgs__msg__PointField__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[10].fields = sensor_msgs__msg__PointField__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&service_msgs__msg__ServiceEventInfo__EXPECTED_HASH, service_msgs__msg__ServiceEventInfo__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[11].fields = service_msgs__msg__ServiceEventInfo__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Float32__EXPECTED_HASH, std_msgs__msg__Float32__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[12].fields = std_msgs__msg__Float32__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[13].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Int64__EXPECTED_HASH, std_msgs__msg__Int64__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[14].fields = std_msgs__msg__Int64__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "gpd_ros_messages/CloudIndexed cloud_indexed\n"
  "---\n"
  "gpd_ros_messages/GraspConfigList grasp_configs";

static char srv_encoding[] = "srv";
static char implicit_encoding[] = "implicit";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
gpd_ros_messages__srv__DetectGrasps__get_individual_type_description_source(
  const rosidl_service_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {gpd_ros_messages__srv__DetectGrasps__TYPE_NAME, 33, 33},
    {srv_encoding, 3, 3},
    {toplevel_type_raw_source, 95, 95},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource *
gpd_ros_messages__srv__DetectGrasps_Request__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {gpd_ros_messages__srv__DetectGrasps_Request__TYPE_NAME, 41, 41},
    {implicit_encoding, 8, 8},
    {NULL, 0, 0},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource *
gpd_ros_messages__srv__DetectGrasps_Response__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {gpd_ros_messages__srv__DetectGrasps_Response__TYPE_NAME, 42, 42},
    {implicit_encoding, 8, 8},
    {NULL, 0, 0},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource *
gpd_ros_messages__srv__DetectGrasps_Event__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {gpd_ros_messages__srv__DetectGrasps_Event__TYPE_NAME, 39, 39},
    {implicit_encoding, 8, 8},
    {NULL, 0, 0},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
gpd_ros_messages__srv__DetectGrasps__get_type_description_sources(
  const rosidl_service_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[17];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 17, 17};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *gpd_ros_messages__srv__DetectGrasps__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[3] = *geometry_msgs__msg__Vector3__get_individual_type_description_source(NULL);
    sources[4] = *gpd_ros_messages__msg__CloudIndexed__get_individual_type_description_source(NULL);
    sources[5] = *gpd_ros_messages__msg__CloudSources__get_individual_type_description_source(NULL);
    sources[6] = *gpd_ros_messages__msg__GraspConfig__get_individual_type_description_source(NULL);
    sources[7] = *gpd_ros_messages__msg__GraspConfigList__get_individual_type_description_source(NULL);
    sources[8] = *gpd_ros_messages__srv__DetectGrasps_Event__get_individual_type_description_source(NULL);
    sources[9] = *gpd_ros_messages__srv__DetectGrasps_Request__get_individual_type_description_source(NULL);
    sources[10] = *gpd_ros_messages__srv__DetectGrasps_Response__get_individual_type_description_source(NULL);
    sources[11] = *sensor_msgs__msg__PointCloud2__get_individual_type_description_source(NULL);
    sources[12] = *sensor_msgs__msg__PointField__get_individual_type_description_source(NULL);
    sources[13] = *service_msgs__msg__ServiceEventInfo__get_individual_type_description_source(NULL);
    sources[14] = *std_msgs__msg__Float32__get_individual_type_description_source(NULL);
    sources[15] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    sources[16] = *std_msgs__msg__Int64__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
gpd_ros_messages__srv__DetectGrasps_Request__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[9];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 9, 9};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *gpd_ros_messages__srv__DetectGrasps_Request__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[3] = *gpd_ros_messages__msg__CloudIndexed__get_individual_type_description_source(NULL);
    sources[4] = *gpd_ros_messages__msg__CloudSources__get_individual_type_description_source(NULL);
    sources[5] = *sensor_msgs__msg__PointCloud2__get_individual_type_description_source(NULL);
    sources[6] = *sensor_msgs__msg__PointField__get_individual_type_description_source(NULL);
    sources[7] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    sources[8] = *std_msgs__msg__Int64__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
gpd_ros_messages__srv__DetectGrasps_Response__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[8];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 8, 8};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *gpd_ros_messages__srv__DetectGrasps_Response__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[3] = *geometry_msgs__msg__Vector3__get_individual_type_description_source(NULL);
    sources[4] = *gpd_ros_messages__msg__GraspConfig__get_individual_type_description_source(NULL);
    sources[5] = *gpd_ros_messages__msg__GraspConfigList__get_individual_type_description_source(NULL);
    sources[6] = *std_msgs__msg__Float32__get_individual_type_description_source(NULL);
    sources[7] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
gpd_ros_messages__srv__DetectGrasps_Event__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[16];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 16, 16};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *gpd_ros_messages__srv__DetectGrasps_Event__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[3] = *geometry_msgs__msg__Vector3__get_individual_type_description_source(NULL);
    sources[4] = *gpd_ros_messages__msg__CloudIndexed__get_individual_type_description_source(NULL);
    sources[5] = *gpd_ros_messages__msg__CloudSources__get_individual_type_description_source(NULL);
    sources[6] = *gpd_ros_messages__msg__GraspConfig__get_individual_type_description_source(NULL);
    sources[7] = *gpd_ros_messages__msg__GraspConfigList__get_individual_type_description_source(NULL);
    sources[8] = *gpd_ros_messages__srv__DetectGrasps_Request__get_individual_type_description_source(NULL);
    sources[9] = *gpd_ros_messages__srv__DetectGrasps_Response__get_individual_type_description_source(NULL);
    sources[10] = *sensor_msgs__msg__PointCloud2__get_individual_type_description_source(NULL);
    sources[11] = *sensor_msgs__msg__PointField__get_individual_type_description_source(NULL);
    sources[12] = *service_msgs__msg__ServiceEventInfo__get_individual_type_description_source(NULL);
    sources[13] = *std_msgs__msg__Float32__get_individual_type_description_source(NULL);
    sources[14] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    sources[15] = *std_msgs__msg__Int64__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
