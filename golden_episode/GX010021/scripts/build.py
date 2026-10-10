"""Merge archived candidate reports. Reads metadata only; never decodes video frames."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

EP = Path(__file__).resolve().parent.parent
ROOT = EP.parents[1]
ANN = EP / "annotations" / "v1_candidate"
REP = EP / "reports"
REPORTS = EP / "annotation_reports"
BASE = "annotation_reports/candidate_events_v1.md"
VERIFY = "annotation_reports/verification_report.md"
CONSISTENCY = "annotation_reports/consistency_revision.md"
CROSS = "annotation_reports/crosscheck_report.md"
README = "annotation_reports/README.md"
INPUT_HASHES = {
    BASE: "d902836c5f22515682189559348f052853a7fa5c6aac2f8ebd779e41b88a43c4",
    VERIFY: "76128353fc3168eac4f358a0d29067c3f614bbe3640caac8c040f51eae4a63d5",
    CONSISTENCY: "4d37d9b5d40374b1a32cb95cbacdccc5b26766b82eb00cf81451ad7228a0e2e7",
    CROSS: "5d0cab2dcf558cbd0ce92061a9bd91f9fdef7aa55c935a447208be9452d58026",
    README: "72b76996ea365a5fbee780b396f45efa8340d2567e7c4aec999a3f27b2fc89c1",
    "source/annotations.json": "88183e371dac0948378b723aa4c2ca102a2597770ed518805d52f180cd780527",
    "source/GX010021.MP4": "fe4a11550bf2aea09a39ce1e72dba4633adc8c8b6a540e9894696e8b2ed1c8f9",
}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return (EP / path).read_text(encoding="utf-8-sig")


def table(path, section, pattern):
    lines = read(path).splitlines()
    active = False
    rows = {}
    for line_number, raw in enumerate(lines, 1):
        if raw.startswith("## "):
            active = raw.startswith(section)
        if active and raw.startswith("|"):
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            if re.fullmatch(pattern, cells[0]):
                if cells[0] in rows:
                    raise ValueError(f"Duplicate source row: {path}:{line_number}")
                rows[cells[0]] = {"cells": cells, "line": line_number, "raw": raw}
    return rows


def ref(path, line=None, section=None):
    result = {"path": path}
    if line is not None:
        result["line"] = line
    if section is not None:
        result["section"] = section
    return result


def seconds(value):
    parts = [float(p) for p in value.split(":")]
    return round(sum(p * 60 ** i for i, p in enumerate(reversed(parts))), 3)


def stamp(value):
    ms = round(value * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"


def time(start, end=None):
    end = start if end is None else end
    return {"start_sec": start, "end_sec": end,
            "start_hms": stamp(start), "end_hms": stamp(end)}


def envelope(artifact):
    return {"$schema": "./schema.json", "schema_version": "1.0",
            "episode_id": "GX010021", "artifact": artifact,
            "data_status": "CANDIDATE", "human_review": "NOT_REVIEWED"}


def write(name, value):
    (ANN / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# Corrected absolute-second evidence, transcribed from consistency_revision §1.
# E001–E034 retain genuine seconds; NEVER apply a numeric threshold conversion.
VISUAL = {
 1: [(0,9,"视角由水槽区移至灶台")],
 2: [(10.2,14.2,"手指按压面板"),(15.2,15.2,'面板显示 "100"')],
 3: [(15,19,'面板显示保持 "100"')],
 4: [(23.2,27.2,"手持白碗、翻看底部并放回叠位")],
 5: [(30.2,40.2,"持嵌套容器、置于台面中央并扶正调整")],
 6: [(44.2,47.2,"触蛋盒并掀起盒盖")],
 7: [(48.2,48.2,"报告称左手见两枚、右手取蛋；逐次过程遮挡"),
     (52.2,54.2,"报告称手持三枚可见；不独立裁决累计取蛋次数")],
 8: [(53.2,54.2,"右手扶盖侧；盖仍呈开启平摊状")],
 9: [(57.2,59.2,"台面两枚蛋、手持一枚")],
 10: [(62.2,62.2,"掰蛋时见蛋黄下落"),(65.2,66.2,"容器一个蛋黄、台面一份蛋壳")],
 11: [(69.2,73.2,"掰第二枚蛋"),(76.2,76.2,"容器两个蛋黄")],
 12: [(78.2,82.2,"手持第三枚蛋有磕/掰样动作"),(81.2,84.2,"容器仍两个蛋黄"),
      (83.2,83.2,"右侧似见第三份蛋壳；报告措辞不确定，不能确证数量")],
 13: [(86.2,89.2,"持蛋走至蛋盒处、伸手，随后空手离开；入盒瞬间不可见")],
 14: [(95.2,97.2,"持灰蓝糖袋并撑开袋口")],
 15: [(99.2,102.2,"取黑色量杯查看")],
 16: [(112.2,118.2,"糖袋向杯倾倒，杯中见褐色颗粒")],
 17: [(120.2,121.2,"糖袋放在右侧")],
 18: [(128.2,131.2,"杯中糖倾入容器，糖堆覆在蛋黄上")],
 19: [(135.2,137.2,"双手在糖袋/粉盖罐处整理、按压；具体内容不可裁决")],
 20: [(140.2,145.2,"手持黑色量杯查看"),(144.2,144.2,'杯柄标签 "1/4 CUP"')],
 21: [(147.2,150.2,"持牛奶盒并拧黄盖")],
 22: [(153.2,156.2,"牛奶盒倒奶入杯，一次可见量取")],
 23: [(159.2,161.2,"杯中奶倾入容器，台面见白色液滴")],
 24: [(168.2,173.2,"拧黄盖并把牛奶盒放回灶侧")],
 25: [(176.2,178.2,"手持两根金属搅拌棒"),(181.2,192.2,"逐根装入打蛋器")],
 26: [(194.2,197.2,"翻转打蛋器查看背面按键")],
 27: [(199.2,199.2,"搅拌棒进入液面"),(200.2,234.2,"搅拌、混合液渐均匀"),
      (235.2,235.2,"搅拌棒提离")],
 28: [(236.2,238.2,"打蛋器置左侧台面")],
 29: [(241.2,241.2,"持空量杯"),(244.2,245.2,"手伸向靠墙白盒；接触部分可见")],
 30: [(260.2,267.2,"开吊柜、取牛皮纸面粉袋、关门")],
 31: [(270.2,281.2,"开袋并向杯倒粉")],
 32: [(287.2,291.2,"量杯倒粉入混合容器，出现白色粉堆")],
 33: [(293.2,300.2,"视角徘徊，所报抽样帧未见立即搅拌")],
 34: [(303.2,318.2,"拿箔包、撕膜剥纸，黄油裸露")],
 35: [(329.2,331.2,"黄油置于鱼形垫上玻璃容器内")],
 36: [(340.2,342.2,"开微波炉门，把玻璃容器放入转盘")],
 37: [(345.2,361.2,"多次按面板；设定时长读数不可确证")],
 38: [(375.2,389.2,"视角停留等待")],
 39: [(390.2,390.2,'显示 "End"'),(393.2,399.2,"容器内黄色液体和固态块共存")],
 40: [(405.2,406.2,"容器放回微波炉转盘")],
 41: [(409.2,412.2,"按键"),(413,425,"门闭等待；与426.2s开门帧的边界约±1s")],
 42: [(429.2,429.2,"第二次取出时液体为主、见浅色块影"),
      (431.2,432.2,"黄液中仍明确可见浅色固态块")],
 43: [(437.2,443.2,"取黑色勺状工具"),(444.2,459.2,"搅动固液混合黄油，仍见固块")],
 44: [(464.2,467.2,"玻璃容器中黄油倾入混合容器"),(470.2,470.2,"倒后玻璃容器空置于灶面")],
 45: [(473.2,528.2,"第二次电动搅拌，混合物渐稠")],
 46: [(530.2,536.2,"端混合容器观察")],
 47: [(542.2,545.2,"折叠黄油包装废弃物并置鱼形垫")],
 48: [(555.2,559.2,"取油瓶、拧绿盖")],
 49: [(560.2,562.2,"油流/油滴进入模底"),(567.2,579.2,"持模倾斜旋转，内壁油膜不可辨")],
 50: [(583.2,589.2,"端容器查看面糊")],
 51: [(595.2,602.2,"袋直接向混合容器倒粉"),(603.2,603.2,"表面新增白粉堆")],
 52: [(605.2,629.2,"第三次电动搅拌"),(630.2,630.2,"面糊表面光滑")],
 53: [(633.2,641.2,"混合容器面糊倾入烤模"),(645.2,677.2,"黑色工具刮容器壁")],
 54: [(680.2,680.2,"糖袋已在敞口粉盖罐内；黑色刮刀留在近空混合容器内"),
      (681.2,683.2,"持粉盖、压盖，罐闭合；没有证明糖袋本段插入")],
 55: [(687.2,691.2,"开烤箱门、放模入架、关门")],
 56: [(693.2,696.2,"灶台/台面静置；玻璃容器仍在灶面")],
}

OBJECTS_BY_EVENT = {
 1: [],2:["O14"],3:["O14"],4:["O19"],5:["O01"],6:["O02","O20"],
 7:["O02","O20"],8:["O20"],9:["O02"],10:["O02","O03","O01","O15"],
 11:["O02","O03","O01","O15"],12:["O02","O03","O01","O15"],13:["O02","O20"],
 14:["O04"],15:["O05"],16:["O04","O05"],17:["O04"],18:["O05","O01","O15"],
 19:["O05","O04","O18"],20:["O05"],21:["O06"],22:["O06","O05"],
 23:["O05","O01","O15"],24:["O06"],25:["O07"],26:["O07"],
 27:["O07","O01","O15"],28:["O07"],29:["O05","O22"],30:["O08"],
 31:["O08","O05"],32:["O05","O01","O15"],33:["O01","O15"],
 34:["O09","O21"],35:["O09","O10"],36:["O09","O10","O11"],
 37:["O09","O10","O11"],38:["O11"],39:["O09","O10","O11"],
 40:["O09","O10","O11"],41:["O09","O10","O11"],42:["O09","O10","O11"],
 43:["O09","O10","O16"],44:["O09","O10","O01","O15"],
 45:["O07","O01","O15"],46:["O07","O01","O15"],47:["O21"],
 48:["O13"],49:["O13","O12"],50:["O01","O15"],51:["O08","O01","O15"],
 52:["O07","O01","O15"],53:["O01","O15","O12","O17"],
 54:["O18","O04","O01","O17"],55:["O12","O14","O15"],56:["O14","O10"],
}

DESCRIPTIONS = {
 2:'手指多次按压灶台/烤箱面板；随后显示为 "100"，显示语义和按键因果未确证。',
 3:'视角停留，面板显示保持 "100"；不能据此确认温度或预热完成。',
 7:'从蛋盒取蛋，报告称手持最终可见三枚；累计取出三枚为跨帧推断，逐次动作部分遮挡。',
 8:'右手扶/碰蛋盒盖后离开；所报帧中盖仍呈开启平摊状，是否短暂扣合未知。',
 12:'对第三枚蛋有磕/掰样动作，容器仍见两个蛋黄；蛋是否破损、是否产生第三份蛋壳未知。',
 13:'持第三枚蛋回到蛋盒处、伸手放下后空手离开；是否进入盒内未确证。',
 19:'放回量杯；双手在糖袋与粉盖罐处整理/按压，糖袋折口和具体收纳动作未确证。',
 20:'手持/比对黑色量杯，杯柄可见 "1/4 CUP"；R19 自述寻找半杯量杯的用途另记为文本线索。',
 27:'搅拌棒进入混合液，第一次电动搅拌；蛋、糖、奶由分层渐变为淡黄均匀液，随后提离。',
 29:'手持空量杯，伸手触向靠墙白色纸盒；接触部分可见，意图和盒内物未知。',
 37:'关门后多次按面板，构成第一次加热流程；面板读数与实际设定时长未确证。',
 39:'显示 End 后开门取出查看；玻璃容器中黄色液体与固态黄油块共存，部分融化。',
 41:'关门按键，构成第二次加热流程，随后等待；设定时长和运行读数未确证。',
 42:'第二次开门取出玻璃容器并关门；黄油以黄色液体为主，仍可见浅色固态块，残留比例未知。',
 43:'以黑色勺/量勺状工具搅动玻璃容器内固液混合黄油；抽样帧仍见固块，工具同一性及最终融化程度未知。',
 44:'玻璃容器中的黄油倒入含面粉的混合容器；倒后玻璃容器空置于灶台黑面。倒入时是否含固块及精确残留量未知。',
 49:'向烤模模底倒少量油，再持模倾斜旋转；内壁油膜是否形成与覆盖范围未确证。',
 53:'面糊倾入烤模，并用黑色柄刮刀/勺状工具刮擦混合容器壁底，将残留面糊刮入模；容器近空。',
 54:'盖回粉色罐盖；糖袋已位于罐内、黑色刮刀留在近空混合容器内仅记录为对象观察状态。',
 55:'打开烤箱门，将盛面糊的烤模放入烤架，关门；实际温度和预热完成未确证。',
}
ACTION_OVERRIDES = {7:"取蛋（累计计数待复核）",8:"扶/碰盒盖后离开",12:"操作第三枚蛋（是否破损未知）",
 13:"持蛋至蛋盒处并放下",19:"放回量杯并整理/按压",20:"手持/比对量杯",29:"持量杯、伸触纸盒",
 37:"关门、按键（第一次加热流程）",41:"关门、按键（第二次加热流程）",
 42:"第二次开门取出（仍有固块）",43:"搅动固液混合黄油",49:"倒油并倾斜旋转烤模",54:"盖回粉色罐盖"}
BOUNDARIES = {27:(199,235),34:(303,319),49:(560,581),51:(595,604),53:(633,679),55:(687,692)}
UNCERTAIN_EVENTS = {7,8,12,19,20,29,37,41,43,49}


def build():
    for path, expected in INPUT_HASHES.items():
        if digest(EP / path) != expected:
            raise ValueError(f"Input differs from initial merge manifest: {path}")
    write("schema.json", make_schema())
    baseline = table(BASE, "## B.", r"E\d{3}")
    object_rows = table(BASE, "## C.", r"O\d{2}")
    verification = table(VERIFY, "## B.", r"E\d{3}")
    mapping = table(CROSS, "## B.", r"R\d{2}")
    assert list(baseline) == [f"E{i:03}" for i in range(1,57)]
    assert list(object_rows) == [f"O{i:02}" for i in range(1,16)]
    assert list(mapping) == [f"R{i:02}" for i in range(1,56)]
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=index,codec_type,codec_name,duration,avg_frame_rate,nb_frames,width,height",
        "-of", "json", str(EP / "source/GX010021.MP4")], text=True, encoding="utf-8"))
    video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    events_doc = envelope("events")
    events_doc["sources"] = [
        {"path": p, "sha256": h, "bytes": (EP / p).stat().st_size,
         "role": "video_metadata_only" if p.endswith("MP4") else
                 "ego_mc_text_only" if p == "source/annotations.json" else "archived_ai_report",
         "priority": {BASE:1,VERIFY:2,CONSISTENCY:3,CROSS:4,README:5}.get(p,0)}
        for p,h in INPUT_HASHES.items()]
    events_doc["video"] = {
        "path": "source/GX010021.MP4", "duration_sec": float(probe["format"]["duration"]),
        "metadata_method": "ffprobe (container/stream metadata only; no frames decoded)",
        "video_stream": video_stream, "reported_evidence_range": time(0.2,696.2),
        "reported_sampling_fps": 1, "sampling_verified": False,
        "uncovered_tail_sec": round(float(probe["format"]["duration"])-696.2,6)}
    events_doc["limitations"] = [
        "所有视觉证据是历史 AI 报告所述抽样帧观察；本次未观察视频、未重新标注、未调用视频模型。",
        "报告实际抽帧数量、覆盖率和抽样策略无法独立验证；原116帧说法撤回，不能把697个理论时间戳当实际抽帧数。",
        "SUPPORTED 仅为报告核验结果，不是人工 Gold；所有记录均为候选且未人工复核。",
        "V2跨帧推断、T文本继承、Ego-MC原始线索分别保存；非视觉线索不提升视觉确定性。",
        "秒级事件边界与小数帧时间存在约0.2s偏移或1–4s不确定性，允许有解释的相邻事件重叠。"]
    evidence = []
    events_doc["evidence"] = evidence
    events = []
    events_doc["events"] = events
    visual_ids = {}

    def add_evidence(eid, kind, source, description, span=None, raw=None):
        item = {"id": eid, "kind": kind, "source": source, "description": description,
                "grade": {"reported_visual_observation":"V1", "model_inference":"V2",
                          "inherited_candidate_text":"T", "ego_mc_text":"TEXT"}[kind]}
        if span is not None:
            item["time"] = span
        if raw is not None:
            item["original_text"] = raw
        evidence.append(item)
        return eid

    for n in range(1,57):
        eid = f"E{n:03}"
        row, vrow = baseline[eid], verification[eid]
        c = row["cells"]
        start,end = BOUNDARIES.get(n,(seconds(c[1]),seconds(c[2])))
        vi = []
        for k,(a,b,description) in enumerate(VISUAL[n],1):
            source = ref(VERIFY,vrow["line"],"B")
            if n == 54:
                source = ref(CROSS,section="E.5")
            vi.append(add_evidence(f"V-{eid}-{k:02}", "reported_visual_observation", source,
                                  description,time(a,b),vrow["cells"][6]))
            if n >= 35 and n <= 54:
                evidence[-1]["normalization_source"] = ref(CONSISTENCY,section="1")
        visual_ids[n] = vi
        original = dict(zip(["id","start_time","end_time","action","actor","target",
                             "description","state_change","certainty"],c))
        original["source"] = ref(BASE,row["line"],"B")
        original["raw_row"] = row["raw"]
        original_status = "CONTRADICTED" if n==42 else "UNCERTAIN" if n in UNCERTAIN_EVENTS else "SUPPORTED"
        status = "CORRECTED_CANDIDATE" if n==42 else "UNCERTAIN" if n in UNCERTAIN_EVENTS else "REPORTED_SUPPORTED"
        current_description = DESCRIPTIONS.get(n,c[6])
        # E053 must not inherit the unverified oil-film assertion from the baseline.
        event = {"id":eid,"time":time(start,end),"time_status":"APPROXIMATE","action":ACTION_OVERRIDES.get(n,c[3]),
                 "actor":c[4],"description":current_description,"object_ids":OBJECTS_BY_EVENT[n],
                 "original_candidate":original,
                 "verification":{"original_claim_status":original_status,"current_claim_status":status,
                    "human_status":"NOT_REVIEWED","report_row":dict(zip(
                        ["id","verdict","time_accuracy","action_accuracy","state_accuracy","evidence","recommendation"],vrow["cells"])),
                    "source":ref(VERIFY,vrow["line"],"B"),"raw_row":vrow["raw"]},
                 "facts":[{"field":"core_action","value":event_action(n,c),
                           "status":"REPORTED_SUPPORTED","evidence_ids":vi,
                           "reason":"仅依据历史报告所述抽样帧的核心动作；未人工确认。"}],
                 "state_change_ids":[],"evidence_ids":list(vi),"ego_mc_record_ids":[],"revisions":[]}
        if (start,end)!=(seconds(c[1]),seconds(c[2])):
            event["revisions"].append({"field":"time","before":time(seconds(c[1]),seconds(c[2])),
               "after":time(start,end),"reason":"依据报告明确边界修正；仍为近似边界。",
               "source":ref(CROSS,section="E.4") if n==49 else ref(VERIFY,vrow["line"],"B")})
        if current_description != c[6] or event["action"] != c[3]:
            event["revisions"].append({"field":"description/action","before":c[6],
                "after":current_description,"reason":"应用后轮修订，去除过度断言并分离观察、推断、文本用途。",
                "source":ref(CROSS,section="E") if n in {7,20,37,41,49,54} else ref(VERIFY,vrow["line"],"B")})
        if n >= 35 and n <= 54:
            event["revisions"].append({"field":"evidence.time","before":vrow["cells"][6],
                "after":[e["time"] for e in evidence if e["id"] in vi],
                "reason":"逐项采用第三轮映射，修正去冒号秒数与内容错配；不是按>696.2阈值机械转换。",
                "source":ref(CONSISTENCY,section="1")})
        if n==54:
            event["revisions"].append({"field":"verification/original_claim_status","before":"CONTRADICTED",
                 "after":"SUPPORTED","reason":"第二轮同一行末尾自我纠正，第三轮统计确认；第四轮只保留盖回粉盖动作。",
                 "source":ref(CONSISTENCY,section="2")})
        events.append(event)

    def event(n):
        return events[n-1]

    # Exact texts, types, and millisecond timestamps come from annotations.json,
    # rather than the rounded/translated summaries in the crosscheck table.
    original_annotations = json.loads(read("source/annotations.json"))
    assert original_annotations["video_id"]=="GX010021"
    assert {len(original_annotations[k]) for k in ("texts","text_types","text_timestamps")}=={55}
    records=[]
    events_doc["ego_mc_records"]=records
    for i,(text,typ,ts) in enumerate(zip(original_annotations["texts"],original_annotations["text_types"],
                                       original_annotations["text_timestamps"]),1):
        rid=f"R{i:02}"
        row=mapping[rid]
        c=row["cells"]
        linked=expand_events(c[4])
        add_evidence(f"T-{rid}","ego_mc_text",ref("source/annotations.json",section=f"texts[{i-1}]"),
                     "原始Ego-MC线索，非视觉事实。",time(ts),text)
        records.append({"id":rid,"source_index":i-1,"text":text,"text_type":typ,"time":time(ts),
                        "event_ids":linked,"alignment":c[5],"mapping_context":c[4],"notes":c[7],
                        "mapping_source":ref(CROSS,row["line"],"B"),"mapping_raw_row":row["raw"],
                        "evidence_id":f"T-{rid}","use":"TEXT_CLUE_ONLY"})
        for eid in linked:
            event(int(eid[1:]))["ego_mc_record_ids"].append(rid)
            event(int(eid[1:]))["evidence_ids"].append(f"T-{rid}")
    # These two instructions were repeatedly delayed; retain their literal table
    # mapping and also link the eventual transfer as context, not execution proof.
    for rid in ["R37","R46"]:
        records[int(rid[1:])-1]["event_ids"].append("E053")
        records[int(rid[1:])-1]["notes"] += "；整合补充链接实际转移E053，仅为延后指令上下文。"
        event(53)["ego_mc_record_ids"].append(rid)
        event(53)["evidence_ids"].append(f"T-{rid}")

    def fact(n,field,value,status="UNCERTAIN",kind="model_inference",reason="",texts=(),v=None):
        ev=event(n)
        ids=list(visual_ids[n] if v is None else v)
        if kind and kind != "ego_mc_text":
            key=f"{'I' if kind=='model_inference' else 'H'}-{ev['id']}-{len(ev['facts']):02}"
            ids.append(add_evidence(key,kind,ref(CONSISTENCY,section="5") if kind=="model_inference" else
                                    ref(BASE,baseline[ev["id"]]["line"],"B"),reason or str(value),ev["time"],
                                    raw=baseline[ev["id"]]["raw"] if kind=="inherited_candidate_text" else None))
        ids.extend(f"T-{rid}" for rid in texts)
        for rid in texts:
            if rid not in ev["ego_mc_record_ids"]:
                ev["ego_mc_record_ids"].append(rid)
                record=records[int(rid[1:])-1]
                record["event_ids"].append(ev["id"])
                record["notes"] += f"；整合补充字段线索关联{ev['id']}，不是新增视觉事实或动作时间对齐。"
        ev["facts"].append({"field":field,"value":value,"status":status,"evidence_ids":ids,"reason":reason})
        ev["evidence_ids"]=list(dict.fromkeys(ev["evidence_ids"]+ids))
        return ids

    # Supported macroscopic observations and unconfirmed fields are separate.
    for n in (2,3):
        fact(n,"display_text","100","REPORTED_SUPPORTED",None,"报告称可见读数；含义另列未知。")
        fact(n,"display_semantics","温度/预热代码含义未知；350°F仅为R01/R02线索。",
             reason="小字和按键功能不可视觉读证；不得将350°F等同显示100。",kind="inherited_candidate_text",texts=("R01","R02"))
    fact(2,"button_display_causality",None,reason="按键与随后显示的具体因果未证实。")
    fact(7,"taken_count",3,reason="V2跨帧计数加R10文本印证，逐次取出被遮挡；保留UNCERTAIN。",texts=("R10",))
    fact(8,"lid_latched",None,reason="54.2s仍开启；短暂扣合不可排除。")
    fact(9,"eggs_on_counter",2,"REPORTED_SUPPORTED",None,"台面暂存数与手中一枚均为报告所述。")
    fact(10,"yolk_count",1,"REPORTED_SUPPORTED",None,"一枚倒入与一个蛋黄可见。")
    fact(11,"yolk_count",2,"REPORTED_SUPPORTED",None,"第二枚倒入，累计两个蛋黄可见。")
    fact(12,"yolk_count",2,"REPORTED_SUPPORTED",None,"所报帧中仍见两个蛋黄。")
    fact(12,"third_egg_integrity",None,reason="磕/掰样动作不能证明破损，也不能维持完整断言。",texts=("R10",))
    fact(12,"third_shell_created",None,reason="似有第三份壳仅为不确定外观；不能以两蛋黄排除第三枚破损。")
    fact(13,"returned_inside_carton",None,reason="持蛋至盒处后空手，不显示入盒瞬间；R11仅支持意图。",texts=("R11",))
    fact(16,"sugar_volume_cup",None,kind="ego_mc_text",reason="半杯指令、反馈和后续1/4杯澄清均非实际量值测量；数量来自Ego-MC而非第一轮。",texts=("R13","R14","R16"))
    fact(18,"sugar_volume_cup",None,kind="ego_mc_text",reason="R16最终1/4杯线索；144.2s标签在加糖后且量杯同一性未知，不能回推糖实际体积。",texts=("R13","R16"))
    fact(19,"sugar_bag_folded_or_inserted",None,reason="整理/按压可见；折口、插入及罐盖开关未知。")
    fact(20,"cup_label","1/4 CUP","REPORTED_SUPPORTED",None,"144.2s杯柄标签，不等于牛奶实测量值。",v=[visual_ids[20][1]])
    fact(20,"same_cup_as_E015",None,reason="无连续跟踪，无法判断同杯或另一只。")
    fact(20,"search_purpose","操作者自述寻找half-cup规格（为牛奶准备）",kind="ego_mc_text",
         reason="用途仅来自R19与R18语境；不作为视觉观察或实际杯规格。",texts=("R18","R19"),v=[])
    for n in (22,23):
        fact(n,"milk_volume_cup",None,kind="ego_mc_text",reason="R18半杯指令与早先1/4 CUP标签不能确认实际使用杯及量值；半杯来自Ego-MC。",texts=("R18","R19"))
    fact(22,"visible_milk_measurements",1,"REPORTED_SUPPORTED",None,"报告只见一次盒到杯的量取；非全帧排除其他动作。")
    fact(23,"visible_milk_additions",1,"REPORTED_SUPPORTED",None,"报告只见一次杯到混合容器倾倒。")
    fact(29,"box_identity_and_intent",None,reason="白盒内容与伸触目的未知，不能凭外观补造材料。")
    for n in (31,32):
        fact(n,"flour_volume_cup",None,kind="ego_mc_text",reason="R26一杯指令非测量；实际杯规格未读证，一杯来自Ego-MC。",texts=("R26",))
    fact(32,"flour_addition_to_mixing_container",1,"REPORTED_SUPPORTED",None,"第一处可见粉入容器；E031仅上游量取。")
    fact(33,"immediate_mixing_after_flour",False,"REPORTED_SUPPORTED",None,"293.2–300.2s所报抽样帧未见搅拌，只记录可见顺序。")
    fact(34,"butter_volume_cup",None,kind="ego_mc_text",reason="R28半杯黄油为Ego-MC指令，未有体积或质量测量。",texts=("R28",))
    for n,rid in ((37,"R30"),(41,"R31")):
        fact(n,"heating_duration_sec",None,kind="inherited_candidate_text" if n==37 else "ego_mc_text",
             reason="15秒分段仅是原始文本线索；第一次0:15也有第一轮继承描述，均不可视觉确证。",texts=(rid,))
        fact(n,"panel_readings",None,kind="inherited_candidate_text",reason="第一轮面板读数/微波炉运行的描述缺少可靠视觉读证，不继承为确定读数。")
    fact(41,"waiting_end_sec",425,reason="425s等待终点与426.2s开门帧间边界约±1s。")
    fact(39,"butter_phase","液体与固态块共存","REPORTED_SUPPORTED",None,"报告393.2–399.2s帧可见；R31只能另作文本佐证。",texts=("R31",))
    fact(42,"butter_phase","以液体为主、仍见固态块","REPORTED_SUPPORTED",None,"否定原完全融化主张；修正观察本身未被否定。")
    fact(42,"solid_fraction",None,reason="抽样帧仅证有固块，质量/体积比例未知。",texts=("R32",))
    fact(43,"same_tool_as_E053_or_cups",None,reason="勺头/刮头外观及连续跟踪不足，不能确定与量杯或后段刮刀同一件。")
    fact(43,"butter_fully_melted_after_stirring",None,reason="444.2–459.2s仍见固块；未覆盖终态消失瞬间。")
    fact(44,"solid_blocks_transferred",None,reason="此前可见固块不能回推464.2–467.2s倾倒时的固块终态。")
    fact(44,"exact_residue_or_mass_balance",None,reason="倒空宏观状态不等于定量全部转移；R42无剩余自述不是测量。",texts=("R42",))
    fact(49,"inner_wall_oil_film",None,reason="模底见油、倾斜旋转不证明内壁油膜或覆盖程度；R45评价不升级事实。",texts=("R43","R45"))
    fact(51,"flour_addition_to_mixing_container",2,"REPORTED_SUPPORTED",None,"第二处可见粉入容器；仅计E032/E051。")
    fact(51,"additional_hidden_flour_addition",None,reason="1fps不能排除遮挡动作，无证据不补造第三次。")
    fact(51,"supplement_intent","操作者自述仍要加一点面粉",kind="ego_mc_text",reason="R49语句印证意图；意图字段仍非视觉事实。",texts=("R49",),v=[])
    fact(53,"same_tool_as_E043_or_cups",None,reason="黑色刮糊工具与E043工具及O05杯组的物理同一性均未知。")
    fact(54,"sugar_bag_inserted_during_event",None,reason="680.2s糖袋已在罐内，没有展示本段插入动作；按第四轮只保留盖回粉盖。")
    fact(54,"scraper_placed_during_event",None,reason="680.2s工具已经留在混合容器；仅保存状态，不增加放置动作。")
    fact(55,"oven_preheat_complete",None,kind="inherited_candidate_text",reason="实际温度与预热完成无视觉证据；R01/R02仅指令/自述。",texts=("R01","R02"))

    build_objects(events_doc,object_rows,visual_ids,add_evidence)
    build_review(events_doc)
    events_doc["statistics"] = {
        "event_count":len(events), "original_claim_status":dict(Counter(e["verification"]["original_claim_status"] for e in events)),
        "current_claim_status":dict(Counter(e["verification"]["current_claim_status"] for e in events)),
        "evidence_kind":dict(Counter(e["kind"] for e in evidence)),
        "ego_mc_record_count":len(records), "ego_mc_type_count":dict(Counter(r["text_type"] for r in records)),
        "flour_visible_addition_event_ids":["E032","E051"],"withdrawn_event_ids":["E057","E058"],
        "human_gold_count":0}
    write("events.json",events_doc)
    return events_doc


def event_action(n,c):
    return ACTION_OVERRIDES.get(n,c[3])


def expand_events(text):
    result=[]
    for match in re.finditer(r"E(\d{3})(?:[–—-]E(\d{3}))?",text):
        a=int(match[1]); b=int(match[2]) if match[2] else a
        result.extend(f"E{i:03}" for i in range(a,b+1))
    return list(dict.fromkeys(result))


def build_objects(events_doc, rows, visual_ids, add_evidence):
    doc = envelope("objects")
    doc["evidence_registry"] = "events.json#/evidence"
    doc["identity_policy"] = "ID为稳定候选指称；O16/O17为两段工具观察，不证明不同实体或同一实体；O05保持量杯组，组内单杯不追认。"
    objects = []
    doc["objects"] = objects
    names = {
        "O02":"盒装褐色鸡蛋（取出组）", "O04":"褐糖袋（品牌文字为原候选线索）",
        "O05":"黑色量杯组", "O06":"牛奶盒（品牌文字为原候选线索）",
        "O08":"面粉纸袋（品牌文字为原候选线索）", "O09":"黄油条及融化后的黄油",
        "O15":"中间混合物/面糊（随配料逐步形成）"}
    summaries = {
        "O01":"选定混合容器，逐步装料并三次电动搅拌；面糊转移后近空，后段报告可见内留黑色工具。",
        "O02":"取蛋计数候选为3；两枚敲入确证；第三枚是否破损与入盒未知。",
        "O03":"前两次敲蛋产生两份蛋壳；第三份是否产生未知，不能固定后段壳总数。",
        "O04":"开袋、供糖、放置、整理；680.2s糖袋已在粉盖罐内，插入动作时间未知。",
        "O05":"量杯组用于糖/奶/粉量取；各段单杯同一性及实际规格未知，不将后段刮刀并入已确认身份。",
        "O06":"开黄盖、量奶、拧盖归位；实际奶体积未知。",
        "O07":"装两根搅拌棒，完成三次可见电动搅拌。",
        "O08":"吊柜取袋、供粉至量杯、后段直接补粉；加入混合容器可见两次，不作量值断言。",
        "O09":"固态、第一次部分融化、第二次液态为主仍见固块、搅动、倒入混合物；终态固块和精确残留未知。",
        "O10":"盛黄油、两次入微波炉、取出、倾倒后空置灶面；末段仍可见。",
        "O11":"两次关门按键加热流程；第一次End显示可见，实际时长和读数未知。",
        "O12":"模底见油并被倾斜旋转；内壁油膜未知；后续装面糊并入烤箱。",
        "O13":"取瓶、开绿盖、倒油；后续是否复盖没有足够证据。",
        "O14":"按键后显示100；显示语义、实际温度、预热完成未知；烤模入架后门关闭。",
        "O15":"蛋液→加糖/奶→均匀淡黄液→表层干粉→加黄油→稠糊→补粉/搅拌成光滑面糊→入模/入烤箱。"}
    for oid,row in rows.items():
        c = row["cells"]
        objects.append({"id":oid,"name":names.get(oid,c[1]),
            "identity_status":"GROUP" if oid in {"O02","O03","O05","O07"} else "CANDIDATE",
            "original_candidate":dict(zip(["id","name","time_range","operation","before","after","event_ids_text"],c)) |
                                 {"source":ref(BASE,row["line"],"C"),"raw_row":row["raw"]},
            "summary":summaries[oid],"identity_relations":[],"facts":[],"event_ids":[],"state_history":[],"revisions":[]})
    added = [
        ("O16","E043黑色勺/量勺状工具（观察指称）","UNRESOLVED_OBSERVATION",43),
        ("O17","E053黑色柄刮刀/勺状工具（观察指称）","UNRESOLVED_OBSERVATION",53),
        ("O18","粉色盖罐（含罐盖）","CANDIDATE",54),
        ("O19","叠放处白碗（被拿取的一只）","CANDIDATE",4),
        ("O20","鸡蛋塑料盒（含盒盖）","CANDIDATE",6),
        ("O21","黄油包装废弃物（箔纸/膜）","GROUP",47),
        ("O22","靠墙白色纸盒（内容未知）","UNRESOLVED_OBSERVATION",29),
    ]
    for oid,name,identity,n in added:
        objects.append({"id":oid,"name":name,"identity_status":identity,"original_candidate":None,
                        "summary":name+"；补充引用记录，不新增操作事件。", "identity_relations":[],
                        "facts":[],"event_ids":[],"state_history":[],
                        "revisions":[{"field":"registry_entry","before":None,"after":name,
                            "reason":"为已有事件中的对象建立引用；不认定新物理实体或新增动作。",
                            "source":ref(VERIFY,section="B/D")}]})
    lookup={o["id"]:o for o in objects}
    for ev in events_doc["events"]:
        for oid in ev["object_ids"]:
            lookup[oid]["event_ids"].append(ev["id"])

    def state(oid,n,field,after,before=None,status="REPORTED_SUPPORTED",kind="transition",span=None,ids=None,reason=""):
        obj=lookup[oid]; ev=events_doc["events"][n-1]
        sid=f"{oid}.S{len(obj['state_history'])+1:02}"
        ids=list(ids or visual_ids[n])
        if status=="UNCERTAIN":
            matching=next((f for f in ev["facts"] if f["field"]==field),None)
            if matching:
                ids=list(matching["evidence_ids"])
            else:
                eid=f"I-{sid}"
                ids.append(add_evidence(eid,"model_inference",ref(CONSISTENCY,section="5/6"),reason or str(after),span or ev["time"]))
                ev["evidence_ids"].append(eid)
        for eid in ids:
            if eid not in ev["evidence_ids"]:
                ev["evidence_ids"].append(eid)
        state_time=span or ev["time"]
        role="aftermath" if state_time["start_sec"]>ev["time"]["end_sec"] else "during"
        obj["state_history"].append({"id":sid,"event_id":ev["id"],"time":state_time,"temporal_role":role,
            "kind":kind,"field":field,"before":before,"after":after,"status":status,
            "evidence_ids":ids,"reason":reason or "历史报告所述宏观状态，未人工复核；before=null表示未断言前态。"})
        ev["state_change_ids"].append(sid)

    # Container states never silently inherit the baseline's full-melt/oil-film claims.
    state("O01",5,"location","台面中央、空置",before="旁侧嵌套存放")
    state("O01",10,"contents","一枚蛋液（一个蛋黄）")
    state("O01",11,"contents","累计两枚蛋液（两个蛋黄）")
    state("O01",18,"contents","蛋液上新增褐色糖堆")
    state("O01",23,"contents","新增牛奶")
    state("O01",27,"contents","淡黄均匀液",before="蛋/糖/奶分层")
    state("O01",32,"contents","淡黄液面新增白色粉堆")
    state("O01",44,"contents","新增倒入的黄油；是否含固块另列未知")
    state("O01",45,"contents","稠厚淡黄糊",before="粉/液分层")
    state("O01",51,"contents","面糊表面新增干粉")
    state("O01",52,"contents","光滑均匀淡黄面糊",before="表面带干粉")
    state("O01",53,"contents","面糊已转入烤模、容器近空")
    state("O01",54,"tool_present","内留黑色刮刀/勺状工具",kind="observation",span=time(680.2),ids=[visual_ids[54][0]],
          reason="工具已在容器内，仅观察结果状态；放置动作时间未知。")
    state("O02",7,"taken_count",3,status="UNCERTAIN",reason="V2计数和R10文字印证不能替代逐次动作确认。")
    state("O02",9,"distribution","台面暂存两枚、手持一枚")
    state("O02",10,"cracked_into_container_count",1)
    state("O02",11,"cracked_into_container_count",2,before=1)
    state("O02",12,"third_egg_integrity",None,status="UNCERTAIN",reason="第三枚有磕/掰样动作，完整性未知。")
    state("O02",13,"returned_inside_carton",None,status="UNCERTAIN",reason="仅见持蛋到盒处、随后空手，不显示入盒。")
    state("O03",10,"observed_shell_portions",1)
    state("O03",11,"observed_shell_portions",2,before=1)
    state("O03",12,"third_shell_created",None,status="UNCERTAIN",reason="83.2s似见第三份壳，未确证；后续总量未知。")
    state("O04",14,"bag_access","袋口打开、手持")
    state("O04",16,"contents_use","部分糖倒入量杯")
    state("O04",17,"location","右侧台面")
    state("O04",19,"sugar_bag_folded_or_inserted",None,status="UNCERTAIN",reason="折口与插入不能由整理动作确认。")
    state("O04",54,"location","已位于粉盖罐内",kind="observation",span=time(680.2),ids=[visual_ids[54][0]],
          reason="第四轮要求记为已存在的状态，插入发生时间未知，不是E054插入动作。")
    state("O04",54,"sugar_bag_inserted_during_event",None,status="UNCERTAIN",kind="observation",
          reason="680.2s已在罐内；不得由状态反推本段插入。")
    for n,value in [(15,"取一只量杯查看"),(16,"杯内见褐色糖"),(18,"杯内糖倒入混合容器"),
                    (19,"量杯放回"),(20,'查看量杯；一只杯柄见1/4 CUP'),(22,"杯中量取牛奶"),
                    (23,"杯中奶倒入混合容器"),(29,"手持空量杯"),(31,"杯中量取面粉"),
                    (32,"杯中面粉倒入混合容器")]:
        state("O05",n,"group_member_use",value,kind="observation",reason="指组内当时观察到的一只量杯，不推定与其他时段为同一只。")
    state("O05",20,"same_cup_as_E015",None,status="UNCERTAIN",kind="observation",reason="单杯身份无连续跟踪。")
    state("O06",21,"closure","黄盖打开")
    state("O06",22,"contents_use","部分牛奶倒入量杯")
    state("O06",24,"closure_and_location","拧回黄盖、归位灶侧")
    state("O07",25,"assembly","两根棒装入本体",before="本体与棒分离")
    for n,k in [(27,1),(45,2),(52,3)]:
        state("O07",n,"mixing_round",k,kind="observation")
    state("O07",28,"location","提离混合容器并置左台面")
    state("O08",30,"location","从吊柜取出至手持")
    state("O08",31,"contents_use","开袋、供粉入量杯")
    state("O08",51,"contents_use","袋直接供粉入混合容器")
    state("O09",34,"packaging_and_phase","拆包、固态黄油裸露")
    state("O09",35,"location","玻璃容器内")
    state("O09",36,"location","随玻璃容器第一次入微波炉")
    state("O09",39,"butter_phase","液体与固态块共存",before="固态")
    state("O09",40,"location","随玻璃容器第二次入微波炉")
    state("O09",42,"butter_phase","以液体为主、仍见固态块",before="部分融化")
    state("O09",42,"solid_fraction",None,status="UNCERTAIN",reason="无定量比例证据。")
    state("O09",43,"butter_phase","固液混合被搅动，抽样帧仍见固块")
    state("O09",43,"butter_fully_melted_after_stirring",None,status="UNCERTAIN",reason="搅拌终态未确认。")
    state("O09",44,"location","倒入混合容器；原玻璃容器宏观近空")
    state("O09",44,"solid_blocks_transferred",None,status="UNCERTAIN",reason="倒入时固块是否已消失未知。")
    state("O09",44,"exact_residue_or_mass_balance",None,status="UNCERTAIN",reason="全部倒入仅为宏观候选，不能当定量质量守恒。")
    for n,val in [(35,"盛固态黄油"),(36,"第一次置微波炉转盘"),(39,"第一次取出，盛固液混合黄油"),
                  (40,"再次置微波炉转盘"),(42,"第二次取出，盛液态为主且有固块黄油")]:
        state("O10",n,"location_and_contents",val)
    state("O10",44,"location_and_contents","倾倒后空置于灶台黑面",span=time(470.2),ids=[visual_ids[44][1]],
          reason="E044放置子动作结果；470.2s为后续结果帧，保留原事件末界469s，不恢复E058。")
    state("O10",56,"location_and_contents","灶台黑面仍可见玻璃容器",kind="observation",span=time(693.2,696.2))
    state("O11",36,"door_and_contents","门开启、置入盛黄油容器")
    state("O11",37,"heating_workflow","第一次关门按键流程")
    state("O11",37,"heating_duration_sec",None,status="UNCERTAIN",reason="15秒仅文本线索。")
    state("O11",39,"display","End",kind="observation",span=time(390.2),ids=[visual_ids[39][0]])
    state("O11",40,"door_and_contents","容器再次放回转盘")
    state("O11",41,"heating_workflow","第二次关门按键流程")
    state("O11",41,"heating_duration_sec",None,status="UNCERTAIN",reason="15秒仅文本线索。")
    state("O11",42,"door_and_contents","取出容器、关门")
    state("O12",49,"oil_at_bottom","模底见少量油；烤模被倾斜旋转")
    state("O12",49,"inner_wall_oil_film",None,status="UNCERTAIN",reason="动作不等于油膜分布确证。")
    state("O12",53,"contents","装入面糊")
    state("O12",55,"location","烤箱烤架内")
    state("O13",48,"closure","绿盖打开")
    state("O13",49,"contents_use","少量油倒入烤模")
    state("O14",2,"display","100",kind="observation",span=time(15.2),ids=[visual_ids[2][1]],
          reason="按键后的结果帧，比事件末界晚1.2s；不证明按键因果或温度语义。")
    state("O14",3,"display","100",kind="observation")
    state("O14",2,"display_semantics",None,status="UNCERTAIN",reason="显示语义未知，不能当预热温度。")
    state("O14",55,"door_and_contents","门打开、置入盛面糊烤模、关门")
    state("O14",55,"oven_preheat_complete",None,status="UNCERTAIN",reason="预热完成无实际温度证据。")
    for n,val in [(10,"一枚蛋液"),(11,"累计两枚蛋液"),(18,"蛋液上加入糖堆"),(23,"加入牛奶"),
                  (27,"均匀淡黄混合液"),(32,"液面新增干粉层"),(44,"加入黄油，固块终态未知"),
                  (45,"稠厚淡黄糊"),(51,"表面补加干粉"),(52,"光滑均匀面糊"),(53,"转入烤模"),(55,"随烤模入烤箱")]:
        state("O15",n,"mixture_state",val)
    state("O16",43,"use","勺/量勺状工具在玻璃容器中搅黄油",kind="observation")
    state("O16",43,"same_tool_as_E053_or_cups",None,status="UNCERTAIN",kind="observation",reason="物理同一性未确认。")
    state("O17",53,"use","刮刀/勺状工具刮擦混合容器",kind="observation")
    state("O17",53,"same_tool_as_E043_or_cups",None,status="UNCERTAIN",kind="observation",reason="物理同一性未确认。")
    state("O17",54,"location","已留在近空混合容器内",kind="observation",span=time(680.2),ids=[visual_ids[54][0]])
    state("O18",19,"handling_content",None,status="UNCERTAIN",kind="observation",reason="整理/按压内容未知，不确证此段开关罐盖。")
    state("O18",54,"contents","罐口已见糖袋",kind="observation",span=time(680.2),ids=[visual_ids[54][0]])
    state("O18",54,"closure","粉色盖盖回、罐闭合",before="盖分离、罐敞口",span=time(681.2,683.2),ids=[visual_ids[54][1]])
    state("O19",4,"location","翻看后放回叠位")
    state("O20",6,"closure","盒盖掀起",before="闭合")
    state("O20",8,"lid_latched",None,status="UNCERTAIN",reason="所报盖开启，是否短暂扣合未知。")
    state("O20",13,"returned_inside_carton",None,status="UNCERTAIN",kind="observation",reason="不将回到盒处等同入盒。")
    state("O21",34,"packaging","黄油被拆出、包装剥离")
    state("O21",47,"location","折叠收拢并放鱼形垫")
    state("O22",29,"box_identity_and_intent",None,status="UNCERTAIN",kind="observation",reason="白盒内容与触碰目的未知。")

    for oid,other,n in [("O05","O16",43),("O05","O17",53),("O16","O05",43),
                         ("O16","O17",43),("O17","O05",53),("O17","O16",53)]:
        lookup[oid]["identity_relations"].append({"object_id":other,"relation":"SAME_AS_UNKNOWN",
            "evidence_ids":next(f["evidence_ids"] for f in events_doc["events"][n-1]["facts"]
                                if f["field"].startswith("same_tool")),
            "reason":"不同观察指称，不断言同一件，也不证明一定为不同件。"})
    for oid,field,value in [("O04","brand_and_product","Trader Joe's Turbinado Raw Cane Sugar"),
                             ("O06","brand","Horizon Organic"),("O08","brand_and_product","Trader Joe's All-Purpose Flour")]:
        eid=add_evidence(f"H-{oid}-NAME","inherited_candidate_text",ref(BASE,rows[oid]["line"],"C"),
                         "品牌/产品名继承第一轮，不声称本次已读证标签。",raw=value)
        lookup[oid]["facts"].append({"field":field,"value":value,"status":"UNCERTAIN","evidence_ids":[eid],
                                    "reason":"后续报告未提供独立标签核验；保留原文字作为线索。"})
    for oid,why in {
        "O01":"将11:20s内留工具记为状态，放置动作时间未知。",
        "O02":"两枚敲入与第三枚终态分开，第三枚是否完整/入盒均未知。",
        "O03":"不沿用两份蛋壳持续不变；第三份可能性未确认。",
        "O04":"糖袋已位于罐内是观察状态，不认定E054插入动作；折口也未知。",
        "O05":"保持量杯组ID；移除末期一只充当刮刀的身份断言，关联O16/O17未知关系。",
        "O09":"删除完全融化节点；保留固块与未知终态，R42不是质量测量。",
        "O10":"保留E044倾倒后的空置灶面状态；E058撤销，末段仍可见。",
        "O11":"运行流程和面板语义分开，15秒仅文本线索。",
        "O12":"内壁沾油降为未知，模底见油和旋转保留。",
        "O14":"100语义和预热完成未知。",
        "O15":"面粉层加入后未立即搅拌；稠糊节点到E045才出现，不能提前继承。",
    }.items():
        lookup[oid]["revisions"].append({"field":"identity/state_history","before":rows[oid]["cells"][5],
            "after":lookup[oid]["summary"],"reason":why,"source":ref(CROSS,section="E") if oid in {"O04","O09","O10"}
                                                                            else ref(CONSISTENCY,section="3–6")})
    # Histories must be ordered by their own corrected time, rather than source row order.
    for obj in objects:
        obj["state_history"].sort(key=lambda s:(s["time"]["start_sec"],s["time"]["end_sec"],s["id"]))
    doc["statistics"]={"object_record_count":len(objects),"baseline_object_count":15,
        "added_reference_count":7,"physical_entity_count":None,
        "state_entry_count":sum(len(o["state_history"]) for o in objects),
        "state_status":dict(Counter(s["status"] for o in objects for s in o["state_history"]))}
    write("objects.json",doc)


def build_review(events_doc):
    objects_doc=json.loads((ANN/"objects.json").read_text(encoding="utf-8"))
    doc=envelope("review_queue")
    doc["priority_policy"]="采用第四轮D节明确的复核片段优先级；其未覆盖的问题沿用较早报告。记录各轮差异，优先级调整不改变字段不确定性。"
    items=[]
    doc["review_items"]=items
    specs=[
      ("P0","黄油固块与倾倒终态",[42,43,44],[(426,470.2)],
       "确认第二次取出后的固块比例、搅拌后是否消失、倒入混合容器时是否含固块。",["R31","R32","R42"],
       ["solid_fraction","butter_fully_melted_after_stirring","solid_blocks_transferred","exact_residue_or_mass_balance"],
       [(VERIFY,"F/P0"),(CONSISTENCY,"7"),(CROSS,"D/P0")]),
      ("P0","鸡蛋逐次计数与第三枚终态",[7,12,13],[(47,89)],
       "确认逐次取蛋次数、第三枚是否磕破或产生蛋壳、是否确实入盒。",["R10","R11"],
       ["taken_count","third_egg_integrity","third_shell_created","returned_inside_carton"],
       [(CONSISTENCY,"7"),(CROSS,"C/Q-02、D/P0")]),
      ("P1","烤模内壁油膜",[49],[(560,581)],
       "确认油是否覆盖内壁及其分布；倾斜旋转与Success评价均不足以证明油膜。",["R43","R45"],
       ["inner_wall_oil_film"],[(VERIFY,"F/P0"),(CONSISTENCY,"7"),(CROSS,"D/P1")]),
      ("P1","黑色工具与量杯物理同一性",[43,53,54],[(434,460),(645.2,685)],
       "追踪搅黄油工具、刮糊工具和量杯，确认同一性及末期放置时点。",[],
       ["same_tool_as_E053_or_cups","same_tool_as_E043_or_cups","scraper_placed_during_event"],[(VERIFY,"F/P1、D/O05")]),
      ("P1","牛奶量杯规格和实际量值",[20,22,23],[(139,165)],
       "确认实际使用杯是否为标签1/4 CUP的杯、规格与倒奶量；半杯指令/自述不能代替量值。",["R18","R19"],
       ["same_cup_as_E015","search_purpose","milk_volume_cup"],[(CROSS,"C/Q-03、D/P1")]),
      ("P1","首次面粉量杯规格和实际量值",[31,32],[(269,292)],
       "确认杯规格与实际加粉量；R26一杯仅为文本线索。",["R26"],
       ["flour_volume_cup"],[(CROSS,"C/Q-04、D/P1")]),
      ("P2","微波时长、显示与等待边界",[37,41],[(344,374),(408,426.2)],
       "高清确认两次设定时长/显示；15秒线索不能等同实际运行时长；等待末界约±1s。",["R30","R31"],
       ["heating_duration_sec","panel_readings","waiting_end_sec"],[(CONSISTENCY,"1、5"),(CROSS,"D/P2")]),
      ("P2","100语义与烤箱预热状态",[2,3,55],[(10,19),(687,692)],
       "确认显示100的语义、按键与显示因果及实际温度/预热完成；350°F为原始文本线索。",["R01","R02"],
       ["display_semantics","button_display_causality","oven_preheat_complete"],[(CROSS,"C/Q-06、D/P2")]),
      ("P2","糖袋整理与收纳动作发生时间",[19,54],[(133,138),(680,685)],
       "确认整理/折口内容和收纳发生时点；680.2s袋已在罐内，E054不认定插入动作。",[],
       ["sugar_bag_folded_or_inserted","sugar_bag_inserted_during_event"],[(VERIFY,"F/P2"),(CROSS,"E.5")]),
      ("P2","蛋盒盖是否曾扣合",[8],[(53,55)],
       "确认扶盖到离开之间是否短暂扣合；报告所述盖仍开启。",[],["lid_latched"],[(VERIFY,"F/P2")]),
      ("P2","白色纸盒身份与触碰意图",[29],[(240,258)],
       "仅短暂伸触部分可见，不能补造盒内材料或用途；若无法裁决继续未知。",[],["box_identity_and_intent"],[(BASE,"D")]),
      ("P2","是否存在遮挡的额外加粉",[51],[(283,292),(595,604)],
       "当前仅计两次可见入混合容器；若有连续证据再修订，不能预先添加第三次。",["R26","R49"],
       ["additional_hidden_flour_addition","supplement_intent"],[(CONSISTENCY,"4")]),
      ("P2","糖/黄油量值与品牌文字",[16,18,34],[(107,132),(303,319)],
       "1/4杯糖、半杯黄油及品牌名均缺独立视觉读证；保存文本线索，不作已确认量值或品牌。",["R13","R14","R16","R28"],
       ["sugar_volume_cup","butter_volume_cup"],[(README,"字段级证据来源"),(CROSS,"F.1")]),
    ]
    for i,(priority,title,ns,ranges,question,rids,fields,sources) in enumerate(specs,1):
        targets=[]
        evs=[events_doc["events"][n-1] for n in ns]
        for ev in evs:
            for f in ev["facts"]:
                if f["status"]=="UNCERTAIN" and f["field"] in fields:
                    targets.append({"artifact":"events","record_id":ev["id"],"field":"facts/"+f["field"]})
        oids=[]; eids=[]
        for obj in objects_doc["objects"]:
            if any(obj["id"] in ev["object_ids"] for ev in evs):
                oids.append(obj["id"])
            for s in obj["state_history"]:
                if s["event_id"] in [ev["id"] for ev in evs] and s["status"]=="UNCERTAIN" and (s["field"] in fields or (i==9 and s["field"]=="handling_content")):
                    targets.append({"artifact":"objects","record_id":obj["id"],"field":"state_history/"+s["id"]})
            if i==13:
                for f in obj["facts"]:
                    targets.append({"artifact":"objects","record_id":obj["id"],"field":"facts/"+f["field"]})
                    oids.append(obj["id"])
        for target in targets:
            if target["artifact"]=="events":
                ev=next(e for e in evs if e["id"]==target["record_id"])
                eids.extend(next(f["evidence_ids"] for f in ev["facts"] if target["field"]=="facts/"+f["field"]))
            else:
                obj=next(o for o in objects_doc["objects"] if o["id"]==target["record_id"])
                collection,key=target["field"].split("/",1)
                match=next(x for x in obj[collection] if x.get("id",x.get("field"))==key)
                eids.extend(match["evidence_ids"])
        eids.extend("T-"+rid for rid in rids)
        items.append({"id":f"RQ{i:02}","priority":priority,"status":"OPEN","title":title,"question":question,
            "time_ranges":[time(a,b) for a,b in ranges],"event_ids":[ev["id"] for ev in evs],
            "object_ids":list(dict.fromkeys(oids)),"ego_mc_record_ids":rids,"targets":targets,
            "evidence_ids":list(dict.fromkeys(eids)),"sources":[ref(p,section=s) for p,s in sources],
            "review_method":"人工查看连续视频/高清局部并记录裁决；若仍无证据则保留UNCERTAIN。",
            "priority_notes":"第三轮/第二轮P0；第四轮D表降为P1，本整合采用第四轮P1，字段仍UNCERTAIN。" if i==3 else
                             "优先采用第四轮D节明确片段清单；未覆盖问题沿用先前优先级，保留来源，不改变事实状态。"})
    items.append({"id":"RQ14","priority":"P2","status":"OPEN","title":"报告抽样覆盖和视频尾部缺口",
        "question":"核实历史抽样实际数量/覆盖率；视频时长696.929567s，报告证据止696.2s，尾部约0.73s未被覆盖。",
        "time_ranges":[time(696.2,events_doc["video"]["duration_sec"])],"event_ids":["E056"],"object_ids":[],
        "ego_mc_record_ids":[],"targets":[{"artifact":"events","record_id":"video","field":"reported_evidence_range"}],
        "evidence_ids":[],"sources":[ref(CONSISTENCY,section="0"),ref("source/GX010021.MP4",section="ffprobe metadata")],
        "review_method":"人工核查抽样记录与原视频尾部；本次整合不解码帧、不扩写事件。",
        "priority_notes":"元数据新发现；不声称实际帧覆盖完整。"})
    doc["statistics"]={"review_item_count":len(items),"priority":dict(Counter(x["priority"] for x in items)),
                       "open_count":len(items)}
    write("review_queue.json",doc)


def make_schema():
    """One schema with shared source, time, fact, and revision definitions."""
    def obj(properties,required=None):
        return {"type":"object","properties":properties,"required":list(properties) if required is None else required,
                "additionalProperties":False}
    def arr(items):
        return {"type":"array","items":items}
    def enum(*values):
        return {"enum":list(values)}
    def pointer(name):
        return {"$ref":"#/$defs/"+name}
    string={"type":"string"}; value={}; nullable_string={"type":["string","null"]}
    ids=arr(string) | {"uniqueItems":True}
    definitions={
        "source":obj({"path":string,"line":{"type":"integer","minimum":1},"section":string},["path"]),
        "time":obj({"start_sec":{"type":"number","minimum":0},"end_sec":{"type":"number","minimum":0},
                    "start_hms":{"type":"string","pattern":r"^\d{2}:\d{2}:\d{2}\.\d{3}$"},
                    "end_hms":{"type":"string","pattern":r"^\d{2}:\d{2}:\d{2}\.\d{3}$"}}),
        "fact":obj({"field":string,"value":value,"status":enum("REPORTED_SUPPORTED","UNCERTAIN"),
                    "evidence_ids":ids,"reason":{"type":"string","minLength":1}}),
        "revision":obj({"field":string,"before":value,"after":value,"reason":string,"source":pointer("source")}),
        "event_original":obj({**{k:string for k in ["id","start_time","end_time","action","actor","target",
                                                     "description","state_change","certainty","raw_row"]},
                              "source":pointer("source")}),
        "object_original":obj({**{k:string for k in ["id","name","time_range","operation","before","after","event_ids_text","raw_row"]},
                               "source":pointer("source")}),
        "verification":obj({"original_claim_status":enum("SUPPORTED","CONTRADICTED","UNCERTAIN"),
            "current_claim_status":enum("REPORTED_SUPPORTED","CORRECTED_CANDIDATE","UNCERTAIN"),
            "human_status":{"const":"NOT_REVIEWED"},
            "report_row":obj({k:string for k in ["id","verdict","time_accuracy","action_accuracy","state_accuracy","evidence","recommendation"]}),
            "source":pointer("source"),"raw_row":string}),
        "evidence":obj({"id":string,"kind":enum("reported_visual_observation","model_inference","inherited_candidate_text","ego_mc_text"),
            "source":pointer("source"),"description":string,"grade":enum("V1","V2","T","TEXT"),"time":pointer("time"),
            "original_text":string,"normalization_source":pointer("source")},["id","kind","source","description","grade"]),
        "event":obj({"id":{"type":"string","pattern":r"^E\d{3}$"},"time":pointer("time"),"time_status":{"const":"APPROXIMATE"},"action":string,"actor":string,
            "description":string,"object_ids":ids,"original_candidate":pointer("event_original"),
            "verification":pointer("verification"),"facts":arr(pointer("fact")),"state_change_ids":ids,
            "evidence_ids":ids,"ego_mc_record_ids":ids,"revisions":arr(pointer("revision"))}),
        "state":obj({"id":string,"event_id":string,"time":pointer("time"),"temporal_role":enum("during","aftermath"),
            "kind":enum("transition","observation"),"field":string,"before":value,"after":value,
            "status":enum("REPORTED_SUPPORTED","UNCERTAIN"),"evidence_ids":ids,"reason":{"type":"string","minLength":1}}),
        "object":obj({"id":{"type":"string","pattern":r"^O\d{2}$"},"name":string,
            "identity_status":enum("CANDIDATE","GROUP","UNRESOLVED_OBSERVATION"),
            "original_candidate":{"anyOf":[pointer("object_original"),{"type":"null"}]},"summary":string,
            "identity_relations":arr(obj({"object_id":string,"relation":{"const":"SAME_AS_UNKNOWN"},"evidence_ids":ids,"reason":string})),
            "facts":arr(pointer("fact")),"event_ids":ids,"state_history":arr(pointer("state")),"revisions":arr(pointer("revision"))}),
        "ego_mc_record":obj({"id":{"type":"string","pattern":r"^R\d{2}$"},"source_index":{"type":"integer","minimum":0},
            "text":string,"text_type":enum("Instruction","User-Comment","Success","Feedback","Instruction-Clarification","User-Question"),
            "time":pointer("time"),"event_ids":ids,"alignment":string,"mapping_context":string,"notes":string,
            "mapping_source":pointer("source"),"mapping_raw_row":string,"evidence_id":string,"use":{"const":"TEXT_CLUE_ONLY"}}),
        "review_item":obj({"id":{"type":"string","pattern":r"^RQ\d{2}$"},"priority":enum("P0","P1","P2"),"status":{"const":"OPEN"},
            "title":string,"question":string,"time_ranges":arr(pointer("time")),"event_ids":ids,"object_ids":ids,"ego_mc_record_ids":ids,
            "targets":arr(obj({"artifact":enum("events","objects"),"record_id":string,"field":string})),
            "evidence_ids":ids,"sources":arr(pointer("source")),"review_method":string,"priority_notes":string}),
    }
    common={"$schema":{"const":"./schema.json"},"schema_version":{"const":"1.0"},"episode_id":{"const":"GX010021"},
            "artifact":string,"data_status":{"const":"CANDIDATE"},"human_review":{"const":"NOT_REVIEWED"}}
    statistics={"type":"object"}
    event_doc=obj(common | {"artifact":{"const":"events"},
        "sources":arr(obj({"path":string,"sha256":{"type":"string","pattern":"^[0-9a-f]{64}$"},
            "bytes":{"type":"integer","minimum":0},"role":enum("video_metadata_only","ego_mc_text_only","archived_ai_report"),
            "priority":{"type":"integer","minimum":0,"maximum":5}})),
        "video":obj({"path":{"const":"source/GX010021.MP4"},"duration_sec":{"type":"number","exclusiveMinimum":0},"metadata_method":string,
            "video_stream":{"type":"object"},"reported_evidence_range":pointer("time"),"reported_sampling_fps":{"const":1},
            "sampling_verified":{"const":False},"uncovered_tail_sec":{"type":"number","minimum":0}}),
        "limitations":arr(string),"evidence":arr(pointer("evidence")),"events":arr(pointer("event")) | {"minItems":56,"maxItems":56},
        "ego_mc_records":arr(pointer("ego_mc_record")) | {"minItems":55,"maxItems":55},"statistics":statistics})
    object_doc=obj(common | {"artifact":{"const":"objects"},"evidence_registry":{"const":"events.json#/evidence"},
                            "identity_policy":string,"objects":arr(pointer("object")),"statistics":statistics})
    queue_doc=obj(common | {"artifact":{"const":"review_queue"},"priority_policy":string,
                           "review_items":arr(pointer("review_item")),"statistics":statistics})
    return {"$schema":"https://json-schema.org/draft/2020-12/schema","title":"GX010021 candidate consolidation v1",
            "oneOf":[event_doc,object_doc,queue_doc],"$defs":definitions}


if __name__ == "__main__":
    result=build()
    print(json.dumps(result["statistics"],ensure_ascii=False,indent=2))
