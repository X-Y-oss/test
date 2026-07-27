# UniP ROS dependency manifest audit

## Core findings

### placeability_scoring/package.xml
The active manifest only declared `gpd_ros` and `gpd_ros_messages`, although the
Python package imports a much larger ROS surface.

Add as runtime dependencies:
- rclpy
- tf2_ros
- sensor_msgs
- sensor_msgs_py
- std_msgs
- geometry_msgs
- builtin_interfaces
- cv_bridge
- control_msgs
- trajectory_msgs
- moveit_msgs
- gpd_ros
- gpd_ros_messages

Keep the package as `ament_python`.

### gpd_ros/package.xml
The active CMakeLists.txt uses `visualization_msgs` and `pcl_conversions`, but
the manifest did not declare them. Add both.

The manifest also declared rosidl generators/runtime even though this package
does not generate interfaces in the active CMakeLists.txt. Those entries can be
removed; interfaces live in `gpd_ros_messages`.

### gpd_ros_messages/package.xml
The active interface definitions depend on std_msgs, sensor_msgs and
geometry_msgs. The existing manifest is sufficient for the current build,
although several rclcpp/tf2 dependencies appear broader than necessary.

### generate_motion_msgs/package.xml
The active message contains no external message-field dependencies in the
provided CMake snippet. Existing rosidl build/runtime declarations are
sufficient.

### steve_config_moveit2
This package intentionally pulls in the full MoveIt configuration/runtime stack.
It is not part of the verified CuRobo core path. Keep it in the workspace, but
do not treat it as a core dependency gate until baseline recovery proves it is
needed.

### steve_description
Historical robot-description package; not a core environment gate.

## Installation policy
`rosdep install --from-paths /workspace/src --ignore-src` should be the single
owner for declared ROS package dependencies. Native GPD remains owned by
`install_gpd.sh`; Torch/CUDA/cuRobo remain compatibility-controlled.
