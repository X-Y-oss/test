#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP cuRobo validator
#
# Gate A validation levels
# ------------------------
# A1  Environment:
#     - Python
#     - Torch import
#     - CUDA availability
#     - nvcc visibility (warning if absent)
#
# A2  Source/install:
#     - CUROBO_ROOT exists
#     - source commit matches CUROBO_COMMIT when provided
#     - curobo imports successfully
#
# A3  Legacy UniP API:
#     - JointState
#     - MotionGen
#     - MotionGenConfig
#     - MotionGenPlanConfig
#
# A4  Functional GPU probe:
#     - default: Torch CUDA tensor computation
#     - optional --motiongen: attempt MotionGen initialization using a robot YAML
#
# This script is read-only and does not install or modify Torch/CUDA/cuRobo.
#
# Typical usage:
#   ./environment/validate_curobo.sh
#
# Optional MotionGen initialization:
#   ./environment/validate_curobo.sh \
#       --motiongen \
#       --robot-config /workspace/src/.../ur5e_robotiq_2f_85.yml
#
# Environment overrides:
#   CUROBO_ROOT=/workspace/external/curobo
#   CUROBO_COMMIT=<known-good-sha>
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
CUROBO_ROOT="${CUROBO_ROOT:-${WORKSPACE_ROOT}/external/curobo}"
CUROBO_COMMIT="${CUROBO_COMMIT:-}"

RUN_MOTIONGEN=0
ROBOT_CONFIG="${ROBOT_CONFIG:-}"

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
  $SCRIPT_NAME [--motiongen] [--robot-config PATH]

Options:
  --motiongen           Attempt cuRobo MotionGen initialization.
  --robot-config PATH   Robot YAML used for MotionGen initialization.
  -h, --help            Show this help.

Environment:
  CUROBO_ROOT           Default: /workspace/external/curobo
  CUROBO_COMMIT         Expected exact cuRobo commit (optional for validation,
                        but recommended for reproducibility).
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --motiongen)
                RUN_MOTIONGEN=1
                ;;
            --robot-config)
                shift
                [[ $# -gt 0 ]] || {
                    printf '[%s] ERROR: --robot-config requires a path\n' "$SCRIPT_NAME" >&2
                    exit 2
                }
                ROBOT_CONFIG="$1"
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


check_environment() {
    section "A1 — Python / Torch / CUDA"

    if ! command -v python3 >/dev/null 2>&1; then
        fail "python3 is not available."
        return
    fi

    printf '  Python executable : %s\n' "$(command -v python3)"
    printf '  Python version    : %s\n' "$(python3 -c 'import platform; print(platform.python_version())')"

    set +e
    python3 - <<'PY'
import shutil
import subprocess
import sys

try:
    import torch
except Exception as exc:
    print(f"  Torch             : FAIL ({type(exc).__name__}: {exc})")
    sys.exit(20)

print(f"  Torch version     : {torch.__version__}")
print(f"  torch CUDA build  : {torch.version.cuda}")

try:
    available = torch.cuda.is_available()
except Exception as exc:
    print(f"  CUDA available    : ERROR ({type(exc).__name__}: {exc})")
    sys.exit(21)

print(f"  CUDA available    : {available}")

if not available:
    sys.exit(22)

try:
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
        lines = (result.stdout or result.stderr).strip().splitlines()
        if lines:
            print(f"  nvcc version      : {lines[-1]}")
    except Exception as exc:
        print(f"  nvcc version      : ERROR ({type(exc).__name__}: {exc})")
else:
    print("  nvcc              : NOT FOUND")
PY
    local rc=$?
    set -e

    case "$rc" in
        0)
            pass "Torch imported and CUDA is available."
            ;;
        20)
            fail "Torch is not importable."
            ;;
        21)
            fail "Torch imported, but CUDA availability check raised an error."
            ;;
        22)
            fail "Torch imported, but torch.cuda.is_available() is False."
            ;;
        *)
            fail "Unexpected Torch/CUDA probe exit code: $rc"
            ;;
    esac

    if command -v nvcc >/dev/null 2>&1; then
        pass "nvcc is available."
    else
        warn "nvcc is not available. This matters if cuRobo extensions need source compilation."
    fi
}


