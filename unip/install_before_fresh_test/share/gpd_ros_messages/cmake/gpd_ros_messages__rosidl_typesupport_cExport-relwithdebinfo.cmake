#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "gpd_ros_messages::gpd_ros_messages__rosidl_typesupport_c" for configuration "RelWithDebInfo"
set_property(TARGET gpd_ros_messages::gpd_ros_messages__rosidl_typesupport_c APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(gpd_ros_messages::gpd_ros_messages__rosidl_typesupport_c PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELWITHDEBINFO "rosidl_runtime_c::rosidl_runtime_c;rosidl_typesupport_c::rosidl_typesupport_c"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libgpd_ros_messages__rosidl_typesupport_c.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libgpd_ros_messages__rosidl_typesupport_c.so"
  )

list(APPEND _cmake_import_check_targets gpd_ros_messages::gpd_ros_messages__rosidl_typesupport_c )
list(APPEND _cmake_import_check_files_for_gpd_ros_messages::gpd_ros_messages__rosidl_typesupport_c "${_IMPORT_PREFIX}/lib/libgpd_ros_messages__rosidl_typesupport_c.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
