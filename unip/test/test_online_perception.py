#!/usr/bin/env python3

import sys
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from sensor_msgs.msg import CameraInfo, Image
from tf2_ros import Buffer, TransformException, TransformListener


# Allow importing the source package without rebuilding the workspace.
PLACEABILITY_SRC = Path(
    "/workspace/src/placeability_scoring"
)

if str(PLACEABILITY_SRC) not in sys.path:
    sys.path.insert(0, str(PLACEABILITY_SRC))

from placeability_scoring.environment_config import get_environment_config


class OnlinePerceptionSmokeTest(Node):
    def __init__(self) -> None:
        super().__init__("online_perception_smoke_test")

        config = get_environment_config()
        sim_config = config["simulation"]

        topics = sim_config["topics"]
        camera_links = sim_config["camera_links"]

        self.base_frame = sim_config.get("base_link", "base_link")
        self.world_frame = "world"
        self.camera_frame = camera_links["wrist"]

        self.rgb_received = False
        self.depth_received = False
        self.camera_info_received = False

        self.create_subscription(
            Image,
            topics["wrist_camera_rgb_topic"],
            self._rgb_callback,
            10,
        )

        self.create_subscription(
            Image,
            topics["wrist_camera_depth_topic"],
            self._depth_callback,
            10,
        )

        self.create_subscription(
            CameraInfo,
            topics["wrist_camera_camera_info_topic"],
            self._camera_info_callback,
            10,
        )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self,
        )

        self.get_logger().info(
            f"RGB topic: "
            f"{topics['wrist_camera_rgb_topic']}"
        )
        self.get_logger().info(
            f"Depth topic: "
            f"{topics['wrist_camera_depth_topic']}"
        )
        self.get_logger().info(
            f"CameraInfo topic: "
            f"{topics['wrist_camera_camera_info_topic']}"
        )
        self.get_logger().info(
            f"Base frame: {self.base_frame}"
        )
        self.get_logger().info(
            f"Camera frame: {self.camera_frame}"
        )

    def _rgb_callback(self, msg: Image) -> None:
        if self.rgb_received:
            return

        self.rgb_received = True
        self.get_logger().info(
            "RGB PASS: "
            f"{msg.width}x{msg.height}, "
            f"encoding={msg.encoding}, "
            f"frame={msg.header.frame_id}"
        )

    def _depth_callback(self, msg: Image) -> None:
        if self.depth_received:
            return

        self.depth_received = True
        self.get_logger().info(
            "Depth PASS: "
            f"{msg.width}x{msg.height}, "
            f"encoding={msg.encoding}, "
            f"frame={msg.header.frame_id}"
        )

    def _camera_info_callback(
        self,
        msg: CameraInfo,
    ) -> None:
        if self.camera_info_received:
            return

        self.camera_info_received = True
        self.get_logger().info(
            "CameraInfo PASS: "
            f"{msg.width}x{msg.height}, "
            f"frame={msg.header.frame_id}, "
            f"fx={msg.k[0]:.3f}, "
            f"fy={msg.k[4]:.3f}"
        )

    def check_transform(
        self,
        target_frame: str,
        source_frame: str,
    ) -> bool:
        try:
            if not self.tf_buffer.can_transform(
                target_frame,
                source_frame,
                rclpy.time.Time(),
            ):
                return False

            transform = self.tf_buffer.lookup_transform(
                target_frame,
                source_frame,
                rclpy.time.Time(),
            )

            translation = transform.transform.translation

            self.get_logger().info(
                f"TF PASS: {target_frame} -> {source_frame}, "
                f"translation="
                f"[{translation.x:.3f}, "
                f"{translation.y:.3f}, "
                f"{translation.z:.3f}]"
            )
            return True

        except TransformException as exc:
            self.get_logger().debug(
                f"Waiting for TF "
                f"{target_frame} -> {source_frame}: {exc}"
            )
            return False


def main() -> int:
    rclpy.init()

    node = OnlinePerceptionSmokeTest()

    timeout_seconds = 15.0
    start_time = time.monotonic()

    base_tf_received = False
    camera_tf_received = False

    try:
        while rclpy.ok():
            rclpy.spin_once(
                node,
                timeout_sec=0.1,
            )

            if not base_tf_received:
                base_tf_received = node.check_transform(
                    node.world_frame,
                    node.base_frame,
                )

            if not camera_tf_received:
                camera_tf_received = node.check_transform(
                    node.world_frame,
                    node.camera_frame,
                )

            all_passed = all(
                [
                    node.rgb_received,
                    node.depth_received,
                    node.camera_info_received,
                    base_tf_received,
                    camera_tf_received,
                ]
            )

            if all_passed:
                node.get_logger().info(
                    "ONLINE PERCEPTION SMOKE TEST: PASS"
                )
                return 0

            elapsed = time.monotonic() - start_time

            if elapsed >= timeout_seconds:
                node.get_logger().error(
                    "ONLINE PERCEPTION SMOKE TEST: FAIL"
                )
                node.get_logger().error(
                    f"RGB received: {node.rgb_received}"
                )
                node.get_logger().error(
                    f"Depth received: {node.depth_received}"
                )
                node.get_logger().error(
                    "CameraInfo received: "
                    f"{node.camera_info_received}"
                )
                node.get_logger().error(
                    f"Base TF received: {base_tf_received}"
                )
                node.get_logger().error(
                    f"Camera TF received: {camera_tf_received}"
                )
                return 1

    finally:
        node.destroy_node()
        rclpy.shutdown()

    return 1


if __name__ == "__main__":
    raise SystemExit(main())