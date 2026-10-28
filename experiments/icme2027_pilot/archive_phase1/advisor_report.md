# GX010021 ICME 2027 最小实验：准备阶段报告

本报告只包含审计、候选适配和媒体准备。**真实先导实验尚未运行；无论文级结果，无正确率。**
本轮新增API调用0，输入/输出Token均0，产生API费用0；下一阶段费用未知。Session1/2既有返回仅为资产，不能算作本实验预测。

|任务|query秒|关键屏蔽秒|等时长对照秒|人工状态|执行状态|
|---|---:|---|---|---|---|
|P01|300|[174.0, 240.0]|[0.0, 66.0]|PENDING|NOT_RUN|
|P02|540|[390.0, 462.0]|[0.0, 72.0]|PENDING|NOT_RUN|

两题均来自T1。筛选明细见 selection_audit.jsonl；T3被排除，原因包括依赖无音轨不能核验的许可对话、第三枚蛋事实不明和没有确认的错误恢复。
延后检查点及YES/NO/UNKNOWN改写仅存在于本实验目录，原任务Schema和原文件保持不变。两题均有风险项，不能仅凭模型历史报告晋升Gold。

## 一次人工入口

打开 [review_checklist.md](review_checklist.md)。先看每题三个原始片段，再看已黑屏的历史和实际1FPS缩略图，核对无替代证据、无近期泄露。
可直接在聊天回复审核结论及证据区间，由工程师写入 review_decisions.jsonl；也可自己编辑该文件，再运行 validate --promote。
每项都通过才可APPROVED；否则REJECTED或INVALID。PENDING不会进入Gold。

## 程序验证与实际边界

本地ffprobe确认视频696.929567秒、854×480、30000/1001fps、无音轨；视频SHA-256与annotation_manifest一致。
所有裁剪MP4逐帧解码检查；实际1FPS采样复用原提取器和PTS校验。关键/对照掩码不仅时长相等，实际抽样帧数也一致。
原始文件保护哈希、Git HEAD及检查结果见 audit/。程序只能证明结构/文件/时间合法，不能证明答案、历史必要性或屏蔽充分性。
figures/preparation_status.png 为准备状态图，无模拟预测。
另见 [program_qa.json](program_qa.json) 与 [program_test_report.txt](program_test_report.txt)：6项离线门禁测试通过；201个既有资产哈希一致；黑屏历史的66/72个采样画面亮度全黑，H.264色度允许1级舍入；生成文本实际密钥扫描无泄露。首次严格色度检查的误拒及修正记录也保留在program_qa.json。
[audit_notes.md](audit_notes.md) 记录具体复用函数、历史API记录与当前限制。所有这些仍属于程序验证。

## 未完成与阻塞清单

1. 两题尚待研究者核验：A–F、1FPS可见性及屏蔽后全部历史无替代证据。
2. 尚无本实验人工Gold；tasks_gold.jsonl在至少一道APPROVED后才创建。
3. 凭据已存在且可加载，但未联网验证，不宣称API有效。
4. 按本轮先审计/准备再确认的要求，真实Agent harness、run、score在确认后继续实现和实测；当前CLI对run/score明确拒绝，不会伪造输出。
5. 下一阶段先跑一题三条件及recent_only，成功且原日志齐全后才扩展。不得将CRITICAL_MASK的正确UNKNOWN计为推理错误。

结果表 results.csv 中所有预测/指标均为空，execution_status=NOT_RUN；summary.json 的accuracy=null。
