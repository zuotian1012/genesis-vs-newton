# Genesis 与 Newton 多物理仿真 Demo 对比

本仓库用于对比 **Genesis** 和 **Newton** 两个仿真平台在经典多物理 demo 上的实现效果。当前工作是在同一硬件环境下，分别用两个平台复现并录制刚体、机器人、软体、布料、流体和多物理耦合场景，从而判断后续工作更适合基于哪个平台继续展开。

本轮 demo 均在 **RTX 5090** 机器上运行。

## 项目目标

本项目关注的不只是“视频能不能跑出来”，而是围绕以下几个问题进行平台评估：

- 两个平台是否都能跑通代表性的经典 demo；
- 刚体、软体、布料、流体等场景是否有直接支持；
- 不同平台的求解器路线和适用场景有什么差异；
- 实现过程中的代码结构、接口复杂度和调参成本如何；
- 在同样 GPU 配置下，仿真效果、稳定性和交互复杂度表现如何；
- 后续如果继续做机器人操作、可变形物体、布料、流体和多物理耦合，哪个平台更合适。

## 完整报告

完整对比报告见：

[打开完整报告](report.md)

说明：GitHub 的 Markdown 页面通常不会直接内嵌播放仓库中的本地 `.mp4` 文件。因此，报告中使用“缩略图 + 视频链接”的形式展示 demo。点击报告中的任意缩略图，即可打开对应的视频文件。

## 仓库结构

```text
.
├── README.md              # 项目说明
├── report.md              # 主报告，包含可点击的视频缩略图
├── video/
│   ├── Genesis/           # Genesis demo 录屏
│   └── Newton/            # Newton demo 录屏
├── thumbnails/
│   ├── Genesis/           # Genesis 视频缩略图
│   └── Newton/            # Newton 视频缩略图
├── genesis-world/         # Genesis 源码 / 示例参考
└── newton/                # Newton 源码 / 示例参考
```

## 当前覆盖的 Demo 类型

当前报告覆盖以下场景：

- 刚体堆叠与碰撞；
- Franka 抓取刚体；
- 铰链与关节约束；
- 机器人关节控制与逆运动学；
- SPH 自由液面流体；
- PBD 粒子液体；
- SPH / MPM / 刚体耦合；
- MPM 多材料仿真；
- 固定边界布料下垂；
- 布料与刚体碰撞；
- Franka 抓取软体；
- FEM / VBD 软体变形；
- 机器人布料操作与 T-shirt 类衣物操作。

## 视频命名规范

视频文件名采用较长但自解释的命名方式，方便只看文件名就判断其平台、物理类别、任务对象和主要求解器路线。

命名格式：

```text
<platform>_<category>_<task/object>_<solver-or-material>_<detail>.mp4
```

示例：

```text
video/Genesis/genesis_fluid_sph_liquid_free_surface.mp4
video/Genesis/genesis_robot_franka_grasp_soft_cube_mpm.mp4
video/Newton/newton_robot_franka_cloth_tshirt_manipulation.mp4
video/Newton/newton_cloth_xpbd_hanging_fixed_edge.mp4
```

每个视频在 `thumbnails/` 下都有一个同名 `.jpg` 缩略图，用于在 GitHub 报告页面中显示预览。

## 当前结论

从本轮实验看，**Genesis** 更适合作为快速、多类型、多物理 demo 的原型平台。它的接口统一，场景搭建速度快，对 SPH 液体、PBD 液体、MPM、FEM、布料、刚体以及多种耦合场景都有比较直接的示例入口。

**Newton** 更适合偏工程化的机器人与可变形物体操作任务。它在机器人控制、IK、VBD / XPBD / Style3D 布料、MPM 材料实验、复杂接触、机器人-布料耦合和机器人-软体耦合方面更有优势，但整体实现和调参成本也更高。

因此，当前更合理的策略是“双平台分工”：

- 使用 Genesis 做多物理覆盖、快速 baseline 和流体相关 demo；
- 使用 Newton 深入机器人-布料、机器人-软体、服装操作和复杂求解器组合任务。

## 备注

- demo 视频已直接提交到仓库，方便在 GitHub 上查看；
- 缩略图由对应视频自动截帧生成，用于改善 GitHub Markdown 的浏览体验；
- `.DS_Store` 是 macOS 本地系统文件，不属于项目内容。
