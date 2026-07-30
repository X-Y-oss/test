# UniP Environment Setup

This repository contains a cleaned environment setup for the UniP baseline.

The installation has been reorganized so that most dependency checks and validation
can be executed through a unified entry script instead of manually running multiple
scripts.

---

## Repository structure

setup_and_validate.sh
scripts/
    install/
    validate/
    utils/

---

## Quick Start

### 1. Clone repositories

...

### 2. Build devcontainer

Open the repository in VS Code and reopen in container.

### 3. Run setup

./setup_and_validate.sh

The script will

- install missing dependencies
- skip already installed components
- validate the environment
- generate a summary

---

## Validation

After setup finishes, the following components should pass:

✓ CUDA

✓ PyTorch CUDA

✓ ROS2

✓ cuRobo

✓ Open3D

✓ GPD

✓ Placeability

✓ Placement sampling

✓ Isaac imports

...

---

## Notes

This setup script is idempotent.

Already installed components are skipped automatically, making it safe to rerun after updates.

---

## Current status

Environment reconstruction:
✔ mostly completed

Remaining work:

- Franka migration
- Full Isaac Sim pipeline validation

---

## Why this wrapper?

The original project contains multiple install and validation scripts spread across
different folders.

This wrapper provides a single entry point that

- executes them in the correct order
- skips completed steps
- reports failures immediately

instead of requiring manual execution of many scripts.
