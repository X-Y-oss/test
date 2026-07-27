#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# Isaac Sim 5.1 compatible ROS 2 Jazzy / Python 3.11 workspace installer
#
# Purpose:
#   Prepare the official Isaac Sim ROS workspace that can be sourced together
#   with Isaac Sim 5.1's Python 3.11 runtime.
#
# Official workflow for Isaac Sim 5.1 / Ubuntu 24.04:
#   IsaacSim-ros_workspaces @ v5.1.0
#   ./build_ros.sh -d jazzy -v 24.04
#
# Important:
#   The official build_ros.sh builds a helper Docker image and extracts the
#   generated Python-3.11 ROS workspaces. Therefore Docker CLI + access to a
#   Docker daemon are required when the prebuilt workspace is not already
#   present.
#
# This script:
#   - pins the official repository to v5.1.0 by default;
#   - is idempotent;
#   - never follows main/master silently;
#   - never sources Ubuntu 24.04's Python-3.12 Jazzy into Isaac Python;
#   - validates rclpy with Isaac Sim's Python runtime after the build.
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

ISAAC_ROS_WS_REPO="${ISAAC_ROS_WS_REPO:-https://github.com/isaac-sim/IsaacSim-ros_workspaces.git}"
ISAAC_ROS_REVISION="${ISAAC_ROS_REVISION:-IsaacSim-5.1.0}"
ISAAC_ROS_WS_ROOT="${ISAAC_ROS_WS_ROOT:-/workspace/external/IsaacSim-ros_workspaces}"

ROS_DISTRO="${ROS_DISTRO_TARGET:-jazzy}"
UBUNTU_VERSION="${ROS_UBUNTU_VERSION:-24.04}"

PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"

ROS311_BASE_SETUP="${ROS311_BASE_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO}/${ROS_DISTRO}_ws/install/local_setup.bash}"
ROS311_ISAAC_SETUP="${ROS311_ISAAC_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO}/isaac_sim_ros_ws/install/local_setup.bash}"

log() {
    printf '[%s] %s\n' "$SCRIPT_NAME" "$*"
}

warn() {
    printf '[%s] WARNING: %s\n' "$SCRIPT_NAME" "$*" >&2
}

fail() {
    printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2
    exit 1
}

on_error() {
    local rc=$?
    local line_no="${1:-unknown}"

    printf '\n[%s] ERROR: command failed at line %s (exit code %s)\n' \
        "$SCRIPT_NAME" "$line_no" "$rc" >&2
    printf '[%s] ISAAC_ROS_WS_ROOT=%s\n' "$SCRIPT_NAME" "$ISAAC_ROS_WS_ROOT" >&2
    printf '[%s] ISAAC_ROS_REVISION=%s\n' "$SCRIPT_NAME" "$ISAAC_ROS_REVISION" >&2
    exit "$rc"
}

trap 'on_error $LINENO' ERR


require_command() {
    local cmd="$1"
    command -v "$cmd" >/dev/null 2>&1 || fail "Required command not found: $cmd"
}


python_runtime_ok() {
    [[ -x "$PYTHON_BIN" ]] || command -v "$PYTHON_BIN" >/dev/null 2>&1
}


check_python_contract() {
    python_runtime_ok || fail "Isaac Python runtime not found: $PYTHON_BIN"

    local version
    version="$("$PYTHON_BIN" -c 'import platform; print(platform.python_version())')"

    log "Python runtime : $PYTHON_BIN"
    log "Python version : $version"

    if [[ "$version" != 3.11.* ]]; then
        fail "Isaac Sim 5.1 ROS workspace requires Python 3.11; found $version"
    fi
}


ensure_source() {
    mkdir -p "$(dirname "$ISAAC_ROS_WS_ROOT")"

    if [[ ! -e "$ISAAC_ROS_WS_ROOT" ]]; then
        log "Cloning official Isaac Sim ROS workspaces..."
        git clone "$ISAAC_ROS_WS_REPO" "$ISAAC_ROS_WS_ROOT"
    elif [[ ! -d "${ISAAC_ROS_WS_ROOT}/.git" ]]; then
        fail "ISAAC_ROS_WS_ROOT exists but is not a Git repository: $ISAAC_ROS_WS_ROOT"
    else
        log "Existing Isaac Sim ROS workspace checkout found."
    fi

    local origin
    origin="$(git -C "$ISAAC_ROS_WS_ROOT" remote get-url origin 2>/dev/null || true)"
    if [[ -n "$origin" && "$origin" != "$ISAAC_ROS_WS_REPO" ]]; then
        warn "Repository origin differs from expected."
        warn "Expected: $ISAAC_ROS_WS_REPO"
        warn "Found:    $origin"
    fi

    log "Fetching release tags..."
    git -C "$ISAAC_ROS_WS_ROOT" fetch --tags --prune origin

    if ! git -C "$ISAAC_ROS_WS_ROOT" rev-parse --verify \
        "${ISAAC_ROS_REVISION}^{commit}" >/dev/null 2>&1; then
        fail "Pinned Isaac ROS workspace revision cannot be resolved: ${ISAAC_ROS_REVISION}"
    fi
}


current_checkout_matches() {
    [[ -d "${ISAAC_ROS_WS_ROOT}/.git" ]] || return 1

    local current expected
    current="$(git -C "$ISAAC_ROS_WS_ROOT" rev-parse HEAD 2>/dev/null || true)"
    expected="$(git -C "$ISAAC_ROS_WS_ROOT" rev-parse \
        "${ISAAC_ROS_REVISION}^{commit}" 2>/dev/null || true)"

    [[ -n "$current" && -n "$expected" && "$current" == "$expected" ]]
}


