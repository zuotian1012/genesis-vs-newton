"""Measure scene complexity and headless simulation FPS for mapped Genesis demos.

This runner executes the original Genesis example script, but temporarily wraps
``genesis.Scene`` so that viewer rendering is disabled and timing stops after a
fixed number of post-build simulation steps.

Examples:

    python metrics/measure_genesis_demo.py --list
    python metrics/measure_genesis_demo.py genesis_rigid_stack_tower --update-csv
"""

from __future__ import annotations

import argparse
import csv
import json
import runpy
import shlex
import sys
import time
from pathlib import Path


try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
GENESIS_ROOT = ROOT / "genesis-world"
MAP_PATH = ROOT / "metrics" / "genesis_demo_map.csv"

sys.path.insert(0, str(GENESIS_ROOT))


class MeasurementComplete(Exception):
    pass


class DummyViewer:
    def update(self, *args, **kwargs):
        return None

    def register_keybinds(self, *args, **kwargs):
        return None

    def is_alive(self):
        return True

    def stop(self):
        return None


def load_demo_map() -> list[dict[str, str]]:
    with MAP_PATH.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find_demo(rows: list[dict[str, str]], key: str) -> dict[str, str]:
    for row in rows:
        if key in (row["demo_key"], row["video_file"], Path(row["video_file"]).stem):
            return row
    choices = ", ".join(row["demo_key"] for row in rows)
    raise SystemExit(f"Unknown demo {key!r}. Choices: {choices}")


def count_or_zero(obj, name: str) -> int:
    try:
        value = getattr(obj, name)
    except Exception:
        return 0
    if callable(value):
        return 0
    try:
        return int(value or 0)
    except Exception:
        return 0


def sync_device() -> None:
    try:
        import torch

        if torch.cuda.is_available():
            torch.cuda.synchronize()
    except Exception:
        pass


def solver_names(scene) -> list[str]:
    try:
        return [type(solver).__name__ for solver in scene.active_solvers]
    except Exception:
        return []


