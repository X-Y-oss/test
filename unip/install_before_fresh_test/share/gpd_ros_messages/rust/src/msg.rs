#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to gpd_ros_messages__msg__CloudIndexed
/// This message holds a point cloud and a list of indices into the point cloud 
/// at which to sample grasp candidates.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CloudIndexed {
    /// The point cloud.
    pub cloud_sources: super::msg::CloudSources,

    /// The indices into the point cloud at which to sample grasp candidates.
    pub indices: Vec<std_msgs::msg::Int64>,

}



impl Default for CloudIndexed {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CloudIndexed::default())
  }
}

impl rosidl_runtime_rs::Message for CloudIndexed {
  type RmwMsg = super::msg::rmw::CloudIndexed;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cloud_sources: super::msg::CloudSources::into_rmw_message(std::borrow::Cow::Owned(msg.cloud_sources)).into_owned(),
        indices: msg.indices
          .into_iter()
          .map(|elem| std_msgs::msg::Int64::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cloud_sources: super::msg::CloudSources::into_rmw_message(std::borrow::Cow::Borrowed(&msg.cloud_sources)).into_owned(),
        indices: msg.indices
          .iter()
          .map(|elem| std_msgs::msg::Int64::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      cloud_sources: super::msg::CloudSources::from_rmw_message(msg.cloud_sources),
      indices: msg.indices
          .into_iter()
          .map(std_msgs::msg::Int64::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to gpd_ros_messages__msg__CloudSamples
/// This message holds a point cloud and a list of samples at which the grasp 
/// detector should search for grasp candidates.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CloudSamples {
    /// The point cloud.
    pub cloud_sources: super::msg::CloudSources,

    /// The samples, as (x,y,z) points, at which to search for grasp candidates.
    pub samples: Vec<geometry_msgs::msg::Point>,

}



impl Default for CloudSamples {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CloudSamples::default())
  }
}

impl rosidl_runtime_rs::Message for CloudSamples {
  type RmwMsg = super::msg::rmw::CloudSamples;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cloud_sources: super::msg::CloudSources::into_rmw_message(std::borrow::Cow::Owned(msg.cloud_sources)).into_owned(),
        samples: msg.samples
          .into_iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cloud_sources: super::msg::CloudSources::into_rmw_message(std::borrow::Cow::Borrowed(&msg.cloud_sources)).into_owned(),
        samples: msg.samples
          .iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      cloud_sources: super::msg::CloudSources::from_rmw_message(msg.cloud_sources),
      samples: msg.samples
          .into_iter()
          .map(geometry_msgs::msg::Point::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to gpd_ros_messages__msg__CloudSources
/// This message holds a point cloud that can be a combination of point clouds 
/// from different camera sources (at least one). For each point in the cloud, 
/// this message also stores the index of the camera that produced the point.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CloudSources {
    /// The point cloud.
    pub cloud: sensor_msgs::msg::PointCloud2,

    /// For each point in the cloud, the index of the camera that acquired the point.
    pub camera_source: Vec<std_msgs::msg::Int64>,

    /// A list of camera positions at which the point cloud was acquired.
    pub view_points: Vec<geometry_msgs::msg::Point>,

}



impl Default for CloudSources {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CloudSources::default())
  }
}

impl rosidl_runtime_rs::Message for CloudSources {
  type RmwMsg = super::msg::rmw::CloudSources;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cloud: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Owned(msg.cloud)).into_owned(),
        camera_source: msg.camera_source
          .into_iter()
          .map(|elem| std_msgs::msg::Int64::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
        view_points: msg.view_points
          .into_iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        cloud: sensor_msgs::msg::PointCloud2::into_rmw_message(std::borrow::Cow::Borrowed(&msg.cloud)).into_owned(),
        camera_source: msg.camera_source
          .iter()
          .map(|elem| std_msgs::msg::Int64::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
        view_points: msg.view_points
          .iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      cloud: sensor_msgs::msg::PointCloud2::from_rmw_message(msg.cloud),
      camera_source: msg.camera_source
          .into_iter()
          .map(std_msgs::msg::Int64::from_rmw_message)
          .collect(),
      view_points: msg.view_points
          .into_iter()
          .map(geometry_msgs::msg::Point::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to gpd_ros_messages__msg__GraspConfig
/// This message describes a 2-finger grasp configuration by its 6-DOF pose,
/// consisting of a 3-DOF position and 3-DOF orientation, and the opening
/// width of the robot hand.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GraspConfig {
    /// Position
    /// grasp position (bottom/base center of robot hand)
    pub position: geometry_msgs::msg::Point,

    /// Orientation represented as three axis (R =)
    /// grasp approach direction
    pub approach: geometry_msgs::msg::Vector3,

    /// hand closing direction
    pub binormal: geometry_msgs::msg::Vector3,

    /// hand axis
    pub axis: geometry_msgs::msg::Vector3,

    /// Required aperture (opening width) of the robot hand
    pub width: std_msgs::msg::Float32,

    /// Score assigned to the grasp by the classifier
    pub score: std_msgs::msg::Float32,

    /// point at which the grasp was found
    pub sample: geometry_msgs::msg::Point,

}



impl Default for GraspConfig {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::GraspConfig::default())
  }
}

