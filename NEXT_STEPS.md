# 后续工作步骤书

这份步骤书用于把当前“现象展示型”项目推进成“可量化的平台选型评估”。当前优先级不是搭完整 benchmark 系统，而是先用最小成本拿到第一批可信数据：手工运行 demo 记录终端 FPS，静态读代码补场景规模，只在确实没有 FPS 输出时再写最小 wrapper。

## Step 1：冻结实验环境

目的：保证之后的 FPS 和稳定性数据可复现。

具体做法：

1. 记录硬件信息：
   - GPU：RTX 5090；
   - CPU：运行 `sysctl -n machdep.cpu.brand_string`；
   - 内存：运行 `sysctl hw.memsize`；
   - 系统版本：运行 `sw_vers`；
   - NVIDIA driver / CUDA：记录当前驱动、CUDA、Warp、Python 版本。

2. 记录代码版本：
   - 在仓库根目录运行 `git rev-parse HEAD`；
   - 在 `genesis-world/` 运行 `git rev-parse HEAD`；
   - 在 `newton/` 运行 `git rev-parse HEAD`。

3. 把这些信息填入 `report.md` 的“统一实验环境”表格。

## Step 2：第一阶段 A：静态统计已完成

目的：先形成一张“每个 demo 的规模 + 参数 + FPS 状态”基础表，避免一开始就陷入完整 benchmark harness。

已经建立第一版静态表：

```text
results/static_demo_stats.csv
```

这张表记录：

- demo ID、平台、视频路径、源码路径；
- 主要求解器路线；
- `dt`、`substeps`、solver iterations；
- cloth grid size / vertex count；
- particle size / particle count；
- robot DOF；
- viewer 是否开启；
- Genesis 是否能直接从终端日志记录 FPS；
- 静态备注。

后续维护规则：

1. 能从源码直接确认的字段就填具体值；
2. 不能确认的字段填 `unknown`，不要猜；
3. 资产内部的 mesh/tet/particle 数量，只有在脚本或资产文件能直接读到时才填；
4. 每次新增 demo，先补 `demo_mapping.md`，再补 `results/static_demo_stats.csv`。

## Step 3：第一阶段 B：手工运行 Genesis demo 并记录终端 FPS

目的：利用 Genesis 运行时终端会打印 FPS 这一点，先快速获得第一批效率数据。

具体做法：

1. 按 `demo_mapping.md` 中的 Genesis 条目逐个运行；
2. 每个 demo 至少跑到画面和 FPS 稳定后再记录；
3. 记录终端中稳定区间的 FPS，而不是刚启动的瞬时值；
4. 如果 demo 有 `--vis` 或类似 viewer 参数，分别记录当前实际运行模式；
5. 如果某个 Genesis demo 明确关闭了 FPS 输出，例如代码里设置了 `show_FPS=False`，在表中保留 `terminal_fps_available=false`。

已经建立运行 FPS 记录表：

```text
results/runtime_fps_log.csv
```

字段：

```text
id,platform,source_file,run_command,warmup_seconds,observed_fps_min,observed_fps_max,observed_fps_avg,viewer_on,recording_on,notes
```

优先手工运行以下 5 个 Genesis demo：

| ID | 选择原因 | 运行命令 | 注意事项 |
|---|---|---|---|
| G01 | 非交互刚体堆叠，适合先验证终端 FPS 记录流程 | `cd genesis-world && python examples/collision/tower.py` | `--vis` 默认 false；无需录屏 |
| G05 | SPH 自由液面，是 Genesis 流体优势代表 | `cd genesis-world && python examples/tutorials/sph_liquid.py` | 代码中 `show_viewer=True`，记录为 viewer-on FPS |
| G06 | PBD 液体，是 Genesis PBD 流体代表 | `cd genesis-world && python examples/pbd_liquid.py` | `--vis` 默认 false；粒子数仍需后续确认 |
| G10 | PBD 布料下垂，是布料 baseline | `cd genesis-world && python examples/tutorials/pbd_cloth.py` | 代码中 `show_viewer=True`；使用本地 cloth mesh |
| G11 | 布料-刚体接触，适合观察接触稳定性 | `cd genesis-world && python examples/coupling/cloth_on_rigid.py` | `--vis` 默认 false；无需外部下载 |

记录方式：

1. 运行命令后等待 `warmup_seconds`，建议先用 10 秒；
2. 观察终端中稳定后的 FPS 输出；
3. 记录稳定区间的最低值、最高值和目测平均值；
4. 不录屏，`recording_on=false`；
5. 如果代码默认开 viewer，则 `viewer_on=true`，不要把它和 simulation-only FPS 混用；
6. 如果 demo 报错、下载资源、打开交互窗口或无法稳定输出 FPS，在 `notes` 中说明，不要强行修改代码。

注意：录屏视频只用于展示效果，不用于最终性能结论。

## Step 4：静态读代码补场景规模

目的：解释“为什么某个 demo 快/慢”，不能只给 FPS。

