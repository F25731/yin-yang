"""Import the licensed KR5 plain-text collection using its authoritative catalog.csv."""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, read_manifest, write_book

SUBCATS = {
    "KR5a": "洞真部", "KR5b": "洞玄部", "KR5c": "洞神部",
    "KR5d": "太玄部", "KR5e": "太平部", "KR5f": "太清部",
    "KR5g": "正一部", "KR5h": "续道藏", "KR5i": "其他",
}
PAGE = re.compile(r"^【([^】]+)】\s*$")


def parse_pages(text):
    pages = []
    current_page = None
    for line in text.replace("\r\n", "\n").splitlines():
        found = PAGE.match(line)
        if found:
            current_page = found.group(1)
            continue
        if line.strip():
            pages.append((current_page, line.rstrip()))
    return pages


def make_units(path, text):
    lines = parse_pages(text)
    units, buf, size, start, end = [], [], 0, None, None
    for page, line in lines:
        if size + len(line) > 100_000 and buf:
            units.append((path, f"整理分段{len(units) + 1}", "\n".join(buf) + "\n",
                          {"page_start": start, "page_end": end, "editorial_segment": True}))
            buf, size, start = [], 0, None
        if start is None:
            start = page
        end = page
        buf.append(line)
        size += len(line) + 1
    if buf:
        units.append((path, f"整理分段{len(units) + 1}", "\n".join(buf) + "\n",
                      {"page_start": start, "page_end": end,
                       "editorial_segment": len(units) > 0}))
    return units


def run(source_root=None, limit=None):
    source = read_manifest()["kr5-corpus"]
    base = Path(source_root) if source_root else ROOT / ".work/kr5-corpus"
    catalog = base / "catalog.csv"
    if not catalog.exists():
        raise FileNotFoundError(f"missing {catalog}; clone {source['url']}")
    with catalog.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    names = Counter(r["title"] for r in rows if r.get("path"))
    failures, imported = [], 0
    for row in rows:
        if not row.get("path"):
            continue
        source_file = base / row["path"]
        if not source_file.is_file():
            failures.append(f"{row['id']}: missing {row['path']}")
            continue
        try:
            text = source_file.read_text(encoding="utf-8-sig")
            units = make_units(row["path"], text)
            if not units:
                raise ValueError("empty text")
            title = row["title"].strip() or row["id"]
            sub = SUBCATS.get(row["subcat"], "其他")
            categories = ["道藏", sub]
            if row["id"] == "KR5h0055":
                categories.extend(["阴阳术数", "紫微斗数"])
            quality = {"grade": "B" if "検証済" in row.get("status", "") else "D",
                       "ocr": False, "known_issues": [] if "検証済" in row.get("status", "")
                       else ["Catalog marks bibliographic data as machine-generated or unverified"]}
            meta = write_book(row["id"], title, "02-道藏/" + sub, source, units,
                              categories=categories, author=row["author"] or None,
                              work_dynasty=row["era"] or None,
                              edition={"name": row["baseedition"] or None,
                                       "base_text": row["baseedition"] or None,
                                       "volume_count": None, "kanripo_commit": row["commit"],
                                       "kanripo_witness": row["witness"],
                                       "dz_no": row["dz_no"] or None},
                              quality=quality, original_format="KR5 plain text",
                              directory_name=title + (f"（{row['id']}）" if names[title] > 1 else ""))
            imported += 1
            if imported % 100 == 0:
                print(f"IMPORTED KR5 {imported}", flush=True)
            if limit and imported >= limit:
                break
        except (UnicodeError, OSError, ValueError) as exc:
            failures.append(f"{row['id']}: {exc}")
    report = ROOT / "reports/KR5_FAILED_ITEMS.txt"
    report.write_text("\n".join(failures) + ("\n" if failures else ""), encoding="utf-8")
    print(f"KR5 imported={imported} failed={len(failures)}")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    run(args.source_root, args.limit)
