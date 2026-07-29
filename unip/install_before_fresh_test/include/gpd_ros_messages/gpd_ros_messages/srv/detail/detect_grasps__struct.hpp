// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from gpd_ros_messages:srv/DetectGrasps.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "gpd_ros_messages/srv/detect_grasps.hpp"


#ifndef GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__STRUCT_HPP_
#define GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'cloud_indexed'
#include "gpd_ros_messages/msg/detail/cloud_indexed__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Request __attribute__((deprecated))
#else
# define DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Request __declspec(deprecated)
#endif

namespace gpd_ros_messages
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct DetectGrasps_Request_
{
  using Type = DetectGrasps_Request_<ContainerAllocator>;

  explicit DetectGrasps_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : cloud_indexed(_init)
  {
    (void)_init;
  }

  explicit DetectGrasps_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : cloud_indexed(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _cloud_indexed_type =
    gpd_ros_messages::msg::CloudIndexed_<ContainerAllocator>;
  _cloud_indexed_type cloud_indexed;

  // setters for named parameter idiom
  Type & set__cloud_indexed(
    const gpd_ros_messages::msg::CloudIndexed_<ContainerAllocator> & _arg)
  {
    this->cloud_indexed = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Request
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Request
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DetectGrasps_Request_ & other) const
  {
    if (this->cloud_indexed != other.cloud_indexed) {
      return false;
    }
    return true;
  }
  bool operator!=(const DetectGrasps_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DetectGrasps_Request_

// alias to use template instance with default allocator
using DetectGrasps_Request =
  gpd_ros_messages::srv::DetectGrasps_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace gpd_ros_messages


// Include directives for member types
// Member 'grasp_configs'
#include "gpd_ros_messages/msg/detail/grasp_config_list__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Response __attribute__((deprecated))
#else
# define DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Response __declspec(deprecated)
#endif

namespace gpd_ros_messages
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct DetectGrasps_Response_
{
  using Type = DetectGrasps_Response_<ContainerAllocator>;

  explicit DetectGrasps_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : grasp_configs(_init)
  {
    (void)_init;
  }

  explicit DetectGrasps_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : grasp_configs(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _grasp_configs_type =
    gpd_ros_messages::msg::GraspConfigList_<ContainerAllocator>;
  _grasp_configs_type grasp_configs;

  // setters for named parameter idiom
  Type & set__grasp_configs(
    const gpd_ros_messages::msg::GraspConfigList_<ContainerAllocator> & _arg)
  {
    this->grasp_configs = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Response
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Response
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DetectGrasps_Response_ & other) const
  {
    if (this->grasp_configs != other.grasp_configs) {
      return false;
    }
    return true;
  }
  bool operator!=(const DetectGrasps_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DetectGrasps_Response_

// alias to use template instance with default allocator
using DetectGrasps_Response =
  gpd_ros_messages::srv::DetectGrasps_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace gpd_ros_messages


// Include directives for member types
// Member 'info'
#include "service_msgs/msg/detail/service_event_info__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Event __attribute__((deprecated))
#else
# define DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Event __declspec(deprecated)
#endif

namespace gpd_ros_messages
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct DetectGrasps_Event_
{
  using Type = DetectGrasps_Event_<ContainerAllocator>;

  explicit DetectGrasps_Event_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : info(_init)
  {
    (void)_init;
  }

  explicit DetectGrasps_Event_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : info(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _info_type =
    service_msgs::msg::ServiceEventInfo_<ContainerAllocator>;
  _info_type info;
  using _request_type =
    rosidl_runtime_cpp::BoundedVector<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>, 1, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>>>;
  _request_type request;
  using _response_type =
    rosidl_runtime_cpp::BoundedVector<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>, 1, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>>>;
  _response_type response;

  // setters for named parameter idiom
  Type & set__info(
    const service_msgs::msg::ServiceEventInfo_<ContainerAllocator> & _arg)
  {
    this->info = _arg;
    return *this;
  }
  Type & set__request(
    const rosidl_runtime_cpp::BoundedVector<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>, 1, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<gpd_ros_messages::srv::DetectGrasps_Request_<ContainerAllocator>>> & _arg)
  {
    this->request = _arg;
    return *this;
  }
  Type & set__response(
    const rosidl_runtime_cpp::BoundedVector<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>, 1, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<gpd_ros_messages::srv::DetectGrasps_Response_<ContainerAllocator>>> & _arg)
  {
    this->response = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator> *;
  using ConstRawPtr =
    const gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Event
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__gpd_ros_messages__srv__DetectGrasps_Event
    std::shared_ptr<gpd_ros_messages::srv::DetectGrasps_Event_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const DetectGrasps_Event_ & other) const
  {
    if (this->info != other.info) {
      return false;
    }
    if (this->request != other.request) {
      return false;
    }
    if (this->response != other.response) {
      return false;
    }
    return true;
  }
  bool operator!=(const DetectGrasps_Event_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct DetectGrasps_Event_

// alias to use template instance with default allocator
using DetectGrasps_Event =
  gpd_ros_messages::srv::DetectGrasps_Event_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace gpd_ros_messages

namespace gpd_ros_messages
{

namespace srv
{

struct DetectGrasps
{
  using Request = gpd_ros_messages::srv::DetectGrasps_Request;
  using Response = gpd_ros_messages::srv::DetectGrasps_Response;
  using Event = gpd_ros_messages::srv::DetectGrasps_Event;
};

}  // namespace srv

}  // namespace gpd_ros_messages

#endif  // GPD_ROS_MESSAGES__SRV__DETAIL__DETECT_GRASPS__STRUCT_HPP_
