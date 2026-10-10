# GX010021 — Golden Episode 候选标注材料（四轮原文归档）

## 目的

本目录整理了 Qwen 对 `GX010021.MP4` 的四轮分析文本，供 Codex 后续构建统一候选事实层（例如 `candidate_events_consolidated.json`）时使用。原始视频与 Ego-MC 文本现归档于本 Episode 的 `../source/`（`GX010021.MP4`、`annotations.json`）。

**这是一份历史报告归档，不是已经合并、审定的 Ground Truth。** 各轮内容按原来的表述分别保留；较早报告中的错误、矛盾与被推翻的结论并未直接覆盖，以保留追溯能力。

## 文件目录

| 文件 | 对应轮次 | 使用方式 |
|---|---|---|
| `candidate_events_v1.md` | 第一轮：独立视频事实标注 | **基础数据**：E001–E056（56 条事件）、O01–O15（15 个对象）、待复核时段 |
| `verification_report.md` | 第二轮：Video Grounding Verification | 各事件原始核验判断、建议修改、疑难对象及人工待审核条目；此文件直接由已上传的 TXT 原文复制 |
| `consistency_revision.md` | 第三轮：核验报告数据一致性审查 | 覆盖第二轮中的时间引用、统计、去重和证据级别错误 |
| `crosscheck_report.md` | 第四轮：与原始 `annotations.json`（现 `../source/annotations.json`）交叉核验 | 55 条辅助记录映射、候选遗漏/冲突线索、最终局部修订建议 |

`candidate_events_v1.md`、`consistency_revision.md`、`crosscheck_report.md` 根据本次对话中用户粘贴的完整结果整理；保留各自报告的表述，未将后轮修订直接写回早期报告。

## Codex 合并时的修订优先级

1. **事件/对象基线**：从 `candidate_events_v1.md` 建立 E001–E056、O01–O15；所有 ID 保持稳定。
2. **初步核验**：读取 `verification_report.md`，保留原判断、证据和修正建议，注意该报告自身存在的时间戳表示错误和 E054 自我纠正。
3. **一致性更正**：应用 `consistency_revision.md` 的时间换算与结论：报告自述的最终汇总为 45 SUPPORTED、1 CONTRADICTED（原 E042）、10 UNCERTAIN；E057 与 E058 撤销；面粉**加入混合容器**两次（E032/E051）。
4. **更晚的局部修订**：`crosscheck_report.md` 对 E049 的候选区间使用 **09:20–09:41**，E054 只保留“盖回粉色罐盖”；“糖袋已位于罐内”记录为对象状态，不视为该时间段内已证实的插入动作。
5. **字段级证据来源**：将视频抽样帧、跨帧推断、来自第一轮的文本继承、Ego-MC 原始文本线索分开记录；不要将原始 Instruction、Feedback、Success 等直接改写为新 Benchmark 的事实或 SOP。
6. **标注身份**：第二轮 `CONTRADICTED` 指“**第一轮原始主张**被否定”；对于 E042，修正后“液态为主、仍可见固态块”是待确认的候选事实，不能直接给修正后断言沿用 `CONTRADICTED`。

## 关键注意事项

- 本包不内嵌原始 `GX010021.MP4`、`annotations.json`；二者作为 Episode 源数据保存在同级 `../source/` 目录，避免把 88MB 视频无谓复制进报告包。
- 原始 Qwen 报告宣称曾观察到约 1fps 抽样帧，但无法从报告独立核验平台实际抽帧数及其覆盖率；“SUPPORTED”也不等于人工审定的事实真值。
- 部分报告使用的时间写法曾将 `MM:SS.s` 误当绝对秒数，**以一致性修订页中的更正为准**；对于仍然没有直接视频证据的字段保留 `UNCERTAIN`。
- 原始 Ego-MC 文字（包括反馈、指令和操作自述）**只提供辅助线索**，不能自动提升视频观察的确定性。
- 三个 Track 的任务/答案及 SOP 均尚未在本包构建；不得把这些候选报告直接作为最终正式评分 Ground Truth。

## 建议的后续产物（本包尚未生成）

`candidate_events_consolidated.json`：由 Codex 合并生成的统一、字段级别溯源的**候选**事件数据，并另存必要的冲突/待审清单。
