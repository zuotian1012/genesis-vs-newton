# Genesis 与 Newton 多物理仿真实现对比报告

## 1. 工作目标与实验背景

本阶段工作的目标，是在同一硬件环境下分别使用 Genesis 和 Newton 复现一组经典多物理仿真 demo，覆盖刚体、机器人、软体、布料、流体以及跨物理耦合场景。两套实验均在 RTX 5090 平台上运行，因此报告重点关注平台本身的场景支持能力、求解器路线、实现效率、视觉与物理效果，以及后续工作应优先选择哪一个平台继续深入。

本报告不是单纯的视频展示说明，而是围绕以下问题进行评估：

- 两个平台是否都能跑通对应类型的 demo；
- 对刚体、软体、布料、流体等经典场景的支持是否完整；
- 实现时的代码组织、接口复杂度和调参成本如何；
- 在同样 GPU 配置下，画面效果、稳定性和交互复杂度表现如何；
- 对后续机器人操作、多物理耦合和复杂场景扩展，哪个平台更合适。

总体观察是：Genesis 更适合快速构建覆盖面广的多物理演示，接口统一，流体与多求解器组合更直观；Newton 更偏工程化和模块化，机器人控制、VBD/XPBD/Style3D 布料、复杂接触和可变形体操作能力更强，但实现门槛和调参复杂度更高。

---

## 2. 刚体堆叠与碰撞

Genesis 的刚体塔示例展示了多刚体堆叠、接触稳定性、摩擦和碰撞传播。场景搭建直接，适合作为刚体求解器稳定性的入门验证。

[![Open video: genesis_rigid_stack_tower](thumbnails/Genesis/genesis_rigid_stack_tower.jpg)](video/Genesis/genesis_rigid_stack_tower.mp4)

Newton 的刚体碰撞示例展示刚体金字塔与破坏球冲击，冲击能量更高，接触数量更多，更能体现复杂接触网络下的约束求解能力。

[![Open video: newton_rigid_collision_ball_pyramid](thumbnails/Newton/newton_rigid_collision_ball_pyramid.jpg)](video/Newton/newton_rigid_collision_ball_pyramid.mp4)

**对比：** 两个平台都能稳定运行基础刚体 demo。Genesis 的实现更轻量、复现更快；Newton 的场景更强调高冲击和多接触条件下的刚体求解表现。若只是快速搭建刚体验证，Genesis 效率更高；若后续需要细分约束、接触参数和更复杂刚体系统，Newton 的工程接口更有扩展空间。

---

## 3. Franka 抓取刚体

Genesis 使用 Franka Panda 抓取刚体立方体，展示机械臂 IK、夹爪闭合、物体接触和抓取后的提升过程。该 demo 的优点是流程清晰，接口统一，比较容易从示例扩展到其他刚体抓取任务。

[![Open video: genesis_robot_franka_pick_cube_rigid](thumbnails/Genesis/genesis_robot_franka_pick_cube_rigid.jpg)](video/Genesis/genesis_robot_franka_pick_cube_rigid.mp4)

Newton 的 Franka 抓取与堆叠任务更复杂，通常包含 GPU IK、有限状态机、SDF 网格碰撞，以及接近、抓取、抬升、移动、放置、释放的完整任务链。

[![Open video: newton_robot_franka_pick_stack_cube](thumbnails/Newton/newton_robot_franka_pick_stack_cube.jpg)](video/Newton/newton_robot_franka_pick_stack_cube.mp4)

**对比：** 两个平台都能实现机械臂刚体操作。Genesis 更适合快速实现和调试抓取流程；Newton 的任务更接近完整机器人操作 pipeline，效果更丰富，但代码结构、状态机和碰撞设置的理解成本明显更高。

---

## 4. 铰链与关节约束刚体

Genesis 的门铰链示例展示了典型转动关节对象，适合验证关节轴、关节限位、阻尼、驱动和刚体碰撞之间的协调。

[![Open video: genesis_rigid_hinge_door_joint](thumbnails/Genesis/genesis_rigid_hinge_door_joint.jpg)](video/Genesis/genesis_rigid_hinge_door_joint.mp4)

Newton 的基础关节示例覆盖 `REVOLUTE`、`PRISMATIC`、`BALL`、`DISTANCE` 等多种约束类型，更像是系统性关节/约束功能测试。

