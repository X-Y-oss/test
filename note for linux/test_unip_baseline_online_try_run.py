#!/usr/bin/env python3
"""
Online Isaac Sim try-run for the existing UniP baseline.

This wrapper:
- forces online Isaac Sim mode at runtime;
- keeps the original UniP pipeline logic;
- allows the baseline camera-view motions;
- uses real ROS camera, joint-state, and TF data;
- suppresses only the final pick-and-place trajectory transmission;
- applies compatibility patches only at runtime, without modifying
  environment_config.py or the baseline source files.
"""

from __future__ import annotations

import copy
import importlib
import sys
import time
import traceback
from pathlib import Path

from isaacsim import SimulationApp


simulation_app = SimulationApp({"headless": True})


import numpy as np
import rclpy
import tf2_ros
from rclpy.duration import Duration
from scipy.spatial.transform import Rotation as R
from sensor_msgs.msg import JointState


PACKAGE_SRC = Path("/workspace/src/placeability_scoring")
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))


import placeability_scoring.UP4_Pipeline_curobo as baseline_module


grasp_recon_module = importlib.import_module(
    "placeability_scoring.mapping.GraspingAreaReconstruction_Interface"
)
place_recon_module = importlib.import_module(
    "placeability_scoring.mapping.PlacingAreaReconstruction_Interface"
)
offline_grasp_recon_module = importlib.import_module(
    "placeability_scoring.mapping.Offline_GraspingAreaReconstruction"
)


_original_get_pipeline_config = baseline_module.get_pipeline_config
_original_get_environment_config = baseline_module.get_environment_config
_original_grasp_reconstruction = grasp_recon_module.Reconstruction
_original_place_reconstruction = place_recon_module.Reconstruction
_original_filter_object = offline_grasp_recon_module.filter_object

TRY_RUN_BLOCK_COUNT = 8000
POST_MOTION_SETTLE_TIME = 2.0

def make_try_run_reconstruction(original_cls, label: str):
    def factory(*args, **kwargs):
        original_block_count = kwargs.get("block_count")
        requested_block_count = (
            int(original_block_count)
            if original_block_count is not None
            else TRY_RUN_BLOCK_COUNT
        )
        kwargs["block_count"] = min(
            requested_block_count,
            TRY_RUN_BLOCK_COUNT,
        )

        print(
            f"\n[TRY-RUN MEMORY OVERRIDE: {label}]"
            f"\n  original block_count: {original_block_count}"
            f"\n  try-run block_count:  {kwargs['block_count']}\n",
            flush=True,
        )
        return original_cls(*args, **kwargs)

    return factory


grasp_recon_module.Reconstruction = make_try_run_reconstruction(
    _original_grasp_reconstruction,
    "grasp reconstruction",
)
place_recon_module.Reconstruction = make_try_run_reconstruction(
    _original_place_reconstruction,
    "place reconstruction",
)


# def get_try_run_environment_config():
#     cfg = copy.deepcopy(_original_get_environment_config())

#     cfg.setdefault("system", {})
#     cfg["system"]["robot_file"] = "ur5e_robotiq_2f_140.yml"

#     sim_cfg = cfg["simulation"]
#     topics = sim_cfg["topics"]
#     camera_links = sim_cfg["camera_links"]

#     topics["static_camera_rgb_topic"] = topics["wrist_camera_rgb_topic"]
#     topics["static_camera_depth_topic"] = topics["wrist_camera_depth_topic"]
#     topics["static_camera_camera_info_topic"] = (
#         topics["wrist_camera_camera_info_topic"]
#     )
#     camera_links["static"] = camera_links["wrist"]

#     print(
#         "\n[TRY-RUN COMPATIBILITY OVERRIDES]"
#         "\n  robot_file: ur5e_robotiq_2f_140.yml"
#         "\n  static RGB-D stream: reused wrist RGB-D stream"
#         "\n  static camera frame: reused wrist camera frame"
#         f"\n  reconstruction block_count: {TRY_RUN_BLOCK_COUNT}\n",
#         flush=True,
#     )

