// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from gpd_ros_messages:srv/DetectGrasps.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "gpd_ros_messages/srv/detect_grasps.hpp"


#ifndef GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__TRAITS_HPP_
#define GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "gpd_ros_messages/srv/detail/detect_grasps__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'cloud_indexed'
#include "gpd_ros_messages/msg/detail/cloud_indexed__traits.hpp"

namespace gpd_ros_messages
{

namespace srv
{

inline void to_flow_style_yaml(
  const DetectGrasps_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: cloud_indexed
  {
    out << "cloud_indexed: ";
    to_flow_style_yaml(msg.cloud_indexed, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DetectGrasps_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: cloud_indexed
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cloud_indexed:\n";
    to_block_style_yaml(msg.cloud_indexed, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DetectGrasps_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace gpd_ros_messages

namespace rosidl_generator_traits
{

[[deprecated("use gpd_ros_messages::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const gpd_ros_messages::srv::DetectGrasps_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  gpd_ros_messages::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use gpd_ros_messages::srv::to_yaml() instead")]]
inline std::string to_yaml(const gpd_ros_messages::srv::DetectGrasps_Request & msg)
{
  return gpd_ros_messages::srv::to_yaml(msg);
}

template<>
inline const char * data_type<gpd_ros_messages::srv::DetectGrasps_Request>()
{
  return "gpd_ros_messages::srv::DetectGrasps_Request";
}

template<>
inline const char * name<gpd_ros_messages::srv::DetectGrasps_Request>()
{
  return "gpd_ros_messages/srv/DetectGrasps_Request";
}

template<>
struct has_fixed_size<gpd_ros_messages::srv::DetectGrasps_Request>
  : std::integral_constant<bool, has_fixed_size<gpd_ros_messages::msg::CloudIndexed>::value> {};

template<>
struct has_bounded_size<gpd_ros_messages::srv::DetectGrasps_Request>
  : std::integral_constant<bool, has_bounded_size<gpd_ros_messages::msg::CloudIndexed>::value> {};

template<>
struct is_message<gpd_ros_messages::srv::DetectGrasps_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'grasp_configs'
#include "gpd_ros_messages/msg/detail/grasp_config_list__traits.hpp"

namespace gpd_ros_messages
{

namespace srv
{

inline void to_flow_style_yaml(
  const DetectGrasps_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: grasp_configs
  {
    out << "grasp_configs: ";
    to_flow_style_yaml(msg.grasp_configs, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DetectGrasps_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: grasp_configs
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "grasp_configs:\n";
    to_block_style_yaml(msg.grasp_configs, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DetectGrasps_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace gpd_ros_messages

namespace rosidl_generator_traits
{

[[deprecated("use gpd_ros_messages::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const gpd_ros_messages::srv::DetectGrasps_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  gpd_ros_messages::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use gpd_ros_messages::srv::to_yaml() instead")]]
inline std::string to_yaml(const gpd_ros_messages::srv::DetectGrasps_Response & msg)
{
  return gpd_ros_messages::srv::to_yaml(msg);
}

template<>
inline const char * data_type<gpd_ros_messages::srv::DetectGrasps_Response>()
{
  return "gpd_ros_messages::srv::DetectGrasps_Response";
}

template<>
inline const char * name<gpd_ros_messages::srv::DetectGrasps_Response>()
{
  return "gpd_ros_messages/srv/DetectGrasps_Response";
}

template<>
struct has_fixed_size<gpd_ros_messages::srv::DetectGrasps_Response>
  : std::integral_constant<bool, has_fixed_size<gpd_ros_messages::msg::GraspConfigList>::value> {};

template<>
struct has_bounded_size<gpd_ros_messages::srv::DetectGrasps_Response>
  : std::integral_constant<bool, has_bounded_size<gpd_ros_messages::msg::GraspConfigList>::value> {};

template<>
struct is_message<gpd_ros_messages::srv::DetectGrasps_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

// Include directives for member types
// Member 'info'
#include "service_msgs/msg/detail/service_event_info__traits.hpp"

namespace gpd_ros_messages
{

namespace srv
{

inline void to_flow_style_yaml(
  const DetectGrasps_Event & msg,
  std::ostream & out)
{
  out << "{";
  // member: info
  {
    out << "info: ";
    to_flow_style_yaml(msg.info, out);
    out << ", ";
  }

  // member: request
  {
    if (msg.request.size() == 0) {
      out << "request: []";
    } else {
      out << "request: [";
      size_t pending_items = msg.request.size();
      for (auto item : msg.request) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: response
  {
    if (msg.response.size() == 0) {
      out << "response: []";
    } else {
      out << "response: [";
      size_t pending_items = msg.response.size();
      for (auto item : msg.response) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const DetectGrasps_Event & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: info
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "info:\n";
    to_block_style_yaml(msg.info, out, indentation + 2);
  }

  // member: request
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.request.size() == 0) {
      out << "request: []\n";
    } else {
      out << "request:\n";
      for (auto item : msg.request) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: response
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.response.size() == 0) {
      out << "response: []\n";
    } else {
      out << "response:\n";
      for (auto item : msg.response) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const DetectGrasps_Event & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace gpd_ros_messages

namespace rosidl_generator_traits
{

[[deprecated("use gpd_ros_messages::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const gpd_ros_messages::srv::DetectGrasps_Event & msg,
  std::ostream & out, size_t indentation = 0)
{
  gpd_ros_messages::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use gpd_ros_messages::srv::to_yaml() instead")]]
inline std::string to_yaml(const gpd_ros_messages::srv::DetectGrasps_Event & msg)
{
  return gpd_ros_messages::srv::to_yaml(msg);
}

template<>
inline const char * data_type<gpd_ros_messages::srv::DetectGrasps_Event>()
{
  return "gpd_ros_messages::srv::DetectGrasps_Event";
}

template<>
inline const char * name<gpd_ros_messages::srv::DetectGrasps_Event>()
{
  return "gpd_ros_messages/srv/DetectGrasps_Event";
}

template<>
struct has_fixed_size<gpd_ros_messages::srv::DetectGrasps_Event>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<gpd_ros_messages::srv::DetectGrasps_Event>
  : std::integral_constant<bool, has_bounded_size<gpd_ros_messages::srv::DetectGrasps_Request>::value && has_bounded_size<gpd_ros_messages::srv::DetectGrasps_Response>::value && has_bounded_size<service_msgs::msg::ServiceEventInfo>::value> {};

template<>
struct is_message<gpd_ros_messages::srv::DetectGrasps_Event>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<gpd_ros_messages::srv::DetectGrasps>()
{
  return "gpd_ros_messages::srv::DetectGrasps";
}

template<>
inline const char * name<gpd_ros_messages::srv::DetectGrasps>()
{
  return "gpd_ros_messages/srv/DetectGrasps";
}

template<>
struct has_fixed_size<gpd_ros_messages::srv::DetectGrasps>
  : std::integral_constant<
    bool,
    has_fixed_size<gpd_ros_messages::srv::DetectGrasps_Request>::value &&
    has_fixed_size<gpd_ros_messages::srv::DetectGrasps_Response>::value
  >
{
};

template<>
struct has_bounded_size<gpd_ros_messages::srv::DetectGrasps>
  : std::integral_constant<
    bool,
    has_bounded_size<gpd_ros_messages::srv::DetectGrasps_Request>::value &&
    has_bounded_size<gpd_ros_messages::srv::DetectGrasps_Response>::value
  >
{
};

template<>
struct is_service<gpd_ros_messages::srv::DetectGrasps>
  : std::true_type
{
};

template<>
struct is_service_request<gpd_ros_messages::srv::DetectGrasps_Request>
  : std::true_type
{
};

template<>
struct is_service_response<gpd_ros_messages::srv::DetectGrasps_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__TRAITS_HPP_