[![Open video: newton_rigid_joint_constraints_hinge](thumbnails/Newton/newton_rigid_joint_constraints_hinge.jpg)](video/Newton/newton_rigid_joint_constraints_hinge.mp4)

**对比：** Genesis 的示例更应用导向；Newton 的约束系统展示更完整。若后续需要构造复杂机构、连杆系统或多关节约束，Newton 的表达能力更强；若只需要快速加入常见关节物体，Genesis 更直接。

---

## 5. 机器人关节控制与逆运动学

Genesis 示例展示机器人关节控制与基础运动能力，适合快速理解机器人实体、关节自由度和控制接口。

[![Open video: genesis_robot_joint_control_demo](thumbnails/Genesis/genesis_robot_joint_control_demo.jpg)](video/Genesis/genesis_robot_joint_control_demo.mp4)

Newton 的 UR10 示例展示工业机械臂的关节运动和控制流程。

[![Open video: newton_robot_ur10_joint_control](thumbnails/Newton/newton_robot_ur10_joint_control.jpg)](video/Newton/newton_robot_ur10_joint_control.mp4)

Newton 的 Franka IK 示例进一步展示末端目标跟踪和逆运动学求解。

[![Open video: newton_robot_franka_inverse_kinematics](thumbnails/Newton/newton_robot_franka_inverse_kinematics.jpg)](video/Newton/newton_robot_franka_inverse_kinematics.mp4)

**对比：** Genesis 的机器人控制接口更统一，适合快速做 demo；Newton 的机器人控制链路更细，IK、动力学、关节目标和控制器之间拆分更明确，更适合后续做复杂任务规划、精细控制和机器人-环境耦合。

---

## 6. SPH 液体自由面

Genesis 提供 SPH 液体坍塌示例，能够直接展示自由液面流动、粒子水体扩散、边界碰撞以及低黏度流体效果。

[![Open video: genesis_fluid_sph_liquid_free_surface](thumbnails/Genesis/genesis_fluid_sph_liquid_free_surface.jpg)](video/Genesis/genesis_fluid_sph_liquid_free_surface.mp4)

Newton 当前实现路线更集中在 MPM/粒子连续介质和 XPBD/VBD 等求解器上，并不以 SPH 自由液面水体作为主要流体 demo 路线。因此，在低黏度水体、水坝坍塌、飞溅和 SPH 水-刚体耦合这类任务上，Genesis 的直接支持更强。

**对比：** 如果后续工作需要真实水感、自由液面或 SPH 风格流体，Genesis 是更自然的选择。Newton 可以做 MPM 流动材料，但它在该类 demo 中表现出的技术路线不是 SPH 水模拟。

---

## 7. PBD 液体

Genesis 提供 PBD 液体示例，用位置约束方式表现粒子流体的整体流动、碰撞和体积保持。

[![Open video: genesis_fluid_pbd_liquid_particles](thumbnails/Genesis/genesis_fluid_pbd_liquid_particles.jpg)](video/Genesis/genesis_fluid_pbd_liquid_particles.mp4)

Newton 虽然有 XPBD 求解器，但本轮实现中液体类效果主要通过 MPM 路线完成，而不是直接复现 Genesis 的 PBD 液体。对于希望快速比较 PBD/SPH/MPM 多种流体方法的工作，Genesis 的求解器谱系更完整。

**对比：** Genesis 在流体求解器覆盖面上更有优势；Newton 更适合把流动材料纳入 MPM 或多物理耦合框架，而不是作为 PBD 液体 demo 平台。

---

## 8. 流体、颗粒与刚体耦合

Genesis 的 SPH-刚体耦合展示粒子流体与刚体之间的双向作用，可观察流体冲击、刚体受力和反馈运动。

[![Open video: genesis_coupling_sph_liquid_rigid](thumbnails/Genesis/genesis_coupling_sph_liquid_rigid.jpg)](video/Genesis/genesis_coupling_sph_liquid_rigid.mp4)

Genesis 的 MPM 沙土示例展示颗粒材料的堆积、流散和塑性变形。

[![Open video: genesis_mpm_sand_granular](thumbnails/Genesis/genesis_mpm_sand_granular.jpg)](video/Genesis/genesis_mpm_sand_granular.mp4)

