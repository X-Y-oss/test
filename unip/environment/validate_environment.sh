#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP environment validator
#
# Purpose:
#   Produce a compact, human-readable environment fingerprint before any
#   functional validation. This script is read-only.
#
# It checks:
#   - workspace paths
#   - Python
#   - ROS distro/domain
#   - GPU visibility
#   - Torch/CUDA state
#   - nvcc availability
#   - Isaac Sim installation hints
#   - key source directories
#
# Exit policy:
#   - hard prerequisites missing -> exit 1
#   - optional/diagnostic items missing -> warning only
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
UNIP_SRC="${UNIP_SRC:-${WORKSPACE_ROOT}/src}"
GPD_ROOT="${GPD_ROOT:-${WORKSPACE_ROOT}/external/gpd}"
CUROBO_ROOT="${CUROBO_ROOT:-${WORKSPACE_ROOT}/external/curobo}"

FAIL_COUNT=0
WARN_COUNT=0

log() {
    printf '[%s] %s\n' "$SCRIPT_NAME" "$*"
}

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

command_exists() {
    command -v "$1" >/dev/null 2>&1
}


check_paths() {
    section "Workspace / Paths"

    printf '  WORKSPACE_ROOT : %s\n' "$WORKSPACE_ROOT"
    printf '  UNIP_SRC       : %s\n' "$UNIP_SRC"
    printf '  GPD_ROOT       : %s\n' "$GPD_ROOT"
    printf '  CUROBO_ROOT    : %s\n' "$CUROBO_ROOT"

    if [[ -d "$WORKSPACE_ROOT" ]]; then
        pass "Workspace root exists."
    else
        fail "Workspace root does not exist: $WORKSPACE_ROOT"
    fi

    if [[ -d "$UNIP_SRC" ]]; then
        pass "UniP src directory exists."
    else
        fail "UniP src directory does not exist: $UNIP_SRC"
    fi

    if [[ -d "$GPD_ROOT" ]]; then
        pass "GPD source directory exists."
    else
        warn "GPD source directory not present yet: $GPD_ROOT"
    fi

    if [[ -d "$CUROBO_ROOT" ]]; then
        pass "cuRobo source directory exists."
    else
        warn "cuRobo source directory not present yet: $CUROBO_ROOT"
    fi
}


check_python() {
    section "Python"

    if ! command_exists python3; then
        fail "python3 not found."
        return
    fi

    local py_exec py_version
    py_exec="$(command -v python3)"
    py_version="$(python3 -c 'import platform; print(platform.python_version())')"

    printf '  Executable : %s\n' "$py_exec"
    printf '  Version    : %s\n' "$py_version"
    pass "Python is available."
}


check_ros() {
    section "ROS 2"

    local ros_distro="${ROS_DISTRO:-<unset>}"
    local ros_domain="${ROS_DOMAIN_ID:-<unset>}"
    local rmw="${RMW_IMPLEMENTATION:-<default/unset>}"

    printf '  ROS_DISTRO         : %s\n' "$ros_distro"
    printf '  ROS_DOMAIN_ID      : %s\n' "$ros_domain"
    printf '  RMW_IMPLEMENTATION : %s\n' "$rmw"

    if [[ "${ROS_DISTRO:-}" == "jazzy" ]]; then
        pass "ROS_DISTRO is Jazzy."
    elif [[ -n "${ROS_DISTRO:-}" ]]; then
        warn "ROS_DISTRO is '${ROS_DISTRO}', not the Option-A target 'jazzy'."
    else
        warn "ROS_DISTRO is not set."
    fi

    if command_exists ros2; then
        pass "ros2 CLI is available."
    else
        warn "ros2 CLI not found in PATH."
    fi

    if python3 - <<'PY' >/dev/null 2>&1
import rclpy
PY
    then
        pass "Python can import rclpy."
    else
        warn "Python cannot import rclpy."
    fi
}


check_gpu() {
    section "GPU / NVIDIA"

    if command_exists nvidia-smi; then
        pass "nvidia-smi is available."
        nvidia-smi --query-gpu=name,driver_version,memory.total \
            --format=csv,noheader 2>/dev/null \
            | sed 's/^/  GPU        : /' \
            || warn "nvidia-smi query failed."
    else
        fail "nvidia-smi not found; NVIDIA GPU visibility cannot be verified."
    fi
}


