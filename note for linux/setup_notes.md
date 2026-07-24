# Thesis Environment Setup Notes - 24.07.2026

## corfu
- Ubuntu 24.04
- RTX 3070 8GB
- RAM: 15GB
- Swap: 4GB
- NVIDIA driver: 580.126.09
- Docker: 29.5.3
- NVIDIA Docker GPU passthrough: working

## Repositories
- unip: main
- isaacsim_5.1.0_ur5e: main, 7eefda6
- isaacsim_5.1.0_devcontainer: main, 8fd40b7

## Isaac Sim
- Image: nvcr.io/nvidia/isaac-sim:5.1.0
- Devcontainer builds and opens successfully
- GPU accessible inside devcontainer
- /workspace is volume-mounted
- Full headless startup reached "app ready"
- Full startup caused severe system slowdown -> needs later investigation

## ROS2
- No standard /opt/ros installation inside Isaac container
- No `ros2` CLI
- Isaac Sim contains internal Humble + Jazzy ROS2 bridge libraries
- Ubuntu 24.04 -> setup_ros_env.sh selects Jazzy
- Internal rclpy works after adding its path to PYTHONPATH

## Important configuration mismatch
Current Isaac devcontainer:
- Isaac Sim 5.1
- Ubuntu 24.04
- /workspace
- internal ROS2 Jazzy bridge

UniP postCreate.sh assumes:
- /home/ws
- ROS2 Humble
- Ubuntu 22.04 CUDA repository
- CUDA 12.1
- Python 3.10 paths
- TORCH_CUDA_ARCH_LIST=8.9
- contains duplicated installation steps

=> Do NOT run old postCreate.sh directly.
=> Treat it as reference and prepare a cleaned setup locally.
=> Validate new setup on corfu later.
