#!/usr/bin/env bash
set -Eeuo pipefail

ISAAC_ROS_WS_ROOT="${ISAAC_ROS_WS_ROOT:-/workspace/external/IsaacSim-ros_workspaces}"
OVERLAY_ROOT="${UNIP_ROS311_OVERLAY_ROOT:-/workspace/external/unip_ros311_ws}"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"
ROS311_BASE_SETUP="${ROS311_BASE_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/jazzy/jazzy_ws/install/local_setup.bash}"
ROS311_ISAAC_SETUP="${ROS311_ISAAC_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/jazzy/isaac_sim_ros_ws/install/local_setup.bash}"
OVERLAY_SETUP="${OVERLAY_ROOT}/install/local_setup.bash"

[[ -f "$ROS311_BASE_SETUP" ]]
[[ -f "$ROS311_ISAAC_SETUP" ]]
[[ -f "$OVERLAY_SETUP" ]]

set +u
source "$ROS311_BASE_SETUP"
source "$ROS311_ISAAC_SETUP"
source "$OVERLAY_SETUP"
set -u

"$PYTHON_BIN" - <<'PY'
import sys
from ament_index_python.packages import get_package_prefix

assert sys.version_info[:2] == (3, 11), sys.version
print(f"[PASS] Isaac Python {sys.version.split()[0]}")

for pkg in (
    "rclpy",
    "rclcpp",
    "sensor_msgs",
    "sensor_msgs_py",
    "tf2",
    "tf2_ros",
    "tf2_ros_py",
    "cv_bridge",
    "control_msgs",
    "trajectory_msgs",
    "moveit_msgs",
):
    print(f"[PASS] {pkg:<20} {get_package_prefix(pkg)}")

for module in (
    "rclpy",
    "sensor_msgs",
    "sensor_msgs_py",
    "tf2_ros",
    "cv_bridge",
    "control_msgs",
    "trajectory_msgs",
    "moveit_msgs",
):
    __import__(module)
    print(f"[PASS] import {module}")

bad = [p for p in sys.path if "python3.12" in p]
if bad:
    raise SystemExit("Python 3.12 contamination: " + repr(bad))
print("[PASS] No Python 3.12 path in Isaac Python sys.path")
PY

if printf '%s' "${AMENT_PREFIX_PATH:-}" | grep -q '/opt/ros/jazzy'; then
  echo "[FAIL] /opt/ros/jazzy contamination detected" >&2
  exit 1
fi

echo "[PASS] No /opt/ros/jazzy in AMENT_PREFIX_PATH"
echo "[PASS] UniP ROS311 overlay validation completed."
