"""TEI P5 parser for the CBETA Taisho collection (noncommercial license)."""
import argparse
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, chunks, clean_path_part, read_manifest, write_book, write_json

TEI = "{http://www.tei-c.org/ns/1.0}"
XML = "{http://www.w3.org/XML/1998/namespace}"
CB = "{http://www.cbeta.org/ns/1.0}"
VOLUME_CATEGORY = {
    **{n: "阿含" for n in (1, 2)},
    **{n: "本缘" for n in (3, 4)},
    **{n: "般若" for n in range(5, 9)},
    9: "法华", 10: "华严", 11: "宝积", 12: "涅槃",
    **{n: "密教" for n in range(18, 22)},
    **{n: "律部" for n in range(22, 25)},
    **{n: "论部" for n in range(25, 33)},
    **{n: "诸宗" for n in range(33, 47)},
    47: "禅宗", 48: "禅宗",
    **{n: "史传" for n in range(49, 53)},
    85: "藏外",
}


def local(element):
    return element.tag.rsplit("}", 1)[-1]


def extract_header(raw):
    start = raw.index("<teiHeader>")
    end = raw.index("</teiHeader>", start) + len("</teiHeader>")
    return raw[start:end] + "\n"


def best_reading(element):
    wanted = ("lem", "rdg") if local(element) == "app" else ("corr", "reg", "orig", "sic")
    for name in wanted:
        for child in element:
            if local(child) == name:
                return child
    return next(iter(element), None)


def parse_body(body):
    sections, out, loc = [], [], {"page_start": None, "page_end": None,
                                    "line_start": None, "line_end": None}
    volume = "1"

    def flush():
        nonlocal out, loc
        content = "".join(out).strip()
        if content:
            sections.append((volume, content, dict(loc)))
        out = []
        loc = {"page_start": None, "page_end": None, "line_start": None, "line_end": None}

    def walk(element):
        nonlocal volume
        tag = local(element)
        if tag == "milestone" and element.get("unit") == "juan":
            flush()
            volume = element.get("n") or volume
            return
        if tag == "pb":
            value = element.get("n")
            if loc["page_start"] is None:
                loc["page_start"] = value
            loc["page_end"] = value
            return
        if tag == "lb":
            value = element.get("n")
            if loc["line_start"] is None:
                loc["line_start"] = value
            loc["line_end"] = value
            out.append("\n")
            return
        if tag in {"note", "anchor", "figure", "graphic", "mulu", "fw", "docNumber"}:
            return
        if tag in {"app", "choice"}:
            selected = best_reading(element)
            if selected is not None:
                walk(selected)
            return
        if tag in {"head", "juan"}:
            out.append("\n\n")
        if tag in {"p", "lg", "l", "div"}:
            out.append("\n")
        if element.text and element.text.strip():
            out.append(element.text.replace("\n", "").replace("\r", ""))
        for child in element:
            walk(child)
            if child.tail and child.tail.strip():
                out.append(child.tail.replace("\n", "").replace("\r", ""))
        if tag in {"head", "juan", "p", "lg", "l", "div"}:
            out.append("\n")

    if body.text and body.text.strip():
        out.append(body.text.replace("\n", "").replace("\r", ""))
    for child in body:
        walk(child)
        if child.tail and child.tail.strip():
            out.append(child.tail.replace("\n", "").replace("\r", ""))
    flush()
    return sections


