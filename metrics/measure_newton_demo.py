"""Measure scene complexity and headless simulation FPS for mapped Newton demos.

Examples:

    python metrics/measure_newton_demo.py --list
    python metrics/measure_newton_demo.py newton_rigid_joint_constraints_hinge
    python metrics/measure_newton_demo.py newton_rigid_collision_ball_pyramid --measured-steps 200

Extra example arguments can be appended with --example-args:

    python metrics/measure_newton_demo.py newton_cloth_xpbd_hanging_fixed_edge --example-args "--width 64 --height 32"
"""

from __future__ import annotations

import argparse
import csv
import importlib
import importlib.util
import json
import shlex
import sys
import time
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
NEWTON_ROOT = ROOT / "newton"
MAP_PATH = ROOT / "metrics" / "newton_demo_map.csv"

sys.path.insert(0, str(NEWTON_ROOT))


def load_demo_map() -> list[dict[str, str]]:
    with MAP_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_demo(rows: list[dict[str, str]], key: str) -> dict[str, str]:
    for row in rows:
        if key in (row["demo_key"], row["video_file"], Path(row["video_file"]).stem):
            return row
    choices = ", ".join(row["demo_key"] for row in rows)
    raise SystemExit(f"Unknown demo {key!r}. Choices: {choices}")


