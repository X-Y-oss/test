#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "gpd_ros_messages__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__CloudIndexed() -> *const std::ffi::c_void;
}

#[link(name = "gpd_ros_messages__rosidl_generator_c")]
extern "C" {
    fn gpd_ros_messages__msg__CloudIndexed__init(msg: *mut CloudIndexed) -> bool;
    fn gpd_ros_messages__msg__CloudIndexed__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CloudIndexed>, size: usize) -> bool;
    fn gpd_ros_messages__msg__CloudIndexed__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CloudIndexed>);
    fn gpd_ros_messages__msg__CloudIndexed__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CloudIndexed>, out_seq: *mut rosidl_runtime_rs::Sequence<CloudIndexed>) -> bool;
}

// Corresponds to gpd_ros_messages__msg__CloudIndexed
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This message holds a point cloud and a list of indices into the point cloud 
/// at which to sample grasp candidates.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CloudIndexed {
    /// The point cloud.
    pub cloud_sources: super::super::msg::rmw::CloudSources,

    /// The indices into the point cloud at which to sample grasp candidates.
    pub indices: rosidl_runtime_rs::Sequence<std_msgs::msg::rmw::Int64>,

}



impl Default for CloudIndexed {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !gpd_ros_messages__msg__CloudIndexed__init(&mut msg as *mut _) {
        panic!("Call to gpd_ros_messages__msg__CloudIndexed__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CloudIndexed {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__CloudIndexed__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__CloudIndexed__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__CloudIndexed__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CloudIndexed {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CloudIndexed where Self: Sized {
  const TYPE_NAME: &'static str = "gpd_ros_messages/msg/CloudIndexed";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__CloudIndexed() }
  }
}


#[link(name = "gpd_ros_messages__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__CloudSamples() -> *const std::ffi::c_void;
}

#[link(name = "gpd_ros_messages__rosidl_generator_c")]
extern "C" {
    fn gpd_ros_messages__msg__CloudSamples__init(msg: *mut CloudSamples) -> bool;
    fn gpd_ros_messages__msg__CloudSamples__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CloudSamples>, size: usize) -> bool;
    fn gpd_ros_messages__msg__CloudSamples__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CloudSamples>);
    fn gpd_ros_messages__msg__CloudSamples__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CloudSamples>, out_seq: *mut rosidl_runtime_rs::Sequence<CloudSamples>) -> bool;
}

// Corresponds to gpd_ros_messages__msg__CloudSamples
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This message holds a point cloud and a list of samples at which the grasp 
/// detector should search for grasp candidates.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CloudSamples {
    /// The point cloud.
    pub cloud_sources: super::super::msg::rmw::CloudSources,

    /// The samples, as (x,y,z) points, at which to search for grasp candidates.
    pub samples: rosidl_runtime_rs::Sequence<geometry_msgs::msg::rmw::Point>,

}



impl Default for CloudSamples {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !gpd_ros_messages__msg__CloudSamples__init(&mut msg as *mut _) {
        panic!("Call to gpd_ros_messages__msg__CloudSamples__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CloudSamples {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__CloudSamples__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__CloudSamples__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__CloudSamples__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CloudSamples {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CloudSamples where Self: Sized {
  const TYPE_NAME: &'static str = "gpd_ros_messages/msg/CloudSamples";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__CloudSamples() }
  }
}


#[link(name = "gpd_ros_messages__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__CloudSources() -> *const std::ffi::c_void;
}

#[link(name = "gpd_ros_messages__rosidl_generator_c")]
extern "C" {
    fn gpd_ros_messages__msg__CloudSources__init(msg: *mut CloudSources) -> bool;
    fn gpd_ros_messages__msg__CloudSources__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CloudSources>, size: usize) -> bool;
    fn gpd_ros_messages__msg__CloudSources__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CloudSources>);
    fn gpd_ros_messages__msg__CloudSources__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CloudSources>, out_seq: *mut rosidl_runtime_rs::Sequence<CloudSources>) -> bool;
}

// Corresponds to gpd_ros_messages__msg__CloudSources
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This message holds a point cloud that can be a combination of point clouds 
/// from different camera sources (at least one). For each point in the cloud, 
/// this message also stores the index of the camera that produced the point.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CloudSources {
    /// The point cloud.
    pub cloud: sensor_msgs::msg::rmw::PointCloud2,

    /// For each point in the cloud, the index of the camera that acquired the point.
    pub camera_source: rosidl_runtime_rs::Sequence<std_msgs::msg::rmw::Int64>,

    /// A list of camera positions at which the point cloud was acquired.
    pub view_points: rosidl_runtime_rs::Sequence<geometry_msgs::msg::rmw::Point>,

}



impl Default for CloudSources {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !gpd_ros_messages__msg__CloudSources__init(&mut msg as *mut _) {
        panic!("Call to gpd_ros_messages__msg__CloudSources__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CloudSources {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__CloudSources__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__CloudSources__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__CloudSources__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CloudSources {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CloudSources where Self: Sized {
  const TYPE_NAME: &'static str = "gpd_ros_messages/msg/CloudSources";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__CloudSources() }
  }
}


#[link(name = "gpd_ros_messages__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__GraspConfig() -> *const std::ffi::c_void;
}

