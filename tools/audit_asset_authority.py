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
        dirs[:]=[d for d in dirs if d not in skip and not (Path(parent)/d).is_symlink() and not (Path(parent)/d).is_junction()]
        for name in files:
            path=Path(parent)/name
            if path.suffix.lower() not in extensions: continue
            relative=path.relative_to(base).as_posix()
            category="unverified"
            low=relative.lower()
            if "/work/" in "/"+low or "candidate" in low or "fail" in low: category="working_or_rejected"
            if "approved/" in low: category="approval_named_requires_evidence"
            records.append({"app":app,"path":str(path),"relative":relative,"bytes":path.stat().st_size,"classification":category,"approval":"NOT_VERIFIED","central_authority":False})
# Preserve byte-evidence in the existing discovery authority on later rescans.
# Re-attest against CURRENT files before publishing; never carry SHA proof
# or duplicate status forward from a changed/missing image or audio clip.
previous_path=dest/"asset-discovery.json"
previous=json.loads(previous_path.read_text(encoding="utf-8-sig")) if previous_path.is_file() else {}
previous_sha={(r["app"],r["relative"]):r for r in previous.get("assets",[]) if r.get("sha256")}
current_rows={(r["app"],r["relative"]):r for r in records}
if len(previous_sha) not in (0,756):
    raise RuntimeError("DISCOVERY_PREVIOUS_SHA_SCOPE_DRIFT:"+str(len(previous_sha)))
for key,prior in previous_sha.items():
    now=current_rows.get(key)
    if not now or now["path"]!=prior["path"] or now["bytes"]!=prior["bytes"]:
        raise RuntimeError("DISCOVERY_PREVIOUS_ASSET_MISSING_OR_SIZE_DRIFT:"+str(key))
    import hashlib
    with open(now["path"],"rb") as verified_source:
        h=hashlib.file_digest(verified_source,"sha256").hexdigest()
    if h!=prior["sha256"]:
        raise RuntimeError("DISCOVERY_SOURCE_SHA_CHANGED_REVIEW_REQUIRED:"+str(key))
    now["sha256"]=h
    now["original_byte_integrity"]=prior["original_byte_integrity"]
    now["observed_duplicate"]=prior["observed_duplicate"]
if previous_sha:
    assert previous.get("cross_app_verified_identity_20261017",{}).get("physical_verified_app_files")==756
records.sort(key=lambda r:(r["app"],r["relative"]))
manifest={"schema":"TAKY_ASSET_DISCOVERY_V1","generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"Media paths excluding .local and generated/cache directories","rule":"DISCOVERY_ONLY_NOT_APPROVAL; NO_COPIES_NO_MOVES","assets":records}
if previous_sha:
    manifest["cross_app_verified_identity_20261017"]=previous["cross_app_verified_identity_20261017"]
dest.mkdir(exist_ok=True)
published=(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
import os
temporary=dest/"asset-discovery.json.tmp"
temporary.write_bytes(published)
assert len(json.loads(temporary.read_text(encoding="utf-8"))["assets"])==len(records)
try:
    os.replace(temporary,previous_path)
except PermissionError:
    with previous_path.open("r+b") as f:
        f.write(published);f.truncate();f.flush();os.fsync(f.fileno())
    temporary.unlink(missing_ok=True)
summary=Counter(r["app"] for r in records)
lines=["# TAKY Asset Authority Audit","","> Discovery inventory, NOT confirmation of approval or runtime binding.","","## Per repository media"]
lines += [f"- {a}: {summary[a]}" for a in apps]
lines += ["","## Existing gaps","- registry/assets.json and badges.json are scaffold; do not mark files APPROVED based on names.","- .local and worktree media must be audited separately before promotion.","- Do not duplicate assets across webapps; migrate authority only with runtime reference update.","- Existing git modifications remain untouched.","","## Next controlled migration","1. Read exact user approval + SHA provenance for every Visual ID.","2. Reconcile application references with source file hashes.","3. Move one canonical original into TAKY-ASSETS, update consumers in the same change set.","4. Verify runtime, archive obsolete pointers, remove redundant copies only after verified.",""]
(dest/"ASSET_AUTHORITY_AUDIT.md").write_text("\n".join(lines),encoding="utf-8")
print(json.dumps({"total":len(records),"by_app":summary,"files":["registry/asset-discovery.json","registry/ASSET_AUTHORITY_AUDIT.md"]},ensure_ascii=False,default=dict))
