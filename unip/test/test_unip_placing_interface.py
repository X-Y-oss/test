#!/usr/bin/env python3

import sys
import traceback

import numpy as np
import open3d as o3d
import rclpy
from pathlib import Path
import placeability_scoring

from rclpy.node import Node
from rclpy.duration import Duration
from tf2_ros import Buffer, TransformListener
from scipy.spatial.transform import Rotation as R

from placeability_scoring.environment_config import get_environment_config
from placeability_scoring.mapping.PlacingAreaReconstruction_Interface import (
    PlacingAreaReconstruction_Interface,
)


class PlacingInterfaceTestNode(Node):
    def __init__(self) -> None:
        super().__init__("test_unip_placing_interface")

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self,
            spin_thread=True,
        )


class TestablePlacingInterface(PlacingAreaReconstruction_Interface):
    """
    Test-only adapter.

    The baseline lookup implementation may call spin_once() from inside an
    image callback. This adapter uses the TransformListener background thread
    instead, avoiding nested executor spinning.
    """

    def lookup_transform(self, source=""):
        transform = self.tf_buffer.lookup_transform(
            "world",
            source,
            rclpy.time.Time(),
            timeout=Duration(seconds=5.0),
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

        # Preserve the baseline camera-axis conversion.
        rotation = rotation @ np.diag([1.0, -1.0, 1.0])
        rotation = rotation @ np.diag([-1.0, 1.0, 1.0])

        matrix = np.eye(4, dtype=float)
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


def point_count(point_cloud) -> int:
    if isinstance(point_cloud, np.ndarray):
        if point_cloud.ndim != 2 or point_cloud.shape[1] != 3:
            raise ValueError(
                f"Unexpected NumPy point-cloud shape: {point_cloud.shape}"
            )
        return point_cloud.shape[0]

    if isinstance(point_cloud, o3d.t.geometry.PointCloud):
        return int(point_cloud.point.positions.shape[0])

    if isinstance(point_cloud, o3d.geometry.PointCloud):
        return len(point_cloud.points)

    raise TypeError(
        f"Unsupported point-cloud type: {type(point_cloud).__name__}"
    )


def main() -> int:
    node = None

    try:
        rclpy.init()

        node = PlacingInterfaceTestNode()

        env_cfg = get_environment_config()
        simulation_cfg = env_cfg["simulation"]
        variables_cfg = env_cfg["variables"]

        topics = simulation_cfg["topics"]
        camera_links = simulation_cfg["camera_links"]

        package_dir = Path(placeability_scoring.__file__).resolve().parent
        extrinsics_dir = Path("/workspace/src/placeability_scoring/""placeability_scoring/camera_extrinsics")

        wrist_extrinsics = extrinsics_dir / "T_wrist_cam.npy"
        if not wrist_extrinsics.is_file():
            raise FileNotFoundError(
                f"Wrist camera extrinsics not found: {wrist_extrinsics}"
            )

        extrinsics_dir = str(extrinsics_dir)

        print("Topics:")
        for key, value in topics.items():
            print(f"  {key}: {value}")

        print("Camera links:")
        for key, value in camera_links.items():
            print(f"  {key}: {value}")

        print("Extrinsics directory:")
        print(f"  {extrinsics_dir}")

        placing_map = TestablePlacingInterface(
            node=node,
            simulation=True,
            rgb_used=True,
            topics=topics,
            camera_links=camera_links,
            extrinsics_save_dir=extrinsics_dir,
        )

        print("\nWaiting for wrist RGB-D placing observation...")

        result = placing_map.process_new_data(
            returning=True,
            dummy="placing_test",
            save_dir="",
        )

        if not isinstance(result, tuple):
            raise TypeError(
                f"Expected tuple result, got {type(result).__name__}"
            )

        if len(result) != 3:
            raise ValueError(
                f"Expected 3 return values, got {len(result)}"
            )

        place_area_pcl, labeled_pointcloud, place_mesh = result

        n_points = point_count(place_area_pcl)

        if not isinstance(place_mesh, o3d.geometry.TriangleMesh):
            raise TypeError(
                "Expected Open3D legacy TriangleMesh, got "
                f"{type(place_mesh).__name__}"
            )

        n_vertices = len(place_mesh.vertices)
        n_triangles = len(place_mesh.triangles)

        print("\nResult:")
        print(f"  Point-cloud type: {type(place_area_pcl).__name__}")
        print(f"  Point count: {n_points}")
        print(
            "  Labeled point cloud: "
            f"{type(labeled_pointcloud).__name__}"
        )
        print(f"  Mesh vertices: {n_vertices}")
        print(f"  Mesh triangles: {n_triangles}")

        if n_points == 0:
            raise RuntimeError("Placing point cloud is empty")

        if n_vertices == 0:
            raise RuntimeError("Placing mesh is empty")

        ############save the placing mesh fixture###########################
        fixture_dir = Path("/workspace/test/fixtures")
        fixture_dir.mkdir(parents=True, exist_ok=True)

        place_mesh_path = fixture_dir / "place_mesh.ply"

        write_ok = o3d.io.write_triangle_mesh(
            str(place_mesh_path),
            place_mesh,
        )

        if not write_ok:
            raise RuntimeError(
                f"Failed to save placing mesh: {place_mesh_path}"
            )

        print(f"  Saved placing mesh fixture: {place_mesh_path}")

        print("\nUNIP PLACING INTERFACE TEST: PASS")
        return 0        
        ##########################################################

    except Exception as exc:
        print(
            "\nUNIP PLACING INTERFACE TEST: FAIL\n"
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        traceback.print_exc()
        return 1

    finally:
        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
