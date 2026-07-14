# Genesis 与 Newton 多物理仿真实现对比报告

> 当前版本定位：**评估型报告模板**。现有视频用于证明 demo 已经跑通；静态场景参数已根据 `results/static_demo_stats.csv` 先行补齐，FPS、稳定性、实现成本和压力测试结论仍按 `NEXT_STEPS.md` 逐步补充。

## 1. 评估目标

本项目在同一硬件环境下使用 Genesis 和 Newton 分别复现一组经典多物理仿真 demo，覆盖刚体、机器人、软体、布料、流体以及多物理耦合场景。现阶段的现象覆盖已经比较完整，但仅展示“都能跑”还不足以支持平台选型。因此，下一阶段评估重点转向：

- 哪些场景两个平台都能稳定完成；
- 哪些场景能体现某个平台的短板或不适合方向；
- 哪些场景能验证平台自己声称的独特优势；
- 在 RTX 5090 上，各 demo 的仿真效率、场景规模和稳定性如何；
- 后续如果做机器人可变形物操作、布料、流体或多物理耦合，应优先选择哪个平台。

## 2. 统一实验环境

| 项目 | 当前记录 |
|---|---|
| GPU | RTX 5090 |
| CPU | [待补充] |
| RAM | [待补充] |
| OS | [待补充] |
| CUDA / Driver | [待补充] |
| Genesis commit | [待补充] |
| Newton commit | [待补充] |
| Python version | [待补充] |
| 是否开启 viewer | [待补充：分别记录 viewer on / off] |
| 是否录屏 | [待补充：recording on / off] |

> 后续 FPS 对比必须区分 **simulation-only FPS** 和 **viewer/render FPS**。录屏会影响性能，不能只用录屏时的体感速度作为最终结论。

## 3. 评价指标定义

| 指标 | 含义 | 记录方式 |
|---|---|---|
| Scene support | 平台是否能直接表达该场景 | `直接支持 / 需要改写 / 只能近似 / 暂不支持` |
| Solver route | 使用的主要求解器或耦合方式 | 如 SPH、PBD、MPM、FEM、IPC、XPBD、VBD、Style3D、Featherstone |
| Scene scale | 场景规模 | 刚体数、关节数、粒子数、顶点数、面片数、四面体数、机器人 DOF |
| Simulation FPS | 不含渲染的平均仿真 FPS | warmup 后统计固定步数 wall time |
| Viewer FPS | 开 viewer 时的平均显示 FPS | 单独统计，避免和 sim FPS 混在一起 |
| Stability | 稳定性 | 是否爆炸、穿模、严重抖动、能量漂移、接触卡死 |
| Implementation cost | 实现成本 | 代码行数、改动文件数、调参时间、API 复杂度 |
| Visual quality | 视觉/物理效果 | 主观评分 + 典型失败截图/视频 |
| Follow-up suitability | 后续适配性 | 是否适合继续做目标方向 |

## 4. 当前现象覆盖总览

