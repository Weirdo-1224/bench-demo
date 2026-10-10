"""Validate schema, cross-file links and source preservation; no video model calls.

Usage (project root): python golden_episode/GX010021/scripts/validate.py --self-test
Requires the already installed jsonschema package. Negative checks run in memory.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

from build import (ANN, BASE, CROSS, EP, INPUT_HASHES, REP, UNCERTAIN_EVENTS,
                   VERIFY, digest, read, stamp, table)


def walk(value,path="$"):
    yield path,value
    if isinstance(value,dict):
        for key,item in value.items():
            yield from walk(item,path+"/"+key)
    elif isinstance(value,list):
        for i,item in enumerate(value):
            yield from walk(item,path+f"/{i}")


def validate(documents,schema,check_inputs=True):
    errors=[]; notes=[]; checks=Counter()
    def check(ok,message,category):
        checks[category]+=1
        if not ok:
            errors.append(message)
    for name,doc in documents.items():
        branch=next(s for s in schema["oneOf"] if s["properties"]["artifact"]["const"]==name)
        root_schema={k:v for k,v in schema.items() if k!="oneOf"} | branch
        validator=Draft202012Validator(root_schema)
        failures=list(validator.iter_errors(doc))
        check(not failures,f"{name}: Schema violation: "+"; ".join(
            "/".join(map(str,f.absolute_path))+": "+
            (f"array length {len(f.instance)} exceeds maximum {f.validator_value}" if f.validator=="maxItems" else f.message[:300])
            for f in failures[:3]),"schema")
    # Semantic checks need structurally valid records. Schema errors are already fatal.
    if errors:
        return {"passed":False,"errors":errors,"notes":notes,"checks":dict(checks)}
    ed,od,qd=(documents[k] for k in ("events","objects","review_queue"))
    duration=ed["video"]["duration_sec"]
    events=ed["events"]; objects=od["objects"]; evidence=ed["evidence"]; records=ed["ego_mc_records"]; queue=qd["review_items"]
    def index(items,kind):
        result={i["id"]:i for i in items}
        check(len(result)==len(items),f"Duplicate {kind} ID","unique_ids")
        return result
    ei=index(events,"event"); oi=index(objects,"object"); vi=index(evidence,"evidence"); ri=index(records,"Ego-MC record"); qi=index(queue,"review")
    states=[s for obj in objects for s in obj["state_history"]]; si=index(states,"state")
    all_ids=[x["id"] for collection in (events,objects,evidence,records,queue,states) for x in collection]
    check(len(set(all_ids))==len(all_ids),"ID collision across namespaces","unique_ids")
    check(set(ei)=={f"E{n:03}" for n in range(1,57)},"Event set must be E001–E056; E057/E058 forbidden","event_set")
    check({f"O{n:02}" for n in range(1,16)} <= set(oi),"Baseline O01–O15 must remain stable","event_set")
    check(set(ri)=={f"R{n:02}" for n in range(1,56)},"Ego-MC record set must be R01–R55","event_set")
    for name,doc in documents.items():
        for path,node in walk(doc):
            if isinstance(node,dict) and {"start_sec","end_sec","start_hms","end_hms"}<=node.keys():
                a,b=node["start_sec"],node["end_sec"]
                check(0<=a<=b<=duration,f"{name}{path}: out-of-range/inverted time {a}–{b}","time")
                check(node["start_hms"]==stamp(a) and node["end_hms"]==stamp(b),f"{name}{path}: HMS/seconds mismatch","time")
            if isinstance(node,dict) and "evidence_ids" in node:
                check(set(node["evidence_ids"])<=set(vi),f"{name}{path}: dangling evidence ID","references")
            if isinstance(node,dict) and "path" in node and ("section" in node or "line" in node):
                p=EP/node["path"]
                check(node["path"] in INPUT_HASHES and p.is_file(),f"{name}{path}: invalid source path","provenance")
                if "line" in node and p.suffix==".md" and p.is_file():
                    check(node["line"]<=len(read(node["path"]).splitlines()),f"{name}{path}: invalid source line","provenance")
    expected_grades={"reported_visual_observation":"V1","model_inference":"V2","inherited_candidate_text":"T","ego_mc_text":"TEXT"}
    for evd in evidence:
        check(evd["grade"]==expected_grades[evd["kind"]],f"{evd['id']}: kind/grade mismatch","evidence_types")
        if evd["kind"]=="ego_mc_text":
            check(evd["source"]["path"]=="source/annotations.json",f"{evd['id']}: Ego-MC must point to raw annotations","evidence_types")
        if evd["kind"]=="reported_visual_observation":
            check(evd["source"]["path"] in {VERIFY,CROSS},f"{evd['id']}: visual observation must be an archived report","evidence_types")
            check("time" in evd and evd["time"]["end_sec"]<=696.2,f"{evd['id']}: visual evidence outside reported range","time")
    def validate_fact(f,label):
        check(bool(f["evidence_ids"]),f"{label}: no evidence/provenance","evidence_types")
        kinds={vi[eid]["kind"] for eid in f["evidence_ids"] if eid in vi}
        if f["status"]=="REPORTED_SUPPORTED":
            check("reported_visual_observation" in kinds,f"{label}: supported claim lacks reported visual observation","evidence_types")
            check(not {"model_inference","inherited_candidate_text"}&kinds,f"{label}: V2/T promoted to supported","uncertainty")
        if f["status"]=="UNCERTAIN":
            check(bool(f["reason"].strip()),f"{label}: uncertain field needs reason","uncertainty")
    expected_uncertain={f"E{n:03}" for n in UNCERTAIN_EVENTS}
    for ev in events:
        eid=ev["id"]
        check(set(ev["object_ids"])<=set(oi),f"{eid}: dangling object ID","references")
        check(set(ev["state_change_ids"])<=set(si),f"{eid}: dangling state ID","references")
        check(set(ev["ego_mc_record_ids"])<=set(ri),f"{eid}: dangling Ego-MC record ID","references")
        check(ev["time"]["end_sec"]<=696.2,f"{eid}: event goes beyond report coverage","time")
        expected_original="CONTRADICTED" if eid=="E042" else "UNCERTAIN" if eid in expected_uncertain else "SUPPORTED"
        expected_current="CORRECTED_CANDIDATE" if eid=="E042" else "UNCERTAIN" if eid in expected_uncertain else "REPORTED_SUPPORTED"
        check(ev["verification"]["original_claim_status"]==expected_original,f"{eid}: incorrect original-claim status","event_status")
        check(ev["verification"]["current_claim_status"]==expected_current,f"{eid}: corrected/current status incorrectly inherited","event_status")
        check(len({f["field"] for f in ev["facts"]})==len(ev["facts"]),f"{eid}: duplicate field claims","unique_ids")
        for f in ev["facts"]:
            validate_fact(f,eid+"/"+f["field"])
            check(set(f["evidence_ids"])<=set(ev["evidence_ids"]),f"{eid}: field evidence missing from event","references")
        for sid in ev["state_change_ids"]:
            if sid in si:
                check(si[sid]["event_id"]==eid,f"{eid}: reverse state link mismatch","references")
                check(set(si[sid]["evidence_ids"])<=set(ev["evidence_ids"]),f"{eid}: state evidence missing from event","references")
        for oid in ev["object_ids"]:
            if oid in oi:
                check(eid in oi[oid]["event_ids"],f"{eid}/{oid}: reverse object link missing","references")
        for rid in ev["ego_mc_record_ids"]:
            if rid in ri:
                check(eid in ri[rid]["event_ids"],f"{eid}/{rid}: reverse text link missing","references")
        for evid in ev["evidence_ids"]:
            if evid in vi and vi[evid]["kind"]=="ego_mc_text":
                rid=evid.removeprefix("T-")
                check(rid in ev["ego_mc_record_ids"] and rid in ri and eid in ri[rid]["event_ids"],
                      f"{eid}/{evid}: field text clue lacks reciprocal mapping","references")
            if evid in vi and vi[evid]["kind"]=="reported_visual_observation":
                start=vi[evid]["time"]["start_sec"]
                end=vi[evid]["time"]["end_sec"]
                check(start>=ev["time"]["start_sec"],f"{eid}/{evid}: visual evidence precedes event unexpectedly","time")
                if end>ev["time"]["end_sec"]:
                    delta=round(end-ev["time"]["end_sec"],3)
                    check(delta<=1.2,f"{eid}/{evid}: unexplained evidence after event by {delta}s","time")
                    notes.append(f"{eid}/{evid}: 结果/边界证据晚于秒级事件末界{delta}s，保留原范围；不是新的事件。")
    for obj in objects:
        oid=obj["id"]
        check(set(obj["event_ids"])<=set(ei),f"{oid}: dangling event ID","references")
        for eid in obj["event_ids"]:
            if eid in ei:
                check(oid in ei[eid]["object_ids"],f"{oid}/{eid}: reverse event link missing","references")
        check([s["time"]["start_sec"] for s in obj["state_history"]]==sorted(s["time"]["start_sec"] for s in obj["state_history"]),
              f"{oid}: state history not chronological","state_history")
        for f in obj["facts"]:
            validate_fact(f,oid+"/"+f["field"])
        for relation in obj["identity_relations"]:
            other=relation["object_id"]
            check(other in oi,f"{oid}: dangling identity relation","references")
            if other in oi:
                check(any(r["object_id"]==oid for r in oi[other]["identity_relations"]),f"{oid}/{other}: asymmetric identity relation","references")
        for s in obj["state_history"]:
            eid=s["event_id"]
            check(eid in ei and oid in ei[eid]["object_ids"],f"{s['id']}: state object not referenced by event","references")
            if eid in ei:
                check(s["id"] in ei[eid]["state_change_ids"],f"{s['id']}: reverse state link missing","references")
                later=s["time"]["start_sec"]>ei[eid]["time"]["end_sec"]
                check(s["temporal_role"]==("aftermath" if later else "during"),f"{s['id']}: incorrect temporal role","state_history")
                check(s["time"]["start_sec"]>=ei[eid]["time"]["start_sec"] and
                      s["time"]["end_sec"]<=ei[eid]["time"]["end_sec"]+1.2,f"{s['id']}: unexplained state time","time")
            check(s["kind"]!="observation" or s["before"] is None,f"{s['id']}: observation must not infer a before state","state_history")
            validate_fact(s,s["id"])
    raw=json.loads(read("source/annotations.json"))
    for i,r in enumerate(records):
        check(r["source_index"]==i and r["id"]==f"R{i+1:02}",f"{r['id']}: bad source index","provenance")
        check(r["text"]==raw["texts"][i] and r["text_type"]==raw["text_types"][i] and
              r["time"]["start_sec"]==r["time"]["end_sec"]==raw["text_timestamps"][i],
              f"{r['id']}: original text/type/exact timestamp changed","provenance")
        check(set(r["event_ids"])<=set(ei),f"{r['id']}: dangling mapped event ID","references")
        check(r["evidence_id"] in vi and vi[r["evidence_id"]].get("original_text")==r["text"],f"{r['id']}: bad raw text evidence","provenance")
        for eid in r["event_ids"]:
            if eid in ei:
                check(r["id"] in ei[eid]["ego_mc_record_ids"],f"{r['id']}/{eid}: missing reverse map","references")
    event_rows=table(BASE,"## B.",r"E\d{3}"); object_rows=table(BASE,"## C.",r"O\d{2}")
    verify_rows=table(VERIFY,"## B.",r"E\d{3}"); map_rows=table(CROSS,"## B.",r"R\d{2}")
    for eid,row in event_rows.items():
        if eid in ei:
            check(ei[eid]["original_candidate"]["raw_row"]==row["raw"],f"{eid}: original candidate row changed","provenance")
            check(ei[eid]["verification"]["raw_row"]==verify_rows[eid]["raw"],f"{eid}: raw verification row changed","provenance")
            fields=["id","start_time","end_time","action","actor","target","description","state_change","certainty"]
            check([ei[eid]["original_candidate"][k] for k in fields]==row["cells"],f"{eid}: structured original candidate changed","provenance")
    for oid,row in object_rows.items():
        if oid in oi:
            check(oi[oid]["original_candidate"]["raw_row"]==row["raw"],f"{oid}: original object row changed","provenance")
    for rid,row in map_rows.items():
        if rid in ri:
            check(ri[rid]["mapping_raw_row"]==row["raw"],f"{rid}: original crosscheck mapping changed","provenance")
    # Field targets resolve to actual unconfirmed facts or state entries.
    covered=set()
    for item in queue:
        for key,lookup in [("event_ids",ei),("object_ids",oi),("ego_mc_record_ids",ri)]:
            check(set(item[key])<=set(lookup),f"{item['id']}: dangling {key}","review_queue")
        for target in item["targets"]:
            art,rid,field=target["artifact"],target["record_id"],target["field"]
            if rid=="video":
                check(art=="events" and field=="reported_evidence_range",f"{item['id']}: invalid video target","review_queue")
                continue
            lookup=ei if art=="events" else oi
            collection,key=field.split("/",1) if "/" in field else ("","")
            candidates=lookup.get(rid,{}).get(collection,[])
            match=next((x for x in candidates if x.get("id",x.get("field"))==key),None)
            check(match is not None and match["status"]=="UNCERTAIN",f"{item['id']}: invalid/unneeded target {rid}/{field}","review_queue")
            covered.add((art,rid,field))
    for ev in events:
        for f in ev["facts"]:
            if f["status"]=="UNCERTAIN":
                check(("events",ev["id"],"facts/"+f["field"]) in covered,f"{ev['id']}/{f['field']}: uncertainty missing from review queue","review_queue")
    for obj in objects:
        for collection in ("facts","state_history"):
            for entry in obj[collection]:
                if entry["status"]=="UNCERTAIN":
                    key=entry.get("id",entry.get("field"))
                    check(("objects",obj["id"],collection+"/"+key) in covered,f"{obj['id']}/{key}: uncertainty missing from review queue","review_queue")
    def get_fact(n,field):
        return next(f for f in ei[f"E{n:03}"]["facts"] if f["field"]==field)
    for n,field in [(7,"taken_count"),(8,"lid_latched"),(12,"third_egg_integrity"),(13,"returned_inside_carton"),
                    (20,"same_cup_as_E015"),(37,"heating_duration_sec"),(41,"heating_duration_sec"),
                    (42,"solid_fraction"),(43,"butter_fully_melted_after_stirring"),(49,"inner_wall_oil_film"),
                    (54,"sugar_bag_inserted_during_event")]:
        check(get_fact(n,field)["status"]=="UNCERTAIN",f"E{n:03}/{field}: critical uncertainty promoted","critical_facts")
    check(ei["E049"]["time"]["start_sec"]==560 and ei["E049"]["time"]["end_sec"]==581,"E049 must cover 09:20–09:41","critical_facts")
    check(ei["E054"]["action"]=="盖回粉色罐盖","E054 must only retain the lid-closing action","critical_facts")
    check(get_fact(42,"butter_phase")["value"]=="以液体为主、仍见固态块","E042 corrected phase must retain solid blocks","critical_facts")
    check([ev["id"] for ev in events if any(f["field"]=="flour_addition_to_mixing_container" for f in ev["facts"])]==["E032","E051"],
          "Flour additions must count only E032 and E051, not E031","critical_facts")
    counts=dict(Counter(ev["verification"]["original_claim_status"] for ev in events))
    check(counts=={"SUPPORTED":45,"CONTRADICTED":1,"UNCERTAIN":10},"Historical verification tally must be 45/1/10","statistics")
    for key,actual in [("event_count",len(events)),("ego_mc_record_count",len(records)),("original_claim_status",counts),
       ("current_claim_status",dict(Counter(e["verification"]["current_claim_status"] for e in events))),
       ("evidence_kind",dict(Counter(e["kind"] for e in evidence))),
       ("ego_mc_type_count",dict(Counter(r["text_type"] for r in records)))]:
        check(ed["statistics"][key]==actual,f"Event statistic mismatch: {key}","statistics")
    for key,actual in [("object_record_count",len(objects)),("state_entry_count",len(states)),
                       ("state_status",dict(Counter(s["status"] for s in states)))]:
        check(od["statistics"][key]==actual,f"Object statistic mismatch: {key}","statistics")
    check(qd["statistics"]["review_item_count"]==len(queue) and qd["statistics"]["priority"]==dict(Counter(x["priority"] for x in queue)),
          "Review statistics mismatch","statistics")
    check(abs(ed["video"]["uncovered_tail_sec"]-(duration-696.2))<0.000001,"Reported tail gap mismatch","time")
    notes.append("报告采样范围696.2s与文件元数据时长696.929567s不同，尾部缺口保留在RQ14。")
    notes.append("事件重叠可由结果帧、停机子动作或近似边界造成；不强制把时间线切成互斥区间。")
    if check_inputs:
        manifest={s["path"]:s for s in ed["sources"]}
        check(set(manifest)==set(INPUT_HASHES),"Source manifest must contain exactly seven inputs","input_integrity")
        for path,expected in INPUT_HASHES.items():
            check(digest(EP/path)==expected,f"Input SHA256 changed: {path}","input_integrity")
            check(manifest.get(path,{}).get("sha256")==expected,f"Manifest hash mismatch: {path}","input_integrity")
    return {"passed":not errors,"errors":errors,"notes":list(dict.fromkeys(notes)),"checks":dict(checks),
            "check_count":sum(checks.values())}


def negative_checks(documents,schema):
    cases=[]
    def case(name,mutate):
        docs=copy.deepcopy(documents)
        mutate(docs)
        result=validate(docs,schema,check_inputs=False)
        cases.append({"case":name,"rejected":not result["passed"],"first_error":next(iter(result["errors"]),None)})
    case("out_of_video_time",lambda d:d["events"]["events"][0]["time"].update(end_sec=800,end_hms=stamp(800)))
    case("duplicate_event_id",lambda d:d["events"]["events"][1].update(id="E001"))
    case("dangling_object_reference",lambda d:d["events"]["events"][0]["object_ids"].append("O99"))
    case("dangling_evidence_reference",lambda d:d["events"]["events"][0]["facts"][0]["evidence_ids"].append("MISSING"))
    case("wrong_evidence_grade",lambda d:d["events"]["evidence"][0].update(grade="T"))
    case("invalid_event_status",lambda d:d["events"]["events"][0]["verification"].update(current_claim_status="GOLD"))
    case("E042_current_claim_inherits_contradicted",lambda d:d["events"]["events"][41]["verification"].update(current_claim_status="CONTRADICTED"))
    case("restore_E057",lambda d:d["events"]["events"].append(dict(d["events"]["events"][-1],id="E057")))
    def promote(d,n,field):
        next(f for f in d["events"]["events"][n-1]["facts"] if f["field"]==field)["status"]="REPORTED_SUPPORTED"
    case("V2_egg_count_promoted",lambda d:promote(d,7,"taken_count"))
    case("oil_film_promoted",lambda d:promote(d,49,"inner_wall_oil_film"))
    case("E054_insertion_action_added",lambda d:d["events"]["events"][53].update(action="插入糖袋并盖回粉色罐盖"))
    case("original_candidate_changed",lambda d:d["events"]["events"][0]["original_candidate"].update(description="改写原候选"))
    case("uncertainty_review_item_removed",lambda d:d["review_queue"]["review_items"].pop(0))
    return cases


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser=argparse.ArgumentParser(); parser.add_argument("--self-test",action="store_true"); args=parser.parse_args()
    docs={name:json.loads((ANN/f"{name}.json").read_text(encoding="utf-8")) for name in ("events","objects","review_queue")}
    schema=json.loads((ANN/"schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    result=validate(docs,schema)
    if args.self_test:
        result["negative_checks"]=negative_checks(docs,schema)
        result["negative_checks_passed"]=all(x["rejected"] for x in result["negative_checks"])
        result["passed"]=result["passed"] and result["negative_checks_passed"]
    (REP/"validation_results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    write_merge_report(docs,result)
    print(json.dumps({k:v for k,v in result.items() if k!="notes"},ensure_ascii=False,indent=2))
    raise SystemExit(0 if result["passed"] else 1)


def write_merge_report(docs,result):
    ed,od,qd=(docs[k] for k in ("events","objects","review_queue"))
    evs=ed["events"]; obs=od["objects"]
    fact_count=sum(len(e["facts"]) for e in evs)+sum(len(o["facts"]) for o in obs)
    uncertain_event_fields=sum(f["status"]=="UNCERTAIN" for e in evs for f in e["facts"])
    uncertain_object_fields=sum(f["status"]=="UNCERTAIN" for o in obs for f in o["facts"])
    summary=od["statistics"]
    evidence_counts=ed["statistics"]["evidence_kind"]
    negative=result.get("negative_checks",[])
    check_rows="\n".join(f"| {name} | {count} |" for name,count in result["checks"].items())
    queue_rows="\n".join(f"| {i['id']} | {i['priority']} | {i['title']} | {', '.join(i['event_ids'])} |" for i in qd["review_items"])
    priorities=qd["statistics"]["priority"]
    hashes="\n".join(f"| `{s['path']}` | `{s['sha256']}` |" for s in ed["sources"])
    status="PASS" if result["passed"] else "FAIL"
    failures="\n".join("- "+err for err in result["errors"]) or "无错误。"
    note_rows="\n".join("- "+note for note in result["notes"])
    md=f"""# GX010021 Golden Episode 候选事实整合报告

