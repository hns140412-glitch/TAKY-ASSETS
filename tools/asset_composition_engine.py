#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SCHEMA="TAKY_ASSET_COMPOSITION_REGISTRY_V1"
ALLOWED_ROLES={"BODY","FACE","ARM","HAND","PROP","EQUIPMENT","EFFECT"}

def sha256(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(root:Path,rel:str)->Path:
    p=(root/rel).resolve();p.relative_to(root.resolve());return p

def validate_registry(reg:dict,root:Path)->list[str]:
    e=[]
    if reg.get("schema")!=SCHEMA:e.append("SCHEMA_INVALID")
    chars=reg.get("characters")
    if not isinstance(chars,list) or not chars:return e+["CHARACTERS_MISSING"]
    ids=set()
    for ci,c in enumerate(chars):
        cid=str(c.get("character_id","")).strip();vid=str(c.get("visual_id","")).strip()
        if not cid or cid in ids:e.append(f"CHAR_{ci}_ID_INVALID_OR_DUPLICATE")
        ids.add(cid)
        if not vid:e.append(f"{cid}:VISUAL_ID_MISSING")
        parts=c.get("parts")
        if not isinstance(parts,list) or not parts:e.append(f"{cid}:PARTS_MISSING");continue
        for pi,p in enumerate(parts):
            role=p.get("role")
            if role not in ALLOWED_ROLES:e.append(f"{cid}:PART_{pi}_ROLE_INVALID")
            for k in ("part_id","path","sha256","state"):
                if not str(p.get(k,"")).strip():e.append(f"{cid}:PART_{pi}_{k.upper()}_MISSING")
            try:
                fp=safe(root,str(p.get("path","")))
                if not fp.is_file() or fp.stat().st_size==0:e.append(f"{cid}:PART_{pi}_BINARY_MISSING")
                elif p.get("sha256") and sha256(fp).lower()!=str(p["sha256"]).lower():
                    e.append(f"{cid}:PART_{pi}_SHA_MISMATCH")
            except Exception:e.append(f"{cid}:PART_{pi}_PATH_INVALID")
        fb=c.get("fallback") or {}
        if fb:
            if fb.get("character_id") not in {None,cid}:e.append(f"{cid}:CROSS_CHARACTER_FALLBACK_FORBIDDEN")
            if not str(fb.get("part_id","")).strip():e.append(f"{cid}:FALLBACK_PART_MISSING")
    return e

def resolve(reg:dict,req:dict)->dict:
    cid=req.get("character_id"); action=req.get("action")
    chars={c.get("character_id"):c for c in reg.get("characters",[])}
    if cid not in chars:return {"pass":False,"error":"CHARACTER_NOT_FOUND"}
    c=chars[cid]
    by_role={}
    for p in c.get("parts",[]):by_role.setdefault(p.get("role"),[]).append(p)
    required=req.get("required_roles",[])
    chosen=[];missing=[]
    for role in required:
        candidates=[p for p in by_role.get(role,[]) if p.get("state")=="APPROVED" and (not p.get("actions") or action in p.get("actions",[]))]
        if candidates:chosen.append(candidates[0]);continue
        missing.append(role)
    if missing:
        fb=c.get("fallback") or {}
        if fb.get("character_id") in (None,cid) and fb.get("part_id"):
            part=next((p for p in c.get("parts",[]) if p.get("part_id")==fb.get("part_id") and p.get("state")=="APPROVED"),None)
            if part:
                return {"pass":True,"character_id":cid,"visual_id":c.get("visual_id"),"action":action,
                        "composition":[part],"fallback_used":True,"missing_roles":missing,
                        "generation_allowed":False}
        return {"pass":False,"error":"APPROVED_PART_MISSING","character_id":cid,"action":action,
                "missing_roles":missing,"generation_allowed":False}
    return {"pass":True,"character_id":cid,"visual_id":c.get("visual_id"),"action":action,
            "composition":chosen,"fallback_used":False,"generation_allowed":False}

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest="cmd",required=True)
    v=sp.add_parser("validate");v.add_argument("registry");v.add_argument("--root",default=".")
    r=sp.add_parser("resolve");r.add_argument("registry");r.add_argument("request")
    a=ap.parse_args()
    reg=json.loads(Path(a.registry).read_text(encoding="utf-8"))
    if a.cmd=="validate":
        e=validate_registry(reg,Path(a.root));print(json.dumps({"pass":not e,"detected":e},ensure_ascii=False,indent=2));return 1 if e else 0
    out=resolve(reg,json.loads(Path(a.request).read_text(encoding="utf-8")))
    print(json.dumps(out,ensure_ascii=False,indent=2));return 0 if out.get("pass") else 1
if __name__=="__main__":raise SystemExit(main())
