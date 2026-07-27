#!/usr/bin/env bash
set -Eeuo pipefail

WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"
REQ_FILE="${REQ_FILE:-${WORKSPACE_ROOT}/requirements/core.txt}"

echo "========================================================================"
echo "Install UniP Python Core Dependencies"
echo "========================================================================"

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "[FAIL] Isaac Python not found: $PYTHON_BIN"
    exit 1
fi

if [[ ! -f "$REQ_FILE" ]]; then
    echo "[FAIL] Requirements file not found: $REQ_FILE"
    exit 1
fi

echo "Python runtime:"
"$PYTHON_BIN" - <<'PY'
import sys

print("  version   :", sys.version.split()[0])
print("  executable:", sys.executable)

if sys.version_info[:2] != (3, 11):
    raise SystemExit("Expected Isaac Python 3.11")
PY

echo
echo "Installing:"
sed 's/^/  /' "$REQ_FILE"

"$PYTHON_BIN" -m pip install \
    --disable-pip-version-check \
    -r "$REQ_FILE"

echo
echo "Validating imports..."

"$PYTHON_BIN" - <<'PY'
import importlib

required = [
    "open3d",
    "pandas",
    "tqdm",
    "klampt",
    "pyfqmr",
    "shapely",
    "toppra",
]

failed = []

for name in required:
    try:
        module = importlib.import_module(name)
        version = getattr(module, "__version__", "<no __version__>")
        print(f"  [PASS] {name:<12} {version}")
    except Exception as exc:
        failed.append(name)
        print(f"  [FAIL] {name:<12} {type(exc).__name__}: {exc}")

if failed:
    raise SystemExit(
        "Python core validation failed: " + ", ".join(failed)
    )

print()
print("Python core dependencies: PASS")
PY

echo
echo "[PASS] UniP Python core dependencies installed."