生成日期：2026-10-08（Asia/Shanghai）。本次产物为 **CANDIDATE / NOT_REVIEWED**。历史 Qwen 报告的 SUPPORTED 仅代表 AI 报告核验结果；本次整合与自动校验均不构成人工 Gold。人工 Gold 数量为 0。

## 交付与统计

| 产物 | 内容 |
|---|---|
| [events.json](../annotations/v1_candidate/events.json) | E001–E056，56 条；原候选完整保留，关联证据、对象、状态节点、Ego-MC 原文及修订依据 |
| [objects.json](../annotations/v1_candidate/objects.json) | {summary['object_record_count']} 条对象引用记录：15 条原始 O01–O15 + 7 条补充指称；{summary['state_entry_count']} 条状态节点 |
| [review_queue.json](../annotations/v1_candidate/review_queue.json) | 14 项 OPEN：P0×{priorities.get('P0',0)}、P1×{priorities.get('P1',0)}、P2×{priorities.get('P2',0)}；全部不确定字段可定位到复核目标 |
| [schema.json](../annotations/v1_candidate/schema.json) | JSON Schema Draft 2020-12；三类产物共用 time / source / fact / revision 定义 |
| [build.py](../scripts/build.py) | 可重跑的只读输入整合脚本；读取 ffprobe 元数据，不解码视频帧 |
| [validate.py](../scripts/validate.py) | Schema、语义一致性与输入 SHA-256 校验；负例检查在内存执行 |
| [validation_results.json](validation_results.json) | 最终校验结果和边界/覆盖说明 |