def import_file(path, source):
    raw = path.read_text(encoding="utf-8-sig")
    root = ET.fromstring(raw)
    header = root.find(TEI + "teiHeader")
    if header is None:
        raise ValueError(f"{path}: no teiHeader")
    availability = " ".join(header.find(TEI + "fileDesc").find(TEI + "publicationStmt").itertext())
    if "non-commercial" not in availability.lower() or "header intact" not in availability.lower():
        raise ValueError(f"{path}: availability differs; requires manual license review")
    title = next(("".join(node.itertext()).strip() for node in header.iter(TEI + "title")
                  if node.get("level") == "m"), None)
    if not title:
        raise ValueError(f"{path}: missing work title")
    volume_no = int(path.parent.name[1:])
    subcategory = VOLUME_CATEGORY.get(volume_no, "其他")
    canonical_no = int(re.search(r"n(\d+)", path.stem).group(1))
    # T09, T12 and T47 cross divisions within a single printed volume.
    if volume_no == 9 and canonical_no >= 278:
        subcategory = "华严"
    elif volume_no == 12:
        subcategory = "宝积" if canonical_no < 360 else "净土" if canonical_no < 374 else "涅槃"
    elif volume_no == 47 and canonical_no <= 1984:
        subcategory = "净土"
    author = next(("".join(node.itertext()).strip() for node in header.iter(TEI + "author")), None)
    body = root.find(TEI + "text/" + TEI + "body")
    if body is None:
        raise ValueError(f"{path}: missing body")
    sections = parse_body(body)
    book_id = path.stem
    dirname = clean_path_part(title + "（" + book_id + "）")
    prior = list((ROOT / "corpus/03-佛藏").glob(f"*/{dirname}/metadata.json"))
    source_path = f"T/{path.parent.name}/{path.name}"
    units = []
    for volume, text, loc in sections:
        for segment, chunk in enumerate(chunks(text), 1):
            units.append((source_path, f"卷{volume}" + (f"・整理分段{segment}" if len(text) > 120_000 else ""),
                          chunk, dict(loc, volume=volume, editorial_segment=len(text) > 120_000)))
    if not units:
        raise ValueError(f"{path}: no body text")
    metadata = write_book("cbeta-" + book_id, title, "03-佛藏/" + subcategory, source, units,
                          categories=["佛藏", subcategory], author=author, original_format="TEI P5 XML",
                          edition={"name": "大正新脩大藏經數位版", "base_text": "大正新脩大藏經",
                                   "canonical_id": book_id, "volume_count": len(set(s[0] for s in sections))},
                          quality={"grade": "B", "ocr": False,
                                   "known_issues": ["Apparatus notes are in provenance; converted reading selects lemma/correction"]},
                          directory_name=title + "（" + book_id + "）")
    exact_header = extract_header(raw)
    provenance = ROOT / "sources/provenance/cbeta"
    provenance.mkdir(parents=True, exist_ok=True)
    (provenance / (book_id + "-teiHeader.xml")).write_text(exact_header, encoding="utf-8")
    notes = []
    for note in root.find(TEI + "text").iter(TEI + "note"):
        notes.append({"id": note.get(XML + "id"), "n": note.get("n"),
                      "target": note.get("target"), "type": note.get("type"),
                      "text": "".join(note.itertext()).strip()})
    if notes:
        with (provenance / (book_id + "-notes.jsonl")).open("w", encoding="utf-8") as stream:
            for note in notes:
                stream.write(json.dumps(note, ensure_ascii=False) + "\n")
    metadata["source"]["tei_header"] = f"sources/provenance/cbeta/{book_id}-teiHeader.xml"
    metadata["source"]["notes"] = f"sources/provenance/cbeta/{book_id}-notes.jsonl" if notes else None
    metadata["source"]["note_count"] = len(notes)
    out = ROOT / "corpus/03-佛藏" / subcategory / dirname / "metadata.json"
    write_json(out, metadata)
    for old in prior:
        if old != out:
            shutil.rmtree(old.parent)
    return metadata


def run(source_root=None, limit=None, volumes=None):
    source = read_manifest()["cbeta-xml-p5"]
    base = Path(source_root) if source_root else ROOT / ".work/xml-p5/T"
    paths = sorted(base.rglob("T*n*.xml"))
    if volumes:
        paths = [p for p in paths if p.parent.name in volumes]
    if not paths:
        raise FileNotFoundError(f"no T XML in {base}")
    failures, withheld, count = [], [], 0
    for path in paths[:limit]:
        try:
            meta = import_file(path, source)
            count += 1
            if count % 50 == 0:
                print(f"IMPORTED CBETA {count}", flush=True)
        except Exception as exc:
            if "availability differs" in str(exc):
                withheld.append(f"{path.name}: {exc}")
            else:
                failures.append(f"{path.name}: {exc}")
    (ROOT / "reports/CBETA_FAILED_ITEMS.txt").write_text("\n".join(failures) + ("\n" if failures else ""), encoding="utf-8")
    (ROOT / "reports/CBETA_WITHHELD_LICENSE.txt").write_text("\n".join(withheld) + ("\n" if withheld else ""), encoding="utf-8")
    print(f"CBETA T imported={count} withheld={len(withheld)} failed={len(failures)}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--volumes", nargs="+", help="T volume directories, e.g. T09 T12")
    args = parser.parse_args()
    run(args.source_root, args.limit, args.volumes)
