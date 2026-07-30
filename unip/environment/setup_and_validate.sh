#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP environment setup + validation orchestrator
#
# Verified target:
#   Isaac Sim 5.1
#   + Isaac-compatible ROS 2 Jazzy / Python 3.11 layer
#   + UniP ROS311 compatibility overlay
#   + native GPD 2.0.0
#   + UniP core ROS311 merge-install
#   + Isaac Python core dependencies
#   + CUDA Toolkit 12.8
#   + Torch/CUDA compatibility gate
#   + pinned cuRobo v0.7.8
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
UNIP_SRC="${UNIP_SRC:-${WORKSPACE_ROOT}/src}"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"
ROS_DISTRO_TARGET="${ROS_DISTRO_TARGET:-jazzy}"
ISAAC_ROS_WS_ROOT="${ISAAC_ROS_WS_ROOT:-${WORKSPACE_ROOT}/external/IsaacSim-ros_workspaces}"

VALIDATE_ONLY=0
WITH_RUNTIME=0
GPD_STARTUP=0

RUN_ID="$(date '+%Y-%m-%d_%H-%M-%S')"
LOG_ROOT="${LOG_ROOT:-${SCRIPT_DIR}/logs}"
RUN_LOG_DIR="${LOG_ROOT}/${RUN_ID}"
SUMMARY_FILE="${RUN_LOG_DIR}/summary.txt"

declare -a STAGE_NAMES=()
declare -a STAGE_RESULTS=()
declare -a STAGE_CLASSES=()
declare -a STAGE_LOGS=()

FIRST_FAILURE_STAGE=""
FIRST_FAILURE_CLASS=""
FIRST_FAILURE_LOG=""
FIRST_FAILURE_CODE=""

mkdir -p "$RUN_LOG_DIR"

usage() {
    cat <<EOF2
Usage:
  $SCRIPT_NAME [OPTIONS]

Options:
  --validate-only   Skip installation/build stages; validate the existing environment.
  --with-runtime    Also validate Isaac/ROS runtime interfaces.
  --gpd-startup     Also run the gpd_ros startup probe.
  -h, --help        Show this help.

Environment overrides:
  WORKSPACE_ROOT      Default: /workspace
  UNIP_SRC            Default: /workspace/src
  PYTHON_BIN          Default: /isaac-sim/python.sh
  LOG_ROOT            Default: environment/logs
  ROS_DISTRO_TARGET   Default: jazzy
  ISAAC_ROS_WS_ROOT   Default: /workspace/external/IsaacSim-ros_workspaces
EOF2
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --validate-only) VALIDATE_ONLY=1 ;;
            --with-runtime)  WITH_RUNTIME=1 ;;
            --gpd-startup)   GPD_STARTUP=1 ;;
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

banner() {
    printf '\n========================================================================\n'
    printf '%s\n' "$1"
    printf '========================================================================\n'
}

record_stage() {
    STAGE_NAMES+=("$1")
    STAGE_RESULTS+=("$2")
    STAGE_CLASSES+=("$3")
    STAGE_LOGS+=("$4")
}

classify_failure() {
    local default_class="$1"
    local log_file="$2"

    if grep -Eiq \
        'python.?3\.11.*not supported|unsupported python|ABI incompat|incompatible.*python|breaking API|API.*incompat' \
        "$log_file" 2>/dev/null; then
        printf 'ARCHITECTURE\n'
        return
    fi

    printf '%s\n' "$default_class"
}

run_stage() {
    local stage_name="$1"
    local default_class="$2"
    shift 2

    local safe_name
    safe_name="$(printf '%s' "$stage_name" | tr '[:upper:] ' '[:lower:]_' | tr -cd '[:alnum:]_-')"
    local log_file="${RUN_LOG_DIR}/${safe_name}.log"

    banner "STAGE — ${stage_name}"
    printf 'Log: %s\n' "$log_file"

    set +e
    (
        set -Eeuo pipefail
        "$@"
    ) > >(tee "$log_file") 2>&1
    local rc=$?
    set -e

    if [[ "$rc" -eq 0 ]]; then
        printf '\n[PASS] %s\n' "$stage_name"
        record_stage "$stage_name" "PASS" "-" "$log_file"
        return 0
    fi

    local failure_class
    failure_class="$(classify_failure "$default_class" "$log_file")"

    printf '\n[FAIL] %s [%s] (exit code %s)\n' "$stage_name" "$failure_class" "$rc" >&2
    record_stage "$stage_name" "FAIL" "$failure_class" "$log_file"

    if [[ -z "$FIRST_FAILURE_STAGE" ]]; then
        FIRST_FAILURE_STAGE="$stage_name"
        FIRST_FAILURE_CLASS="$failure_class"
        FIRST_FAILURE_LOG="$log_file"
        FIRST_FAILURE_CODE="$rc"
    fi

    return "$rc"
}

