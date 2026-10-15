# GX010021 Showcase · Session 4A

这是后续学术汇报 HTML 的展示数据与真实画面包。它整理已有 V2 标注、Session 3 候选任务、历史证据及原视频帧，保留原 ID、来源指针、时间精度和不确定性。**不是新标注或 Gold 数据集**。

产物位于 `golden_episode/GX010021/showcase/`，包含 8 个时间轴节点、3 条事件/3 条状态/3 条关系和 1 条可选指导实例、T1-002/T2-003/T3-001 三个案例、3 组交叉核验差异及 12 张真实原帧。所有图片都是已有 PNG 的字节一致副本，没有新增抽帧、生成图像或事实内容修改。

## 文件

- [showcase_manifest.json](showcase_manifest.json)：机器可读入口及未改动的源记录快照。
- [showcase_notes.md](showcase_notes.md)：模块配对、中文叙述、候选边界、图片清单和证据缺口。
- [assets/](assets/)：12 张展示原帧，源路径、实际 PTS 秒数、用途、原 ID 和 SHA-256 见 asset_registry。
- [prepare_showcase.py](prepare_showcase.py)：确定性整理与简单校验脚本，不调用模型或网络，不修改源数据。
- [validation_report.json](validation_report.json)：校验记录及原 MP4 解码像素比对结果。

## 使用 manifest

`timeline` 直接提供标题、中文说明、实际帧锚点、图片 ID、Event/Evidence ID 与候选动作区间。`annotation_examples.display_links` 给出图像→事件→状态→关系的联动映射；在 `record_registry[原始ID]` 中读取 `key_fields` 和说明。

三个 `track*_case` 含准确的完整任务 ID（GX010021-V2- 前缀）、成熟度、Agent 公共输入/输出约束、Evaluator 私有触发/候选答案/评分门禁。其 `source_record` 为 Session 3 原任务全文，额外的 display 字段仅用于研究展示。T2 另含 7 项证据展示映射、6 条材料关系边、查询锚点、候选 unknown 字段和两种跨度口径。

`crosscheck_examples` 提供原统计和三组差异，各组同时保留历史候选、模型主张（如存在）及当前可支持的限定结论。所有源记录均有 `source.path/json_pointer/sha256`；`source_catalog` 固定本次使用的输入文件哈希。

路径约定：

- `asset_registry.relative_path` 相对于本 `showcase/` 目录，例如 `assets/K002_153.219733.png`。
- `source.path`、`original_image_path`、`source_video_path` 和 `historical_clip.path` 相对于仓库根目录。
- 图片的 `original_video_time_sec` 与 `source_pts × time_base` 对应。文件名中的请求 seek 时间不能替代实际原帧时间。
- `evidence_bindings` 区分精确快照、候选范围内帧及近似定位尾端后一帧内的关联；不修改历史定位以迎合图片时间。

最小读取示例：

```python
import json
from pathlib import Path

package = Path('golden_episode/GX010021/showcase')
data = json.loads((package / 'showcase_manifest.json').read_text(encoding='utf-8'))
assets = {a['asset_id']: a for a in data['asset_registry']}
for node in data['timeline']:
    image_path = package / assets[node['asset_ids'][0]]['relative_path']
    print(node['title_zh'], node['video_time_sec'], image_path)
```

后续网页应将“实际图片时间”和“候选事件范围”分别呈现，关系边标记为候选，保留 unknown/null 和 NOT_REVIEWED。源状态的历史观察区间不等于连续有效期。量具观察组不等于已确认的同一物理杯。

## 与原数据的关系

权威来源仍为 `../annotations/v2_video_model/`、`../tasks/v2_candidates/`、`../evidence/` 和 `../source/`。本包只做展示层选择与关联，不覆盖它们。原始 V1-only 候选仍未自动成为当前视频事实。

T1 两个检查点为 431.2308 / 445.211433 秒，对应各自准确原帧，仅支持局部候选相态。T2 查询为 680.212867 秒；527.012867 秒是候选证据定位跨度，选定实际图片跨度约 526.993134 秒，二者不证明历史必要性。T3 是限定规则负例候选，当前 NEEDS_EVIDENCE / DISABLED，不含虚构异常或报警/恢复真值。

本包含 Evaluator 私有候选参考，适合研究页面说明。不能将整个 manifest 作为被评测 Agent 输入。历史证据图的旧任务 ID 保留在源快照中，展示任务的关联采用 Session 3 的 GX010021-V2- ID。此处资产 ID 是素材导航标识，不是未来 Runner 的公开 observation ID。

## 可复现校验

从仓库根目录执行常规校验（Python 标准库即可）：

```powershell
python golden_episode/GX010021/showcase/prepare_showcase.py --validate-only
```

需要再次独立核对媒体 PTS 与像素时，安装环境中已有的 Pillow，并确保 ffmpeg / ffprobe 在 PATH 中：

```powershell
python golden_episode/GX010021/showcase/prepare_showcase.py --validate-only --verify-media
```

重建 manifest 与图片副本：

```powershell
python golden_episode/GX010021/showcase/prepare_showcase.py --verify-media
```

脚本只在本 showcase 目录写入产物，媒体验证使用临时目录，不修改 MP4、历史图、标注或任务。手写的 README/notes 不由重建脚本覆盖；若更新策展选择，需同步修改说明。校验报告会由每次运行覆盖，`media_verification.performed` 指示该次是否实际解码。

本次完整验证 PASS：12 张图片按原 MP4 的 PTS 解码，像素逐一一致；源记录快照、来源/片段文件及哈希、时间范围、原始 ID、任务定义和候选门禁一致。**这只确认来源与展示映射；没有完成人工语义裁决或正式评测准备。**

工作范围止于素材整理：本轮未修改 HTML、标注或任务，未开发 Runner / Evaluator / Baseline。