- 原始主张的报告核验状态：45 SUPPORTED、1 CONTRADICTED（E042）、10 UNCERTAIN（E007/E008/E012/E019/E020/E029/E037/E041/E043/E049）。
- 整合后候选状态：45 REPORTED_SUPPORTED、1 CORRECTED_CANDIDATE（E042）、10 UNCERTAIN；所有事件均 NOT_REVIEWED。
- 证据注册表共 {len(ed['evidence'])} 条：所报视觉观察 {evidence_counts['reported_visual_observation']}（V1）、模型推断 {evidence_counts['model_inference']}（V2）、第一轮文本继承 {evidence_counts['inherited_candidate_text']}（T）、Ego-MC 原始文本 {evidence_counts['ego_mc_text']}（TEXT）。这些是溯源记录数，不能解读为独立帧数或人工裁决数。
- 事件/对象 facts 合计 {fact_count} 个，其中事件字段 {uncertain_event_fields} 个 UNCERTAIN、对象品牌字段 {uncertain_object_fields} 个 UNCERTAIN；对象状态节点 {summary['state_status'].get('REPORTED_SUPPORTED',0)} 个 REPORTED_SUPPORTED、{summary['state_status'].get('UNCERTAIN',0)} 个 UNCERTAIN。状态未知字段与事件未知字段是互相关联的不同视图，不能相加当独立争议数。
- 原始 annotations.json 的 55 条文本、类型、精确时间（含毫秒）按 source_index 0–54 完整保留；R01–R55 是稳定派生 ID，不是原文件原生 ID。类型分布复算与交叉核验一致：Instruction 12、User-Comment 11、Success 12、Feedback 7、Instruction-Clarification 7、User-Question 6。
- 新增操作事件 0。E057/E058 未恢复。可见面粉进入混合容器次数仅 2（E032/E051），E031 是袋到量杯的上游量取。

