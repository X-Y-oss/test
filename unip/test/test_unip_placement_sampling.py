#!/usr/bin/env python3

import sys
import time
import traceback
from pathlib import Path

import numpy as np
import open3d as o3d
from scipy.spatial import ConvexHull


PLACEABILITY_SRC = Path("/workspace/src/placeability_scoring")

if str(PLACEABILITY_SRC) not in sys.path:
    sys.path.insert(0, str(PLACEABILITY_SRC))


from placeability_scoring.environment_config import get_environment_config
import placeability_scoring.placeability.placeability as placeability_module
from placeability_scoring.placing.get_placement_locations import (
    get_placement_locations_multiple_orientations,
    make_o3d_mesh_object,
)


GPD_FIXTURE_PATH = Path(
    "/workspace/test/fixtures/gpd_roundtrip_fixture.npz"
)

PLACE_MESH_PATH = Path(
    "/workspace/test/fixtures/place_mesh.ply"
)

OUTPUT_DIR = Path(
    "/workspace/test/output/placement_sampling"
)


ORIGINAL_COMPUTE_STABILITY = placeability_module.compute_stability


def test_compute_stability_adapter(*args, **kwargs):
    """
    Test-only compatibility adapter.

    The current compute_stability() may return one score per support polygon,
    while get_stability() expects one scalar score. This runtime test uses the
    mean score without modifying production code.
    """
    result = ORIGINAL_COMPUTE_STABILITY(*args, **kwargs)

    if not isinstance(result, tuple):
        return result

    raw_scores = result[0]
    remaining_outputs = result[1:]

    score_values = np.asarray(
        raw_scores,
        dtype=np.float64,
    ).reshape(-1)

    aggregated_score = (
        float(np.mean(score_values))
        if score_values.size > 0
        else 0.0
    )

    print(
        "[TEST ADAPTER] support scores: "
        f"{score_values.tolist()} -> "
        f"mean={aggregated_score:.6f}"
    )

    return (aggregated_score, *remaining_outputs)


def normalize_convex_hulls(raw_hulls):
    """
    Test-only compatibility normalization.

    compute_placeability() currently may return one list of support polygons
    per orientation, while placement sampling expects one ConvexHull object
    per orientation. Select the first valid hull for this runtime test.
    """
    normalized = []

    for orientation_index, value in enumerate(raw_hulls):
        if isinstance(value, ConvexHull):
            normalized.append(value)
            continue

        if isinstance(value, (list, tuple)):
            valid = [
                item for item in value
                if isinstance(item, ConvexHull)
            ]

            if valid:
                print(
                    "[TEST ADAPTER] orientation "
                    f"{orientation_index}: selected first of "
                    f"{len(valid)} support hulls"
                )
                normalized.append(valid[0])
                continue

        raise RuntimeError(
            "No valid ConvexHull for orientation "
            f"{orientation_index}: {type(value).__name__}"
        )

    return normalized


def validate_transform_list(poses, orientation_count):
    if len(poses) != orientation_count:
        raise RuntimeError(
            "Orientation/result mismatch: "
            f"{orientation_count} orientations, "
            f"{len(poses)} pose arrays"
        )

    total_poses = 0

    for orientation_index, pose_array in enumerate(poses):
        pose_array = np.asarray(pose_array)

        print(
            f"  orientation {orientation_index}: "
            f"{pose_array.shape}"
        )

        if pose_array.ndim != 3 or pose_array.shape[1:] != (4, 4):
            raise RuntimeError(
                "Unexpected pose shape for orientation "
                f"{orientation_index}: {pose_array.shape}"
            )

        if not np.isfinite(pose_array).all():
            raise RuntimeError(
                "Non-finite placement transform for orientation "
                f"{orientation_index}"
            )

        if pose_array.shape[0] > 0:
            last_rows = pose_array[:, 3, :]
            expected_last_rows = np.tile(
                np.array([0.0, 0.0, 0.0, 1.0]),
                (pose_array.shape[0], 1),
            )

            if not np.allclose(
                last_rows,
                expected_last_rows,
                atol=1e-6,
            ):
                raise RuntimeError(
                    "Invalid homogeneous transform row for orientation "
                    f"{orientation_index}"
                )

        total_poses += pose_array.shape[0]

    if total_poses == 0:
        raise RuntimeError(
            "Placement sampling returned no valid poses"
        )

    return total_poses


