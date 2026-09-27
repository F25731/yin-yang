"""Import selected Kanripo mandoku texts, preserving glyphs and source paths."""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, chunks, read_manifest, write_book

BOOKS = {
    "KR3l0099": ("搜神記", "01-志怪神异", ["志怪神异"], "干寶", "東晉", "東晉", "四庫全書・文淵閣"),
    "KR3l0118": ("太平廣記", "01-志怪神异", ["志怪神异"], None, None, "宋", "四庫全書・文淵閣"),
    "KR1a0001": ("周易", "04-阴阳术数/01-周易", ["阴阳术数", "周易"], None, None, None, "tls"),
    "KR3g0042": ("三命通會", "04-阴阳术数/02-八字四柱", ["阴阳术数", "八字四柱"], None, None, "明", "四庫全書・文淵閣"),
    "KR3g0047": ("太乙金鏡式經", "04-阴阳术数/08-太乙神数", ["阴阳术数", "太乙神数"], None, None, "唐", "四庫全書・文淵閣"),
    "KR3g0048": ("遁甲演義", "04-阴阳术数/06-奇门遁甲", ["阴阳术数", "奇门遁甲"], None, None, "明", "四庫全書・文淵閣"),
    "KR3g0051": ("欽定協紀辨方書", "04-阴阳术数/10-择日", ["阴阳术数", "择日"], None, None, "清", "四庫全書・文淵閣"),
}


def convert(raw):
    out, pages = [], []
    for line in raw.replace("\r\n", "\n").splitlines():
        line = line.strip("\ufeff")
        if line.startswith(("# -*-", "#+")) or not line.strip():
            continue
        if line.startswith("<pb:"):
            pages.append(line.removeprefix("<pb:").split(">")[0] if hasattr(str, "removeprefix") else line[4:].split(">")[0])
            continue
        if line.startswith(("@", "<md:")):
            continue
        line = line.replace("¶", "").rstrip()
        if line.startswith("** "):
            line = "## " + line[3:].strip()
        elif line.startswith("* "):
            line = "## " + line[2:].strip()
        if line:
            out.append(line)
    return "\n".join(out).strip(), pages


def import_one(code, source_root=None):
    title, category_path, categories, author, author_dynasty, work_dynasty, base = BOOKS[code]
    manifest = read_manifest()[f"kanripo-{code}"]
    src = Path(source_root) if source_root else ROOT / ".work" / code
    if not src.exists():
        raise FileNotFoundError(f"missing {src}; clone {manifest['url']} at {manifest['imported_commit']}")
    units = []
    files = sorted(src.glob(f"{code}_*.txt"))
    if not files:
        raise ValueError(f"{code}: no source files")
    for file in files:
        raw = file.read_text(encoding="utf-8-sig")
        content, pages = convert(raw)
        volume = int(file.stem.split("_")[-1])
        label = "提要及序" if volume == 0 else f"卷{volume}"
        for segment, part in enumerate(chunks(content), 1):
            suffix = f"・整理分段{segment}" if len(content) > 120_000 else ""
            units.append((file.name, label + suffix, part,
                          {"volume": volume, "page_start": pages[0] if pages else None,
                           "page_end": pages[-1] if pages else None,
                           "editorial_segment": bool(suffix)}))
    meta = write_book("kanripo-" + code, title, category_path, manifest, units,
                      categories=categories, author=author, author_dynasty=author_dynasty,
                      work_dynasty=work_dynasty,
                      edition={"name": base, "base_text": base,
                               "volume_count": len([p for p in files if not p.stem.endswith("_000")])},
                      quality={"grade": "B", "ocr": False,
                               "known_issues": ["Source transcription has not been collated by this project"]},
                      original_format="mandoku text")
    print(f"IMPORTED {code} {meta['statistics']['chapters']} units")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("codes", nargs="*", choices=list(BOOKS) if False else None)
    parser.add_argument("--source-root")
    args = parser.parse_args()
    for code in args.codes or BOOKS:
        if code not in BOOKS:
            parser.error(f"unknown code: {code}")
        import_one(code, args.source_root)