| 场景类别 | Genesis 当前状态 | Newton 当前状态 | 初步差异 | 数据状态 |
|---|---|---|---|---|
| 刚体堆叠/碰撞 | 已跑通 | 已跑通 | Newton 更偏复杂碰撞网络；Genesis 更轻量 | 静态规模已补，FPS 待测 |
| Franka 抓取刚体 | 已跑通 | 已跑通 | Newton 任务链更完整；Genesis 更易搭 | DOF 已补，FPS 待测 |
| 铰链/关节约束 | 已跑通 | 已跑通 | Newton 关节类型展示更系统 | 部分 DOF 已补，FPS 待测 |
| 机器人控制/IK | 已跑通 | 已跑通 | Newton IK 和控制链更细 | 部分 DOF 已补，FPS 待测 |
| SPH 液体 | 已跑通 | [待补充：直接支持/近似/不支持] | Genesis 直接 SPH 更强 | Genesis 参数已补，Newton 对照待做 |
| PBD 液体 | 已跑通 | [待补充：直接支持/近似/不支持] | Genesis PBD 液体入口更直接 | Genesis 参数已补，Newton 对照待做 |
| MPM/刚体耦合 | 已跑通 | 已跑通 | Newton MPM 工程化较强；Genesis 求解器覆盖广 | 静态参数已补，FPS 待测 |
| MPM 多材料 | 已跑通 | 已跑通 | Newton 更适合材料模型对比 | 材料/采样参数已补，FPS 待测 |
| 布料下垂 | 已跑通 | 已跑通 | Newton 可比较 XPBD/VBD/Style3D | 顶点规模已补，FPS 待测 |
| 布料-刚体接触 | 已跑通 | 已跑通 | 接触稳定性需要压力测试 | 顶点规模已补，自碰撞/穿模待测 |
| 机器人抓软体 | 已跑通 | 已跑通 | Newton 更适合复杂机器人-软体管线 | 部分 DOF/solver 参数已补，FPS 待测 |
| 软体悬挂 | 已跑通 | 已跑通 | Genesis 偏 FEM；Newton 偏 VBD | solver 参数已补，精确 tets 待补 |
| 机器人布料操作 | 已跑通遥操作 | 已跑通 T-shirt 操作 | Newton 更接近自动化衣物操作 | solver/部分 DOF 已补，稳定性/FPS 待测 |

## 5. 已知静态统计与待测指标

本节根据 `results/static_demo_stats.csv` 回填已经能从源码静态确认的信息。`unknown` 表示当前源码或资产入口中无法直接确认，后续不要猜测；FPS、稳定性和实现成本仍需按 `NEXT_STEPS.md` 手工运行或最小 wrapper 补齐。