run_required_stage() {
    local stage_name="$1"
    local default_class="$2"
    shift 2

    if run_stage "$stage_name" "$default_class" "$@"; then
        return 0
    fi

    local rc=$?
    abort_with_summary "$FIRST_FAILURE_STAGE" "$FIRST_FAILURE_CLASS" "$FIRST_FAILURE_LOG" "$rc"
}

run_optional_stage() {
    local stage_name="$1"
    local default_class="$2"
    shift 2

    if run_stage "$stage_name" "$default_class" "$@"; then
        return 0
    fi

    printf '[%s] Optional stage failed; continuing for final report.\n' "$SCRIPT_NAME" >&2
    return 0
}

skip_stage() {
    local stage_name="$1"
    local reason="$2"
    local safe_name
    safe_name="$(printf '%s' "$stage_name" | tr '[:upper:] ' '[:lower:]_' | tr -cd '[:alnum:]_-')"
    local log_file="${RUN_LOG_DIR}/${safe_name}.log"

    printf 'SKIPPED: %s\n' "$reason" >"$log_file"
    record_stage "$stage_name" "SKIP" "-" "$log_file"

    banner "STAGE — ${stage_name}"
    printf '[SKIP] %s\n' "$reason"
}

check_script() {
    local path="$1"
    if [[ ! -f "$path" ]]; then
        printf '[%s] ERROR: required script not found: %s\n' "$SCRIPT_NAME" "$path" >&2
        return 1
    fi
}

preflight() {
    banner "UniP Setup / Validation Preflight"

    printf 'Run ID              : %s\n' "$RUN_ID"
    printf 'Repository root     : %s\n' "$REPO_ROOT"
    printf 'Workspace root      : %s\n' "$WORKSPACE_ROOT"
    printf 'Workspace src       : %s\n' "$UNIP_SRC"
    printf 'Python runtime      : %s\n' "$PYTHON_BIN"
    printf 'ROS target          : %s\n' "$ROS_DISTRO_TARGET"
    printf 'Isaac ROS workspace : %s\n' "$ISAAC_ROS_WS_ROOT"
    printf 'Validate only       : %s\n' "$VALIDATE_ONLY"
    printf 'With runtime        : %s\n' "$WITH_RUNTIME"
    printf 'GPD startup         : %s\n' "$GPD_STARTUP"
    printf 'Logs                : %s\n' "$RUN_LOG_DIR"

    local required_scripts=(
        "${SCRIPT_DIR}/install_python_core.sh"
        "${SCRIPT_DIR}/install_ros_jazzy_py311.sh"
        "${SCRIPT_DIR}/validate_ros_jazzy_py311.sh"
        "${SCRIPT_DIR}/install_unip_ros311_overlay.sh"
        "${SCRIPT_DIR}/validate_unip_ros311_overlay.sh"
        "${SCRIPT_DIR}/install_gpd.sh"
        "${SCRIPT_DIR}/build_unip_workspace_ros311.sh"
        "${SCRIPT_DIR}/install_cuda_toolkit.sh"
        "${SCRIPT_DIR}/validate_torch_cuda_gate.sh"
        "${SCRIPT_DIR}/install_curobo.sh"
        "${SCRIPT_DIR}/validate_curobo.sh"
        "${SCRIPT_DIR}/validate_gpd.sh"
        "${SCRIPT_DIR}/validate_workspace.sh"
        "${SCRIPT_DIR}/validate_environment.sh"
    )

    if [[ "$WITH_RUNTIME" -eq 1 ]]; then
        required_scripts+=("${SCRIPT_DIR}/validate_ros_interfaces.sh")
    fi

    local script
    for script in "${required_scripts[@]}"; do
        check_script "$script" || return 1
    done

    [[ -d "$WORKSPACE_ROOT" ]] || {
        printf '[%s] ERROR: workspace root missing: %s\n' "$SCRIPT_NAME" "$WORKSPACE_ROOT" >&2
        return 1
    }

    [[ -d "$UNIP_SRC" ]] || {
        printf '[%s] ERROR: workspace src missing: %s\n' "$SCRIPT_NAME" "$UNIP_SRC" >&2
        return 1
    }

    if [[ ! -x "$PYTHON_BIN" ]] && ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
        printf '[%s] ERROR: Python runtime not found: %s\n' "$SCRIPT_NAME" "$PYTHON_BIN" >&2
        return 1
    fi

    return 0
}

