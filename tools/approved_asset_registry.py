#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SCHEMA="TAKY_APPROVED_ASSET_REGISTRY_V1"
ALLOWED_CLASS={"APPROVED_ORIGINAL","APPROVED_LAYER","APPROVED_DERIVATIVE","GOLDEN_REFERENCE_ONLY"}

def sha256(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def safe(root:Path, rel:str)->Path:
    p=(root/rel).resolve()
    p.relative_to(root.resolve())
    return p

def validate(entry:dict, root:Path)->list[str]:
    e=[]
    if entry.get("schema")!=SCHEMA:e.append("SCHEMA_INVALID")
    if not str(entry.get("asset_id","")).strip():e.append("ASSET_ID_MISSING")
    if entry.get("classification") not in ALLOWED_CLASS:e.append("CLASSIFICATION_INVALID")
    for k in ("production_state","pipeline_state","retry_count","generation_prompt","generation_status",
              "qa_work_queue","next_production_action","art_batch_state","mask_work_state"):
        if k in entry:e.append("PRODUCTION_STATE_OWNERSHIP_VIOLATION:"+k)
    approval=entry.get("approval") or {}
    if approval.get("status")!="APPROVED":e.append("APPROVAL_NOT_APPROVED")
    if not str(approval.get("authority_ref","")).strip():e.append("APPROVAL_AUTHORITY_REF_MISSING")
    source=entry.get("source") or {}
    for k in ("path","sha256"):
        if not str(source.get(k,"")).strip():e.append("SOURCE_"+k.upper()+"_MISSING")
    if source.get("path"):
        try:
            p=safe(root,source["path"])
            if not p.is_file() or p.stat().st_size==0:e.append("SOURCE_BINARY_MISSING")
            elif source.get("sha256") and sha256(p).lower()!=str(source["sha256"]).lower():
                e.append("SOURCE_SHA_MISMATCH")
        except Exception:e.append("SOURCE_PATH_INVALID")
    pointer=entry.get("producer_pointer") or {}
    if not str(pointer.get("pipeline_owner","")).strip():e.append("PIPELINE_OWNER_POINTER_MISSING")
    if not str(pointer.get("evidence_ref","")).strip():e.append("PIPELINE_EVIDENCE_REF_MISSING")
    consumers=entry.get("consumers")
    if not isinstance(consumers,list):e.append("CONSUMERS_INVALID")
    for i,c in enumerate(consumers or []):
        if not isinstance(c,dict):e.append(f"CONSUMER_{i}_INVALID");continue
        for k in ("repo","runtime_key","pointer_status"):
            if not str(c.get(k,"")).strip():e.append(f"CONSUMER_{i}_{k.upper()}_MISSING")
        if c.get("pointer_status") not in {"REGISTERED","BOUND","VERIFIED"}:
            e.append(f"CONSUMER_{i}_POINTER_STATUS_INVALID")
    if entry.get("producer") in {"TAKY-ASSETS","ASSET_REGISTRY"}:
        e.append("REGISTRY_CANNOT_BE_PRODUCER")
    return e

def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest",type=Path)
    ap.add_argument("--root",type=Path,default=Path.cwd())
    a=ap.parse_args()
    entry=json.loads(a.manifest.read_text(encoding="utf-8"))
    errors=validate(entry,a.root)
    print(json.dumps({"pass":not errors,"detected":errors},ensure_ascii=False,indent=2))
    return 1 if errors else 0

if __name__=="__main__":
    raise SystemExit(main())
