#!/usr/bin/env python3

import sys
import time
from pathlib import Path

import numpy as np
import rclpy
import traceback
import open3d as o3d
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from rclpy.duration import Duration
from scipy.spatial.transform import Rotation as R
from tf2_ros import TransformException

PLACEABILITY_SRC = Path("/workspace/src/placeability_scoring")

if str(PLACEABILITY_SRC) not in sys.path:
    sys.path.insert(0, str(PLACEABILITY_SRC))

from placeability_scoring.environment_config import get_environment_config
from placeability_scoring.mapping.GraspingAreaReconstruction_Interface import (
    GraspingAreaReconstruction_Interface,
)


class UniPGraspingInterfaceTestNode(Node):
    def __init__(self) -> None:
        super().__init__("unip_grasping_interface_test")

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self,
            spin_thread=True,
        )

class TestableGraspingInterface(
    GraspingAreaReconstruction_Interface
):
    """Test-only adapter that avoids nested rclpy.spin_once()."""

    def lookup_transform(self, source: str = ""):
        try:
            transform = self.tf_buffer.lookup_transform(
                "world",
                source,
                rclpy.time.Time(),
                timeout=Duration(seconds=2.0),
            )

            translation = transform.transform.translation
            quaternion = transform.transform.rotation

            rotation = R.from_quat(
                [
                    quaternion.x,
                    quaternion.y,
                    quaternion.z,
                    quaternion.w,
                ]
            ).as_matrix()

            rotation = rotation @ np.diag([1.0, -1.0, 1.0])
            rotation = rotation @ np.diag([-1.0, 1.0, 1.0])

            matrix = np.eye(4)
            matrix[:3, :3] = rotation
            matrix[:3, 3] = [
                translation.x,
                translation.y,
                translation.z,
            ]

            self.node.get_logger().info(
                f"TF PASS: world -> {source}"
            )
            return matrix

        except TransformException as exc:
            self.node.get_logger().error(
                f"TF lookup failed: world -> {source}: {exc}"
            )
            return None


def main() -> int:
    rclpy.init()

    node = UniPGraspingInterfaceTestNode()

    config = get_environment_config()
    sim_config = config["simulation"]

    extrinsics_dir = (
        "/workspace/src/placeability_scoring/"
        "placeability_scoring/camera_extrinsics/"
    )

    node.get_logger().info(
        "Initializing GraspingAreaReconstruction_Interface"
    )

    interface = TestableGraspingInterface(
        node=node,
        simulation=True,
        selected_cameras=["wrist"],
        topics=sim_config["topics"],
        camera_links=sim_config["camera_links"],
        extrinsics_save_dir=extrinsics_dir,
    )

    try:
        start_time = time.monotonic()

        points, mesh, weights = interface.process_new_data(
            selected_camera="wrist",
            show=False,
            save_dir="",
        )

        elapsed = time.monotonic() - start_time

        if points is None:
            node.get_logger().error(
                "Point cloud extraction returned None"
            )
            return 1

        
        if isinstance(points, np.ndarray):
            points_array = points

        elif isinstance(points, o3d.t.geometry.PointCloud):
            points_array = points.point.positions.numpy()

        elif isinstance(points, o3d.geometry.PointCloud):
            points_array = np.asarray(points.points)

        else:
            raise TypeError(
                f"Unsupported point cloud type: {type(points)}"
            )

        node.get_logger().info(
            f"Point cloud shape: {points_array.shape}"
        )

        node.get_logger().info(
            f"Point cloud dtype: {points_array.dtype}"
        )

        node.get_logger().info(
            f"Mesh vertices: "
            f"{len(mesh.vertices) if mesh is not None else 'None'}"
        )

        weights_array = np.asarray(weights)

        node.get_logger().info(
            f"Weights shape: {weights_array.shape}"
        )

        node.get_logger().info(
            f"Elapsed time: {elapsed:.3f} s"
        )

        if points_array.size == 0:
            node.get_logger().error(
                "Point cloud is empty"
            )
            return 1

        if points_array.ndim != 2:
            node.get_logger().error(
                f"Unexpected point cloud dimensions: "
                f"{points_array.shape}"
            )
            return 1

        if points_array.shape[1] != 3:
            node.get_logger().error(
                f"Unexpected point format: "
                f"{points_array.shape}"
            )
            return 1

        if not np.isfinite(points_array).all():
            node.get_logger().error(
                "Point cloud contains NaN or Inf values"
            )
            return 1

        node.get_logger().info(
            "UNIP GRASPING INTERFACE TEST: PASS"
        )

        return 0

    except Exception as exc:
        node.get_logger().error(
            f"UNIP GRASPING INTERFACE TEST: FAIL: {exc}"
        )
        traceback.print_exc()
        return 1

    finally:
        try:
            interface.free_contruction_memory()
        except Exception:
            pass

        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())