## 输入与修订顺序

实际输入为本 Episode `source/` 下的 `GX010021.MP4`、`annotations.json`，以及 `annotation_reports/` 中五份 Markdown。SHA-256 初始快照已写入事件文件的 sources；最终重新计算七个输入哈希，全部保持一致。仅做过目录归位，未修改、复制任何输入内容。

按 [归档说明](../annotation_reports/README.md) 的规则执行：第一轮建立稳定 ID → 第二轮保留原核验表和修正建议 → 第三轮覆盖错误时间/统计/去重/证据级别 → 第四轮应用明确的局部修订。较晚文本只有在其明确修订的字段生效，不能抹掉证据限制。README 负责解释合并规则，不是新增视觉证据。

第二轮 E054 同一行既有最初 CONTRADICTED 又有末尾 SUPPORTED 自我纠正，完整原行保存在 verification.raw_row；最终原始主张状态使用第三轮明确确认的 SUPPORTED。第二轮最初概览的 44/2/10 与最终 45/1/10 冲突以第三轮为准。

## 关键修正

| 范围 | 整合结果与依据 |
|---|---|
| E042 / O09 | 原“完全融化”主张为 CONTRADICTED；修正候选“液态为主、仍见浅色固块”标 CORRECTED_CANDIDATE。固块存在的所报观察保留，残留比例/搅拌终态/倒入时固块未知。R32 Success 不改变视觉主张。 |
| E007/E012/E013 / O02/O03/O20 | 3 枚累计取出是 V2 + R10 线索，仍 UNCERTAIN；两枚敲入与两个蛋黄保留所报观察。第三枚磕/掰样动作不等于确定破损；空手离开盒侧不等于已入盒；不固定后段蛋壳总数为两份。 |
| O05 / O16/O17 | O05 保持原量杯组 ID；O16 是 E043 工具观察，O17 是 E053 工具观察。SAME_AS_UNKNOWN 同时涵盖工具相互之间及与量杯组的关系，既不认定同一件，也不证明不同件。 |
| E019 / O04/O18 | 整理/按压与具体折口、插入、开关罐盖分开；具体内容未知。 |
| E020/E022/E023 | 144.2s “1/4 CUP”是标签观察；R19 “寻找半杯”只作用途线索。不能把该标签回推到加糖或实际倒奶杯规格/量值。 |
| E037/E041 / O11 | 两次关门按键流程保留；15秒、面板读数与运行时长为 T + Ego-MC 线索，实际值为 null / UNCERTAIN；第二次等待末界约±1s。 |
| E049 / O12 | 时间提前至 00:09:20–00:09:41（560–581s），涵盖560.2–562.2s倒油与567.2–579.2s倾斜旋转；内壁油膜仍未知。E053 不继承“已抹油”作为确定状态。 |
| E054 / O04/O18/O01/O17 | 只保留盖回粉色罐盖；680.2s糖袋已在罐内与刮刀已在混合容器内作为 observation 状态。没有认定本段插入糖袋或放置刮刀动作。 |
| E057/E058 | E057 撤销，盖盖观察归 E054；其插入动作被第四轮排除，仅存 O04 已在罐内的状态。E058 撤销，空玻璃容器置灶面保留 E044/O10 的结果节点。 |
| E032/E051 / O08/O15 | 加粉入混合容器仅两次；不恢复第三次无证据加入。E032 后抽样帧未见立即搅拌；O15 的干粉层节点与E045出现稠糊的节点分开。 |
| R39/R41/R35/R37/R46 | 烘焙纸、黄油抹模建议没有对应可见动作，不建立事件/对象。重复催促和被推迟的转移指令只保存文字上下文；R37/R46另链接最终实际转移E053，仍不作执行证据。 |

