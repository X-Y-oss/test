#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP cuRobo installer / compatibility gate
#
# Purpose:
#   Prepare the project-specific BennoWingender/curobo fork in a reproducible,
#   explicit way without silently changing Torch or CUDA.
#
# Policy:
#   - Repository defaults to BennoWingender/curobo.
#   - CUROBO_COMMIT MUST be supplied explicitly before installation.
#   - Existing source trees are preserved; local modifications are never
#     overwritten automatically.
#   - Torch/CUDA/Python are inspected and reported, not "fixed" by this script.
#   - Installation is skipped if the requested commit is already checked out
#     and the expected legacy UniP cuRobo API imports successfully.
#
# Example:
#   export CUROBO_COMMIT=<known-good-sha>
#   ./environment/install_curobo.sh
#
# This script does NOT:
#   - install or downgrade Torch;
#   - install or downgrade CUDA;
#   - choose a cuRobo version automatically;
#   - run the full MotionGen/GPU functional validation.
# -----------------------------------------------------------------------------

CUROBO_REPO="${CUROBO_REPO:-https://github.com/BennoWingender/curobo.git}"
CUROBO_ROOT="${CUROBO_ROOT:-/workspace/external/curobo}"
CUROBO_COMMIT="${CUROBO_COMMIT:-}"

SCRIPT_NAME="$(basename "$0")"

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

on_error() {
    local exit_code=$?
    local line_no=${1:-unknown}

    printf '\n[%s] ERROR: command failed at line %s (exit code %s)\n' \
        "$SCRIPT_NAME" "$line_no" "$exit_code" >&2
    printf '[%s] CUROBO_ROOT=%s\n' "$SCRIPT_NAME" "$CUROBO_ROOT" >&2
    printf '[%s] CUROBO_COMMIT=%s\n' "$SCRIPT_NAME" "${CUROBO_COMMIT:-<unset>}" >&2
    exit "$exit_code"
}

trap 'on_error $LINENO' ERR


require_command() {
    local cmd="$1"
    command -v "$cmd" >/dev/null 2>&1 || fail "Required command not found: $cmd"
}


print_python_environment() {
    log "Python / Torch / CUDA environment:"

    python3 - <<'PY'
import platform
import shutil
import subprocess
import sys

print(f"  Python executable : {sys.executable}")
print(f"  Python version    : {platform.python_version()}")

try:
    import torch
except Exception as exc:
    print(f"  Torch             : NOT IMPORTABLE ({type(exc).__name__}: {exc})")
else:
    print(f"  Torch version     : {torch.__version__}")
    print(f"  torch CUDA build  : {torch.version.cuda}")
    try:
        print(f"  CUDA available    : {torch.cuda.is_available()}")
    except Exception as exc:
        print(f"  CUDA available    : ERROR ({type(exc).__name__}: {exc})")

    try:
        if torch.cuda.is_available():
            print(f"  CUDA device       : {torch.cuda.get_device_name(0)}")
    except Exception as exc:
        print(f"  CUDA device       : ERROR ({type(exc).__name__}: {exc})")

nvcc = shutil.which("nvcc")
if nvcc:
    print(f"  nvcc              : {nvcc}")
    try:
        result = subprocess.run(
            [nvcc, "--version"],
            check=False,
            capture_output=True,
            text=True,
        )
        output = (result.stdout or result.stderr).strip().splitlines()
        if output:
            print(f"  nvcc version      : {output[-1]}")
    except Exception as exc:
        print(f"  nvcc version      : ERROR ({type(exc).__name__}: {exc})")
else:
    print("  nvcc              : NOT FOUND")
PY
}


validate_requested_commit() {
    if [[ -z "$CUROBO_COMMIT" ]]; then
        fail "CUROBO_COMMIT is not set. Refusing to install an unpinned cuRobo revision."
    fi

    # Reject obvious floating references. We want a reproducible commit SHA.
    case "$CUROBO_COMMIT" in
        master|main|HEAD|latest)
            fail "CUROBO_COMMIT must be an exact commit SHA, not '$CUROBO_COMMIT'."
            ;;
    esac
}


