#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"

CUROBO_REPO="${CUROBO_REPO:-https://github.com/BennoWingender/curobo.git}"
CUROBO_ROOT="${CUROBO_ROOT:-${WORKSPACE_ROOT}/external/curobo}"
CUROBO_COMMIT="${CUROBO_COMMIT:-d64c4b005459db10c5dd867d8b30a87d5bda9bdb}"
CUROBO_REQUIREMENTS="${CUROBO_REQUIREMENTS:-${WORKSPACE_ROOT}/requirements/curobo.txt}"

log() {
    printf '[%s] %s\n' "$SCRIPT_NAME" "$*"
}


fail() {
    printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2
    exit 1
}


validate_contract() {
    [[ -x "$PYTHON_BIN" ]] ||
        fail "Isaac Python missing: $PYTHON_BIN"

    [[ -n "$CUROBO_COMMIT" ]] ||
        fail "CUROBO_COMMIT is not set."

    case "$CUROBO_COMMIT" in
        master|main|HEAD|latest)
            fail "CUROBO_COMMIT must be an exact SHA."
            ;;
    esac

    [[ -f "$CUROBO_REQUIREMENTS" ]] ||
        fail "cuRobo requirements file not found: $CUROBO_REQUIREMENTS"

    if ! "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import torch

assert torch.cuda.is_available()
assert torch.version.cuda is not None
PY
    then
        fail "Torch/CUDA unavailable in Isaac Python."
    fi
}


ensure_source() {
    mkdir -p "$(dirname "$CUROBO_ROOT")"

    if [[ ! -e "$CUROBO_ROOT" ]]; then
        git clone "$CUROBO_REPO" "$CUROBO_ROOT"

    elif [[ ! -d "${CUROBO_ROOT}/.git" ]]; then
        fail "CUROBO_ROOT is not a Git repo: $CUROBO_ROOT"
    fi

    git -C "$CUROBO_ROOT" fetch \
        --tags \
        --prune \
        origin

    if ! git -C "$CUROBO_ROOT" \
        cat-file -e "${CUROBO_COMMIT}^{commit}" \
        2>/dev/null; then

        git -C "$CUROBO_ROOT" \
            fetch origin "$CUROBO_COMMIT" || true
    fi

    git -C "$CUROBO_ROOT" \
        cat-file -e "${CUROBO_COMMIT}^{commit}" \
        2>/dev/null ||
        fail "Cannot resolve commit: $CUROBO_COMMIT"
}


checkout_commit() {
    local current
    local expected

    current="$(
        git -C "$CUROBO_ROOT" \
            rev-parse HEAD \
            2>/dev/null || true
    )"

    expected="$(
        git -C "$CUROBO_ROOT" \
            rev-parse "${CUROBO_COMMIT}^{commit}"
    )"

    if [[ "$current" == "$expected" ]]; then
        return
    fi

    [[ -z "$(git -C "$CUROBO_ROOT" status --porcelain)" ]] ||
        fail "cuRobo source has local changes."

    git -C "$CUROBO_ROOT" \
        checkout --detach "$CUROBO_COMMIT"
}


legacy_api_ok() {
    "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import warp
import yourdfpy
import curobo

from curobo.types.robot import JointState
from curobo.wrap.reacher.motion_gen import (
    MotionGen,
    MotionGenConfig,
    MotionGenPlanConfig,
)
PY
}


configure_cuda_arch() {
    if [[ -n "${TORCH_CUDA_ARCH_LIST:-}" ]]; then
        log "Using existing TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST}"
        return
    fi

    export TORCH_CUDA_ARCH_LIST="$(
        "$PYTHON_BIN" - <<'PY'
import torch

major, minor = torch.cuda.get_device_capability(0)
print(f"{major}.{minor}")
PY
    )"

    log "TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST}"
}


install_runtime_dependencies() {
    log "Installing pinned cuRobo runtime dependencies..."

    "$PYTHON_BIN" -m pip install \
        --disable-pip-version-check \
        --no-deps \
        -r "$CUROBO_REQUIREMENTS"
}


install_curobo() {
    configure_cuda_arch

    log "Installing pinned cuRobo revision..."

    "$PYTHON_BIN" -m pip install \
        --disable-pip-version-check \
        --no-deps \
        --no-build-isolation \
        -e "$CUROBO_ROOT"
}


main() {
    validate_contract
    ensure_source
    checkout_commit

    if legacy_api_ok; then
        log "SKIP: requested cuRobo revision and legacy API already ready."
        exit 0
    fi

    install_runtime_dependencies
    install_curobo

    legacy_api_ok ||
        fail "Legacy cuRobo API import failed after installation."

    log "PASS: cuRobo installed with Isaac Python."
}


main "$@"