Newton 的 MPM-刚体耦合示例展示 MPM 材料与刚体的双向交互，重点在于 MPM 粒子对刚体施力，以及刚体运动对材料形态的反馈。

[![Open video: newton_coupling_mpm_rigid_twoway](thumbnails/Newton/newton_coupling_mpm_rigid_twoway.jpg)](video/Newton/newton_coupling_mpm_rigid_twoway.mp4)

Newton 的 MPM 流体视频展示高黏度或连续介质材料的流动效果。

[![Open video: newton_mpm_liquid_viscous_flow](thumbnails/Newton/newton_mpm_liquid_viscous_flow.jpg)](video/Newton/newton_mpm_liquid_viscous_flow.mp4)

**对比：** Genesis 同时覆盖 SPH 与 MPM，流体/颗粒/刚体耦合路径更完整；Newton 的 MPM 耦合工程化程度更高，更适合连续介质、颗粒材料和刚体相互作用。若后续目标是“水”和“低黏度液体”，Genesis 更合适；若目标是沙、泥、软材料或 MPM-刚体作用，Newton 值得继续深入。

---

## 9. MPM 多材料模拟

Genesis 的 MPM 示例展示基础连续介质、液体和弹塑性材料行为，适合快速验证 MPM 求解器是否可用。

[![Open video: genesis_mpm_elastic_liquid_plastic_demo](thumbnails/Genesis/genesis_mpm_elastic_liquid_plastic_demo.jpg)](video/Genesis/genesis_mpm_elastic_liquid_plastic_demo.mp4)

Newton 的 MPM 多材料示例更强调不同材料模型在统一框架下的组合与对比，例如颗粒、黏塑性材料、高黏度材料或不同本构参数下的形变差异。

[![Open video: newton_mpm_multi_material_demo](thumbnails/Newton/newton_mpm_multi_material_demo.jpg)](video/Newton/newton_mpm_multi_material_demo.mp4)

**对比：** 两个平台都能跑通 MPM demo。Genesis 更适合快速入门和可视化演示；Newton 的 MPM 路线更偏材料库和工程参数实验，后续若需要系统比较材料模型，Newton 的扩展空间更好。

---

## 10. 固定一侧的下垂布料

Genesis 的 PBD 布料示例展示布料在固定边界下的下垂、振荡和稳定过程。

[![Open video: genesis_cloth_pbd_hanging_fixed_edge](thumbnails/Genesis/genesis_cloth_pbd_hanging_fixed_edge.jpg)](video/Genesis/genesis_cloth_pbd_hanging_fixed_edge.mp4)

Newton 提供多条布料求解路线。XPBD 布料强调约束稳定性和实时性。

[![Open video: newton_cloth_xpbd_hanging_fixed_edge](thumbnails/Newton/newton_cloth_xpbd_hanging_fixed_edge.jpg)](video/Newton/newton_cloth_xpbd_hanging_fixed_edge.mp4)

VBD 布料强调可变形体求解下的稳定接触和变形表现。

[![Open video: newton_cloth_vbd_hanging_fixed_edge](thumbnails/Newton/newton_cloth_vbd_hanging_fixed_edge.jpg)](video/Newton/newton_cloth_vbd_hanging_fixed_edge.mp4)

Style3D 布料更偏高质量服装/布料仿真工作流。

[![Open video: newton_cloth_style3d_garment_demo](thumbnails/Newton/newton_cloth_style3d_garment_demo.jpg)](video/Newton/newton_cloth_style3d_garment_demo.mp4)

**对比：** 布料是 Newton 表现较强的方向。Genesis 的 PBD 布料实现简单、复现快；Newton 可以在 XPBD、VBD 和 Style3D 之间比较求解器效果，适合研究布料精度、稳定性和服装级仿真。不过 Newton 的配置项更多，前期调参和理解成本更高。

---

## 11. 布料与刚体碰撞

Genesis 展示布料落在刚体上的接触与包覆行为，重点是布料网格与刚体表面之间的碰撞稳定性。

[![Open video: genesis_cloth_rigid_collision](thumbnails/Genesis/genesis_cloth_rigid_collision.jpg)](video/Genesis/genesis_cloth_rigid_collision.mp4)

