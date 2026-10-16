from pathlib import Path
from collections import Counter
import json, datetime
root=Path(r"D:\Git PWA")
dest=root/"TAKY-ASSETS"/"registry"
skip={".git","node_modules",".venv","__pycache__","dist","build",".next",".local","coverage"}
extensions={".png",".jpg",".jpeg",".webp",".svg",".gif",".mp3",".wav",".ogg",".glb",".gltf",".webm",".mp4",".lottie"}
apps=["TAKY-ASSETS","TAKY","Ready & Set","Hide & Seek","Play Camp","Snap & Pop","SAVEY","TAKY-MOBILE","TAKY-WORK-OS"]
records=[]
for app in apps:
    base=root/app
    if not base.is_dir(): continue
    for parent,dirs,files in __import__("os").walk(base):
        dirs[:]=[d for d in dirs if d not in skip]
        for name in files:
            path=Path(parent)/name
            if path.suffix.lower() not in extensions: continue
            relative=path.relative_to(base).as_posix()
            category="unverified"
            low=relative.lower()
            if "/work/" in "/"+low or "candidate" in low or "fail" in low: category="working_or_rejected"
            if "approved/" in low: category="approval_named_requires_evidence"
            records.append({"app":app,"path":str(path),"relative":relative,"bytes":path.stat().st_size,"classification":category,"approval":"NOT_VERIFIED","central_authority":False})
records.sort(key=lambda r:(r["app"],r["relative"]))
manifest={"schema":"TAKY_ASSET_DISCOVERY_V1","generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"Media paths excluding .local and generated/cache directories","rule":"DISCOVERY_ONLY_NOT_APPROVAL; NO_COPIES_NO_MOVES","assets":records}
dest.mkdir(exist_ok=True)
(dest/"asset-discovery.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
summary=Counter(r["app"] for r in records)
lines=["# TAKY Asset Authority Audit","","> Discovery inventory, NOT confirmation of approval or runtime binding.","","## Per repository media"]
lines += [f"- {a}: {summary[a]}" for a in apps]
lines += ["","## Existing gaps","- registry/assets.json and badges.json are scaffold; do not mark files APPROVED based on names.","- .local and worktree media must be audited separately before promotion.","- Do not duplicate assets across webapps; migrate authority only with runtime reference update.","- Existing git modifications remain untouched.","","## Next controlled migration","1. Read exact user approval + SHA provenance for every Visual ID.","2. Reconcile application references with source file hashes.","3. Move one canonical original into TAKY-ASSETS, update consumers in the same change set.","4. Verify runtime, archive obsolete pointers, remove redundant copies only after verified.",""]
(dest/"ASSET_AUTHORITY_AUDIT.md").write_text("\n".join(lines),encoding="utf-8")
print(json.dumps({"total":len(records),"by_app":summary,"files":["registry/asset-discovery.json","registry/ASSET_AUTHORITY_AUDIT.md"]},ensure_ascii=False,default=dict))