按 `results/static_demo_stats.csv` 继续补充这些信息：

- 刚体数；
- 关节数；
- 机器人 DOF；
- 粒子数；
- 布料顶点数和面片数；
- 软体 tet 数；
- timestep；
- substeps；
- solver iterations；
- viewer 是否开启；
- 主要求解器路线。

Genesis 静态检查重点：

1. `gs.Scene(sim_options=...)` 中的 `dt`、`substeps`；
2. `RigidOptions`、`PBDOptions`、`SPHOptions`、`MPMOptions`、`FEMOptions`、`ProfilingOptions`；
3. `add_entity` 的 mesh、primitive、material；
4. 机器人控制 DOF 列表；
5. mesh 文件能直接读取时，再统计 vertices/faces/tets。

Newton 静态检查重点：

1. `fps`、`frame_dt`、`sim_substeps`、`sim_dt`；
2. `SolverXPBD`、`SolverVBD`、`SolverMuJoCo`、`SolverImplicitMPM`、`Style3D` 等求解器；
3. `iterations`、`max_iterations`、`ls_iterations`；
4. `add_cloth_grid`、`add_soft_grid`、`add_particle_grid` 的分辨率；
5. builder 或 asset 中没有直接写出的数量保持 `unknown`。

## Step 5：第二阶段：只给 Newton 关键 demo 或缺 FPS demo 写最小 wrapper

目的：补齐没有终端 FPS 的平台或 demo，不做大而全 benchmark 系统。

触发条件：

- Newton 关键 demo 没有稳定终端 FPS；
- Genesis demo 关闭了 FPS 输出，例如 G13；
- 需要明确区分 simulation-only 和 viewer-on；
- 手工终端 FPS 与实际体验明显不一致，需要复核。

最小 wrapper 只保留：

- 原 demo 的 scene/model build；
- warmup loop；
- timed step loop；
- 打印一行 JSON；
- 不录屏；
- 默认不开 viewer，除非专门测 viewer-on。

建议输出字段：

```json
{
  "id": "N09",
  "platform": "Newton",
  "mode": "simulation-only",
  "warmup_steps": 100,
  "benchmark_steps": 1000,
  "elapsed_sec": 4.32,
  "sim_fps": 231.5,
  "stable": true
}
```

建议结果文件：

```text
results/newton_runtime_fps.csv
```

已经建立最小 Newton benchmark wrapper：

```text
scripts/benchmark_newton_minimal.py
```

当前支持的 demo：

| ID | 场景 | 运行目标 |
|---|---|---|
| N01 | Newton rigid pyramid collision | XPBD rigid contact simulation-only FPS |
| N09a | Newton cloth hanging XPBD | XPBD cloth simulation-only FPS |
| N09b | Newton cloth hanging VBD | VBD cloth simulation-only FPS，可作为下一条补充运行 |

推荐在 GPU-enabled Newton 环境中运行：

```bash
conda run -n newton python scripts/benchmark_newton_minimal.py --demo N01 --demo N09a
```

如果要同时测 VBD cloth：

```bash
conda run -n newton python scripts/benchmark_newton_minimal.py --demo N09b
```

默认参数：

```text
warmup_steps = 50
benchmark_steps = 200
viewer_on = false
recording_on = false
```

注意：当前本机 `newton` conda 环境中的 Warp 显示 `CUDA not enabled in this build`，因此脚本已经在 `results/newton_runtime_fps.csv` 中写入 blocked 记录，而不是记录 CPU FPS。这样可以避免把 CPU 结果误当成 RTX 5090 结果。换到 CUDA-enabled Newton 环境后，重新运行上述命令即可得到真实 `sim_fps`。

如确实想做 CPU smoke test，可显式加：

```bash
conda run -n newton python scripts/benchmark_newton_minimal.py --demo N01 --warmup-steps 1 --benchmark-steps 2 --allow-cpu
```

CPU smoke test 只用于验证 wrapper 逻辑，不进入最终性能结论。

这一阶段不要新建完整 benchmark 框架、批量 runner 或复杂 harness。先把 Newton 关键 demo 的第一版证据补齐。

## Step 6：新增高区分度压力测试

目的：让报告不仅说明“两边都还行”，还能说明“哪里不适合、哪里有明显优势”。

优先做以下 4 个测试：

### S01：低黏度水体自由液面

目标：验证 Genesis SPH/PBD 液体优势，以及 Newton 是否只能用 MPM 近似。

具体做法：

1. Genesis：基于现有 SPH/PBD liquid demo，加大粒子数，做水坝坍塌或容器倒水；
2. Newton：尝试用现有 MPM liquid/viscous demo 复现相同几何和初始条件；
3. 对比是否直接支持、粒子数、FPS、水面视觉效果、数值稳定性、实现代码量。

回填位置：`report.md` 第 6 节 S01、第 9 节“流体”结论。

### S02：多铰接刚体压力测试

目标：验证复杂 articulated rigid body 支持能力，类似很多门、抽屉、铰链、连杆的场景。

