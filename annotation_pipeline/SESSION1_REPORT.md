# GX010021 V2 · Session 1 实施与验收报告

日期：2026-10-10（Asia/Shanghai）  
结果：**代码、Dry-run、真实短窗口媒体验证完成；真实模型 Smoke Test 尚未通过，原因是未配置 API Key。**

更新：本文件保留首次无密钥验收的历史记录。用户配置凭证后，两个真实窗口调用已成功；最新结果见 `SESSION1_SMOKE_RETRY_REPORT.md`。

## 实施范围

已阅读总体设计 V1.0、实际文件 `docs/GX010021 V2 视频模型标注 · Session 1 实施规格.md`，扫描实际 GX010021 目录。未重设三个 Track。发现根 README 中使用旧 Track 名称，本轮遵从总体设计 V1.0；未改根 README 或 V1。

| 文件 | 功能 |
|---|---|
| `annotation_pipeline/config.example.yaml`、`common.py` | 路径、模型/接口/凭证变量、窗口/采样/限额配置；安全输出范围；哈希和独占写入 |
| `inspect_video.py` | ffprobe 媒体参数、SHA-256、首秒可解码检查 |
| `media.py` | 连续重叠窗口、真实帧抽样、解码 PTS、源/局部时间映射、帧缓存完整性 |
| `providers/base.py`、`providers/qwen.py`、`providers/__init__.py` | 可替换 Provider 接口；Qwen 帧序列 API 适配；一次 invoke 对应一次请求 |
| `prompts/segment_observation.md` | 中性独立视觉观察要求，禁止补造话语/规则/意图/违规 |
| `schemas/segment_observation.schema.json` | L0/L2 契约及模型局部时间输出 Schema；CANDIDATE；未实现层明确为 null |
| `annotate_segments.py` | Dry-run / 最多两个短窗口 Smoke；保存来源、请求/响应、结构化候选和验收结果 |
| `calls.py` | 持久调用预留、预算、限次重试、成功响应复用、不确定计费中断保护 |
| `validate_output.py` | Schema、ID、时间/证据/路径/来源校验，并比对候选与原始响应内容 |
| `verify_media.py` | 用 ffprobe 独立核对原视频 PTS 与抽样证据定位 |
| `tests/test_pipeline.py`、`tests/test_integration.py` | 19 项测试，含端到端合成夹具、断点复用、重解析、预算与负例校验 |
| `requirements.txt`、`README.md`、包初始化文件、包内 `.gitignore` | 依赖、PowerShell 操作说明、本地配置/哈希快照忽略规则 |

另修改项目 `.gitignore`，忽略 `v2_video_model/runs/`；更新 V2 目录 README，说明本轮实际状态。没有修改旧脚本、V1 文件、原始媒体或任务库。

## 真实视频检查与运行记录

视频：`golden_episode/GX010021/source/GX010021.MP4`

- SHA-256：`fe4a11550bf2aea09a39ce1e72dba4633adc8c8b6a540e9894696e8b2ed1c8f9`
- 大小：91,608,663 字节；分辨率 854 × 480。
- 时长：696.929567 秒；帧率 `30000/1001` ≈ 29.97003 fps；原视频 time base 为 `1/30000`。
- 无音轨；存在 timecode 数据轨，不能将其当作音频。
- 首秒解码检查通过；两个指定短窗口的抽样解码通过。

最终代码运行 ID：`session1-55b5a94222a1f53ddf0f`。代码和配置相同时默认复用此运行；改配置/代码会得到新指纹。

本地记录都位于 `golden_episode/GX010021/annotations/v2_video_model/runs/session1-55b5a94222a1f53ddf0f/`：

- Dry-run：`dry_run-0dc6b731fbdb4844bff5bc9c4e563c44.json`，`DRY_RUN_PASS`。
- 首次 Smoke：`summary-0850d47d521a40b5bc7d1af904e5e497.json`，`SMOKE_INCOMPLETE`。
- 同运行重跑：`summary-dfd3e078210d4a4d89e5cfa49f4a1ae3.json`，仍因缺密钥阻塞，复用输入帧与请求，新增请求 0。
- 独立媒体核验：`media_qa-f31576107a344f5796ac7e1e3f3910fc.json`，`PASS`。
- 原文件保护结果：`v1_integrity.json`，80 项原有 Episode 文件 SHA-256 全一致，变更列表为空。