#     return cfg

############################only use the first viewpoint#################
def get_try_run_environment_config():
    cfg = copy.deepcopy(_original_get_environment_config())

    cfg.setdefault("variables", {})
    cfg["variables"]["object_area"] = [
        0.10, 0.22,
        0.26, 0.38,
    ]

    print(
        "  object_area override: "
        f"{cfg['variables']['object_area']}",
        flush=True,
    )

    cfg.setdefault("system", {})
    cfg["system"]["robot_file"] = "ur5e_robotiq_2f_140.yml"

    sim_cfg = cfg["simulation"]
    topics = sim_cfg["topics"]
    camera_links = sim_cfg["camera_links"]

    topics["static_camera_rgb_topic"] = topics["wrist_camera_rgb_topic"]
    topics["static_camera_depth_topic"] = topics["wrist_camera_depth_topic"]
    topics["static_camera_camera_info_topic"] = (
        topics["wrist_camera_camera_info_topic"]
    )
    camera_links["static"] = camera_links["wrist"]

    # Smoke-test override: retain only the viewpoint that is reachable
    # in the current Isaac Sim / CuRobo setup.
    original_grasp_views = copy.deepcopy(
        cfg["points_of_interest_grasping"]
    )
    cfg["points_of_interest_grasping"] = [
        original_grasp_views[0]
    ]

    print(
        "\n[TRY-RUN COMPATIBILITY OVERRIDES]"
        "\n  robot_file: ur5e_robotiq_2f_140.yml"
        "\n  static RGB-D stream: reused wrist RGB-D stream"
        "\n  static camera frame: reused wrist camera frame"
        f"\n  reconstruction block_count: {TRY_RUN_BLOCK_COUNT}"
        "\n  grasp viewpoints: first reachable pose only\n",
        flush=True,
    )

    return cfg

def get_try_run_pipeline_config():
    cfg = copy.deepcopy(_original_get_pipeline_config())
    runtime = cfg.setdefault("runtime", {})
    runtime["online"] = True
    runtime["recalculate_grasps"] = True
    runtime["recalculate_placeposes"] = True
    return cfg


def lookup_transform_without_nested_spin(self, source: str = ""):
    try:
        transform = self.tf_buffer.lookup_transform(
            "world",
            source,
            rclpy.time.Time(),
            timeout=Duration(seconds=0.2),
        )
    except (
        tf2_ros.LookupException,
        tf2_ros.ConnectivityException,
        tf2_ros.ExtrapolationException,
    ) as exc:
        self.node.get_logger().warning(
            f"Buffered TF world <- {source} is not ready: {exc}"
        )
        return None

    t = transform.transform.translation
    q = transform.transform.rotation
    rotation = R.from_quat([q.x, q.y, q.z, q.w]).as_matrix()
    rotation = rotation @ np.diag([1.0, -1.0, 1.0])
    rotation = rotation @ np.diag([-1.0, 1.0, 1.0])

    matrix = np.eye(4, dtype=float)
    matrix[:3, :3] = rotation
    matrix[:3, 3] = [t.x, t.y, t.z]

    print(
        f"\nBuffered camera transform world <- {source}:"
        f"\n{matrix}",
        flush=True,
    )
    return matrix


grasp_recon_module.GraspingAreaReconstruction_Interface.lookup_transform = (
    lookup_transform_without_nested_spin
)
place_recon_module.PlacingAreaReconstruction_Interface.lookup_transform = (
    lookup_transform_without_nested_spin
)

def update_map_static_try_run(self):
    print(
        "\n[TRY-RUN STATIC TSDF]"
        "\n  static stream is the wrist optical stream"
        "\n  using direct optical-frame TF"
        "\n  skipping legacy T_static_cam.npy",
        flush=True,
    )

    self.reconstruction.update_vbg(
        depth=self.static_camera_depth_image_raw,
        intrinsic=self.static_camera_intrinsics[:3, :3],
        pose=self.static_camera_pose,
        color=self.static_camera_color_image_raw,
    )


