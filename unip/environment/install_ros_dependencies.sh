#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# Install declared ROS dependencies for the UniP workspace.
#
# Scope:
#   - source the Isaac-compatible Jazzy/Python-3.11 workspaces;
#   - update rosdep;
#   - install dependencies declared in package.xml files under /workspace/src;
#   - ignore packages that are provided by the same workspace;
#   - do not install native GPD, Torch, CUDA, or cuRobo here.
#
# This script intentionally relies on package.xml ownership rather than a long
# hard-coded apt list.
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
UNIP_SRC="${UNIP_SRC:-${WORKSPACE_ROOT}/src}"

ROS_DISTRO_TARGET="${ROS_DISTRO_TARGET:-jazzy}"
ISAAC_ROS_WS_ROOT="${ISAAC_ROS_WS_ROOT:-${WORKSPACE_ROOT}/external/IsaacSim-ros_workspaces}"

ROS311_BASE_SETUP="${ROS311_BASE_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO_TARGET}/${ROS_DISTRO_TARGET}_ws/install/local_setup.bash}"
ROS311_ISAAC_SETUP="${ROS311_ISAAC_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO_TARGET}/isaac_sim_ros_ws/install/local_setup.bash}"

log()  { printf '[%s] %s\n' "$SCRIPT_NAME" "$*"; }
warn() { printf '[%s] WARNING: %s\n' "$SCRIPT_NAME" "$*" >&2; }
fail() { printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

require_command() {
    command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

source_ros311() {
    [[ -f "$ROS311_BASE_SETUP" ]] ||
        fail "Missing base ROS setup: $ROS311_BASE_SETUP"
    [[ -f "$ROS311_ISAAC_SETUP" ]] ||
        fail "Missing Isaac ROS setup: $ROS311_ISAAC_SETUP"

    set +u
    # shellcheck disable=SC1090
    source "$ROS311_BASE_SETUP"
    # shellcheck disable=SC1090
    source "$ROS311_ISAAC_SETUP"
    set -u
}

ensure_rosdep_initialized() {
    require_command rosdep

    if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
        log "Initializing rosdep database..."
        rosdep init
    else
        log "rosdep already initialized."
    fi

    log "Updating rosdep database..."
    rosdep update
}

install_declared_dependencies() {
    [[ -d "$UNIP_SRC" ]] || fail "ROS source directory not found: $UNIP_SRC"

    log "Installing declared ROS dependencies."
    log "Source root : $UNIP_SRC"
    log "ROS distro  : ${ROS_DISTRO:-$ROS_DISTRO_TARGET}"

    rosdep install \
        --from-paths "$UNIP_SRC" \
        --ignore-src \
        --rosdistro "${ROS_DISTRO:-$ROS_DISTRO_TARGET}" \
        -r \
        -y

    log "rosdep install completed."
}

verify_declared_dependencies() {
    log "Verifying declared dependencies with rosdep check..."

    set +e
    rosdep check \
        --from-paths "$UNIP_SRC" \
        --ignore-src \
        --rosdistro "${ROS_DISTRO:-$ROS_DISTRO_TARGET}"
    local rc=$?
    set -e

    if [[ "$rc" -ne 0 ]]; then
        fail "rosdep check still reports unsatisfied declared dependencies."
    fi

    log "PASS: all declared ROS dependencies are satisfied."
}

main() {
    printf '========================================================================\n'
    printf 'UniP ROS Dependency Installation\n'
    printf '========================================================================\n'

    source_ros311
    require_command rosdep

    ensure_rosdep_initialized
    install_declared_dependencies
    verify_declared_dependencies
}

main "$@"
