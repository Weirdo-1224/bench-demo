# Long-Horizon Streaming Agent Benchmark — bench-demo

多 Episode Benchmark 的单 Episode（Pilot）工作区。当前以 GX010021 为 Golden Episode 完成候选事实整合、自动校验与 Pilot 候选任务生成；全部产物仍为 **CANDIDATE / NOT_REVIEWED**，人工 Gold 数量为 0。

## 目录结构

```
bench-demo/
├── docs/                    # Benchmark 总体设计文档（V1.0）
├── golden_episode/
│   └── GX010021/            # 第一个 Golden Episode（后续 Episode 按同构目录并列添加）
│       ├── source/          # 原始输入：GX010021.MP4、annotations.json（Ego-MC 原文）
│       ├── annotation_reports/  # Qwen 四轮历史标注报告及归档说明 README
│       ├── annotations/     # 结构化候选标注：events.json / objects.json / review_queue.json / schema.json
│       ├── tasks/           # pilot_task_candidates.json（T1/T2/T3 候选任务，gold_answer 全 null）
│       ├── reports/         # 整合报告、Track 适配性、缺口分析、任务生成报告、validation_results.json
│       ├── scripts/         # build.py（可重跑整合）、validate.py（schema/语义/输入哈希校验）
│       └── evidence/        # 证据复核产物：manifest、关键帧 PNG（入库）、切片 mp4（仅本地，
│                            # 不入库，可用 prepare_evidence.py 从本地视频重新生成）、复核清单/裁决
└── archive/                 # 已归档交付包（GX010021_pilot_task_candidates.zip），非日常输入，不入库
```

> 媒体文件说明：`*.MP4/*.mp4/*.zip` 与 `evidence/clips/` 已被 `.gitignore` 排除。原始视频（约 88MB）与 2.7GB 证据切片只保留在本地；克隆仓库后需把 `GX010021.MP4` 放回 `golden_episode/GX010021/source/` 才能重跑 `prepare_evidence.py` 与 build/validate 的视频元数据步骤。

## 复现校验

依赖：Python 3.11+、`jsonschema`、`ffprobe`（PATH）。在项目根目录执行：

```bash
python golden_episode/GX010021/scripts/build.py
python golden_episode/GX010021/scripts/validate.py --self-test
```

- `build.py` 先校验 7 个输入文件的 SHA-256 快照（4 份报告 + README + 视频元数据 + Ego-MC 原文），再从 `annotation_reports/` 整合生成 `annotations/` 下四个 JSON；只读取 ffprobe 元数据，不解码视频帧。
- `validate.py` 执行 Schema、ID/引用/时间/状态一致性、统计复算与输入哈希校验（约 5600 项断言），并运行内存负例检查；同时刷新 `reports/validation_results.json` 与 `reports/merge_report.md`。

最近一次校验：**PASS**（5618 项断言，13/13 负例被拒绝，7 个输入哈希一致）。

## 当前进度

- [x] GX010021 四轮历史报告归档与合并规则整理（`annotation_reports/README.md`）
- [x] 候选事实整合：56 事件 / 22 对象引用 / 115 状态节点 / 162 证据 / 55 Ego-MC 记录，字段级溯源
- [x] 自动校验与负例检查通过；14 项复核条目全部 OPEN（P0×2、P1×4、P2×8）
- [x] Pilot 候选任务包（Track T1/T2/T3 适配性分析、缺口分析、任务生成报告）
- [x] Episode 目录结构整理（source / annotation_reports / annotations / tasks / reports / scripts / evidence）
- [x] 证据准备产物（`evidence/`）：切片 + 关键帧 + manifest + T1/T2 任务复核清单与裁决记录（adjudication 尚未执行）
- [ ] 证据复核裁决执行与人工 Gold 标注
- [ ] Evaluator / Harness 开发、Pilot 与 Baseline 运行
- [ ] 第二个及后续 Episode 接入

## 注意事项

- `source/GX010021.MP4`（约 88MB）被 `.gitignore` 排除，不进入普通 Git 提交；原始视频保留在本地，勿删。
- 所有事件的 `time_status=APPROXIMATE`；视觉证据仅为历史 AI 报告所述抽样帧观察，SUPPORTED ≠ 人工 Gold。
