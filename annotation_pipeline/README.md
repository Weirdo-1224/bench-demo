# V2 视频模型标注流水线 · Session 1

本包实现独立的 L0 媒体来源与 L2 可见事件候选观察。三个 Track 以总体设计 V1.0 为准：T1 过程状态理解、T2 长程过程依赖推理、T3 持续监测与及时干预。本包不是 Streaming Runner 或 Evaluator。

正式运行只读取原始 `source/<episode_id>.MP4`、配置、Schema、中性提示词和本流水线自己的运行记录。不会读取源 `annotations.json`、V1 候选、历史报告、现有证据清单或任务答案。所有事件只能为 **CANDIDATE**；空事件集合也是合法输出，不表示整片无动作。

## 快速运行（Windows PowerShell 5.1 / 7）

在项目根目录执行。依赖 Python 3.11+、PATH 中的 ffmpeg / ffprobe：

```powershell
python -m pip install -r annotation_pipeline/requirements.txt
python -m annotation_pipeline.inspect_video
python -m annotation_pipeline.annotate_segments --dry-run --smoke
python -m unittest discover -s annotation_pipeline/tests -v
```

复制配置（这个文件已忽略，不入库），修改模型、endpoint、窗口、采样率和预算：

```powershell
Copy-Item -LiteralPath annotation_pipeline/config.example.yaml -Destination annotation_pipeline/config.local.yaml
```

默认凭证变量为 `DASHSCOPE_API_KEY`。`api_key_env` 必须是变量名称，不能直接填密钥。程序优先读取环境变量；未设置时读取被 Git 忽略的 `annotation_pipeline/credentials.local.json`，其结构为 `{"DASHSCOPE_API_KEY": "<在本地填写真实密钥>"}`。凭证值不会进入配置哈希、运行配置、提示词或请求审计文件。

也可以在本地 PowerShell 输入密钥，不写入配置或聊天：

```powershell
$annotationSecret = Read-Host 'DashScope API Key' -AsSecureString
$annotationSecretPtr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($annotationSecret)
try {
    $env:DASHSCOPE_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($annotationSecretPtr)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($annotationSecretPtr)
    Remove-Variable annotationSecret, annotationSecretPtr
}
python -m annotation_pipeline.annotate_segments --config annotation_pipeline/config.local.yaml --smoke
```

该变量在此 PowerShell 会话内生效；在同一会话启动命令。默认 endpoint 为中国内地 DashScope 兼容接口，必须与密钥所属地域一致。可通过配置或 `$env:ANNOTATION_ENDPOINT`、`$env:ANNOTATION_MODEL`、`$env:ANNOTATION_API_KEY_ENV` 覆盖三项设置。若使用 `QWEN_API_KEY`，将 `api_key_env` 改为这个变量名；不会自动尝试多个密钥。

初始默认：60 秒窗口、10 秒重叠、1 fps、最多两个窗口 `[0,60)` / `[50,110)`。`smoke_start_sec` 可改起点，`smoke_segments: 1` 可进一步限额。Smoke 必须是 1–2 个 30–60 秒窗口，尾部不足 30 秒会拒绝执行。无 `--smoke` 的真实调用被禁用。仅 `--dry-run` 可以列出全片窗口计划，但不抽全片帧、不调用模型。

环境变量和本地凭证均缺失时，Smoke 仍完成这两个短窗口的真实抽帧、请求构造与输入校验，然后记录 `MISSING_API_KEY`，退出码为 2；没有 `candidate.json` 和成功响应。Dry-run 退出码为 0，不发请求、不抽帧，只检查元数据、首秒可解码性和计划。

## 模型接口与来源

`VideoModelProvider` 定义 `build_request` / `invoke` / `extract_content`。`provider: qwen` 使用 Qwen3-VL-Plus；可配置任意符合契约的 `module:Class` 替换。通用调度层管理时间、审计、重试和预算，Provider 决定请求结构。当前实现采用从 MP4 解码的 JPEG 帧序列，以 Qwen 的 `type: video` 和 `fps` 提交。接口形态依据[阿里云官方接口文档](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-openai-chat-completions)。2026-10-10 两窗口真实 API Smoke Test 已通过；替换模型或接口仍需重新验证。

模型别名 `qwen3-vl-plus` 的配置版本标为 `alias-unpinned`；不能声称供应商返回的别名就是固定权重版本。后续应选择账户可用的快照型号，并设置 `model_version`。保留请求型号和服务端实际返回型号。

ffmpeg 从原视频时间轴选取每个采样格点之后的首个可用源帧；不使用恒定帧率转码来重造时间。保存解码帧 PTS、实际 time base、原视频秒数、片段相对秒数、JPEG 哈希及 ffmpeg 命令。原视频第一个媒体时刻为 0，映射公式是：

```text
source_sec = source_pts * pts_time_base - stream_start_sec
clip_local_sec = source_sec - segment.start_sec
event.source_sec = event.clip_local_sec + segment.start_sec
```

