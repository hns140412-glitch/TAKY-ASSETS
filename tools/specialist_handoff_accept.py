#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

SCHEMA="TAKY_SPECIALIST_TO_ASSET_REGISTRY_HANDOFF_V1"

def validate(x:dict)->list[str]:
    e=[]
    if x.get("schema")!=SCHEMA:e.append("SCHEMA_INVALID")
    for k in ("pipeline_owner","pipeline_receipt_ref","asset_id","visual_id","approval_status","binary_sha256","runtime_url","handoff_sha256"):
        if not x.get(k):e.append(k.upper()+"_MISSING")
    if x.get("approval_status")!="APPROVED":e.append("NOT_APPROVED")
    forbidden=("pipeline_state","retry_count","generation_prompt","qa_queue","next_action")
    for k in forbidden:
        if k in x:e.append("PRODUCTION_STATE_LEAK:"+k)
    return e

def main():
    ap=argparse.ArgumentParser();ap.add_argument("handoff")
    a=ap.parse_args()
    x=json.loads(Path(a.handoff).read_text(encoding="utf8"))
    e=validate(x)
    print(json.dumps({"pass":not e,"detected":e},ensure_ascii=False,indent=2))
    return 1 if e else 0
if __name__=="__main__":raise SystemExit(main())
