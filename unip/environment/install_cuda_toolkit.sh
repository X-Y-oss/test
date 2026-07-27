#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"

CUDA_VERSION="${CUDA_VERSION:-12.8}"
CUDA_PACKAGE="${CUDA_PACKAGE:-cuda-toolkit-12-8}"
CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.8}"

CUDA_REPO_DISTRO="${CUDA_REPO_DISTRO:-ubuntu2404}"
CUDA_REPO_ARCH="${CUDA_REPO_ARCH:-x86_64}"
CUDA_KEYRING_URL="${CUDA_KEYRING_URL:-https://developer.download.nvidia.com/compute/cuda/repos/${CUDA_REPO_DISTRO}/${CUDA_REPO_ARCH}/cuda-keyring_1.1-1_all.deb}"

log()  { printf '[%s] %s\n' "$SCRIPT_NAME" "$*"; }
warn() { printf '[%s] WARNING: %s\n' "$SCRIPT_NAME" "$*" >&2; }
fail() { printf '[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

require_command() {
    command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

nvcc_path() {
    if [[ -x "${CUDA_HOME}/bin/nvcc" ]]; then
        printf '%s\n' "${CUDA_HOME}/bin/nvcc"
        return 0
    fi
    command -v nvcc 2>/dev/null || return 1
}

nvcc_is_target_version() {
    local nvcc
    nvcc="$(nvcc_path)" || return 1
    "$nvcc" --version 2>/dev/null | grep -Eq "release[[:space:]]+12\.8([,[:space:]]|$)"
}

ensure_root() {
    [[ "$(id -u)" -eq 0 ]] || fail "CUDA toolkit installation requires root."
}

ensure_cuda_repository() {
    if dpkg-query -W -f='${Status}' cuda-keyring 2>/dev/null | grep -q "install ok installed"; then
        log "NVIDIA CUDA keyring already installed."
        return
    fi

    require_command wget
    require_command dpkg

    local tmp_deb
    tmp_deb="$(mktemp --suffix=.deb)"

    log "Downloading NVIDIA CUDA repository keyring..."
    wget -qO "$tmp_deb" "$CUDA_KEYRING_URL"

    log "Installing CUDA repository keyring..."
    dpkg -i "$tmp_deb"
    rm -f "$tmp_deb"
}

install_toolkit() {
    log "Installing ${CUDA_PACKAGE}..."
    apt-get update
    apt-get install -y --no-install-recommends "$CUDA_PACKAGE"
    rm -rf /var/lib/apt/lists/*
}

ensure_cuda_symlink() {
    if [[ ! -e /usr/local/cuda && -d "$CUDA_HOME" ]]; then
        ln -s "$CUDA_HOME" /usr/local/cuda
        log "Created /usr/local/cuda -> ${CUDA_HOME}"
    fi
}

verify_installation() {
    local nvcc="${CUDA_HOME}/bin/nvcc"

    [[ -x "$nvcc" ]] || fail "nvcc missing after install: $nvcc"
    "$nvcc" --version | grep -Eq "release[[:space:]]+12\.8([,[:space:]]|$)" ||
        fail "nvcc does not report CUDA 12.8."
    [[ -d "${CUDA_HOME}/include" ]] ||
        fail "CUDA include directory missing: ${CUDA_HOME}/include"

    log "CUDA toolkit verification:"
    "$nvcc" --version | tail -n 2 | sed 's/^/  /'
    log "PASS: CUDA ${CUDA_VERSION} development toolkit is ready."
}

main() {
    printf '========================================================================\n'
    printf 'UniP CUDA Toolkit Installation\n'
    printf '========================================================================\n'

    if nvcc_is_target_version; then
        log "SKIP: compatible CUDA ${CUDA_VERSION} nvcc already available."
        verify_installation
        exit 0
    fi

    log "CUDA 12.8 nvcc not found; preparing NVIDIA repository."
    ensure_root
    ensure_cuda_repository
    install_toolkit
    ensure_cuda_symlink
    verify_installation
}

main "$@"
