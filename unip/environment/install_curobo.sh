#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"
CUROBO_REPO="${CUROBO_REPO:-https://github.com/BennoWingender/curobo.git}"
CUROBO_ROOT="${CUROBO_ROOT:-/workspace/external/curobo}"
CUROBO_COMMIT="${CUROBO_COMMIT:-}"

log() { printf '[%s] %s\n' "$SCRIPT_NAME" "$*"; }
fail() { printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

validate_contract() {
    [[ -x "$PYTHON_BIN" ]] || fail "Isaac Python missing: $PYTHON_BIN"
    [[ -n "$CUROBO_COMMIT" ]] || fail "CUROBO_COMMIT is not set."
    case "$CUROBO_COMMIT" in
        master|main|HEAD|latest) fail "CUROBO_COMMIT must be an exact SHA." ;;
    esac
    "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1 || fail "Torch/CUDA unavailable in Isaac Python."
import torch
assert torch.cuda.is_available()
PY
}

ensure_source() {
    mkdir -p "$(dirname "$CUROBO_ROOT")"
    if [[ ! -e "$CUROBO_ROOT" ]]; then
        git clone "$CUROBO_REPO" "$CUROBO_ROOT"
    elif [[ ! -d "${CUROBO_ROOT}/.git" ]]; then
        fail "CUROBO_ROOT is not a Git repo: $CUROBO_ROOT"
    fi

    git -C "$CUROBO_ROOT" fetch --tags --prune origin
    git -C "$CUROBO_ROOT" cat-file -e "${CUROBO_COMMIT}^{commit}" 2>/dev/null ||
        git -C "$CUROBO_ROOT" fetch origin "$CUROBO_COMMIT" || true
    git -C "$CUROBO_ROOT" cat-file -e "${CUROBO_COMMIT}^{commit}" 2>/dev/null ||
        fail "Cannot resolve commit: $CUROBO_COMMIT"
}

checkout_commit() {
    local current expected
    current="$(git -C "$CUROBO_ROOT" rev-parse HEAD 2>/dev/null || true)"
    expected="$(git -C "$CUROBO_ROOT" rev-parse "${CUROBO_COMMIT}^{commit}")"
    [[ "$current" == "$expected" ]] && return

    [[ -z "$(git -C "$CUROBO_ROOT" status --porcelain)" ]] ||
        fail "cuRobo source has local changes."
    git -C "$CUROBO_ROOT" checkout --detach "$CUROBO_COMMIT"
}

legacy_api_ok() {
    "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import curobo
from curobo.types.robot import JointState
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig, MotionGenPlanConfig
PY
}

configure_cuda_arch() {
    [[ -n "${TORCH_CUDA_ARCH_LIST:-}" ]] && return
    export TORCH_CUDA_ARCH_LIST="$("$PYTHON_BIN" - <<'PY'
import torch
major, minor = torch.cuda.get_device_capability(0)
print(f"{major}.{minor}")
PY
)"
    log "TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST}"
}

main() {
    validate_contract
    ensure_source
    checkout_commit

    if legacy_api_ok; then
        log "SKIP: requested cuRobo revision and legacy API already ready."
        exit 0
    fi

    configure_cuda_arch
    "$PYTHON_BIN" -m pip install -e "$CUROBO_ROOT" --no-build-isolation

    legacy_api_ok || fail "Legacy cuRobo API import failed after installation."
    log "PASS: cuRobo installed with Isaac Python."
}

main "$@"
