# UniP Environment Setup

This repository contains a cleaned environment setup for the UniP baseline.

The installation has been reorganized so that most dependency checks and validation
can be executed through a unified entry script instead of manually running multiple
scripts.

---

## Current Environment

### Core Runtime

- OS: Ubuntu 24.04
- Isaac Sim: 5.1.0
- ROS 2: Jazzy
- Python runtime: 3.11
- Boost.Python: 1.83.0, built for Python 3.11
- Open3D: 0.19.0
- PyTorch: 2.7.0+cu128
- CUDA runtime used by PyTorch: 12.8

### Grasp Detection Stack

- Native GPD repository: `atenpas/gpd`
- Version/tag: `2.0.0`
- Commit: `6c6f975`
- Native GPD build: PASS
- ROS message and interface build: PASS

### Motion Planning Stack

- cuRobo repository: `BennoWingender/curobo`
- Branch: `main`
- Commit: `d64c4b0`
- PyTorch/CUDA backend: PASS
- Full UniP planner integration: PENDING

---

## Validation

After setup finishes, the following components should pass:

- NVIDIA GPU access

- Torch/CUDA

- Boost.Python

- ROS 2 environment and communication

- cuRobo validation

- Open3D

- native GPD and the ROS 2 GPD interface

- Isaac Sim imports

...

---

## Notes

Already installed components are skipped automatically, making it safe to rerun after updates.

---

## Current status

Environment reconstruction: mostly completed

Remaining work:

- resolve the remaining module-interface issues
- validate native GPD during full pipeline execution
- run the original UR5e baseline end to end
- begin the Franka migration after the UR5e baseline is reproducible

---

## Why this wrapper?

The original project contains multiple install and validation scripts spread across
different folders.

This wrapper provides a single entry point that

- executes them in the correct order
- skips completed steps
- reports failures immediately

instead of requiring manual execution of many scripts.
