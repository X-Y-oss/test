#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP ROS workspace validator
#
# Purpose:
#   Validate the ROS workspace layer without starting the full UP4 pipeline.
#
# Validation stages
# -----------------
# W1  ROS environment / rosdep readiness
# W2  Optional rosdep dependency check
# W3  colcon build
# W4  package discovery after sourcing install/setup.bash
# W5  Python import smoke tests
#
# Typical usage:
#   ./environment/validate_workspace.sh
#
# Skip the rosdep check if needed:
#   ./environment/validate_workspace.sh --skip-rosdep
#
# Build selected packages only:
#   ./environment/validate_workspace.sh \
#       --packages gpd_ros_messages gpd_ros placeability_scoring
#
# Environment overrides:
#   WORKSPACE_ROOT=/workspace
#   UNIP_SRC=/workspace/src
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
UNIP_SRC="${UNIP_SRC:-${WORKSPACE_ROOT}/src}"

RUN_ROSDEP=1
PACKAGES=()

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

usage() {
    cat <<EOF
Usage:
  $SCRIPT_NAME [--skip-rosdep] [--packages PKG1 PKG2 ...]

Options:
  --skip-rosdep          Skip rosdep dependency check.
  --packages ...         Build only the listed packages and their dependencies.
  -h, --help             Show this help.

Examples:
  $SCRIPT_NAME

  $SCRIPT_NAME --packages \
      gpd_ros_messages gpd_ros placeability_scoring
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --skip-rosdep)
                RUN_ROSDEP=0
                shift
                ;;
            --packages)
                shift
                while [[ $# -gt 0 && "$1" != --* ]]; do
                    PACKAGES+=("$1")
                    shift
                done
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                printf '[%s] ERROR: unknown argument: %s\n' "$SCRIPT_NAME" "$1" >&2
                usage >&2
                exit 2
                ;;
        esac
    done
}

source_ros_if_needed() {
    # In Isaac Sim 5.1 containers ROS may not be in the normal /opt/ros path.
    # We do not guess hidden bridge paths here; validate_environment.sh reports
    # them separately. This validator only sources a conventional ROS setup if
    # available and otherwise relies on the caller's environment.

    if [[ -n "${ROS_DISTRO:-}" ]]; then
        pass "ROS environment already active: ${ROS_DISTRO}"
        return
    fi

    local candidate
    for candidate in \
        /opt/ros/jazzy/setup.bash \
        /opt/ros/humble/setup.bash; do
        if [[ -f "$candidate" ]]; then
            # shellcheck disable=SC1090
            source "$candidate"
            pass "Sourced ROS environment: $candidate"
            return
        fi
    done

    warn "No conventional ROS setup.bash found; relying on current environment."
}

check_workspace_layout() {
    section "W1 — Workspace / ROS Environment"

    printf '  WORKSPACE_ROOT : %s\n' "$WORKSPACE_ROOT"
    printf '  UNIP_SRC       : %s\n' "$UNIP_SRC"
    printf '  ROS_DISTRO     : %s\n' "${ROS_DISTRO:-<unset>}"

    if [[ -d "$WORKSPACE_ROOT" ]]; then
        pass "Workspace root exists."
    else
        fail "Workspace root does not exist: $WORKSPACE_ROOT"
    fi

    if [[ -d "$UNIP_SRC" ]]; then
        pass "Workspace src directory exists."
    else
        fail "Workspace src directory does not exist: $UNIP_SRC"
    fi

    if command -v ros2 >/dev/null 2>&1; then
        pass "ros2 CLI is available."
    else
        fail "ros2 CLI is not available."
    fi

    if command -v colcon >/dev/null 2>&1; then
        pass "colcon is available."
    else
        fail "colcon is not available."
    fi

    if command -v rosdep >/dev/null 2>&1; then
        pass "rosdep is available."
    else
        warn "rosdep is not available."
    fi
}

check_rosdep() {
    section "W2 — rosdep Dependency Check"

    if [[ "$RUN_ROSDEP" -ne 1 ]]; then
        printf '  [SKIP] rosdep check disabled by --skip-rosdep.\n'
        return
    fi

    if ! command -v rosdep >/dev/null 2>&1; then
        warn "rosdep unavailable; dependency check skipped."
        return
    fi

    local args=(
        check
        --from-paths "$UNIP_SRC"
        --ignore-src
    )

    if [[ -n "${ROS_DISTRO:-}" ]]; then
        args+=(--rosdistro "$ROS_DISTRO")
    fi

    set +e
    rosdep "${args[@]}"
    local rc=$?
    set -e

    if [[ "$rc" -eq 0 ]]; then
        pass "rosdep reports all declared dependencies satisfied."
    else
        warn "rosdep check reported missing/unsatisfied declared dependencies."
        warn "This may indicate package.xml gaps or packages not yet installed."
    fi
}

build_workspace() {
    section "W3 — colcon Build"

    if ! command -v colcon >/dev/null 2>&1; then
        fail "Cannot build: colcon is unavailable."
        return
    fi

    local cmd=(
        colcon build
        --base-paths "$UNIP_SRC"
        --cmake-args
        -DCMAKE_BUILD_TYPE=RelWithDebInfo
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
    )

    if [[ "${#PACKAGES[@]}" -gt 0 ]]; then
        cmd+=(
            --packages-up-to
            "${PACKAGES[@]}"
        )
        printf '  Selected packages: %s\n' "${PACKAGES[*]}"
    else
        printf '  Selected packages: ALL\n'
    fi

    printf '  Command:'
    printf ' %q' "${cmd[@]}"
    printf '\n'

    pushd "$WORKSPACE_ROOT" >/dev/null

    set +e
    "${cmd[@]}"
    local rc=$?
    set -e

    popd >/dev/null

    if [[ "$rc" -eq 0 ]]; then
        pass "colcon build completed successfully."
    else
        fail "colcon build failed (exit code $rc)."
    fi
}

source_workspace() {
    if [[ -f "${WORKSPACE_ROOT}/install/setup.bash" ]]; then
        # shellcheck disable=SC1091
        source "${WORKSPACE_ROOT}/install/setup.bash"
        pass "Sourced ${WORKSPACE_ROOT}/install/setup.bash"
        return 0
    fi

    fail "Workspace install/setup.bash not found."
    return 1
}

check_package_discovery() {
    section "W4 — ROS Package Discovery"

    source_workspace || return

    local core_packages=(
        gpd_ros_messages
        gpd_ros
        placeability_scoring
    )

    local pkg
    for pkg in "${core_packages[@]}"; do
        if ros2 pkg prefix "$pkg" >/dev/null 2>&1; then
            pass "ROS package discoverable: $pkg"
        else
            fail "ROS package not discoverable: $pkg"
        fi
    done

    # Kept in workspace but not proven core.
    local keep_packages=(
        generate_motion_msgs
        steve_description
        steve_config_moveit2
    )

    for pkg in "${keep_packages[@]}"; do
        if ros2 pkg prefix "$pkg" >/dev/null 2>&1; then
            pass "Workspace package discoverable: $pkg"
        else
            warn "Workspace package not discoverable: $pkg"
        fi
    done
}

python_import_smoke_tests() {
    section "W5 — Python Import Smoke Tests"

    source_workspace || return

    set +e
    python3 - <<'PY'
import importlib
import sys

tests = [
    # Core workspace package.
    "placeability_scoring",

    # Core ROS interfaces/packages used by the baseline.
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

    # Confirmed Python runtime dependencies.
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

    # Compatibility-controlled core dependency.
    "torch",

    # Project-specific planner dependency.
    "curobo",
]

failed = []

for name in tests:
    try:
        importlib.import_module(name)
    except Exception as exc:
        failed.append((name, f"{type(exc).__name__}: {exc}"))
        print(f"  {name:<24} FAIL ({type(exc).__name__}: {exc})")
    else:
        print(f"  {name:<24} PASS")

if failed:
    raise SystemExit(60)

raise SystemExit(0)
PY
    local rc=$?
    set -e

    if [[ "$rc" -eq 0 ]]; then
        pass "All import smoke tests passed."
    else
        fail "One or more import smoke tests failed."
    fi
}

print_summary() {
    section "Workspace Validation Summary"

    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"

    if [[ "$FAIL_COUNT" -gt 0 ]]; then
        printf '\nRESULT: FAIL [BUILD/SETUP]\n'
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
    parse_args "$@"

    printf '========================================================================\n'
    printf 'UniP ROS Workspace Validation\n'
    printf '========================================================================\n'

    source_ros_if_needed
    check_workspace_layout
    check_rosdep
    build_workspace
    check_package_discovery
    python_import_smoke_tests
    print_summary
}

main "$@"
