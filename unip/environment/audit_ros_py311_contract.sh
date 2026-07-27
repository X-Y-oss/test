#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# Audit the ROS 2 Jazzy / Python 3.11 contract used by UniP.
#
# This script is READ-ONLY. It does not install packages or modify the workspace.
#
# Purpose:
#   1. Source NVIDIA's Isaac-compatible Jazzy/Python-3.11 workspaces.
#   2. Check which ROS packages needed by UniP are already present there.
#   3. Check which Python ROS modules are importable from Isaac Python 3.11.
#   4. Show which colcon/rosdep executables currently belong to system Python
#      versus an eventual Python-3.11 tooling environment.
#
# The output tells us exactly which ROS packages need a Python-3.11 source build,
# instead of blindly letting rosdep install Ubuntu Jazzy/Python-3.12 packages.
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"
ROS_DISTRO_TARGET="${ROS_DISTRO_TARGET:-jazzy}"
ISAAC_ROS_WS_ROOT="${ISAAC_ROS_WS_ROOT:-${WORKSPACE_ROOT}/external/IsaacSim-ros_workspaces}"

ROS311_BASE_SETUP="${ROS311_BASE_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO_TARGET}/${ROS_DISTRO_TARGET}_ws/install/local_setup.bash}"
ROS311_ISAAC_SETUP="${ROS311_ISAAC_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO_TARGET}/isaac_sim_ros_ws/install/local_setup.bash}"

FAIL_COUNT=0
WARN_COUNT=0

pass() { printf '  [PASS] %s\n' "$*"; }
warn() { WARN_COUNT=$((WARN_COUNT + 1)); printf '  [WARN] %s\n' "$*" >&2; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf '  [FAIL] %s\n' "$*" >&2; }

section() {
    printf '\n========================================================================\n'
    printf '%s\n' "$1"
    printf '========================================================================\n'
}

source_ros311() {
    [[ -f "$ROS311_BASE_SETUP" ]] ||
        fail "Missing base ROS 3.11 setup: $ROS311_BASE_SETUP"
    [[ -f "$ROS311_ISAAC_SETUP" ]] ||
        fail "Missing Isaac ROS 3.11 setup: $ROS311_ISAAC_SETUP"

    [[ "$FAIL_COUNT" -eq 0 ]] || return 1

    set +u
    # shellcheck disable=SC1090
    source "$ROS311_BASE_SETUP"
    # shellcheck disable=SC1090
    source "$ROS311_ISAAC_SETUP"
    set -u

    return 0
}

check_runtime_identity() {
    section "R0 — Runtime identity"

    printf '  WORKSPACE_ROOT      : %s\n' "$WORKSPACE_ROOT"
    printf '  ISAAC_ROS_WS_ROOT   : %s\n' "$ISAAC_ROS_WS_ROOT"
    printf '  ROS311_BASE_SETUP   : %s\n' "$ROS311_BASE_SETUP"
    printf '  ROS311_ISAAC_SETUP  : %s\n' "$ROS311_ISAAC_SETUP"
    printf '  ROS_DISTRO          : %s\n' "${ROS_DISTRO:-<unset>}"
    printf '  AMENT_PREFIX_PATH   : %s\n' "${AMENT_PREFIX_PATH:-<unset>}"

    if [[ -x "$PYTHON_BIN" ]]; then
        "$PYTHON_BIN" - <<'PY'
import platform
import sys
print("  Isaac Python version :", platform.python_version())
print("  Isaac sys.executable :", sys.executable)
PY
        pass "Isaac Python runtime exists."
    else
        fail "Isaac Python runtime missing: $PYTHON_BIN"
    fi

    printf '  system python3      : %s\n' "$(command -v python3 2>/dev/null || echo '<missing>')"
    python3 --version 2>/dev/null | sed 's/^/  system /' || true
}

check_tooling_identity() {
    section "R1 — Build-tool interpreter identity"

    local tool
    for tool in colcon rosdep ros2; do
        if command -v "$tool" >/dev/null 2>&1; then
            local path
            path="$(command -v "$tool")"
            printf '  %-8s : %s\n' "$tool" "$path"
            if head -n 1 "$path" 2>/dev/null | grep -q '^#!'; then
                printf '             shebang: %s\n' "$(head -n 1 "$path")"
            fi
        else
            printf '  %-8s : <missing>\n' "$tool"
        fi
    done

    if command -v colcon >/dev/null 2>&1; then
        warn "A colcon CLI is present, but its shebang above must be Python 3.11 before we use it for UniP ament_python packages."
    else
        warn "colcon CLI not present."
    fi
}

