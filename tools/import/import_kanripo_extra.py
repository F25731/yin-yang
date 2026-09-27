"""Register and import additional Kanripo KR3g titles from its official catalog."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, chunks, read_manifest, write_book
from import_kanripo import convert

FENGSHUI = list(range(19, 28))
DIVINATION = list(range(28, 33))
BAZI = list(range(33, 40))
PHYSIOGNOMY = list(range(43, 47))
CODES = [f"KR3g{x:04d}" for x in FENGSHUI + DIVINATION + BAZI + PHYSIOGNOMY]


def category(number):
    if number in FENGSHUI:
        return "04-阴阳术数/09-风水堪舆", ["阴阳术数", "风水堪舆"]
    if number == 31:
        return "04-阴阳术数/07-大六壬", ["阴阳术数", "大六壬"]
    if number in DIVINATION:
        cats = ["阴阳术数", "卜筮"]
        if number in (30, 32):
            cats.append("六爻")
        return "04-阴阳术数/12-卜筮", cats
    if number in BAZI:
        return "04-阴阳术数/02-八字四柱", ["阴阳术数", "八字四柱"]
    return "04-阴阳术数/11-相术", ["阴阳术数", "相术"]


def catalog_entries():
    file = ROOT / ".work/KR-Catalog/KR/KR3g.txt"
    if not file.exists():
        raise FileNotFoundError(f"missing {file}; clone https://github.com/kanripo/KR-Catalog")
    entries = {}
    for line in file.read_text(encoding="utf-8").splitlines():
        found = re.match(r"^\*\*\* (KR3g\d{4}) (.*?)-([^-]*)-([^-]*)$", line)
        if found:
            code, title, era, author = found.groups()
            entries[code] = (title.strip(), era.strip() or None, author.strip() or None)
    return entries


def register():
    entries = catalog_entries()
    manifest_path = ROOT / "sources/manifest.yaml"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    known = {entry["id"] for entry in manifest}
    for code in CODES:
        if code not in entries:
            raise ValueError(f"{code} not found in official catalog")
        if f"kanripo-{code}" in known:
            continue
        base = ROOT / ".work" / code
        sha = subprocess.check_output(["git", "-C", str(base), "rev-parse", "HEAD"], text=True).strip()
        title, era, author = entries[code]
        _, cats = category(int(code[-4:]))
        manifest.append({"id": f"kanripo-{code}", "name": f"Kanripo {title}",
                         "url": f"https://github.com/kanripo/{code}", "type": "git",
                         "categories": cats, "license": {"name": "CC BY-SA 4.0", "verified": True,
                                                          "status": "ATTRIBUTION_REQUIRED"},
                         "imported_commit": sha, "importer": "tools/import/import_kanripo_extra.py",
                         "enabled": True, "catalog_title": title, "catalog_era": era,
                         "catalog_author": author})
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"REGISTERED {len(CODES)} additional Kanripo sources")


def import_one(code):
    source = read_manifest()[f"kanripo-{code}"]
    title = source["catalog_title"]
    path, categories = category(int(code[-4:]))
    base = ROOT / ".work" / code
    files = [p for p in sorted(base.glob(f"{code}_*.txt"))
             if re.fullmatch(r"\d{3}", p.stem.split("_")[-1])]
    if not files:
        raise FileNotFoundError(f"no source text in {base}")
    units = []
    for file in files:
        content, pages = convert(file.read_text(encoding="utf-8-sig"))
        vol = int(file.stem.split("_")[-1])
        label = "提要及序" if vol == 0 else f"卷{vol}"
        for n, part in enumerate(chunks(content), 1):
            units.append((file.name, label + (f"・整理分段{n}" if len(content) > 120_000 else ""),
                          part, {"volume": vol, "page_start": pages[0] if pages else None,
                                 "page_end": pages[-1] if pages else None,
                                 "editorial_segment": len(content) > 120_000}))
    meta = write_book("kanripo-" + code, title, path, source, units, categories=categories,
                      author=source.get("catalog_author"), work_dynasty=source.get("catalog_era"),
                      edition={"name": "Kanripo", "base_text": None,
                               "volume_count": len([p for p in files if not p.stem.endswith("_000")])},
                      quality={"grade": "B", "ocr": False,
                               "known_issues": ["Bibliographic attribution follows Kanripo catalog; not independently collated"]},
                      original_format="mandoku text")
    print(f"IMPORTED {code} {meta['statistics']['chapters']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--register", action="store_true")
    parser.add_argument("codes", nargs="*")
    args = parser.parse_args()
    if args.register:
        register()
    for code in args.codes or ([] if args.register else CODES):
        if code not in CODES:
            parser.error(f"unknown code: {code}")
        import_one(code)
