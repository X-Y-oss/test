// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from gpd_ros_messages:srv/DetectGrasps.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "gpd_ros_messages/srv/detect_grasps.hpp"


#ifndef GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__BUILDER_HPP_
#define GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "gpd_ros_messages/srv/detail/detect_grasps__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace gpd_ros_messages
{

namespace srv
{

namespace builder
{

class Init_DetectGrasps_Request_cloud_indexed
{
public:
  Init_DetectGrasps_Request_cloud_indexed()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::gpd_ros_messages::srv::DetectGrasps_Request cloud_indexed(::gpd_ros_messages::srv::DetectGrasps_Request::_cloud_indexed_type arg)
  {
    msg_.cloud_indexed = std::move(arg);
    return std::move(msg_);
  }

private:
  ::gpd_ros_messages::srv::DetectGrasps_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::gpd_ros_messages::srv::DetectGrasps_Request>()
{
  return gpd_ros_messages::srv::builder::Init_DetectGrasps_Request_cloud_indexed();
}

}  // namespace gpd_ros_messages


namespace gpd_ros_messages
{

namespace srv
{

namespace builder
{

class Init_DetectGrasps_Response_grasp_configs
{
public:
  Init_DetectGrasps_Response_grasp_configs()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::gpd_ros_messages::srv::DetectGrasps_Response grasp_configs(::gpd_ros_messages::srv::DetectGrasps_Response::_grasp_configs_type arg)
  {
    msg_.grasp_configs = std::move(arg);
    return std::move(msg_);
  }

private:
  ::gpd_ros_messages::srv::DetectGrasps_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::gpd_ros_messages::srv::DetectGrasps_Response>()
{
  return gpd_ros_messages::srv::builder::Init_DetectGrasps_Response_grasp_configs();
}

}  // namespace gpd_ros_messages


namespace gpd_ros_messages
{

namespace srv
{

namespace builder
{

class Init_DetectGrasps_Event_response
{
public:
  explicit Init_DetectGrasps_Event_response(::gpd_ros_messages::srv::DetectGrasps_Event & msg)
  : msg_(msg)
  {}
  ::gpd_ros_messages::srv::DetectGrasps_Event response(::gpd_ros_messages::srv::DetectGrasps_Event::_response_type arg)
  {
    msg_.response = std::move(arg);
    return std::move(msg_);
  }

private:
  ::gpd_ros_messages::srv::DetectGrasps_Event msg_;
};

class Init_DetectGrasps_Event_request
{
public:
  explicit Init_DetectGrasps_Event_request(::gpd_ros_messages::srv::DetectGrasps_Event & msg)
  : msg_(msg)
  {}
  Init_DetectGrasps_Event_response request(::gpd_ros_messages::srv::DetectGrasps_Event::_request_type arg)
  {
    msg_.request = std::move(arg);
    return Init_DetectGrasps_Event_response(msg_);
  }

private:
  ::gpd_ros_messages::srv::DetectGrasps_Event msg_;
};

class Init_DetectGrasps_Event_info
{
public:
  Init_DetectGrasps_Event_info()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_DetectGrasps_Event_request info(::gpd_ros_messages::srv::DetectGrasps_Event::_info_type arg)
  {
    msg_.info = std::move(arg);
    return Init_DetectGrasps_Event_request(msg_);
  }

private:
  ::gpd_ros_messages::srv::DetectGrasps_Event msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::gpd_ros_messages::srv::DetectGrasps_Event>()
{
  return gpd_ros_messages::srv::builder::Init_DetectGrasps_Event_info();
}

}  // namespace gpd_ros_messages

#endif  // GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__BUILDER_HPP_