ensure_source() {
    mkdir -p "$(dirname "$CUROBO_ROOT")"

    if [[ ! -e "$CUROBO_ROOT" ]]; then
        log "Cloning cuRobo repository..."
        git clone "$CUROBO_REPO" "$CUROBO_ROOT"
    elif [[ ! -d "${CUROBO_ROOT}/.git" ]]; then
        fail "CUROBO_ROOT exists but is not a Git repository: $CUROBO_ROOT"
    else
        local current_origin
        current_origin="$(git -C "$CUROBO_ROOT" remote get-url origin 2>/dev/null || true)"

        if [[ -n "$current_origin" && "$current_origin" != "$CUROBO_REPO" ]]; then
            warn "Existing cuRobo checkout uses a different origin."
            warn "Expected: $CUROBO_REPO"
            warn "Found:    $current_origin"
        fi

        log "Existing cuRobo checkout found: $CUROBO_ROOT"
    fi

    log "Fetching requested revision..."
    git -C "$CUROBO_ROOT" fetch --tags --prune origin

    if ! git -C "$CUROBO_ROOT" cat-file -e "${CUROBO_COMMIT}^{commit}" 2>/dev/null; then
        # A raw SHA may not be present locally after a shallow/limited fetch.
        log "Requested commit not present locally; attempting direct fetch..."
        git -C "$CUROBO_ROOT" fetch origin "$CUROBO_COMMIT" || true
    fi

    if ! git -C "$CUROBO_ROOT" cat-file -e "${CUROBO_COMMIT}^{commit}" 2>/dev/null; then
        fail "Requested cuRobo commit cannot be resolved: $CUROBO_COMMIT"
    fi
}


current_commit() {
    git -C "$CUROBO_ROOT" rev-parse HEAD 2>/dev/null || true
}


current_checkout_matches() {
    [[ -d "${CUROBO_ROOT}/.git" ]] || return 1

    local current expected
    current="$(current_commit)"
    expected="$(git -C "$CUROBO_ROOT" rev-parse "${CUROBO_COMMIT}^{commit}" 2>/dev/null || true)"

    [[ -n "$current" && -n "$expected" && "$current" == "$expected" ]]
}


checkout_requested_commit() {
    if current_checkout_matches; then
        log "Requested cuRobo commit is already checked out."
        return
    fi

    if [[ -n "$(git -C "$CUROBO_ROOT" status --porcelain)" ]]; then
        fail "cuRobo source tree has local modifications. Refusing to overwrite: $CUROBO_ROOT"
    fi

    log "Checking out cuRobo commit: $CUROBO_COMMIT"
    git -C "$CUROBO_ROOT" checkout --detach "$CUROBO_COMMIT"
}


legacy_api_imports_work() {
    python3 - <<'PY' >/dev/null 2>&1
import curobo
from curobo.types.robot import JointState
from curobo.wrap.reacher.motion_gen import (
    MotionGen,
    MotionGenConfig,
    MotionGenPlanConfig,
)
PY
}


already_ready() {
    current_checkout_matches && legacy_api_imports_work
}


install_curobo() {
    log "Installing cuRobo in editable mode..."
    log "This script will NOT alter Torch or CUDA."

    python3 -m pip install -e "$CUROBO_ROOT"
}


verify_imports() {
    log "Verifying legacy UniP cuRobo API imports..."

    python3 - <<'PY'
import curobo
from curobo.types.robot import JointState
from curobo.wrap.reacher.motion_gen import (
    MotionGen,
    MotionGenConfig,
    MotionGenPlanConfig,
)

print("  import curobo                                 PASS")
print("  curobo.types.robot.JointState                PASS")
print("  MotionGen / MotionGenConfig / PlanConfig      PASS")
PY
}


print_source_summary() {
    local commit
    commit="$(current_commit)"

    log "cuRobo source summary:"
    log "Repository : $CUROBO_REPO"
    log "Commit     : $commit"
    log "Source     : $CUROBO_ROOT"
}


main() {
    log "========================================"
    log "cuRobo installation / compatibility gate"
    log "========================================"

    require_command git
    require_command python3

    validate_requested_commit

    log "Repository : $CUROBO_REPO"
    log "Commit     : $CUROBO_COMMIT"
    log "Source     : $CUROBO_ROOT"

    print_python_environment

    # Torch is a real UniP/core dependency and a cuRobo prerequisite.
    if ! python3 - <<'PY' >/dev/null 2>&1
import torch
PY
    then
        fail "Torch is not importable. Install/freeze the Torch/CUDA compatibility profile before cuRobo."
    fi

    ensure_source
    checkout_requested_commit

    if already_ready; then
        log "Correct cuRobo commit and expected legacy API detected."
        log "SKIP: cuRobo is already ready."
        print_source_summary
        exit 0
    fi

    install_curobo
    verify_imports
    print_source_summary

    log "PASS: cuRobo installation/import gate completed."
    log "NOTE: GPU/MotionGen functional validation belongs to validate_curobo.sh."
}


main "$@"
