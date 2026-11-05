#!/usr/bin/env python3
"""Sync canonical Explorer Crew mock voices from TAKY-ASSETS into app copies.

Canonical source: TAKY-ASSETS/audio/explorer-crew/mock/
App copies (runtime-required, gitignored in each app):
  Hide & Seek / Ready & Set / Snap & Pop : audio/explorer-crew/mock/

Default is --check (read-only). --apply copies missing/different files only.
Never deletes files in apps; extra app files are reported, not removed.
"""
import argparse
import hashlib
import shutil
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1]
SRC = ASSETS / "audio" / "explorer-crew" / "mock"
WORKSPACE = ASSETS.parent
APPS = ["Hide & Seek", "Ready & Set", "Snap & Pop"]
REL = Path("audio") / "explorer-crew" / "mock"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def files(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): p for p in root.rglob("*") if p.is_file()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="copy missing/different files")
    args = ap.parse_args()
    if not SRC.is_dir():
        print(f"FAIL canonical source missing: {SRC}")
        return 2
    src = files(SRC)
    src_sha = {k: sha(v) for k, v in src.items()}
    bad = 0
    for app in APPS:
        dst_root = WORKSPACE / app / REL
        dst = files(dst_root) if dst_root.is_dir() else {}
        missing = [k for k in src if k not in dst]
        differ = [k for k in src if k in dst and sha(dst[k]) != src_sha[k]]
        extra = [k for k in dst if k not in src]
        if args.apply:
            for k in missing + differ:
                out = dst_root / k
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src[k], out)
            missing_after = [k for k in src if not (dst_root / k).is_file() or sha(dst_root / k) != src_sha[k]]
            status = "OK" if not missing_after else "FAIL"
            print(f"{status} {app}: copied={len(missing) + len(differ)} extra_kept={len(extra)}")
            bad += bool(missing_after)
        else:
            status = "OK" if not missing and not differ else "DRIFT"
            print(f"{status} {app}: files={len(dst)} missing={len(missing)} differ={len(differ)} extra={len(extra)}")
            bad += status != "OK"
    print(f"canonical files={len(src)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