validate_gpd_command() {
    if [[ "$GPD_STARTUP" -eq 1 ]]; then
        "${SCRIPT_DIR}/validate_gpd.sh" --startup
    else
        "${SCRIPT_DIR}/validate_gpd.sh"
    fi
}

write_summary() {
    {
        printf '========================================================================\n'
        printf 'UniP Environment Setup Report\n'
        printf '========================================================================\n'
        printf 'Run ID          : %s\n' "$RUN_ID"
        printf 'Repository root : %s\n' "$REPO_ROOT"
        printf 'Workspace root  : %s\n' "$WORKSPACE_ROOT"
        printf 'Python runtime  : %s\n' "$PYTHON_BIN"
        printf 'ROS target      : %s\n' "$ROS_DISTRO_TARGET"
        printf 'Validate only   : %s\n' "$VALIDATE_ONLY"
        printf 'With runtime    : %s\n' "$WITH_RUNTIME"
        printf 'GPD startup     : %s\n' "$GPD_STARTUP"
        printf '\n'
        printf '%-40s %-10s %-16s %s\n' "STAGE" "RESULT" "CLASS" "LOG"
        printf '%-40s %-10s %-16s %s\n' "----------------------------------------" "----------" "----------------" "---"

        local i
        for i in "${!STAGE_NAMES[@]}"; do
            printf '%-40s %-10s %-16s %s\n' \
                "${STAGE_NAMES[$i]}" \
                "${STAGE_RESULTS[$i]}" \
                "${STAGE_CLASSES[$i]}" \
                "${STAGE_LOGS[$i]}"
        done

        printf '\n'

        if [[ -n "$FIRST_FAILURE_STAGE" ]]; then
            printf 'OVERALL RESULT      : FAIL\n'
            printf 'First failing stage : %s\n' "$FIRST_FAILURE_STAGE"
            printf 'Failure class       : %s\n' "$FIRST_FAILURE_CLASS"
            printf 'Exit code           : %s\n' "$FIRST_FAILURE_CODE"
            printf 'Failure log         : %s\n' "$FIRST_FAILURE_LOG"
        else
            printf 'OVERALL RESULT      : PASS\n'
            if [[ "$WITH_RUNTIME" -eq 0 ]]; then
                printf 'Runtime integration : NOT REQUESTED\n'
            fi
        fi

        printf '\nLog directory: %s\n' "$RUN_LOG_DIR"
        printf '========================================================================\n'
    } | tee "$SUMMARY_FILE"
}

abort_with_summary() {
    local stage="$1"
    local class="$2"
    local log_file="$3"
    local rc="$4"

    if [[ -z "$FIRST_FAILURE_STAGE" ]]; then
        FIRST_FAILURE_STAGE="$stage"
        FIRST_FAILURE_CLASS="$class"
        FIRST_FAILURE_LOG="$log_file"
        FIRST_FAILURE_CODE="$rc"
    fi

    write_summary
    printf '\n[%s] STOPPED at: %s [%s]\n' "$SCRIPT_NAME" "$stage" "$class" >&2
    printf '[%s] See: %s\n' "$SCRIPT_NAME" "$log_file" >&2
    exit "$rc"
}

