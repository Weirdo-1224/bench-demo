# GX010021 V2 视频模型标注 · Session 1 实施规格

> 状态：实施规格草案（不是已完成的标注结果）  
> 目标：建立 **能够真正调用视频模型、输出可追溯候选观察** 的最小标注流水线，并对一段真实视频做 Smoke Test。  
> 不在本轮运行整段 696.93 秒视频，也不生成正式 Ground Truth 或三个 Track 的完整题库。

## 1. 背景与固定边界

- 依据现有 `docs/` 内《Long-Horizon Streaming Agent Benchmark Overall Design V1.0》，不修改 T1/T2/T3 的研究定义。
- 输入是 `golden_episode/GX010021/source/GX010021.MP4`，约 696.93 秒；**已知该 MP4 无音轨**。
- `source/annotations.json`、旧版 `annotations/v1_candidate/`、`tasks/v1_candidates/` 仅在以后交叉对照阶段使用；首次视频观察不得读取旧候选答案。
- 已完成重构的实际目录，以本地文件扫描结果为准。不要按本文拼写盲目重建或移动现有目录。
- 视频模型可以离线查看完整片段做标注；这不等于参评 Agent 获得未来输入。二者必须严格分开。

## 2. 标注数据设计：先定义核心字段，不冻结所有业务细节

总体设计中的六层：L0 媒体/来源；L1 规范/指令；L2 观察事件；L3 事实状态；L4 历史依赖；L5 错误与干预。本轮重点打通 **L0 + L2** 的生成和校验，并为 L3–L5 预留明确的数据契约。不得为了填满空字段捏造规则或异常。

### L0 — Media & Source

- `episode_id`、视频哈希、分辨率、帧率、时长、音频存在与否。
- 模型名称与版本、接口、采样率、窗口位置、提示词版本、配置哈希、运行 ID、原始响应。
- 每项观察的原媒体秒数（建议同时保存原始帧 PTS 或可追溯帧引用）；任何 `clip-local` 时间必须可还原成原始视频时间。

### L2 — Observed Event（主产物）

事件字段（建议，实际以实现出的 Schema 为准）：

| 字段 | 含义 |
|---|---|
| `event_id` / `local_event_id` | 唯一标识；先按片段内部编号，跨片段归并后再生成稳定全局 ID |
| `start_sec`, `end_sec` | 原视频时间，允许粗略或区间不确定性 |
| `actor` | 可见执行者或 `unknown` |
| `action` | 可见动作（如搅拌、移动、倾倒），不写推测意图 |
| `objects` | 操作对象、工具、来源容器、目标容器，以及局部轨迹 ID |
| `visual_change` | 前后可见状态变化；证据不足时为空 |
| `evidence` | 视频时间范围与帧/片段定位，不能仅写事件标题 |
| `observability` | `direct` / `partial` / `unobservable` |
| `uncertainties` | 遮挡、画外、模糊、物体身份、材料性质等 |
| `provenance` | `model_id`、`run_id`、片段 ID、原始响应引用 |
| `annotation_status` | 本阶段只能是 `CANDIDATE` |

### L3 — Factual State（下一会话完善）

对象身份、属性、状态前后、有效时间区间、状态转移、连续身份不确定性。**相似外观/相同旧 ID ≠ 已证明是同一实体**。

### L1 / L4 / L5（后续补足）

- L1：规范要求与实际动作分开；无音轨视频不能独立证明实际话语、角色和公开时刻，来自源 `annotations.json` 的文本必须保存独立的来源及可靠性标签。
- L4：依赖图需要可核验的转移/前置关系和多处证据，不能将先后顺序直接当作因果依赖。
- L5：T3 只能基于明确规则与可见偏差构造异常；没有正例时如实报告，不制造违规。

## 3. 视频模型标注工作流

