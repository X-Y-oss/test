#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "generate_motion_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__generate_motion_msgs__msg__GenerateMotion() -> *const std::ffi::c_void;
}

#[link(name = "generate_motion_msgs__rosidl_generator_c")]
extern "C" {
    fn generate_motion_msgs__msg__GenerateMotion__init(msg: *mut GenerateMotion) -> bool;
    fn generate_motion_msgs__msg__GenerateMotion__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GenerateMotion>, size: usize) -> bool;
    fn generate_motion_msgs__msg__GenerateMotion__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GenerateMotion>);
    fn generate_motion_msgs__msg__GenerateMotion__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GenerateMotion>, out_seq: *mut rosidl_runtime_rs::Sequence<GenerateMotion>) -> bool;
}

// Corresponds to generate_motion_msgs__msg__GenerateMotion
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GenerateMotion {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_file: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pose_lists: rosidl_runtime_rs::Sequence<f64>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub segment_modes: rosidl_runtime_rs::Sequence<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub linear_axes: rosidl_runtime_rs::Sequence<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attach_cylinder: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attach_after_index: rosidl_runtime_rs::Sequence<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub detach_after_index: rosidl_runtime_rs::Sequence<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub cylinder_radius: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub cylinder_height: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub cylinder_pose: rosidl_runtime_rs::Sequence<f64>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub grasp_prepose_motion: bool,

}



impl Default for GenerateMotion {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !generate_motion_msgs__msg__GenerateMotion__init(&mut msg as *mut _) {
        panic!("Call to generate_motion_msgs__msg__GenerateMotion__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GenerateMotion {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { generate_motion_msgs__msg__GenerateMotion__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { generate_motion_msgs__msg__GenerateMotion__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { generate_motion_msgs__msg__GenerateMotion__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GenerateMotion {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GenerateMotion where Self: Sized {
  const TYPE_NAME: &'static str = "generate_motion_msgs/msg/GenerateMotion";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__generate_motion_msgs__msg__GenerateMotion() }
  }
}


