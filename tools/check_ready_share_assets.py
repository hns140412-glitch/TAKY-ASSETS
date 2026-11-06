#!/usr/bin/env python3
"""Bounded inventory check for one canonical Ready share-card asset revision."""
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PREFIX = pathlib.Path("assets/Ready-Set/share-card/interim-2026-09-29")
source = ROOT / PREFIX / "manifest.json"
manifest = json.loads(source.read_text(encoding="utf-8"))
assert manifest["asset_id"] == "READY_SHARE_FOUR_STATE_INTERIM_20260929"
assert manifest["content_prefix"] == PREFIX.as_posix() + "/"
if manifest["status"] != "BINARY_IMPORTED_HASH_VERIFIED":
    sys.exit("HOLD: Central asset registry exists; 16 actual binary files have not been imported.")
files = manifest.get("files", [])
if len(files) != 16:
    sys.exit("FAIL: manifest must contain exactly 4 full scenes + 12 alpha layers")
listed = set()
for entry in files:
    path = pathlib.Path(entry["path"])
    if not path.is_relative_to(PREFIX) or path in listed or path.suffix not in {".png", ".webp"}:
        sys.exit(f"FAIL: unsafe/duplicate asset entry: {path}")
    listed.add(path)
    abs_path = ROOT / path
    if not abs_path.is_file():
        sys.exit(f"HOLD: source file not yet in GitHub tree: {path}")
    data = abs_path.read_bytes()
    if len(data) != entry["size_bytes"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
        sys.exit(f"FAIL: SHA-256/size mismatch: {path}")
all_images = set(p.relative_to(ROOT) for p in (ROOT / PREFIX).rglob("*") if p.suffix in {".webp", ".png"})
if listed != all_images:
    sys.exit(f"FAIL: unregistered image files or missing manifest entries: {sorted(str(p) for p in (all_images ^ listed))}")
receipt_path = ROOT / PREFIX / "import-receipt.json"
if not receipt_path.is_file():
    sys.exit("HOLD: import receipt is missing")
receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
if receipt.get("file_count") != 16 or receipt.get("asset_id") != manifest["asset_id"]:
    sys.exit("FAIL: import receipt differs from manifest")
print("PASS: TAKY-ASSETS Ready share scenes: 16 actual files, complete manifest, matching SHA-256/size, review branch only")