当采样格点漂移超过一帧源视频时长或帧数不完整时拒绝输入，避免宣称看过缺失帧。当前策略对 CFR 视频验证通过；遇到 VFR 或缺帧素材需调整并复核，不自动填补。模型提示词提供实际帧时间表，1 fps 帧间的内容未送入模型；采样不能证明快速动作没有发生。

## Schema 与校验

唯一权威 Schema 在 `schemas/segment_observation.schema.json`，内含 `$defs/model_response`（clip-local 输出）和最终候选契约。

| 契约 | 本轮字段 / 语义 |
|---|---|
| L0 | Episode、视频 SHA-256、时长/分辨率/fps/音轨；模型、endpoint、配置/代码/Schema/提示词哈希、运行 ID、请求哈希、原始响应引用与哈希 |
| L2 事件 | 片段局部事件 ID、运行范围事件 ID、源时间和局部时间、actor/action、对象局部轨迹 ID 和角色、visual_change、observability、uncertainties |
| L2 证据 | 范围、确实提交的 frame_id、帧路径、PTS、源秒数、哈希；frame_refs 的路径相对于 input_manifest 所在目录 |
| 时间精度 | `APPROXIMATE_SAMPLED`，不得当作逐帧确认的动作起止 |
| 后续层 | `deferred_layers.L1/L3/L4/L5 = null`，表示未标注，不是已证明不存在 |
| 成熟度 | 顶层和每个事件均为 `CANDIDATE` |

自动校验包括 JSON Schema、有限数值、视频/窗口/事件边界、局部到源时间映射、重复 ID、证据范围、未提交帧引用、帧和源视频哈希、安全路径、运行/模型/提示词来源、成功原始响应以及候选内容与原响应一致性。结构验证通过不表示事实正确或人工 Gold。

L3 可在后续通过事件 ID、片段局部对象 ID、前后可见变化和证据关联状态；本轮没有冻结跨窗口实体身份、材料谱系或状态有效期表。L4 还需要独立规范来源、真实前置关系和多段证据，事件先后不能直接转换成依赖边。不能从无音轨 MP4 单独恢复指令公开时刻。

## 保存、复用与限额

运行目录默认位于 `golden_episode/<episode_id>/annotations/v2_video_model/runs/`，已加入项目 `.gitignore`：

```text
session1-<fingerprint>/
  run_manifest.json          # 元数据、配置、代码/Schema/提示词哈希
  prompt_snapshot.json       # 中性提示词和模型输出 Schema
  dry_run-<uuid>.json
  summary-<uuid>.json
  media_qa-<uuid>.json
  seg-0000/
    input/input_manifest.json
    input/frame-*.jpg
    input/ffmpeg.log
    request.json             # 完整提示词、参数、输入帧索引、请求哈希；不存 Authorization
    attempt-000.start.json    # 发出前的调用与预算预留
    attempt-000.response.json # HTTP 状态、原始响应正文、耗时；或不确定传输错误类型
    candidate.json           # 仅真实成功响应经解析校验后创建
    validation.json
    error-<uuid>.json
```

所有运行产物以独占创建保存，不覆盖原始响应或候选。默认运行 ID 由视频、配置、提示词、Schema、代码和窗口计划指纹决定。相同配置重跑自动复用已验证候选；有成功响应而没有有效候选时只重解析保存的原响应，不再请求模型。`--reparse-only` 强制禁止新请求。改代码、模型、参数或提示词会产生新运行，可能重新计费；显式 `--run-id` 必须谨慎使用。

429 / 5xx 按指数退避重试（默认最多两次）；401/403/其他 4xx 不重试。超时、连接失败或仅有 start 记录的中断具有不确定计费结果，默认阻止重发。确实需要再次请求时显式传 `--retry-uncertain`；已经花费的尝试仍计入预算。进程崩溃可能遗留 `.active.lock`，应先检查原进程已停止再删除该锁；不自动抢占。

`max_api_calls` 是单个运行内含重试/中断预留的持久总上限（默认 4 次；两个窗口各重试两次理论上需要 6 次，预算会提前阻止）。默认费用预留上限 1 CNY，每次预留 0.25 CNY，均为本地配置值，**不是官方价格或实际账单保证**。记录服务商原始 usage、返回 Token、提交帧数、耗时；未返回时标记未知。可以填写 `input_cost_per_million` / `output_cost_per_million` 估算费用，实际账单始终需服务商对账，当前 `actual_billed_cost` 为 null。

独立核对真实源 PTS、验证候选（把 RUN_ID 替换为本次输出值）：

```powershell
python -m annotation_pipeline.verify_media 'golden_episode/GX010021/annotations/v2_video_model/runs/RUN_ID'
python -m annotation_pipeline.validate_output 'golden_episode/GX010021/annotations/v2_video_model/runs/RUN_ID/seg-0000/candidate.json'
python -m annotation_pipeline.annotate_segments --smoke --reparse-only
```

测试中的合成 Provider/事件只写 TemporaryDirectory，明确为 `SYNTHETIC_TEST_ONLY`，不进入 Episode 标注目录。初次缺密钥结果见 `SESSION1_REPORT.md`；配置密钥后的真实成功调用与进入 Session 2 的缺口见 `SESSION1_SMOKE_RETRY_REPORT.md`。
