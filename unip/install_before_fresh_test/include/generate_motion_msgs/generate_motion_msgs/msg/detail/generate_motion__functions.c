// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from generate_motion_msgs:msg/GenerateMotion.idl
// generated code does not contain a copyright notice
#include "generate_motion_msgs/msg/detail/generate_motion__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `robot_file`
#include "rosidl_runtime_c/string_functions.h"
// Member `pose_lists`
// Member `segment_modes`
// Member `linear_axes`
// Member `attach_after_index`
// Member `detach_after_index`
// Member `cylinder_pose`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
generate_motion_msgs__msg__GenerateMotion__init(generate_motion_msgs__msg__GenerateMotion * msg)
{
  if (!msg) {
    return false;
  }
  // robot_file
  if (!rosidl_runtime_c__String__init(&msg->robot_file)) {
    generate_motion_msgs__msg__GenerateMotion__fini(msg);
    return false;
  }
  // pose_lists
  if (!rosidl_runtime_c__double__Sequence__init(&msg->pose_lists, 0)) {
    generate_motion_msgs__msg__GenerateMotion__fini(msg);
    return false;
  }
  // segment_modes
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->segment_modes, 0)) {
    generate_motion_msgs__msg__GenerateMotion__fini(msg);
    return false;
  }
  // linear_axes
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->linear_axes, 0)) {
    generate_motion_msgs__msg__GenerateMotion__fini(msg);
    return false;
  }
  // attach_cylinder
  // attach_after_index
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->attach_after_index, 0)) {
    generate_motion_msgs__msg__GenerateMotion__fini(msg);
    return false;
  }
  // detach_after_index
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->detach_after_index, 0)) {
    generate_motion_msgs__msg__GenerateMotion__fini(msg);
    return false;
  }
  // cylinder_radius
  // cylinder_height
  // cylinder_pose
  if (!rosidl_runtime_c__double__Sequence__init(&msg->cylinder_pose, 0)) {
    generate_motion_msgs__msg__GenerateMotion__fini(msg);
    return false;
  }
  // grasp_prepose_motion
  return true;
}

void
generate_motion_msgs__msg__GenerateMotion__fini(generate_motion_msgs__msg__GenerateMotion * msg)
{
  if (!msg) {
    return;
  }
  // robot_file
  rosidl_runtime_c__String__fini(&msg->robot_file);
  // pose_lists
  rosidl_runtime_c__double__Sequence__fini(&msg->pose_lists);
  // segment_modes
  rosidl_runtime_c__int32__Sequence__fini(&msg->segment_modes);
  // linear_axes
  rosidl_runtime_c__int32__Sequence__fini(&msg->linear_axes);
  // attach_cylinder
  // attach_after_index
  rosidl_runtime_c__int32__Sequence__fini(&msg->attach_after_index);
  // detach_after_index
  rosidl_runtime_c__int32__Sequence__fini(&msg->detach_after_index);
  // cylinder_radius
  // cylinder_height
  // cylinder_pose
  rosidl_runtime_c__double__Sequence__fini(&msg->cylinder_pose);
  // grasp_prepose_motion
}

bool
generate_motion_msgs__msg__GenerateMotion__are_equal(const generate_motion_msgs__msg__GenerateMotion * lhs, const generate_motion_msgs__msg__GenerateMotion * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // robot_file
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->robot_file), &(rhs->robot_file)))
  {
    return false;
  }
  // pose_lists
  if (!rosidl_runtime_c__double__Sequence__are_equal(
      &(lhs->pose_lists), &(rhs->pose_lists)))
  {
    return false;
  }
  // segment_modes
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->segment_modes), &(rhs->segment_modes)))
  {
    return false;
  }
  // linear_axes
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->linear_axes), &(rhs->linear_axes)))
  {
    return false;
  }
  // attach_cylinder
  if (lhs->attach_cylinder != rhs->attach_cylinder) {
    return false;
  }
  // attach_after_index
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->attach_after_index), &(rhs->attach_after_index)))
  {
    return false;
  }
  // detach_after_index
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->detach_after_index), &(rhs->detach_after_index)))
  {
    return false;
  }
  // cylinder_radius
  if (lhs->cylinder_radius != rhs->cylinder_radius) {
    return false;
  }
  // cylinder_height
  if (lhs->cylinder_height != rhs->cylinder_height) {
    return false;
  }
  // cylinder_pose
  if (!rosidl_runtime_c__double__Sequence__are_equal(
      &(lhs->cylinder_pose), &(rhs->cylinder_pose)))
  {
    return false;
  }
  // grasp_prepose_motion
  if (lhs->grasp_prepose_motion != rhs->grasp_prepose_motion) {
    return false;
  }
  return true;
}