#[link(name = "gpd_ros_messages__rosidl_generator_c")]
extern "C" {
    fn gpd_ros_messages__msg__GraspConfig__init(msg: *mut GraspConfig) -> bool;
    fn gpd_ros_messages__msg__GraspConfig__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GraspConfig>, size: usize) -> bool;
    fn gpd_ros_messages__msg__GraspConfig__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GraspConfig>);
    fn gpd_ros_messages__msg__GraspConfig__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GraspConfig>, out_seq: *mut rosidl_runtime_rs::Sequence<GraspConfig>) -> bool;
}

// Corresponds to gpd_ros_messages__msg__GraspConfig
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This message describes a 2-finger grasp configuration by its 6-DOF pose,
/// consisting of a 3-DOF position and 3-DOF orientation, and the opening
/// width of the robot hand.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GraspConfig {
    /// Position
    /// grasp position (bottom/base center of robot hand)
    pub position: geometry_msgs::msg::rmw::Point,

    /// Orientation represented as three axis (R =)
    /// grasp approach direction
    pub approach: geometry_msgs::msg::rmw::Vector3,

    /// hand closing direction
    pub binormal: geometry_msgs::msg::rmw::Vector3,

    /// hand axis
    pub axis: geometry_msgs::msg::rmw::Vector3,

    /// Required aperture (opening width) of the robot hand
    pub width: std_msgs::msg::rmw::Float32,

    /// Score assigned to the grasp by the classifier
    pub score: std_msgs::msg::rmw::Float32,

    /// point at which the grasp was found
    pub sample: geometry_msgs::msg::rmw::Point,

}



impl Default for GraspConfig {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !gpd_ros_messages__msg__GraspConfig__init(&mut msg as *mut _) {
        panic!("Call to gpd_ros_messages__msg__GraspConfig__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GraspConfig {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__GraspConfig__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__GraspConfig__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__GraspConfig__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GraspConfig {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GraspConfig where Self: Sized {
  const TYPE_NAME: &'static str = "gpd_ros_messages/msg/GraspConfig";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__GraspConfig() }
  }
}


#[link(name = "gpd_ros_messages__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__GraspConfigList() -> *const std::ffi::c_void;
}

#[link(name = "gpd_ros_messages__rosidl_generator_c")]
extern "C" {
    fn gpd_ros_messages__msg__GraspConfigList__init(msg: *mut GraspConfigList) -> bool;
    fn gpd_ros_messages__msg__GraspConfigList__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<GraspConfigList>, size: usize) -> bool;
    fn gpd_ros_messages__msg__GraspConfigList__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<GraspConfigList>);
    fn gpd_ros_messages__msg__GraspConfigList__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<GraspConfigList>, out_seq: *mut rosidl_runtime_rs::Sequence<GraspConfigList>) -> bool;
}

// Corresponds to gpd_ros_messages__msg__GraspConfigList
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This message stores a list of grasp configurations.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GraspConfigList {
    /// The time of acquisition, and the coordinate frame ID.
    pub header: std_msgs::msg::rmw::Header,

    /// The list of grasp configurations.
    pub grasps: rosidl_runtime_rs::Sequence<super::super::msg::rmw::GraspConfig>,

}



impl Default for GraspConfigList {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !gpd_ros_messages__msg__GraspConfigList__init(&mut msg as *mut _) {
        panic!("Call to gpd_ros_messages__msg__GraspConfigList__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for GraspConfigList {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__GraspConfigList__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__GraspConfigList__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__GraspConfigList__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for GraspConfigList {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for GraspConfigList where Self: Sized {
  const TYPE_NAME: &'static str = "gpd_ros_messages/msg/GraspConfigList";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__GraspConfigList() }
  }
}


#[link(name = "gpd_ros_messages__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__SamplesMsg() -> *const std::ffi::c_void;
}

#[link(name = "gpd_ros_messages__rosidl_generator_c")]
extern "C" {
    fn gpd_ros_messages__msg__SamplesMsg__init(msg: *mut SamplesMsg) -> bool;
    fn gpd_ros_messages__msg__SamplesMsg__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SamplesMsg>, size: usize) -> bool;
    fn gpd_ros_messages__msg__SamplesMsg__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SamplesMsg>);
    fn gpd_ros_messages__msg__SamplesMsg__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SamplesMsg>, out_seq: *mut rosidl_runtime_rs::Sequence<SamplesMsg>) -> bool;
}

// Corresponds to gpd_ros_messages__msg__SamplesMsg
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// This message describes a set of point samples at which to detect grasps.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SamplesMsg {
    /// Header
    pub header: std_msgs::msg::rmw::Header,

    /// The samples, as (x,y,z) points, at which to search for grasp candidates.
    pub samples: rosidl_runtime_rs::Sequence<geometry_msgs::msg::rmw::Point>,

}



impl Default for SamplesMsg {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !gpd_ros_messages__msg__SamplesMsg__init(&mut msg as *mut _) {
        panic!("Call to gpd_ros_messages__msg__SamplesMsg__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SamplesMsg {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__SamplesMsg__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__SamplesMsg__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { gpd_ros_messages__msg__SamplesMsg__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SamplesMsg {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SamplesMsg where Self: Sized {
  const TYPE_NAME: &'static str = "gpd_ros_messages/msg/SamplesMsg";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__gpd_ros_messages__msg__SamplesMsg() }
  }
}


