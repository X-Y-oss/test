#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# Isaac Sim 5.1 ROS 2 Jazzy / Python 3.11 validator
#
# Purpose:
#   Validate the ROS/Python ABI layer required by the unified Option-A runtime.
#
# Validation stages
# -----------------
# J1  Isaac Python contract:
#     - PYTHON_BIN exists
#     - Python version is 3.11
#
# J2  Pinned official workspace:
#     - IsaacSim-ros_workspaces checkout exists
#     - revision matches the expected pinned release when configured
#
# J3  Generated workspace artifacts:
#     - jazzy_ws local_setup.bash exists
#     - isaac_sim_ros_ws local_setup.bash exists
#
# J4  Python ABI validation:
#     - source both generated workspaces
#     - Isaac Python imports rclpy
#     - rclpy resolves from the sourced workspace/environment
#
# J5  ROS tooling:
#     - ros2 CLI availability after sourcing
#     - basic ROS environment variables
#
# This script is read-only.
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
ISAAC_ROS_WS_ROOT="${ISAAC_ROS_WS_ROOT:-${WORKSPACE_ROOT}/external/IsaacSim-ros_workspaces}"
#ISAAC_ROS_WS_REVISION="${ISAAC_ROS_WS_REVISION:-v5.1.0}"
ISAAC_ROS_WS_REVISION="${ISAAC_ROS_WS_REVISION:-IsaacSim-5.1.0}"

PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"

ROS_DISTRO_TARGET="${ROS_DISTRO_TARGET:-jazzy}"

ROS311_BASE_SETUP="${ROS311_BASE_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO_TARGET}/${ROS_DISTRO_TARGET}_ws/install/local_setup.bash}"
ROS311_ISAAC_SETUP="${ROS311_ISAAC_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/${ROS_DISTRO_TARGET}/isaac_sim_ros_ws/install/local_setup.bash}"

FAIL_COUNT=0
WARN_COUNT=0

pass() {
    printf '  [PASS] %s\n' "$*"
}

warn() {
    WARN_COUNT=$((WARN_COUNT + 1))
    printf '  [WARN] %s\n' "$*" >&2
}

fail() {
    FAIL_COUNT=$((FAIL_COUNT + 1))
    printf '  [FAIL] %s\n' "$*" >&2
}

section() {
    printf '\n============================================================\n'
    printf '%s\n' "$1"
    printf '============================================================\n'
}

python_runtime_available() {
    [[ -x "$PYTHON_BIN" ]] || command -v "$PYTHON_BIN" >/dev/null 2>&1
}


check_python_contract() {
    section "J1 — Isaac Python Contract"

    printf '  PYTHON_BIN : %s\n' "$PYTHON_BIN"

    if ! python_runtime_available; then
        fail "Isaac Python runtime not found: $PYTHON_BIN"
        return
    fi

    pass "Isaac Python runtime is available."

    local version
    version="$("$PYTHON_BIN" -c 'import platform; print(platform.python_version())' 2>/dev/null || true)"

    printf '  Version    : %s\n' "${version:-<unknown>}"

    if [[ "$version" == 3.11.* ]]; then
        pass "Python version matches Isaac Sim 5.1 contract (3.11)."
    elif [[ -n "$version" ]]; then
        fail "Expected Python 3.11, found $version."
    else
        fail "Could not determine Isaac Python version."
    fi
}


check_pinned_workspace() {
    section "J2 — Official Isaac ROS Workspace Revision"

    printf '  Workspace root    : %s\n' "$ISAAC_ROS_WS_ROOT"
    printf '  Expected revision : %s\n' "$ISAAC_ROS_WS_REVISION"

    if [[ ! -d "$ISAAC_ROS_WS_ROOT" ]]; then
        fail "Isaac ROS workspace source directory is missing."
        return
    fi

    pass "Isaac ROS workspace source directory exists."

    if [[ ! -d "${ISAAC_ROS_WS_ROOT}/.git" ]]; then
        warn "Workspace source exists but is not a Git checkout; revision cannot be verified."
        return
    fi

    local current expected describe
    current="$(git -C "$ISAAC_ROS_WS_ROOT" rev-parse HEAD 2>/dev/null || true)"
    expected="$(git -C "$ISAAC_ROS_WS_ROOT" rev-parse \
        "${ISAAC_ROS_WS_REVISION}^{commit}" 2>/dev/null || true)"
    describe="$(git -C "$ISAAC_ROS_WS_ROOT" describe --tags --always 2>/dev/null || true)"

    printf '  Current commit    : %s\n' "${current:-<unknown>}"
    printf '  Current describe  : %s\n' "${describe:-<unknown>}"

    if [[ -n "$current" && -n "$expected" && "$current" == "$expected" ]]; then
        pass "Workspace checkout matches pinned revision."
    elif [[ -z "$expected" ]]; then
        fail "Expected revision cannot be resolved locally: $ISAAC_ROS_WS_REVISION"
    else
        fail "Workspace checkout does not match pinned revision."
    fi

    if [[ -n "$(git -C "$ISAAC_ROS_WS_ROOT" status --porcelain 2>/dev/null)" ]]; then
        warn "Isaac ROS workspace source tree has local modifications."
    else
        pass "Isaac ROS workspace source tree is clean."
    fi
}


