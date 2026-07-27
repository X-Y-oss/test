# syntax=docker/dockerfile:1

# -----------------------------------------------------------------------------
# UniP / Isaac Sim 5.1 development image
#
# Design goals
# ------------
# - Preserve the known-working Isaac Sim 5.1 container as the runtime anchor.
# - Add only stable OS/native build prerequisites here.
# - Do NOT install a normal Ubuntu ROS Jazzy Python stack into Isaac's Python.
#   Isaac Sim 5.1 uses Python 3.11, while Ubuntu 24.04's default Jazzy install
#   uses Python 3.12. The Isaac-compatible Jazzy/Python-3.11 workspace is handled
#   separately.
# - Do NOT install Torch, CUDA toolkit, cuRobo, or native GPD here.
#   Those are compatibility-controlled/project-source dependencies.
# -----------------------------------------------------------------------------

FROM nvcr.io/nvidia/isaac-sim:5.1.0

ARG DEBIAN_FRONTEND=noninteractive

# Canonical project/runtime paths.
ENV WORKSPACE_ROOT=/workspace \
    UNIP_SRC=/workspace/src \
    GPD_ROOT=/workspace/external/gpd \
    CUROBO_ROOT=/workspace/external/curobo \
    PYTHON_BIN=/isaac-sim/python.sh \
    CUDA_HOME=/usr/local/cuda-12.8 \
    PATH=/usr/local/cuda-12.8/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:${LD_LIBRARY_PATH}

# Stable system and native-build prerequisites.
#
# Notes:
# - python3-rosdep / python3-colcon-common-extensions are CLI/build tools. They
#   are not used as the Isaac Python runtime.
# - PCL / Eigen / OpenCV are required by gpd_ros/native GPD.
# - Boost/OpenMP are included because native GPD and its historical build stack
#   use standard C++/parallel dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        ninja-build \
        pkg-config \
        git \
        git-lfs \
        curl \
        wget \
        ca-certificates \
        sudo \
        lsb-release \
        gnupg2 \
        software-properties-common \
        python3-rosdep \
        python3-colcon-common-extensions \
        libeigen3-dev \
        libpcl-dev \
        libopencv-dev \
        libboost-all-dev \
        libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep's system database if the image does not already contain it.
# Failure here is intentionally non-fatal because network availability during
# image build can vary; post-create validation will report the real state.
RUN if command -v rosdep >/dev/null 2>&1; then \
        rosdep init 2>/dev/null || true; \
    fi

# Create the project-owned directories expected by the environment scripts.
RUN mkdir -p \
        /workspace/src \
        /workspace/external \
        /workspace/external/gpd \
        /workspace/external/curobo

WORKDIR /workspace

# Deliberately NOT installed here:
#
#   - ros-jazzy-* runtime/development packages
#       -> Ubuntu 24.04 default ROS uses Python 3.12; Isaac Sim 5.1 requires
#          Python 3.11 for rclpy/custom workspaces loaded with Isaac.
#
#   - torch
#       -> version must be frozen together with CUDA/cuRobo Gate A.
#
#   - cuda-toolkit-12-1
#       -> legacy workaround; toolkit version must follow the selected
#          Torch/cuRobo compatibility profile.
#
#   - cuRobo
#       -> installed from the pinned BennoWingender/curobo revision.
#
#   - native GPD
#       -> installed by environment/install_gpd.sh (default candidate 2.0.0).
#
#   - MoveIt
#       -> full MoveIt planning stack is not part of the verified CuRobo
#          planning path; only actually required ROS interfaces/messages will
#          be provided by the ROS workspace/dependency layer.
#
#   - standalone usd-core
#       -> Isaac Sim owns the USD/PXR runtime.
#
# The next environment layer must provide an Isaac-compatible ROS 2 Jazzy
# workspace built for Python 3.11 before UniP's custom ROS packages are built.
