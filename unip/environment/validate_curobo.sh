#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
CUROBO_ROOT="${CUROBO_ROOT:-${WORKSPACE_ROOT}/external/curobo}"
CUROBO_COMMIT="${CUROBO_COMMIT:-}"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"

FAIL_COUNT=0
WARN_COUNT=0

pass() { printf '  [PASS] %s\n' "$*"; }
warn() { WARN_COUNT=$((WARN_COUNT + 1)); printf '  [WARN] %s\n' "$*" >&2; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf '  [FAIL] %s\n' "$*" >&2; }
section() { printf '\n============================================================\n%s\n============================================================\n' "$1"; }

check_environment() {
    section "A1 — Isaac Python / Torch / CUDA"
    [[ -x "$PYTHON_BIN" ]] || { fail "Isaac Python missing: $PYTHON_BIN"; return; }

    set +e
    "$PYTHON_BIN" - <<'PY'
import platform, shutil, torch
from torch.utils.cpp_extension import CUDA_HOME

print("  Python         :", platform.python_version())
print("  Torch          :", torch.__version__)
print("  Torch CUDA     :", torch.version.cuda)
print("  CUDA available :", torch.cuda.is_available())
print("  CUDA_HOME      :", CUDA_HOME)
print("  nvcc           :", shutil.which("nvcc"))

if not torch.cuda.is_available():
    raise SystemExit(20)
if torch.version.cuda != "12.8":
    raise SystemExit(21)
if CUDA_HOME is None:
    raise SystemExit(22)

print("  GPU            :", torch.cuda.get_device_name(0))
print("  Capability     :", torch.cuda.get_device_capability(0))
PY
    local rc=$?
    set -e

    case "$rc" in
        0) pass "Isaac Python/Torch/CUDA contract is valid." ;;
        20) fail "Torch cannot access CUDA." ;;
        21) fail "Torch CUDA build is not 12.8." ;;
        22) fail "Torch cannot locate CUDA_HOME." ;;
        *) fail "Environment probe failed (exit $rc)." ;;
    esac

    command -v nvcc >/dev/null 2>&1 && pass "nvcc available." || fail "nvcc missing."
}

check_source_and_api() {
    section "A2/A3 — cuRobo source and legacy API"

    [[ -d "$CUROBO_ROOT" ]] || { fail "CUROBO_ROOT missing: $CUROBO_ROOT"; return; }

    if [[ -d "${CUROBO_ROOT}/.git" ]]; then
        local current
        current="$(git -C "$CUROBO_ROOT" rev-parse HEAD 2>/dev/null || true)"
        printf '  Current commit : %s\n' "${current:-<unknown>}"

        if [[ -n "$CUROBO_COMMIT" ]]; then
            local expected
            expected="$(git -C "$CUROBO_ROOT" rev-parse "${CUROBO_COMMIT}^{commit}" 2>/dev/null || true)"
            [[ -n "$expected" && "$current" == "$expected" ]] \
                && pass "Revision matches CUROBO_COMMIT." \
                || fail "Revision does not match CUROBO_COMMIT."
        else
            warn "CUROBO_COMMIT unset; exact revision not verified."
        fi
    fi

    set +e
    "$PYTHON_BIN" - <<'PY'
import curobo
from curobo.types.robot import JointState
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig, MotionGenPlanConfig

print("  import curobo              PASS")
print("  JointState                 PASS")
print("  MotionGen                  PASS")
print("  MotionGenConfig            PASS")
print("  MotionGenPlanConfig        PASS")
PY
    local rc=$?
    set -e

    [[ "$rc" -eq 0 ]] && pass "Legacy UniP cuRobo API imports." || fail "Legacy cuRobo API import failed."
}

check_gpu_compute() {
    section "A4 — GPU functional probe"

    set +e
    "$PYTHON_BIN" - <<'PY'
import torch
x = torch.arange(4096, device="cuda", dtype=torch.float32)
value = x.square().sum().item()
torch.cuda.synchronize()
print("  Device :", torch.cuda.get_device_name(0))
print("  Result :", value)
raise SystemExit(0 if value > 0 else 40)
PY
    local rc=$?
    set -e

    [[ "$rc" -eq 0 ]] && pass "Torch CUDA computation succeeded." || fail "Torch CUDA computation failed."
}

summary() {
    section "cuRobo Validation Summary"
    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"
    [[ "$FAIL_COUNT" -eq 0 ]]
}

main() {
    check_environment
    check_source_and_api
    check_gpu_compute
    summary
}

main "$@"
