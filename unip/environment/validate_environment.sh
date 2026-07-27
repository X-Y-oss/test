#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
UNIP_SRC="${UNIP_SRC:-${WORKSPACE_ROOT}/src}"
GPD_ROOT="${GPD_ROOT:-${WORKSPACE_ROOT}/external/gpd}"
CUROBO_ROOT="${CUROBO_ROOT:-${WORKSPACE_ROOT}/external/curobo}"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"
CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.8}"

FAIL_COUNT=0
WARN_COUNT=0

pass() { printf '  [PASS] %s\n' "$*"; }
warn() { WARN_COUNT=$((WARN_COUNT + 1)); printf '  [WARN] %s\n' "$*" >&2; }
fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); printf '  [FAIL] %s\n' "$*" >&2; }
section() { printf '\n============================================================\n%s\n============================================================\n' "$1"; }

check_layout() {
    section "Workspace"
    [[ -d "$WORKSPACE_ROOT" ]] && pass "Workspace root exists." || fail "Workspace root missing."
    [[ -d "$UNIP_SRC" ]] && pass "UniP src exists." || fail "UniP src missing."
    [[ -d "$GPD_ROOT" ]] && pass "GPD source exists." || warn "GPD source not present yet."
    [[ -d "$CUROBO_ROOT" ]] && pass "cuRobo source exists." || warn "cuRobo source not present yet."
}

check_python() {
    section "Isaac Python"
    [[ -x "$PYTHON_BIN" ]] || { fail "Isaac Python missing: $PYTHON_BIN"; return; }

    set +e
    "$PYTHON_BIN" - <<'PY'
import platform, sys
print("  Executable :", sys.executable)
print("  Version    :", platform.python_version())
raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 10)
PY
    local rc=$?
    set -e
    [[ "$rc" -eq 0 ]] && pass "Isaac Python 3.11 contract valid." || fail "Expected Python 3.11."
}

check_ros() {
    section "ROS 2"
    printf '  ROS_DISTRO    : %s\n' "${ROS_DISTRO:-<unset>}"
    printf '  ROS_DOMAIN_ID : %s\n' "${ROS_DOMAIN_ID:-<unset>}"

    [[ "${ROS_DISTRO:-}" == "jazzy" ]] && pass "ROS_DISTRO is Jazzy." || warn "Jazzy environment not active yet."
    command -v ros2 >/dev/null 2>&1 && pass "ros2 CLI available." || warn "ros2 CLI unavailable yet."

    set +e
    "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import rclpy
PY
    local rc=$?
    set -e
    [[ "$rc" -eq 0 ]] && pass "Isaac Python imports rclpy." || warn "rclpy not importable yet."
}

check_gpu_torch() {
    section "GPU / Torch / CUDA"

    command -v nvidia-smi >/dev/null 2>&1 \
        && pass "nvidia-smi available." \
        || fail "nvidia-smi unavailable."

    set +e
    "$PYTHON_BIN" - <<'PY'
import shutil, torch
from torch.utils.cpp_extension import CUDA_HOME

print("  Torch          :", torch.__version__)
print("  Torch CUDA     :", torch.version.cuda)
print("  CUDA available :", torch.cuda.is_available())
print("  CUDA_HOME      :", CUDA_HOME)
print("  nvcc           :", shutil.which("nvcc"))
if torch.cuda.is_available():
    print("  GPU            :", torch.cuda.get_device_name(0))
    print("  Capability     :", torch.cuda.get_device_capability(0))
else:
    raise SystemExit(20)
PY
    local rc=$?
    set -e

    [[ "$rc" -eq 0 ]] && pass "Torch can access CUDA." || fail "Torch CUDA probe failed."
    command -v nvcc >/dev/null 2>&1 && pass "nvcc available." || warn "nvcc not installed yet."
    [[ -d "$CUDA_HOME" ]] && pass "CUDA_HOME directory exists." || warn "CUDA_HOME not present yet."
}

check_docker() {
    section "Docker helper"
    command -v docker >/dev/null 2>&1 || { warn "Docker CLI unavailable."; return; }
    pass "Docker CLI available."
    docker info >/dev/null 2>&1 && pass "Host Docker daemon reachable." || warn "Docker daemon not reachable."
}

summary() {
    section "Environment Validation Summary"
    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"
    [[ "$FAIL_COUNT" -eq 0 ]]
}

main() {
    check_layout
    check_python
    check_ros
    check_gpu_torch
    check_docker
    summary
}

main "$@"
