// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from generate_motion_msgs:msg/GenerateMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "generate_motion_msgs/msg/generate_motion.hpp"


#ifndef GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__TRAITS_HPP_
#define GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "generate_motion_msgs/msg/detail/generate_motion__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace generate_motion_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const GenerateMotion & msg,
  std::ostream & out)
{
  out << "{";
  // member: robot_file
  {
    out << "robot_file: ";
    rosidl_generator_traits::value_to_yaml(msg.robot_file, out);
    out << ", ";
  }

  // member: pose_lists
  {
    if (msg.pose_lists.size() == 0) {
      out << "pose_lists: []";
    } else {
      out << "pose_lists: [";
      size_t pending_items = msg.pose_lists.size();
      for (auto item : msg.pose_lists) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: segment_modes
  {
    if (msg.segment_modes.size() == 0) {
      out << "segment_modes: []";
    } else {
      out << "segment_modes: [";
      size_t pending_items = msg.segment_modes.size();
      for (auto item : msg.segment_modes) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: linear_axes
  {
    if (msg.linear_axes.size() == 0) {
      out << "linear_axes: []";
    } else {
      out << "linear_axes: [";
      size_t pending_items = msg.linear_axes.size();
      for (auto item : msg.linear_axes) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: attach_cylinder
  {
    out << "attach_cylinder: ";
    rosidl_generator_traits::value_to_yaml(msg.attach_cylinder, out);
    out << ", ";
  }

  // member: attach_after_index
  {
    if (msg.attach_after_index.size() == 0) {
      out << "attach_after_index: []";
    } else {
      out << "attach_after_index: [";
      size_t pending_items = msg.attach_after_index.size();
      for (auto item : msg.attach_after_index) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: detach_after_index
  {
    if (msg.detach_after_index.size() == 0) {
      out << "detach_after_index: []";
    } else {
      out << "detach_after_index: [";
      size_t pending_items = msg.detach_after_index.size();
      for (auto item : msg.detach_after_index) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: cylinder_radius
  {
    out << "cylinder_radius: ";
    rosidl_generator_traits::value_to_yaml(msg.cylinder_radius, out);
    out << ", ";
  }

  // member: cylinder_height
  {
    out << "cylinder_height: ";
    rosidl_generator_traits::value_to_yaml(msg.cylinder_height, out);
    out << ", ";
  }

  // member: cylinder_pose
  {
    if (msg.cylinder_pose.size() == 0) {
      out << "cylinder_pose: []";
    } else {
      out << "cylinder_pose: [";
      size_t pending_items = msg.cylinder_pose.size();
      for (auto item : msg.cylinder_pose) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: grasp_prepose_motion
  {
    out << "grasp_prepose_motion: ";
    rosidl_generator_traits::value_to_yaml(msg.grasp_prepose_motion, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const GenerateMotion & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: robot_file
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "robot_file: ";
    rosidl_generator_traits::value_to_yaml(msg.robot_file, out);
    out << "\n";
  }

  // member: pose_lists
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.pose_lists.size() == 0) {
      out << "pose_lists: []\n";
    } else {
      out << "pose_lists:\n";
      for (auto item : msg.pose_lists) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: segment_modes
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.segment_modes.size() == 0) {
      out << "segment_modes: []\n";
    } else {
      out << "segment_modes:\n";
      for (auto item : msg.segment_modes) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: linear_axes
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.linear_axes.size() == 0) {
      out << "linear_axes: []\n";
    } else {
      out << "linear_axes:\n";
      for (auto item : msg.linear_axes) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: attach_cylinder
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "attach_cylinder: ";
    rosidl_generator_traits::value_to_yaml(msg.attach_cylinder, out);
    out << "\n";
  }

  // member: attach_after_index
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.attach_after_index.size() == 0) {
      out << "attach_after_index: []\n";
    } else {
      out << "attach_after_index:\n";
      for (auto item : msg.attach_after_index) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: detach_after_index
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.detach_after_index.size() == 0) {
      out << "detach_after_index: []\n";
    } else {
      out << "detach_after_index:\n";
      for (auto item : msg.detach_after_index) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: cylinder_radius
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cylinder_radius: ";
    rosidl_generator_traits::value_to_yaml(msg.cylinder_radius, out);
    out << "\n";
  }

  // member: cylinder_height
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "cylinder_height: ";
    rosidl_generator_traits::value_to_yaml(msg.cylinder_height, out);
    out << "\n";
  }

  // member: cylinder_pose
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.cylinder_pose.size() == 0) {
      out << "cylinder_pose: []\n";
    } else {
      out << "cylinder_pose:\n";
      for (auto item : msg.cylinder_pose) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }

  // member: grasp_prepose_motion
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "grasp_prepose_motion: ";
    rosidl_generator_traits::value_to_yaml(msg.grasp_prepose_motion, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const GenerateMotion & msg, bool use_flow_style = false)
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

}  // namespace generate_motion_msgs

namespace rosidl_generator_traits
{

[[deprecated("use generate_motion_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const generate_motion_msgs::msg::GenerateMotion & msg,
  std::ostream & out, size_t indentation = 0)
{
  generate_motion_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use generate_motion_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const generate_motion_msgs::msg::GenerateMotion & msg)
{
  return generate_motion_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<generate_motion_msgs::msg::GenerateMotion>()
{
  return "generate_motion_msgs::msg::GenerateMotion";
}

template<>
inline const char * name<generate_motion_msgs::msg::GenerateMotion>()
{
  return "generate_motion_msgs/msg/GenerateMotion";
}

template<>
struct has_fixed_size<generate_motion_msgs::msg::GenerateMotion>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<generate_motion_msgs::msg::GenerateMotion>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<generate_motion_msgs::msg::GenerateMotion>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__TRAITS_HPP_