开发过程中还有一个较早代码指纹的本地运行 `session1-bf9a5a3ff15a83eb18d3`，同样请求数为 0、没有候选事件，保留作审计，不覆盖。

## Smoke Test 实际结果

| 窗口 | 原视频区间（秒） | 抽取帧数 | 实际首帧 / 末帧（源秒数） | 最大采样格点偏差 | 模型状态 |
|---|---|---:|---|---:|---|
| seg-0000 | `[0,60)` | 60 | 0.000000 / 59.025633 | 0.033000 秒 | BLOCKED：缺 API Key |
| seg-0001 | `[50,110)` | 60 | 50.016633 / 109.008900 | 0.033267 秒 | BLOCKED：缺 API Key |

默认请求型号为 `qwen3-vl-plus`，版本为未固定的别名 `alias-unpinned`。当前进程没有 `DASHSCOPE_API_KEY` 或 `QWEN_API_KEY`；配置使用前者，未自动寻找或替换凭证。

**真实模型调用：0。提交帧数：0。模型 usage 记录：0。结构化候选事件产物：0。**

没有成功原始响应、没有 `candidate.json`，不把抽样输入或测试夹具描述成模型观察。观察结果不是“模型确认无事件”，而是“尚未得到模型响应”。因此模型服务端认证、请求接受性、真实 JSON 输出质量、动作语义与事件时间准确性均未实证验证。

19 项测试全部通过（2026-10-10）。合成事件只在测试 TemporaryDirectory 内生成，明确标识测试来源，未混入 Episode。测试验证了成功流程、已完成候选复用、原始响应重解析、结构及内容篡改拒绝、缺密钥零调用、429/5xx 重试、401 不重试、超时不自动重发、持久次数/费用预留限额和全视频调用禁用。

## 时间与证据可靠性

独立 ffprobe 在视频前 111 秒解码得到 3,327 个源帧时间戳，全部 120 个抽样帧的 PTS 能在原视频解码结果中找到。采样格点偏差小于一个源帧周期（约 0.033367 秒）；例如第二窗口首帧源 PTS 为 1,500,499，对应源时间 50.016633333 秒和局部时间 0.016633333 秒。

这个结果支持**源帧定位和时间映射可靠**。它不支持“模型识别动作边界精度为 33 毫秒”。模型只会收到 1 fps 样本，帧间快速动作、遮挡和对象交换可能遗漏；事件时间标记 `APPROXIMATE_SAMPLED`，之后仍需真实输出和人工/密集复核。

候选自动校验要求证据确实引用提交帧，源视频/帧/响应哈希匹配、所有时间不越界，并能恢复原媒体位置。无音轨时没有可直接核验的实际话语或指导者指令公开时刻。

## Schema 对后续整合的支撑与缺口

本轮 Schema 足以承载**后续整合的输入观察与审计基础**：运行范围事件 ID、片段局部对象 ID、参与角色、可见变化、未知信息、证据帧和来源。没有真实模型输出，尚不能声称这些字段已在 GX010021 上验证覆盖充分。

L3 仍缺跨窗口实体身份裁决、物理对象与材料连续性区分、属性/状态字典、状态前后、有效时间区间和状态转移契约。L4 仍缺独立规范来源、指令版本/有效期、可核验前置关系以及多证据集合。局部对象轨迹 ID 不等于全局实体 ID，事件先后不等于依赖。

L1/L3/L4/L5 用 null 显式表示“未标注”，没有填补虚构规则、依赖或异常。本轮没有 Fusion、V1 cross-check、全视频模型处理、Track 派生、Gold 晋升或 Evaluator 开发。

## 进入 Session 2 前需要完成

1. 在同一 PowerShell 会话配置地域匹配的有效 API Key，先完成本次 1–2 窗口真实调用，并验证原始响应、候选事件、证据与 Schema。
2. 复核真实候选，评估 1 fps 能否覆盖动作/对象转移，选定可用模型快照、采样参数与正式费用预算。现在的费用上限只是本地每次调用预留，实际账单未知。
3. 基于真实观察补足 L3 状态与对象身份契约、跨窗口融合和冲突审计；再确定全片 Global / Segment / Dense Review 策略。
4. 在独立观察首版保存后才进入 V1 对照，并为无音轨视频的规范文本明确来源与可靠性；Track 任务派生留至 Session 3。

可执行 PowerShell 密钥输入方式和运行命令详见 `annotation_pipeline/README.md`。本轮至此停止，等待下一轮安排。