check_ros_package_prefixes() {
    section "R2 — ROS package availability in sourced Python-3.11 environment"

    # Packages directly required by active UniP manifests/code.
    local packages=(
        ament_cmake
        ament_python
        ament_index_cpp
        rclcpp
        rclpy
        std_msgs
        sensor_msgs
        sensor_msgs_py
        geometry_msgs
        builtin_interfaces
        visualization_msgs
        tf2_ros
        tf2_eigen
        tf2_geometry_msgs
        cv_bridge
        control_msgs
        trajectory_msgs
        moveit_msgs
        pcl_conversions
        launch
        launch_ros
    )

    if ! command -v ros2 >/dev/null 2>&1; then
        fail "ros2 CLI unavailable after sourcing ROS 3.11 workspaces."
        return
    fi

    local pkg
    for pkg in "${packages[@]}"; do
        if ros2 pkg prefix "$pkg" >/dev/null 2>&1; then
            local prefix
            prefix="$(ros2 pkg prefix "$pkg" 2>/dev/null)"
            printf '  [PASS] %-24s %s\n' "$pkg" "$prefix"
        else
            printf '  [MISS] %-24s\n' "$pkg"
        fi
    done
}

check_python_imports() {
    section "R3 — Isaac Python 3.11 ROS imports"

    [[ -x "$PYTHON_BIN" ]] || {
        fail "Cannot run Python import audit."
        return
    }

    set +e
    "$PYTHON_BIN" - <<'PY'
import importlib

modules = [
    "rclpy",
    "std_msgs",
    "sensor_msgs",
    "sensor_msgs_py",
    "geometry_msgs",
    "builtin_interfaces",
    "tf2_ros",
    "cv_bridge",
    "control_msgs",
    "trajectory_msgs",
    "moveit_msgs",
    "launch",
    "launch_ros",
]

failed = []

for name in modules:
    try:
        module = importlib.import_module(name)
    except Exception as exc:
        failed.append(name)
        print(f"  [MISS] {name:<24} {type(exc).__name__}: {exc}")
    else:
        path = getattr(module, "__file__", None)
        print(f"  [PASS] {name:<24} {path or '<namespace/package>'}")

print()
print("  Missing Python ROS modules:", ", ".join(failed) if failed else "<none>")
PY
    local rc=$?
    set -e

    if [[ "$rc" -eq 0 ]]; then
        pass "Python import inventory completed."
    else
        fail "Python import inventory itself failed (exit $rc)."
    fi
}

check_python_search_paths() {
    section "R4 — Python search-path sanity"

    "$PYTHON_BIN" - <<'PY'
import sys

print("  Python search paths containing ROS/workspace-like entries:")
for p in sys.path:
    low = p.lower()
    if "ros" in low or "install" in low or "workspace" in low:
        print("   ", p)
PY

    if printf '%s' "${PYTHONPATH:-}" | grep -q 'python3\.12'; then
        fail "PYTHONPATH contains Python 3.12 path(s)."
    else
        pass "No Python 3.12 path detected in PYTHONPATH."
    fi

    if printf '%s' "${AMENT_PREFIX_PATH:-}" | grep -q '/opt/ros/jazzy'; then
        warn "AMENT_PREFIX_PATH contains /opt/ros/jazzy. Verify that the default Python-3.12 ROS install has not leaked into the Isaac runtime."
    else
        pass "No /opt/ros/jazzy prefix detected in AMENT_PREFIX_PATH."
    fi
}

summary() {
    section "ROS Python-3.11 Contract Audit Summary"

    printf '  Hard failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings      : %s\n' "$WARN_COUNT"

    printf '\nInterpretation:\n'
    printf '  - [PASS] package/import = already available to the Isaac Python-3.11 side.\n'
    printf '  - [MISS] package/import = candidate for explicit Python-3.11 source build.\n'
    printf '  - Do not fix [MISS] entries by blindly installing ros-jazzy-* apt packages.\n'
    printf '    Ubuntu 24.04 Jazzy Python bindings are built for Python 3.12.\n'

    [[ "$FAIL_COUNT" -eq 0 ]]
}

main() {
    printf '========================================================================\n'
    printf 'UniP ROS Jazzy / Python 3.11 Contract Audit\n'
    printf '========================================================================\n'

    source_ros311 || true
    check_runtime_identity
    check_tooling_identity
    check_ros_package_prefixes
    check_python_imports
    check_python_search_paths
    summary
}

main "$@"