checkout_pinned_revision() {
    if current_checkout_matches; then
        log "Pinned Isaac ROS workspace revision already checked out: $ISAAC_ROS_REVISION"
        return
    fi

    if [[ -n "$(git -C "$ISAAC_ROS_WS_ROOT" status --porcelain)" ]]; then
        fail "Isaac ROS workspace source has local modifications; refusing to overwrite."
    fi

    log "Checking out pinned revision: $ISAAC_ROS_REVISION"
    git -C "$ISAAC_ROS_WS_ROOT" checkout --detach "$ISAAC_ROS_REVISION"

    log "Updating repository submodules..."
    git -C "$ISAAC_ROS_WS_ROOT" submodule update --init --recursive
}


workspace_artifacts_exist() {
    [[ -f "$ROS311_BASE_SETUP" && -f "$ROS311_ISAAC_SETUP" ]]
}


docker_daemon_available() {
    command -v docker >/dev/null 2>&1 &&
        docker info >/dev/null 2>&1
}


build_official_workspace() {
    local build_script="${ISAAC_ROS_WS_ROOT}/build_ros.sh"

    [[ -x "$build_script" ]] || fail "Official build script is missing or not executable: $build_script"

    if ! docker_daemon_available; then
        cat >&2 <<EOF
[$SCRIPT_NAME] ERROR: Python-3.11 Jazzy workspace is not built yet, and no usable
Docker daemon is available from this container.

The Isaac Sim 5.1 official build workflow itself uses Docker.

Required action:
  1. Expose a Docker daemon to this devcontainer (typically /var/run/docker.sock)
     and make the docker CLI available, OR
  2. Run the pinned official build on the host:
       cd ${ISAAC_ROS_WS_ROOT}
       ./build_ros.sh -d jazzy -v 24.04

Expected artifacts:
  ${ROS311_BASE_SETUP}
  ${ROS311_ISAAC_SETUP}
EOF
        exit 1
    fi

    log "Building official Isaac-compatible ROS Jazzy/Python-3.11 workspaces..."
    log "Command: ./build_ros.sh -d ${ROS_DISTRO} -v ${UBUNTU_VERSION}"

    pushd "$ISAAC_ROS_WS_ROOT" >/dev/null
    ./build_ros.sh -d "$ROS_DISTRO" -v "$UBUNTU_VERSION"
    popd >/dev/null
}


verify_workspace() {
    log "Verifying generated ROS workspace artifacts..."

    [[ -f "$ROS311_BASE_SETUP" ]] ||
        fail "Base Jazzy Python-3.11 setup file missing: $ROS311_BASE_SETUP"

    [[ -f "$ROS311_ISAAC_SETUP" ]] ||
        fail "Isaac ROS workspace setup file missing: $ROS311_ISAAC_SETUP"

    # Source only the Python-3.11 workspaces produced by NVIDIA.
    set +u
    # shellcheck disable=SC1090
    source "$ROS311_BASE_SETUP"
    # shellcheck disable=SC1090
    source "$ROS311_ISAAC_SETUP"
    set -u

    log "Validating rclpy with Isaac Python..."

    "$PYTHON_BIN" - <<'PY'
import platform

import rclpy

print(f"  Python : {platform.python_version()}")
print(f"  rclpy  : {rclpy.__file__}")
PY

    if command -v ros2 >/dev/null 2>&1; then
        log "ros2 CLI available after sourcing: $(command -v ros2)"
    else
        warn "ros2 CLI is not available after sourcing the Python-3.11 workspaces."
        warn "Python rclpy compatibility passed, but CLI availability should be checked."
    fi
}


already_ready() {
    current_checkout_matches || return 1
    workspace_artifacts_exist || return 1

    (
        set +u
        # shellcheck disable=SC1090
        source "$ROS311_BASE_SETUP"
        # shellcheck disable=SC1090
        source "$ROS311_ISAAC_SETUP"
        set -u

        "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import sys

assert sys.version_info[:2] == (3, 11)
import rclpy
PY
    )
}


print_summary() {
    local commit
    commit="$(git -C "$ISAAC_ROS_WS_ROOT" rev-parse --short HEAD)"

    log "ROS Jazzy / Python 3.11 workspace ready."
    log "Repository    : $ISAAC_ROS_WS_REPO"
    log "Revision      : $ISAAC_ROS_REVISION"
    log "Commit        : $commit"
    log "Source        : $ISAAC_ROS_WS_ROOT"
    log "Base setup    : $ROS311_BASE_SETUP"
    log "Isaac setup   : $ROS311_ISAAC_SETUP"
}


main() {
    log "============================================================"
    log "Isaac Sim 5.1 ROS Jazzy / Python 3.11 installation"
    log "============================================================"

    require_command git
    check_python_contract

    ensure_source
    checkout_pinned_revision

    if already_ready; then
        log "Correct pinned revision and working Python-3.11 rclpy detected."
        log "SKIP: Isaac-compatible ROS workspace is already ready."
        print_summary
        exit 0
    fi

    if ! workspace_artifacts_exist; then
        build_official_workspace
    else
        log "Existing build artifacts found; skipping rebuild."
    fi

    verify_workspace
    print_summary

    log "PASS: Isaac-compatible ROS Jazzy/Python-3.11 workspace prepared."
}


main "$@"
