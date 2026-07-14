"""Measure scene complexity and headless simulation FPS for Newton basic_joints.

Run from the repository root:

    python metrics/measure_newton_basic_joints.py

This script expects the Newton example dependencies to be installed, especially
warp-lang.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NEWTON_ROOT = ROOT / "newton"
sys.path.insert(0, str(NEWTON_ROOT))

import warp as wp  # noqa: E402

import newton  # noqa: E402
import newton.examples  # noqa: E402
import newton.viewer  # noqa: E402
from newton.examples.basic.example_basic_joints import Example  # noqa: E402


def count_or_zero(obj, name: str) -> int:
    return int(getattr(obj, name, 0) or 0)


def main() -> None:
    warmup_steps = 50
    measured_steps = 500

    parser = newton.examples.create_parser()
    parser.add_argument("--solver", choices=["xpbd", "vbd"], default="xpbd")
    args = parser.parse_args(["--viewer", "null", "--quiet"])

    viewer = newton.viewer.ViewerNull(num_frames=warmup_steps + measured_steps)
    example = Example(viewer, args)
    model = example.model

    for _ in range(warmup_steps):
        example.step()
    wp.synchronize()

    start = time.perf_counter()
    for _ in range(measured_steps):
        example.step()
    wp.synchronize()
    wall_time_sec = time.perf_counter() - start

    sim_fps = measured_steps / wall_time_sec
    real_time_factor = measured_steps * example.frame_dt / wall_time_sec

    result = {
        "platform": "Newton",
        "scene_name": "Rigid joint constraints hinge",
        "video_file": "video/Newton/newton_rigid_joint_constraints_hinge.mp4",
        "category": "rigid_joint",
        "solver": "XPBD rigid constraints",
        "rigid_body_count": count_or_zero(model, "body_count"),
        "robot_dof": 0,
        "generalized_dof_count": count_or_zero(model, "joint_dof_count"),
        "deformable_vertex_count": 0,
        "particle_count": count_or_zero(model, "particle_count"),
        "joint_or_constraint_count": count_or_zero(model, "joint_count"),
        "sim_dt": example.sim_dt,
        "substeps": example.sim_substeps,
        "warmup_steps": warmup_steps,
        "measured_steps": measured_steps,
        "wall_time_sec": wall_time_sec,
        "sim_fps": sim_fps,
        "real_time_factor": real_time_factor,
        "measurement_mode": "headless_sim_loop",
        "notes": f"shape_count={count_or_zero(model, 'shape_count')}; viewer=ViewerNull",
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
