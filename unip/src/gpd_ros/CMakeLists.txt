cmake_minimum_required(VERSION 3.8)
project(gpd_ros)

set(CMAKE_CXX_STANDARD 20)
add_compile_options(-std=c++20)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)


if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

## Find ament packages and system dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(rclcpp REQUIRED)  # C++ client library
find_package(rclcpp_action REQUIRED)
find_package(tf2_eigen REQUIRED) # Equivalent of eigen_conversions
find_package(tf2_geometry_msgs REQUIRED)

# PCL
find_package(PCL 1.9 REQUIRED)
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})
find_package(pcl_conversions)

# OpenCV
find_package(OpenCV REQUIRED)

# Messages from gpd_ros_messages
find_package(gpd_ros_messages REQUIRED)

# Eigen
find_package(Eigen3 REQUIRED)

# find_package(gpd REQUIRED)  # Add this line for gpd


# Locate the GPD library
find_library(GPD_LIB NAMES gpd PATHS /usr/local/lib PATH_SUFFIXES lib NO_DEFAULT_PATH)
if (GPD_LIB)
  message(STATUS "Library GPD found in ${GPD_LIB}")
else()
  message(FATAL_ERROR "Library GPD not found")
endif()

# Include the GPD include directory
include_directories(${GPD_LIB_INCLUDE_DIR})
message(STATUS "gpd_include_dir: ${GPD_LIB_INCLUDE_DIR}")

set(CMAKE_CXX_FLAGS "-O3 -fopenmp -fPIC -Wno-deprecated -Wenum-compare -Wno-ignored-attributes -std=c++14")


# --------------------------

# Create a library for your messages
add_library(${PROJECT_NAME}_grasp_messages SHARED
  src/${PROJECT_NAME}/grasp_messages.cpp
)

add_executable(detect_grasps src/gpd_ros/grasp_detection_node.cpp)

# Link dependencies using ament_target_dependencies
ament_target_dependencies(${PROJECT_NAME}_grasp_messages
  rclcpp
  gpd_ros_messages
  PCL
  tf2_eigen
  tf2_geometry_msgs
  OpenCV
  Eigen3
)
ament_target_dependencies(detect_grasps
    rclcpp
    gpd_ros_messages
    PCL
    tf2_eigen
    tf2_geometry_msgs
    OpenCV
    Eigen3
    visualization_msgs
    pcl_conversions
)



# If GPD_LIB is a C++ library, link it using target_link_libraries
target_link_libraries(${PROJECT_NAME}_grasp_messages
  ${GPD_LIB}  # Link the GPD library here
)
target_link_libraries(detect_grasps
    ${PROJECT_NAME}_grasp_messages
    # grasp_plotter
    ${GPD_LIB}
    ${PCL_LIBRARIES}
)

target_include_directories(${PROJECT_NAME}_grasp_messages
  PRIVATE
  include  # Add this line to include your header files
)
target_include_directories(detect_grasps
  PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include  # Add this line to include your header files
)

# Install the library
install(
  TARGETS ${PROJECT_NAME}_grasp_messages detect_grasps
  DESTINATION lib/${PROJECT_NAME}
)
# install launch
install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# ament package
ament_export_dependencies(rclcpp gpd_ros_messages)
install(
  TARGETS ${PROJECT_NAME}_grasp_messages detect_grasps
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)


ament_export_libraries(${PROJECT_NAME}_grasp_messages)
ament_package()


# ament_export_dependencies(rosidl_default_runtime)

# # Include directories for your project
# include_directories(
#   include
#   ${CMAKE_CURRENT_BINARY_DIR}/rosidl_generator_cpp
# )

# # Define libraries
# add_library(${PROJECT_NAME}_grasp_messages src/${PROJECT_NAME}/grasp_messages.cpp)

# include_directories(
#   ${CMAKE_CURRENT_SOURCE_DIR}/include
#   ${CMAKE_CURRENT_BINARY_DIR}/include
#   ${ament_INCLUDE_DIRS} # This ensures generated files from ROS 2 are included
# )

# # link the necessary libraries
# ament_target_dependencies(${PROJECT_NAME}_grasp_messages
#   rclcpp
#   std_msgs
#   geometry_msgs
#   sensor_msgs
#   PCL
#   tf2_eigen
#   rosidl_default_runtime
# )

# # Installation steps
# install(
#   DIRECTORY include/${PROJECT_NAME}/
#   DESTINATION include/${PROJECT_NAME}
# )

# install(
#   TARGETS ${PROJECT_NAME}_grasp_messages
#   DESTINATION lib/${PROJECT_NAME}
# )

# install(
#   DIRECTORY msg/
#   DESTINATION share/${PROJECT_NAME}
# )

# # Add executable for grasp detection node
# add_executable(${PROJECT_NAME}_detect_grasps src/gpd_ros/grasp_detection_node.cpp)

# # Set target properties for the executable
# set_target_properties(${PROJECT_NAME}_detect_grasps PROPERTIES OUTPUT_NAME detect_grasps PREFIX "")

# # Link the grasp messages library to the grasp detection node
# ament_target_dependencies(${PROJECT_NAME}_detect_grasps
#   rclcpp
#   std_msgs
#   geometry_msgs
#   sensor_msgs
#   PCL
#   OpenCV
#   tf2_eigen
# )
# # Link the grasp messages library to the grasp detection node
# target_link_libraries(${PROJECT_NAME}_detect_grasps
#                       ${PROJECT_NAME}_grasp_messages
#                       ${GPD_LIB}
#                       ${PCL_LIBRARIES}
#                       ${catkin_LIBRARIES})

# target_link_libraries(${PROJECT_NAME}_grasp_messages
#                       ${GPD_LIB}
#                       ${PCL_LIBRARIES})
