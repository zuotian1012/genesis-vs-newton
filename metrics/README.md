# Scene Metrics

This directory stores lightweight complexity and runtime statistics for the Genesis vs Newton demo comparison.

The first target is a consistent table, not a full profiler integration. Each demo should be measured with the same high-level rules:

- Count scene complexity after the scene/model is built.
- Measure only the simulation loop.
- Exclude viewer rendering, video recording, video encoding, and screenshot generation from runtime timing.
- Run a short warmup before timing so one-time compilation or cache setup does not dominate the result.
- Record the hardware and backend notes when they affect interpretation.

## Columns

- `platform`: `Genesis` or `Newton`.
- `scene_name`: Human-readable scenario name.
- `video_file`: Existing recorded video path.
- `category`: Broad scene category used in the report.
- `solver`: Main solver or modeling route used by the demo.
- `rigid_body_count`: Number of rigid bodies, if applicable.
- `robot_dof`: Articulated robot joint DoF only.
- `generalized_dof_count`: Generalized model DoF, such as joint DoF in a rigid articulated system.
- `deformable_vertex_count`: Cloth, soft body, or mesh vertices used as a scene-scale proxy.
- `particle_count`: Particle count for SPH, PBD, MPM, or other particle/grid-particle methods.
- `joint_or_constraint_count`: Explicit joints, hinges, constraints, fixed points, or comparable constraints where easy to extract.
- `sim_dt`: Simulation timestep.
- `substeps`: Substeps per external frame or control step.
- `warmup_steps`: Steps run before timing.
- `measured_steps`: Steps included in timing.
- `wall_time_sec`: Wall-clock time for the measured simulation loop.
- `sim_fps`: `measured_steps / wall_time_sec`.
- `real_time_factor`: `(measured_steps * sim_dt) / wall_time_sec`.
- `measurement_mode`: Suggested value is `headless_sim_loop`.
- `notes`: Any caveats, such as viewer disabled, compiler warmup excluded, or counts being estimated.

For deformables and particles, use vertex or particle counts as the primary comparable scale. If a DoF proxy is needed in prose, state it as `vertices x 3` or `particles x 3`, rather than mixing it into `robot_dof`.

## Newton Measurement

Newton demo mappings are stored in `newton_demo_map.csv`.

List available Newton demo keys:

```powershell
python metrics\measure_newton_demo.py --list
```

Measure one demo and print JSON:

```powershell
python metrics\measure_newton_demo.py newton_rigid_joint_constraints_hinge
```

Measure one demo and update `scene_metrics.csv`:

```powershell
python metrics\measure_newton_demo.py newton_rigid_joint_constraints_hinge --update-csv
```

Use shorter runs for expensive demos:

```powershell
python metrics\measure_newton_demo.py newton_robot_franka_cloth_tshirt_manipulation --warmup-steps 5 --measured-steps 20 --update-csv
```

The script matches rows by `video_file` when writing back to `scene_metrics.csv`, so Genesis and Newton scenes may safely share the same `scene_name`.

## Genesis Measurement

Genesis demo mappings are stored in `genesis_demo_map.csv`.

Run these commands from the repository root in the `genesis` conda environment.

List available Genesis demo keys:

```powershell
conda activate genesis
python metrics\measure_genesis_demo.py --list
```

Measure one demo and update `scene_metrics.csv`:

```powershell
python metrics\measure_genesis_demo.py genesis_rigid_stack_tower --update-csv
```

Use shorter runs for expensive particle, cloth, MPM, FEM, or IPC demos:

```powershell
python metrics\measure_genesis_demo.py genesis_mpm_sand_granular --warmup-steps 10 --measured-steps 50 --update-csv
```

The Genesis runner executes the original example script, temporarily disables the viewer, times only post-build `scene.step()` calls, and writes results back by matching `video_file`.

Current caveat: `genesis_robot_franka_ipc_cloth_teleop` fails on the original CPU backend in this Windows environment with an LLVM `IMAGE_REL_AMD64_ADDR32NB relocation` error. Measure it with the GPU backend override:

```powershell
python metrics\measure_genesis_demo.py genesis_robot_franka_ipc_cloth_teleop --force-backend gpu --warmup-steps 10 --measured-steps 50 --update-csv
```
