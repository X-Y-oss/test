#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to gpd_ros_messages__srv__DetectGrasps_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DetectGrasps_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub cloud_indexed: super::msg::CloudIndexed,

}



impl Default for DetectGrasps_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::DetectGrasps_Request::default())
  }
}

impl rosidl_runtime_rs::Message for DetectGrasps_Request {
  type RmwMsg = super::srv::rmw::DetectGrasps_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cloud_indexed: super::msg::CloudIndexed::into_rmw_message(std::borrow::Cow::Owned(msg.cloud_indexed)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cloud_indexed: super::msg::CloudIndexed::into_rmw_message(std::borrow::Cow::Borrowed(&msg.cloud_indexed)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      cloud_indexed: super::msg::CloudIndexed::from_rmw_message(msg.cloud_indexed),
    }
  }
}


// Corresponds to gpd_ros_messages__srv__DetectGrasps_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct DetectGrasps_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub grasp_configs: super::msg::GraspConfigList,

}



impl Default for DetectGrasps_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::DetectGrasps_Response::default())
  }
}

impl rosidl_runtime_rs::Message for DetectGrasps_Response {
  type RmwMsg = super::srv::rmw::DetectGrasps_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        grasp_configs: super::msg::GraspConfigList::into_rmw_message(std::borrow::Cow::Owned(msg.grasp_configs)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        grasp_configs: super::msg::GraspConfigList::into_rmw_message(std::borrow::Cow::Borrowed(&msg.grasp_configs)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      grasp_configs: super::msg::GraspConfigList::from_rmw_message(msg.grasp_configs),
    }
  }
}






#[link(name = "gpd_ros_messages__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__gpd_ros_messages__srv__DetectGrasps() -> *const std::ffi::c_void;
}

// Corresponds to gpd_ros_messages__srv__DetectGrasps
#[allow(missing_docs, non_camel_case_types)]
pub struct DetectGrasps;

impl rosidl_runtime_rs::Service for DetectGrasps {
    type Request = DetectGrasps_Request;
    type Response = DetectGrasps_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__gpd_ros_messages__srv__DetectGrasps() }
    }
}


