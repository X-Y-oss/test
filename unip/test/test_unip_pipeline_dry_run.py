#!/usr/bin/env python3

import sys
import traceback
from isaacsim import SimulationApp


def check(name, callback):
    print(f"\n=== {name} ===")
    result = callback()
    print(f"{name}: PASS")
    return result

def run_checks():
    try:
        check(
            "Environment configuration",
            lambda: __import__(
                "placeability_scoring.environment_config",
                fromlist=["get_environment_config"],
            ),
        )

        from placeability_scoring.environment_config import (
            get_environment_config,
            get_pipeline_config,
        )

        env_cfg = check(
            "Load environment config",
            get_environment_config,
        )

        pipeline_cfg = check(
            "Load pipeline config",
            get_pipeline_config,
        )

        simulation_cfg = env_cfg["simulation"]

        print("\nSimulation topics:")
        for key, value in simulation_cfg["topics"].items():
            print(f"  {key}: {value}")

        print("\nSimulation camera links:")
        for key, value in simulation_cfg["camera_links"].items():
            print(f"  {key}: {value}")

        print(
            "  base_link:",
            simulation_cfg.get("base_link", "base_link"),
        )

        check(
            "Grasping reconstruction import",
            lambda: __import__(
                "placeability_scoring.mapping."
                "GraspingAreaReconstruction_Interface",
                fromlist=["GraspingAreaReconstruction_Interface"],
            ),
        )

        check(
            "Placing reconstruction import",
            lambda: __import__(
                "placeability_scoring.mapping."
                "PlacingAreaReconstruction_Interface",
                fromlist=["PlacingAreaReconstruction_Interface"],
            ),
        )

        check(
            "GPD interface import",
            lambda: __import__(
                "placeability_scoring.grasping.GPD_Interface",
                fromlist=["GPD_Interface"],
            ),
        )

        check(
            "Placeability import",
            lambda: __import__(
                "placeability_scoring.placeability.placeability",
                fromlist=["compute_placeability"],
            ),
        )

        check(
            "Placement sampling import",
            lambda: __import__(
                "placeability_scoring.placing.get_placement_locations",
                fromlist=["get_placement_locations_multiple_orientations"],
            ),
        )

        check(
            "Collision validation import",
            lambda: __import__(
                "placeability_scoring.placeability."
                "Gripper_CollisionValidation",
                fromlist=["Gripper_CollisionValidation"],
            ),
        )

        check(
            "CuRobo planner interface import",
            lambda: __import__(
                "placeability_scoring.planning.UR5e_Interface_curobo",
                fromlist=["UR5e_Interface"],
            ),
        )

        check(
            "Main pipeline module import",
            lambda: __import__(
                "placeability_scoring.UP4_Pipeline_curobo",
                fromlist=["UP4_Pipeline"],
            ),
        )

        print("\nUNIP PIPELINE DRY-RUN: PASS")
        return 0

    except Exception as exc:
        print(
            f"\nUNIP PIPELINE DRY-RUN: FAIL\n"
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        traceback.print_exc()
        return 1



def main():
    simulation_app = None

    try:
        simulation_app = SimulationApp({"headless": True})
        return run_checks()

    except Exception as exc:
        print(
            f"\nUNIP PIPELINE DRY-RUN: FAIL\n"
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        traceback.print_exc()
        return 1

    finally:
        if simulation_app is not None:
            simulation_app.close()


if __name__ == "__main__":
    raise SystemExit(main())