check_source_revision() {
    section "A2 — cuRobo Source / Installation"

    printf '  CUROBO_ROOT   : %s\n' "$CUROBO_ROOT"
    printf '  CUROBO_COMMIT : %s\n' "${CUROBO_COMMIT:-<unset>}"

    if [[ ! -d "$CUROBO_ROOT" ]]; then
        fail "cuRobo source directory does not exist: $CUROBO_ROOT"
        return
    fi

    pass "cuRobo source directory exists."

    if [[ -d "${CUROBO_ROOT}/.git" ]]; then
        local current
        current="$(git -C "$CUROBO_ROOT" rev-parse HEAD 2>/dev/null || true)"
        printf '  Source commit : %s\n' "${current:-<unknown>}"

        if [[ -z "$CUROBO_COMMIT" ]]; then
            warn "CUROBO_COMMIT is not set; reproducible revision cannot be verified."
        else
            local expected
            expected="$(git -C "$CUROBO_ROOT" rev-parse "${CUROBO_COMMIT}^{commit}" 2>/dev/null || true)"
            if [[ -n "$current" && -n "$expected" && "$current" == "$expected" ]]; then
                pass "cuRobo source commit matches CUROBO_COMMIT."
            else
                fail "cuRobo source commit does not match CUROBO_COMMIT."
            fi
        fi

        if [[ -n "$(git -C "$CUROBO_ROOT" status --porcelain 2>/dev/null)" ]]; then
            warn "cuRobo source tree has local modifications."
        else
            pass "cuRobo source tree is clean."
        fi
    else
        warn "CUROBO_ROOT is not a Git checkout; revision cannot be verified."
    fi

    set +e
    python3 - <<'PY'
try:
    import curobo
except Exception as exc:
    print(f"  import curobo      : FAIL ({type(exc).__name__}: {exc})")
    raise SystemExit(30)

print("  import curobo      : PASS")
PY
    local rc=$?
    set -e

    if [[ "$rc" -eq 0 ]]; then
        pass "cuRobo Python package is importable."
    else
        fail "cuRobo Python package is not importable."
    fi
}


check_legacy_api() {
    section "A3 — Legacy UniP cuRobo API"

    set +e
    python3 - <<'PY'
checks = []

try:
    from curobo.types.robot import JointState
    checks.append(("curobo.types.robot.JointState", True, ""))
except Exception as exc:
    checks.append(("curobo.types.robot.JointState", False, f"{type(exc).__name__}: {exc}"))

try:
    from curobo.wrap.reacher.motion_gen import MotionGen
    checks.append(("MotionGen", True, ""))
except Exception as exc:
    checks.append(("MotionGen", False, f"{type(exc).__name__}: {exc}"))

try:
    from curobo.wrap.reacher.motion_gen import MotionGenConfig
    checks.append(("MotionGenConfig", True, ""))
except Exception as exc:
    checks.append(("MotionGenConfig", False, f"{type(exc).__name__}: {exc}"))

try:
    from curobo.wrap.reacher.motion_gen import MotionGenPlanConfig
    checks.append(("MotionGenPlanConfig", True, ""))
except Exception as exc:
    checks.append(("MotionGenPlanConfig", False, f"{type(exc).__name__}: {exc}"))

failed = False
for name, ok, detail in checks:
    if ok:
        print(f"  {name:<42} PASS")
    else:
        failed = True
        print(f"  {name:<42} FAIL ({detail})")

raise SystemExit(31 if failed else 0)
PY
    local rc=$?
    set -e

    if [[ "$rc" -eq 0 ]]; then
        pass "All legacy UniP cuRobo API imports succeeded."
    else
        fail "One or more legacy UniP cuRobo API imports failed."
    fi
}


check_torch_gpu_operation() {
    section "A4a — Torch GPU Functional Probe"

    set +e
    python3 - <<'PY'
import sys

try:
    import torch
except Exception as exc:
    print(f"  Torch import failed: {type(exc).__name__}: {exc}")
    raise SystemExit(40)

if not torch.cuda.is_available():
    print("  CUDA unavailable.")
    raise SystemExit(41)

try:
    a = torch.arange(1, 4097, dtype=torch.float32, device="cuda")
    b = torch.sin(a) * torch.cos(a)
    checksum = float(b.sum().item())
    torch.cuda.synchronize()
except Exception as exc:
    print(f"  GPU operation failed: {type(exc).__name__}: {exc}")
    raise SystemExit(42)

print(f"  Device   : {torch.cuda.get_device_name(0)}")
print(f"  Elements : {a.numel()}")
print(f"  Checksum : {checksum:.6f}")
PY
    local rc=$?
    set -e

    case "$rc" in
        0)
            pass "Torch CUDA computation completed successfully."
            ;;
        40)
            fail "Torch import failed during GPU probe."
            ;;
        41)
            fail "CUDA unavailable during GPU probe."
            ;;
        42)
            fail "Torch CUDA operation failed."
            ;;
        *)
            fail "Unexpected GPU-probe exit code: $rc"
            ;;
    esac
}


