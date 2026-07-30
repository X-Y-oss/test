#!/usr/bin/env bash

set -Eeuo pipefail

BOOST_VERSION="${BOOST_VERSION:-1.83.0}"
BOOST_VERSION_U="${BOOST_VERSION//./_}"
BOOST_PREFIX="${BOOST_PREFIX:-/usr/local}"

PYTHON_BIN="${PYTHON_BIN:-/isaac-sim/kit/python/bin/python3}"
PYTHON_INCLUDE="${PYTHON_INCLUDE:-/isaac-sim/kit/python/include/python3.11}"
PYTHON_LIB_DIR="${PYTHON_LIB_DIR:-/isaac-sim/kit/python/lib}"

BOOST_LIBRARY="${BOOST_PREFIX}/lib/libboost_python311.so.${BOOST_VERSION}"
BUILD_ROOT="${BOOST_BUILD_ROOT:-/tmp/boost-python311-build}"
ARCHIVE="${BUILD_ROOT}/boost_${BOOST_VERSION_U}.tar.gz"
SOURCE_DIR="${BUILD_ROOT}/boost_${BOOST_VERSION_U}"

log() {
    printf '[install_boost_python311] %s\n' "$*"
}

fail() {
    printf '[install_boost_python311] ERROR: %s\n' "$*" >&2
    exit 1
}

if [[ -f "$BOOST_LIBRARY" ]]; then
    log "Boost.Python 3.11 already installed: $BOOST_LIBRARY"
    ldconfig
    exit 0
fi

[[ -x "$PYTHON_BIN" ]] ||
    fail "Python 3.11 executable not found: $PYTHON_BIN"

[[ -f "${PYTHON_INCLUDE}/Python.h" ]] ||
    fail "Python 3.11 headers not found: ${PYTHON_INCLUDE}/Python.h"

apt-get update
apt-get install -y \
    build-essential \
    ca-certificates \
    wget

mkdir -p "$BUILD_ROOT"

if [[ ! -f "$ARCHIVE" ]]; then
    wget \
        "https://archives.boost.io/release/${BOOST_VERSION}/source/boost_${BOOST_VERSION_U}.tar.gz" \
        -O "$ARCHIVE"
fi

rm -rf "$SOURCE_DIR"
tar -xzf "$ARCHIVE" -C "$BUILD_ROOT"

cat > "${BUILD_ROOT}/user-config.jam" <<EOF
using python
  : 3.11
  : ${PYTHON_BIN}
  : ${PYTHON_INCLUDE}
  : ${PYTHON_LIB_DIR}
  ;
EOF

cd "$SOURCE_DIR"

./bootstrap.sh \
    --with-libraries=python \
    --prefix="$BOOST_PREFIX"

./b2 \
    --user-config="${BUILD_ROOT}/user-config.jam" \
    variant=release \
    link=shared \
    runtime-link=shared \
    threading=multi \
    python=3.11 \
    address-model=64 \
    -j"$(nproc)" \
    install

echo "${BOOST_PREFIX}/lib" \
    > /etc/ld.so.conf.d/boost-python311.conf

ldconfig

[[ -f "$BOOST_LIBRARY" ]] ||
    fail "Expected library was not installed: $BOOST_LIBRARY"

ldconfig -p | grep -q 'libboost_python311.so.1.83.0' ||
    fail "Boost.Python 3.11 is missing from linker cache"

log "PASS: Boost.Python ${BOOST_VERSION} for Python 3.11 installed."