bool
generate_motion_msgs__msg__GenerateMotion__copy(
  const generate_motion_msgs__msg__GenerateMotion * input,
  generate_motion_msgs__msg__GenerateMotion * output)
{
  if (!input || !output) {
    return false;
  }
  // robot_file
  if (!rosidl_runtime_c__String__copy(
      &(input->robot_file), &(output->robot_file)))
  {
    return false;
  }
  // pose_lists
  if (!rosidl_runtime_c__double__Sequence__copy(
      &(input->pose_lists), &(output->pose_lists)))
  {
    return false;
  }
  // segment_modes
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->segment_modes), &(output->segment_modes)))
  {
    return false;
  }
  // linear_axes
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->linear_axes), &(output->linear_axes)))
  {
    return false;
  }
  // attach_cylinder
  output->attach_cylinder = input->attach_cylinder;
  // attach_after_index
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->attach_after_index), &(output->attach_after_index)))
  {
    return false;
  }
  // detach_after_index
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->detach_after_index), &(output->detach_after_index)))
  {
    return false;
  }
  // cylinder_radius
  output->cylinder_radius = input->cylinder_radius;
  // cylinder_height
  output->cylinder_height = input->cylinder_height;
  // cylinder_pose
  if (!rosidl_runtime_c__double__Sequence__copy(
      &(input->cylinder_pose), &(output->cylinder_pose)))
  {
    return false;
  }
  // grasp_prepose_motion
  output->grasp_prepose_motion = input->grasp_prepose_motion;
  return true;
}

generate_motion_msgs__msg__GenerateMotion *
generate_motion_msgs__msg__GenerateMotion__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  generate_motion_msgs__msg__GenerateMotion * msg = (generate_motion_msgs__msg__GenerateMotion *)allocator.allocate(sizeof(generate_motion_msgs__msg__GenerateMotion), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(generate_motion_msgs__msg__GenerateMotion));
  bool success = generate_motion_msgs__msg__GenerateMotion__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
generate_motion_msgs__msg__GenerateMotion__destroy(generate_motion_msgs__msg__GenerateMotion * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    generate_motion_msgs__msg__GenerateMotion__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
generate_motion_msgs__msg__GenerateMotion__Sequence__init(generate_motion_msgs__msg__GenerateMotion__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  generate_motion_msgs__msg__GenerateMotion * data = NULL;

  if (size) {
    if (size > SIZE_MAX / sizeof(generate_motion_msgs__msg__GenerateMotion)) {
      return false;
    }
    data = (generate_motion_msgs__msg__GenerateMotion *)allocator.zero_allocate(size, sizeof(generate_motion_msgs__msg__GenerateMotion), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = generate_motion_msgs__msg__GenerateMotion__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        generate_motion_msgs__msg__GenerateMotion__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
generate_motion_msgs__msg__GenerateMotion__Sequence__fini(generate_motion_msgs__msg__GenerateMotion__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      generate_motion_msgs__msg__GenerateMotion__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

generate_motion_msgs__msg__GenerateMotion__Sequence *
generate_motion_msgs__msg__GenerateMotion__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  generate_motion_msgs__msg__GenerateMotion__Sequence * array = (generate_motion_msgs__msg__GenerateMotion__Sequence *)allocator.allocate(sizeof(generate_motion_msgs__msg__GenerateMotion__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = generate_motion_msgs__msg__GenerateMotion__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
generate_motion_msgs__msg__GenerateMotion__Sequence__destroy(generate_motion_msgs__msg__GenerateMotion__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    generate_motion_msgs__msg__GenerateMotion__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
generate_motion_msgs__msg__GenerateMotion__Sequence__are_equal(const generate_motion_msgs__msg__GenerateMotion__Sequence * lhs, const generate_motion_msgs__msg__GenerateMotion__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!generate_motion_msgs__msg__GenerateMotion__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
generate_motion_msgs__msg__GenerateMotion__Sequence__copy(
  const generate_motion_msgs__msg__GenerateMotion__Sequence * input,
  generate_motion_msgs__msg__GenerateMotion__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    if (input->size > SIZE_MAX / sizeof(generate_motion_msgs__msg__GenerateMotion)) {
      return false;
    }
    const size_t allocation_size =
      input->size * sizeof(generate_motion_msgs__msg__GenerateMotion);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    generate_motion_msgs__msg__GenerateMotion * data =
      (generate_motion_msgs__msg__GenerateMotion *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!generate_motion_msgs__msg__GenerateMotion__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          generate_motion_msgs__msg__GenerateMotion__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!generate_motion_msgs__msg__GenerateMotion__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
