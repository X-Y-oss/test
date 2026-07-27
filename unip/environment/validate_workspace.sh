#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
UNIP_SRC="${UNIP_SRC:-${WORKSPACE_ROOT}/src}"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"
ROS_DISTRO_TARGET="${ROS_DISTRO_TARGET:-jazzy}"
ISAAC_ROS_WS_ROOT="${ISAAC_ROS_WS_ROOT:-${WORKSPACE_ROOT}/external/IsaacSim-ros_workspaces}"
ROS311_BASE_SETUP="${ROS311_BASE_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO_TARGET}/${ROS_DISTRO_TARGET}_ws/install/local_setup.bash}"
ROS311_ISAAC_SETUP="${ROS311_ISAAC_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO_TARGET}/isaac_sim_ros_ws/install/local_setup.bash}"

CORE_PACKAGES=(
    gpd_ros_messages
    gpd_ros
    generate_motion_msgs
    placeability_scoring
)

FAIL_COUNT=0
WARN_COUNT=0

pass() { printf '  [PASS] %s\n' "$*"; }
warn() { WARN_COUNT=$((WARN_COUNT + 1)); printf '  [WARN] %s\n' "$*" >&2; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf '  [FAIL] %s\n' "$*" >&2; }
section() { printf '\n============================================================\n%s\n============================================================\n' "$1"; }

source_ros311() {
    [[ -f "$ROS311_BASE_SETUP" ]] || { fail "Missing base ROS setup."; return 1; }
    [[ -f "$ROS311_ISAAC_SETUP" ]] || { fail "Missing Isaac ROS setup."; return 1; }
    set +u
    source "$ROS311_BASE_SETUP"
    source "$ROS311_ISAAC_SETUP"
    set -u
}

check_layout() {
    section "W1 — Workspace / ROS environment"
    [[ -d "$WORKSPACE_ROOT" ]] && pass "Workspace root exists." || fail "Workspace root missing."
    [[ -d "$UNIP_SRC" ]] && pass "Workspace src exists." || fail "Workspace src missing."
    [[ -x "$PYTHON_BIN" ]] && pass "Isaac Python exists." || fail "Isaac Python missing."
    command -v ros2 >/dev/null 2>&1 && pass "ros2 CLI available." || fail "ros2 CLI unavailable."
    command -v colcon >/dev/null 2>&1 && pass "colcon available." || fail "colcon unavailable."
}

check_rosdep() {
    section "W2 — rosdep core dependency check"

    if ! command -v rosdep >/dev/null 2>&1; then
        warn "rosdep CLI unavailable; dependency check skipped."
        return
    fi

    local paths=()
    local pkg
    for pkg in "${CORE_PACKAGES[@]}"; do
        [[ -f "${UNIP_SRC}/${pkg}/package.xml" ]] && paths+=("${UNIP_SRC}/${pkg}")
    done

    [[ "${#paths[@]}" -gt 0 ]] || { fail "No core package manifests found."; return; }

    set +e
    rosdep check \
        --from-paths "${paths[@]}" \
        --ignore-src \
        --rosdistro "${ROS_DISTRO:-$ROS_DISTRO_TARGET}"
    local rc=$?
    set -e
    [[ "$rc" -eq 0 ]] && pass "rosdep core check passed." || fail "rosdep core check failed."
}

build_workspace() {
    section "W3 — colcon build"
    cd "$WORKSPACE_ROOT"

    set +e
    colcon build \
        --symlink-install \
        --packages-up-to "${CORE_PACKAGES[@]}" \
        --cmake-args \
            -DCMAKE_BUILD_TYPE=RelWithDebInfo \
            -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
    local rc=$?
    set -e
    [[ "$rc" -eq 0 ]] && pass "Core workspace build passed." || fail "Core workspace build failed."
}

source_workspace() {
    [[ -f "${WORKSPACE_ROOT}/install/setup.bash" ]] || { fail "Workspace setup missing."; return 1; }
    set +u
    source "${WORKSPACE_ROOT}/install/setup.bash"
    set -u
}

check_discovery() {
    section "W4 — Package discovery"
    source_workspace || return

    local pkg
    for pkg in "${CORE_PACKAGES[@]}"; do
        ros2 pkg prefix "$pkg" >/dev/null 2>&1 \
            && pass "Package discoverable: $pkg" \
            || fail "Package not discoverable: $pkg"
    done
}

python_imports() {
    section "W5 — Isaac Python import smoke tests"
    source_workspace || return

    set +e
    "$PYTHON_BIN" - <<'PY'
import importlib

tests = [
    "placeability_scoring",
    "rclpy",
    "sensor_msgs",
    "sensor_msgs_py",
    "std_msgs",
    "geometry_msgs",
    "tf2_ros",
    "cv_bridge",
    "control_msgs",
    "trajectory_msgs",
    "builtin_interfaces",
    "moveit_msgs",
    "gpd_ros_messages",
    "numpy",
    "scipy",
    "open3d",
    "matplotlib",
    "pandas",
    "tqdm",
    "klampt",
    "pyfqmr",
    "shapely",
    "toppra",
    "torch",
    "curobo",
]
failed = []
for name in tests:
    try:
        importlib.import_module(name)
    except Exception as exc:
        failed.append(name)
        print(f"  {name:<24} FAIL ({type(exc).__name__}: {exc})")
    else:
        print(f"  {name:<24} PASS")
raise SystemExit(60 if failed else 0)
PY
    local rc=$?
    set -e
    [[ "$rc" -eq 0 ]] && pass "All imports passed." || fail "One or more imports failed."
}

summary() {
    section "Workspace Validation Summary"
    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"
    [[ "$FAIL_COUNT" -eq 0 ]]
}

main() {
    source_ros311 || true
    check_layout
    check_rosdep
    build_workspace
    check_discovery
    python_imports
    summary
}

main "$@"