impl rosidl_runtime_rs::Message for GraspConfig {
  type RmwMsg = super::msg::rmw::GraspConfig;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        position: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.position)).into_owned(),
        approach: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.approach)).into_owned(),
        binormal: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.binormal)).into_owned(),
        axis: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.axis)).into_owned(),
        width: std_msgs::msg::Float32::into_rmw_message(std::borrow::Cow::Owned(msg.width)).into_owned(),
        score: std_msgs::msg::Float32::into_rmw_message(std::borrow::Cow::Owned(msg.score)).into_owned(),
        sample: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.sample)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        position: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.position)).into_owned(),
        approach: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.approach)).into_owned(),
        binormal: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.binormal)).into_owned(),
        axis: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.axis)).into_owned(),
        width: std_msgs::msg::Float32::into_rmw_message(std::borrow::Cow::Borrowed(&msg.width)).into_owned(),
        score: std_msgs::msg::Float32::into_rmw_message(std::borrow::Cow::Borrowed(&msg.score)).into_owned(),
        sample: geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.sample)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      position: geometry_msgs::msg::Point::from_rmw_message(msg.position),
      approach: geometry_msgs::msg::Vector3::from_rmw_message(msg.approach),
      binormal: geometry_msgs::msg::Vector3::from_rmw_message(msg.binormal),
      axis: geometry_msgs::msg::Vector3::from_rmw_message(msg.axis),
      width: std_msgs::msg::Float32::from_rmw_message(msg.width),
      score: std_msgs::msg::Float32::from_rmw_message(msg.score),
      sample: geometry_msgs::msg::Point::from_rmw_message(msg.sample),
    }
  }
}


// Corresponds to gpd_ros_messages__msg__GraspConfigList
/// This message stores a list of grasp configurations.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct GraspConfigList {
    /// The time of acquisition, and the coordinate frame ID.
    pub header: std_msgs::msg::Header,

    /// The list of grasp configurations.
    pub grasps: Vec<super::msg::GraspConfig>,

}



impl Default for GraspConfigList {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::GraspConfigList::default())
  }
}

impl rosidl_runtime_rs::Message for GraspConfigList {
  type RmwMsg = super::msg::rmw::GraspConfigList;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        grasps: msg.grasps
          .into_iter()
          .map(|elem| super::msg::GraspConfig::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        grasps: msg.grasps
          .iter()
          .map(|elem| super::msg::GraspConfig::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      grasps: msg.grasps
          .into_iter()
          .map(super::msg::GraspConfig::from_rmw_message)
          .collect(),
    }
  }
}


// Corresponds to gpd_ros_messages__msg__SamplesMsg
/// This message describes a set of point samples at which to detect grasps.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SamplesMsg {
    /// Header
    pub header: std_msgs::msg::Header,

    /// The samples, as (x,y,z) points, at which to search for grasp candidates.
    pub samples: Vec<geometry_msgs::msg::Point>,

}



impl Default for SamplesMsg {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::SamplesMsg::default())
  }
}

impl rosidl_runtime_rs::Message for SamplesMsg {
  type RmwMsg = super::msg::rmw::SamplesMsg;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        samples: msg.samples
          .into_iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        samples: msg.samples
          .iter()
          .map(|elem| geometry_msgs::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      samples: msg.samples
          .into_iter()
          .map(geometry_msgs::msg::Point::from_rmw_message)
          .collect(),
    }
  }
}


