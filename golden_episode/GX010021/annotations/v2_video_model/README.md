# V2 Video-model Annotation（GX010021）

**状态：尚未实施（占位目录，当前无任何标注产物）**

## 用途

存放下一阶段由**视频理解模型**对原始视频 `source/GX010021.MP4` 独立理解后生成的结构化时序标注（事件、对象状态、依赖关系等），服务于 Benchmark 三个 Track（T1 Streaming QA / T2 Agentic Online Assistant / T3 State-dependent Procedure，见 `docs/` 总体设计 V1.0）。

## 与 V1 的关系

- `../v1_candidate/` 为历史基线：由多轮 AI 辅助报告整合而来的候选事实（CANDIDATE / NOT_REVIEWED），不代表人工 Gold。
- V2 由视频模型**独立**标注，再与 V1 交叉整合；两者冲突处需保留来源并标记，不静默覆盖任一方。

## 当前状态

- [x] 目录建立
- [ ] V2 Schema 设计
- [ ] 视频模型接入与标注生成
- [ ] 与 V1 候选标注的交叉整合

> 注意：本轮重构不生成任何新的事件、状态、依赖关系或评测题目。
