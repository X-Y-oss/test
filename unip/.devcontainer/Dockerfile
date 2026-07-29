# syntax=docker/dockerfile:1
FROM nvcr.io/nvidia/isaac-sim:5.1.0

USER root

ARG DEBIAN_FRONTEND=noninteractive

ENV WORKSPACE_ROOT=/workspace \
    UNIP_SRC=/workspace/src \
    GPD_ROOT=/workspace/external/gpd \
    CUROBO_ROOT=/workspace/external/curobo \
    PYTHON_BIN=/isaac-sim/python.sh \
    ROS_DISTRO_TARGET=jazzy \
    ISAAC_ROS_WS_ROOT=/workspace/external/IsaacSim-ros_workspaces \
    CUDA_HOME=/usr/local/cuda-12.8 \
    PATH=/usr/local/cuda-12.8/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/cuda-12.8/lib64:${LD_LIBRARY_PATH}

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        ninja-build \
        pkg-config \
        git \
        git-lfs \
        liblttng-ust1t64 \
        curl \
        wget \
        ca-certificates \
        sudo \
        lsb-release \
        gnupg2 \
        software-properties-common \
        docker.io \
        colcon \
        python3-pip \
        python3-dev \
        libeigen3-dev \
        libpcl-dev \
        libopencv-dev \
        python3-opencv \
        libboost-all-dev \
        libomp-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p \
        /workspace/src \
        /workspace/external \
        /workspace/external/gpd \
        /workspace/external/curobo

WORKDIR /workspace
ENTRYPOINT ["/bin/bash"]
