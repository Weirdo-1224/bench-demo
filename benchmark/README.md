# 共用评测模块规划

本次只建立职责入口，不搬迁先导代码，不增加空实现。

后续按实际复用需求提取 Episode manifest 读取、任务与条件定义、流式调度、受控记忆、离线评分和报告模块。先支持显式 Episode 配置，再以 P01 精确 replay 验证兼容性。

benchmark 可复用 annotation_pipeline 的媒体与校验能力；Episode 数据不承载共用 Python 实现；实验目录保存协议、配置与结果。历史 pilot.py、runtime.py 和三份 code_snapshot 保持原位，不用新模块覆盖冻结代码。
