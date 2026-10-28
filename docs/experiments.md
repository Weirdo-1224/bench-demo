# 实验版本与复现边界

`experiments/icme2027_pilot/` 整体原位保留。P01 为已执行的 GX010021 单任务四条件先导实验，P02 保持 PENDING。

| 层次 | 路径 | 保留规则 |
|---|---|---|
| 原始输入 | `golden_episode/GX010021/source/` | 视频及源标注不覆盖 |
| 候选标注 | Episode 的 `annotations/v1_candidate/`、`v2_video_model/` | 不等于人工 Gold |
| 人工裁决 | 实验的 `tasks_gold.jsonl`、`review_decisions.jsonl` | 保留原字节与批准链 |
| 准备历史 | `archive_phase1/` 和版本化文件 | 不合并、不删除 |
| 执行版本 | `runs/p01-v1/` | 保留 manifest、amendment 和全部 code_snapshot |
| 精确输入输出 | request、frames、attempt response、checkpoint | 包括失败尝试和 length recovery |
| 账本 | `request_ledger/`、`request_index_v1.jsonl` | 保留全部 18 次记录 |
| 派生结果 | results、summary、predictions、scoring_details、advisor_report、figures | 仅在副本生成，不覆盖原记录 |

离线验证覆盖 18 次 wire SHA、四条件 checkpoint/记忆前缀链和原始 HTTP body 重解析。模型回答为 FULL=YES、CRITICAL_MASK=NO、CONTROL_MASK=YES、recent_only=NO；证据不足的条件恰当回答应为 UNKNOWN，语义支持仍待人工审核。

旧 verify_run_v1.py 会调用 run 做复用检查，并重写审计。本次采用独立验证器，禁止网络及 inference 入口。旧 verify_originals() 冻结文档和 Git HEAD：整理前 HEAD 已不同于旧审计，.gitignore 也已有哈希差异。本次不修改旧审计基线；提交后仍需人工版本复核才能重新使用旧 HEAD 门禁。

补充测试只在副本恢复旧 .gitignore/README，并对测试加载的 pilot.cmd 的 HEAD 查询返回原审计 HEAD；其余原哈希检查仍执行。该结果用于隔离历史上下文问题，不代表当前上下文门禁通过。

云模型使用未固定 alias，离线结果可核验，不保证重新推理逐字一致。完整本地资产不包含在 Git clone 中。本次不启动任何新的真实推理。
