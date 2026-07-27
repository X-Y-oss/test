#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# Torch / CUDA compatibility gate for UniP + legacy cuRobo
#
# Validates the toolchain required before cuRobo's CUDA extensions are built.
# This script does not install or downgrade Torch or CUDA.
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"

FAIL_COUNT=0
WARN_COUNT=0

pass() { printf '  [PASS] %s\n' "$*"; }
warn() { WARN_COUNT=$((WARN_COUNT + 1)); printf '  [WARN] %s\n' "$*" >&2; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf '  [FAIL] %s\n' "$*" >&2; }

section() {
    printf '\n============================================================\n'
    printf '%s\n' "$1"
    printf '============================================================\n'
}

python_available() {
    [[ -x "$PYTHON_BIN" ]] || command -v "$PYTHON_BIN" >/dev/null 2>&1
}

check_python_torch() {
    section "T1 — Isaac Python / Torch"
    printf '  PYTHON_BIN          : %s\n' "$PYTHON_BIN"

    if ! python_available; then
        fail "Python runtime not found: $PYTHON_BIN"
        return
    fi

    set +e
    "$PYTHON_BIN" - <<'PY'
import platform
import sys

print(f"  Python version      : {platform.python_version()}")
print(f"  sys.executable      : {sys.executable}")

if sys.version_info[:2] != (3, 11):
    raise SystemExit(31)

try:
    import torch
except Exception as exc:
    print(f"  Torch import        : FAIL ({type(exc).__name__}: {exc})")
    raise SystemExit(32)

print(f"  Torch version       : {torch.__version__}")
print(f"  Torch CUDA build    : {torch.version.cuda}")
print(f"  CXX11 ABI           : {getattr(torch._C, '_GLIBCXX_USE_CXX11_ABI', '<unknown>')}")
PY
    local rc=$?
    set -e

    case "$rc" in
        0)  pass "Isaac Python 3.11 and Torch import are valid." ;;
        31) fail "Expected Python 3.11 for Isaac Sim 5.1." ;;
        32) fail "Torch is not importable in Isaac Python." ;;
        *)  fail "Unexpected Python/Torch probe failure (exit $rc)." ;;
    esac
}

check_cuda_runtime() {
    section "T2 — Torch CUDA Runtime / GPU"

    if ! python_available; then
        fail "Cannot inspect CUDA runtime because PYTHON_BIN is unavailable."
        return
    fi

    set +e
    "$PYTHON_BIN" - <<'PY'
try:
    import torch
except Exception:
    raise SystemExit(41)

try:
    available = torch.cuda.is_available()
except Exception as exc:
    print(f"  CUDA available      : ERROR ({type(exc).__name__}: {exc})")
    raise SystemExit(42)

print(f"  CUDA available      : {available}")
if not available:
    raise SystemExit(43)

print(f"  Device count        : {torch.cuda.device_count()}")
print(f"  GPU                 : {torch.cuda.get_device_name(0)}")
major, minor = torch.cuda.get_device_capability(0)
print(f"  Compute capability  : {major}.{minor}")
print(f"  Recommended arch    : {major}.{minor}")
PY
    local rc=$?
    set -e

    case "$rc" in
        0)  pass "Torch can access the CUDA GPU." ;;
        41) fail "Torch is unavailable, so CUDA runtime cannot be checked." ;;
        42) fail "Torch CUDA availability probe raised an exception." ;;
        43) fail "Torch is installed but CUDA is not available." ;;
        *)  fail "Unexpected CUDA runtime probe failure (exit $rc)." ;;
    esac
}

check_nvcc() {
    section "T3 — CUDA Toolkit / nvcc"

    if command -v nvcc >/dev/null 2>&1; then
        pass "nvcc is available."
        printf '  nvcc path           : %s\n' "$(command -v nvcc)"
        nvcc --version | tail -n 2 | sed 's/^/  /'
    else
        fail "nvcc is not available. cuRobo CUDA extensions cannot be compiled."
    fi

    if [[ -n "${CUDA_HOME:-}" ]]; then
        printf '  CUDA_HOME(shell)    : %s\n' "$CUDA_HOME"
    else
        warn "CUDA_HOME is not set in the shell; Torch will attempt auto-detection."
    fi
}

check_torch_build_contract() {
    section "T4 — Torch CUDA Build Contract"

    if ! python_available; then
        fail "Cannot inspect Torch build contract."
        return
    fi

    set +e
    "$PYTHON_BIN" - <<'PY'
import shutil
import subprocess

try:
    import torch
    from torch.utils.cpp_extension import CUDA_HOME
except Exception as exc:
    print(f"  cpp_extension       : FAIL ({type(exc).__name__}: {exc})")
    raise SystemExit(51)

print(f"  torch.version.cuda  : {torch.version.cuda}")
print(f"  CUDA_HOME(torch)    : {CUDA_HOME}")
print(f"  CXX11 ABI           : {getattr(torch._C, '_GLIBCXX_USE_CXX11_ABI', '<unknown>')}")

if torch.cuda.is_available():
    major, minor = torch.cuda.get_device_capability(0)
    print(f"  GPU arch            : {major}.{minor}")

nvcc = shutil.which("nvcc")
if nvcc:
    result = subprocess.run([nvcc, "--version"], capture_output=True, text=True)
    lines = (result.stdout or result.stderr).strip().splitlines()
    if lines:
        print(f"  nvcc                : {lines[-1]}")

if torch.version.cuda is None:
    raise SystemExit(52)
if CUDA_HOME is None:
    raise SystemExit(53)
PY
    local rc=$?
    set -e

    case "$rc" in
        0)  pass "Torch exposes CUDA build metadata and CUDA_HOME." ;;
        51) fail "torch.utils.cpp_extension cannot be imported." ;;
        52) fail "Installed Torch is not a CUDA build." ;;
        53) fail "Torch cannot locate CUDA_HOME / CUDA toolkit." ;;
        *)  fail "Unexpected Torch build-contract failure (exit $rc)." ;;
    esac
}

print_summary() {
    section "Torch / CUDA Gate Summary"
    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"

    if [[ "$FAIL_COUNT" -gt 0 ]]; then
        printf '\nRESULT: FAIL [CUROBO TOOLCHAIN GATE]\n'
        return 1
    fi

    if [[ "$WARN_COUNT" -gt 0 ]]; then
        printf '\nRESULT: PASS WITH WARNINGS\n'
    else
        printf '\nRESULT: PASS\n'
    fi
}

main() {
    printf '========================================================================\n'
    printf 'UniP Torch / CUDA Compatibility Gate\n'
    printf '========================================================================\n'

    check_python_torch
    check_cuda_runtime
    check_nvcc
    check_torch_build_contract
    print_summary
}

main "$@"