check_torch_cuda() {
    section "Torch / CUDA"

    if ! command_exists python3; then
        fail "Cannot inspect Torch because python3 is unavailable."
        return
    fi

    python3 - <<'PY'
import shutil
import subprocess
import sys

try:
    import torch
except Exception as exc:
    print(f"  Torch import : FAIL ({type(exc).__name__}: {exc})")
    sys.exit(20)

print(f"  Torch version    : {torch.__version__}")
print(f"  torch CUDA build : {torch.version.cuda}")

try:
    available = torch.cuda.is_available()
except Exception as exc:
    print(f"  CUDA available   : ERROR ({type(exc).__name__}: {exc})")
    sys.exit(21)

print(f"  CUDA available   : {available}")

if available:
    try:
        print(f"  CUDA device      : {torch.cuda.get_device_name(0)}")
    except Exception as exc:
        print(f"  CUDA device      : ERROR ({type(exc).__name__}: {exc})")

nvcc = shutil.which("nvcc")
if nvcc:
    print(f"  nvcc             : {nvcc}")
    try:
        result = subprocess.run(
            [nvcc, "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
        lines = (result.stdout or result.stderr).strip().splitlines()
        if lines:
            print(f"  nvcc version     : {lines[-1]}")
    except Exception as exc:
        print(f"  nvcc version     : ERROR ({type(exc).__name__}: {exc})")
else:
    print("  nvcc             : NOT FOUND")
PY
    local rc=$?

    case "$rc" in
        0)
            pass "Torch imported successfully."
            ;;
        20)
            warn "Torch is not importable yet."
            ;;
        21)
            warn "Torch imported, but CUDA availability check raised an error."
            ;;
        *)
            warn "Torch/CUDA probe returned unexpected code: $rc"
            ;;
    esac

    if command_exists nvcc; then
        pass "nvcc is available."
    else
        warn "nvcc is not available. cuRobo source-extension build may require a toolkit later."
    fi
}


check_isaac() {
    section "Isaac Sim"

    local found=0

    if [[ -n "${ISAACSIM_PATH:-}" ]]; then
        printf '  ISAACSIM_PATH : %s\n' "$ISAACSIM_PATH"
        if [[ -e "$ISAACSIM_PATH" ]]; then
            pass "ISAACSIM_PATH exists."
            found=1
        else
            warn "ISAACSIM_PATH is set but does not exist."
        fi
    fi

    # Common Isaac Sim container locations.
    local candidate
    for candidate in \
        /isaac-sim \
        /opt/isaac-sim \
        /root/.local/share/ov/pkg/isaac-sim-*; do

        # shellcheck disable=SC2086
        for expanded in $candidate; do
            if [[ -d "$expanded" ]]; then
                printf '  Candidate     : %s\n' "$expanded"
                pass "Isaac Sim installation candidate found."
                found=1
            fi
        done
    done

    if command_exists isaac-sim.sh; then
        printf '  isaac-sim.sh  : %s\n' "$(command -v isaac-sim.sh)"
        pass "isaac-sim.sh is in PATH."
        found=1
    fi

    if [[ "$found" -eq 0 ]]; then
        warn "Isaac Sim installation was not detected by common path checks."
    fi
}


check_key_files() {
    section "Key UniP Sources"

    local key_files=(
        "${UNIP_SRC}/placeability_scoring/placeability_scoring/UP4_Pipeline_curobo.py"
        "${UNIP_SRC}/placeability_scoring/placeability_scoring/environment_config.py"
        "${UNIP_SRC}/placeability_scoring/placeability_scoring/planning/Curobo_Planner.py"
        "${UNIP_SRC}/placeability_scoring/placeability_scoring/planning/UR5e_Interface_curobo.py"
        "${UNIP_SRC}/gpd_ros/CMakeLists.txt"
    )

    local path
    for path in "${key_files[@]}"; do
        if [[ -f "$path" ]]; then
            pass "$path"
        else
            warn "Missing expected source file: $path"
        fi
    done
}


print_summary() {
    section "Environment Validation Summary"

    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"

    if [[ "$FAIL_COUNT" -gt 0 ]]; then
        printf '\nRESULT: FAIL [SETUP]\n'
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
    printf 'UniP Environment Validation\n'
    printf '========================================================================\n'

    check_paths
    check_python
    check_ros
    check_gpu
    check_torch_cuda
    check_isaac
    check_key_files
    print_summary
}


main "$@"
