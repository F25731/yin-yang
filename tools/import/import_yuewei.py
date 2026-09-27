"""Import all 24 revision-pinned Wikisource volumes of 閱微草堂筆記."""
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

WORK = ROOT / ".work/yuewei"
NOTES = ROOT / "sources/provenance/yuewei-notes.jsonl"


def fetch(source):
    WORK.mkdir(parents=True, exist_ok=True)
    for number in range(1, 25):
        revision = source["revisions"][str(number)]
        url = "https://zh.wikisource.org/w/index.php?" + urllib.parse.urlencode(
            {"oldid": revision["id"], "action": "raw"})
        request = urllib.request.Request(url, headers={"User-Agent": "YinYangCorpus/1.0 (F25731/yin-yang)"})
        data = urllib.request.urlopen(request, timeout=60).read()
        digest = hashlib.sha1(data).hexdigest()
        if digest != revision["sha1"]:
            raise ValueError(f"volume {number}: SHA1 mismatch: {digest}")
        (WORK / f"{number}.wiki").write_bytes(data)


def convert(raw, number):
    raw, removed = re.subn(r"\A\{\{header2?\b.*?\}\}\s*", "", raw, count=1, flags=re.DOTALL)
    if removed != 1:
        raise ValueError(f"volume {number}: missing header template")
    notes = []

    def note(match):
        notes.append({"volume": number, "index": len(notes) + 1, "text": match.group(1)})
        return ""

    raw = re.sub(r"\{\{\*\|([^{}]*)\}\}", note, raw)
    raw = re.sub(r"\{\{YL\|([^{}]*)\}\}", r"\1", raw)
    raw = raw.replace("{{PD-old}}", "")
    raw = re.sub(r"\[\[([^]|]+)\|([^]]+)\]\]", r"\2", raw)
    raw = re.sub(r"\[\[([^]]+)\]\]", r"\1", raw)
    if "{{" in raw or "[[" in raw or "}}" in raw or "]]" in raw:
        raise ValueError(f"volume {number}: unhandled wiki markup")
    return raw.strip() + "\n", notes


def run(do_fetch=False):
    source = read_manifest()["wikisource-yuewei"]
    if do_fetch:
        fetch(source)
    units, all_notes = [], []
    for number in range(1, 25):
        revision = source["revisions"][str(number)]
        data = (WORK / f"{number}.wiki").read_bytes()
        digest = hashlib.sha1(data).hexdigest()
        if digest != revision["sha1"]:
            raise ValueError(f"volume {number}: SHA1 mismatch: {digest}")
        text, notes = convert(data.decode("utf-8-sig"), number)
        all_notes.extend(notes)
        units.append((revision["title"], f"卷{number}", text,
                      {"volume": number, "revision_id": revision["id"],
                       "revision_sha1": revision["sha1"]}))
    meta = write_book(
        "wikisource-yuewei", "閱微草堂筆記", "01-志怪神异", source, units,
        categories=["志怪神异"], author="紀昀", author_dynasty="清", work_dynasty="清",
        aliases=["阅微草堂笔记", "閱微艸堂筆記"],
        edition={"name": "維基文庫校錄版", "base_text": None, "volume_count": 24,
                 "revisions": source["revisions"]},
        quality={"grade": "C", "ocr": False,
                 "known_issues": ["Wikisource transcription has not been independently collated"]},
        original_format="MediaWiki wikitext",
        processing_changes="Removed wiki navigation and links; preserved source glyphs; wiki annotations saved separately")
    NOTES.parent.mkdir(parents=True, exist_ok=True)
    NOTES.write_text("".join(json.dumps(n, ensure_ascii=False) + "\n" for n in all_notes), encoding="utf-8")
    meta["source"]["editorial_notes"] = NOTES.relative_to(ROOT).as_posix()
    meta["source"]["editorial_note_count"] = len(all_notes)
    write_json(ROOT / "corpus/01-志怪神异/閱微草堂筆記/metadata.json", meta)
    print(f"IMPORTED 閱微草堂筆記: 24 volumes, {len(all_notes)} editorial notes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    run(parser.parse_args().fetch)
