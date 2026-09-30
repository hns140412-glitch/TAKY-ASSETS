#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, mimetypes, sys
from pathlib import Path

SCHEMA="TAKY_ASSET_PIPELINE_V1"
REQUIRED_TOP=("schema","asset_id","source","approval","classification","consumers")

def sha256(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def safe(root:Path, rel:str)->Path:
    p=(root/rel).resolve()
    p.relative_to(root.resolve())
    return p

def validate_manifest(m:dict, root:Path)->list[str]:
    e=[]
    for k in REQUIRED_TOP:
        if k not in m:e.append("MISSING_"+k.upper())
    if m.get("schema")!=SCHEMA:e.append("SCHEMA_INVALID")
    if not str(m.get("asset_id","")).strip():e.append("ASSET_ID_MISSING")
    cls=m.get("classification")
    if cls not in {"APPROVED_ORIGINAL","APPROVED_LAYER","DERIVED_RUNTIME_COPY","GOLDEN_REFERENCE_ONLY"}:
        e.append("CLASSIFICATION_INVALID")
    src=m.get("source") or {}
    for k in ("path","sha256"):
        if not str(src.get(k,"")).strip():e.append("SOURCE_"+k.upper()+"_MISSING")
    if src.get("path"):
        try:
            p=safe(root,src["path"])
            if not p.is_file() or p.stat().st_size==0:e.append("SOURCE_BINARY_MISSING")
            elif src.get("sha256") and sha256(p).lower()!=str(src["sha256"]).lower():
                e.append("SOURCE_SHA_MISMATCH")
        except Exception:e.append("SOURCE_PATH_INVALID")
    appr=m.get("approval") or {}
    for k in ("authority_ref","status"):
        if not str(appr.get(k,"")).strip():e.append("APPROVAL_"+k.upper()+"_MISSING")
    if appr.get("status")!="APPROVED":e.append("APPROVAL_NOT_APPROVED")
    vid=m.get("visual_id")
    if cls in {"APPROVED_ORIGINAL","APPROVED_LAYER","DERIVED_RUNTIME_COPY"} and not str(vid or "").strip():
        e.append("VISUAL_ID_MISSING")
    layers=m.get("layers",[])
    if layers is not None and not isinstance(layers,list):e.append("LAYERS_INVALID")
    for i,x in enumerate(layers or []):
        if not isinstance(x,dict):e.append(f"LAYER_{i}_INVALID");continue
        for k in ("role","path","sha256"):
            if not str(x.get(k,"")).strip():e.append(f"LAYER_{i}_{k.upper()}_MISSING")
        if x.get("path"):
            try:
                p=safe(root,x["path"])
                if not p.is_file():e.append(f"LAYER_{i}_BINARY_MISSING")
                elif x.get("sha256") and sha256(p).lower()!=str(x["sha256"]).lower():
                    e.append(f"LAYER_{i}_SHA_MISMATCH")
            except Exception:e.append(f"LAYER_{i}_PATH_INVALID")
    consumers=m.get("consumers")
    if not isinstance(consumers,list) or not consumers:e.append("CONSUMERS_MISSING")
    for i,c in enumerate(consumers or []):
        if not isinstance(c,dict):e.append(f"CONSUMER_{i}_INVALID");continue
        for k in ("repo","runtime_key","status"):
            if not str(c.get(k,"")).strip():e.append(f"CONSUMER_{i}_{k.upper()}_MISSING")
        if c.get("status") not in {"PLANNED","BOUND","VERIFIED"}:e.append(f"CONSUMER_{i}_STATUS_INVALID")
    if m.get("runtime_ready") is True:
        if any(c.get("status")!="VERIFIED" for c in consumers or [] if isinstance(c,dict)):
            e.append("RUNTIME_READY_WITH_UNVERIFIED_CONSUMER")
        if not m.get("integrity_verified"):e.append("RUNTIME_READY_WITHOUT_INTEGRITY")
    return e

def make_manifest(args):
    root=Path(args.root).resolve()
    p=safe(root,args.source)
    if not p.is_file():raise SystemExit("SOURCE_BINARY_MISSING")
    m={
      "schema":SCHEMA,
      "asset_id":args.asset_id,
      "visual_id":args.visual_id,
      "classification":args.classification,
      "source":{"path":args.source,"sha256":sha256(p),"bytes":p.stat().st_size,"mime":mimetypes.guess_type(p.name)[0] or "application/octet-stream"},
      "approval":{"authority_ref":args.authority_ref,"status":"APPROVED"},
      "layers":[],
      "consumers":[{"repo":r,"runtime_key":args.runtime_key,"status":"PLANNED"} for r in args.consumer],
      "integrity_verified":True,
      "runtime_ready":False
    }
    Path(args.out).write_text(json.dumps(m,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(m,ensure_ascii=False,indent=2))

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    v=sp.add_parser("validate");v.add_argument("manifest");v.add_argument("--root",default=".")
    i=sp.add_parser("intake")
    i.add_argument("--root",default=".");i.add_argument("--source",required=True);i.add_argument("--asset-id",required=True)
    i.add_argument("--visual-id");i.add_argument("--classification",default="APPROVED_ORIGINAL",
      choices=["APPROVED_ORIGINAL","APPROVED_LAYER","DERIVED_RUNTIME_COPY","GOLDEN_REFERENCE_ONLY"])
    i.add_argument("--authority-ref",required=True);i.add_argument("--consumer",action="append",required=True)
    i.add_argument("--runtime-key",required=True);i.add_argument("--out",required=True)
    a=ap.parse_args()
    if a.cmd=="intake":make_manifest(a);return 0
    m=json.loads(Path(a.manifest).read_text(encoding="utf-8"))
    e=validate_manifest(m,Path(a.root))
    print(json.dumps({"pass":not e,"detected":e},ensure_ascii=False,indent=2))
    return 1 if e else 0
if __name__=="__main__":raise SystemExit(main())