O18（粉盖罐）、O19（白碗）、O20（蛋盒）、O21（黄油包装）、O22（白色纸盒）补足既有事件的对象引用。总计22条是引用记录数量，不是已确认的物理实体数；无法确定物理实体总数。

## 时间修正与元数据差异

时间统一为绝对秒 + `HH:MM:SS.mmm`；自动检查两种表达严格等值。第三轮原文宣称33处修正（包括重复C/D/E表引用），本次不把33当作重新发现的独立错误计数；具体规范化涉及E035–E054的20条事件证据记录，原错误原文仍完整保留。

例如，`529.2–531.2s`按原表语境修正为329.2–331.2s；`630.2s End`修正为390.2s，而630.2s的真实报告内容为面糊表面；E051原`995.2–1002.2s`逐项采用第三轮映射为595.2–602.2s，不能作通用“去冒号”数值算法。低于696.2的错误值也已修正，未采用“只改超限值”的阈值策略。

明确调整了6条事件的边界：

| 事件 | 原候选区间 | 整合区间 |
|---|---|---|
| E027 | 03:20–03:54 | 03:19–03:55 |
| E034 | 05:01–05:19 | 05:03–05:19 |
| E049 | 09:26–09:41 | 09:20–09:41 |
| E051 | 09:52–10:04 | 09:55–10:04 |
| E053 | 10:32–11:19 | 10:33–11:19 |
| E055 | 11:26–11:32 | 11:27–11:32 |

