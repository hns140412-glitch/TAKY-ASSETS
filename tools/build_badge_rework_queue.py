from pathlib import Path
import json, hashlib, sys

TAKY = Path(r"D:\Git PWA\TAKY")
ASSETS = Path(r"D:\Git PWA\TAKY-ASSETS")
SRC = TAKY / "BADGE" / "badge-60-story-20-history-working.json"
OUT = ASSETS / "badges" / "work" / "20261001" / "badge_rework_queue_31.json"

REWORK = [
    1,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21,25,28,
    33,34,40,42,43,44,46,53,55,58,60
]

def sha256(path):
    h=hashlib.sha256(path.read_bytes()).hexdigest()
    return h
def main():
    data=json.loads(SRC.read_text(encoding="utf-8-sig"))
    presets=data.get("presets",[])
    by_slot={int(x["slot"]):x for x in presets}
    if len(REWORK)!=31 or len(set(REWORK))!=31:
        raise SystemExit("FAIL: REWORK list must be exactly 31 unique IDs")
    missing=[n for n in REWORK if n not in by_slot]
    if missing:
        raise SystemExit(f"FAIL: source missing IDs {missing}")

    items=[]
    for n in REWORK:
        x=by_slot[n]
        items.append({
            "slot":n,
            "source_draft_id":x["source_draft_id"],
            "stable_name":x["stable_name"],
            "visual_id":x["visual_id"],
            "motif":x["motif"],
            "source_asset_status":x["asset_status"],
            "production_state":"REWORK_REQUIRED",
            "final_approval":False
        })
    payload={
        "queue_version":"2026-10-01.1",
        "purpose":"BADGE_ASSET_REWORK_ONLY",
        "source_sha256":sha256(SRC),
        "source_path":str(SRC),
        "qa_authority":"BADGE_60_VISUAL_QA_REPORT.md / 2026-09-27",
        "count":len(items),
        "holds":{
            "canonical_change":True,
            "runtime_integration":True,
            "registry_activation":True,
            "deployment":True
        },
        "items":items
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("QUEUE:",OUT)
    print("COUNT:",len(items))
    print("FIRST:",items[0]["source_draft_id"],items[0]["stable_name"])
    print("LAST:",items[-1]["source_draft_id"],items[-1]["stable_name"])
    print("RESULT: PASS")
    return 0

if __name__=="__main__":
    sys.exit(main())
