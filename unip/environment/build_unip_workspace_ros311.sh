#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/workspace}"
UNIP_SRC="${UNIP_SRC:-${WORKSPACE_ROOT}/src}"
BASE_IMAGE="${UNIP_CORE_BASE_IMAGE:-unip_ros311_overlay:jazzy_py311}"
BUILD_IMAGE="${UNIP_CORE_BUILD_IMAGE:-unip_core_ros311:latest}"
BUILD_WS="${UNIP_CORE_BUILD_WS:-/workspace/unip_core_ws}"
OUTPUT_INSTALL="${UNIP_CORE_INSTALL:-${WORKSPACE_ROOT}/install}"
GPD_REPO="${GPD_REPO:-https://github.com/atenpas/gpd.git}"
GPD_REVISION="${GPD_REVISION:-2.0.0}"
GPD_COMMIT_EXPECTED="${GPD_COMMIT_EXPECTED:-6c6f9752b6197bdeffbf861da57ec04f96549148}"

CORE_PACKAGES=(
    gpd_ros_messages
    gpd_ros
    generate_motion_msgs
    placeability_scoring
)

log() { printf '[%s] %s\n' "$SCRIPT_NAME" "$*"; }
fail() { printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

cleanup() {
    [[ -n "${CID:-}" ]] && docker rm -f "$CID" >/dev/null 2>&1 || true
    [[ -n "${TMP_DIR:-}" && -d "${TMP_DIR:-}" ]] && rm -rf "$TMP_DIR"
}
trap cleanup EXIT

command -v docker >/dev/null 2>&1 || fail "docker CLI not found"
docker info >/dev/null 2>&1 || fail "Docker daemon unavailable"
docker image inspect "$BASE_IMAGE" >/dev/null 2>&1 || fail "Base image missing: $BASE_IMAGE"

for pkg in "${CORE_PACKAGES[@]}"; do
    [[ -f "${UNIP_SRC}/${pkg}/package.xml" ]] || fail "Missing package manifest: ${UNIP_SRC}/${pkg}/package.xml"
done

TMP_DIR="$(mktemp -d)"
CONTEXT_DIR="${TMP_DIR}/context"
mkdir -p "${CONTEXT_DIR}/src"

for pkg in "${CORE_PACKAGES[@]}"; do
    log "Copying source package: $pkg"
    cp -a "${UNIP_SRC}/${pkg}" "${CONTEXT_DIR}/src/"
done

cat > "${CONTEXT_DIR}/Dockerfile" <<DOCKERFILE
FROM ${BASE_IMAGE}
SHELL ["/bin/bash", "-lc"]
WORKDIR /workspace

RUN python3 --version && \
    test "\$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')" = "3.11" && \
    echo "colcon: \$(command -v colcon)" && \
    head -n 1 "\$(command -v colcon)"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
        libboost-all-dev \
        libeigen3-dev \
        libopencv-dev \
        libpcl-dev && \
    rm -rf /var/lib/apt/lists/*

RUN git clone ${GPD_REPO} /tmp/gpd && \
    cd /tmp/gpd && \
    git checkout ${GPD_REVISION} && \
    test "\$(git rev-parse HEAD)" = "${GPD_COMMIT_EXPECTED}" && \
    mkdir -p build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr/local .. && \
    cmake --build . -j"\$(nproc)" && \
    cmake --install . && \
    ldconfig && \
    ldconfig -p | grep libgpd && \
    test -f /usr/local/include/gpd/grasp_detector.h

RUN rm -rf ${BUILD_WS} && mkdir -p ${BUILD_WS}/src
COPY src/ ${BUILD_WS}/src/

RUN source /workspace/jazzy_ws/install/setup.bash && \
    source /workspace/unip_ros311_ws/install/local_setup.bash && \
    cd ${BUILD_WS} && \
    colcon build \
        --merge-install \
        --packages-up-to \
            gpd_ros_messages \
            gpd_ros \
            generate_motion_msgs \
            placeability_scoring \
        --cmake-args \
            -DCMAKE_BUILD_TYPE=RelWithDebInfo \
            -DCMAKE_EXPORT_COMPILE_COMMANDS=ON

RUN source /workspace/jazzy_ws/install/setup.bash && \
    source /workspace/unip_ros311_ws/install/local_setup.bash && \
    source ${BUILD_WS}/install/local_setup.bash && \
    python3 -c 'import sys; assert sys.version_info[:2] == (3, 11); import placeability_scoring, gpd_ros_messages; print("UniP core Python imports: PASS")'
DOCKERFILE

log "Building UniP core ROS311 image..."
docker build --network=host -t "$BUILD_IMAGE" "$CONTEXT_DIR"

log "Extracting install tree to: $OUTPUT_INSTALL"
rm -rf "$OUTPUT_INSTALL"
CID="$(docker create "$BUILD_IMAGE")"
docker cp "${CID}:${BUILD_WS}/install" "$OUTPUT_INSTALL"
docker rm "$CID" >/dev/null
CID=""

[[ -f "${OUTPUT_INSTALL}/local_setup.bash" ]] || fail "Extracted install/local_setup.bash missing"

log "PASS: UniP core ROS311 workspace build completed."
log "Install tree: $OUTPUT_INSTALL"