E014 保留第一轮01:30–01:37，拿糖袋帧95.2s在该候选范围内；不把第二轮自指“01:34→01:34”当明确边界修订。E030同理保留04:19–04:28，以260.2–267.2s证据说明动作。E029原04:00–04:18范围宽于已给伸触证据，不自行裁切。E046保留08:50–09:00，而非原核验误写的850–900绝对秒。

`ffprobe`仅读取容器/流元数据：时长 **{ed['video']['duration_sec']}s**，视频流H.264、854×480、30000/1001fps，nb_frames=20887。这个nb_frames是视频流元数据，不能当历史模型抽样帧数。报告声称的抽样证据范围为0.2–696.2s；末尾 **{ed['video']['uncovered_tail_sec']}s** 未被报告覆盖，列RQ14。本次不解码、不重标注，也不自动延长E056到实际视频末尾。

秒级事件区间与小数结果帧不总相互包含。E002末界14s而显示100结果帧15.2s，E044末界469s而空置结果帧470.2s，作为有来源的 aftermath 保存。其他0.2s末界偏移保留近似区间。相邻事件可以重叠，不能因整齐化而补造新的精确边界。

## Schema与溯源使用

三个JSON共用 schema_version / episode_id / artifact / data_status / human_review。events.json保存中央 evidence 注册表，objects.json 和 review_queue.json通过 evidence_ids 引用同一注册表。

