# GX010021 P01 真实先导实验报告 v1

生成时间：2026-10-28T13:09:57+08:00。问题：**截至视频第 300 秒，是否曾使用电动搅拌器对容器内材料进行搅拌？**

## 审核与输入

研究者在本会话明确APPROVED原视频证据：174–240秒电动搅拌，屏蔽后虽材料均匀但不能确定搅拌方式，240–300秒无新的动作或等价证据，0–66秒对照无关。事实Gold=YES；FULL/CONTROL有直接证据，CRITICAL/recent证据不足。UNKNOWN为证据适当响应，未预设模型输出。
工程检查实际1FPS保留36张199–235秒动作帧，全部位于关键mask；关键/对照均66张。实际输入帧与掩码见mask_manifest_applied_v1.jsonl及runs/p01-v1/*/seg-*/input_manifest.json。
三个rolling条件各从空记忆独立观察5窗；recent只接收240–300秒；问题只在最后窗口提供。每个API输入含60帧，原PTS<300；原始API视频字段同时携带fps=1。记忆字符上限4096、输出上限1536tokens、temperature0；完整提示、参数、模型别名及代码哈希见run_manifest。

## 观察结果（真实原始响应）

四组全部完成。

|条件|执行|答案|answerability|证据适当回答|无依据确定回答|输入 / 输出tokens（含全部窗口尝试）|API耗时秒|
|---|---|---|---|---|---|---|---|
|FULL|SUCCESS|YES|ANSWERABLE|True|False|97052 / 7390|266.609|
|CRITICAL_MASK|SUCCESS|NO|ANSWERABLE|False|True|67798 / 2746|109.813|
|CONTROL_MASK|SUCCESS|YES|ANSWERABLE|True|False|68031 / 2971|129.373|
|recent_only|SUCCESS|NO|ANSWERABLE|False|True|13153 / 161|22.063|

共预留18次推理尝试，收到18条HTTP响应/传输记录。输入246034、输出13268tokens，API累计耗时527.858秒。费用估计与实际账单均null：当前地域/别名单价未可靠核实；硬上限20次尝试，本地预留4.50元仅为额度约束，不是供应商账单保证。重跑可复用同条件前缀，不产生新请求；score完全离线重解析原响应。

### FULL

```json
{
  "answer": "YES",
  "answerability": "ANSWERABLE",
  "evidence_intervals_sec": [
    [
      68.0,
      84.0
    ]
  ],
  "reason": "在68.0–72.0秒，右手按压开关启动电动打蛋器，搅拌头高速旋转，开始搅打盒中混合液；72.0–84.0秒持续搅打，混合液变浅黄、起泡并最终呈均匀乳浊状。此过程明确显示电动搅拌器已用于搅拌容器（透明塑料盒）内的材料。该事件发生在300秒前，且有直接视觉证据支持。"
}
```

原始响应：[seg-0000](runs/p01-v1/FULL/seg-0000/attempt-000.response.json), [seg-0001](runs/p01-v1/FULL/seg-0001/attempt-000.response.json), [seg-0002](runs/p01-v1/FULL/seg-0002/attempt-000.response.json), [seg-0003](runs/p01-v1/FULL/seg-0003/attempt-002.response.json), [seg-0004](runs/p01-v1/FULL/seg-0004/attempt-000.response.json)
### CRITICAL_MASK

```json
{
  "answer": "NO",
  "answerability": "ANSWERABLE",
  "evidence_intervals_sec": [
    [
      0.0,
      58.0
    ]
  ],
  "reason": "A white electric hand mixer is visible on the counter throughout the observed frames (0.0–58.0s), but it is never picked up or used. The person only cracks eggs into the container, measures brown sugar, and handles milk—no stirring or mixing action with the hand mixer occurs in any visible frame. Since all frames up to 58.0s are the only ones with visual data, and no later frames (including the black frames from 180–240s and 240–300s) show any use of the mixer, we can conclude it was not used by 300s."
}
```

原始响应：[seg-0000](runs/p01-v1/CRITICAL_MASK/seg-0000/attempt-000.response.json), [seg-0001](runs/p01-v1/CRITICAL_MASK/seg-0001/attempt-000.response.json), [seg-0002](runs/p01-v1/CRITICAL_MASK/seg-0002/attempt-000.response.json), [seg-0003](runs/p01-v1/CRITICAL_MASK/seg-0003/attempt-000.response.json), [seg-0004](runs/p01-v1/CRITICAL_MASK/seg-0004/attempt-000.response.json)
### CONTROL_MASK

```json
{
  "answer": "YES",
  "answerability": "ANSWERABLE",
  "evidence_intervals_sec": [
    [
      180.013,
      224.004
    ]
  ],
  "reason": "在180.013–224.004秒区间内，视频明确显示操作者右手持白色手持电动搅拌器（带双金属打蛋头），将打蛋头插入透明塑料盒中并启动搅拌，混合液被快速搅动、产生气泡与漩涡，体积略增、质地蓬松；219–224秒将搅拌器放回台面左侧。此为直接可见的电动搅拌器使用行为。截至300秒，无证据表明该动作未发生或被撤销。"
}
```

原始响应：[seg-0000](runs/p01-v1/CONTROL_MASK/seg-0000/attempt-000.response.json), [seg-0001](runs/p01-v1/CONTROL_MASK/seg-0001/attempt-000.response.json), [seg-0002](runs/p01-v1/CONTROL_MASK/seg-0002/attempt-000.response.json), [seg-0003](runs/p01-v1/CONTROL_MASK/seg-0003/attempt-000.response.json), [seg-0004](runs/p01-v1/CONTROL_MASK/seg-0004/attempt-000.response.json)
### recent_only

