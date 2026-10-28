# Episode 数据索引与新视频接入

| Episode | 状态 | 实际数据位置 | 索引 |
|---|---|---|---|
| GX010021 | P01 已完成；P02 PENDING | `golden_episode/GX010021/` | [episode.json](episodes/GX010021/episode.json) |

未来新 Episode 统一采用：

```text
data/episodes/<episode_id>/
├── episode.json                ID、版本、相对路径、源哈希、审核状态
├── raw/                        原视频和源标注，不可覆盖
├── annotations/
│   ├── candidates/<version>/   模型候选及生成来源
│   └── gold/<version>/         人工批准结果、裁决和来源
├── evidence/                   evidence_manifest.json 与帧/切片索引
├── tasks/<version>/            任务、状态及证据引用
└── metadata/                   ffprobe、采样规范和 SHA-256 清单
```

1. 选择唯一 episode_id，复制原视频到 raw，记录来源、SHA-256、时长、帧率和音轨。
2. 新建 episode.json，统一使用相对仓库根的路径，避免个人绝对路径。
3. 复用 annotation_pipeline，显式指定输入与输出，将候选按版本写入 candidates。候选不得自动提升为 Gold。
4. 人工审核后，才在 gold 保存批准结果，记录审核人、时间、证据和裁决。未审核保持 PENDING。
5. evidence_manifest 记录源视频哈希、相对路径、PTS/时间区间、采样参数及帧哈希；任务引用确切 Gold 与证据版本。
6. 实验保存到 `experiments/<study>/runs/<run_id>/`，记录 episode_id、task_id、condition、协议与代码版本、输入、记忆链、请求和响应；禁止覆盖旧 run。真实付费推理另行授权。

Git 提交 manifest、小型 metadata、结构化候选、人工 Gold、任务与证据索引。原视频、帧、切片、原始模型运行/响应、账本与凭据仅保留本地并独立备份；raw 中源标注也按本地原始资产保管，必要的可分享来源说明可放 metadata。既有已跟踪 PNG 不取消跟踪。

GX010021 的 manifest 仅定位旧数据，不复制资产，不把候选视为 Gold。