def collect_counts(scene) -> dict[str, int | str]:
    entities = list(getattr(scene, "entities", []) or [])
    rigid_solver = getattr(scene, "rigid_solver", None)

    rigid_body_count = count_or_zero(rigid_solver, "n_links")
    generalized_dof_count = count_or_zero(rigid_solver, "n_dofs")
    joint_count = count_or_zero(rigid_solver, "n_joints") or count_or_zero(rigid_solver, "n_equalities")

    particle_count = 0
    deformable_vertex_count = 0
    tri_count = 0
    tet_count = 0
    edge_count = 0

    for entity in entities:
        entity_type = type(entity).__name__.lower()
        entity_particles = count_or_zero(entity, "n_particles")
        entity_verts = count_or_zero(entity, "n_verts") or count_or_zero(entity, "n_vertices")
        particle_count += entity_particles
        if "rigid" not in entity_type:
            deformable_vertex_count += entity_particles or entity_verts
        tri_count += count_or_zero(entity, "n_faces")
        tet_count += count_or_zero(entity, "n_tets") or count_or_zero(entity, "n_elements")
        edge_count += count_or_zero(entity, "n_edges")

    for solver in getattr(scene, "active_solvers", []) or []:
        name = type(solver).__name__.lower()
        if "rigid" in name:
            continue
        solver_particles = count_or_zero(solver, "n_particles")
        solver_verts = count_or_zero(solver, "n_verts") or count_or_zero(solver, "n_vertices")
        particle_count = max(particle_count, solver_particles)
        deformable_vertex_count = max(deformable_vertex_count, solver_particles or solver_verts)
        tri_count = max(tri_count, count_or_zero(solver, "n_faces") or count_or_zero(solver, "n_tris"))
        tet_count = max(tet_count, count_or_zero(solver, "n_tets") or count_or_zero(solver, "n_elements"))
        edge_count = max(edge_count, count_or_zero(solver, "n_edges"))

    return {
        "entity_count": len(entities),
        "rigid_body_count": rigid_body_count,
        "generalized_dof_count": generalized_dof_count,
        "joint_or_constraint_count": joint_count,
        "particle_count": particle_count,
        "deformable_vertex_count": deformable_vertex_count,
        "tri_count": tri_count,
        "tet_count": tet_count,
        "edge_count": edge_count,
        "active_solvers": "+".join(solver_names(scene)),
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


def measure(
    row: dict[str, str],
    warmup_steps: int,
    measured_steps: int,
    example_args: str,
    force_backend: str,
) -> dict:
    import genesis as gs

    original_scene = gs.Scene
    original_init = gs.init
    state = {
        "scene": None,
        "counts": {},
        "step_count": 0,
        "start": None,
        "wall_time_sec": None,
    }

    class TrackingScene(original_scene):
        def __init__(self, *args, **kwargs):
            kwargs["show_viewer"] = False
            super().__init__(*args, **kwargs)
            state["scene"] = self

        def build(self, *args, **kwargs):
            result = super().build(*args, **kwargs)
            state["counts"] = collect_counts(self)
            if getattr(self, "viewer", None) is None:
                self._visualizer._viewer = DummyViewer()
            return result

        def step(self, *args, **kwargs):
            i = int(state["step_count"])
            if i == warmup_steps:
                sync_device()
                state["start"] = time.perf_counter()

            result = super().step(*args, **kwargs)
            state["step_count"] = i + 1

            if i + 1 == warmup_steps + measured_steps:
                sync_device()
                state["wall_time_sec"] = time.perf_counter() - float(state["start"])
                raise MeasurementComplete()
            return result

    def tracking_init(*args, **kwargs):
        kwargs["logging_level"] = "warning"
        if force_backend:
            kwargs["backend"] = getattr(gs, force_backend)
        return original_init(*args, **kwargs)

    gs.Scene = TrackingScene
    gs.init = tracking_init

    script_path = ROOT / row["script_path"]
    old_argv = sys.argv[:]
    argv = [str(script_path)]
    if row.get("default_args"):
        argv.extend(shlex.split(row["default_args"]))
    if example_args:
        argv.extend(shlex.split(example_args))
    sys.argv = argv

    try:
        runpy.run_path(str(script_path), run_name="__main__")
    except MeasurementComplete:
        pass
    finally:
        sys.argv = old_argv
        gs.Scene = original_scene
        gs.init = original_init

    scene = state["scene"]
    if scene is None or state["wall_time_sec"] is None:
        raise RuntimeError(f"{row['demo_key']} did not reach the requested measured steps")

    counts = dict(state["counts"])
    wall_time_sec = float(state["wall_time_sec"])
    sim_fps = measured_steps / wall_time_sec
    sim_dt = float(getattr(scene, "dt", 0.0) or 0.0)
    real_time_factor = measured_steps * sim_dt / wall_time_sec if sim_dt else 0.0

    robot_dof_override = row.get("robot_dof_override", "").strip()
    robot_dof = int(robot_dof_override) if robot_dof_override else 0

    notes = [
        f"entity_count={counts['entity_count']}",
        f"active_solvers={counts['active_solvers']}",
        f"tri_count={counts['tri_count']}",
        f"tet_count={counts['tet_count']}",
        f"edge_count={counts['edge_count']}",
        "show_viewer=False",
        "compile/build excluded",
    ]
    if force_backend:
        notes.append(f"force_backend={force_backend}")

    return {
        "platform": "Genesis",
        "scene_name": row["scene_name"],
        "video_file": row["video_file"],
        "category": row["category"],
        "solver": row["solver_label"],
        "rigid_body_count": counts["rigid_body_count"],
        "robot_dof": robot_dof,
        "generalized_dof_count": counts["generalized_dof_count"],
        "deformable_vertex_count": counts["deformable_vertex_count"],
        "particle_count": counts["particle_count"],
        "joint_or_constraint_count": counts["joint_or_constraint_count"],
        "sim_dt": sim_dt,
        "substeps": int(getattr(scene, "substeps", 0) or 0),
        "warmup_steps": warmup_steps,
        "measured_steps": measured_steps,
        "wall_time_sec": wall_time_sec,
        "sim_fps": sim_fps,
        "real_time_factor": real_time_factor,
        "measurement_mode": "headless_sim_loop",
        "notes": "; ".join(notes),
    }


def main() -> None:
    rows = load_demo_map()

    parser = argparse.ArgumentParser()
    parser.add_argument("demo_key", nargs="?")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--warmup-steps", type=int, default=20)
    parser.add_argument("--measured-steps", type=int, default=100)
    parser.add_argument("--example-args", default="")
    parser.add_argument("--force-backend", choices=["cpu", "gpu", "cuda"], default="")
    parser.add_argument("--update-csv", action="store_true")
    args = parser.parse_args()

    if args.list:
        for row in rows:
            print(f"{row['demo_key']}\t{row['script_path']}\t{row['default_args']}")
        return

    if not args.demo_key:
        parser.error("demo_key is required unless --list is used")

    row = find_demo(rows, args.demo_key)
    result = measure(row, args.warmup_steps, args.measured_steps, args.example_args, args.force_backend)
    if args.update_csv:
        update_scene_metrics(result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
