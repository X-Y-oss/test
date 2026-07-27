#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP GPD validator
#
# Validation levels
# -----------------
# B1  Native GPD installation:
#     - libgpd discoverable
#     - installed GPD headers present
#     - source revision visible when GPD_ROOT is a Git checkout
#
# B2  ROS wrapper availability:
#     - ROS 2 CLI available
#     - gpd_ros_messages discoverable
#     - gpd_ros discoverable
#     - gpd_ros executable discoverable
#
# B3  Optional node-startup probe (--startup):
#     - starts the gpd_ros executable with a GPD config file
#     - a node that remains alive until timeout counts as PASS
#
# B4  Functional CloudIndexed -> GraspConfigList roundtrip is intentionally
#     NOT automated here yet. It requires a known-valid point-cloud fixture.
#
# Typical usage:
#   ./environment/validate_gpd.sh
#
# With startup probe:
#   ./environment/validate_gpd.sh --startup
#
# Optional overrides:
#   GPD_ROOT=/workspace/external/gpd
#   GPD_REVISION=2.0.0
#   GPD_CONFIG_FILE=/workspace/external/gpd/cfg/ros_eigen_params.cfg
#   GPD_EXECUTABLE=<actual executable name>
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
GPD_ROOT="${GPD_ROOT:-${WORKSPACE_ROOT}/external/gpd}"
GPD_REVISION="${GPD_REVISION:-2.0.0}"
GPD_INSTALL_PREFIX="${GPD_INSTALL_PREFIX:-/usr/local}"
GPD_CONFIG_FILE="${GPD_CONFIG_FILE:-${GPD_ROOT}/cfg/ros_eigen_params.cfg}"
GPD_EXECUTABLE="${GPD_EXECUTABLE:-}"
GPD_STARTUP_TIMEOUT="${GPD_STARTUP_TIMEOUT:-8}"

RUN_STARTUP=0
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
  $SCRIPT_NAME [--startup]

Options:
  --startup    Also run the gpd_ros node-startup probe.
  -h, --help   Show this help.
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --startup)
                RUN_STARTUP=1
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
        shift
    done
}

source_ros_workspace_if_available() {
    # Source an already-built UniP workspace if present.
    if [[ -f "${WORKSPACE_ROOT}/install/setup.bash" ]]; then
        # shellcheck disable=SC1091
        source "${WORKSPACE_ROOT}/install/setup.bash"
        pass "Sourced workspace install/setup.bash."
    else
        warn "Workspace install/setup.bash not found; ROS package discovery may be incomplete."
    fi
}

libgpd_path() {
    if command -v ldconfig >/dev/null 2>&1; then
        local line
        line="$(ldconfig -p 2>/dev/null | grep -E 'libgpd(\.so|\s)' | head -n 1 || true)"
        if [[ -n "$line" ]]; then
            printf '%s\n' "$line"
            return 0
        fi
    fi

    local found
    found="$(
        find "${GPD_INSTALL_PREFIX}/lib" "${GPD_INSTALL_PREFIX}/lib64" \
            -maxdepth 1 -type f -name 'libgpd.so*' -print -quit 2>/dev/null || true
    )"

    [[ -n "$found" ]] || return 1
    printf '%s\n' "$found"
}

check_native_gpd() {
    section "B1 — Native GPD"

    printf '  GPD_ROOT           : %s\n' "$GPD_ROOT"
    printf '  Expected revision  : %s\n' "$GPD_REVISION"
    printf '  Install prefix     : %s\n' "$GPD_INSTALL_PREFIX"

    local lib_info
    lib_info="$(libgpd_path || true)"
    if [[ -n "$lib_info" ]]; then
        pass "libgpd is discoverable."
        printf '         %s\n' "$lib_info"
    else
        fail "libgpd is not discoverable."
    fi

    local header_found=0
    local candidate
    for candidate in \
        "${GPD_INSTALL_PREFIX}/include/gpd/grasp_detector.h" \
        "${GPD_INSTALL_PREFIX}/include/gpd/grasp_detector.hpp" \
        "${GPD_INSTALL_PREFIX}/include/gpd/util/cloud.h"; do
        if [[ -f "$candidate" ]]; then
            pass "GPD header found: $candidate"
            header_found=1
            break
        fi
    done

    if [[ "$header_found" -eq 0 ]]; then
        fail "Expected installed GPD headers were not found."
    fi

    if [[ -d "${GPD_ROOT}/.git" ]]; then
        local commit describe expected_commit
        commit="$(git -C "$GPD_ROOT" rev-parse HEAD 2>/dev/null || true)"
        describe="$(git -C "$GPD_ROOT" describe --tags --always 2>/dev/null || true)"
        expected_commit="$(git -C "$GPD_ROOT" rev-parse "${GPD_REVISION}^{commit}" 2>/dev/null || true)"

        printf '  Source commit      : %s\n' "${commit:-<unknown>}"
        printf '  Source describe    : %s\n' "${describe:-<unknown>}"

        if [[ -n "$commit" && -n "$expected_commit" && "$commit" == "$expected_commit" ]]; then
            pass "GPD source checkout matches expected revision."
        else
            warn "GPD source checkout does not match expected revision or could not be verified."
        fi
    else
        warn "GPD_ROOT is not a Git checkout; source revision cannot be verified."
    fi

    if [[ -f "$GPD_CONFIG_FILE" ]]; then
        pass "GPD config file exists: $GPD_CONFIG_FILE"
    else
        warn "GPD config file not found: $GPD_CONFIG_FILE"
    fi
}

