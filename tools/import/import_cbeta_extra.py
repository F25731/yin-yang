"""Import all non-Taisho CBETA XML-P5 collections whose embedded header permits use.

The existing import_cbeta.py handles the Taisho T collection. This second importer
covers the other collections in xml-p5, preserving each exact TEI header and notes.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

THIS = Path(__file__).resolve()
sys.path.insert(0, str(THIS.parents[1]))
sys.path.insert(0, str(THIS.parent))
from common import ROOT, chunks, clean_path_part, read_manifest, write_book, write_json
from import_cbeta import TEI, XML, extract_header, parse_body

SOURCE_ID = "cbeta-xml-p5"


def git(*args, cwd=None):
    subprocess.run(["git", *args], cwd=cwd, check=True)


def ensure_source(source, fetch=False):
    root = ROOT / ".work/xml-p5"
    if fetch:
        if root.exists():
            shutil.rmtree(root)
        root.parent.mkdir(parents=True, exist_ok=True)
        git("clone", "--filter=blob:none", "--no-checkout", source["url"], str(root))
        git("checkout", source["imported_commit"], cwd=root)
    if not root.exists():
        raise FileNotFoundError(f"{root} missing; use --fetch")
    return root


def collection_category(code):
    if code == "ZW":
        return "藏外"
    if code in {"GA", "GB", "ZS", "I", "D"}:
        return "史传"
    if code in {"LC", "TX", "Y", "YP"}:
        return "诸宗"
    return "其他"


def import_one(path, base, source, canons):
    raw = path.read_text(encoding="utf-8-sig")
    root = ET.fromstring(raw)
    header = root.find(TEI + "teiHeader")
    if header is None:
        raise ValueError("no teiHeader")
    file_desc = header.find(TEI + "fileDesc")
    if file_desc is None:
        raise ValueError("no fileDesc")
    pub = file_desc.find(TEI + "publicationStmt")
    availability = " ".join(pub.itertext()) if pub is not None else ""
    low = availability.lower()
    if "non-commercial" not in low or "header intact" not in low:
        raise PermissionError("availability differs from CBETA reusable header pattern")

    title = next(("".join(node.itertext()).strip() for node in header.iter(TEI + "title")
                  if node.get("level") == "m"), None)
    if not title:
        title = next(("".join(node.itertext()).strip() for node in header.iter(TEI + "title")), None)
    if not title:
        raise ValueError("missing title")
    author = next(("".join(node.itertext()).strip() for node in header.iter(TEI + "author")), None)

    body = root.find(TEI + "text/" + TEI + "body")
    if body is None:
        raise ValueError("missing body")
    sections = parse_body(body)
    if not sections:
        raise ValueError("no body text")

    rel = path.relative_to(base).as_posix()
    collection = rel.split("/", 1)[0]
    canon = canons.get(collection, {})
    canon_name = canon.get("short-title-zh") or canon.get("title-zh") or collection
    subcategory = collection_category(collection)
    stem = path.stem
    book_id = "cbeta-" + stem

    units = []
    for volume, text, loc in sections:
        parts = list(chunks(text))
        for segment, chunk in enumerate(parts, 1):
            label = f"卷{volume}" + (f"・整理分段{segment}" if len(parts) > 1 else "")
            units.append((rel, label, chunk,
                          dict(loc, volume=volume, editorial_segment=len(parts) > 1,
                               cbeta_collection=collection, cbeta_canon=canon_name)))

    meta = write_book(
        book_id, title, "03-佛藏/" + subcategory, source, units,
        categories=["佛藏", subcategory],
        author=author,
        topics=[canon_name, "CBETA", collection],
        original_format="TEI P5 XML",
        edition={"name": canon.get("title-zh") or canon_name,
                 "base_text": canon.get("title-zh") or canon_name,
                 "canonical_id": stem,
                 "collection": collection,
                 "volume_count": len(set(v for v, _, _ in sections))},
        quality={"grade": "B", "ocr": False,
                 "known_issues": ["Apparatus notes retained in provenance; text not independently collated by this project"]},
        directory_name=title + "（" + stem + "）",
        processing_changes="Parsed TEI structure; preserved source glyphs; notes/header retained in provenance",
    )

    provenance = ROOT / "sources/provenance/cbeta"
    provenance.mkdir(parents=True, exist_ok=True)
    (provenance / (stem + "-teiHeader.xml")).write_text(extract_header(raw), encoding="utf-8")
    notes = []
    text_node = root.find(TEI + "text")
    if text_node is not None:
        for note in text_node.iter(TEI + "note"):
            notes.append({
                "id": note.get(XML + "id"), "n": note.get("n"),
                "target": note.get("target"), "type": note.get("type"),
                "text": "".join(note.itertext()).strip(),
            })
    if notes:
        with (provenance / (stem + "-notes.jsonl")).open("w", encoding="utf-8") as stream:
            for note in notes:
                stream.write(json.dumps(note, ensure_ascii=False) + "\n")

    meta["source"]["tei_header"] = f"sources/provenance/cbeta/{stem}-teiHeader.xml"
    meta["source"]["notes"] = f"sources/provenance/cbeta/{stem}-notes.jsonl" if notes else None
    meta["source"]["note_count"] = len(notes)
    meta["source"]["cbeta_collection"] = collection
    meta["source"]["cbeta_canon"] = canon_name
    out = ROOT / "corpus/03-佛藏" / subcategory / clean_path_part(title + "（" + stem + "）") / "metadata.json"
    write_json(out, meta)
    return collection, meta


def run(fetch=False, limit=None):
    source = read_manifest()[SOURCE_ID]
    base = ensure_source(source, fetch)
    canons_path = base / "canons.json"
    canons = json.loads(canons_path.read_text(encoding="utf-8")) if canons_path.exists() else {}

    paths = sorted(
        p for p in base.glob("*/*/*.xml")
        if p.parts[-3] != "T"
    )
    if limit:
        paths = paths[:limit]

    existing = set()
    for p in (ROOT / "corpus/03-佛藏").rglob("metadata.json"):
        try:
            existing.add(json.loads(p.read_text(encoding="utf-8")).get("id"))
        except Exception:
            pass

    counts = Counter()
    skipped_existing = 0
    withheld = []
    failures = []
    imported = 0
    for idx, path in enumerate(paths, 1):
        bid = "cbeta-" + path.stem
        if bid in existing:
            skipped_existing += 1
            continue
        try:
            collection, _ = import_one(path, base, source, canons)
            counts[collection] += 1
            imported += 1
            existing.add(bid)
            if imported % 50 == 0:
                print(f"CBETA EXTRA imported={imported} current={path.relative_to(base)}", flush=True)
        except PermissionError as exc:
            withheld.append(f"{path.relative_to(base)}: {exc}")
        except Exception as exc:
            failures.append(f"{path.relative_to(base)}: {exc}")

    (ROOT / "reports/CBETA_EXTRA_WITHHELD.txt").write_text(
        "\n".join(withheld) + ("\n" if withheld else ""), encoding="utf-8")
    (ROOT / "reports/CBETA_EXTRA_FAILED_ITEMS.txt").write_text(
        "\n".join(failures) + ("\n" if failures else ""), encoding="utf-8")
    lines = [
        "# CBETA 其他藏经系列导入报告", "",
        f"- 新增：**{imported}** 部",
        f"- 已存在跳过：**{skipped_existing}** 部",
        f"- 因 header 条件不同暂缓：**{len(withheld)}** 部",
        f"- 转换失败：**{len(failures)}** 部", "",
        "## 按系列", "",
    ]
    for code, count in sorted(counts.items()):
        canon = canons.get(code, {})
        name = canon.get("title-zh") or code
        lines.append(f"- {code} / {name}：{count}")
    (ROOT / "reports/CBETA_EXTRA_IMPORT_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"CBETA EXTRA imported={imported} withheld={len(withheld)} failed={len(failures)}")
    # Conversion failures are reported but do not discard thousands of successful imports.
    if imported == 0 and not skipped_existing:
        raise SystemExit("no CBETA extra collection imported")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    run(args.fetch, args.limit)