| ID | 平台 | 场景 | 求解器路线 | 已知规模 / DOF | dt / substeps | solver iterations | viewer | FPS 状态 | sim FPS | 稳定性 | 备注 |
|---|---|---|---|---|---|---|---|---|---:|---|---|
| G01 | Genesis | 刚体塔堆叠 | Rigid | 约 100 个塔中 box + plane + 下落刚体；DOF unknown | 0.0015 / unknown | unknown | args.vis 默认 false | 可从 Genesis 终端记录 | [待记录] | [待测] | `num_stacks=50`，每层 2 个 box |
| G02 | Genesis | 铰链门 | Rigid hinge joint | 1 个 hinge DOF | 0.01 / 4 | unknown | true | 可从 Genesis 终端记录 | [待记录] | [待测] | 自定义门框、门板和 hinge joint |
| G03 | Genesis | Franka 抓取刚体 | Rigid + IK | Franka 9 DOF | 0.01 / unknown | unknown | args.vis 默认 false | 可从 Genesis 终端记录 | [待记录] | [待测] | 7 个 arm joints + 2 个 finger joints |
| G04 | Genesis | 机器人关节控制 | Rigid + PD/velocity/force control | 机器人 9 DOF | 0.01 / unknown | unknown | true | 可从 Genesis 终端记录 | [待记录] | [待测] | 展示位置、速度、力控制 |
| G05 | Genesis | SPH 自由液面 | SPH | particle size = 0.01；particle count unknown | 4e-3 / 10 | unknown | true | 可从 Genesis 终端记录 | [待记录] | [待测] | 液体粒子数需运行或读 entity 后确认 |
| G06 | Genesis | PBD 液体 | PBD Liquid | particle count unknown | 2e-3 / unknown | density 10；viscosity 1 | args.vis 默认 false | 可从 Genesis 终端记录 | [待记录] | [待测] | 粒子数依赖场景采样 |
| G07 | Genesis | SPH-刚体耦合 | SPH + Rigid coupling | particle count unknown；刚体数 unknown | 1e-2 / 10 | unknown | args.vis 默认 false | 可从 Genesis 终端记录 | [待记录] | [待测] | SPH 与刚体耦合路径明确 |
| G08 | Genesis | MPM 沙土与轮子 | MPM Sand + Rigid coupling | grid_density = 64；max_particles = 200000 | 3e-3 / 10 | unknown | args.vis 默认 false | 可从 Genesis 终端记录 | [待记录] | [待测] | 颗粒材料与刚体轮交互 |
| G09 | Genesis | MPM 多材料 | MPM Elastic/Liquid/ElastoPlastic | 3 个 MPM material object；particle count unknown | 4e-3 / 10 | unknown | true | 可从 Genesis 终端记录 | [待记录] | [待测] | 材料类别明确，采样粒子数待确认 |
| G10 | Genesis | PBD 布料下垂 | PBD Cloth | 2 个 cloth.obj；每个 6400 vertices / 12482 faces | 4e-3 / 10 | unknown | true | 可从 Genesis 终端记录 | [待记录] | [待测] | mesh 统计来自 Genesis cloth asset |
| G11 | Genesis | 布料-刚体接触 | PBD Cloth + Rigid coupling | 1 个 cloth.obj：6400 vertices / 12482 faces；particle_size = 1e-2 | 2e-3 / 10 | unknown | args.vis 默认 false | 可从 Genesis 终端记录 | [待记录] | [待测] | 布料资产分辨率已知 |
| G12 | Genesis | Franka 抓软立方体 | MPM soft cube + Rigid Franka | grid_density = 128；particle count unknown；Franka 9 DOF | 5e-3 / 15 | unknown | args.vis 默认 false | 可从 Genesis 终端记录 | [待记录] | [待测] | 软体粒子数依赖 MPM 采样 |
| G13 | Genesis | FEM 软体约束 | FEM implicit / explicit | vertex/tet count unknown | implicit: 1e-3 / 1；explicit: 1e-4 / 5 | unknown | args.vis 默认 false | 代码关闭终端 FPS | [待测] | [待测] | `show_FPS=False`，需最小 wrapper 或修改 profiling |
| G14 | Genesis | IPC 布料遥操作 | IPC Cloth + Rigid Franka | 2 个 grid20x20 cloth mesh；Franka 9 DOF；4x4 rigid blocks | 0.02 / unknown | line search iterations = 8 | true | 可从 Genesis 终端记录 | [待记录] | [待测] | cloth 具体顶点数需读下载资产 |
| N01 | Newton | 刚体金字塔碰撞 | XPBD rigid contact | 约 4200 boxes；DOF unknown | 0.001 / 10 | XPBD_ITERATIONS = 2 | true | 需最小 wrapper 或现有 benchmark 路径 | [待测] | [待测] | fps = 100，frame_dt = 0.01 |
| N02 | Newton | Franka 抓取/堆叠刚体 | MuJoCo rigid/SDF + IK state machine | brick_count = 3；Franka 9 DOF | 1/960 / 16 | iterations = 15；ls_iterations = 100 | true | 需最小 wrapper | [待测] | [待测] | fps = 60 |
| N03 | Newton | 基础关节约束 | XPBD/VBD articulated joints | 3 类 articulation visible；exact DOF unknown | 0.001 / 10 | VBD=2 if selected；XPBD unknown | true | 需最小 wrapper | [待测] | [待测] | revolute / prismatic / ball 示例明确 |
| N04 | Newton | UR10 关节控制 | MuJoCo robot simulation | UR10 DOF 来自资产，静态 unknown | 0.002 / 10 | unknown | true | 需最小 wrapper | [待测] | [待测] | fps = 50，contacts disabled |
| N05 | Newton | Franka IK | Analytic IK solver | Franka DOF 来自模型，静态 unknown | unknown / unknown | ik_iters = 24 | true | 需最小 wrapper | [待测] | [待测] | 该例主要测 IK，不是完整物理 step benchmark |
| N06 | Newton | MPM-刚体双向耦合 | MPM + MuJoCo rigid coupling | 6 个 moving boxes + ground；bed grid 约 121x121x31 | 0.0025 / 4 | MPM max_iterations = 50 | true | 需最小 wrapper | [待测] | [待测] | fps = 100，voxel_size = 0.05 |
| N07 | Newton | MPM 黏性流体 | MPM viscous material | voxel_size = 0.005；particle count depends on cone filter | 1/240 / 1 | max_iterations = 250 | true | 需最小 wrapper | [待测] | [待测] | fps 参数默认 240 |
| N08 | Newton | MPM 多材料 | MPM multi-material | 4 个 particle grids；静态估计约 178669 points before filtering | 1/60 / 1 | max_iterations = 250 | true | 需最小 wrapper | [待测] | [待测] | sand / snow / mud / kinematic block |
| N09a | Newton | XPBD 布料下垂 | XPBD Cloth | width=64 height=32；约 65x33=2145 vertices | 1/600 / 10 | iterations = 10 | true | 需最小 wrapper | [待测] | [待测] | 与 N09b 共用源码，不同 solver route |
| N09b | Newton | VBD 布料下垂 | VBD Cloth | width=64 height=32；约 65x33=2145 vertices | 1/600 / 10 | iterations = 10 | true | 需最小 wrapper | [待测] | [待测] | 与 N09a 共用源码，不同 solver route |
| N10 | Newton | Style3D 服装布料 | Style3D Cloth | garment mesh count unknown | 1/600 / 10 | iterations = 4 | true | 需最小 wrapper | [待测] | [待测] | Women_Sweatshirt USD 资产内部数量待读 |
| N11 | Newton | 布料-刚体接触 | VBD Cloth + collision pipeline | cloth_resolution=40；约 41x41=1681 vertices；table + sphere + ground | 1/720 / 12 | iterations = 10 | true | 需最小 wrapper | [待测] | [待测] | 自定义 cloth_on_rigid 脚本 |
| N12 | Newton | Franka 抓软体 | VBD Softbody + Featherstone Franka | tet mesh count unknown；robot DOF unknown | 1/600 / 10 | softbody iterations = 5；IK iters = 24 | true | 需最小 wrapper | [待测] | [待测] | rubber duck tet mesh 来自下载资产 |
| N13 | Newton | VBD 软体悬挂 | VBD Softbody | 4 个 soft grids；dim_x=12 dim_y=4 dim_z=4；exact vertices/tets unknown | 1/600 / 10 | iterations = 10 | true | 需最小 wrapper | [待测] | [待测] | 精确拓扑依赖 add_soft_grid 实现 |
| N14 | Newton | Franka T-shirt 操作 | VBD Cloth + Featherstone | garment mesh count unknown；robot DOF unknown | 1/600 / 10 | iterations = 5 | true | 需最小 wrapper | [待测] | [待测] | unisex_shirt.usd 资产内部数量待读 |

