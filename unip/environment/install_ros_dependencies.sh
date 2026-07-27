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
ROSDEP_VERSION="${ROSDEP_VERSION:-0.26.0}"

CORE_PACKAGE_DIRS=(
    "${UNIP_SRC}/gpd_ros_messages"
    "${UNIP_SRC}/gpd_ros"
    "${UNIP_SRC}/placeability_scoring"
    "${UNIP_SRC}/generate_motion_msgs"
)
CORE_PATH_ARGS=()
ROSDEP_BIN=""

log() { printf '[%s] %s\n' "$SCRIPT_NAME" "$*"; }
warn() { printf '[%s] WARNING: %s\n' "$SCRIPT_NAME" "$*" >&2; }
fail() { printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

source_ros311() {
    [[ -f "$ROS311_BASE_SETUP" ]] || fail "Missing base ROS setup: $ROS311_BASE_SETUP"
    [[ -f "$ROS311_ISAAC_SETUP" ]] || fail "Missing Isaac ROS setup: $ROS311_ISAAC_SETUP"
    set +u
    source "$ROS311_BASE_SETUP"
    source "$ROS311_ISAAC_SETUP"
    set -u
}

ensure_rosdep() {
    if command -v rosdep >/dev/null 2>&1; then
        ROSDEP_BIN="$(command -v rosdep)"
        return
    fi

    log "Installing rosdep==${ROSDEP_VERSION} with Isaac Python."
    "$PYTHON_BIN" -m pip install "rosdep==${ROSDEP_VERSION}"

    local scripts_dir
    scripts_dir="$("$PYTHON_BIN" - <<'PY'
import sysconfig
print(sysconfig.get_path("scripts"))
PY
)"
    export PATH="${scripts_dir}:${PATH}"
    hash -r
    command -v rosdep >/dev/null 2>&1 || fail "rosdep CLI still not discoverable."
    ROSDEP_BIN="$(command -v rosdep)"
}

collect_core_paths() {
    local p
    CORE_PATH_ARGS=()
    for p in "${CORE_PACKAGE_DIRS[@]}"; do
        if [[ -f "${p}/package.xml" ]]; then
            CORE_PATH_ARGS+=("$p")
            log "Core ROS package: $p"
        else
            warn "Missing core package manifest: $p/package.xml"
        fi
    done
    [[ "${#CORE_PATH_ARGS[@]}" -gt 0 ]] || fail "No core package manifests found."
}

main() {
    source_ros311
    ensure_rosdep

    if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
        "$ROSDEP_BIN" init
    fi
    "$ROSDEP_BIN" update

    collect_core_paths

    "$ROSDEP_BIN" install \
        --from-paths "${CORE_PATH_ARGS[@]}" \
        --ignore-src \
        --rosdistro "${ROS_DISTRO:-$ROS_DISTRO_TARGET}" \
        -r -y

    "$ROSDEP_BIN" check \
        --from-paths "${CORE_PATH_ARGS[@]}" \
        --ignore-src \
        --rosdistro "${ROS_DISTRO:-$ROS_DISTRO_TARGET}"

    log "PASS: core ROS dependencies satisfied."
}

main "$@"
