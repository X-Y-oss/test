# Advisor Communication Log – Nils Dengler

## 2026-07-03 – Follow-up confirmation
- A+B direction seems like a good plan.
- Main direction: placement-oriented active perception + physical investigation.
- Generative placement proposal remains optional.

## 2026-07-08 – Feasibility map feedback
- Feasibility map looks good.
- Once the proposal is satisfactory, full baseline code will be provided.
- Baseline components will be accessible and modifiable.
- Existing codebase includes UR5 arm in Isaac Sim.
- First implementation task: adapt codebase to Franka arm and make it actually pick and place objects in simulation.
- After proof of concept, mild clutter can be added in the grasping process: source object surrounded by 1–2 other objects.
- This makes view acquisition more challenging.

## 2026-07-10 – Visual NBV scope and camera setup
- Nils confirmed that the staged visual scope makes sense.
- The simulation currently uses an eye-in-hand RGB-D camera.
- The camera setup can be extended if needed.
- Proposal implication:
  - Start visual evidence acquisition with eye-in-hand NBV around the source object / grasping scene under mild clutter.
  - Treat target-region / support-geometry view acquisition as a follow-up or optional extension.
  - 
## 2026-07-13 – Proposal feedback and implementation checkpoint
- Nils reviewed the proposal and said that it looks very good so far.
- The proposed timeline looks doable, although the actual progress will depend on work effort.
- Nils emphasized that Section 3.4 is the main contribution.
  - The thesis framing and possible paper framing should center around the interactive placeability decision layer / uncertainty-based decision logic.
  - Visual and physical evidence acquisition should be framed as supporting actions around this decision layer.
- For RQ1, Nils suggested that a novel uncertainty quantification method could still be considered if useful.
  - The first implementation should use uncertainty-related signals already provided by the baseline.
  - If these signals are insufficient, a lightweight learned module could later combine them into a stronger placement-confidence estimate.
  - The current plan is therefore:
    - MVP: heuristic confidence estimator based on baseline signals.
    - Second-stage improvement: learned uncertainty module after simulation rollouts and labels are available.
- Nils proposed an additional clutter-clearing idea:
  - In the grasping zone, the best grasp needed to realize the best placement may be occluded by clutter.
  - A possible extension is to reason whether clearing space, for example by pushing an occluding object aside, would unlock a more robust grasp-placement pair.
  - This should be treated as an optional later-phase extension rather than the first MVP.
- Nils agreed that source-side clutter clearing is optional, but stated that it is more important than the diffusion/generative placement optional task.
- Proposal implication:
  - Reframe the thesis more clearly around the 3.4 decision logic.
  - Keep learned uncertainty quantification as a second-stage option.
  - Move source-side clutter clearing above diffusion/generative placement in the optional extension priority.
  - Keep Franka + baseline setup as the first concrete benchmark before thesis registration.

## 2026-07-14 – PEARL Lab onboarding and dedicated thesis channel
- Nils invited Yuhang to the PEARL Lab Discord server.
- A dedicated Masterarbeit / thesis channel was created for the project.
- Nils reposted the proposal and the additional lightweight backbone note in the channel so that relevant people can access them.
- From now on, thesis-related discussions should happen in the dedicated channel.
- Direct messages with Nils can still be used for general questions or topics that should not be visible to the professor.
- This indicates a transition from informal topic discussion toward lab-level onboarding / thesis preparation.

## 2026-07-14 – Code access status
- Nils said that code access will be provided tomorrow.
- There are currently some server issues, so access is delayed.
- The expected first technical benchmark remains:
  - get access to the simulation code,
  - prepare the Isaac Sim environment,
  - adapt / implement the Franka setup,
  - get the existing baseline running in Isaac Sim.
- Once the Franka + baseline benchmark works, thesis registration can be discussed.

## 2026-07-15 – GitLab access and repository orientation
- Access to three repositories was confirmed:
  - `UniP`
  - `IsaacSim_5.1.0_ur5e`
  - `isaacsim_5.1.0_devcontainer`
- Nils confirmed that the base code is `UniP`.
- Main file that he executed for the experiments: src/placeability_scoring/placeability_scoring/UP4_Pipeline_curobo.py
- The Isaac Sim / devcontainer repositories should be used to understand the simulation and environment setup.
- There is currently no documentation for the codebase.
  - Nils said another student plans to add documentation in the next few weeks.
  - In the meantime, Yuhang should start by getting familiar with the code and Isaac Sim.
- Nils said to let him know if there are any major blockers.
- Immediate next steps:
  - Start code orientation from `UniP`.
  - Inspect repository structure, scripts, configs, requirements, and possible entry points.
  - Check `isaacsim_5.1.0_devcontainer` for environment setup.
  - Check `IsaacSim_5.1.0_ur5e` for the existing Isaac Sim robot setup.
  - Prepare a personal code-orientation note before asking detailed technical questions.
 
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

## Proposal implications
- Add a simulation setup section.
- Treat Franka adaptation as technical prerequisite, not main contribution.
- Keep A+B as main research direction.
- Keep C/generative placement proposal as optional extension.
- Add cluttered grasping as staged extension/evaluation condition after proof of concept.
- Keep motion planning as execution feasibility backend.