## 6. 能体现平台短板/优势的新增测试

| 测试编号 | 目标 | Genesis 预期 | Newton 预期 | 要验证的问题 | 结果占位 |
|---|---|---|---|---|---|
| S01 | 低黏度水体自由液面压力测试 | SPH/PBD 路线应更自然 | 可能需要 MPM 近似或缺少直接 SPH | Newton 是否能直接做 SPH/PBD 水；Genesis 水体效果与 FPS | [待补充] |
| S02 | 水-刚体强耦合，如水流推动叶轮 | Genesis 有 SPH/MPM/刚体耦合基础 | Newton 可做 MPM-刚体，但水感可能不同 | 谁更适合水流驱动刚体 | [待补充] |
| S03 | 多铰接刚体压力测试，50/100/200 个关节 | 验证统一建模和关节稳定性 | 验证 joint/constraint 系统工程能力 | 类似 Isaac Sim 多部件铰接场景谁更稳 | [待补充] |
| S04 | 布料强自碰撞与尖锐刚体接触 | 验证 IPC/PBD/FEM 接触稳定性 | 验证 VBD/Style3D 自碰撞和接触 | 哪个平台穿模少、调参少 | [待补充] |
| S05 | 机器人夹布料边缘并拖拽 | Genesis 能用 IPC teleop 验证 | Newton 更接近自动化 cloth manipulation | 机器人-布料任务谁更适合后续研究 | [待补充] |
| S06 | 高分辨率布料/软体扩展测试 | 观察 FPS 下降与稳定性 | 观察 VBD/XPBD/Style3D 扩展性 | 顶点数翻倍后谁更稳、更快 | [待补充] |
| S07 | 多求解器组合：机器人 + 刚体 + 布料 + 流体 | Genesis 统一 Scene 可能更方便 | Newton 组合更模块化但复杂 | 场景构建复杂度与可维护性 | [待补充] |

