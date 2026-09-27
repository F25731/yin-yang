"""Import revision-pinned Wikisource 聊齋志異 by story, keeping annotations separate."""
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

WORK = ROOT / ".work/liaozhai"
NOTES = ROOT / "sources/provenance/liaozhai-editorial-notes.jsonl"
HEADING = re.compile(r"(?m)^==(?!=)\s*(.*?)\s*==(?!=)\s*$")


def fetch(source):
    WORK.mkdir(parents=True, exist_ok=True)
    for number in range(1, 13):
        revision = source["revisions"][str(number)]
        url = "https://zh.wikisource.org/w/index.php?" + urllib.parse.urlencode(
            {"oldid": revision["id"], "action": "raw"})
        request = urllib.request.Request(url, headers={"User-Agent": "YinYangCorpus/1.0 (F25731/yin-yang)"})
        data = urllib.request.urlopen(request, timeout=60).read()
        digest = hashlib.sha1(data).hexdigest()
        if digest != revision["sha1"]:
            raise ValueError(f"volume {number}: SHA1 mismatch: {digest}")
        (WORK / f"{number}.wiki").write_bytes(data)


def clean_story(raw, volume, story):
    notes = []

    def record(kind, content):
        notes.append({"volume": volume, "story": story, "kind": kind, "text": content})

    raw = re.sub(r"<noinclude>.*?</noinclude>", "", raw, flags=re.DOTALL)

    def footnote(match):
        record("editorial_ref", match.group(1).strip())
        return ""

    raw = re.sub(r"<ref(?:\s+[^>]*)?>(.*?)</ref>", footnote, raw, flags=re.DOTALL)

    def comment(match):
        record("editorial_comment", match.group(1).strip())
        return ""

    raw = re.sub(r"\{\{\*\|([^{}]*)\}\}", comment, raw)

    def variant(match):
        reading, alternative = match.group(1), match.group(2)
        record("variant", {"reading": reading, "alternative": alternative})
        return reading

    raw = re.sub(r"\{\{另\|([^{}|]*)\|([^{}|]*)\}\}", variant, raw)
    raw = re.sub(r"\{\{(?:ProperNoun|PUA)\|(.*?)\}\}", r"\1", raw, flags=re.DOTALL)

    def rare(match):
        record("rare_glyph_description", match.group(2))
        return match.group(1)

    raw = re.sub(r"\{\{僻字\|([^{}|]*)\|([^{}|]*)\}\}", rare, raw)
    raw = re.sub(r"\{\{reflist(?:\|[^{}]*)?\}\}", "", raw)
    raw = raw.replace("<u>", "").replace("</u>", "")
    raw = re.sub(r"\[\[([^]|]+)\|([^]]+)\]\]", r"\2", raw)
    raw = re.sub(r"\[\[([^]]+)\]\]", r"\1", raw)
    raw = re.sub(r"(?m)^===\s*(.*?)\s*===\s*$", r"### \1", raw)
    remaining = re.search(r"\{\{|\}\}|\[\[|\]\]|<\s*/?\s*[a-zA-Z]", raw)
    if remaining:
        raise ValueError(f"volume {volume} story {story}: unhandled source markup {raw[remaining.start():remaining.start()+90]!r}")
    return "\n".join(line.rstrip() for line in raw.splitlines()).strip() + "\n", notes


def run(do_fetch=False):
    source = read_manifest()["wikisource-liaozhai"]
    if do_fetch:
        fetch(source)
    units, notes = [], []
    for number in range(1, 13):
        revision = source["revisions"][str(number)]
        data = (WORK / f"{number}.wiki").read_bytes()
        digest = hashlib.sha1(data).hexdigest()
        if digest != revision["sha1"]:
            raise ValueError(f"volume {number}: SHA1 mismatch: {digest}")
        raw = data.decode("utf-8-sig")
        raw, removed = re.subn(r"\A\{\{header\b.*?\}\}\s*", "", raw, count=1, flags=re.DOTALL)
        if removed != 1:
            raise ValueError(f"volume {number}: missing header")
        parts = HEADING.split(raw)
        if parts[0].strip():
            raise ValueError(f"volume {number}: text before first story")
        if len(parts) < 3 or len(parts) % 2 != 1:
            raise ValueError(f"volume {number}: invalid story headings")
        for title, body in zip(parts[1::2], parts[2::2]):
            title = re.sub(r"\{\{ProperNoun\|(.*?)\}\}", r"\1", title).strip()
            if not title:
                raise ValueError(f"volume {number}: empty story title")
            if title == "註釋":
                continue
            text, story_notes = clean_story(body, number, title)
            notes.extend(story_notes)
            units.append((revision["title"], f"卷{number}・{title}", text,
                          {"volume": number, "story": title, "revision_id": revision["id"],
                           "revision_sha1": revision["sha1"]}))
    if len(units) != 493:
        raise ValueError(f"incomplete story count: {len(units)}")
    meta = write_book(
        "wikisource-liaozhai", "聊齋志異", "01-志怪神异", source, units,
        categories=["志怪神异"], author="蒲松齡", author_dynasty="清", work_dynasty="清",
        aliases=["聊斋志异"],
        edition={"name": "維基文庫十二卷校錄版", "base_text": None, "volume_count": 12,
                 "revisions": source["revisions"]},
        quality={"grade": "C", "ocr": False,
                 "known_issues": ["Wikisource transcription has not been independently collated",
                                  "493 story entries in the pinned twelve-volume source; differs from some 496-story counts"]},
        original_format="MediaWiki wikitext",
        processing_changes="Removed wiki navigation and editorial glosses; selected first marked reading; preserved source glyphs")
    NOTES.parent.mkdir(parents=True, exist_ok=True)
    NOTES.write_text("".join(json.dumps(n, ensure_ascii=False) + "\n" for n in notes), encoding="utf-8")
    meta["source"]["editorial_notes"] = NOTES.relative_to(ROOT).as_posix()
    meta["source"]["editorial_note_count"] = len(notes)
    chapter_dir = ROOT / "corpus/01-志怪神异/聊齋志異/chapters"
    for stale in chapter_dir.glob("*.md"):
        if int(stale.stem) > len(units):
            stale.unlink()
    write_json(ROOT / "corpus/01-志怪神异/聊齋志異/metadata.json", meta)
    print(f"IMPORTED 聊齋志異: {len(units)} stories, {len(notes)} editorial notes/variants")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    run(parser.parse_args().fetch)
