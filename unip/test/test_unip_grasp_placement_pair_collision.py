#!/usr/bin/env python3

import sys
import time
import traceback
from pathlib import Path

import numpy as np
import open3d as o3d
from scipy.spatial.transform import Rotation as R

SRC = Path('/workspace/src/placeability_scoring')
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from placeability_scoring.environment_config import get_environment_config
from placeability_scoring.grasping.GPD_Interface import GPD_grasp_to_transform
from placeability_scoring.placeability.Gripper_CollisionValidation import Gripper_CollisionValidation
import placeability_scoring.placeability.placeability as pm

GPD_FIXTURE = Path('/workspace/test/fixtures/gpd_roundtrip_fixture.npz')
POSES_PATH = Path('/workspace/test/output/placement_sampling/placement_poses.npy')
MESH_PATH = Path('/workspace/test/output/placement_sampling/placement_collision_mesh.ply')
OUT_DIR = Path('/workspace/test/output/grasp_placement_pair_collision')
ORIGINAL_COMPUTE_STABILITY = pm.compute_stability


def stability_adapter(*args, **kwargs):
    result = ORIGINAL_COMPUTE_STABILITY(*args, **kwargs)
    if not isinstance(result, tuple):
        return result
    values = np.asarray(result[0], dtype=np.float64).reshape(-1)
    score = float(np.mean(values)) if values.size else 0.0
    print(f'[TEST ADAPTER] support scores: {values.tolist()} -> mean={score:.6f}')
    return (score, *result[1:])


def main() -> int:
    try:
        for path in (GPD_FIXTURE, POSES_PATH, MESH_PATH):
            if not path.is_file():
                raise FileNotFoundError(path)

        OUT_DIR.mkdir(parents=True, exist_ok=True)

        with np.load(GPD_FIXTURE) as data:
            object_points = np.asarray(data['object_points'], dtype=np.float64)
            object_weights = np.asarray(data['object_weights'], dtype=np.float64)
            grasps = np.asarray(data['grasps'], dtype=np.float64)

        pose_groups = [
            np.asarray(group, dtype=np.float64)
            for group in np.load(POSES_PATH, allow_pickle=True)
        ]
        poses = np.vstack([g for g in pose_groups if g.shape[0] > 0])

        mesh = o3d.io.read_triangle_mesh(str(MESH_PATH))
        if mesh.is_empty():
            raise RuntimeError('Collision mesh is empty')

        cfg = get_environment_config()
        variables = cfg['variables']
        orientations = variables['orientations']

        stability_cfg = {
            'rotation_averaging_n': 1,
            'rotation_perturbation_deg': 0.0,
            'rotation_sampling_seed': 0,
            'n_mc_samples': 1000,
            'ground_threshold': float(variables.get('ground_threshold', 0.005)),
        }

        pm.compute_stability = stability_adapter
        try:
            filtered_grasps, _, _, _ = pm.compute_placeability(
                grasps_array=grasps,
                pointcloud=object_points,
                weights=object_weights,
                orientations=orientations,
                plotting=False,
                clearance=float(variables['clearance']),
                calculate_stability=True,
                path=str(OUT_DIR) + '/',
                stability_config=stability_cfg,
            )
        finally:
            pm.compute_stability = ORIGINAL_COMPUTE_STABILITY

        filtered_grasps = np.asarray(filtered_grasps, dtype=np.float64)
        local_grasps = np.stack(
            [GPD_grasp_to_transform(g)[0] for g in filtered_grasps],
            axis=0,
        )

        # Mirror the production pipeline's local X-180 grasp duplication.
        tx180 = np.eye(4, dtype=np.float64)
        tx180[:3, :3] = R.from_euler('x', 180, degrees=True).as_matrix()
        local_grasps = np.concatenate(
            [local_grasps, local_grasps @ tx180],
            axis=0,
        )

        collider = Gripper_CollisionValidation()
        collider.setMesh(mesh)

        pair_transforms = []
        collision_rows = []
        start = time.monotonic()

        for pose_index, pose in enumerate(poses):
            # Exact production relation:
            # temp_grasp_transforms = poses[pose_idx] @ self.grasp_pose_world_list
            transformed = pose @ local_grasps
            flags = np.asarray(
                collider.validate_collisions(
                    Transforms=transformed,
                    plotting=False,
                ),
                dtype=bool,
            )

            if flags.shape != (local_grasps.shape[0],):
                raise RuntimeError(
                    f'Unexpected flags for pose {pose_index}: {flags.shape}'
                )

            pair_transforms.append(transformed)
            collision_rows.append(flags)
            print(
                f'pose {pose_index}: pairs={flags.size}, '
                f'colliding={int(flags.sum())}, '
                f'collision_free={int((~flags).sum())}'
            )

        pair_transforms = np.stack(pair_transforms, axis=0)
        collision_flags = np.stack(collision_rows, axis=0)
        feasible_mask = ~collision_flags
        elapsed = time.monotonic() - start

        expected = (poses.shape[0], local_grasps.shape[0])
        if collision_flags.shape != expected:
            raise RuntimeError(
                f'Unexpected collision matrix: {collision_flags.shape}, expected {expected}'
            )
        if pair_transforms.shape != (*expected, 4, 4):
            raise RuntimeError(
                f'Unexpected pair transforms: {pair_transforms.shape}'
            )

        out = OUT_DIR / 'grasp_placement_pair_collision_results.npz'
        np.savez_compressed(
            out,
            poses=poses,
            local_grasp_transforms=local_grasps,
            pair_transforms=pair_transforms,
            collision_flags=collision_flags,
            feasible_mask=feasible_mask,
        )

        print('\nResult:')
        print('  placement poses:', poses.shape)
        print('  local grasps after x180 duplication:', local_grasps.shape)
        print('  pair transforms:', pair_transforms.shape)
        print('  collision flags:', collision_flags.shape)
        print('  colliding pairs:', int(collision_flags.sum()))
        print('  collision-free pairs:', int(feasible_mask.sum()))
        print(f'  elapsed: {elapsed:.3f} s')
        print('  saved:', out)
        print('\nUNIP GRASP-PLACEMENT PAIR COLLISION TEST: PASS')
        print('NOTE: source-side table/OBB/collision/reachability filtering is not reproduced in this isolated target-side test.')
        return 0

    except Exception as exc:
        pm.compute_stability = ORIGINAL_COMPUTE_STABILITY
        print(f'\nUNIP GRASP-PLACEMENT PAIR COLLISION TEST: FAIL: {exc}')
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
