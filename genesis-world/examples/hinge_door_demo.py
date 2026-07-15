from pathlib import Path

import numpy as np
import genesis as gs


MJCF_TEXT = """
<mujoco model="genesis_hinged_door">
  <compiler angle="degree" autolimits="true"/>

  <option gravity="0 0 -9.81"/>

  <worldbody>
    <!-- 没有 joint 的根 body 固定在世界坐标系中 -->
    <body name="door_frame">
      <geom
        name="frame_post"
        type="box"
        pos="0 0 0.60"
        size="0.05 0.05 0.60"
        rgba="0.25 0.25 0.30 1"
      />

      <!-- child body 通过一个 revolute/hinge joint 连接 -->
      <body name="door" pos="0.08 0 0.60">
        <joint
          name="door_hinge"
          type="hinge"
          axis="0 0 1"
          limited="true"
          range="-100 100"
          damping="1.0"
          armature="0.02"
        />

        <geom
          name="door_panel"
          type="box"
          pos="0.45 0 0"
          size="0.45 0.035 0.55"
          density="500"
          rgba="0.80 0.30 0.15 1"
        />
      </body>
    </body>
  </worldbody>
</mujoco>
"""


def main() -> None:
    xml_path = Path(__file__).resolve().with_name("hinged_door.xml")
    xml_path.write_text(MJCF_TEXT, encoding="utf-8")

    gs.init(
        backend=gs.gpu,
        precision="32",
        logging_level="info",
    )

    scene = gs.Scene(
        sim_options=gs.options.SimOptions(
            dt=0.01,
            substeps=4,
            gravity=(0.0, 0.0, -9.81),
        ),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(2.2, -2.2, 1.5),
            camera_lookat=(0.50, 0.0, 0.60),
            camera_fov=40,
            max_FPS=60,
        ),
        show_viewer=True,
    )

    scene.add_entity(gs.morphs.Plane())

    door = scene.add_entity(
        gs.morphs.MJCF(file=str(xml_path))
    )

    scene.build()

    hinge_joint = door.get_joint("door_hinge")

    # 同时兼容不同 Genesis 版本中的关节索引属性名称。
    if hasattr(hinge_joint, "dofs_idx_local"):
        hinge_dof = int(hinge_joint.dofs_idx_local[0])
    else:
        hinge_dof = int(hinge_joint.dof_idx_local)

    dofs = [hinge_dof]

    door.set_dofs_kp(
        np.array([80.0], dtype=np.float32),
        dofs_idx_local=dofs,
    )
    door.set_dofs_kv(
        np.array([8.0], dtype=np.float32),
        dofs_idx_local=dofs,
    )

    # 让门板在约 ±52 度范围内周期摆动。
    for step in range(100_000):
        target_angle = 0.9 * np.sin(step * 0.01)

        door.control_dofs_position(
            np.array([target_angle], dtype=np.float32),
            dofs_idx_local=dofs,
        )

        scene.step()


if __name__ == "__main__":
    main()