Newton 对应视频展示布料落到刚体平台上的过程，可观察折弯、接触、滑动和碰撞响应。

[![Open video: newton_cloth_rigid_collision](thumbnails/Newton/newton_cloth_rigid_collision.jpg)](video/Newton/newton_cloth_rigid_collision.mp4)

**对比：** 两个平台都能实现布料-刚体碰撞。Genesis 的场景写法更直接；Newton 的优势在于可以进一步切换求解器、控制接触边界和自碰撞设置，适合对布料接触做更深入调试。

---

## 12. 机械臂抓取软体

Genesis 使用 Franka 抓取软立方体，展示机械臂、夹爪与软体物体之间的耦合接触。

[![Open video: genesis_robot_franka_grasp_soft_cube_mpm](thumbnails/Genesis/genesis_robot_franka_grasp_soft_cube_mpm.jpg)](video/Genesis/genesis_robot_franka_grasp_soft_cube_mpm.mp4)

Newton 使用 Franka 抓取软体物体，通常依赖 VBD 四面体软体、机器人积分和 IK 控制共同完成任务。

[![Open video: newton_robot_franka_grasp_softbody_vbd](thumbnails/Newton/newton_robot_franka_grasp_softbody_vbd.jpg)](video/Newton/newton_robot_franka_grasp_softbody_vbd.mp4)

**对比：** 两个平台都能完成机器人-软体交互。Genesis 更适合作为软体抓取快速原型；Newton 在软体网格、机器人控制、接触管线和可变形体求解方面更细，适合后续扩展为复杂可变形物操作任务。

---

## 13. 软体悬挂与 FEM/VBD 表现

Genesis 的 FEM 示例展示软体在约束、重力和弹性材料作用下的变形行为，可用于观察软体有限元求解、边界固定和材料参数对变形的影响。

[![Open video: genesis_softbody_fem_deformation](thumbnails/Genesis/genesis_softbody_fem_deformation.jpg)](video/Genesis/genesis_softbody_fem_deformation.mp4)

Newton 的 VBD 软体示例展示四面体软体在固定边界和不同阻尼设置下的下垂、振荡与稳定过程。

[![Open video: newton_softbody_vbd_hanging_damping](thumbnails/Newton/newton_softbody_vbd_hanging_damping.jpg)](video/Newton/newton_softbody_vbd_hanging_damping.mp4)

**对比：** Genesis 更接近传统 FEM 软体演示，便于教学和快速观察材料变形；Newton 的 VBD 更强调稳定、可组合以及与机器人/接触系统集成。若后续重点是软体材料本身，Genesis 更直观；若重点是软体与机器人、刚体、布料的复杂交互，Newton 更适合继续投入。

---

## 14. 机器人布料操作与叠衣服

Genesis 提供 IPC 布料遥操作示例，通过键盘控制 Franka 移动、抓取布料并完成交互。该示例体现 Genesis 在机器人、IPC 接触和布料耦合上的可运行性，但任务本身更偏人工遥操作流程。

[![Open video: genesis_robot_franka_ipc_cloth_teleop](thumbnails/Genesis/genesis_robot_franka_ipc_cloth_teleop.jpg)](video/Genesis/genesis_robot_franka_ipc_cloth_teleop.mp4)

Newton 的 Franka-布料示例使用 VBD 求解布料、Featherstone 求解机器人，并显式处理机器人-布料接触、自碰撞、厘米尺度仿真与可视化尺度转换。该类实现更接近自动化机器人布料操作或叠衣服任务所需的工程结构。

[![Open video: newton_robot_franka_cloth_tshirt_manipulation](thumbnails/Newton/newton_robot_franka_cloth_tshirt_manipulation.jpg)](video/Newton/newton_robot_franka_cloth_tshirt_manipulation.mp4)

**对比：** 这是 Newton 相对 Genesis 更有优势的场景之一。Genesis 能跑通机器人与布料交互，接口更统一；Newton 的实现更复杂，但对 T-shirt 这类真实服装网格、机器人控制、布料自碰撞和复杂接触的支持更系统。若后续工作要继续做机器人叠衣服、衣物整理或可变形物操作，Newton 更值得优先考虑。

---

## 15. 场景规模与运行效率统计