discover_gpd_executable() {
    if [[ -n "$GPD_EXECUTABLE" ]]; then
        printf '%s\n' "$GPD_EXECUTABLE"
        return 0
    fi

    local executables
    executables="$(ros2 pkg executables gpd_ros 2>/dev/null || true)"
    [[ -n "$executables" ]] || return 1

    # Prefer the name suggested by the source class / historical wrapper.
    local preferred
    preferred="$(
        printf '%s\n' "$executables" \
            | awk '$1=="gpd_ros" && ($2 ~ /grasp.*detect|gpd.*node|grasp.*node/) {print $2; exit}'
    )"

    if [[ -n "$preferred" ]]; then
        printf '%s\n' "$preferred"
        return 0
    fi

    # Fallback: if the package exposes exactly one executable, use it.
    local count
    count="$(printf '%s\n' "$executables" | awk '$1=="gpd_ros" {c++} END {print c+0}')"

    if [[ "$count" -eq 1 ]]; then
        printf '%s\n' "$executables" | awk '$1=="gpd_ros" {print $2; exit}'
        return 0
    fi

    return 1
}

check_ros_wrapper() {
    section "B2 — ROS Wrapper"

    if ! command -v ros2 >/dev/null 2>&1; then
        fail "ros2 CLI is not available."
        return
    fi

    pass "ros2 CLI is available."

    if ros2 pkg prefix gpd_ros_messages >/dev/null 2>&1; then
        pass "ROS package discoverable: gpd_ros_messages"
    else
        fail "ROS package not discoverable: gpd_ros_messages"
    fi

    if ros2 pkg prefix gpd_ros >/dev/null 2>&1; then
        pass "ROS package discoverable: gpd_ros"
    else
        fail "ROS package not discoverable: gpd_ros"
        return
    fi

    local executables
    executables="$(ros2 pkg executables gpd_ros 2>/dev/null || true)"

    if [[ -n "$executables" ]]; then
        pass "gpd_ros exposes ROS executable(s):"
        printf '%s\n' "$executables" | sed 's/^/         /'
    else
        fail "No ROS executable found for gpd_ros."
        return
    fi

    local executable
    executable="$(discover_gpd_executable || true)"

    if [[ -n "$executable" ]]; then
        pass "Selected gpd_ros executable: $executable"
        GPD_EXECUTABLE="$executable"
    else
        warn "Could not select a unique gpd_ros executable automatically."
        warn "Set GPD_EXECUTABLE explicitly before using --startup."
    fi
}

run_startup_probe() {
    section "B3 — gpd_ros Node Startup"

    if [[ "$RUN_STARTUP" -ne 1 ]]; then
        printf '  [SKIP] Startup probe not requested. Use --startup to enable it.\n'
        return
    fi

    if ! command -v ros2 >/dev/null 2>&1; then
        fail "Cannot run startup probe because ros2 CLI is unavailable."
        return
    fi

    if [[ -z "$GPD_EXECUTABLE" ]]; then
        GPD_EXECUTABLE="$(discover_gpd_executable || true)"
    fi

    if [[ -z "$GPD_EXECUTABLE" ]]; then
        fail "Cannot determine gpd_ros executable. Set GPD_EXECUTABLE explicitly."
        return
    fi

    if [[ ! -f "$GPD_CONFIG_FILE" ]]; then
        fail "Cannot run startup probe because GPD config file is missing: $GPD_CONFIG_FILE"
        return
    fi

    if ! command -v timeout >/dev/null 2>&1; then
        fail "Required command for startup probe not found: timeout"
        return
    fi

    local temp_log
    temp_log="$(mktemp -t unip_gpd_startup.XXXXXX.log)"

    printf '  Executable    : %s\n' "$GPD_EXECUTABLE"
    printf '  Config file   : %s\n' "$GPD_CONFIG_FILE"
    printf '  Timeout       : %ss\n' "$GPD_STARTUP_TIMEOUT"
    printf '  Temporary log : %s\n' "$temp_log"

    set +e
    timeout --signal=INT "${GPD_STARTUP_TIMEOUT}s" \
        ros2 run gpd_ros "$GPD_EXECUTABLE" \
        --ros-args \
        -p "config_file:=${GPD_CONFIG_FILE}" \
        >"$temp_log" 2>&1
    local rc=$?
    set -e

    # GNU timeout returns 124 when the command remained alive until timeout.
    if [[ "$rc" -eq 124 ]]; then
        pass "gpd_ros remained alive for the startup window."
    elif [[ "$rc" -eq 0 ]]; then
        warn "gpd_ros exited cleanly before timeout; inspect the startup log."
    else
        fail "gpd_ros exited during startup probe (exit code $rc)."
    fi

    if grep -Eiq \
        'successfully initialized|created.*grasp.*detector|initializ.*grasp.*detection' \
        "$temp_log"; then
        pass "Initialization message detected in node output."
    else
        warn "Expected initialization message was not detected."
    fi

    printf '\n  --- startup log tail ---\n'
    tail -n 25 "$temp_log" | sed 's/^/  /'
    printf '  --- end log tail ---\n'

    printf '\n  NOTE: B4 functional CloudIndexed -> GraspConfigList validation\n'
    printf '        is intentionally deferred until a known-valid fixture exists.\n'
}

print_summary() {
    section "GPD Validation Summary"

    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"

    if [[ "$FAIL_COUNT" -gt 0 ]]; then
        printf '\nRESULT: FAIL [BUILD/RUNTIME]\n'
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
    printf 'UniP GPD Validation\n'
    printf '========================================================================\n'

    source_ros_workspace_if_available
    check_native_gpd
    check_ros_wrapper
    run_startup_probe
    print_summary
}

main "$@"
