# 整理验收结果

| 检查 | 整理前 | 整理后 |
|---|---|---|
| 标注流水线测试 | 26/26 通过 | 26/26 通过 |
| P01 当前上下文测试 | 13/16 通过；2 FAIL、1 ERROR | 相同 3 项受旧门禁阻断 |
| P01 冻结上下文补充测试 | 16/16 通过 | 16/16 通过 |
| 原始 wire 请求重构 | 18/18 | 18/18 |
| 四条件 checkpoint/记忆链重放与评分 | 4/4 成功 | 4/4 成功 |
| 报告生成 | 副本内完成 | 副本内完成 |
| 模型 API 调用 | 0 | 0 |

当前上下文失败的测试为 test_approved_without_all_checks_cannot_promote、test_pending_does_not_create_gold、test_tampered_definition_rejected_before_promotion。整理前 .gitignore 已不同于 audit/original_hashes；冻结 HEAD 为 d0db40f，整理前当前 HEAD 已为 635cc72。整理后文档改写使 README 也触发旧冻结门禁。本次保留原审计和测试，未掩盖失败。验证命令因此返回非零退出码。

补充测试只在独立副本恢复旧文档，并替换测试加载的 pilot.cmd 的 HEAD 查询返回值，其他原始资产哈希校验照常执行。补充测试不等同于当前门禁通过。

全量比对 5,381 个原文件，除授权编辑的 README.md 和 .gitignore 外均保持 SHA-256；没有最终路径迁移。原实验目录、视频、候选标注、Gold、所有请求、帧、记忆、原始响应和历史输出均未改写。

before/after 的 results.csv、predictions.jsonl、scoring_details_v1.json、PNG 哈希一致，且与原记录逐字节一致。报告 Markdown 固定生成时间后前后哈希一致；summary 去除 created_at 后完全相同。原报告和原 summary 不写入。

关键结果保持：四条件完成；18 次原始响应；input_tokens=246034，output_tokens=13268，elapsed_sec≈527.858；P02=PENDING。模型回答 FULL=YES、CRITICAL_MASK=NO、CONTROL_MASK=YES、recent_only=NO。语义证据审核仍为 PENDING。

完整机器可读结果和 SHA-256 见 validation.json；原日志位于 `.local/layout-validation/{before,after}/`，副本评分、报告和 PNG 位于各 phase 的 workspace/experiments/icme2027_pilot/。早期验证尝试已另名保留，仅 before/after 是最终验收。

最终运行 `python -X utf8 scripts/check_catalog.py`：9 份新增/更新入口文档、21 个文档链接、8 个 Episode 路径引用均通过；原视频 SHA-256 与兼容 manifest 一致；5,379 个未授权改写的原文件全部哈希一致，仅根 README 和 .gitignore 按计划编辑。忽略规则验证确认本地恢复包、重放副本和新视频被忽略，而新 Episode 的 Gold JSON 与证据 manifest 不被忽略。`git diff --check` 通过。
