# GX010021 定向展示素材包

建议阅读顺序：

1. `process/chronology.md`：先理解 V1→V2→Session3→Session4A 的真实历史链。
2. `process/stage_metrics.csv` 与 `audit/coverage_and_open_issues.md`：查看当前统计口径及与旧锚点的差异。
3. `cases/case_gallery.md`：导师口语化讲解四个案例。
4. `cases/*.json`、`annotation/state_transitions.json`、`annotation/relation_graph.json`：前端可直接消费的案例数据。
5. `tasks/all_task_definitions.json`：12 条完整设计定义，包含 3 条 UNSUITABLE。
6. `media/media_index.json`：12 张真实帧的 PTS、哈希、来源和任务映射。

可以演示：候选标注如何经过多轮核验与修订；T1 双检查点的局部状态；T2 长跨度材料候选链；T3 中许可替代和证据不足为何会造成假阳性。

不能声称：本 Episode 已有正式 Gold；V2 是全片逐帧人工审定；PILOT_CANDIDATE 可用于主榜评分；12 张展示帧等于 12 条已审定结论；长时间跨度已经证明历史必要性；原 annotations 文本在在线时刻一定可用。

原视频超过 80 MiB，未纳入 ZIP。详见 `media/video_pointer.json`。本包没有生成 HTML、没有重跑视频模型、没有新抽帧，也没有修改任何源文件。

注意：历史 V1 `reports/validation_results.json` 自身记录过一次输入 README 哈希变化，因此原始结果为 `passed=false`；本包原样归档该记录。本次导出验收则全部通过，二者是不同阶段、不同校验对象。
