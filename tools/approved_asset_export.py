#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

SCHEMA="TAKY_APPROVED_ASSET_EXPORT_V1"

def export(entries:list[dict])->dict:
    out=[];seen=set();errors=[]
    for i,e in enumerate(entries or []):
        if e.get("approval_status")!="APPROVED":
            continue
        p=str(e.get("asset_pointer","")).strip()
        if not p:
            errors.append(f"{i}:POINTER_MISSING");continue
        if p in seen:
            errors.append(f"{i}:POINTER_DUPLICATE");continue
        seen.add(p)
        sha=str(e.get("sha256",""))
        if len(sha)!=64 or any(c not in "0123456789abcdefABCDEF" for c in sha):
            errors.append(f"{i}:SHA_INVALID");continue
        if not str(e.get("runtime_url","")).strip():
            errors.append(f"{i}:RUNTIME_URL_MISSING");continue
        if not str(e.get("visual_id","")).strip():
            errors.append(f"{i}:VISUAL_ID_MISSING");continue
        if not str(e.get("producer_pointer","")).strip():
            errors.append(f"{i}:PRODUCER_POINTER_MISSING");continue
        out.append({
          "asset_pointer":p,
          "asset_id":e.get("asset_id"),
          "visual_id":e.get("visual_id"),
          "approval_status":"APPROVED",
          "sha256":sha,
          "runtime_url":e.get("runtime_url"),
          "producer_pointer":e.get("producer_pointer")
        })
    return {"schema":SCHEMA,"pass":not errors,"assets":out,"detected":errors}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("source");ap.add_argument("--out")
    a=ap.parse_args()
    raw=json.loads(Path(a.source).read_text(encoding="utf8"))
    entries=raw.get("assets",raw if isinstance(raw,list) else [])
    result=export(entries)
    payload=json.dumps(result,ensure_ascii=False,indent=2)+"\n"
    if a.out:Path(a.out).write_text(payload,encoding="utf8")
    print(payload,end="")
    return 0 if result["pass"] else 1
if __name__=="__main__":raise SystemExit(main())
