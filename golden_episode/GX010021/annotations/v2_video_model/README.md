# V2 Video-model Annotation（GX010021）

**状态：Session 1 最小流水线与两个真实短窗口的 Qwen API Smoke Test 均已通过；已生成 13 条未融合的 CANDIDATE 观察，尚未完成人工复核。**

## 用途

存放由**视频理解模型**对原始视频 `source/GX010021.MP4` 独立理解后生成的结构化候选时序标注。三个 Track 以总体设计 V1.0 为准：T1 过程状态理解、T2 长程过程依赖推理、T3 持续监测与及时干预。Session 1 只实现 L0 来源和 L2 观察事件契约，不生成状态整合、依赖图或 Track 任务。

## 与 V1 的关系

- `../v1_candidate/` 为历史基线：由多轮 AI 辅助报告整合而来的候选事实（CANDIDATE / NOT_REVIEWED），不代表人工 Gold。
- V2 由视频模型**独立**标注，再与 V1 交叉整合；两者冲突处需保留来源并标记，不静默覆盖任一方。

## 当前状态

- [x] 目录建立
- [x] Session 1 L0/L2 Schema、可替换 Provider 和 Qwen API 适配实现
- [x] 两个真实短窗口抽帧、源 PTS 独立核对、Dry-run、单元测试
- [x] Qwen 真实认证调用与候选观察生成（两个窗口、2 次调用、4 + 9 条候选）
- [ ] 与 V1 候选标注的交叉整合

运行中间产物位于本目录下 `runs/`（已忽略，不入库）。成功运行 ID 为 `session1-6d141472d332d26a2a86`。运行指令见项目级 `annotation_pipeline/README.md`，最新结果见 `annotation_pipeline/SESSION1_SMOKE_RETRY_REPORT.md`，初次缺密钥记录仍保留。候选中存在意图用语、材料身份和读数待复核问题；没有合成事件混入此目录。