- 事件的 original_candidate 保留第一轮全部字段及原行；time_status=APPROXIMATE明确全部候选边界为近似时间；verification 保存第二轮原行与历史/当前主张状态；revisions 保存字段修改前后、原因与实际文件/行或章节。
- facts 的 field / value / status / evidence_ids / reason统一表示字段断言；null表示未确认，不等于否定。原文数量3等可以作为UNCERTAIN候选值保存；文本意图也保持UNCERTAIN，不当视觉观察。
- 对象 state_history 通过 event_id、时间和证据定位；事件 state_change_ids反向引用。kind=observation只观察当时状态，before=null，不反推插入或放置动作。transition也允许before=null，表示未断言前态。
- reported_visual_observation(V1)只表示历史AI报告称可见；model_inference(V2)、inherited_candidate_text(T)、ego_mc_text(TEXT)分别存储。V2/T不能自动升格为REPORTED_SUPPORTED；文字可以与V1并存佐证，但没有V1的字段不能被文字单独确证。
- Ego-MC原文的精确时间与候选事件边界是上下文映射，不要求言语与动作同时发生；映射类别/前置/末尾信息仍保留。字段补充引用的文字同步补足双向映射，并在notes记录补充语境；不改原始映射行。糖/奶/面粉/黄油数量文字直接引用Ego-MC证据，不误分类为第一轮文本继承。
- review_queue targets定位events事实字段、objects状态ID或品牌字段，并全部保持OPEN。human_review/verification.human_status都为NOT_REVIEWED。

