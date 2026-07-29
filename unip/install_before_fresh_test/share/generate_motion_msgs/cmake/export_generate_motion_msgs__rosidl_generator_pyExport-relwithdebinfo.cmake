#----------------------------------------------------------------
# Generated CMake target import file for configuration "RelWithDebInfo".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "generate_motion_msgs::generate_motion_msgs__rosidl_generator_py" for configuration "RelWithDebInfo"
set_property(TARGET generate_motion_msgs::generate_motion_msgs__rosidl_generator_py APPEND PROPERTY IMPORTED_CONFIGURATIONS RELWITHDEBINFO)
set_target_properties(generate_motion_msgs::generate_motion_msgs__rosidl_generator_py PROPERTIES
  IMPORTED_LINK_DEPENDENT_LIBRARIES_RELWITHDEBINFO "generate_motion_msgs::generate_motion_msgs__rosidl_generator_c;Python3::Python;generate_motion_msgs::generate_motion_msgs__rosidl_typesupport_c"
  IMPORTED_LOCATION_RELWITHDEBINFO "${_IMPORT_PREFIX}/lib/libgenerate_motion_msgs__rosidl_generator_py.so"
  IMPORTED_SONAME_RELWITHDEBINFO "libgenerate_motion_msgs__rosidl_generator_py.so"
  )

list(APPEND _cmake_import_check_targets generate_motion_msgs::generate_motion_msgs__rosidl_generator_py )
list(APPEND _cmake_import_check_files_for_generate_motion_msgs::generate_motion_msgs__rosidl_generator_py "${_IMPORT_PREFIX}/lib/libgenerate_motion_msgs__rosidl_generator_py.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
