# Long-Horizon Streaming Agent Benchmark

面向多 Episode、多任务、多条件的长程流式视频 Agent 评测，研究 T1 在线过程状态理解、T2 长程依赖推理和 T3 持续监测与及时干预。

当前 GX010021 是兼容保留的先导 Episode。P01 已完成四条件真实实验，P02 保持 **PENDING**。候选标注不等于人工 Gold；P01 批准记录以原实验文件为准。

- [研究与文档入口](docs/README.md)
- [数据索引与新视频接入](data/README.md)
- [实验版本和复现边界](docs/experiments.md)
- [目录整理、映射、验收和恢复](docs/maintenance/README.md)
- [现有标注流水线](annotation_pipeline/README.md)

```text
annotation_pipeline/         兼容保留的标注代码、schemas、providers、tests
benchmark/                   后续共用评测模块规划
data/episodes/<episode_id>/   新 Episode 规范和旧数据索引
golden_episode/GX010021/      旧 Episode 原位保留
experiments/icme2027_pilot/   P01 冻结实验和重构链；P02 待定
docs/                        当前研究设计、实验说明与整理记录
archive/                     历史材料索引
tests/                       测试入口说明
scripts/                     自动化整理验证
```

离线验收使用 Python 3.11 和现有 requirements.txt 中的依赖，需要完整本地资产及整理快照：

```powershell
python -X utf8 scripts/verify_layout.py --phase before
python -X utf8 scripts/verify_layout.py --phase after
python -X utf8 scripts/check_catalog.py
```

本次已执行，日志位于 `.local/layout-validation/`。重复执行前请将旧 phase 目录另名保留。流程在禁止网络的副本中运行单元测试、18 次 wire 请求重构、离线评分和报告生成。旧审计存在整理前就有的门禁失败，详情见验收报告，因此命令会返回非零退出码。

Git 保存代码、文档、schemas、结构化标注、Gold 和小型结果；原视频、原始响应、帧、凭据及恢复快照仅留本地并独立备份。**Git clone 不包含完整实验资产。** 本次未调用模型 API，也未启动下一轮实验。