1. **Inspect**：用 ffprobe 获取视频参数、帧率、音轨、时长、SHA-256；检查视频可解码。
2. **Global Pass（下一会话）**：全片粗粒度概览，仅给阶段候选，不直接确认细粒度事实。
3. **Segment Pass（Session 1 先打通）**：默认 60 秒片段、10 秒重叠、初始 1 fps，保留源时间映射。每片段输出 JSON 形式的可见动作候选与未知信息；可按模型能力调整采样方式。
4. **Dense Review（后续）**：对快速动作/对象交换/转移/片段冲突按需提高采样率并缩短片段，不对全视频盲目高密度调用。
5. **Cross-window Fusion（Session 2）**：相邻片段重叠事件合并；分离物理对象身份与材料连续性；冲突保留审计。
6. **V1 Cross-check（Session 2）**：在独立视频观察的首版输出已经写入且不可随意覆盖之后，再读取历史候选标注进行匹配、发现遗漏与冲突。
7. **Task Derivation（Session 3）**：从统一事实层派生 T1/T2/T3 候选实例，标注证据是否足够和适用 Track。

片段推荐值（60 秒、重叠 10 秒、1 fps）只是开发起点，不是固定 Benchmark 评分参数。请在配置中暴露。

## 4. 模型接入与工程要求

- 首先实现一个 `VideoModelProvider` 接口，并接入**一种实际可用的视频模型**，建议优先测试 Qwen 视频理解 API（可配置具体模型、endpoint 和凭证）；不要把模型名写死在标注逻辑里。
- 服务端直接接收 MP4 还是抽样帧，由 Provider 决定，必须记录实际传入了哪些片段或帧，以及采样参数；不可以声称看过未送达模型的帧。
- 原始响应保存为不可覆盖的运行记录；校验后生成结构化候选观察。解析失败要保留错误输出并能够重新执行。
- Windows PowerShell 兼容；避免只给 Bash 指令。密钥通过环境变量/本地未入库配置提供，绝不能写入源文件或日志。
- 支持 `--dry-run`（不调用模型，验证路径/计划/参数）和 `--smoke`（仅处理一至两个 30–60 秒片段）。首次不全量运行。
- 超时、错误重试、重复运行跳过已完成片段、费用/Token/帧数记录（服务商能返回时）及成本上限必须可配置；没有 API Key 时报告阻塞，不伪造成功。
- V1 数据完全只读，**不要修改目录重构或已有构建脚本**。

## 5. 建议的轻量级项目结构

```text
bench-demo/
├── annotation_pipeline/
│   ├── README.md
│   ├── config.example.yaml
│   ├── schemas/
│   │   └── segment_observation.schema.json
│   ├── prompts/
│   │   └── segment_observation.md
│   ├── providers/
│   │   ├── base.py
│   │   └── qwen.py
│   ├── inspect_video.py
│   ├── annotate_segments.py
│   └── validate_output.py
└── golden_episode/GX010021/
    ├── source/                       # 不变
    ├── annotations/v1_candidate/     # 不变
    └── annotations/v2_video_model/
        ├── README.md
        └── runs/                     # 不入库的运行中间产物和结构化结果
```

目录只是职责建议，可适配现有项目；不引入数据库、队列、Web 界面或完整 Runner。

## 6. Session 1 的验收条件

1. 代码能通过本地 MP4 做 inspect，并准确报告有无音轨、时长、帧率及哈希。
2. `--dry-run` 正确列出源时间区间、采样计划、预计调用次数，**不产生网络模型请求**。
3. 能调用所配置的视频模型完成至少一个真实片段的分析；若缺密钥则留下可执行命令与清晰阻塞原因，不将 Mock 输出当作真实结果。
4. 真实输出保存原始响应和结构化 JSON，标记 `CANDIDATE`，有完整时间、视频证据和模型来源。
5. JSON Schema、时间边界、路径、非空来源记录自动校验通过；不产生源视频外的时间戳。
6. 保留 V1 所有现有数据内容及文件哈希，不生成任务库、不晋升 Gold。
7. 提供最简 PowerShell 运行指令和 Smoke Test 实际结果报告。

## 7. 后续 Session 划分（不在本轮实施）

- **Session 2：全片分析与 V2 事实整合**：Global + Segment + Dense Review + Fusion + V1 cross-check，输出事件、对象、状态、关系、来源与缺口报告。
- **Session 3：Track 实例化**：从 V2 生成 T1 状态检查点、T2 依赖 Probe、T3 合规/异常候选任务；审计可评分性、Historical Necessity 和 T3 正例覆盖，保留未解决问题。

**原则：先让视频模型实际产生可追溯观察，再讨论如何提升标注覆盖度与质量。**