具体做法：

1. 设计同一类结构：50 / 100 / 200 个 hinge，可选加入 prismatic joint；
2. Genesis 和 Newton 各实现一版；
3. 记录 joint 数、body 数、FPS、是否抖动、是否关节爆炸、代码复杂度。

回填位置：`report.md` 第 6 节 S03、第 9 节“复杂铰接刚体”结论。

### S03：布料强接触与自碰撞

目标：验证 Genesis IPC/PBD/FEM 与 Newton VBD/XPBD/Style3D 在复杂接触中的差异。

具体做法：

1. 设计布料落到尖锐/复杂刚体上的场景；
2. 设计布料折叠后自碰撞场景；
3. 改变布料分辨率：low / medium / high；
4. 记录 vertices、faces、solver iterations、FPS、穿模次数、是否抖动或爆炸、调参时间。

回填位置：`report.md` 第 6 节 S04/S06、第 7 节平台 claim 验证。

### S04：机器人夹布料边缘并拖拽

目标：验证机器人-布料交互是否适合后续衣物整理/叠衣服方向。

具体做法：

1. Genesis：基于 IPC cloth teleop 或 Franka cloth demo，做夹住布料边缘后拖拽；
2. Newton：基于 `cloth_franka` / T-shirt manipulation demo，做相同目标；
3. 对比是否容易指定抓取点、是否容易做自动轨迹、是否穿模、是否容易调接触参数、FPS、任务成功率。

回填位置：`report.md` 第 6 节 S05、第 9 节“机器人可变形物操作”结论。

## Step 7：记录实现成本

目的：平台选型不仅看 FPS，也看开发效率。

每个 demo 记录：

- 新增/修改文件数；
- demo script 代码行数；
- 从开始改到跑通所需时间；
- 调参次数；
- 是否需要改平台源码；
- 是否需要额外资产转换；
- 是否需要特殊尺度处理，例如 Newton cloth cm-scale。

可以用粗粒度分级：

```text
low    = 30 分钟内跑通，主要改示例参数
medium = 半天内跑通，需要理解 API 或调参
high   = 1 天以上，需要改代码结构或处理复杂接触/资产
```

## Step 8：生成新视频和缩略图

目的：新增压力测试后保持 GitHub 报告可浏览。

具体做法：

1. 视频放到：

```text
video/Genesis/
video/Newton/
```

2. 命名遵循现有规则：

```text
<platform>_<category>_<task/object>_<solver-or-material>_<detail>.mp4
```

3. 生成缩略图：

```bash
mkdir -p thumbnails/Genesis thumbnails/Newton
ffmpeg -y -ss 0.3 -i video/Genesis/<name>.mp4 -frames:v 1 -vf 'scale=960:-1' -q:v 4 thumbnails/Genesis/<name>.jpg
ffmpeg -y -ss 0.3 -i video/Newton/<name>.mp4 -frames:v 1 -vf 'scale=960:-1' -q:v 4 thumbnails/Newton/<name>.jpg
```

4. 在 `report.md` 中使用：

```md
[![Open video: <name>](thumbnails/<Platform>/<name>.jpg)](video/<Platform>/<name>.mp4)
```

## Step 9：回填报告

目的：把报告从占位模板变成最终评估报告。

回填顺序：

1. 填第 2 节实验环境；
2. 根据 `results/static_demo_stats.csv` 填第 5 节场景规模和参数；
3. 根据 `results/manual_fps_log.csv` 或 `results/minimal_benchmark_results.csv` 填 FPS；
4. 填第 6 节压力测试结果；
5. 填第 7 节平台 claim 验证；
6. 更新第 9 节阶段结论；
7. 最后检查所有视频和缩略图链接。

检查命令：

```bash
python -c "import re, pathlib; text=pathlib.Path('report.md').read_text(); paths=re.findall(r'\\]\\((video/[^)]+\\.mp4)\\)|!\\[[^\\]]*\\]\\((thumbnails/[^)]+\\.jpg)\\)', text); flat=[p for pair in paths for p in pair if p]; print([p for p in flat if not pathlib.Path(p).exists()])"
```

输出应为空列表。

## Step 10：形成最终选型建议

最终报告需要明确回答：

1. 如果目标是快速搭建多物理 demo，选哪个？
2. 如果目标是流体，选哪个？
3. 如果目标是机器人-布料/软体操作，选哪个？
4. 如果目标是复杂铰接刚体，选哪个？
5. 如果目标是长期维护和扩展，哪个代码结构更合适？
6. 是否应该双平台分工？

建议最终结论格式：

```text
如果后续重点是 [任务 A]，优先选择 [平台 X]，原因是 [量化证据 + 实现成本 + 稳定性]。
如果后续重点是 [任务 B]，优先选择 [平台 Y]，原因是 [量化证据 + 实现成本 + 稳定性]。
```

不要只写“看起来效果不错”，每个判断都尽量绑定 FPS、场景规模、稳定性和实现成本。
