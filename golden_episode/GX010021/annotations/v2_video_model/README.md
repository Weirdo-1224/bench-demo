# V2 Video-model Annotation（GX010021）

**Session 2 已完成真实原生全片分析与历史整合；所有产物为 CANDIDATE / NOT_REVIEWED。**

两次 Qwen3-VL-Plus 分别输入完整原 MP4，独立结果保存后才读取 V1/源文本。模型细节仍有遗漏与错误；全片输入成功不代表事实已确认。

主要入口为 [full_video_report.md](full_video_report.md)、[crosscheck_report.md](crosscheck_report.md) 和 [annotation_manifest.json](annotation_manifest.json)。统一数据包括 events.json、objects.json、procedure.json、relations.json、anomaly_candidates.json、evidence_index.json；global_analysis.json 为独立模型输出加透明结构修复，语义未被历史覆盖。

统计：59 条统一事件候选、28 个对象/材料/观察组 ID、138 条状态主张、24 条关系、55 条来源文本、7 项未确认 L5 候选。已确认错误与 Gold 均为0。计数细节及来源限制见报告。

原始响应、完整中性提示词、配置、调用预留、原帧/PTS 与修复记录位于 runs/session2-full-video/，已被 Git 忽略。两次推理共输入67610、输出23378 Token；按未扣缓存价格估算0.452085 CNY，实际账单未知。

来源校验见 validation_report.json 和 integrity_report.json。独立全局观察、历史候选、最终整合各自可回溯，未重启逐条裁决。V1/source/旧任务与历史报告保持哈希一致；本轮未产生正式评测题目、Runner、Evaluator、Baseline 或其他 Episode 标注。

运行和离线复用指令见 [annotation_pipeline/README.md](../../../../annotation_pipeline/README.md)。Session 1 两个 Smoke 窗口继续保留在原运行目录，未覆写。