## 7. 平台 claim 验证表

| 平台 | 待验证 claim | 对应测试 | 评价方式 | 结果占位 |
|---|---|---|---|---|
| Genesis | 统一多物理接口降低 demo 构建成本 | 现有所有 demo + S07 | 代码行数、修改文件数、实现时间 | [待补充] |
| Genesis | SPH/PBD/MPM/FEM/IPC 等求解器覆盖较完整 | G05-G14 + S01/S02/S04 | 直接支持程度、效果、FPS | [待补充] |
| Genesis | IPC/接触在布料和机器人交互中有优势 | G14 + S04/S05 | 穿模率、接触稳定性、调参成本 | [待补充] |
| Newton | 模块化求解器适合复杂机器人和可变形体任务 | N12/N14 + S05/S07 | 任务完整度、控制器可扩展性 | [待补充] |
| Newton | VBD/XPBD/Style3D 布料路线丰富 | N10a/N10b/N10c + S04/S06 | 稳定性、视觉效果、FPS | [待补充] |
| Newton | 机器人 IK/动力学/接触管线更工程化 | N02/N04/N14 | 任务链完整度、代码复杂度、可控性 | [待补充] |

## 8. 现有 Demo 证据与初步观察

### 8.1 刚体堆叠与碰撞

Genesis 刚体塔：

[![Open video: genesis_rigid_stack_tower](thumbnails/Genesis/genesis_rigid_stack_tower.jpg)](video/Genesis/genesis_rigid_stack_tower.mp4)

Newton 刚体金字塔碰撞：

[![Open video: newton_rigid_collision_ball_pyramid](thumbnails/Newton/newton_rigid_collision_ball_pyramid.jpg)](video/Newton/newton_rigid_collision_ball_pyramid.mp4)

初步观察：两者都能跑通基础刚体接触。下一步需要用 S03 的多铰接刚体压力测试进一步拉开差异。

### 8.2 Franka 抓取刚体

Genesis Franka 抓取立方体：

[![Open video: genesis_robot_franka_pick_cube_rigid](thumbnails/Genesis/genesis_robot_franka_pick_cube_rigid.jpg)](video/Genesis/genesis_robot_franka_pick_cube_rigid.mp4)

Newton Franka 抓取/堆叠：

[![Open video: newton_robot_franka_pick_stack_cube](thumbnails/Newton/newton_robot_franka_pick_stack_cube.jpg)](video/Newton/newton_robot_franka_pick_stack_cube.mp4)

初步观察：Genesis 更快搭建抓取流程；Newton 任务链更完整。后续需要补机器人 DOF、控制器类型、平均 FPS、代码量和调参时间。

### 8.3 关节约束与机器人控制

Genesis 铰链门：

[![Open video: genesis_rigid_hinge_door_joint](thumbnails/Genesis/genesis_rigid_hinge_door_joint.jpg)](video/Genesis/genesis_rigid_hinge_door_joint.mp4)

Newton 关节约束：

[![Open video: newton_rigid_joint_constraints_hinge](thumbnails/Newton/newton_rigid_joint_constraints_hinge.jpg)](video/Newton/newton_rigid_joint_constraints_hinge.mp4)

Genesis 机器人控制：

[![Open video: genesis_robot_joint_control_demo](thumbnails/Genesis/genesis_robot_joint_control_demo.jpg)](video/Genesis/genesis_robot_joint_control_demo.mp4)

