"""Shared, dependency-free corpus writer. Source glyphs are never normalized."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_CHARS = 120_000


def read_manifest():
    return {item["id"]: item for item in json.loads((ROOT / "sources/manifest.yaml").read_text(encoding="utf-8"))}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clean_path_part(value):
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value).strip(" .")[:80] or "未题"


def chunks(text, limit=MAX_CHARS):
    """Split only at existing line boundaries; create editorial chunk labels."""
    buf, size = [], 0
    for line in text.splitlines():
        if size + len(line) > limit and buf:
            yield "\n".join(buf).strip() + "\n"
            buf, size = [], 0
        buf.append(line)
        size += len(line) + 1
    if buf:
        yield "\n".join(buf).strip() + "\n"


def frontmatter(meta, chapter, source_path, extra=None):
    fields = {
        "book_id": meta["id"], "title": meta["title"],
        "chapter": chapter, "source_id": meta["source"]["source_id"],
        "source_file": source_path,
    }
    fields.update(extra or {})
    out = ["---"]
    for key, value in fields.items():
        out.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    out.append("categories:")
    out += [f"  - {json.dumps(x, ensure_ascii=False)}" for x in meta["categories"]]
    out.append("---")
    return "\n".join(out) + "\n\n"


def write_book(book_id, title, category_path, source, units, *, categories,
               author=None, author_dynasty=None, work_dynasty=None,
               aliases=None, topics=None, edition=None, quality=None,
               original_format="text/plain", original_script="source_preserved",
               directory_name=None, processing_changes=None):
    """units: [(source relative path, label, source text, provenance dict)]."""
    if not units:
        raise ValueError(f"{book_id}: no text")
    path = ROOT / "corpus" / category_path / clean_path_part(directory_name or title)
    path.mkdir(parents=True, exist_ok=True)
    src = source["url"]
    units = [(p, label, txt.replace("\r\n", "\n").replace("\r", "\n").strip() + "\n", extra)
             for p, label, txt, extra in units if txt.strip()]
    if not units:
        raise ValueError(f"{book_id}: empty text")
    char_count = sum(len(u[2]) for u in units)
    meta = {
        "schema_version": "1.0", "id": book_id, "title": title,
        "aliases": aliases or [], "author": author, "author_dynasty": author_dynasty,
        "work_dynasty": work_dynasty, "categories": categories, "topics": topics or [],
        "text_type": "classical_text", "language": "classical_chinese", "script": original_script,
        "edition": edition or {"name": None, "base_text": None, "volume_count": None},
        "source": {"source_id": source["id"], "repository": src,
                   "commit": source["imported_commit"],
                   "original_path": [u[0] for u in units],
                   "upstream_url": src},
        "license": {"status": source["license"]["status"],
                    "name": source["license"]["name"],
                    "notice": "See LICENSES.md and reports/LICENSE_REPORT.md"},
        "processing": {"importer_version": "1.0", "normalized": True,
                       "ai_modified_text": False, "import_date": str(date.today()),
                       "changes": processing_changes or "Removed source format directives and page markers; preserved source glyphs"},
        "statistics": {"characters": char_count, "chapters": len(units)},
        "quality": quality or {"grade": "B", "ocr": False, "known_issues": []},
        "original_format": original_format, "current_format": "text/markdown; charset=utf-8",
    }
    # Avoid redundant full/chapter copies. Small works use only full.md.
    if len(units) == 1 and char_count < 200_000:
        p, label, txt, extra = units[0]
        (path / "full.md").write_text(frontmatter(meta, label, p, extra) + f"# {title}\n\n" + txt, encoding="utf-8")
        meta["statistics"]["chapters"] = 1
    else:
        chapter_dir = path / "chapters"
        chapter_dir.mkdir(exist_ok=True)
        for idx, (p, label, txt, extra) in enumerate(units, 1):
            (chapter_dir / f"{idx:04d}.md").write_text(frontmatter(meta, label, p, extra) + f"# {label}\n\n" + txt, encoding="utf-8")
        full = path / "full.md"
        if full.exists():
            full.unlink()
    write_json(path / "metadata.json", meta)
    location = path.relative_to(ROOT).as_posix()
    (path / "README.md").write_text(
        f"# {title}\n\n- ID：`{book_id}`\n- 来源：[上游]({src})，commit `{source['imported_commit']}`\n"
        f"- 授权：{source['license']['name']}；详见仓库 LICENSES.md\n"
        f"- 阅读：`{'full.md' if (path / 'full.md').exists() else 'chapters/'}`\n"
        f"- 路径：`{location}`\n\n整理仅移除源格式标记并切分，未改写正文；章节编号如非原书标题，属于整理编号。\n",
        encoding="utf-8")
    return meta


def text_hash(text):
    return hashlib.sha256(text.lstrip("\ufeff").replace("\r\n", "\n").strip().encode("utf-8")).hexdigest()
