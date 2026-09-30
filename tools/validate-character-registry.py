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
expected = list(range(7, 25))
if ids != expected:
    fail.append(f"VISUAL_ID_SEQUENCE:{ids}")

codes = [c.get("display_name") for c in chars]
if len(set(codes)) != len(codes):
    fail.append("DUPLICATE_DISPLAY_NAME")

for c in chars:
    vid = c.get("visual_id")
    expected_id = f"GUIDE-{vid:02d}" if isinstance(vid, int) else None
    if c.get("character_id") != expected_id:
        fail.append(f"CHARACTER_ID_MISMATCH:{vid}")
    src = c.get("source_authority", {})
    group_sha = src.get("group_sha256")
    if not re.fullmatch(r"[0-9a-f]{64}", group_sha or ""):
        fail.append(f"BAD_GROUP_SHA:{vid}")
    cut = c.get("independent_cutout", {})
    state = c.get("pipeline_state")
    if state == "AWAITING_INDEPENDENT_CUTOUT_SHA":
        if cut.get("sha256") is not None or cut.get("asset_ref") is not None:
            fail.append(f"PREMATURE_CUTOUT_BINDING:{vid}")
    if cut.get("sha256") == group_sha and cut.get("sha256") is not None:
        fail.append(f"GROUP_SHA_MISUSED_AS_CUTOUT_SHA:{vid}")
    mask = c.get("mask_spec", {})
    if cut.get("sha256") is None and mask.get("status") != "BLOCKED_UNTIL_CUTOUT_SHA_LOCK":
        fail.append(f"MASK_NOT_BLOCKED:{vid}")

by_id = {c["visual_id"]: c for c in chars}
if by_id.get(24, {}).get("display_name") != "VIVI":
    fail.append("VISUAL_ID_24_NOT_VIVI")
if "INVALID_DERIVATIVE_LEFT_HAND_MISSING_DO_NOT_PROMOTE" not in by_id.get(21, {}).get("qa_flags", []):
    fail.append("TESS_QA_FLAG_MISSING")
if "INVALID_DERIVATIVE_LOWER_BODY_LEG_DISTORTION_DO_NOT_PROMOTE" not in by_id.get(23, {}).get("qa_flags", []):
    fail.append("ZEKE_QA_FLAG_MISSING")

if fail:
    print("FAIL: character registry")
    for x in fail:
        print(x)
    raise SystemExit(1)

print(f"PASS: {len(chars)} expansion characters registered; source authority locked; cutout/mask gates remain fail-closed.")
