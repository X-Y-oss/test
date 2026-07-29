// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from gpd_ros_messages:srv/DetectGrasps.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "gpd_ros_messages/srv/detect_grasps.h"


#ifndef GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__STRUCT_H_
#define GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'cloud_indexed'
#include "gpd_ros_messages/msg/detail/cloud_indexed__struct.h"

/// Struct defined in srv/DetectGrasps in the package gpd_ros_messages.
typedef struct gpd_ros_messages__srv__DetectGrasps_Request
{
  gpd_ros_messages__msg__CloudIndexed cloud_indexed;
} gpd_ros_messages__srv__DetectGrasps_Request;

// Struct for a sequence of gpd_ros_messages__srv__DetectGrasps_Request.
typedef struct gpd_ros_messages__srv__DetectGrasps_Request__Sequence
{
  gpd_ros_messages__srv__DetectGrasps_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} gpd_ros_messages__srv__DetectGrasps_Request__Sequence;

// Constants defined in the message

// Include directives for member types
// Member 'grasp_configs'
#include "gpd_ros_messages/msg/detail/grasp_config_list__struct.h"

/// Struct defined in srv/DetectGrasps in the package gpd_ros_messages.
typedef struct gpd_ros_messages__srv__DetectGrasps_Response
{
  gpd_ros_messages__msg__GraspConfigList grasp_configs;
} gpd_ros_messages__srv__DetectGrasps_Response;

// Struct for a sequence of gpd_ros_messages__srv__DetectGrasps_Response.
typedef struct gpd_ros_messages__srv__DetectGrasps_Response__Sequence
{
  gpd_ros_messages__srv__DetectGrasps_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} gpd_ros_messages__srv__DetectGrasps_Response__Sequence;

// Constants defined in the message

// Include directives for member types
// Member 'info'
#include "service_msgs/msg/detail/service_event_info__struct.h"

// constants for array fields with an upper bound
// request
enum
{
  gpd_ros_messages__srv__DetectGrasps_Event__request__MAX_SIZE = 1
};
// response
enum
{
  gpd_ros_messages__srv__DetectGrasps_Event__response__MAX_SIZE = 1
};

/// Struct defined in srv/DetectGrasps in the package gpd_ros_messages.
typedef struct gpd_ros_messages__srv__DetectGrasps_Event
{
  service_msgs__msg__ServiceEventInfo info;
  gpd_ros_messages__srv__DetectGrasps_Request__Sequence request;
  gpd_ros_messages__srv__DetectGrasps_Response__Sequence response;
} gpd_ros_messages__srv__DetectGrasps_Event;

// Struct for a sequence of gpd_ros_messages__srv__DetectGrasps_Event.
typedef struct gpd_ros_messages__srv__DetectGrasps_Event__Sequence
{
  gpd_ros_messages__srv__DetectGrasps_Event * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} gpd_ros_messages__srv__DetectGrasps_Event__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__STRUCT_H_