Newton UR10 与 Franka IK：

[![Open video: newton_robot_ur10_joint_control](thumbnails/Newton/newton_robot_ur10_joint_control.jpg)](video/Newton/newton_robot_ur10_joint_control.mp4)

[![Open video: newton_robot_franka_inverse_kinematics](thumbnails/Newton/newton_robot_franka_inverse_kinematics.jpg)](video/Newton/newton_robot_franka_inverse_kinematics.mp4)

初步观察：Newton 在关节类型和 IK/控制管线展示上更系统；Genesis 更适合快速上手。S03 应加入大量铰接部件来验证差异。

### 8.4 流体与颗粒

Genesis SPH 液体：

[![Open video: genesis_fluid_sph_liquid_free_surface](thumbnails/Genesis/genesis_fluid_sph_liquid_free_surface.jpg)](video/Genesis/genesis_fluid_sph_liquid_free_surface.mp4)

Genesis PBD 液体：

[![Open video: genesis_fluid_pbd_liquid_particles](thumbnails/Genesis/genesis_fluid_pbd_liquid_particles.jpg)](video/Genesis/genesis_fluid_pbd_liquid_particles.mp4)

Genesis SPH-刚体耦合与 MPM 沙土：

[![Open video: genesis_coupling_sph_liquid_rigid](thumbnails/Genesis/genesis_coupling_sph_liquid_rigid.jpg)](video/Genesis/genesis_coupling_sph_liquid_rigid.mp4)

[![Open video: genesis_mpm_sand_granular](thumbnails/Genesis/genesis_mpm_sand_granular.jpg)](video/Genesis/genesis_mpm_sand_granular.mp4)

Newton MPM-刚体耦合与 MPM 流体：

[![Open video: newton_coupling_mpm_rigid_twoway](thumbnails/Newton/newton_coupling_mpm_rigid_twoway.jpg)](video/Newton/newton_coupling_mpm_rigid_twoway.mp4)

[![Open video: newton_mpm_liquid_viscous_flow](thumbnails/Newton/newton_mpm_liquid_viscous_flow.jpg)](video/Newton/newton_mpm_liquid_viscous_flow.mp4)

初步观察：Genesis 在 SPH/PBD 低黏度流体上更直接；Newton 的 MPM 更适合连续介质/高黏度材料/颗粒。S01/S02 应专门验证 Newton 是否能直接复现水体类效果。

### 8.5 MPM 多材料

Genesis MPM：

[![Open video: genesis_mpm_elastic_liquid_plastic_demo](thumbnails/Genesis/genesis_mpm_elastic_liquid_plastic_demo.jpg)](video/Genesis/genesis_mpm_elastic_liquid_plastic_demo.mp4)

Newton MPM 多材料：

[![Open video: newton_mpm_multi_material_demo](thumbnails/Newton/newton_mpm_multi_material_demo.jpg)](video/Newton/newton_mpm_multi_material_demo.mp4)

初步观察：两者都能跑 MPM。下一步需要补材料参数、粒子数、FPS 和不同材料在同一框架下的可扩展性。

### 8.6 布料

Genesis PBD 布料：

[![Open video: genesis_cloth_pbd_hanging_fixed_edge](thumbnails/Genesis/genesis_cloth_pbd_hanging_fixed_edge.jpg)](video/Genesis/genesis_cloth_pbd_hanging_fixed_edge.mp4)

Newton XPBD / VBD / Style3D 布料：

[![Open video: newton_cloth_xpbd_hanging_fixed_edge](thumbnails/Newton/newton_cloth_xpbd_hanging_fixed_edge.jpg)](video/Newton/newton_cloth_xpbd_hanging_fixed_edge.mp4)

[![Open video: newton_cloth_vbd_hanging_fixed_edge](thumbnails/Newton/newton_cloth_vbd_hanging_fixed_edge.jpg)](video/Newton/newton_cloth_vbd_hanging_fixed_edge.mp4)