在完成视频复现后，本项目进一步为每个 demo 补充了场景复杂度和运行效率统计，结果保存在 `metrics/scene_metrics.csv`。测量口径为 headless simulation loop：关闭 viewer，排除视频录制、截图、渲染、build 和首次编译开销，在短暂 warmup 后只统计 `step()` 循环耗时。因此，这里的 FPS 更适合作为“仿真循环吞吐量”参考，而不是最终带渲染视频输出的播放帧率。

整体上，Genesis 14 个场景均已获得有效测量，Newton 15 个场景也均已获得有效测量。两者平均 FPS 接近，但这个均值不应被过度解读，因为不同 demo 的粒子数、网格规模、时间步长和任务复杂度差异很大。更有意义的是按场景类型观察：Genesis 在 PBD 液体、基础刚体和简单机器人任务上吞吐量很高；Newton 在关节约束、IK、XPBD/VBD 布料和机器人-可变形体操作上表现更稳定；高粒子数 SPH/MPM、FEM、机器人抓软体等场景则明显更消耗算力。

| 场景类型 | Genesis 规模与 FPS | Newton 规模与 FPS | 观察 |
|---|---:|---:|---|
| 刚体堆叠/碰撞 | 102 刚体，428.28 FPS | 4201 刚体，366.39 FPS | Newton 场景规模远大于 Genesis，仍保持较高吞吐；Genesis 更适合快速搭建中等规模刚体 demo。 |
| Franka 刚体抓取 | 13 刚体，9 robot DoF，392.34 FPS | 17 刚体，9 robot DoF，63.26 FPS | Genesis 的简单抓取循环更轻量；Newton 的堆叠任务更完整，控制和接触流程更重。 |
| 刚体关节/约束 | 3 刚体，1 generalized DoF，135.55 FPS | 6 刚体，5 generalized DoF，911.91 FPS | Newton 的基础关节 demo 很轻且吞吐高，适合系统性约束测试。 |
| 机器人关节控制/IK | 12 刚体，9 robot DoF，281.64 FPS | UR10: 800 刚体/600 DoF，354.85 FPS；Franka IK: 412.62 FPS | Newton 在批量机器人/IK 示例上吞吐表现突出，但场景定义和控制链路更工程化。 |
| SPH/PBD 液体 | SPH 64k 粒子，46.82 FPS；PBD 16k 粒子，1134.29 FPS | 本组 Newton 无直接 SPH/PBD 液体对应项 | Genesis 在流体求解器覆盖面上更完整，PBD 液体吞吐很高。 |
| 流体/颗粒-刚体耦合 | SPH 216k 粒子 + 2 刚体，37.86 FPS；MPM 沙 200k 粒子 + 5 刚体，38.12 FPS | MPM 453,871 粒子 + 6 刚体，97.89 FPS | Newton 的 MPM-刚体耦合在更大粒子规模下仍有较好吞吐；Genesis 的 SPH 路线提供了 Newton 当前 demo 中没有的水体耦合形式。 |
| MPM 多材料 | 39,184 粒子，48.35 FPS | 178,669 粒子，41.40 FPS | 两者都能跑通 MPM 多材料；Newton 粒子规模更大，Genesis 更易快速复现。 |
| 悬挂布料 | PBD 22,414 粒子，38.46 FPS | XPBD 2145 粒子，236.74 FPS；VBD 2145 粒子，73.28 FPS；Style3D 24,510 粒子，22.10 FPS | Newton 布料路线更多，可比较 XPBD/VBD/Style3D；FPS 需结合网格规模和求解器精度理解。 |
| 布料-刚体碰撞 | 2896 粒子，36.59 FPS | 1681 粒子，6.71 FPS | Newton 的 VBD 接触场景更重，吞吐低但接触细节和稳定性调参空间更大。 |
| 机器人抓软体 | MPM 512 粒子 + Franka，17.70 FPS | VBD 2734 粒子 + Franka，71.45 FPS | Newton 在机器人-软体操作上吞吐和工程组织更有优势；Genesis 更适合快速原型。 |
| 软体变形 | FEM 982 顶点，13.69 FPS | VBD 1300 顶点，51.36 FPS | Newton VBD 在该组软体 demo 中更快；Genesis FEM 更接近传统有限元演示。 |
| 机器人布料操作 | IPC cloth 800 顶点 + Franka，21.87 FPS | VBD T-shirt 6436 粒子 + Franka，65.11 FPS | Newton 的 T-shirt 场景规模更大且 FPS 更高，更适合后续机器人衣物操作深入。 |

