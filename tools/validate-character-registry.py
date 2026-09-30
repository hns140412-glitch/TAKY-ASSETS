#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "characters.json"
SCHEMA = ROOT / "schemas" / "character.schema.json"

data = json.loads(REGISTRY.read_text(encoding="utf-8-sig"))
schema = json.loads(SCHEMA.read_text(encoding="utf-8-sig"))
chars = data.get("characters", [])
fail = []

try:
    import jsonschema
    for i, item in enumerate(chars):
        try:
            jsonschema.validate(item, schema)
        except Exception as e:
            fail.append(f"SCHEMA:{i}:{e}")
except Exception:
    pass

ids = [c.get("visual_id") for c in chars]
if ids != list(range(7, 25)):
    fail.append(f"VISUAL_ID_SEQUENCE:{ids}")

for c in chars:
    vid = c.get("visual_id")
    if c.get("character_id") != f"GUIDE-{vid:02d}":
        fail.append(f"CHARACTER_ID_MISMATCH:{vid}")
    if c.get("production_owner") != "GUIDE_VISUAL_ID_SPECIALIST_PIPELINE":
        fail.append(f"WRONG_PRODUCTION_OWNER:{vid}")
    src = c.get("source_authority", {})
    if not re.fullmatch(r"[0-9a-f]{64}", src.get("group_sha256") or ""):
        fail.append(f"BAD_GROUP_SHA:{vid}")
    runtime = c.get("runtime_asset", {})
    if runtime.get("status") == "NOT_REGISTERED":
        if any(runtime.get(k) is not None for k in ("asset_ref", "sha256", "asset_version")):
            fail.append(f"PREMATURE_RUNTIME_BINDING:{vid}")
    for forbidden in ("pipeline_state", "independent_cutout", "mask_spec"):
        if forbidden in c:
            fail.append(f"DUPLICATE_SPECIALIST_STATE:{vid}:{forbidden}")

by_id = {c["visual_id"]: c for c in chars}
if by_id.get(24, {}).get("display_name") != "VIVI":
    fail.append("VISUAL_ID_24_NOT_VIVI")

if fail:
    print("FAIL: shared character registry")
    for item in fail:
        print(item)
    raise SystemExit(1)

print(f"PASS: {len(chars)} GUIDE source pointers registered; specialist production state is not duplicated.")