def main() -> int:
    try:
        if not GPD_FIXTURE_PATH.is_file():
            raise FileNotFoundError(
                f"Missing GPD fixture: {GPD_FIXTURE_PATH}"
            )

        if not PLACE_MESH_PATH.is_file():
            raise FileNotFoundError(
                f"Missing placing mesh fixture: {PLACE_MESH_PATH}"
            )

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with np.load(GPD_FIXTURE_PATH) as data:
            object_points = np.asarray(
                data["object_points"],
                dtype=np.float64,
            )
            object_weights = np.asarray(
                data["object_weights"],
                dtype=np.float64,
            )
            grasps = np.asarray(
                data["grasps"],
                dtype=np.float64,
            )

        place_mesh = o3d.io.read_triangle_mesh(
            str(PLACE_MESH_PATH)
        )

        if place_mesh.is_empty():
            raise RuntimeError(
                f"Placing mesh is empty: {PLACE_MESH_PATH}"
            )

        place_mesh.compute_vertex_normals()

        print("Fixtures:")
        print(f"  object_points:  {object_points.shape}")
        print(f"  object_weights: {object_weights.shape}")
        print(f"  grasps:         {grasps.shape}")
        print(
            "  place_mesh:     "
            f"{len(place_mesh.vertices)} vertices, "
            f"{len(place_mesh.triangles)} triangles"
        )

        if object_points.ndim != 2 or object_points.shape[1] != 3:
            raise RuntimeError(
                f"Unexpected object point shape: {object_points.shape}"
            )

        if object_weights.shape != (object_points.shape[0],):
            raise RuntimeError(
                "Point/weight mismatch: "
                f"{object_points.shape[0]} points versus "
                f"{object_weights.shape} weights"
            )

        if grasps.ndim != 2 or grasps.shape[1] != 17:
            raise RuntimeError(
                f"Unexpected grasp shape: {grasps.shape}"
            )

        if not np.isfinite(object_points).all():
            raise RuntimeError(
                "object_points contains NaN or Inf"
            )

        if not np.isfinite(object_weights).all():
            raise RuntimeError(
                "object_weights contains NaN or Inf"
            )

        if not np.isfinite(grasps).all():
            raise RuntimeError(
                "grasps contains NaN or Inf"
            )

        config = get_environment_config()
        variables = config["variables"]

        orientations = variables["orientations"]
        clearance = float(variables["clearance"])

        if not orientations:
            raise RuntimeError(
                "No placement orientations configured"
            )

        # Deterministic and reduced-cost runtime test.
        stability_config = {
            "rotation_averaging_n": 1,
            "rotation_perturbation_deg": 0.0,
            "rotation_sampling_seed": 0,
            "n_mc_samples": 1000,
            "ground_threshold": float(
                variables.get("ground_threshold", 0.005)
            ),
        }

        print("\nStep 3A prerequisite: recomputing placeability...")

        placeability_module.compute_stability = (
            test_compute_stability_adapter
        )

        try:
            (
                filtered_grasps,
                placement_maps,
                raw_convex_hulls,
                center_alignments,
            ) = placeability_module.compute_placeability(
                grasps_array=grasps,
                pointcloud=object_points,
                weights=object_weights,
                orientations=orientations,
                plotting=False,
                clearance=clearance,
                calculate_stability=True,
                path=str(OUTPUT_DIR) + "/",
                stability_config=stability_config,
            )
        finally:
            placeability_module.compute_stability = (
                ORIGINAL_COMPUTE_STABILITY
            )

        filtered_grasps = np.asarray(filtered_grasps)
        placement_maps = np.asarray(placement_maps)
        center_alignments = np.asarray(
            center_alignments,
            dtype=np.float64,
        )

        object_convex_hulls = normalize_convex_hulls(
            raw_convex_hulls
        )

        print("\nPlaceability prerequisite result:")
        print(f"  filtered_grasps:  {filtered_grasps.shape}")
        print(f"  placement_maps:   {placement_maps.shape}")
        print(f"  convex_hulls:      {len(object_convex_hulls)}")
        print(f"  center_alignments: {center_alignments.shape}")

        if center_alignments.shape != (len(orientations), 3):
            raise RuntimeError(
                "Unexpected center alignment shape: "
                f"{center_alignments.shape}"
            )

        print("\nBuilding object mesh...")

        object_pointcloud = o3d.geometry.PointCloud()
        object_pointcloud.points = o3d.utility.Vector3dVector(
            np.asarray(object_points, dtype=np.float64)
        )

        object_mesh = make_o3d_mesh_object(
            object_pointcloud,
            voxel_size=0.01,
            alpha=0.05,
        )

        if not isinstance(
            object_mesh,
            o3d.geometry.TriangleMesh,
        ):
            raise TypeError(
                "make_o3d_mesh_object() returned "
                f"{type(object_mesh).__name__}"
            )

        if object_mesh.is_empty():
            raise RuntimeError(
                "Generated object mesh is empty"
            )

        object_mesh.compute_vertex_normals()

        print(
            "  object_mesh: "
            f"{len(object_mesh.vertices)} vertices, "
            f"{len(object_mesh.triangles)} triangles"
        )

        place_vertices = np.asarray(
            place_mesh.vertices,
            dtype=np.float64,
        )

        mesh_min = place_vertices.min(axis=0)
        mesh_max = place_vertices.max(axis=0)

        print("\nCurrent placing mesh bounds:")
        print(
            f"  x=[{mesh_min[0]:.3f}, {mesh_max[0]:.3f}]"
        )
        print(
            f"  y=[{mesh_min[1]:.3f}, {mesh_max[1]:.3f}]"
        )
        print(
            f"  z=[{mesh_min[2]:.3f}, {mesh_max[2]:.3f}]"
        )

        # Test-local USD-aligned bounds.
        #
        # These broad bounds are only for runtime validation. They must not be
        # treated as the final experiment configuration.
        margin = np.array([0.005, 0.005, 0.005])

        test_min = mesh_min - margin
        test_max = mesh_max + margin

        placement_bounds = {
            "lower_shelf": {
                "min_bound": test_min,
                "max_bound": test_max,
                "min_bound_shelf": test_min,
                "max_bound_shelf": test_max,
                "min_bound_placement": test_min,
                "max_bound_placement": test_max,
            }
        }

        print("\nRunning placement candidate generation...")
        print("  environment: lower_shelf")
        print(f"  sampled poses requested: 50")
        print(
            "  TEST-LOCAL bounds: "
            f"min={test_min.tolist()}, "
            f"max={test_max.tolist()}"
        )

        np.random.seed(0)
        start_time = time.monotonic()

        poses, collision_mesh = (
            get_placement_locations_multiple_orientations(
                obj_mesh=object_mesh,
                env_mesh=place_mesh,
                object_convex_hull=object_convex_hulls,
                orientations=orientations,
                center_alignments=center_alignments,
                plotting=False,
                number_of_poses=50,
                environment="lower_shelf",
                placement_bounds=placement_bounds,
            )
        )

        elapsed = time.monotonic() - start_time

        print("\nPlacement result:")
        total_poses = validate_transform_list(
            poses,
            len(orientations),
        )

        if not isinstance(
            collision_mesh,
            o3d.geometry.TriangleMesh,
        ):
            raise TypeError(
                "Unexpected collision mesh type: "
                f"{type(collision_mesh).__name__}"
            )

        if collision_mesh.is_empty():
            raise RuntimeError(
                "Returned collision mesh is empty"
            )

        print(f"  total valid poses: {total_poses}")
        print(
            "  collision mesh: "
            f"{len(collision_mesh.vertices)} vertices, "
            f"{len(collision_mesh.triangles)} triangles"
        )
        print(f"  elapsed: {elapsed:.3f} s")

        ##############save the collision mesh###########################
        collision_mesh_path = (
            OUTPUT_DIR / "placement_collision_mesh.ply"
        )

        write_ok = o3d.io.write_triangle_mesh(
            str(collision_mesh_path),
            collision_mesh,
        )

        if not write_ok:
            raise RuntimeError(
                f"Failed to save collision mesh: {collision_mesh_path}"
            )

        print(f"  saved collision mesh: {collision_mesh_path}")
        ###############################################################

        pose_fixture = OUTPUT_DIR / "placement_poses.npy"

        np.save(
            pose_fixture,
            np.array(poses, dtype=object),
            allow_pickle=True,
        )

        print(f"  saved poses: {pose_fixture}")

        print(
            "\nUNIP PLACEMENT SAMPLING TEST: PASS\n"
            "NOTE: This runtime test used temporary USD-aligned "
            "placement bounds."
        )

        return 0

    except Exception as exc:
        placeability_module.compute_stability = (
            ORIGINAL_COMPUTE_STABILITY
        )

        print(
            "\nUNIP PLACEMENT SAMPLING TEST: "
            f"FAIL: {exc}"
        )
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