def load_module(module_or_file: str) -> ModuleType:
    if module_or_file.startswith("file:"):
        path = (ROOT / module_or_file.removeprefix("file:")).resolve()
        spec = importlib.util.spec_from_file_location(f"metrics_{path.stem}", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load module from {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return importlib.import_module(module_or_file)


def parser_for(module: ModuleType, example_class):
    import newton.examples

    if hasattr(example_class, "create_parser"):
        return example_class.create_parser()
    if hasattr(module, "create_parser"):
        return module.create_parser()
    return newton.examples.create_parser()


def count_or_zero(obj, name: str) -> int:
    return int(getattr(obj, name, 0) or 0)


def is_model_like(obj) -> bool:
    return obj is not None and any(hasattr(obj, name) for name in ("body_count", "particle_count", "joint_count"))


def collect_models(example) -> list:
    models = []
    seen = set()

    def add(obj) -> None:
        if not is_model_like(obj):
            return
        obj_id = id(obj)
        if obj_id in seen:
            return
        seen.add(obj_id)
        models.append(obj)

    add(getattr(example, "model", None))
    for name, value in vars(example).items():
        if name == "model" or name.endswith("_model"):
            add(value)
    return models


def sum_count(models: list, name: str) -> int:
    return sum(count_or_zero(model, name) for model in models)


def infer_frame_dt(example) -> float:
    if hasattr(example, "frame_dt"):
        return float(example.frame_dt)
    if hasattr(example, "sim_dt"):
        return float(example.sim_dt)
    return 0.0


def infer_sim_dt(example) -> float:
    return float(getattr(example, "sim_dt", infer_frame_dt(example)) or 0.0)


def measure(row: dict[str, str], warmup_steps: int, measured_steps: int, device: str | None, example_args: str) -> dict:
    import warp as wp

    import newton.viewer

    if device:
        wp.set_device(device)

    module = load_module(row["module_or_file"])
    example_class = getattr(module, row["class_name"])
    parser = parser_for(module, example_class)

    argv = []
    if row.get("default_args"):
        argv.extend(shlex.split(row["default_args"]))
    if example_args:
        argv.extend(shlex.split(example_args))

    args, unknown = parser.parse_known_args(argv)
    if unknown:
        raise SystemExit(f"Unknown example args for {row['demo_key']}: {' '.join(unknown)}")
    args.viewer = "null"
    args.quiet = True
    if device:
        args.device = device

    wp.config.log_level = max(wp.config.log_level, wp.LOG_WARNING)

    viewer = newton.viewer.ViewerNull(num_frames=warmup_steps + measured_steps)
    example = example_class(viewer, args)
    models = collect_models(example)
    if not models:
        raise RuntimeError(f"{row['demo_key']} did not expose any model-like object")

    for _ in range(warmup_steps):
        example.step()
    wp.synchronize()

    start = time.perf_counter()
    for _ in range(measured_steps):
        example.step()
    wp.synchronize()
    wall_time_sec = time.perf_counter() - start

    frame_dt = infer_frame_dt(example)
    sim_dt = infer_sim_dt(example)
    sim_fps = measured_steps / wall_time_sec
    real_time_factor = measured_steps * frame_dt / wall_time_sec if frame_dt else 0.0

    particle_count = sum_count(models, "particle_count")
    tri_count = sum_count(models, "tri_count")
    tet_count = sum_count(models, "tet_count")
    edge_count = sum_count(models, "edge_count")
    deformable_vertex_count = particle_count

    notes = [
        f"model_count={len(models)}",
        f"shape_count={sum_count(models, 'shape_count')}",
        f"tri_count={tri_count}",
        f"tet_count={tet_count}",
        f"edge_count={edge_count}",
        "viewer=ViewerNull",
        "compile/build excluded",
    ]

    robot_dof_override = row.get("robot_dof_override", "").strip()
    if robot_dof_override:
        robot_dof = int(robot_dof_override)
    elif row["category"].startswith("robot"):
        robot_dof = sum_count(models, "joint_dof_count")
    else:
        robot_dof = 0

    return {
        "platform": "Newton",
        "scene_name": row["scene_name"],
        "video_file": row["video_file"],
        "category": row["category"],
        "solver": row["solver_label"],
        "rigid_body_count": sum_count(models, "body_count"),
        "robot_dof": robot_dof,
        "generalized_dof_count": sum_count(models, "joint_dof_count"),
        "deformable_vertex_count": deformable_vertex_count,
        "particle_count": particle_count,
        "joint_or_constraint_count": sum_count(models, "joint_count"),
        "sim_dt": sim_dt,
        "substeps": count_or_zero(example, "sim_substeps"),
        "warmup_steps": warmup_steps,
        "measured_steps": measured_steps,
        "wall_time_sec": wall_time_sec,
        "sim_fps": sim_fps,
        "real_time_factor": real_time_factor,
        "measurement_mode": "headless_sim_loop",
        "notes": "; ".join(notes),
    }


def update_scene_metrics(result: dict) -> None:
    path = ROOT / "metrics" / "scene_metrics.csv"
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if not fieldnames:
        raise RuntimeError(f"{path} has no CSV header")

    updated = False
    for row in rows:
        if row.get("video_file") == result["video_file"]:
            for key, value in result.items():
                if key in row:
                    row[key] = str(value)
            updated = True
            break

    if not updated:
        raise RuntimeError(f"No matching row found for {result['video_file']}")

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = load_demo_map()

    parser = argparse.ArgumentParser()
    parser.add_argument("demo_key", nargs="?")
    parser.add_argument("--list", action="store_true", help="List available demo keys.")
    parser.add_argument("--warmup-steps", type=int, default=50)
    parser.add_argument("--measured-steps", type=int, default=500)
    parser.add_argument("--device", default=None)
    parser.add_argument("--example-args", default="", help="Additional arguments passed to the target example parser.")
    parser.add_argument("--update-csv", action="store_true", help="Write the measured result into metrics/scene_metrics.csv.")
    args = parser.parse_args()

    if args.list:
        for row in rows:
            print(f"{row['demo_key']}\t{row['module_or_file']}\t{row['default_args']}")
        return

    if not args.demo_key:
        parser.error("demo_key is required unless --list is used")

    row = find_demo(rows, args.demo_key)
    result = measure(row, args.warmup_steps, args.measured_steps, args.device, args.example_args)
    if args.update_csv:
        update_scene_metrics(result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