check_workspace_artifacts() {
    section "J3 — Generated ROS Workspace Artifacts"

    printf '  Base setup  : %s\n' "$ROS311_BASE_SETUP"
    printf '  Isaac setup : %s\n' "$ROS311_ISAAC_SETUP"

    if [[ -f "$ROS311_BASE_SETUP" ]]; then
        pass "Base Jazzy Python-3.11 workspace setup exists."
    else
        fail "Missing base Jazzy Python-3.11 setup."
    fi

    if [[ -f "$ROS311_ISAAC_SETUP" ]]; then
        pass "Isaac ROS workspace setup exists."
    else
        fail "Missing Isaac ROS workspace setup."
    fi
}


with_ros311_environment() {
    if [[ ! -f "$ROS311_BASE_SETUP" || ! -f "$ROS311_ISAAC_SETUP" ]]; then
        return 1
    fi

    set +u
    # shellcheck disable=SC1090
    source "$ROS311_BASE_SETUP"
    # shellcheck disable=SC1090
    source "$ROS311_ISAAC_SETUP"
    set -u

    "$@"
}


python_rclpy_probe() {
    "$PYTHON_BIN" - <<'PY'
import platform
import sys

try:
    import rclpy
except Exception as exc:
    print(f"  rclpy import : FAIL ({type(exc).__name__}: {exc})")
    raise SystemExit(40)

print(f"  Python       : {platform.python_version()}")
print(f"  sys.executable: {sys.executable}")
print(f"  rclpy        : {rclpy.__file__}")
print("  rclpy import : PASS")

if sys.version_info[:2] != (3, 11):
    raise SystemExit(41)
PY
}


check_python_abi() {
    section "J4 — Python 3.11 / rclpy ABI"

    if ! python_runtime_available; then
        fail "Cannot validate rclpy because PYTHON_BIN is unavailable."
        return
    fi

    if [[ ! -f "$ROS311_BASE_SETUP" || ! -f "$ROS311_ISAAC_SETUP" ]]; then
        fail "Cannot validate rclpy because generated ROS workspaces are missing."
        return
    fi

    set +e
    (
        set -Eeuo pipefail
        set +u
        # shellcheck disable=SC1090
        source "$ROS311_BASE_SETUP"
        # shellcheck disable=SC1090
        source "$ROS311_ISAAC_SETUP"
        set -u
        python_rclpy_probe
    )
    local rc=$?
    set -e

    case "$rc" in
        0)
            pass "Isaac Python 3.11 imports rclpy successfully."
            ;;
        40)
            fail "rclpy is not importable with Isaac Python."
            ;;
        41)
            fail "rclpy imported under the wrong Python major/minor version."
            ;;
        *)
            fail "Unexpected Python/rclpy ABI probe exit code: $rc"
            ;;
    esac
}


check_ros_tooling() {
    section "J5 — ROS Tooling After Sourcing"

    if [[ ! -f "$ROS311_BASE_SETUP" || ! -f "$ROS311_ISAAC_SETUP" ]]; then
        fail "Cannot inspect ROS tooling because generated setup files are missing."
        return
    fi

    set +u
    # shellcheck disable=SC1090
    source "$ROS311_BASE_SETUP"
    # shellcheck disable=SC1090
    source "$ROS311_ISAAC_SETUP"
    set -u

    printf '  ROS_DISTRO         : %s\n' "${ROS_DISTRO:-<unset>}"
    printf '  AMENT_PREFIX_PATH  : %s\n' "${AMENT_PREFIX_PATH:-<unset>}"
    printf '  PYTHONPATH         : %s\n' "${PYTHONPATH:-<unset>}"

    if [[ "${ROS_DISTRO:-}" == "$ROS_DISTRO_TARGET" ]]; then
        pass "ROS_DISTRO matches target: $ROS_DISTRO_TARGET"
    elif [[ -n "${ROS_DISTRO:-}" ]]; then
        warn "ROS_DISTRO is '${ROS_DISTRO}', expected '${ROS_DISTRO_TARGET}'."
    else
        warn "ROS_DISTRO is not set after sourcing."
    fi

    if command -v ros2 >/dev/null 2>&1; then
        pass "ros2 CLI is available after sourcing."
        printf '  ros2 CLI           : %s\n' "$(command -v ros2)"
    else
        warn "ros2 CLI is not available after sourcing."
        warn "rclpy compatibility may still be valid, but workspace tooling is incomplete."
    fi

    if command -v colcon >/dev/null 2>&1; then
        pass "colcon is available."
    else
        warn "colcon is not available."
    fi

    if command -v rosdep >/dev/null 2>&1; then
        pass "rosdep is available."
    else
        warn "rosdep is not available."
    fi
}


print_summary() {
    section "ROS Jazzy / Python 3.11 Validation Summary"

    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"

    if [[ "$FAIL_COUNT" -gt 0 ]]; then
        printf '\nRESULT: FAIL [SETUP/ABI]\n'
        return 1
    fi

    if [[ "$WARN_COUNT" -gt 0 ]]; then
        printf '\nRESULT: PASS WITH WARNINGS\n'
        return 0
    fi

    printf '\nRESULT: PASS\n'
    return 0
}


main() {
    printf '========================================================================\n'
    printf 'Isaac Sim 5.1 ROS Jazzy / Python 3.11 Validation\n'
    printf '========================================================================\n'

    check_python_contract
    check_pinned_workspace
    check_workspace_artifacts
    check_python_abi
    check_ros_tooling
    print_summary
}


main "$@"
