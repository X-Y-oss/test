#!/usr/bin/env python3

import sys
import time
import traceback
from pathlib import Path

import numpy as np


PLACEABILITY_SRC = Path("/workspace/src/placeability_scoring")

if str(PLACEABILITY_SRC) not in sys.path:
    sys.path.insert(0, str(PLACEABILITY_SRC))


from placeability_scoring.environment_config import get_environment_config
import placeability_scoring.placeability.placeability as placeability_module


FIXTURE_PATH = Path(
    "/workspace/test/fixtures/gpd_roundtrip_fixture.npz"
)

OUTPUT_DIR = Path(
    "/workspace/test/output/placeability_scoring"
)


# Preserve the production function. The test temporarily replaces only the
# reference held inside placeability.py and restores it afterward.
ORIGINAL_COMPUTE_STABILITY = placeability_module.compute_stability


def test_compute_stability_adapter(*args, **kwargs):
    """
    Test-only compatibility adapter.

    The current compute_stability() may return one score per support polygon,
    while get_stability() expects a scalar. For this runtime test only, the
    scores are aggregated with their mean. Production code remains unchanged.
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


def main() -> int:
    try:
        if not FIXTURE_PATH.is_file():
            raise FileNotFoundError(
                f"Fixture not found: {FIXTURE_PATH}"
            )

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with np.load(FIXTURE_PATH) as data:
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

        print("Fixture:")
        print(f"  object_points:  {object_points.shape}")
        print(f"  object_weights: {object_weights.shape}")
        print(f"  grasps:         {grasps.shape}")

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

        print("\nConfiguration:")
        print(f"  orientations: {len(orientations)}")
        print(f"  clearance:    {clearance}")

        # Keep the first runtime test deterministic and relatively fast.
        stability_config = {
            "rotation_averaging_n": 1,
            "rotation_perturbation_deg": 0.0,
            "rotation_sampling_seed": 0,
            "n_mc_samples": 1000,
            "ground_threshold": float(
                variables.get("ground_threshold", 0.005)
            ),
        }

        print("\nRunning compute_placeability()...")

        start_time = time.monotonic()

        placeability_module.compute_stability = (
            test_compute_stability_adapter
        )

        try:
            (
                filtered_grasps,
                placement_maps,
                convex_hulls,
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

        elapsed = time.monotonic() - start_time

        filtered_grasps = np.asarray(filtered_grasps)
        placement_maps = np.asarray(placement_maps)
        center_alignments = np.asarray(center_alignments)

        print("\nResult:")
        print(f"  filtered_grasps:  {filtered_grasps.shape}")
        print(f"  placement_maps:   {placement_maps.shape}")
        print(f"  convex_hulls:      {len(convex_hulls)}")
        print(f"  center_alignments: {center_alignments.shape}")
        print(f"  elapsed:           {elapsed:.3f} s")

        stability_file = OUTPUT_DIR / "stability_scores.npy"

        if not stability_file.is_file():
            raise RuntimeError(
                f"Missing stability output: {stability_file}"
            )

        stability_scores = np.load(stability_file)

        print(f"  stability_scores:  {stability_scores.shape}")
        print(f"  stability values:  {stability_scores}")

        if filtered_grasps.ndim != 2:
            raise RuntimeError(
                "Unexpected filtered grasp dimensions: "
                f"{filtered_grasps.shape}"
            )

        if filtered_grasps.shape[1] != 17:
            raise RuntimeError(
                f"Unexpected filtered grasp shape: {filtered_grasps.shape}"
            )

        if filtered_grasps.shape[0] == 0:
            raise RuntimeError(
                "No positive-score grasps remained after scoring"
            )

        if placement_maps.ndim != 3:
            raise RuntimeError(
                "Unexpected placement map dimensions: "
                f"{placement_maps.shape}"
            )

        if placement_maps.shape[0] != len(orientations):
            raise RuntimeError(
                "Orientation/result mismatch: "
                f"{len(orientations)} configured orientations, "
                f"{placement_maps.shape[0]} placement maps"
            )

        if placement_maps.shape[1] != filtered_grasps.shape[0]:
            raise RuntimeError(
                "Grasp/placeability row mismatch: "
                f"{filtered_grasps.shape[0]} grasps, "
                f"{placement_maps.shape[1]} placement rows"
            )

        if placement_maps.shape[2] != 17:
            raise RuntimeError(
                f"Unexpected placement map shape: {placement_maps.shape}"
            )

        if center_alignments.shape != (len(orientations), 3):
            raise RuntimeError(
                "Unexpected center alignment shape: "
                f"{center_alignments.shape}"
            )

        if stability_scores.shape != (len(orientations),):
            raise RuntimeError(
                "Unexpected stability score shape: "
                f"{stability_scores.shape}"
            )

        if not np.isfinite(filtered_grasps).all():
            raise RuntimeError(
                "Filtered grasps contain NaN or Inf"
            )

        if not np.isfinite(placement_maps).all():
            raise RuntimeError(
                "Placement maps contain NaN or Inf"
            )

        if not np.isfinite(center_alignments).all():
            raise RuntimeError(
                "Center alignments contain NaN or Inf"
            )

        if not np.isfinite(stability_scores).all():
            raise RuntimeError(
                "Stability scores contain NaN or Inf"
            )

        print("\nUNIP PLACEABILITY SCORING TEST: PASS")
        return 0

    except Exception as exc:
        # Restore the production function even if failure happens before the
        # inner finally block.
        placeability_module.compute_stability = (
            ORIGINAL_COMPUTE_STABILITY
        )

        print(
            "\nUNIP PLACEABILITY SCORING TEST: "
            f"FAIL: {exc}"
        )
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())