## 自动校验结果

最终结果：**{status}**；错误{len(result['errors'])}条；执行{result.get('check_count',0)}项断言，含3份JSON的Schema入口检查。成功判定只涉及结构/引用/溯源/约束一致性，不能证明视频事实本身正确。

| 类别 | 断言数 |
|---|---|
{check_rows}

检查涵盖时间范围与双格式、ID唯一性、全部对象/状态/证据/文本引用及反向关系、证据种类与级别、历史与当前事件状态分离、状态顺序、字段不确定性到复核队列的覆盖、统计复算和七个输入哈希。

负例检查 **{sum(x['rejected'] for x in negative)}/{len(negative)}**被正确拒绝，全部为内存副本：越界时间、重复事件ID、悬空对象/证据、错误证据级别、无效事件状态、E042当前主张继承CONTRADICTED、恢复E057、V2计数升格、油膜升格、E054补插入动作、改写原候选、删除必要复核项。未修改最终数据或输入。

{failures}

运行命令（项目根目录，Python和现有jsonschema，ffprobe已在PATH）：

```powershell
python golden_episode/GX010021/scripts/build.py
python golden_episode/GX010021/scripts/validate.py --self-test
```

build.py为可重跑整合，先校验初始输入哈希；validate.py同时更新validation_results.json与本报告。若输入改变会拒绝按旧快照重建，避免把历史溯源悄然换掉。

非错误边界/覆盖说明：

{note_rows}

## 待复核问题

| ID | 优先级 | 问题 | 关联事件 |
|---|---|---|---|
{queue_rows}

油膜在第二/第三轮为P0、第四轮D表为P1，本次采用第四轮明确的P1并保留历史差异，字段继续UNCERTAIN。鸡蛋/奶杯/粉杯在第四轮C与D节存在P2与更高片段优先级差异，采用D节专门的复核片段清单。工具身份等第四轮没有覆盖的问题沿用较早优先级；优先级变化不改变字段确定性。

不生成SOP、异常标签或任何Track评测题目；未调用视频模型，未重新标注视频，未执行原始Instruction。证据不足的字段继续保留未知或候选值，人工连续视频裁决应在后续独立流程中记录，当前没有人工Gold。

## 输入完整性快照

| 输入实际相对路径 | SHA-256（整合前后相同） |
|---|---|
{hashes}
"""
    (REP/"merge_report.md").write_text(md,encoding="utf-8")


if __name__=="__main__":
    main()
