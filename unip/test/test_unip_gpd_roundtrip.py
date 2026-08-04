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

from placeability_scoring.grasping.GPD_Interface import GPD_Interface
from placeability_scoring.mapping.Offline_GraspingAreaReconstruction import (filter_object,)

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
    variables = config["variables"]

    table_height = variables["tableheight"]
    object_area = variables["object_area"]

    # Test-local ROI override for the current Isaac Sim scene.
    object_area = [
        0.50,   # xmin
        1.40,   # xmax
        1.18,   # ymin
        1.33,   # ymax
    ]

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

        node.get_logger().info(
            "Filtering object points from reconstructed environment"
        )

        weights_array = np.asarray(weights)

        if weights_array.shape[0] != points_array.shape[0]:
            raise RuntimeError(
                "Point/weight size mismatch: "
                f"{points_array.shape[0]} points, "
                f"{weights_array.shape[0]} weights"
            )
        environment_pointcloud = o3d.geometry.PointCloud()
        environment_pointcloud.points = o3d.utility.Vector3dVector(
            np.asarray(points_array, dtype=np.float64)
        )

        #######################validate the error of datatype##############################
        mins = points_array.min(axis=0)
        maxs = points_array.max(axis=0)

        node.get_logger().info(
            "Environment bounds: "
            f"x=[{mins[0]:.3f}, {maxs[0]:.3f}], "
            f"y=[{mins[1]:.3f}, {maxs[1]:.3f}], "
            f"z=[{mins[2]:.3f}, {maxs[2]:.3f}]"
        )

        node.get_logger().info(
            f"Configured object_area: {object_area}"
        )

        node.get_logger().info(
            f"Configured table_height: {table_height:.3f}"
        )

        xmin, xmax, ymin, ymax = object_area

        roi_mask = (
            (points_array[:, 0] >= xmin)
            & (points_array[:, 0] <= xmax)
            & (points_array[:, 1] >= ymin)
            & (points_array[:, 1] <= ymax)
        )

        above_table_mask = points_array[:, 2] >= table_height

        combined_mask = roi_mask & above_table_mask

        node.get_logger().info(
            f"Points inside XY object ROI: {np.count_nonzero(roi_mask)}"
        )

        node.get_logger().info(
            f"Points at/above table height: "
            f"{np.count_nonzero(above_table_mask)}"
        )

        node.get_logger().info(
            f"Points satisfying both: "
            f"{np.count_nonzero(combined_mask)}"
        )
        ############################################################################
        ############test############################################################
        object_height_min = table_height + 0.01
        object_height_max = min(
            table_height + 0.25,
            float(points_array[:, 2].max()),
        )

        height_mask = (
            (points_array[:, 2] >= object_height_min)
            & (points_array[:, 2] <= object_height_max)
        )

        candidate_points = points_array[height_mask]

        node.get_logger().info(
            f"Candidate height range: "
            f"[{object_height_min:.3f}, {object_height_max:.3f}]"
        )

        node.get_logger().info(
            f"Candidate points above table: {candidate_points.shape[0]}"
        )

        if candidate_points.shape[0] == 0:
            raise RuntimeError(
                "No candidate object points found above the table"
            )

        for percentile in (1, 5, 10, 25, 50, 75, 90, 95, 99):
            x_value = np.percentile(candidate_points[:, 0], percentile)
            y_value = np.percentile(candidate_points[:, 1], percentile)

            node.get_logger().info(
                f"Candidate XY p{percentile:02d}: "
                f"x={x_value:.3f}, y={y_value:.3f}"
            )

        ######################################################################
        if np.count_nonzero(roi_mask) == 0:
            raise RuntimeError(
                "Configured object_area does not overlap the reconstructed cloud: "
                f"object_area={object_area}"
            )
        #######################################################################

        object_points, object_weights, _, transform_obb_to_world = filter_object(
            environment_pointcloud,
            weights_array,
            plotting=False,
            table_height=table_height,
            object_area=object_area,
        )

        object_points = np.asarray(
            object_points,
            dtype=np.float32,
        ).reshape(-1, 3)

        object_weights = np.asarray(object_weights)

        node.get_logger().info(
            f"Filtered object point shape: {object_points.shape}"
        )

        node.get_logger().info(
            f"Filtered object weights shape: {object_weights.shape}"
        )

        if object_points.shape[0] == 0:
            raise RuntimeError(
                "filter_object() returned an empty object point cloud"
            )

        if not np.isfinite(object_points).all():
            raise RuntimeError(
                "Filtered object point cloud contains NaN or Inf"
            )

        gpd = GPD_Interface(node)

        # Wait for DDS discovery first
        discovery_deadline = time.monotonic() + 10.0
        while (
            gpd.publisher.get_subscription_count() == 0
            and time.monotonic() < discovery_deadline
        ):
            rclpy.spin_once(node, timeout_sec=0.1)

        if gpd.publisher.get_subscription_count() == 0:
            raise RuntimeError(
                "No GPD subscriber discovered on /cloud_stitched"
            )

        indices = np.arange(
            object_points.shape[0],
            dtype=np.int64,
        )

        gpd.publish_cloud_indexed(
            target=object_points,
            indices=indices,
            use_all=True,
        )

        grasp_deadline = time.monotonic() + 120.0
        last_status_time = time.monotonic()

        while rclpy.ok() and time.monotonic() < grasp_deadline:
            rclpy.spin_once(node, timeout_sec=0.1)

            if (
                isinstance(gpd.grasps, np.ndarray)
                and gpd.grasps.ndim == 2
                and gpd.grasps.shape[0] > 0
            ):
                break

            if time.monotonic() - last_status_time >= 10.0:
                remaining = grasp_deadline - time.monotonic()
                node.get_logger().info(
                    f"Waiting for clustered grasps; "
                    f"{remaining:.1f} seconds remaining"
                )
                last_status_time = time.monotonic()

        grasps = np.asarray(gpd.grasps)

        if grasps.ndim != 2 or grasps.shape[0] == 0:
            raise TimeoutError(
                "No clustered grasps received from GPD within 120 seconds"
            )

        if grasps.shape[1] != 17:
            raise RuntimeError(
                f"Unexpected grasp array shape: {grasps.shape}; "
                "expected (N, 17)"
            )

        if not np.isfinite(grasps).all():
            raise RuntimeError(
                "Received grasp array contains NaN or Inf"
            )

        node.get_logger().info(
            f"Received grasp array shape: {grasps.shape}"
        )

        node.get_logger().info(
            f"Best score: {np.max(grasps[:, 13]):.6f}"
        )

        #save the fixture
        fixture_dir = Path("/workspace/test/fixtures")
        fixture_dir.mkdir(parents=True, exist_ok=True)

        fixture_path = fixture_dir / "gpd_roundtrip_fixture.npz"

        np.savez_compressed(
            fixture_path,
            object_points=np.asarray(object_points, dtype=np.float32),
            object_weights=np.asarray(object_weights, dtype=np.float32),
            grasps=np.asarray(grasps, dtype=np.float32),
            transform_obb_to_world=np.asarray(
                transform_obb_to_world,
                dtype=np.float64,
            ),
        )

        node.get_logger().info(
            f"Saved GPD roundtrip fixture: {fixture_path}"
        )

        node.get_logger().info(
            "UNIP GPD ROUNDTRIP TEST: PASS"
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