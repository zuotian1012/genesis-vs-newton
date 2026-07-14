#!/usr/bin/env python3
"""Minimal simulation-only FPS probe for a small set of Newton demos.

This is intentionally not a full benchmark framework. It only wraps two easy
Newton examples selected from demo_mapping/static_demo_stats and writes a
small CSV row for each run.
"""

from __future__ import annotations

import argparse
import csv
import importlib
import pathlib
import sys
import time
from dataclasses import dataclass


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
NEWTON_ROOT = REPO_ROOT / "newton"
if str(NEWTON_ROOT) not in sys.path:
    sys.path.insert(0, str(NEWTON_ROOT))

import warp as wp  # noqa: E402


RESULTS_PATH = REPO_ROOT / "results" / "newton_runtime_fps.csv"
FIELDNAMES = [
    "id",
    "platform",
    "source_file",
    "solver_route",
    "mode",
    "warmup_steps",
    "benchmark_steps",
    "elapsed_sec",
    "sim_fps",
    "dt",
    "substeps",
    "solver_iterations",
    "viewer_on",
    "recording_on",
    "stable",
    "notes",
]


@dataclass(frozen=True)
class DemoSpec:
    demo_id: str
    source_file: str
    module: str
    solver_route: str
    parser_args: tuple[str, ...]
    dt: str
    substeps: str
    solver_iterations: str


DEMOS: dict[str, DemoSpec] = {
    "N01": DemoSpec(
        demo_id="N01",
        source_file="newton/newton/examples/contacts/example_pyramid.py",
        module="newton.examples.contacts.example_pyramid",
        solver_route="XPBD rigid contact",
        parser_args=("--viewer", "null", "--quiet"),
        dt="0.001",
        substeps="10",
        solver_iterations="XPBD_ITERATIONS=2",
    ),
    "N09a": DemoSpec(
        demo_id="N09a",
        source_file="newton/newton/examples/cloth/example_cloth_hanging.py",
        module="newton.examples.cloth.example_cloth_hanging",
        solver_route="XPBD cloth solver",
        parser_args=("--viewer", "null", "--quiet", "--solver", "xpbd"),
        dt="1/600",
        substeps="10",
        solver_iterations="iterations=10",
    ),
    "N09b": DemoSpec(
        demo_id="N09b",
        source_file="newton/newton/examples/cloth/example_cloth_hanging.py",
        module="newton.examples.cloth.example_cloth_hanging",
        solver_route="VBD cloth solver",
        parser_args=("--viewer", "null", "--quiet", "--solver", "vbd"),
        dt="1/600",
        substeps="10",
        solver_iterations="iterations=10",
    ),
}


class NullViewer:
    """Small no-op viewer for simulation-only use.

    The selected Newton examples only need these methods during construction
    and stepping. Keeping this local avoids opening GUI viewers and avoids
    changing upstream demo code.
    """

    def set_model(self, model):
        self.model = model

    def set_camera(self, *args, **kwargs):
        return None

    def apply_forces(self, state):
        return None

    def begin_frame(self, sim_time):
        return None

    def log_state(self, *args, **kwargs):
        return None

    def log_contacts(self, *args, **kwargs):
        return None

    def end_frame(self):
        return None

    def close(self):
        return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--demo",
        action="append",
        choices=sorted(DEMOS),
        help="Demo id to run. Repeatable. Defaults to N01 and N09a.",
    )
    parser.add_argument("--warmup-steps", type=int, default=50)
    parser.add_argument("--benchmark-steps", type=int, default=200)
    parser.add_argument(
        "--allow-cpu",
        action="store_true",
        help="Allow CPU-only Warp runs. Off by default to avoid recording non-RTX-5090 FPS by accident.",
    )
    parser.add_argument("--output", type=pathlib.Path, default=RESULTS_PATH)
    return parser.parse_args()


def build_example(spec: DemoSpec):
    module = importlib.import_module(spec.module)
    parser = module.Example.create_parser()
    demo_args = parser.parse_args(list(spec.parser_args))
    viewer = NullViewer()
    return module.Example(viewer, demo_args)


def synchronize():
    try:
        wp.synchronize()
    except Exception:
        # Some CPU-only paths may not require or expose synchronization.
        pass


def cuda_available() -> bool:
    try:
        return any("cuda" in str(device).lower() for device in wp.get_devices())
    except Exception:
        return False


def run_demo(spec: DemoSpec, warmup_steps: int, benchmark_steps: int, allow_cpu: bool) -> dict[str, str]:
    notes: list[str] = []
    stable = True
    elapsed = 0.0
    sim_fps = 0.0

    try:
        if not allow_cpu and not cuda_available():
            raise RuntimeError("CUDA device is not available in this Python/Warp environment")

        example = build_example(spec)

        for _ in range(warmup_steps):
            example.step()
        synchronize()

        start = time.perf_counter()
        for _ in range(benchmark_steps):
            example.step()
        synchronize()
        elapsed = time.perf_counter() - start
        sim_fps = benchmark_steps / elapsed if elapsed > 0 else 0.0
        notes.append("simulation-only; NullViewer; no recording")
        notes.append(f"warp_devices={','.join(str(device) for device in wp.get_devices())}")
    except Exception as exc:  # noqa: BLE001 - report blocked rows instead of crashing batch.
        stable = False
        notes.append(f"blocked: {type(exc).__name__}: {exc}")
        try:
            notes.append(f"warp_devices={','.join(str(device) for device in wp.get_devices())}")
        except Exception:
            pass

    return {
        "id": spec.demo_id,
        "platform": "Newton",
        "source_file": spec.source_file,
        "solver_route": spec.solver_route,
        "mode": "simulation-only",
        "warmup_steps": str(warmup_steps),
        "benchmark_steps": str(benchmark_steps),
        "elapsed_sec": f"{elapsed:.6f}" if stable else "unknown",
        "sim_fps": f"{sim_fps:.3f}" if stable else "unknown",
        "dt": spec.dt,
        "substeps": spec.substeps,
        "solver_iterations": spec.solver_iterations,
        "viewer_on": "false",
        "recording_on": "false",
        "stable": str(stable).lower(),
        "notes": "; ".join(notes),
    }


def append_rows(path: pathlib.Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    demo_ids = args.demo or ["N01", "N09a"]
    rows = [
        run_demo(DEMOS[demo_id], args.warmup_steps, args.benchmark_steps, args.allow_cpu)
        for demo_id in demo_ids
    ]
    append_rows(args.output, rows)

    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
