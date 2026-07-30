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


BOOST_PYTHON_LIB="/usr/local/lib/libboost_python311.so.1.83.0"

[[ -f "$BOOST_PYTHON_LIB" ]] || {
    echo "ERROR: missing $BOOST_PYTHON_LIB" >&2
    exit 1
}

CV_BRIDGE_SO="$(find \
  /workspace/external/unip_ros311_ws/install \
  -name 'cv_bridge_boost*.so' \
  | head -n 1)"

[[ -n "$CV_BRIDGE_SO" ]] || {
    echo "ERROR: cv_bridge_boost.so not found" >&2
    exit 1
}

if ldd "$CV_BRIDGE_SO" | grep -q 'not found'; then
    echo "ERROR: unresolved cv_bridge native dependencies" >&2
    ldd "$CV_BRIDGE_SO"
    exit 1
fi

/isaac-sim/python.sh - <<'PY'
from cv_bridge.boost.cv_bridge_boost import getCvType

assert getCvType("rgb8") >= 0
assert getCvType("32FC1") >= 0

print("cv_bridge native extension: PASS")
PY