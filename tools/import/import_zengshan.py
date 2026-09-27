"""Import the pinned Wikisource four-volume 增刪卜易 transcription."""
import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, read_manifest, write_book, write_json

WORK = ROOT / ".work/zengshan"
NOTES = ROOT / "sources/provenance/zengshan-editorial-notes.jsonl"
ORDER = ([str(n) for n in range(1, 16)] + ["15又"]
         + [str(n) for n in range(16, 27)] + [f"26又{n}" for n in range(1, 5)])


def get_raw(revision):
    url = "https://zh.wikisource.org/w/index.php?" + urllib.parse.urlencode(
        {"oldid": revision["id"], "action": "raw"})
    request = urllib.request.Request(url, headers={"User-Agent": "YinYangCorpus/1.0 (F25731/yin-yang)"})
    data = urllib.request.urlopen(request, timeout=60).read()
    if hashlib.sha1(data).hexdigest() != revision["sha1"]:
        raise ValueError(f"revision SHA1 mismatch: {revision['id']}")
    return data


def fetch(source):
    WORK.mkdir(parents=True, exist_ok=True)
    for key in ["main", *ORDER, "3-chart"]:
        (WORK / f"{key}.wiki").write_bytes(get_raw(source["revisions"][key]))


def convert(raw, volume, section):
    notes = []

    def note(match):
        notes.append({"volume": volume, "section": section, "text": match.group(1).strip()})
        return ""

    raw = re.sub(r"\{\{\*\|([^{}]*)\}\}", note, raw)
    raw = re.sub(r"\{\{(?:Header2?|Textquality)\b.*?\}\}", "", raw,
                 flags=re.IGNORECASE | re.DOTALL)
    raw = raw.replace("{{PD-old}}", "").replace("{{未排版}}", "")
    raw = re.sub(r"\[\[分[類类]:[^]]+\]\]", "", raw)
    raw = re.sub(r"\[\[([^]|]+)\|([^]]+)\]\]", r"\2", raw)
    raw = re.sub(r"\[\[([^]]+)\]\]", r"\1", raw)
    raw = re.sub(r"-\{([^{}]*)\}-", r"\1", raw)
    raw = re.sub(r"<br\s*/?>", "\n", raw, flags=re.IGNORECASE)
    for tag in ("onlyinclude", "poem"):
        raw = re.sub(rf"</?{tag}>", "\n", raw, flags=re.IGNORECASE)
    raw = re.sub(r"<pre>", "\n\n```text\n", raw, flags=re.IGNORECASE)
    raw = re.sub(r"</pre>", "\n```\n\n", raw, flags=re.IGNORECASE)
    if re.search(r"\{\{|\}\}|\[\[|\]\]|<\s*/?\s*[a-zA-Z]|-\{", raw):
        raise ValueError(f"volume {volume} {section}: unhandled source markup")
    return raw.strip() + "\n", notes


def run(do_fetch=False):
    source = read_manifest()["wikisource-zengshan"]
    if do_fetch:
        fetch(source)
    units, notes = [], []

    def read(key):
        revision = source["revisions"][key]
        data = (WORK / f"{key}.wiki").read_bytes()
        if hashlib.sha1(data).hexdigest() != revision["sha1"]:
            raise ValueError(f"{key}: revision SHA1 mismatch")
        return data.decode("utf-8-sig"), revision

    for key in ORDER:
        raw, revision = read(key)
        section = re.search(r"(?m)^\s*\|\s*section\s*=\s*(.*?)\s*$", raw, flags=re.IGNORECASE)
        if section is None:
            raise ValueError(f"{key}: no section label")
        content, new_notes = convert(raw, 1, section.group(1))
        notes.extend(new_notes)
        units.append((revision["title"], f"卷1・{section.group(1)}", content,
                      {"volume": 1, "revision_id": revision["id"], "revision_sha1": revision["sha1"]}))
        if key == "3":
            chart, chart_revision = read("3-chart")
            chart, chart_notes = convert(chart, 1, "八卦各宮全圖")
            notes.extend(chart_notes)
            units.append((chart_revision["title"], "卷1・八卦各宮全圖", chart,
                          {"volume": 1, "revision_id": chart_revision["id"],
                           "revision_sha1": chart_revision["sha1"]}))

    raw, main_revision = read("main")
    headings = [f"== 增刪卜易卷之{x} ==" for x in ("二", "三", "四")]
    positions = [raw.index(heading) for heading in headings]
    if positions != sorted(positions):
        raise ValueError("main page volume order differs")
    for volume, (start, end) in enumerate(zip(positions, positions[1:] + [len(raw)]), 2):
        content, new_notes = convert(raw[start + len(headings[volume - 2]):end], volume, f"卷{volume}")
        notes.extend(new_notes)
        units.append((main_revision["title"], f"卷{volume}", content,
                      {"volume": volume, "revision_id": main_revision["id"],
                       "revision_sha1": main_revision["sha1"]}))
    if len(units) != 35:
        raise ValueError(f"incomplete source: {len(units)} units")
    meta = write_book(
        "wikisource-zengshan", "增刪卜易", "04-阴阳术数/04-六爻", source, units,
        categories=["阴阳术数", "六爻", "卜筮"], author="野鶴老人",
        aliases=["增删卜易"],
        edition={"name": "維基文庫四卷錄入版", "base_text": None, "volume_count": 4,
                 "revisions": source["revisions"]},
        quality={"grade": "D", "ocr": False,
                 "known_issues": ["Wikisource labels main transcription 25% text quality and chapter pages 50%",
                                  "Source transcription is not independently collated; some modern editorial insertions may remain"]},
        original_format="MediaWiki wikitext",
        processing_changes="Excluded modern recorder preface; converted wiki markup; kept diagrams as preformatted text")
    NOTES.parent.mkdir(parents=True, exist_ok=True)
    NOTES.write_text("".join(json.dumps(n, ensure_ascii=False) + "\n" for n in notes), encoding="utf-8")
    meta["source"]["editorial_notes"] = NOTES.relative_to(ROOT).as_posix()
    meta["source"]["editorial_note_count"] = len(notes)
    write_json(ROOT / "corpus/04-阴阳术数/04-六爻/增刪卜易/metadata.json", meta)
    print(f"IMPORTED 增刪卜易: 4 volumes, {len(units)} units, {len(notes)} editorial notes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    run(parser.parse_args().fetch)