从这些数据可以看出，性能结论不能简单写成“Genesis 更快”或“Newton 更快”。Genesis 的优势在于统一接口下快速覆盖多类物理现象，尤其是 SPH/PBD/MPM 等流体与粒子场景入口清晰；Newton 的优势在于复杂机器人、布料、软体和接触系统的工程化能力，在多个可变形体相关任务中即使场景更复杂也能保持可用 FPS。

---

# 平台能力总结与后续选择建议

## 1. 场景覆盖

Genesis 覆盖面更均衡：刚体、机器人、SPH 液体、PBD 液体、MPM、FEM、布料和多物理耦合都有较直接的示例入口。对于“先确认平台能不能跑经典 demo”这一阶段，Genesis 的效率很高。

Newton 覆盖方向更集中：刚体、机器人、IK、XPBD/VBD/Style3D 布料、VBD 软体、Implicit MPM、多求解器耦合和机器人可变形体操作。它不是流体求解器覆盖最完整的平台，但在机器人和可变形体交互方面更强。

## 2. 实现效率

Genesis 的优势是统一 `Scene`、实体添加和 `scene.step()` 风格，快速复现实验更省时间。大多数 demo 的代码逻辑更直观，适合教学展示和快速搭建 baseline。

Newton 的实现通常需要显式管理 `ModelBuilder`、solver、state、control、collision pipeline、visualization state 等模块。初期实现效率较低，但一旦理解框架，复杂任务的可控性和可扩展性更好。

## 3. 实现效果

在刚体、基础机器人、布料下垂、软体变形等常规 demo 上，两者都能跑通。Genesis 的效果优势在于流体和多求解器组合展示更直观；Newton 的效果优势在于布料/软体接触更细、机器人操作任务更完整，尤其是 Franka 与 T-shirt 布料交互这类复杂场景。

## 4. 求解器路线

Genesis 当前对本组 demo 的覆盖包括刚体、SPH、PBD、MPM、FEM、IPC/布料耦合等，适合比较不同物理求解器在同一平台中的表现。

Newton 当前对本组 demo 的覆盖主要包括 XPBD、VBD、Style3D、Implicit MPM、Featherstone/MuJoCo 机器人动力学和多求解器耦合。它的优势不是“所有物理类型都有最直接入口”，而是把机器人、布料、软体和复杂接触组织成更工程化的系统。

## 5. 在 RTX 5090 上的工作感受

在 5090 上，两个平台的这些 demo 都具备运行条件，且 headless 仿真循环大多可以达到可交互或接近可交互的速度。统计结果显示，轻量刚体、关节和基础机器人场景通常不是瓶颈；真正拉低吞吐的是高粒子数流体/MPM、FEM、布料接触和机器人-可变形体耦合。Genesis 的低门槛让它更快形成可视化结果，Newton 的模块化结构让复杂任务更可控，但需要更多调参、尺度处理和状态管理。

## 6. 建议

如果后续目标是快速扩展经典多物理 demo、覆盖更多流体/软体/刚体组合，或做课程展示型对比，建议优先选择 Genesis。当前数据支持这一点：Genesis 已覆盖 SPH、PBD、MPM、FEM、IPC 布料和机器人耦合等多类入口，其中 PBD 液体、刚体塔和基础机器人 demo 的仿真 FPS 都较高，适合快速迭代。

如果后续目标是机器人叠衣服、机器人操作可变形物、复杂布料接触、服装级仿真或需要精细控制器与求解器组合，建议优先选择 Newton。当前数据也支持这一点：Newton 在 Franka-T-shirt、Franka-软体、VBD 软体、XPBD/VBD/Style3D 布料和 MPM-刚体耦合等场景上提供了更工程化的路线，并在若干复杂场景中保持了更好的吞吐。

综合当前实验和统计结果，可以采用“双平台分工”的策略：Genesis 作为多物理现象覆盖和快速原型平台，Newton 作为机器人-布料/软体复杂操作的重点深入平台。这样既能保留 Genesis 在流体、统一接口和快速搭建上的优势，也能利用 Newton 在复杂机器人可变形体任务上的工程能力。