grasp_recon_module.GraspingAreaReconstruction_Interface.update_map_static = (
    update_map_static_try_run
)


def update_map_wrist_try_run(self):
    pose = self.wrist_camera_pose

    print(
        "\n[TRY-RUN WRIST TSDF]"
        "\n  using direct optical-frame TF"
        "\n  skipping legacy T_wrist_cam.npy",
        flush=True,
    )

    self.reconstruction.update_vbg(
        depth=self.wrist_camera_depth_image_raw,
        intrinsic=self.wrist_camera_intrinsics[:3, :3],
        pose=pose,
        color=self.wrist_camera_color_image_raw,
    )


grasp_recon_module.GraspingAreaReconstruction_Interface.update_map_wrist = (
    update_map_wrist_try_run
)


def filter_object_with_debug(
    pointcloud,
    weights,
    plotting=False,
    table_height=0.0,
    object_area=None,
    *args,
    **kwargs,
):
    if hasattr(pointcloud, "points"):
        points = np.asarray(pointcloud.points)
        pointcloud_type = type(pointcloud).__name__
    else:
        points = np.asarray(pointcloud)
        pointcloud_type = type(pointcloud).__name__

    weights_array = np.asarray(weights)

    print(
        "\n[TRY-RUN OBJECT FILTER DEBUG]"
        f"\n  pointcloud type: {pointcloud_type}"
        f"\n  point shape: {points.shape}"
        f"\n  weights shape: {weights_array.shape}"
        f"\n  object_area: {object_area}"
        f"\n  table_height: {table_height}",
        flush=True,
    )

    if points.ndim != 2 or points.shape[1] < 3 or len(points) == 0:
        print(
            "  cloud is empty or malformed",
            flush=True,
        )
    else:
        xyz = points[:, :3]

        print(
            f"  cloud min: {xyz.min(axis=0)}"
            f"\n  cloud max: {xyz.max(axis=0)}",
            flush=True,
        )

        xy_mask = (
            (xyz[:, 0] >= object_area[0])
            & (xyz[:, 0] <= object_area[1])
            & (xyz[:, 1] >= object_area[2])
            & (xyz[:, 1] <= object_area[3])
        )

        object_crop_mask = (
            xy_mask
            & (xyz[:, 2] >= table_height)
            & (xyz[:, 2] <= table_height + 0.4)
        )

        print(
            f"  points inside XY object area: {int(xy_mask.sum())}"
            f"\n  points inside full XYZ crop: "
            f"{int(object_crop_mask.sum())}",
            flush=True,
        )

        if xy_mask.any():
            xy_points = xyz[xy_mask]

            print(
                f"  Z range inside XY area: "
                f"[{xy_points[:, 2].min():.6f}, "
                f"{xy_points[:, 2].max():.6f}]",
                flush=True,
            )

        np.save(
            "/workspace/test/output/"
            "try_run_grasp_environment_points.npy",
            xyz,
        )

    return _original_filter_object(
        pointcloud,
        weights,
        plotting=plotting,
        table_height=table_height,
        object_area=object_area,
        *args,
        **kwargs,
    )


offline_grasp_recon_module.filter_object = filter_object_with_debug
baseline_module.filter_object = filter_object_with_debug

baseline_module.get_pipeline_config = get_try_run_pipeline_config
baseline_module.get_environment_config = get_try_run_environment_config


