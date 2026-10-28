# 只读资产审计补充

本轮审计只读原资产，新文件只写`experiments/icme2027_pilot/`。冻结基准为Git `d0db40fb7a7d7dd73edab546505b22b6d4b71eee`，用户原有未跟踪`_showcase_export/`不处理。完整文件哈希与真实机器路径见`audit/audit.json`及`audit/original_hashes.json`。

|资产|实际相对路径|审计结论与复用|
|---|---|---|
|原片|golden_episode/GX010021/source/GX010021.MP4|本地存在，91,608,663字节；哈希与annotation_manifest一致；视频+timecode轨，无音轨|
|Session1来源任务|golden_episode/GX010021/tasks/v1_candidates/pilot_task_candidates.json|8条任务，T1 4条、T3 1条；未确认Gold，历史路径字段有旧路径，使用当前实际路径|
|Session2整合|golden_episode/GX010021/annotations/v2_video_model/annotation_manifest.json|CANDIDATE；human_review=NOT_REVIEWED，Gold=0|
|Session2报告|golden_episode/GX010021/annotations/v2_video_model/full_video_report.md|两次真实全片返回，出现三蛋及完全融化误判；不能直接当真值|
|Session2交叉对照|golden_episode/GX010021/annotations/v2_video_model/crosscheck_report.md|保留蛋数、固块、糖入料时刻等冲突；局部原帧只证明局部，不证明连续事件|
|Session3任务|golden_episode/GX010021/tasks/v2_candidates/task_candidates.json|12条定义，T1 4条、T3 4条；均非人工Gold；13条跨版本T1/T3筛选记录已输出|
|Session3可行性|golden_episode/GX010021/tasks/v2_candidates/task_feasibility_report.md|T1局部题大多近期可答；T3缺错误/规则时间；仅适配两道T1作延后问答|
|既有帧API|annotation_pipeline/providers/qwen.py|QwenProvider.build_request/invoke/extract_content；严格4+帧约束，POST无重定向；下阶段复用|
|既有原生API|annotation_pipeline/providers/qwen_native.py|私有临时上传可用，但服务端采样PTS未知；本试验优先可审计帧序列|
|凭据|annotation_pipeline/credentials.local.json|存在且load_api_key可加载，禁止输出值；本轮未联网核验；已冻结文件内容哈希|
|抽帧与时间|annotation_pipeline/media.py|已实际复用extract_frames/verify_frames/plan_segments；原PTS、1FPS、哈希检查|
|媒体探测|annotation_pipeline/inspect_video.py|已实际复用inspect_video；原片元数据/哈希及首秒解码|
|断点与预算|annotation_pipeline/calls.py|call_or_reuse、ledger：请求前预留、持久attempt、429/5xx重试、超时未知计费阻断；下阶段评估复用。原账本按run_dir计数，不够直接保证跨run-id总上限，需本目录内单独封口与独占锁|

Session1调用记录见`docs/SESSION1_SMOKE_RETRY_REPORT.md`：2026-10-10两个真实帧序列窗口成功；Session2原响应引用见manifest的`independent_passes`。这些是历史资产，不是本试验FULL/CRITICAL/CONTROL预测。不存在可以直接复用为当前实验Gold的已批准题目。

当前依赖已具备：Python 3.11、requests、PyYAML、Pillow、jsonschema、FFmpeg、ffprobe；matplotlib未安装，准备状态图使用Pillow生成，不引入额外依赖。没有安装新软件。

工程师离线目视检查了P01的180–240/240–300秒缩略表、P02的360–420/420–480秒缩略表，以及约463/465秒原采样帧。该检查支持把两题交付人工核验，但不构成人工Gold：P01近期可见静置搅拌器和液体外观，P02关键屏蔽结束后仍见玻璃容器转移。需研究者判断这些是否是明显泄露/替代证据；目前均PENDING，不宣称残留证据检查已在语义上通过。

所有片段逐帧解码通过；`verify_preparation.py`另检查黑屏历史的采样画面整个图像YUV极值，以及生成文本是否含实际密钥值。程序记录见`program_qa.json`。这些检查都属于程序验证，不是先导实验。
