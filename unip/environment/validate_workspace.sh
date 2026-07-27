#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"
ISAAC_ROS_WS_ROOT="${ISAAC_ROS_WS_ROOT:-${WORKSPACE_ROOT}/external/IsaacSim-ros_workspaces}"
UNIP_ROS311_OVERLAY_ROOT="${UNIP_ROS311_OVERLAY_ROOT:-${WORKSPACE_ROOT}/external/unip_ros311_ws}"
UNIP_CORE_INSTALL="${UNIP_CORE_INSTALL:-${WORKSPACE_ROOT}/install}"

ROS311_BASE_SETUP="${ROS311_BASE_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/jazzy/jazzy_ws/install/local_setup.bash}"
ROS311_ISAAC_SETUP="${ROS311_ISAAC_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/jazzy/isaac_sim_ros_ws/install/local_setup.bash}"
ROS311_OVERLAY_SETUP="${ROS311_OVERLAY_SETUP:-${UNIP_ROS311_OVERLAY_ROOT}/install/local_setup.bash}"
UNIP_CORE_SETUP="${UNIP_CORE_SETUP:-${UNIP_CORE_INSTALL}/local_setup.bash}"

FAIL_COUNT=0
WARN_COUNT=0

pass(){ printf '  [PASS] %s\n' "$*"; }
warn(){ WARN_COUNT=$((WARN_COUNT+1)); printf '  [WARN] %s\n' "$*" >&2; }
fail(){ FAIL_COUNT=$((FAIL_COUNT+1)); printf '  [FAIL] %s\n' "$*" >&2; }
section(){ printf '\n============================================================\n%s\n============================================================\n' "$1"; }

source_stack() {
    section "W1 — Source verified ROS311 stack"
    local setup
    set +u
    for setup in         "$ROS311_BASE_SETUP"         "$ROS311_ISAAC_SETUP"         "$ROS311_OVERLAY_SETUP"         "$UNIP_CORE_SETUP"
    do
        if [[ -f "$setup" ]]; then
            source "$setup"
            pass "Sourced: $setup"
        else
            fail "Required setup missing: $setup"
        fi
    done
    set -u
}

runtime_identity() {
    section "W2 — Runtime identity / contamination"
    "$PYTHON_BIN" - <<'PY'
import sys
print("  Python:", sys.version.split()[0])
print("  Executable:", sys.executable)
assert sys.version_info[:2] == (3, 11), sys.version
bad = [p for p in sys.path if "python3.12" in p]
if bad:
    raise SystemExit("Python 3.12 contamination: " + repr(bad))
PY
    pass "Isaac Python 3.11 contract holds."

    if printf '%s' "${AMENT_PREFIX_PATH:-}" | grep -q '/opt/ros/jazzy'; then
        fail "/opt/ros/jazzy contamination detected."
    else
        pass "No /opt/ros/jazzy prefix in AMENT_PREFIX_PATH."
    fi

    if printf '%s' "${PYTHONPATH:-}" | grep -q 'python3\.12'; then
        fail "Python 3.12 path detected in PYTHONPATH."
    else
        pass "No Python 3.12 path detected in PYTHONPATH."
    fi

    if command -v colcon >/dev/null 2>&1; then
        printf '  system colcon: %s\n' "$(command -v colcon)"
        printf '  shebang      : %s\n' "$(head -n 1 "$(command -v colcon)" 2>/dev/null || true)"
        warn "System colcon is informational only; do not use it for UniP core builds."
    fi
}

package_discovery() {
    section "W3 — Ament package discovery"
    set +e
    "$PYTHON_BIN" - <<'PY'
from ament_index_python.packages import get_package_prefix, PackageNotFoundError
required = [
    "rclpy","rclcpp","sensor_msgs","sensor_msgs_py","tf2","tf2_ros","tf2_ros_py",
    "tf2_eigen","tf2_geometry_msgs","cv_bridge","control_msgs","trajectory_msgs",
    "moveit_msgs","pcl_conversions",
    "gpd_ros_messages","gpd_ros","generate_motion_msgs","placeability_scoring",
]
missing=[]
for pkg in required:
    try:
        print(f"  [PASS] {pkg:<24} {get_package_prefix(pkg)}")
    except PackageNotFoundError:
        print(f"  [MISS] {pkg}")
        missing.append(pkg)
raise SystemExit(0 if not missing else 21)
PY
    rc=$?
    set -e
    [[ "$rc" -eq 0 ]] && pass "All required ROS packages are discoverable." || fail "Required ROS package discovery failed."
}

install_artifact() {
    section "W4 — UniP core install artifact"
    [[ -f "$UNIP_CORE_SETUP" ]] && pass "Core local_setup.bash exists." || fail "Core local_setup.bash missing."
    local idx="${UNIP_CORE_INSTALL}/share/ament_index/resource_index/packages"
    local pkg
    for pkg in gpd_ros_messages gpd_ros generate_motion_msgs placeability_scoring; do
        [[ -e "${idx}/${pkg}" ]] && pass "Package marker exists: $pkg" || fail "Package marker missing: $pkg"
    done
    local exe="${UNIP_CORE_INSTALL}/lib/gpd_ros/detect_grasps"
    [[ -x "$exe" ]] && pass "gpd_ros executable exists: $exe" || fail "gpd_ros executable missing: $exe"
}

python_smoke() {
    section "W5 — Isaac Python import smoke tests"
    set +e
    "$PYTHON_BIN" - <<'PY'
import importlib
tests = [
    "placeability_scoring","gpd_ros_messages",
    "rclpy","sensor_msgs","sensor_msgs_py","std_msgs","geometry_msgs","tf2_ros",
    "cv_bridge","control_msgs","trajectory_msgs","builtin_interfaces","moveit_msgs",
    "numpy","scipy","open3d","matplotlib","pandas","tqdm","klampt","pyfqmr",
    "shapely","toppra","torch",
]
failed=[]
for name in tests:
    try:
        m=importlib.import_module(name)
        print(f"  {name:<24} PASS  {getattr(m,'__file__',None) or ''}")
    except Exception as exc:
        failed.append(name)
        print(f"  {name:<24} FAIL ({type(exc).__name__}: {exc})")
raise SystemExit(0 if not failed else 31)
PY
    rc=$?
    set -e
    [[ "$rc" -eq 0 ]] && pass "All required Python imports passed." || fail "One or more Python imports failed."
}

native_gpd() {
    section "W6 — Native GPD linkage"
    libgpd_entry="$(
        ldconfig -p 2>/dev/null \
            | grep 'libgpd\.so' \
            | head -n 1 \
            || true
    )"

    if [[ -n "$libgpd_entry" ]]; then
        pass "libgpd is discoverable."
        printf '        %s\n' "$libgpd_entry"
    else
        fail "libgpd is not discoverable."
    fi
    [[ -f /usr/local/include/gpd/grasp_detector.h ]] && pass "Native GPD header exists." || fail "Native GPD header missing."
}

summary() {
    section "Workspace Validation Summary"
    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"
    if [[ "$FAIL_COUNT" -gt 0 ]]; then
        printf '\nRESULT: FAIL [RUNTIME/SETUP]\n'
        return 1
    elif [[ "$WARN_COUNT" -gt 0 ]]; then
        printf '\nRESULT: PASS WITH WARNINGS\n'
    else
        printf '\nRESULT: PASS\n'
    fi
}

main() {
    printf '========================================================================\n'
    printf 'UniP ROS311 Workspace Validation\n'
    printf '========================================================================\n'
    source_stack
    runtime_identity
    package_discovery
    install_artifact
    python_smoke
    native_gpd
    summary
}
main "$@"
