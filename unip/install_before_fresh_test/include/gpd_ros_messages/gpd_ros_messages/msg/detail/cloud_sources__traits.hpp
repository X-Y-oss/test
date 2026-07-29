// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from gpd_ros_messages:msg/CloudSources.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "gpd_ros_messages/msg/cloud_sources.hpp"


#ifndef GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SOURCES__TRAITS_HPP_
#define GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SOURCES__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "gpd_ros_messages/msg/detail/cloud_sources__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'cloud'
#include "sensor_msgs/msg/detail/point_cloud2__traits.hpp"
// Member 'camera_source'
#include "std_msgs/msg/detail/int64__traits.hpp"
// Member 'view_points'
#include "geometry_msgs/msg/detail/point__traits.hpp"

namespace gpd_ros_messages
{

namespace msg
{

inline void to_flow_style_yaml(
  const CloudSources & msg,
  std::ostream & out)
{
  out << "{";
  // member: cloud
  {
    out << "cloud: ";
    to_flow_style_yaml(msg.cloud, out);
    out << ", ";
  }

  // member: camera_source
  {
    if (msg.camera_source.size() == 0) {
      out << "camera_source: []";
    } else {
      out << "camera_source: [";
      size_t pending_items = msg.camera_source.size();
      for (auto item : msg.camera_source) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: view_points
  {
    if (msg.view_points.size() == 0) {
      out << "view_points: []";
    } else {
      out << "view_points: [";
      size_t pending_items = msg.view_points.size();
      for (auto item : msg.view_points) {
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
  const CloudSources & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: cloud
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cloud:\n";
    to_block_style_yaml(msg.cloud, out, indentation + 2);
  }

  // member: camera_source
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.camera_source.size() == 0) {
      out << "camera_source: []\n";
    } else {
      out << "camera_source:\n";
      for (auto item : msg.camera_source) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: view_points
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.view_points.size() == 0) {
      out << "view_points: []\n";
    } else {
      out << "view_points:\n";
      for (auto item : msg.view_points) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const CloudSources & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace gpd_ros_messages

namespace rosidl_generator_traits
{

[[deprecated("use gpd_ros_messages::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const gpd_ros_messages::msg::CloudSources & msg,
  std::ostream & out, size_t indentation = 0)
{
  gpd_ros_messages::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use gpd_ros_messages::msg::to_yaml() instead")]]
inline std::string to_yaml(const gpd_ros_messages::msg::CloudSources & msg)
{
  return gpd_ros_messages::msg::to_yaml(msg);
}

template<>
inline const char * data_type<gpd_ros_messages::msg::CloudSources>()
{
  return "gpd_ros_messages::msg::CloudSources";
}

template<>
inline const char * name<gpd_ros_messages::msg::CloudSources>()
{
  return "gpd_ros_messages/msg/CloudSources";
}

template<>
struct has_fixed_size<gpd_ros_messages::msg::CloudSources>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<gpd_ros_messages::msg::CloudSources>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<gpd_ros_messages::msg::CloudSources>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // GPD_ROS_MESSAGES__MSG__DETAIL__CLOUD_SOURCES__TRAITS_HPP_
