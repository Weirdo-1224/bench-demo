"""Offline replay/secret/integrity audit of every real attempt, including failures."""
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import pilot as p
import runtime as r


def main():
    t=r.gold(); r.init_run(t)
    references=[]
    for path in sorted(r.RUN.glob("*/seg-*/attempt-*.response.json")):
        directory=path.parent
        raw=p.read(path);request=p.read(directory/"request.json");m=p.read(directory/"input_manifest.json")
        r.assert_input(t,request["condition"],m["frames"],m["segment"])
        wire=r.wire_request(directory,m,request["prompt"])
        wire["max_tokens"]=raw.get("effective_max_output_tokens",r.CONFIG["max_output_tokens"])
        if r.digest(wire)!=raw["request_sha256"]: raise ValueError("Original wire reconstruction failed: "+str(path))
        b=json.loads(raw["body"]) if raw["body"] else {}
        references.append({"condition":request["condition"],"segment":m["segment"],
            "request_sha256":raw["request_sha256"],"base_request_ref":p.rel(directory/"request.json"),
            "input_manifest_ref":p.rel(directory/"input_manifest.json"),"effective_max_output_tokens":wire["max_tokens"],
            "raw_response_ref":p.rel(path),"raw_response_sha256":r.file_hash(path),"http_status":raw["http_status"],
            "request_id":b.get("id"),"usage":b.get("usage"),"finish_reason":b.get("choices",[{}])[0].get("finish_reason"),
            "elapsed_sec":raw["elapsed_sec"],"estimated_cost_cny":None,"actual_billed_cost_cny":None,
            "source":"REAL_HTTP_RESPONSE; no simulated data"})
    p.write_rows(p.HERE/"request_index_v1.jsonl",references)
    key=r.load_api_key(r.CONFIG);leaks=[];files=0
    for f in p.HERE.rglob("*"):
        if f.is_file() and f.suffix in [".json",".jsonl",".csv",".md",".py",".txt",".log"]:
            files+=1
            if key and key in f.read_text(encoding="utf-8-sig",errors="replace"):leaks.append(p.rel(f))
    if leaks:raise ValueError("Credential leakage detected in: "+", ".join(leaks))
    before=len(r.ledger())
    run=subprocess.run([sys.executable,"-X","utf8",str(p.HERE/"pilot.py"),"run","--task","P01","--condition","ALL","--max-calls","20"],
                       cwd=p.ROOT,capture_output=True)
    (p.HERE/"resume_verification_v1.txt").write_bytes(run.stdout+run.stderr)
    if run.returncode or len(r.ledger())!=before:
        raise ValueError("Zero-new-call resume validation failed; inspect resume_verification_v1.txt")
    used=sum(1 for line in run.stdout.decode("utf-8",errors="replace").splitlines() if '"status": "REUSED"' in line)
    if used!=16:raise ValueError("Expected16 reused logical requests")
    result={"created_at":p.now(),"type":"OFFLINE_REAL_TRACE_QA","all_attempts_reconstruct_exact_wire":len(references),
            "raw_http200":sum(x["http_status"]==200 for x in references),
            "truncated_responses_preserved":sum(x["finish_reason"]=="length" for x in references),
            "unique_request_ids":len({x["request_id"] for x in references}),
            "resume_reused_logical_requests":used,"resume_added_inference_attempts":len(r.ledger())-before,
            "secret_scan_text_files":files,"secret_leaks":0,"original_integrity":p.verify_originals(),
            "conclusion":"Input replay and logs verified; model alias is unpinned, so new cloud inference is not guaranteed bitwise reproducible"}
    p.write(p.HERE/"run_qa_v1.json",result)
    p.write(p.HERE/"audit/integrity_check.json",result["original_integrity"])
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=="__main__":main()
