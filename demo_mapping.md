# Demo Mapping（确定版）

本文件记录 `video/` 中每个录屏与源代码 demo 文件之间的最终映射关系。当前版本基于 `report.md`、`video/`、`thumbnails/`、`genesis-world`、`newton` 的代码搜索结果，以及人工确认后的修正整理而成。

当前阶段只做 mapping：未运行 benchmark，未修改任何 demo 逻辑。

说明：

- `confidence` 统一写为 `confirmed`，表示该条 mapping 已进入确定版。
- `needs_manual_check` 统一写为 `否`，表示不再作为 mapping 阻塞项。
- Genesis 铰链门 demo 已人工确认为 `genesis-world/examples/hinge_door_demo.py`。该脚本会在运行时生成 `hinged_door.xml`，再通过 MJCF 加载门框、门板和 hinge joint。

## Mapping 表

| video_path | platform | scene_category | solver_route | likely_source_file | confidence | reason |
|---|---|---|---|---|---|---|
| `video/Genesis/genesis_rigid_stack_tower.mp4` | Genesis | 刚体 / 接触碰撞 / 堆叠稳定性 | Rigid solver，刚体接触与碰撞响应 | `genesis-world/examples/collision/tower.py` | confirmed | 该视频对应 Genesis 刚体堆叠塔场景；源文件构建多层 box tower，并让球体、圆柱等刚体下落碰撞，和视频内容一致。 |
| `video/Genesis/genesis_rigid_hinge_door_joint.mp4` | Genesis | 刚体 / 铰接关节 / hinge door | Rigid solver，revolute/hinge joint articulated rigid body | `genesis-world/examples/hinge_door_demo.py` | confirmed | 已人工确认为自定义 hinge door demo；源文件定义门框、门板和 `door_hinge` hinge joint，并通过目标角控制门板周期摆动。 |
| `video/Genesis/genesis_robot_franka_pick_cube_rigid.mp4` | Genesis | 机器人 / 刚体抓取 / pick-and-place | Rigid solver + Franka IK / 关节控制 | `genesis-world/examples/rigid/franka_cube.py` | confirmed | 源文件加载 Franka 和 cube，包含末端位姿 IK、夹爪闭合和抬升流程；对应视频中的 Franka 抓取刚体立方体。 |
| `video/Genesis/genesis_robot_joint_control_demo.mp4` | Genesis | 机器人 / 关节控制 | Rigid solver + PD / velocity / force control | `genesis-world/examples/tutorials/control_your_robot.py` | confirmed | 已按当前确认结果映射到 Genesis 机器人控制 tutorial；该 demo 展示关节位置控制、速度控制和力控制，符合视频中的机器人关节控制场景。 |
| `video/Genesis/genesis_fluid_sph_liquid_free_surface.mp4` | Genesis | 流体 / SPH 液体 / 自由表面 | SPH solver | `genesis-world/examples/tutorials/sph_liquid.py` | confirmed | 该 tutorial 为 SPH liquid 示例；视频展示液体粒子自由表面和边界碰撞。 |
| `video/Genesis/genesis_fluid_pbd_liquid_particles.mp4` | Genesis | 流体 / PBD 液体粒子 | PBD solver，particle-based liquid | `genesis-world/examples/pbd_liquid.py` | confirmed | 源文件为 PBD liquid 示例；视频展示粒子液体流动与聚集形态。 |
| `video/Genesis/genesis_coupling_sph_liquid_rigid.mp4` | Genesis | 多物理耦合 / SPH 液体 + 刚体 | SPH solver + Rigid solver coupling | `genesis-world/examples/coupling/sph_rigid.py` | confirmed | 源文件为 SPH-rigid coupling 示例；视频展示液体粒子与刚体方块之间的耦合交互。 |
| `video/Genesis/genesis_mpm_sand_granular.mp4` | Genesis | 颗粒材料 / MPM sand / 刚体交互 | MPM solver，sand material + rigid coupling | `genesis-world/examples/coupling/sand_wheel.py` | confirmed | 源文件使用 MPM sand 与轮状刚体交互；视频展示沙土/颗粒材料受刚体扰动后的堆积与流散。 |
| `video/Genesis/genesis_mpm_elastic_liquid_plastic_demo.mp4` | Genesis | MPM 多材料 / elastic-liquid-plastic | MPM solver，多材料参数 | `genesis-world/examples/tutorials/mpm.py` | confirmed | 源文件包含 Elastic、Liquid、ElastoPlastic 等 MPM 材料设置；视频展示多材料 MPM 对比。 |
| `video/Genesis/genesis_cloth_pbd_hanging_fixed_edge.mp4` | Genesis | 布料 / PBD 悬挂 / 固定边界 | PBD solver，cloth particles / fixed vertices | `genesis-world/examples/tutorials/pbd_cloth.py` | confirmed | 源文件为 PBD cloth tutorial，并设置固定粒子/固定边界；对应视频中的悬挂布料。 |
| `video/Genesis/genesis_cloth_rigid_collision.mp4` | Genesis | 布料-刚体耦合 / 碰撞 | PBD cloth + Rigid collider coupling | `genesis-world/examples/coupling/cloth_on_rigid.py` | confirmed | 源文件为 cloth_on_rigid 示例；视频展示布料落到刚体球/支撑物上的接触与包覆。 |
| `video/Genesis/genesis_robot_franka_grasp_soft_cube_mpm.mp4` | Genesis | 机器人 / 软体抓取 / MPM soft cube | Rigid robot + MPM elastic body coupling | `genesis-world/examples/coupling/grasp_soft_cube.py` | confirmed | 源文件为 Franka 抓取 MPM soft cube 示例；对应视频中的机械臂夹取软立方体。 |
| `video/Genesis/genesis_softbody_fem_deformation.mp4` | Genesis | 软体 / FEM 形变 | FEM solver，soft body constraints / deformation | `genesis-world/examples/fem_hard_and_soft_constraint.py` | confirmed | 源文件创建 FEM soft object 并设置硬/软约束；视频展示软体在外力、约束和碰撞下的变形。 |
| `video/Genesis/genesis_robot_franka_ipc_cloth_teleop.mp4` | Genesis | 机器人 / IPC 布料操作 / teleoperation | IPC solver / IPC coupling + FEM cloth + Rigid robot | `genesis-world/examples/IPC_Solver/ipc_robot_cloth_teleop.py` | confirmed | 源文件名与视频名一致；demo 包含 Franka、IPC coupler、布料和键盘 teleop，用于验证机器人-布料接触操作。 |
| `video/Newton/newton_rigid_collision_ball_pyramid.mp4` | Newton | 刚体 / 球-金字塔碰撞 | XPBD rigid contact solver | `newton/newton/examples/contacts/example_pyramid.py` | confirmed | 源文件为 box pyramid 示例，包含方块金字塔与 wrecking ball；视频展示球体冲击刚体金字塔。 |
| `video/Newton/newton_robot_franka_pick_stack_cube.mp4` | Newton | 机器人 / 刚体抓取堆叠 | MuJoCo rigid / SDF collision + IK / 状态机控制 | `newton/newton/examples/contacts/example_brick_stacking.py` | confirmed | 源文件为 Franka brick stacking 示例；视频展示机械臂拾取、移动并堆叠刚体砖块。 |
| `video/Newton/newton_rigid_joint_constraints_hinge.mp4` | Newton | 刚体 / joint constraints / hinge 等关节 | XPBD 或 VBD joint constraint route | `newton/newton/examples/basic/example_basic_joints.py` | confirmed | 源文件展示 ball、distance、prismatic、revolute 等基础关节/约束；视频对应关节约束集合。 |
| `video/Newton/newton_robot_ur10_joint_control.mp4` | Newton | 机器人 / UR10 关节控制 | MuJoCo / articulated robot joint target control | `newton/newton/examples/robot/example_robot_ur10.py` | confirmed | 源文件加载 UR10 并施加关节目标控制；对应视频中的 UR10 关节运动。 |
| `video/Newton/newton_robot_franka_inverse_kinematics.mp4` | Newton | 机器人 / Franka IK | IK route + articulated robot control | `newton/newton/examples/ik/example_ik_franka.py` | confirmed | 源文件为 Franka inverse kinematics 示例；视频展示末端目标跟踪和 IK 结果。 |
| `video/Newton/newton_coupling_mpm_rigid_twoway.mp4` | Newton | 多物理耦合 / MPM + 刚体双向耦合 | Implicit MPM + rigid coupling / MuJoCo route | `newton/newton/examples/mpm/example_mpm_twoway_coupling.py` | confirmed | 源文件为 MPM two-way coupling 示例；视频展示 MPM 材料与刚体之间的双向作用。 |
| `video/Newton/newton_mpm_liquid_viscous_flow.mp4` | Newton | 流体 / MPM 黏性液体 | Implicit MPM viscous material route | `newton/newton/examples/mpm/example_mpm_viscous.py` | confirmed | 源文件为 MPM viscous 示例；视频展示黏性材料/液体从漏斗或喷嘴下落流动。 |
| `video/Newton/newton_mpm_multi_material_demo.mp4` | Newton | MPM 多材料 / sand-snow-mud 等 | Implicit MPM multi-material route | `newton/newton/examples/mpm/example_mpm_multi_material.py` | confirmed | 源文件为 MPM multi material 示例；视频展示不同 MPM 材料块的形变与运动差异。 |
| `video/Newton/newton_cloth_xpbd_hanging_fixed_edge.mp4` | Newton | 布料 / XPBD 悬挂 / 固定边界 | Cloth XPBD solver route | `newton/newton/examples/cloth/example_cloth_hanging.py` | confirmed | 源文件的 hanging cloth 示例支持多 solver；该视频对应 XPBD 参数路线。 |
| `video/Newton/newton_cloth_vbd_hanging_fixed_edge.mp4` | Newton | 布料 / VBD 悬挂 / 固定边界 | Cloth VBD solver route | `newton/newton/examples/cloth/example_cloth_hanging.py` | confirmed | 源文件的 hanging cloth 示例支持多 solver；该视频对应 VBD 参数路线。 |
| `video/Newton/newton_cloth_style3d_garment_demo.mp4` | Newton | 布料 / 服装仿真 / garment | Style3D cloth solver route | `newton/newton/examples/cloth/example_cloth_style3d.py` | confirmed | 源文件为 Style3D garment 示例；视频展示服装/衣片布料仿真。 |
| `video/Newton/newton_cloth_rigid_collision.mp4` | Newton | 布料-刚体耦合 / 碰撞 | VBD cloth + rigid collider route | `newton/cloth_on_rigid_custom.py` | confirmed | 当前仓库中存在自定义 cloth_on_rigid 脚本；视频展示布料与刚体球/支撑物的接触碰撞。 |
| `video/Newton/newton_robot_franka_grasp_softbody_vbd.mp4` | Newton | 机器人 / 软体抓取 / VBD soft body | VBD softbody + articulated Franka / IK route | `newton/newton/examples/softbody/example_softbody_franka.py` | confirmed | 源文件为 Franka grasp softbody 示例；视频展示机械臂抓取 VBD 软体对象。 |
| `video/Newton/newton_softbody_vbd_hanging_damping.mp4` | Newton | 软体 / VBD 悬挂 / 阻尼对比 | VBD softbody solver，damping parameter sweep | `newton/newton/examples/softbody/example_softbody_hanging.py` | confirmed | 源文件为 softbody hanging 示例，包含不同 damping 设置；视频展示多个软体块悬挂和振荡差异。 |
| `video/Newton/newton_robot_franka_cloth_tshirt_manipulation.mp4` | Newton | 机器人 / 布料 T-shirt 操作 | VBD cloth + articulated Franka coupling | `newton/newton/examples/cloth/example_cloth_franka.py` | confirmed | 源文件为 Franka cloth manipulation 示例；视频展示机械臂操作 T-shirt/布料网格。 |

## 已确认后的注意事项

1. 本表共有 29 条 mapping，覆盖当前 `video/Genesis` 与 `video/Newton` 下的全部 `.mp4` 视频。
2. 所有 mapping 均已进入确定版，`needs_manual_check` 不再作为后续统计的阻塞项。
3. 所有 `likely_source_file` 路径均能在当前工作区找到，可作为下一阶段自动化统计和 benchmark 的输入。
4. 下一阶段可以在本表基础上追加 `run_command`、`num_bodies`、`num_particles_or_vertices`、`num_dofs`、`sim_fps`、`viewer_fps`、`gpu`、`notes` 等字段。
