# SPDX-License-Identifier: Apache-2.0
"""
Custom Newton demo: a free cloth sheet drops onto a static rigid sphere
mounted on a rigid table.

Run from a Newton source checkout:
    uv run --extra examples python cloth_on_rigid_custom.py \
        --viewer gl --device cuda:0 --num-frames 1200
"""

import warp as wp

import newton
import newton.examples


class Example:
    def __init__(self, viewer, args):
        self.viewer = viewer
        self.sim_time = 0.0

        # One rendered frame represents 1/60 s of simulation.
        self.fps = 60
        self.frame_dt = 1.0 / self.fps
        self.sim_substeps = args.sim_substeps
        self.sim_dt = self.frame_dt / self.sim_substeps
        self.iterations = args.solver_iterations

        builder = newton.ModelBuilder(gravity=-9.81)

        # ------------------------------------------------------------------
        # Static rigid platform
        # ------------------------------------------------------------------
        table_half_x = 0.75
        table_half_y = 0.75
        table_half_z = 0.08
        table_center_z = table_half_z

        table_body = builder.add_body(
            xform=wp.transform(
                p=wp.vec3(0.0, 0.0, table_center_z),
                q=wp.quat_identity(),
            ),
            label="rigid_table",
        )

        table_cfg = newton.ModelBuilder.ShapeConfig()
        table_cfg.density = 0.0  # zero density makes this body static
        table_cfg.ke = 5.0e5
        table_cfg.kd = 5.0e3
        table_cfg.mu = 0.55

        builder.add_shape_box(
            table_body,
            hx=table_half_x,
            hy=table_half_y,
            hz=table_half_z,
            cfg=table_cfg,
        )

        # ------------------------------------------------------------------
        # Static rigid sphere sitting on the platform
        # ------------------------------------------------------------------
        sphere_radius = 0.26
        table_top_z = table_center_z + table_half_z
        sphere_center_z = table_top_z + sphere_radius

        sphere_body = builder.add_body(
            xform=wp.transform(
                p=wp.vec3(0.0, 0.0, sphere_center_z),
                q=wp.quat_identity(),
            ),
            label="rigid_sphere",
        )

        sphere_cfg = newton.ModelBuilder.ShapeConfig()
        sphere_cfg.density = 0.0
        sphere_cfg.ke = 5.0e5
        sphere_cfg.kd = 5.0e3
        sphere_cfg.mu = 0.55

        builder.add_shape_sphere(
            sphere_body,
            radius=sphere_radius,
            cfg=sphere_cfg,
        )

        # ------------------------------------------------------------------
        # Free cloth sheet
        # ------------------------------------------------------------------
        resolution = args.cloth_resolution
        cloth_size = 1.20
        cell_size = cloth_size / resolution
        particle_mass = 2.0e-4
        particle_radius = 0.40 * cell_size

        # add_cloth_grid places a (resolution + 1)^2 particle sheet in XY.
        # The position below is the lower-left corner of the sheet.
        builder.add_cloth_grid(
            pos=wp.vec3(-0.5 * cloth_size, -0.5 * cloth_size, 1.10),
            rot=wp.quat_identity(),
            vel=wp.vec3(0.0, 0.0, 0.0),
            dim_x=resolution,
            dim_y=resolution,
            cell_x=cell_size,
            cell_y=cell_size,
            mass=particle_mass,
            fix_left=False,
            fix_right=False,
            fix_top=False,
            fix_bottom=False,
            # In-plane stretch/shear stiffness and damping.
            tri_ke=1.0e3,
            tri_ka=1.0e3,
            tri_kd=1.0e2,
            # Lower bending stiffness makes it behave like soft fabric.
            edge_ke=5.0,
            edge_kd=0.1,
            particle_radius=particle_radius,
        )

        # Ground catches the cloth if it slides off the table.
        ground_cfg = newton.ModelBuilder.ShapeConfig()
        ground_cfg.ke = 1.0e5
        ground_cfg.kd = 1.0e2
        ground_cfg.mu = 0.6
        builder.add_ground_plane(cfg=ground_cfg)

        # VBD requires graph coloring of the cloth constraints.
        builder.color(include_bending=True)

        self.model = builder.finalize()

        # Particle-to-rigid and particle-to-ground contact material.
        self.model.soft_contact_ke = 1.0e5
        self.model.soft_contact_kd = 1.0e2
        self.model.soft_contact_mu = 0.55

        # VBD handles the cloth deformation. Self-contact keeps overlapping
        # folds from passing through one another.
        self.solver = newton.solvers.SolverVBD(
            model=self.model,
            iterations=self.iterations,
            particle_enable_self_contact=True,
            particle_self_contact_radius=0.35 * cell_size,
            particle_self_contact_margin=0.45 * cell_size,
            particle_topological_contact_filter_threshold=2,
            particle_rest_shape_contact_exclusion_radius=0.0,
            rigid_body_particle_contact_buffer_size=8192,
        )

        self.state_0 = self.model.state()
        self.state_1 = self.model.state()
        self.control = self.model.control()

        # Explicit collision pipeline is used because the scene contains
        # particle cloth contacts against rigid shapes.
        self.collision_pipeline = newton.CollisionPipeline(
            self.model,
            broad_phase="nxn",
            soft_contact_margin=0.50 * cell_size,
        )
        self.contacts = self.collision_pipeline.contacts()

        self.viewer.set_model(self.model)
        self.viewer.set_camera(
            pos=wp.vec3(2.0, -2.0, 1.35),
            pitch=-18.0,
            yaw=135.0,
        )
        if hasattr(self.viewer, "camera") and hasattr(self.viewer.camera, "fov"):
            self.viewer.camera.fov = 55.0

        # Deliberately avoid CUDA graph capture in this custom starter demo.
        # It is fast enough on an RTX 5090 and easier to modify/debug.
        self.graph = None

    def simulate(self):
        for _ in range(self.sim_substeps):
            self.state_0.clear_forces()
            self.viewer.apply_forces(self.state_0)

            self.collision_pipeline.collide(self.state_0, self.contacts)

            self.solver.step(
                self.state_0,
                self.state_1,
                self.control,
                self.contacts,
                self.sim_dt,
            )
            self.state_0, self.state_1 = self.state_1, self.state_0

    def step(self):
        self.simulate()
        self.sim_time += self.frame_dt

    def render(self):
        self.viewer.begin_frame(self.sim_time)
        self.viewer.log_state(self.state_0)
        self.viewer.end_frame()

    @staticmethod
    def create_parser():
        parser = newton.examples.create_parser()
        parser.add_argument(
            "--cloth-resolution",
            type=int,
            default=40,
            help="Number of cloth cells along each side; vertices are resolution+1.",
        )
        parser.add_argument(
            "--sim-substeps",
            type=int,
            default=12,
            help="Physics substeps per displayed frame.",
        )
        parser.add_argument(
            "--solver-iterations",
            type=int,
            default=10,
            help="VBD iterations per physics substep.",
        )
        return parser


if __name__ == "__main__":
    parser = Example.create_parser()
    viewer, args = newton.examples.init(parser)
    newton.examples.run(Example(viewer, args), args)