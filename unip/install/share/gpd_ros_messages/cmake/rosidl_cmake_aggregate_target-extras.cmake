# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target gpd_ros_messages::gpd_ros_messages
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${gpd_ros_messages_TARGETS}.
if(gpd_ros_messages_TARGETS AND NOT TARGET gpd_ros_messages::gpd_ros_messages)
  add_library(gpd_ros_messages::gpd_ros_messages INTERFACE IMPORTED)
  set_target_properties(gpd_ros_messages::gpd_ros_messages PROPERTIES
    INTERFACE_LINK_LIBRARIES "${gpd_ros_messages_TARGETS}")
endif()
