#!/usr/bin/env python3

import sys
import time
import traceback
from pathlib import Path

import numpy as np
import open3d as o3d

SRC = Path("/workspace/src/placeability_scoring")
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from placeability_scoring.placeability.Gripper_CollisionValidation import (
    Gripper_CollisionValidation,
)


POSES_PATH = Path(
    "/workspace/test/output/placement_sampling/placement_poses.npy"
)

MESH_PATH = Path(
    "/workspace/test/output/placement_sampling/"
    "placement_collision_mesh.ply"
)

OUTPUT_DIR = Path(
    "/workspace/test/output/gripper_collision_validation"
)


def main() -> int:
    try:
        if not POSES_PATH.is_file():
            raise FileNotFoundError(POSES_PATH)

        if not MESH_PATH.is_file():
            raise FileNotFoundError(MESH_PATH)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        raw_groups = np.load(
            POSES_PATH,
            allow_pickle=True,
        )

        placement_groups = []

        for orientation_index, raw_group in enumerate(raw_groups):
            group = np.asarray(
                raw_group,
                dtype=np.float64,
            )

            if group.ndim != 3 or group.shape[1:] != (4, 4):
                raise RuntimeError(
                    f"Unexpected pose shape for orientation "
                    f"{orientation_index}: {group.shape}"
                )

            if not np.isfinite(group).all():
                raise RuntimeError(
                    f"Non-finite transform in orientation "
                    f"{orientation_index}"
                )

            placement_groups.append(group)

        nonempty_groups = [
            group
            for group in placement_groups
            if group.shape[0] > 0
        ]

        if not nonempty_groups:
            raise RuntimeError(
                "No placement poses available"
            )

        transforms = np.concatenate(
            nonempty_groups,
            axis=0,
        )

        collision_mesh = o3d.io.read_triangle_mesh(
            str(MESH_PATH)
        )

        if collision_mesh.is_empty():
            raise RuntimeError(
                "Collision mesh is empty"
            )

        print("Input:")
        print(f"  transforms: {transforms.shape}")
        print(
            "  collision mesh: "
            f"{len(collision_mesh.vertices)} vertices, "
            f"{len(collision_mesh.triangles)} triangles"
        )

        collider = Gripper_CollisionValidation()
        collider.setMesh(collision_mesh)

        start_time = time.monotonic()

        collision_flags = collider.validate_collisions(
            Transforms=transforms,
            plotting=False,
        )

        elapsed = time.monotonic() - start_time

        if collision_flags is None:
            raise RuntimeError(
                "validate_collisions() returned None"
            )

        collision_flags = np.asarray(
            collision_flags,
            dtype=bool,
        )

        if collision_flags.shape != (transforms.shape[0],):
            raise RuntimeError(
                "Unexpected collision flag shape: "
                f"{collision_flags.shape}"
            )

        feasible_mask = ~collision_flags

        output_path = (
            OUTPUT_DIR / "placement_collision_flags.npz"
        )

        np.savez_compressed(
            output_path,
            transforms=transforms,
            collision_flags=collision_flags,
            feasible_mask=feasible_mask,
        )

        print("\nResult:")
        print(f"  total transforms: {transforms.shape[0]}")
        print(
            f"  colliding: "
            f"{np.count_nonzero(collision_flags)}"
        )
        print(
            f"  collision-free: "
            f"{np.count_nonzero(feasible_mask)}"
        )
        print(f"  elapsed: {elapsed:.3f} s")
        print(f"  saved: {output_path}")

        print(
            "\nUNIP GRIPPER COLLISION VALIDATION TEST: PASS"
        )
        return 0

    except Exception as exc:
        print(
            "\nUNIP GRIPPER COLLISION VALIDATION TEST: "
            f"FAIL: {exc}"
        )
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
