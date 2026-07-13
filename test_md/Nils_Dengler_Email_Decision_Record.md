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
## 2026-07-13 – Proposal feedback and code-access preparation
- Nils said the proposal looks very good so far.
- The timeline looks doable, depending on work effort.
- Section 3.4 is the main contribution and the thesis / possible paper framing should center around it.
- RQ1 should start from uncertainty signals provided by the baseline, but can be strengthened later by a novel or learned uncertainty quantification module if useful.
- The first MVP should use existing baseline signals and a heuristic confidence estimator to connect the decision policy and evidence-acquisition loops.
- A learned uncertainty module is considered a second-stage improvement after simulation rollouts and labels are available.
- Nils suggested source-side clutter clearing as an optional extension:
  - if the grasp needed for the best grasp-placement pair is occluded,
  - the robot could reason whether clearing/pushing the occluder improves robustness.
- Nils agreed this should be optional, but stated it is more important than the diffusion optional task.
- First benchmark before thesis registration:
  - Franka + baseline setup in Isaac Sim.
  - Once this works, thesis registration can be discussed.
- Nils asked for TU Darmstadt email, likely for code/repository access.

## Proposal implications
- Add a simulation setup section.
- Treat Franka adaptation as technical prerequisite, not main contribution.
- Keep A+B as main research direction.
- Keep C/generative placement proposal as optional extension.
- Add cluttered grasping as staged extension/evaluation condition after proof of concept.
- Keep motion planning as execution feasibility backend.