main() {
    parse_args "$@"

    set +e
    preflight > >(tee "${RUN_LOG_DIR}/preflight.log") 2>&1
    local preflight_rc=$?
    set -e

    if [[ "$preflight_rc" -ne 0 ]]; then
        record_stage "Preflight" "FAIL" "SETUP" "${RUN_LOG_DIR}/preflight.log"
        abort_with_summary "Preflight" "SETUP" "${RUN_LOG_DIR}/preflight.log" "$preflight_rc"
    fi

    record_stage "Preflight" "PASS" "-" "${RUN_LOG_DIR}/preflight.log"

    # 0. Non-blocking environment fingerprint before setup.
    run_optional_stage \
        "Environment pre-check" \
        "SETUP" \
        "${SCRIPT_DIR}/validate_environment.sh"

    # 1. Install/build the reproducible environment.
    if [[ "$VALIDATE_ONLY" -eq 0 ]]; then
        run_required_stage \
            "Python core install" \
            "SETUP" \
            "${SCRIPT_DIR}/install_python_core.sh"

        run_required_stage \
            "ROS Jazzy Py3.11 install" \
            "SETUP" \
            "${SCRIPT_DIR}/install_ros_jazzy_py311.sh"

        run_required_stage \
            "Boost.Python 1.83 for Python 3.11" \
            "SETUP" \
            "${SCRIPT_DIR}/install_boost_python311.sh"

        run_required_stage \
            "UniP ROS311 overlay install" \
            "BUILD" \
            "${SCRIPT_DIR}/install_unip_ros311_overlay.sh"

        run_required_stage \
            "Native GPD install" \
            "BUILD" \
            "${SCRIPT_DIR}/install_gpd.sh"

        run_required_stage \
            "UniP core ROS311 build" \
            "BUILD" \
            "${SCRIPT_DIR}/build_unip_workspace_ros311.sh"

        run_required_stage \
            "CUDA Toolkit 12.8 install" \
            "SETUP" \
            "${SCRIPT_DIR}/install_cuda_toolkit.sh"
    else
        skip_stage "Python core install" "--validate-only"
        skip_stage "ROS Jazzy Py3.11 install" "--validate-only"
        skip_stage "UniP ROS311 overlay install" "--validate-only"
        skip_stage "Native GPD install" "--validate-only"
        skip_stage "UniP core ROS311 build" "--validate-only"
        skip_stage "CUDA Toolkit 12.8 install" "--validate-only"
    fi

    # 2. Validate ROS311 layers and CUDA before cuRobo.
    run_required_stage \
        "ROS Jazzy Py3.11 validation" \
        "SETUP" \
        "${SCRIPT_DIR}/validate_ros_jazzy_py311.sh"

    run_required_stage \
        "UniP ROS311 overlay validation" \
        "SETUP" \
        "${SCRIPT_DIR}/validate_unip_ros311_overlay.sh"

    run_required_stage \
        "Torch/CUDA pre-cuRobo gate" \
        "ARCHITECTURE" \
        "${SCRIPT_DIR}/validate_torch_cuda_gate.sh"

    # 3. Install pinned cuRobo, then immediately guard Isaac Torch/CUDA again.
    if [[ "$VALIDATE_ONLY" -eq 0 ]]; then
        run_required_stage \
            "cuRobo install" \
            "BUILD" \
            "${SCRIPT_DIR}/install_curobo.sh"
    else
        skip_stage "cuRobo install" "--validate-only"
    fi

    run_required_stage \
        "Torch/CUDA post-cuRobo gate" \
        "ARCHITECTURE" \
        "${SCRIPT_DIR}/validate_torch_cuda_gate.sh"

    # 4. Component and workspace validation.
    run_required_stage \
        "cuRobo validation" \
        "RUNTIME" \
        "${SCRIPT_DIR}/validate_curobo.sh"

    run_required_stage \
        "GPD validation" \
        "RUNTIME" \
        validate_gpd_command

    run_required_stage \
        "ROS311 workspace validation" \
        "RUNTIME" \
        "${SCRIPT_DIR}/validate_workspace.sh"

    # 5. Optional live Isaac/ROS interface validation.
    if [[ "$WITH_RUNTIME" -eq 1 ]]; then
        run_required_stage \
            "Isaac ROS interface validation" \
            "INTEGRATION" \
            "${SCRIPT_DIR}/validate_ros_interfaces.sh"
    else
        skip_stage \
            "Isaac ROS interface validation" \
            "runtime validation not requested; use --with-runtime"
    fi

    # 6. Final non-blocking environment fingerprint.
    run_optional_stage \
        "Environment post-check" \
        "SETUP" \
        "${SCRIPT_DIR}/validate_environment.sh"

    write_summary

    printf '\n[%s] PASS: requested setup/validation flow completed.\n' "$SCRIPT_NAME"
    printf '[%s] Logs: %s\n' "$SCRIPT_NAME" "$RUN_LOG_DIR"
}

main "$@"
