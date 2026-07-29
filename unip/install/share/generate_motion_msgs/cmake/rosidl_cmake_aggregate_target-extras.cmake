# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target generate_motion_msgs::generate_motion_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${generate_motion_msgs_TARGETS}.
if(generate_motion_msgs_TARGETS AND NOT TARGET generate_motion_msgs::generate_motion_msgs)
  add_library(generate_motion_msgs::generate_motion_msgs INTERFACE IMPORTED)
  set_target_properties(generate_motion_msgs::generate_motion_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${generate_motion_msgs_TARGETS}")
endif()