check_motiongen() {
    section "A4b — MotionGen Initialization"

    if [[ "$RUN_MOTIONGEN" -ne 1 ]]; then
        printf '  [SKIP] MotionGen initialization not requested.\n'
        printf '         Use --motiongen --robot-config PATH to enable it.\n'
        return
    fi

    if [[ -z "$ROBOT_CONFIG" ]]; then
        fail "--motiongen requested but no robot config was supplied."
        return
    fi

    if [[ ! -f "$ROBOT_CONFIG" ]]; then
        fail "Robot config does not exist: $ROBOT_CONFIG"
        return
    fi

    printf '  Robot config : %s\n' "$ROBOT_CONFIG"

    set +e
    ROBOT_CONFIG="$ROBOT_CONFIG" python3 - <<'PY'
import os
import sys

robot_config = os.environ["ROBOT_CONFIG"]

try:
    import torch
    from curobo.types.base import TensorDeviceType
    from curobo.types.robot import RobotConfig
    from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig
except Exception as exc:
    print(f"  Import phase failed: {type(exc).__name__}: {exc}")
    raise SystemExit(50)

try:
    tensor_args = TensorDeviceType()

    # Different cuRobo revisions have changed config-loading helpers.
    # Try the common legacy path first and fail explicitly if the selected
    # project fork uses a different constructor contract.
    if hasattr(MotionGenConfig, "load_from_robot_config"):
        cfg = MotionGenConfig.load_from_robot_config(
            robot_config,
            tensor_args=tensor_args,
        )
    else:
        print("  MotionGenConfig.load_from_robot_config is unavailable in this revision.")
        raise SystemExit(51)

    motion_gen = MotionGen(cfg)

    # warmup() is the important functional step because it commonly exercises
    # CUDA-backed planning kernels/extensions.
    if hasattr(motion_gen, "warmup"):
        motion_gen.warmup()
    else:
        print("  MotionGen.warmup is unavailable in this revision.")
        raise SystemExit(52)

    if torch.cuda.is_available():
        torch.cuda.synchronize()

except SystemExit:
    raise
except Exception as exc:
    print(f"  MotionGen initialization failed: {type(exc).__name__}: {exc}")
    raise SystemExit(53)

print("  MotionGen construction : PASS")
print("  MotionGen warmup       : PASS")
PY
    local rc=$?
    set -e

    case "$rc" in
        0)
            pass "MotionGen initialization/warmup completed."
            ;;
        50)
            fail "MotionGen probe failed during imports."
            ;;
        51)
            warn "Selected cuRobo revision uses a different MotionGenConfig loading API."
            ;;
        52)
            warn "Selected cuRobo revision does not expose MotionGen.warmup()."
            ;;
        53)
            fail "MotionGen initialization or warmup failed."
            ;;
        *)
            fail "Unexpected MotionGen probe exit code: $rc"
            ;;
    esac
}


print_summary() {
    section "cuRobo Validation Summary"

    printf '  Failures : %s\n' "$FAIL_COUNT"
    printf '  Warnings : %s\n' "$WARN_COUNT"

    if [[ "$FAIL_COUNT" -gt 0 ]]; then
        printf '\nRESULT: FAIL [RUNTIME/ARCHITECTURE CANDIDATE]\n'
        printf 'NOTE: A failure here does NOT automatically trigger Option B.\n'
        printf '      Classify the root cause first (SETUP/BUILD/RUNTIME/ARCHITECTURE).\n'
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
    printf 'UniP cuRobo Validation — Gate A\n'
    printf '========================================================================\n'

    check_environment
    check_source_revision
    check_legacy_api
    check_torch_gpu_operation
    check_motiongen
    print_summary
}

main "$@"
