from pathlib import Path
import json, sys, hashlib

TAKY = Path(r"D:\Git PWA\TAKY")
ASSETS = Path(r"D:\Git PWA\TAKY-ASSETS")
SRC = TAKY / "BADGE" / "badge-60-story-20-history-working.json"
COPY = TAKY / "BADGE" / "badge-wow-inspired-copyworking.json"
REG = ASSETS / "registry" / "badges.json"

EXPECTED_COUNT = 60
EXPECTED_ASSET_STATUS = "UNBOUND_NOT_APPROVED"
EXPECTED_CATALOG_STATUS = "PRESET_WORKING_NOT_RUNTIME_ACTIVE"

def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
def fail(msg):
    print("FAIL:", msg)
    return False

def main():
    ok = True
    for path in (SRC, COPY, REG):
        if not path.exists():
            ok = fail(f"missing {path}") and ok
    if not ok:
        return 2

    src, copy, reg = load(SRC), load(COPY), load(REG)
    presets = src.get("presets", [])
    if len(presets) != EXPECTED_COUNT:
        ok = fail(f"preset count={len(presets)} expected={EXPECTED_COUNT}") and ok

    ids = [x.get("source_draft_id") for x in presets]
    if len(set(ids)) != len(ids):
        ok = fail("duplicate source_draft_id") and ok

    required = ("source_draft_id", "stable_name", "motif", "visual_id")
    for item in presets:
        bid = item.get("source_draft_id", "<missing-id>")
        for key in required:
            if not item.get(key):
                ok = fail(f"{bid}: missing {key}") and ok
        if item.get("asset_status") != EXPECTED_ASSET_STATUS:
            ok = fail(f"{bid}: asset_status changed") and ok
        if item.get("catalog_status") != EXPECTED_CATALOG_STATUS:
            ok = fail(f"{bid}: catalog_status changed") and ok
        if item.get("auto_award") is not False:
            ok = fail(f"{bid}: auto_award must remain false") and ok

    if reg.get("status") != "SCAFFOLD" or reg.get("badges") != []:
        ok = fail("shared badge registry is not HOLD/SCAFFOLD-empty") and ok

    print("BADGE PIPELINE PREFLIGHT")
    print("source_sha256:", sha256(SRC))
    print("copy_sha256:", sha256(COPY))
    print("preset_count:", len(presets))
    print("registry_status:", reg.get("status"))
    print("canonical_change: HOLD")
    print("runtime_integration: HOLD")
    print("deployment: HOLD")
    print("result:", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
