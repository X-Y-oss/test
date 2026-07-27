#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP ROS Jazzy / Python 3.11 overlay installer
#
# Builds the ROS packages missing from NVIDIA's Isaac Sim 5.1 Jazzy/Python 3.11
# underlay inside a dedicated Docker image, then copies the resulting overlay
# into /workspace/external/unip_ros311_ws.
# -----------------------------------------------------------------------------

SCRIPT_NAME="$(basename "$0")"

ISAAC_ROS_WS_ROOT="${ISAAC_ROS_WS_ROOT:-/workspace/external/IsaacSim-ros_workspaces}"
OVERLAY_ROOT="${UNIP_ROS311_OVERLAY_ROOT:-/workspace/external/unip_ros311_ws}"

BASE_IMAGE="${UNIP_ROS311_BASE_IMAGE:-isaac_sim_ros:ubuntu_24_jazzy}"
OVERLAY_IMAGE="${UNIP_ROS311_OVERLAY_IMAGE:-unip_ros311_overlay:jazzy_py311}"

PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/python.sh}"

ROS311_BASE_SETUP="${ROS311_BASE_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/jazzy/jazzy_ws/install/local_setup.bash}"
ROS311_ISAAC_SETUP="${ROS311_ISAAC_SETUP:-${ISAAC_ROS_WS_ROOT}/build_ws/jazzy/isaac_sim_ros_ws/install/local_setup.bash}"


log() {
    printf '[%s] %s\n' "$SCRIPT_NAME" "$*"
}


fail() {
    printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2
    exit 1
}


cleanup() {
    if [[ -n "${TMP_DIR:-}" && -d "${TMP_DIR:-}" ]]; then
        rm -rf "$TMP_DIR"
    fi

    if [[ -n "${CID:-}" ]]; then
        docker rm -f "$CID" >/dev/null 2>&1 || true
    fi
}


trap cleanup EXIT


# -----------------------------------------------------------------------------
# Preflight
# -----------------------------------------------------------------------------

command -v docker >/dev/null 2>&1 \
    || fail "docker CLI not found"

docker info >/dev/null 2>&1 \
    || fail "Docker daemon unavailable"

docker image inspect "$BASE_IMAGE" >/dev/null 2>&1 \
    || fail "Base image missing: $BASE_IMAGE"

[[ -f "$ROS311_BASE_SETUP" ]] \
    || fail "Missing base setup: $ROS311_BASE_SETUP"

[[ -f "$ROS311_ISAAC_SETUP" ]] \
    || fail "Missing Isaac setup: $ROS311_ISAAC_SETUP"


log "Checking Isaac Python..."

"$PYTHON_BIN" - <<'PY'
import sys

assert sys.version_info[:2] == (3, 11), sys.version
print("Isaac Python:", sys.version.split()[0])
PY


# -----------------------------------------------------------------------------
# Generate temporary Dockerfile
# -----------------------------------------------------------------------------

TMP_DIR="$(mktemp -d)"
DOCKERFILE="${TMP_DIR}/Dockerfile"

cat > "$DOCKERFILE" <<'DOCKERFILE'
ARG BASE_IMAGE=isaac_sim_ros:ubuntu_24_jazzy
FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-lc"]
WORKDIR /workspace


# -----------------------------------------------------------------------------
# 1. Prepare UniP ROS311 overlay source workspace
# -----------------------------------------------------------------------------

RUN rm -rf /workspace/unip_ros311_ws && \
    mkdir -p /workspace/unip_ros311_ws/src


# Generate only packages missing from NVIDIA's Jazzy source set.
RUN rosinstall_generator \
        sensor_msgs_py \
        tf2_ros \
        tf2_ros_py \
        cv_bridge \
        control_msgs \
        moveit_msgs \
        launch \
        launch_ros \
        --deps \
        --rosdistro jazzy \
        --exclude-path /workspace/jazzy_ws/src \
        > /workspace/unip_ros311_ws/unip_overlay.rosinstall && \
    echo "===== UniP ROS311 source closure =====" && \
    grep "local-name:" \
        /workspace/unip_ros311_ws/unip_overlay.rosinstall && \
    echo "===== count =====" && \
    grep -c "local-name:" \
        /workspace/unip_ros311_ws/unip_overlay.rosinstall && \
    vcs import \
        /workspace/unip_ros311_ws/src \
        < /workspace/unip_ros311_ws/unip_overlay.rosinstall


