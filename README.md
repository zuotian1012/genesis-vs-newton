# Genesis vs Newton Multi-Physics Demo Comparison

This repository compares **Genesis** and **Newton** by re-implementing and recording a set of classical multi-physics simulation demos on the same hardware platform.

The current evaluation covers rigid bodies, robot control, inverse kinematics, soft bodies, cloth, fluids, MPM materials, and robot-cloth / robot-softbody coupling. All recorded demos in this repository were run on an **RTX 5090** machine.

## Project Goal

The goal is to understand which simulation platform is more suitable for follow-up work by checking:

- whether both platforms can run representative classical demos;
- which physical scenes and solver families each platform supports directly;
- how efficient each implementation is in terms of code structure and setup cost;
- how stable and visually convincing the results are under the same GPU configuration;
- which platform is better suited for future work on robot manipulation, deformable objects, cloth, fluids, and multi-physics coupling.

## Main Report

The full comparison report is here:

[Open the full report](report.md)

GitHub does not reliably render embedded local `.mp4` files in Markdown, so the report uses clickable thumbnails. Click any thumbnail in the report to open the corresponding demo video.

## Repository Structure

```text
.
├── report.md              # Main comparison report with clickable video thumbnails
├── video/
│   ├── Genesis/           # Recorded Genesis demo videos
│   └── Newton/            # Recorded Newton demo videos
├── thumbnails/
│   ├── Genesis/           # Preview images used by report.md
│   └── Newton/            # Preview images used by report.md
├── genesis-world/         # Genesis source checkout / reference implementation
└── newton/                # Newton source checkout / reference implementation
```

## Demo Categories

The current report compares the following scene families:

- rigid stacking and collision;
- Franka rigid object grasping;
- hinge and joint constraints;
- robot joint control and inverse kinematics;
- SPH free-surface liquid;
- PBD particle liquid;
- SPH / MPM / rigid coupling;
- MPM multi-material simulation;
- cloth hanging with fixed boundary constraints;
- cloth-rigid collision;
- Franka soft-body grasping;
- FEM / VBD soft-body deformation;
- robot cloth manipulation and T-shirt-style manipulation.

## Video Naming Convention

Videos are named to make the platform, physical category, demo task, and solver/material route visible from the filename.

Pattern:

```text
<platform>_<category>_<task/object>_<solver-or-material>_<detail>.mp4
```

Examples:

```text
video/Genesis/genesis_fluid_sph_liquid_free_surface.mp4
video/Genesis/genesis_robot_franka_grasp_soft_cube_mpm.mp4
video/Newton/newton_robot_franka_cloth_tshirt_manipulation.mp4
video/Newton/newton_cloth_xpbd_hanging_fixed_edge.mp4
```

Each video has a matching thumbnail with the same basename under `thumbnails/`.

## Current Findings

In this stage, **Genesis** is stronger as a fast, unified multi-physics prototyping platform. It provides direct and convenient demos for SPH liquid, PBD liquid, MPM, FEM, cloth, rigid bodies, and multiple coupling cases.

**Newton** is stronger for more engineering-oriented robot and deformable-object workflows. Its advantages are more visible in robot control, IK, VBD / XPBD / Style3D cloth, MPM material experiments, complex contact handling, and robot-cloth or robot-softbody manipulation.

The practical recommendation from the current experiments is to use a **dual-platform strategy**:

- use Genesis for broad multi-physics coverage, fast baselines, and fluid-heavy demos;
- use Newton for robot-cloth, robot-softbody, garment manipulation, and solver-composition-heavy tasks.

## Notes

- The demo videos are committed directly in this repository for convenient review.
- The thumbnails are generated from the videos so GitHub can display visual previews in `report.md`.
- `.DS_Store` files are local macOS artifacts and are not part of the intended project content.
