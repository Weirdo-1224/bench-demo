# Long-Horizon Streaming Agent Benchmark — bench-demo

多 Episode Benchmark 的单 Episode（Pilot）工作区，用于评测 **Model + Agent Harness** 的整体能力。当前以 GX010021 为 Golden Episode。

## 研究目标与三个 Track

Benchmark 总体设计见 `docs/Long_Horizon_Streaming_Agent_Benchmark_Overall_Design_v1.0 (1).md`，定义了面向长程过程性视频（第一视角烹饪等）的三个 Track：

- **T1 Streaming QA**：视频流式输入下的在线问答，考察信息可见时刻与最早可答时间。
- **T2 Agentic Online Assistant**：助手在交互规则、建议与许可约束下的在线辅助行为。
- **T3 State-dependent Procedure**：依赖过程状态与历史一致性的程序性任务。

统一评测协议与三 Track 的任务定义以总体设计 V1.0 为准。

## V1 与 V2 的区别

- **V1 Candidate（已完成，已归档）**：利用 AI 辅助分析、历史报告整合形成的结构化候选事实与任务数据（`annotations/v1_candidate/`、`tasks/v1_candidates/`），作为历史基线和交叉核验来源。全部为 **CANDIDATE / NOT_REVIEWED**，人工 Gold 数量为 0，不代表人工确认的 Gold Ground Truth。
- **V2 Video-model Annotation（尚未实施）**：计划由视频理解模型**独立**理解原始视频，再与 V1 历史标注交叉整合，生成服务于三个 Track 的统一时序标注，并派生 V2 候选任务。当前仅有占位目录（`annotations/v2_video_model/`、`tasks/v2_candidates/`），**没有任何标注或任务产物**。

## 当前项目进度

- [x] Benchmark Overall Design V1.0（三个 Track 任务定义与统一评测协议）
- [x] GX010021 多轮 AI 辅助标注报告归档与候选事实整合（V1：56 事件 / 22 对象引用 / 115 状态节点 / 162 证据 / 55 Ego-MC 记录）
- [x] V1 自动校验与负例检查通过；14 项复核条目全部 OPEN（P0×2、P1×4、P2×8）
- [x] 三个 Track 的 Pilot 候选任务实例化（`tasks/v1_candidates/pilot_task_candidates.json`，gold_answer 全 null）
- [x] 证据准备产物（`evidence/`）：切片 + 关键帧 + manifest + T1/T2 任务复核清单与裁决记录（adjudication 尚未执行）
- [x] V1/V2 目录隔离重构（Git 快照标签 `pre-v2-annotation`）
- [ ] V2 Schema 设计、视频模型接入与独立标注
- [ ] V2 与 V1 交叉整合、三个 Track 候选任务重新派生
- [ ] 证据复核裁决执行与人工 Gold 标注
- [ ] Evaluator / Harness 开发、Pilot 与 Baseline 运行
- [ ] 第二个及后续 Episode 接入

## 目录结构

```
bench-demo/
├── docs/                    # Benchmark 总体设计文档（V1.0）
├── golden_episode/
│   └── GX010021/            # 第一个 Golden Episode（后续 Episode 按同构目录并列添加）
│       ├── source/          # 原始输入：GX010021.MP4、annotations.json（Ego-MC 原文）
│       ├── annotation_reports/  # Qwen 四轮历史标注报告及归档说明 README
│       ├── annotations/
│       │   ├── v1_candidate/    # V1 结构化候选标注：events.json / objects.json / review_queue.json / schema.json
│       │   └── v2_video_model/  # V2 视频模型标注工作区（占位，尚未实施）
│       ├── tasks/
│       │   ├── v1_candidates/   # pilot_task_candidates.json（T1/T2/T3 候选任务，gold_answer 全 null）
│       │   └── v2_candidates/   # V2 候选任务工作区（占位，尚未实施）
│       ├── reports/         # 整合报告、Track 适配性、缺口分析、任务生成报告、validation_results.json
│       ├── scripts/         # build.py（可重跑整合）、validate.py（schema/语义/输入哈希校验）
│       └── evidence/        # 证据复核产物：manifest、关键帧 PNG（入库）、切片 mp4（仅本地，
│                            # 不入库，可用 prepare_evidence.py 从本地视频重新生成）、复核清单/裁决
└── archive/                 # 已归档交付包（GX010021_pilot_task_candidates.zip），非日常输入，不入库
```

> 媒体文件说明：`*.MP4/*.mp4/*.zip` 与 `evidence/clips/` 已被 `.gitignore` 排除。原始视频（约 88MB）与 2.7GB 证据切片只保留在本地；克隆仓库后需把 `GX010021.MP4` 放回 `golden_episode/GX010021/source/` 才能重跑 `prepare_evidence.py` 与 build/validate 的视频元数据步骤。

## V1 标注构建与校验

依赖：Python 3.11+、`jsonschema`、`ffprobe`（PATH）。在项目根目录执行：

```bash
python golden_episode/GX010021/scripts/build.py
python golden_episode/GX010021/scripts/validate.py --self-test
```

- `build.py` 基于脚本位置解析 Episode 根目录（不依赖调用时工作目录），先校验 7 个输入文件的 SHA-256 快照（4 份报告 + README + 视频元数据 + Ego-MC 原文），再从 `annotation_reports/` 整合生成 `annotations/v1_candidate/` 下四个 JSON；只读取 ffprobe 元数据，不解码视频帧。输入变化会拒绝重建。
- `validate.py` 执行 Schema、ID/引用/时间/状态一致性、统计复算与输入哈希校验（约 5600 项断言），并运行内存负例检查；同时刷新 `reports/validation_results.json` 与 `reports/merge_report.md`。

最近一次校验：**PASS**（5618 项断言，13/13 负例被拒绝，7 个输入哈希一致）。

注意：`build.py` 会覆盖重写 `annotations/v1_candidate/` 下的归档 JSON，属于可重跑的确定性重建（输入哈希校验通过后才会执行），不要在未核对输入快照的情况下对归档数据直接重跑。

## 下一阶段计划（V2）

1. 设计 V2 统一时序标注 Schema（覆盖三 Track 需求）。
2. 接入视频理解模型，对 `source/GX010021.MP4` 独立标注。
3. 与 V1 候选标注交叉整合（冲突保留双方来源），派生三个 Track 的 V2 候选任务。
4. 执行证据复核裁决，逐步建立人工 Gold。

## 注意事项

- `source/GX010021.MP4`（约 88MB）被 `.gitignore` 排除，不进入普通 Git 提交；原始视频保留在本地，勿删。
- 所有事件的 `time_status=APPROXIMATE`；视觉证据仅为历史 AI 报告所述抽样帧观察，SUPPORTED ≠ 人工 Gold。
- 历史报告与 `evidence/` 清单中记录的旧路径（如 `annotations/events.json`、`tasks/pilot_task_candidates.json`）为历史溯源字段，保留原值；当前实际运行路径见上方目录结构与各脚本中的 `v1_candidate` / `v1_candidates` 路径常量。
