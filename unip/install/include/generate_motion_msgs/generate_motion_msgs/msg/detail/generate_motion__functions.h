// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from generate_motion_msgs:msg/GenerateMotion.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "generate_motion_msgs/msg/generate_motion.h"


#ifndef GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__FUNCTIONS_H_
#define GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/action_type_support_struct.h"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_runtime_c/service_type_support_struct.h"
#include "rosidl_runtime_c/type_description/type_description__struct.h"
#include "rosidl_runtime_c/type_description/type_source__struct.h"
#include "rosidl_runtime_c/type_hash.h"
#include "rosidl_runtime_c/visibility_control.h"
#include "generate_motion_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "generate_motion_msgs/msg/detail/generate_motion__struct.h"

/// Initialize msg/GenerateMotion message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * generate_motion_msgs__msg__GenerateMotion
 * )) before or use
 * generate_motion_msgs__msg__GenerateMotion__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
bool
generate_motion_msgs__msg__GenerateMotion__init(generate_motion_msgs__msg__GenerateMotion * msg);

/// Finalize msg/GenerateMotion message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
void
generate_motion_msgs__msg__GenerateMotion__fini(generate_motion_msgs__msg__GenerateMotion * msg);

/// Create msg/GenerateMotion message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * generate_motion_msgs__msg__GenerateMotion__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
generate_motion_msgs__msg__GenerateMotion *
generate_motion_msgs__msg__GenerateMotion__create(void);

/// Destroy msg/GenerateMotion message.
/**
 * It calls
 * generate_motion_msgs__msg__GenerateMotion__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
void
generate_motion_msgs__msg__GenerateMotion__destroy(generate_motion_msgs__msg__GenerateMotion * msg);

/// Check for msg/GenerateMotion message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
bool
generate_motion_msgs__msg__GenerateMotion__are_equal(const generate_motion_msgs__msg__GenerateMotion * lhs, const generate_motion_msgs__msg__GenerateMotion * rhs);

/// Copy a msg/GenerateMotion message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
bool
generate_motion_msgs__msg__GenerateMotion__copy(
  const generate_motion_msgs__msg__GenerateMotion * input,
  generate_motion_msgs__msg__GenerateMotion * output);

/// Retrieve pointer to the hash of the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
const rosidl_type_hash_t *
generate_motion_msgs__msg__GenerateMotion__get_type_hash(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
const rosidl_runtime_c__type_description__TypeDescription *
generate_motion_msgs__msg__GenerateMotion__get_type_description(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the single raw source text that defined this type.
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
const rosidl_runtime_c__type_description__TypeSource *
generate_motion_msgs__msg__GenerateMotion__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support);

/// Retrieve pointer to the recursive raw sources that defined the description of this type.
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
const rosidl_runtime_c__type_description__TypeSource__Sequence *
generate_motion_msgs__msg__GenerateMotion__get_type_description_sources(
  const rosidl_message_type_support_t * type_support);

/// Initialize array of msg/GenerateMotion messages.
/**
 * It allocates the memory for the number of elements and calls
 * generate_motion_msgs__msg__GenerateMotion__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
bool
generate_motion_msgs__msg__GenerateMotion__Sequence__init(generate_motion_msgs__msg__GenerateMotion__Sequence * array, size_t size);

/// Finalize array of msg/GenerateMotion messages.
/**
 * It calls
 * generate_motion_msgs__msg__GenerateMotion__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
void
generate_motion_msgs__msg__GenerateMotion__Sequence__fini(generate_motion_msgs__msg__GenerateMotion__Sequence * array);

/// Create array of msg/GenerateMotion messages.
/**
 * It allocates the memory for the array and calls
 * generate_motion_msgs__msg__GenerateMotion__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
generate_motion_msgs__msg__GenerateMotion__Sequence *
generate_motion_msgs__msg__GenerateMotion__Sequence__create(size_t size);

/// Destroy array of msg/GenerateMotion messages.
/**
 * It calls
 * generate_motion_msgs__msg__GenerateMotion__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
void
generate_motion_msgs__msg__GenerateMotion__Sequence__destroy(generate_motion_msgs__msg__GenerateMotion__Sequence * array);

/// Check for msg/GenerateMotion message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
bool
generate_motion_msgs__msg__GenerateMotion__Sequence__are_equal(const generate_motion_msgs__msg__GenerateMotion__Sequence * lhs, const generate_motion_msgs__msg__GenerateMotion__Sequence * rhs);

/// Copy an array of msg/GenerateMotion messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_generate_motion_msgs
bool
generate_motion_msgs__msg__GenerateMotion__Sequence__copy(
  const generate_motion_msgs__msg__GenerateMotion__Sequence * input,
  generate_motion_msgs__msg__GenerateMotion__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // GENERATE_MOTION_MSGS__MSG__DETAIL__GENERATE_MOTION__FUNCTIONS_H_