class BaselineOnlineTryRun(baseline_module.UP4_Pipeline):
    """Existing baseline with runtime-only compatibility adaptations."""

    def _get_joint_command_publisher(self):
        if not hasattr(self, "_joint_command_pub"):
            self._joint_command_pub = self.create_publisher(
                JointState,
                "/joint_command",
                10,
            )
            print(
                "TRY-RUN CAMERA MOTION: created /joint_command publisher",
                flush=True,
            )
            time.sleep(1.0)

        return self._joint_command_pub

    def _print_post_motion_camera_tf(self):
        camera_frame = "wrist_camera_color_optical_frame"

        try:
            transform = self.tf_buffer.lookup_transform(
                "world",
                camera_frame,
                rclpy.time.Time(),
                timeout=Duration(seconds=1.0),
            )

            t = transform.transform.translation
            q = transform.transform.rotation

            print(
                "\n[TRY-RUN POST-MOTION CAMERA TF]"
                f"\n  frame: world <- {camera_frame}"
                f"\n  translation: [{t.x:.6f}, {t.y:.6f}, {t.z:.6f}]"
                f"\n  quaternion xyzw: "
                f"[{q.x:.6f}, {q.y:.6f}, {q.z:.6f}, {q.w:.6f}]",
                flush=True,
            )

        except (
            tf2_ros.LookupException,
            tf2_ros.ConnectivityException,
            tf2_ros.ExtrapolationException,
        ) as exc:
            print(
                "\n[TRY-RUN POST-MOTION CAMERA TF]"
                f"\n  unavailable: {exc}",
                flush=True,
            )

    def joint_motion_movements(
        self,
        joints,
        export_usd=False,
        wait=True,
    ):
        """
        Plan with the original CuRobo interface and publish the resulting
        camera-view trajectory to Isaac Sim through /joint_command.
        """
        target = np.asarray(joints, dtype=float)

        print(
            "\n"
            "============================================================\n"
            "TRY-RUN CAMERA MOTION\n"
            f"target joints:\n{target}\n"
            f"export_usd: {export_usd}\n"
            f"wait: {wait}\n"
            "planning started\n"
            "============================================================",
            flush=True,
        )

        planning_start = time.time()

        trajectory, seg_end_indices = self.arm_mover.plan(
            pose_list=[target],
            export_usd=export_usd,
            segment_modes=(0,),
        )

        planning_time = time.time() - planning_start

        print(
            "\nTRY-RUN CAMERA MOTION: planning returned"
            f"\n  planning time: {planning_time:.3f} s"
            f"\n  trajectory count: {len(trajectory)}"
            f"\n  segment end indices: {seg_end_indices}",
            flush=True,
        )

        if len(trajectory) <= 0:
            raise RuntimeError(
                "CuRobo returned no camera-motion trajectory."
            )

        first_trajectory = np.asarray(
            trajectory[0],
            dtype=float,
        )

        if first_trajectory.ndim != 2:
            raise RuntimeError(
                "Expected trajectory shape (T, 6), "
                f"got {first_trajectory.shape}."
            )

        joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ]

        if first_trajectory.shape[1] != len(joint_names):
            raise RuntimeError(
                "Trajectory joint dimension does not match UR5e joints: "
                f"{first_trajectory.shape}."
            )

        print(
            "\nTRY-RUN CAMERA MOTION: trajectory ready"
            f"\n  trajectory shape: {first_trajectory.shape}"
            f"\n  final target error: "
            f"{np.linalg.norm(first_trajectory[-1] - target):.6f} rad",
            flush=True,
        )

        publisher = self._get_joint_command_publisher()
        publish_period = 0.02  # 50 Hz

        print(
            "\nTRY-RUN CAMERA MOTION: publishing to /joint_command"
            f"\n  points: {len(first_trajectory)}"
            f"\n  frequency: {1.0 / publish_period:.1f} Hz"
            f"\n  nominal duration: "
            f"{len(first_trajectory) * publish_period:.3f} s",
            flush=True,
        )

        send_start = time.time()

        for point_index, joint_positions in enumerate(first_trajectory):
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = joint_names
            msg.position = joint_positions.tolist()

            publisher.publish(msg)

            if point_index == 0:
                print(
                    "TRY-RUN CAMERA MOTION: first command published",
                    flush=True,
                )

            time.sleep(publish_period)

        print(
            "\nTRY-RUN CAMERA MOTION: trajectory publication finished"
            f"\n  points published: {len(first_trajectory)}"
            f"\n  elapsed time: {time.time() - send_start:.3f} s",
            flush=True,
        )

        if wait:
            print(
                f"TRY-RUN CAMERA MOTION: waiting "
                f"{POST_MOTION_SETTLE_TIME:.1f} s for articulation/TF update",
                flush=True,
            )
            time.sleep(POST_MOTION_SETTLE_TIME)

        self._print_post_motion_camera_tf()

        print(
            "TRY-RUN CAMERA MOTION: movement adapter returned",
            flush=True,
        )

    def lookup_transform(self, source: str = "", target: str = "world"):
        requested_target = target
        fallback_target = (
            "base_link" if requested_target == "ur5e_base_link" else None
        )
        warned_fallback = False

        while rclpy.ok():
            targets = [requested_target]
            if fallback_target is not None:
                targets.append(fallback_target)

            for candidate_target in targets:
                try:
                    transform = self.tf_buffer.lookup_transform(
                        candidate_target,
                        source,
                        rclpy.time.Time(),
                        timeout=Duration(seconds=0.5),
                    )

                    if candidate_target != requested_target and not warned_fallback:
                        self.get_logger().warning(
                            "TF compatibility fallback: "
                            f"requested target '{requested_target}' was unavailable; "
                            f"using '{candidate_target}'."
                        )
                        warned_fallback = True

                    t = transform.transform.translation
                    q = transform.transform.rotation
                    rotation = R.from_quat(
                        [q.x, q.y, q.z, q.w]
                    ).as_matrix()

                    matrix = np.eye(4, dtype=float)
                    matrix[:3, :3] = rotation
                    matrix[:3, 3] = [t.x, t.y, t.z]

                    print(
                        "\nResolved baseline transform:"
                        f"\n  source frame: {source}"
                        f"\n  target frame: {candidate_target}"
                        f"\n  matrix:\n{matrix}",
                        flush=True,
                    )
                    return matrix

                except (
                    tf2_ros.LookupException,
                    tf2_ros.ConnectivityException,
                    tf2_ros.ExtrapolationException,
                ):
                    continue

            self.get_logger().warning(
                "Waiting for TF from "
                f"'{source}' to '{requested_target}'"
                + (
                    f" or fallback '{fallback_target}'"
                    if fallback_target
                    else ""
                )
            )
            time.sleep(0.2)

        raise RuntimeError("ROS shut down while waiting for TF")

    def execution(self):
        print(
            "\n"
            "============================================================\n"
            "BASELINE TRY-RUN: entering original execution() in PLAN-ONLY mode\n"
            "Camera/reconstruction motions before this point were online.\n"
            "Final grasp/place/release trajectories will NOT be transmitted.\n"
            "============================================================\n",
            flush=True,
        )

        original_online = self.online
        self.online = False
        try:
            result = super().execution()
        finally:
            self.online = original_online

        print(
            "\n"
            "============================================================\n"
            "BASELINE TRY-RUN: original execution() returned\n"
            "No final pick-and-place trajectory was sent.\n"
            "============================================================\n",
            flush=True,
        )
        return result


def main(args=None) -> int:
    rclpy.init(args=args)
    node = None

    try:
        print(
            "\n"
            "UNIP ONLINE BASELINE TRY-RUN\n"
            "  simulation:              True\n"
            "  online perception:       True\n"
            "  recalculate grasps:      True\n"
            "  recalculate placements:  True\n"
            "  camera-view arm motion:  enabled by original baseline\n"
            "  final pick/place motion: disabled\n"
            f"  TSDF block_count:        {TRY_RUN_BLOCK_COUNT}\n",
            flush=True,
        )

        node = BaselineOnlineTryRun(simulation=True)
        print("\nUNIP ONLINE BASELINE TRY-RUN: PIPELINE RETURNED", flush=True)
        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user.", flush=True)
        return 130

    except BaseException as exc:
        print(f"\nUNIP ONLINE BASELINE TRY-RUN: FAIL: {exc}", flush=True)
        traceback.print_exc()
        return 1

    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    exit_code = 1
    try:
        exit_code = main()
    finally:
        simulation_app.close()

    raise SystemExit(exit_code)