```json
{
  "answer": "NO",
  "answerability": "ANSWERABLE",
  "evidence_intervals_sec": [
    [
      0.0,
      299.032067
    ]
  ],
  "reason": "从视频开始到第299秒，画面中可见一台白色手持电动搅拌器放置在台面左侧（例如0:00、0:15等帧），但从未被拿起或用于搅拌任何容器内的材料。所有操作仅涉及手动倾倒面粉（如0:34–0:42）和用勺子/量杯转移物料（如0:48–0:52），未见搅拌动作。因此，截至300秒，电动搅拌器未被使用。"
}
```

原始响应：[seg-0004](runs/p01-v1/recent_only/seg-0004/attempt-000.response.json)

## 研究推断（与观察分开）

CRITICAL_MASK在研究者审核为证据不足的输入上仍作确定回答。这属于无充分依据的确定性；若理由把均匀材料、工具存在等当成使用证据，则与搅拌结果/搅拌方式混淆一致，但须结合原理由和窗口记忆逐项检查，不能仅由YES断言机制。
Recent-only作确定回答，表明当前窗口/先验触发了超出审核证据的结论；是否混淆材料均匀与电动搅拌需看其实际理由。

不能把工具可见、材料变均匀等同于使用过电动搅拌器。自动字段只判断输出枚举、证据充分性审核下的合适回答，以及引用区间是否有可见输入帧；不自动把区间合法当作语义支持。具体理由的语义支持、记忆中的推断来源和混淆归因单列复核，不强行给语义准确率。

## 是否可扩展

工程层面：四条件端到端路径已跑通，可作为后续小规模先导流程的基础。当前不建议直接批量扩展：需要先固定截断恢复策略、解决原时间轴定位和记忆归因，再用少量独立视频验证。
研究层面：本实验只有1个视频、1道题、每条件1次，不足以支持跨视频泛化或论文级结论。关键mask66秒跨窗且清除工具安装，存在视觉空白/信息量效应；对照时长与采样数匹配但所处阶段不同。1FPS可能遗漏短事件；模型别名未固定权重；文本记忆压缩可能遗忘。扩展前需多视频独立题目审核、必要性/替代线索检查、不同历史跨度与mask位置对照、重复运行及样本量规划。当前可以扩展的是小规模受控先导流程，不是直接汇报论文级基准成绩。

## 程序测试、未完成与失败

离线测试见offline_tests_v1.txt和offline_qa_v1.json；不使用模拟模型预测。原文件哈希检查见audit/integrity_check.json。原始响应、request_id、精确提示、窗口记忆、帧及哈希均在runs/p01-v1/。
当前失败清单：[]。历史错误保留runs/p01-v1/*/error-*.json及attempt日志，不因续跑成功删除。P02继续PENDING。供应商实际账单未知，语义证据支持需要复核；无论文级结果。

FULL在180–240秒窗口两次返回HTTP200但finish_reason=length，未当作有效记忆使用。统一的、与答案无关的恢复修订只提高该触发情形的max_tokens至4096；提示、帧、输入记忆及4096字符记忆边界均不变，最终回答仍1536tokens。修订见runtime_amendment_v1_at_execution.json。18次尝试包括这两次失败及恢复，不能按16次计费。该非对称触发需要在后续固定协议中事先声明，当前不是完全无修订的确认性实验。

## 本次证据链逐项诊断（工程分析，非新增人工Gold）

- FULL答YES，但引用[[68.0, 84.0]]，没有命中已确认199–235秒动作采样。其窗口记忆把搅拌记到68–84秒；原记录保留不作事后时间纠正。因此事实枚举正确，证据定位不可靠，不能计为已验证的证据支持。
- CRITICAL_MASK明确用‘未观察到使用’支持NO，未正确保留黑屏中的未知。原理由还称240–300秒为黑帧，而实际该窗60帧全部可见且与其他三组逐帧哈希一致。这是输出对输入可见性/时间覆盖的错误描述，不能误称输入真正缺失。它引用的0–58秒虽属于可见历史，仍不足以证明整段未使用。
- Recent-only只收到240–300秒，却声称从视频开始到299秒均未使用，引用[[0.0, 299.032067]]。该区间超出实际供给历史，自动时间覆盖检查为False；理由又用窗口内0:34–0:42等局部时间描述加粉，表明局部时间与原时间轴发生混用。
- CONTROL_MASK答YES，引用区间与已确认电动搅拌采样有交集，且FULL/CONTROL答案一致；这只表明本题无关屏蔽没有改变枚举答案。理由所述具体起止/放回时刻仍有偏差，因此语义支持字段保留复核标记。

本次没有直接观察到‘只因材料均匀，就判定用过电动搅拌器’这一特定模式：两组证据不足条件都输出了NO。更明确的现象是把未见动作当作未发生，以及原时间定位/历史覆盖描述错误。FULL的YES伴随错误证据时间，不能仅凭答案翻转证明必要历史状态已被可靠利用；这些都是外部行为诊断，不能直接断言模型内部机制。

**扩展判断：工程输入、隔离、断点和日志链路可以复用；当前测量协议不宜直接批量扩展为正式实验。** 先固定记忆压缩/截断恢复，约束记忆中的原时间引用（如结构化event与source-frame引用），并在独立视频上验证证据不足判断及定位评分。对照应继续匹配采样数，并补充mask所处阶段的控制。当前运行使用可变模型别名，能复现输入与离线评分，不能保证未来云端重新推理逐字一致。
