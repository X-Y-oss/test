#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to generate_motion_msgs__msg__GenerateMotion

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GenerateMotion {

    // This member is not documented.
    #[allow(missing_docs)]
    pub robot_file: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pose_lists: Vec<f64>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub segment_modes: Vec<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub linear_axes: Vec<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attach_cylinder: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub attach_after_index: Vec<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub detach_after_index: Vec<i32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub cylinder_radius: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub cylinder_height: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub cylinder_pose: Vec<f64>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub grasp_prepose_motion: bool,

}



impl Default for GenerateMotion {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::GenerateMotion::default())
  }
}

impl rosidl_runtime_rs::Message for GenerateMotion {
  type RmwMsg = super::msg::rmw::GenerateMotion;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_file: msg.robot_file.as_str().into(),
        pose_lists: msg.pose_lists.into(),
        segment_modes: msg.segment_modes.into(),
        linear_axes: msg.linear_axes.into(),
        attach_cylinder: msg.attach_cylinder,
        attach_after_index: msg.attach_after_index.into(),
        detach_after_index: msg.detach_after_index.into(),
        cylinder_radius: msg.cylinder_radius,
        cylinder_height: msg.cylinder_height,
        cylinder_pose: msg.cylinder_pose.into(),
        grasp_prepose_motion: msg.grasp_prepose_motion,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        robot_file: msg.robot_file.as_str().into(),
        pose_lists: msg.pose_lists.as_slice().into(),
        segment_modes: msg.segment_modes.as_slice().into(),
        linear_axes: msg.linear_axes.as_slice().into(),
      attach_cylinder: msg.attach_cylinder,
        attach_after_index: msg.attach_after_index.as_slice().into(),
        detach_after_index: msg.detach_after_index.as_slice().into(),
      cylinder_radius: msg.cylinder_radius,
      cylinder_height: msg.cylinder_height,
        cylinder_pose: msg.cylinder_pose.as_slice().into(),
      grasp_prepose_motion: msg.grasp_prepose_motion,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      robot_file: msg.robot_file.to_string(),
      pose_lists: msg.pose_lists
          .into_iter()
          .collect(),
      segment_modes: msg.segment_modes
          .into_iter()
          .collect(),
      linear_axes: msg.linear_axes
          .into_iter()
          .collect(),
      attach_cylinder: msg.attach_cylinder,
      attach_after_index: msg.attach_after_index
          .into_iter()
          .collect(),
      detach_after_index: msg.detach_after_index
          .into_iter()
          .collect(),
      cylinder_radius: msg.cylinder_radius,
      cylinder_height: msg.cylinder_height,
      cylinder_pose: msg.cylinder_pose
          .into_iter()
          .collect(),
      grasp_prepose_motion: msg.grasp_prepose_motion,
    }
  }
}