[![Open video: newton_cloth_style3d_garment_demo](thumbnails/Newton/newton_cloth_style3d_garment_demo.jpg)](video/Newton/newton_cloth_style3d_garment_demo.mp4)

Genesis / Newton 布料-刚体接触：

[![Open video: genesis_cloth_rigid_collision](thumbnails/Genesis/genesis_cloth_rigid_collision.jpg)](video/Genesis/genesis_cloth_rigid_collision.mp4)

[![Open video: newton_cloth_rigid_collision](thumbnails/Newton/newton_cloth_rigid_collision.jpg)](video/Newton/newton_cloth_rigid_collision.mp4)

初步观察：Newton 的布料求解器路线更丰富；Genesis 更快搭建基础布料。S04/S06 需要做高分辨率、自碰撞和强接触压力测试。

### 8.7 软体与机器人-可变形体操作

Genesis Franka 抓软立方体：

[![Open video: genesis_robot_franka_grasp_soft_cube_mpm](thumbnails/Genesis/genesis_robot_franka_grasp_soft_cube_mpm.jpg)](video/Genesis/genesis_robot_franka_grasp_soft_cube_mpm.mp4)

Newton Franka 抓软体：

[![Open video: newton_robot_franka_grasp_softbody_vbd](thumbnails/Newton/newton_robot_franka_grasp_softbody_vbd.jpg)](video/Newton/newton_robot_franka_grasp_softbody_vbd.mp4)

Genesis FEM 软体与 Newton VBD 软体：

[![Open video: genesis_softbody_fem_deformation](thumbnails/Genesis/genesis_softbody_fem_deformation.jpg)](video/Genesis/genesis_softbody_fem_deformation.mp4)

[![Open video: newton_softbody_vbd_hanging_damping](thumbnails/Newton/newton_softbody_vbd_hanging_damping.jpg)](video/Newton/newton_softbody_vbd_hanging_damping.mp4)

机器人布料操作：

[![Open video: genesis_robot_franka_ipc_cloth_teleop](thumbnails/Genesis/genesis_robot_franka_ipc_cloth_teleop.jpg)](video/Genesis/genesis_robot_franka_ipc_cloth_teleop.mp4)

[![Open video: newton_robot_franka_cloth_tshirt_manipulation](thumbnails/Newton/newton_robot_franka_cloth_tshirt_manipulation.jpg)](video/Newton/newton_robot_franka_cloth_tshirt_manipulation.mp4)

初步观察：机器人-布料/软体任务是 Newton 值得重点深入的方向；Genesis 的优势是统一接口和 IPC/多物理覆盖。后续重点补 S05/S07。

## 9. 当前阶段结论占位

| 结论问题 | 当前初步判断 | 需要补的数据 |
|---|---|---|
| 哪个平台更适合快速覆盖多物理 demo？ | Genesis 暂时更优 | 代码量、实现时间、场景构建步骤 |
| 哪个平台更适合流体？ | Genesis 在 SPH/PBD 液体更优；Newton MPM 材料更强 | S01/S02 FPS 与视觉对照 |
| 哪个平台更适合布料？ | Newton 求解器路线更丰富；Genesis 更快搭 | S04/S06 自碰撞、强接触、高分辨率测试 |
| 哪个平台更适合机器人可变形物操作？ | Newton 暂时更优 | S05 任务成功率、接触稳定性、FPS |
| 哪个平台更适合复杂铰接刚体？ | [待补充] | S03 多关节压力测试 |
| 是否建议双平台分工？ | 暂时建议 Genesis 做覆盖/流体，Newton 做机器人-布料/软体 | 完成量化表后更新 |

## 10. 下一步

下一步工作按 `NEXT_STEPS.md` 执行，优先级如下：

1. 为所有现有 demo 补齐场景规模和 FPS；
2. 新增 4 个高区分度压力测试：低黏度流体、多铰接刚体、布料强接触、机器人布料拖拽；
3. 把所有结果回填第 5、6、7、9 节；
4. 根据量化数据更新最终平台选型建议。
