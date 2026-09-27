"""Import the pinned Wikisource transcription of 奇门宝鉴御定."""
import argparse
import hashlib
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, read_manifest, write_book

WORK = ROOT / ".work/qimenbaojian.wiki"


def fetch(revision):
    url = "https://zh.wikisource.org/w/index.php?" + urllib.parse.urlencode(
        {"oldid": revision["id"], "action": "raw"})
    request = urllib.request.Request(url, headers={"User-Agent": "YinYangCorpus/1.0 (F25731/yin-yang)"})
    data = urllib.request.urlopen(request, timeout=60).read()
    if hashlib.sha1(data).hexdigest() != revision["sha1"]:
        raise ValueError("revision SHA1 mismatch")
    WORK.parent.mkdir(parents=True, exist_ok=True)
    WORK.write_bytes(data)


def run(do_fetch=False):
    source = read_manifest()["wikisource-qimenbaojian"]
    revision = source["revision"]
    if do_fetch:
        fetch(revision)
    data = WORK.read_bytes()
    if hashlib.sha1(data).hexdigest() != revision["sha1"]:
        raise ValueError("cached revision SHA1 mismatch")
    raw = data.decode("utf-8-sig")
    match = re.fullmatch(r"\s*\{\{header\s*.*?\}\}\s*==《奇门宝鉴御定》==\s*(.*)", raw,
                         flags=re.DOTALL)
    if not match:
        raise ValueError("unexpected Wikisource page wrapper")
    body = match.group(1).strip() + "\n"
    if re.search(r"\{\{|\}\}|\[\[|\]\]|<\s*/?\s*[a-zA-Z]", body):
        raise ValueError("unhandled source markup")
    if len(body) < 30_000 or not body.endswith("天机深惜智在克宽。\n"):
        raise ValueError("source text appears truncated")
    write_book(
        "wikisource-qimenbaojian", "奇门宝鉴御定", "04-阴阳术数/06-奇门遁甲", source,
        [(revision["title"], "维基文库单页转录", body,
          {"revision_id": revision["id"], "revision_sha1": revision["sha1"]})],
        categories=["阴阳术数", "奇门遁甲"], aliases=["奇門寶鑑御定"],
        edition={"name": "维基文库单页转录版", "base_text": None, "volume_count": None,
                 "revision": revision,
                 "upstream_attribution": "唐 徐道符（与正文提及明代人物矛盾，未经证实）"},
        quality={"grade": "D", "ocr": False,
                 "known_issues": ["Upstream attributes this work to Tang Xu Daofu, but the text discusses Ming figures; attribution is inconsistent",
                                  "No identified print base or independent collation; edition completeness outside this page is unverified"]},
        original_format="MediaWiki wikitext",
        processing_changes="Removed page header and title markup; preserved source text and glyphs without modernization")
    print(f"IMPORTED 奇门宝鉴御定: {len(body)} source characters")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    run(parser.parse_args().fetch)
