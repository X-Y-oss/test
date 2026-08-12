# UniP Development Workspace

Development workspace for the UniP Isaac Sim baseline.

This repository provides a reproducible Isaac Sim / ROS 2 development environment together with a simplified installation and validation workflow for the UniP baseline.

The goal is to keep the original UniP perception, placeability reasoning, and planning pipeline reproducible while providing a clean development base for the Franka migration and later thesis extensions.
---
##Project Status
###UR5e Baseline Reproduction — Frozen
The main UniP perception-to-planning pipeline has been reproduced and validated:
- RGB-D / TSDF reconstruction
- GPD grasp generation
- placement sampling
- stability / PCG / clearance evaluation
- joint grasp-placement reasoning
- CuRobo planning
Online robot motion was additionally validated in Isaac Sim through a temporary /joint_command execution bridge.
The UR5e setup is now kept as a reference baseline. Remaining legacy scene/viewpoint and execution-interface issues will not be further reconstructed in the UR5e version.
---

## Quick Start

Run:

```bash
bash environment/setup_and_validate.sh
```

For detailed installation instructions, validation steps and troubleshooting, see

[UniP Environment Setup](/unip/environment/README.md)
