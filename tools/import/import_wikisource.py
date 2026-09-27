"""Import revision-pinned Wikisource 梅花易數 wikitext without modernizing glyphs."""
import argparse
import hashlib
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, read_manifest, write_book


def fetch(source):
    target = ROOT / ".work"
    target.mkdir(exist_ok=True)
    for volume, revision in source["revisions"].items():
        url = "https://zh.wikisource.org/w/index.php?" + urllib.parse.urlencode(
            {"oldid": revision["id"], "action": "raw"})
        req = urllib.request.Request(url, headers={"User-Agent": "YinYangCorpus/1.0 (F25731/yin-yang)"})
        data = urllib.request.urlopen(req, timeout=60).read()
        digest = hashlib.sha1(data).hexdigest()
        if digest != revision["sha1"]:
            raise ValueError(f"revision mismatch for {volume}: {digest}")
        (target / f"meihua-{volume}.wiki").write_bytes(data)


def convert(text):
    if "{{" in text:
        raise ValueError("unhandled template")
    text = re.sub(r"\[\[([^]|]+)\|([^]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^]]+)\]\]", r"\1", text)
    text = text.replace("<poem>", "").replace("</poem>", "")
    def heading(match):
        level = min(len(match.group(1)) + 1, 5)
        return "#" * level + " " + match.group(2).strip()
    text = re.sub(r"(?m)^(={1,4})\s*(.*?)\s*\1\s*$", heading, text)
    if "[[" in text or "{{" in text or "<poem" in text:
        raise ValueError("unhandled wiki markup")
    return text.strip() + "\n"


def run(do_fetch=False):
    source = read_manifest()["wikisource-meihua"]
    if do_fetch:
        fetch(source)
    units = []
    for volume in ("main", "1", "2", "3"):
        file = ROOT / ".work" / f"meihua-{volume}.wiki"
        data = file.read_bytes()
        digest = hashlib.sha1(data).hexdigest()
        revision = source["revisions"][volume]
        if digest != revision["sha1"]:
            raise ValueError(f"{file}: expected {revision['sha1']}, got {digest}")
        text = data.decode("utf-8-sig")
        if volume == "main":
            text = text.split("==序==", 1)[1].split("==目錄==", 1)[0]
            label = "序"
            page = "梅花易數"
        else:
            label = f"卷{volume}"
            page = f"梅花易數/卷{'一二三'[int(volume) - 1]}"
        units.append((page, label, convert(text),
                      {"volume": int(volume) if volume != "main" else 0,
                       "revision_id": revision["id"], "revision_sha1": revision["sha1"]}))
    meta = write_book("wikisource-meihua", "梅花易數", "04-阴阳术数/05-梅花易数",
                      source, units, categories=["阴阳术数", "梅花易数"],
                      author="傳邵雍", aliases=["觀梅數", "梅花數"],
                      edition={"name": "維基文庫校錄版", "base_text": None,
                               "volume_count": 3, "revisions": source["revisions"]},
                      quality={"grade": "C", "ocr": False,
                               "known_issues": ["Traditional attribution to Shao Yong is not independently verified",
                                                "Wikisource transcription has not been collated by this project"]},
                      original_format="MediaWiki wikitext",
                      processing_changes="Converted wiki headings and links to Markdown; preserved source glyphs")
    print(f"IMPORTED 梅花易數 {meta['statistics']['chapters']} units")


def run_gold(do_fetch=False):
    source = read_manifest()["wikisource-huangjince"]
    path = ROOT / ".work/huangjin.wiki"
    if do_fetch:
        revision = source["revisions"]["main"]
        url = "https://zh.wikisource.org/w/index.php?" + urllib.parse.urlencode(
            {"oldid": revision["id"], "action": "raw"})
        req = urllib.request.Request(url, headers={"User-Agent": "YinYangCorpus/1.0 (F25731/yin-yang)"})
        path.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    raw = path.read_bytes()
    digest = hashlib.sha1(raw).hexdigest()
    revision = source["revisions"]["main"]
    if digest != revision["sha1"]:
        raise ValueError(f"revision mismatch: {digest}")
    text = raw.decode("utf-8-sig").split("<onlyinclude>", 1)[1].split("</onlyinclude>", 1)[0]
    text = re.sub(r"\{\{\*\|[^}]*\}\}", "", text)
    text = convert(text)
    meta = write_book("wikisource-huangjince", "黃金策", "04-阴阳术数/04-六爻", source,
                      [("黄金策", "全文", text, {"revision_id": revision["id"],
                                                 "revision_sha1": revision["sha1"]})],
                      categories=["阴阳术数", "六爻", "卜筮"], author="題劉基",
                      edition={"name": "《卜筮正宗》本文字版", "base_text": "卜筮正宗",
                               "volume_count": 1, "revision": revision},
                      quality={"grade": "C", "ocr": False,
                               "known_issues": ["Author attribution follows Wikisource header",
                                                "Wikisource transcription has not been collated by this project"]},
                      original_format="MediaWiki wikitext",
                      processing_changes="Removed wiki templates and converted headings; preserved source glyphs")
    print(f"IMPORTED 黃金策 {meta['statistics']['chapters']} units")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true", help="download frozen revision IDs")
    parser.add_argument("--work", choices=["meihua", "huangjince", "all"], default="all")
    args = parser.parse_args()
    if args.work in ("meihua", "all"):
        run(args.fetch)
    if args.work in ("huangjince", "all"):
        run_gold(args.fetch)
