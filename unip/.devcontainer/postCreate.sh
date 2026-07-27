#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP devcontainer post-create bootstrap
#
# Purpose:
#   Keep VS Code's automatic postCreate step thin and predictable.
#
# Responsibilities:
#   - verify that the expected repository layout exists;
#   - ensure environment scripts are executable;
#   - create the runtime log directory;
#   - run the environment orchestrator in installation mode when a pinned
#     CUROBO_COMMIT is provided;
#   - otherwise stop safely with a clear message instead of installing an
#     unpinned cuRobo revision.
#
# Heavy setup logic lives in:
#   environment/setup_and_validate.sh
#
# This file deliberately does NOT contain:
#   - apt package installation;
#   - ROS workspace build logic;
#   - GPD build logic;
#   - Torch/CUDA selection;
#   - cuRobo source selection;
#   - colcon build commands.
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
ENV_DIR="${ENV_DIR:-${WORKSPACE_ROOT}/environment}"
REQUIREMENTS_DIR="${REQUIREMENTS_DIR:-${WORKSPACE_ROOT}/requirements}"

ORCHESTRATOR="${ENV_DIR}/setup_and_validate.sh"
LOG_DIR="${ENV_DIR}/logs"

# Optional policy control:
#   POSTCREATE_VALIDATE_ONLY=1
#       Never install; only validate an already-prepared environment.
#
#   POSTCREATE_SKIP_SETUP=1
#       Do not run setup_and_validate.sh automatically at all.
#
# Default behavior:
#   - with CUROBO_COMMIT set -> full setup + validation
#   - without CUROBO_COMMIT -> bootstrap only, print the exact next command
POSTCREATE_VALIDATE_ONLY="${POSTCREATE_VALIDATE_ONLY:-0}"
POSTCREATE_SKIP_SETUP="${POSTCREATE_SKIP_SETUP:-0}"


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


check_layout() {
    log "Checking UniP workspace layout..."

    [[ -d "$WORKSPACE_ROOT" ]] ||
        fail "Workspace root does not exist: $WORKSPACE_ROOT"

    [[ -d "${WORKSPACE_ROOT}/src" ]] ||
        fail "Expected ROS source directory is missing: ${WORKSPACE_ROOT}/src"

    [[ -d "$ENV_DIR" ]] ||
        fail "Environment directory is missing: $ENV_DIR"

    [[ -d "$REQUIREMENTS_DIR" ]] ||
        fail "Requirements directory is missing: $REQUIREMENTS_DIR"

    [[ -f "$ORCHESTRATOR" ]] ||
        fail "Environment orchestrator is missing: $ORCHESTRATOR"

    [[ -f "${REQUIREMENTS_DIR}/core.txt" ]] ||
        fail "Core requirements file is missing: ${REQUIREMENTS_DIR}/core.txt"

    log "Workspace layout looks valid."
}


prepare_environment_directory() {
    log "Preparing environment helper scripts..."

    mkdir -p "$LOG_DIR"

    # Git may not preserve executable bits depending on how the repository was
    # copied or checked out, so normalize them here.
    find "$ENV_DIR" \
        -maxdepth 1 \
        -type f \
        -name '*.sh' \
        -exec chmod +x {} +

    log "Environment shell scripts marked executable."
    log "Log directory: $LOG_DIR"
}


print_runtime_contract() {
    log "Runtime contract:"
    log "  WORKSPACE_ROOT=${WORKSPACE_ROOT}"
    log "  PYTHON_BIN=${PYTHON_BIN:-<unset>}"
    log "  ROS_DISTRO_TARGET=${ROS_DISTRO_TARGET:-<unset>}"
    log "  ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-<unset>}"
    log "  GPD_ROOT=${GPD_ROOT:-<unset>}"
    log "  CUROBO_ROOT=${CUROBO_ROOT:-<unset>}"
    log "  ISAAC_ROS_WS_ROOT=${ISAAC_ROS_WS_ROOT:-<unset>}"
    log "  CUROBO_COMMIT=${CUROBO_COMMIT:-<unset>}"
}


run_orchestrator() {
    if [[ "$POSTCREATE_SKIP_SETUP" == "1" ]]; then
        warn "POSTCREATE_SKIP_SETUP=1: automatic environment setup skipped."
        warn "Run manually when ready:"
        warn "  ${ORCHESTRATOR}"
        return 0
    fi

    if [[ "$POSTCREATE_VALIDATE_ONLY" == "1" ]]; then
        log "POSTCREATE_VALIDATE_ONLY=1: running validation only."
        "$ORCHESTRATOR" --validate-only
        return 0
    fi

    if [[ -z "${CUROBO_COMMIT:-}" ]]; then
        cat <<EOF

[$SCRIPT_NAME] Bootstrap completed, but full environment setup was NOT started.

Reason:
  CUROBO_COMMIT is not set.

This is intentional. The clean environment refuses to install an unpinned
cuRobo revision.

Next step:
  export CUROBO_COMMIT=<known-good-Benno-curobo-commit>
  ${ORCHESTRATOR}

To validate an already-prepared environment instead:
  ${ORCHESTRATOR} --validate-only

EOF
        return 0
    fi

    log "Pinned cuRobo commit provided; starting full setup + validation."
    "$ORCHESTRATOR"
}


main() {
    printf '========================================================================\n'
    printf 'UniP Devcontainer Post-Create Bootstrap\n'
    printf '========================================================================\n'

    check_layout
    prepare_environment_directory
    print_runtime_contract
    run_orchestrator

    printf '\n[%s] postCreate bootstrap finished.\n' "$SCRIPT_NAME"
}


main "$@"
