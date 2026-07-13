import argparse

import genesis as gs


def main():
    parser = argparse.ArgumentParser(
        description="Genesis basic shapes falling onto a ground plane",
    )
    parser.add_argument(
        "-v",
        "--vis",
        action="store_true",
        help="打开可视化窗口",
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="使用 CPU；默认使用 NVIDIA CUDA",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=1000,
        help="仿真帧数",
    )
    args = parser.parse_args()

    ########################## 初始化 ##########################

    gs.init(
        backend=gs.cpu if args.cpu else gs.cuda,
        precision="32",
        logging_level="info",
    )

    ########################## 创建场景 ##########################

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(
            dt=0.005,
            substeps=2,
            gravity=(0.0, 0.0, -9.81),
        ),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(9.0, -12.0, 5.5),
            camera_lookat=(0.0, 0.0, 2.0),
            camera_fov=38,
            res=(1280, 720),
        ),
        show_viewer=args.vis,
    )

    ########################## 地面 ##########################

    scene.add_entity(
        morph=gs.morphs.Plane(),
        surface=gs.surfaces.Default(
            color=(0.55, 0.55, 0.58, 1.0),
        ),
    )

    ########################## 自由下落刚体 ##########################

    # 三个物体在 X 方向相隔 4 米，因此不会相互碰撞。

    # 左侧盒子。
    scene.add_entity(
        morph=gs.morphs.Box(
            pos=(-4.0, 0.0, 5.0),
            size=(0.8, 0.8, 0.8),
            euler=(20.0, 15.0, 30.0),
            fixed=False,
        ),
        surface=gs.surfaces.Default(
            color=(0.90, 0.25, 0.20, 1.0),
        ),
    )

    # 中间球体。
    scene.add_entity(
        morph=gs.morphs.Sphere(
            pos=(0.0, 0.0, 6.0),
            radius=0.45,
            fixed=False,
        ),
        surface=gs.surfaces.Default(
            color=(0.20, 0.55, 0.95, 1.0),
        ),
    )

    # 右侧圆柱。
    scene.add_entity(
        morph=gs.morphs.Cylinder(
            pos=(4.0, 0.0, 7.0),
            radius=0.40,
            height=1.0,
            euler=(30.0, 20.0, 10.0),
            fixed=False,
        ),
        surface=gs.surfaces.Default(
            color=(0.35, 0.80, 0.40, 1.0),
        ),
    )

    ########################## 构建与运行 ##########################

    scene.build()

    for _ in range(args.frames):
        scene.step()


if __name__ == "__main__":
    main()