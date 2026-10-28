# GX010021 ICME 2027 pilot

本目录只做 GX010021。当前交付为**审计及候选准备阶段**，没有运行付费API，也没有实验正确率。真实三条件实验在研究者核验后继续完成。

在仓库根目录 `D:\Python_Project\bench-demo` 使用 PowerShell：

```powershell
python -m pip install -r experiments/icme2027_pilot/requirements.txt
python -X utf8 experiments/icme2027_pilot/pilot.py audit
python -X utf8 experiments/icme2027_pilot/pilot.py prepare
python -X utf8 experiments/icme2027_pilot/pilot.py validate
python -X utf8 experiments/icme2027_pilot/pilot.py dry-run --task P01
python -X utf8 experiments/icme2027_pilot/pilot.py report
python -X utf8 -m unittest discover -s experiments/icme2027_pilot -p "test_*.py" -v
python -X utf8 experiments/icme2027_pilot/verify_preparation.py
```

依赖 Python 3.11+、PATH 中的 FFmpeg/ffprobe、requests、PyYAML、Pillow。当前环境已有这些依赖，无需新增安装。`prepare` 首次需要本地解码/转码时间；重复运行复用哈希一致的剪辑与帧，不发API请求。任一步骤失败返回非零退出码，保留失败文件以便检查，禁止静默覆盖不匹配缓存。

**人工核验唯一入口：[review_checklist.md](review_checklist.md)**。先审核 P01 即可启动最小真实实验，P02可留待后续。可以在聊天按清单回复，不需要手工编写JSON或上传文件。工程师根据回复填入 `review_decisions.jsonl`。

熟悉JSON的研究者也可自行编辑 `review_decisions.jsonl`：每行一题，`status` 可为 `PENDING/APPROVED/REJECTED/INVALID`。批准须填写研究者姓名/代号、ISO日期时间、8项PASS、4个条件答案，以及从视频确认的证据区间。修改候选定义/视频/区间后必须重新准备与审核，不能沿用旧签名。不要直接修改 `candidate_tasks.jsonl`。

```powershell
# 只有研究者明确确认并记录完成后执行：
python -X utf8 experiments/icme2027_pilot/pilot.py validate --promote
```

无批准任务时不生成 `tasks_gold.jsonl`。存在批准任务后，Gold仅包含APPROVED记录；已有Gold不一致时拒绝覆盖。`validate` 只是结构、哈希与时间检查，不能代替人工语义核验。

|命令|当前状态|是否付费|
|---|---|---|
|audit|可运行：资产、依赖、凭证可加载性、原文件保护|否|
|prepare|可运行：候选、筛选账本、片段、1FPS帧、计划掩码|否|
|validate [--promote]|可运行：审核门禁；只将人工APPROVED写入Gold|否|
|dry-run [--task P01]|可运行：逐窗执行计划及请求数量|否|
|report|可运行：准备阶段Markdown、CSV、JSON、PNG|否|
|run|确认后继续实现及实测；当前明确报错退出，不产生预测|否|
|score|确认后继续实现；当前明确报错退出，不产生分数|否|

下一阶段不会把现有历史API响应或程序测试当作先导实验。首题必须从空记忆分别真实运行FULL、CRITICAL_MASK、CONTROL_MASK，保留原始响应、输入重构清单、usage、时延和请求账本，成功后再扩展。完整固定协议及待实现边界见 [experiment_protocol.md](experiment_protocol.md)。

产物说明：

- `audit/audit.json`：实际路径、Git版本、依赖与凭证状态；从不保存密钥值。
- `audit/original_hashes.json`、`audit/integrity_check.json`：原文件冻结清单及复核；不修改原Git历史。
- `candidate_tasks.jsonl`：2条PENDING候选；`selection_audit.jsonl`：13条T1/T3筛选记录。
- `clips/P01/`、`clips/P02/`：每题关键/当前/对照三个MP4，加黑屏历史MP4；每个附`.manifest.json`。
- `inputs/`：9个60秒窗口的实际1FPS原帧及原PTS/哈希，P01复用前5窗。
- `review_frames/`：每秒缩略图及完整采样清单，仅供人工审阅；模型不接收拼图。
- `mask_manifest.jsonl`：计划掩码，明确`applied_to_model=false`，不是已执行模型输入。
- `review_decisions.jsonl`：人工审核状态；`tasks_gold.jsonl`：批准后才创建。
- `predictions.jsonl`：当前空文件；`results.csv`：NOT_RUN行、空指标；`summary.json`：accuracy=null。
- `advisor_report.md`、`figures/preparation_status.png`：准备报告与准备状态图。

所有新产物在本目录。原视频、既有Gold/候选、任务Schema、凭据和ReflectWorld代码都不改写。原始凭据沿用`annotation_pipeline/credentials.local.json`或`DASHSCOPE_API_KEY`环境变量，禁止复制密钥到新配置、日志或聊天。
