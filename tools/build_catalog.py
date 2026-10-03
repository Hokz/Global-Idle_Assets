#!/usr/bin/env python3
"""Build a safe machine-readable inventory from an EXTRACTED private-reference tree.

This script contains no client assets. It hashes and classifies source files and writes
normalized indexes under indexes/generated/. It is intentionally conservative: unknown
source formats stay unknown instead of being guessed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

MINIMAP_PATTERNS = [
    re.compile(r"(?P<x>-?\\d+)[_-](?P<y>-?\\d+)[_-](?P<z>-?\\d+)(?:\\.[^.]+)?$"),
    re.compile(r"(?P<x>-?\\d+)_(?P<y>-?\\d+)_(?P<z>-?\\d+)", re.I),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def minimap_coords(name: str):
    stem = Path(name).name
    for pattern in MINIMAP_PATTERNS:
        m = pattern.search(stem)
        if m:
            return {k: int(v) for k, v in m.groupdict().items()}
    return None


def classify(rel: str) -> str:
    low = rel.lower()
    if low.startswith("minimap/"):
        return "minimap"
    if low.startswith("assets/") and low.endswith(".lzma"):
        return "compressed_asset"
    if "appearance" in low:
        return "appearance_data"
    if "staticmap" in low:
        return "static_map_data"
    if "staticdata" in low:
        return "static_data"
    if low.startswith("storeimages/"):
        return "store_image"
    if low.startswith("conf/"):
        return "configuration"
    if low.startswith("characterdata/"):
        return "character_local_data"
    return "other"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path, help="extracted client/reference root")
    p.add_argument("--out", type=Path, default=Path("indexes/generated"))
    args = p.parse_args()
    root = args.source.resolve()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    records = []
    category_counts = Counter()
    extension_counts = Counter()
    minimaps = []
    total_bytes = 0

    for path in sorted(x for x in root.rglob("*") if x.is_file()):
        rel = path.relative_to(root).as_posix()
        category = classify(rel)
        size = path.stat().st_size
        total_bytes += size
        extension_counts[path.suffix.lower() or "<none>"] += 1
        category_counts[category] += 1
        rec = {
            "path": rel,
            "size": size,
            "sha256": sha256(path),
            "category": category,
        }
        if category == "minimap":
            coords = minimap_coords(rel)
            if coords:
                rec["coords"] = coords
                minimaps.append({"path": rel, **coords})
        records.append(rec)

    manifest = {
        "schemaVersion": 1,
        "sourceRootName": root.name,
        "fileCount": len(records),
        "totalBytes": total_bytes,
        "categoryCounts": dict(sorted(category_counts.items())),
        "extensionCounts": dict(sorted(extension_counts.items())),
        "rules": {
            "characterLocalData": "inventory only; excluded from semantic game catalog",
            "unknownFormats": "preserved as unknown; never inferred into gameplay semantics",
        },
    }

    (out / "source-files.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    (out / "minimap-sectors.json").write_text(json.dumps(minimaps, indent=2), encoding="utf-8")
    (out / "inventory-summary.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
