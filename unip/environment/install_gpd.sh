#!/usr/bin/env bash
set -Eeuo pipefail

# -----------------------------------------------------------------------------
# UniP native GPD installer
#
# Purpose:
#   Install a reproducible native GPD library for gpd_ros.
#
# Policy:
#   - Default repository: https://github.com/atenpas/gpd.git
#   - Default revision: 2.0.0
#   - Install prefix: /usr/local
#   - Idempotent: skip rebuild when the requested revision is already present
#     and libgpd is discoverable.
#
# This script does NOT:
#   - build gpd_ros;
#   - modify ROS packages;
#   - install Python dependencies;
#   - run functional grasp-detection tests.
# -----------------------------------------------------------------------------

GPD_REPO="${GPD_REPO:-https://github.com/atenpas/gpd.git}"
GPD_REVISION="${GPD_REVISION:-2.0.0}"
GPD_ROOT="${GPD_ROOT:-/workspace/external/gpd}"
GPD_BUILD_DIR="${GPD_BUILD_DIR:-${GPD_ROOT}/build}"
GPD_INSTALL_PREFIX="${GPD_INSTALL_PREFIX:-/usr/local}"
GPD_BUILD_JOBS="${GPD_BUILD_JOBS:-$(nproc)}"

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
    printf '[%s] GPD_ROOT=%s\n' "$SCRIPT_NAME" "$GPD_ROOT" >&2
    printf '[%s] GPD_REVISION=%s\n' "$SCRIPT_NAME" "$GPD_REVISION" >&2
    exit "$exit_code"
}

trap 'on_error $LINENO' ERR


require_command() {
    local cmd="$1"
    command -v "$cmd" >/dev/null 2>&1 || fail "Required command not found: $cmd"
}


is_libgpd_discoverable() {
    # Prefer ldconfig because gpd_ros links against the installed native library.
    if command -v ldconfig >/dev/null 2>&1; then
        if ldconfig -p 2>/dev/null | grep -Eq 'libgpd(\.so|\s)'; then
            return 0
        fi
    fi

    # Fallback for environments where ldconfig output is unavailable.
    find "${GPD_INSTALL_PREFIX}/lib" "${GPD_INSTALL_PREFIX}/lib64" \
        -maxdepth 1 -type f -name 'libgpd.so*' -print -quit 2>/dev/null \
        | grep -q .
}


is_gpd_header_installed() {
    local candidates=(
        "${GPD_INSTALL_PREFIX}/include/gpd/grasp_detector.h"
        "${GPD_INSTALL_PREFIX}/include/gpd/grasp_detector.hpp"
        "${GPD_INSTALL_PREFIX}/include/gpd/util/cloud.h"
    )

    local path
    for path in "${candidates[@]}"; do
        if [[ -f "$path" ]]; then
            return 0
        fi
    done

    return 1
}


current_checkout_matches() {
    [[ -d "${GPD_ROOT}/.git" ]] || return 1

    local current_commit expected_commit

    current_commit="$(git -C "$GPD_ROOT" rev-parse HEAD 2>/dev/null || true)"
    [[ -n "$current_commit" ]] || return 1

    expected_commit="$(git -C "$GPD_ROOT" rev-parse "${GPD_REVISION}^{commit}" 2>/dev/null || true)"
    [[ -n "$expected_commit" ]] || return 1

    [[ "$current_commit" == "$expected_commit" ]]
}


ensure_source() {
    mkdir -p "$(dirname "$GPD_ROOT")"

    if [[ ! -e "$GPD_ROOT" ]]; then
        log "Cloning native GPD repository..."
        git clone "$GPD_REPO" "$GPD_ROOT"
    elif [[ ! -d "${GPD_ROOT}/.git" ]]; then
        fail "GPD_ROOT exists but is not a Git repository: $GPD_ROOT"
    else
        local current_origin
        current_origin="$(git -C "$GPD_ROOT" remote get-url origin 2>/dev/null || true)"

        if [[ -n "$current_origin" && "$current_origin" != "$GPD_REPO" ]]; then
            warn "Existing GPD checkout uses a different origin."
            warn "Expected: $GPD_REPO"
            warn "Found:    $current_origin"
        fi

        log "Existing GPD checkout found: $GPD_ROOT"
    fi

    log "Fetching tags/revisions..."
    git -C "$GPD_ROOT" fetch --tags --prune origin

    if ! git -C "$GPD_ROOT" rev-parse --verify "${GPD_REVISION}^{commit}" >/dev/null 2>&1; then
        fail "Requested GPD revision does not exist: $GPD_REVISION"
    fi
}


checkout_requested_revision() {
    if current_checkout_matches; then
        log "Requested GPD revision is already checked out: $GPD_REVISION"
        return
    fi

    if [[ -n "$(git -C "$GPD_ROOT" status --porcelain)" ]]; then
        fail "GPD source tree has local modifications. Refusing to overwrite: $GPD_ROOT"
    fi

    log "Checking out GPD revision: $GPD_REVISION"
    git -C "$GPD_ROOT" checkout --detach "$GPD_REVISION"
}


already_ready() {
    current_checkout_matches &&
        is_libgpd_discoverable &&
        is_gpd_header_installed
}


configure_and_build() {
    log "Configuring native GPD..."
    cmake \
        -S "$GPD_ROOT" \
        -B "$GPD_BUILD_DIR" \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX="$GPD_INSTALL_PREFIX"

    log "Building native GPD with ${GPD_BUILD_JOBS} job(s)..."
    cmake --build "$GPD_BUILD_DIR" --parallel "$GPD_BUILD_JOBS"
}


install_gpd() {
    log "Installing native GPD to: $GPD_INSTALL_PREFIX"

    if [[ "$(id -u)" -eq 0 ]]; then
        cmake --install "$GPD_BUILD_DIR"
        ldconfig
    elif command -v sudo >/dev/null 2>&1; then
        sudo cmake --install "$GPD_BUILD_DIR"
        sudo ldconfig
    else
        fail "Installation to $GPD_INSTALL_PREFIX requires root privileges or sudo."
    fi
}


verify_installation() {
    log "Verifying native GPD installation..."

    if ! is_libgpd_discoverable; then
        fail "libgpd was not found after installation."
    fi

    if ! is_gpd_header_installed; then
        fail "Installed GPD headers were not found under ${GPD_INSTALL_PREFIX}/include."
    fi

    local commit
    commit="$(git -C "$GPD_ROOT" rev-parse --short HEAD)"

    log "Native GPD installation verified."
    log "Repository : $GPD_REPO"
    log "Revision   : $GPD_REVISION"
    log "Commit     : $commit"
    log "Source     : $GPD_ROOT"
    log "Prefix     : $GPD_INSTALL_PREFIX"
}


main() {
    log "========================================"
    log "Native GPD installation"
    log "========================================"
    log "Repository : $GPD_REPO"
    log "Revision   : $GPD_REVISION"
    log "Source     : $GPD_ROOT"
    log "Prefix     : $GPD_INSTALL_PREFIX"

    require_command git
    require_command cmake
    require_command grep
    require_command find

    ensure_source
    checkout_requested_revision

    if already_ready; then
        log "Correct source revision and installed libgpd detected."
        log "SKIP: native GPD is already ready."
        exit 0
    fi

    configure_and_build
    install_gpd
    verify_installation

    log "PASS: native GPD installation completed."
}


main "$@"