# -----------------------------------------------------------------------------
# 2. Build Boost.Python for Python 3.11
#
# Ubuntu 24.04's packaged Boost.Python targets Python 3.12.  cv_bridge in this
# workspace must target Python 3.11, so build only Boost.Python 1.83 locally.
# -----------------------------------------------------------------------------

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        wget \
        libopencv-dev && \
    rm -rf /var/lib/apt/lists/* && \
    cd /tmp && \
    wget -q \
        https://archives.boost.io/release/1.83.0/source/boost_1_83_0.tar.gz && \
    tar -xzf boost_1_83_0.tar.gz && \
    cd boost_1_83_0 && \
    ./bootstrap.sh \
        --with-libraries=python \
        --with-python=/usr/bin/python3.11 && \
    echo "===== Boost project-config.jam =====" && \
    cat project-config.jam && \
    echo "===== Building Boost.Python 3.11 only =====" && \
    ./b2 \
        --debug-configuration \
        libs/python/build//boost_python \
        link=shared \
        threading=multi \
        variant=release \
        -j"$(nproc)" && \
    echo "===== Installing Boost.Python 3.11 =====" && \
    BOOST_PYTHON_LIB="$(find bin.v2/libs/python/build \
        -type f \
        -name 'libboost_python311.so.1.83.0' \
        -print \
        -quit)" && \
    test -n "$BOOST_PYTHON_LIB" && \
    echo "Found: $BOOST_PYTHON_LIB" && \
    mkdir -p /usr/local/lib && \
    cp -av "$BOOST_PYTHON_LIB" \
        /usr/local/lib/libboost_python311.so.1.83.0 && \
    ln -sf \
        libboost_python311.so.1.83.0 \
        /usr/local/lib/libboost_python311.so && \
    ldconfig && \
    echo "===== Installed Boost.Python libraries =====" && \
    ls -l /usr/local/lib/libboost_python311*

# Make locally built Boost.Python visible before the Ubuntu Boost.Python 3.12
# package when CMake configures cv_bridge.
ENV LD_LIBRARY_PATH=/usr/local/lib:${LD_LIBRARY_PATH}


# -----------------------------------------------------------------------------
# 3. Build ROS311 overlay
# -----------------------------------------------------------------------------

RUN source /workspace/jazzy_ws/install/setup.bash && \
    cd /workspace/unip_ros311_ws && \
    colcon build \
        --merge-install \
        --cmake-args \
            -DPython3_EXECUTABLE=/usr/bin/python3.11 \
            -DPYTHON_EXECUTABLE=/usr/bin/python3.11 \
            -DPYTHON_INCLUDE_DIR=/usr/include/python3.11 \
            -DPYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.11.so \
            -DBoost_NO_BOOST_CMAKE=ON \
            -DBoost_INCLUDE_DIR=/usr/include \
            -DBoost_LIBRARY_DIR=/usr/local/lib


# -----------------------------------------------------------------------------
# 4. Validate inside build image
# -----------------------------------------------------------------------------

RUN source /workspace/jazzy_ws/install/setup.bash && \
    source /workspace/unip_ros311_ws/install/local_setup.bash && \
    python3.11 - <<'PY'
from ament_index_python.packages import get_package_prefix

packages = (
    "sensor_msgs_py",
    "tf2_ros",
    "tf2_ros_py",
    "cv_bridge",
    "control_msgs",
    "moveit_msgs",
)

for pkg in packages:
    print(f"[PASS] {pkg:<20} {get_package_prefix(pkg)}")

import sensor_msgs_py
import tf2_ros
import cv_bridge
import control_msgs
import moveit_msgs

print("Overlay build-image validation: PASS")
PY

DOCKERFILE


# -----------------------------------------------------------------------------
# Build overlay image
# -----------------------------------------------------------------------------

log "Building ROS311 overlay image..."

docker build \
    --network=host \
    --build-arg "BASE_IMAGE=${BASE_IMAGE}" \
    -f "$DOCKERFILE" \
    -t "$OVERLAY_IMAGE" \
    "$TMP_DIR"


# -----------------------------------------------------------------------------
# Extract built overlay
# -----------------------------------------------------------------------------

log "Extracting overlay to: $OVERLAY_ROOT"

rm -rf "$OVERLAY_ROOT"

CID="$(docker create "$OVERLAY_IMAGE")"

docker cp \
    "${CID}:/workspace/unip_ros311_ws" \
    "$OVERLAY_ROOT"

docker rm "$CID" >/dev/null
CID=""

[[ -f "${OVERLAY_ROOT}/install/local_setup.bash" ]] \
    || fail "Extracted overlay setup missing"


# -----------------------------------------------------------------------------
# Validate extracted overlay with Isaac Python
# -----------------------------------------------------------------------------

log "Validating extracted overlay with Isaac Python..."

set +u

# shellcheck disable=SC1090
source "$ROS311_BASE_SETUP"

# shellcheck disable=SC1090
source "$ROS311_ISAAC_SETUP"

# shellcheck disable=SC1090
source "${OVERLAY_ROOT}/install/local_setup.bash"

set -u


"$PYTHON_BIN" - <<'PY'
from ament_index_python.packages import get_package_prefix

packages = (
    "sensor_msgs_py",
    "tf2_ros",
    "cv_bridge",
    "control_msgs",
    "moveit_msgs",
)

for pkg in packages:
    print(f"[PASS] {pkg:<20} {get_package_prefix(pkg)}")

import sensor_msgs_py
import tf2_ros
import cv_bridge
import control_msgs
import moveit_msgs

print("Isaac Python overlay imports: PASS")
PY


log "PASS: UniP ROS Jazzy/Python-3.11 overlay prepared."
log "Overlay setup: ${OVERLAY_ROOT}/install/local_setup.bash"
