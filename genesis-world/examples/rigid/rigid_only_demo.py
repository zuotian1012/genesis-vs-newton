import argparse

import genesis as gs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--vis",
        action="store_true",
        help="打开可视化窗口",
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="使用 CPU；默认强制使用 NVIDIA CUDA",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=1500,
        help="仿真帧数",
    )
    args = parser.parse_args()

    # 使用 gs.cuda，可以避免 gs.gpu 在不可用时静默退回 CPU。
    gs.init(
        backend=gs.cpu if args.cpu else gs.cuda,
        precision="32",
        logging_level="info",
    )

    print(f"Genesis backend: {gs.backend}")
    print(f"Genesis device:  {gs.device}")

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(
            dt=0.005,
            substeps=2,
        ),
        rigid_options=gs.options.RigidOptions(
            # 显式开启盒子之间的碰撞检测。
            box_box_detection=True,
        ),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(4.5, -4.5, 3.2),
            camera_lookat=(0.0, 0.0, 1.0),
            camera_fov=40,
            res=(1280, 720),
        ),
        show_viewer=args.vis,
    )

    # 静态地面。
    scene.add_entity(
        morph=gs.morphs.Plane(),
    )

    colors = [
        (0.90, 0.25, 0.20, 1.0),
        (0.20, 0.55, 0.95, 1.0),
        (0.25, 0.80, 0.40, 1.0),
        (0.95, 0.70, 0.20, 1.0),
    ]

    # 盒子塔：全部为自由动态刚体。
    for i in range(12):
        scene.add_entity(
            morph=gs.morphs.Box(
                size=(0.45, 0.45, 0.28),
                pos=(
                    0.04 * (i % 2),
                    0.0,
                    0.16 + 0.30 * i,
                ),
                euler=(
                    0.0,
                    0.0,
                    4.0 * (i % 3),
                ),
                fixed=False,
            ),
            surface=gs.surfaces.Default(
                color=colors[i % len(colors)],
            ),
        )

    # 从侧上方落下的球体。
    for i in range(5):
        scene.add_entity(
            morph=gs.morphs.Sphere(
                radius=0.16,
                pos=(
                    -1.0 + 0.45 * i,
                    -0.65,
                    2.0 + 0.35 * i,
                ),
                fixed=False,
            ),
            surface=gs.surfaces.Default(
                color=(0.65, 0.30, 0.90, 1.0),
            ),
        )

    scene.build()

    for _ in range(args.frames):
        scene.step()


if __name__ == "__main__":
    main()