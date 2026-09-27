"""Deterministically rebuild corpus metadata, catalog, search and audit reports."""
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, read_manifest, write_json

MAJORS = ["志怪神异", "道藏", "佛藏", "阴阳术数"]


def dump_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def body(path):
    text = path.read_text(encoding="utf-8-sig")
    if text.startswith("---\n"):
        text = text.split("---\n", 2)[-1]
    if text.startswith("\n# "):
        text = text.split("\n", 3)[-1]
    return text.strip()


def canonical(text):
    return re.sub(r"[\W_]+", "", text)


def title_key(title):
    return re.sub(r"[\W_]+", "", title)


def build_duplicates(books, files_by_id):
    exact, by_title, signatures = defaultdict(list), defaultdict(list), {}
    title_counts = Counter(title_key(book["title"]) for book in books)
    for book in books:
        bid = book["id"]
        text = "\n".join(body(p) for p in files_by_id[bid])
        strict = text.lstrip("\ufeff").replace("\r\n", "\n").strip()
        norm = canonical(text)
        digest = hashlib.sha256(strict.encode("utf-8")).hexdigest()
        exact[digest].append(bid)
        by_title[title_key(book["title"])].append(bid)
        if title_counts[title_key(book["title"])] > 1:
            shingles = {norm[i:i + 5] for i in range(0, max(0, len(norm) - 4), max(1, len(norm) // 2000))}
            signatures[bid] = (len(norm), shingles)
    exact_groups = [{"kind": "exact_strict", "hash": key, "books": ids}
                    for key, ids in exact.items() if len(ids) > 1]
    near = []
    editions = []
    for key, ids in by_title.items():
        if len(ids) < 2:
            continue
        editions.append({"canonical_work": key, "editions": ids})
        for i, first in enumerate(ids):
            for second in ids[i + 1:]:
                size_a, set_a = signatures[first]
                size_b, set_b = signatures[second]
                ratio = min(size_a, size_b) / max(size_a, size_b) if max(size_a, size_b) else 0
                similarity = len(set_a & set_b) / len(set_a | set_b) if (set_a | set_b) else 0
                if ratio >= .8 and similarity >= .75:
                    near.append({"books": [first, second], "length_ratio": round(ratio, 3),
                                 "sampled_5gram_jaccard": round(similarity, 3), "status": "review"})
    result = {"exact_groups": exact_groups, "near_candidates": near, "edition_groups": editions,
              "method": "Unicode-preserving punctuation/space removal; sampled 5-gram Jaccard only among identical titles"}
    write_json(ROOT / "metadata/duplicate-groups.json", result)
    return result


def markdown_index(title, books, key_fn):
    groups = defaultdict(list)
    for book in books:
        for key in key_fn(book):
            groups[key or "未详"].append(book)
    lines = ["# " + title, ""]
    for key in sorted(groups):
        lines.extend(["## " + key, ""])
        for book in sorted(groups[key], key=lambda x: (x["title"], x["id"])):
            label = book["title"].replace("[", "\\[").replace("]", "\\]")
            lines.append(f"- [{label}](<../{book['path']}/README.md>) — `{book['id']}`")
        lines.append("")
    return "\n".join(lines)


def build():
    manifest = read_manifest()
    books, files_by_id, search = [], {}, []
    empty_files = 0
    for meta_file in sorted((ROOT / "corpus").rglob("metadata.json")):
        book = json.loads(meta_file.read_text(encoding="utf-8"))
        book["path"] = meta_file.parent.relative_to(ROOT).as_posix()
        units = sorted((meta_file.parent / "chapters").glob("*.md")) if (meta_file.parent / "chapters").exists() else [meta_file.parent / "full.md"]
        if not units or any(not p.is_file() for p in units):
            raise ValueError(f"{book['id']}: missing content")
        files_by_id[book["id"]] = units
        books.append(book)
        for pos, file in enumerate(units, 1):
            unit_chars = len(body(file))
            if unit_chars == 0:
                empty_files += 1
            search.append({"id": f"{book['id']}:{pos:04d}", "book_id": book["id"],
                           "book": book["title"], "path": file.relative_to(ROOT).as_posix(),
                           "categories": book["categories"], "topics": book.get("topics", []),
                           "characters": unit_chars, "source_id": book["source"]["source_id"]})
    books.sort(key=lambda x: x["id"])
    search.sort(key=lambda x: x["id"])
    dump_jsonl(ROOT / "metadata/books.jsonl", books)
    dump_jsonl(ROOT / "indexes/search-manifest.jsonl", search)
    write_json(ROOT / "metadata/sources.json", list(manifest.values()))
    write_json(ROOT / "metadata/aliases.json", {book["id"]: book.get("aliases", []) for book in books if book.get("aliases")})
    write_json(ROOT / "indexes/titles.json", {book["id"]: book["title"] for book in books})
    keywords = defaultdict(list)
    for book in books:
        for word in book.get("topics", []):
            keywords[word].append(book["id"])
    write_json(ROOT / "indexes/keywords.json", dict(keywords))
    index_dir = ROOT / "indexes"
    index_dir.mkdir(exist_ok=True)
    for filename, title, fn in [
        ("by-title.md", "按书名", lambda b: [b["title"][0]]),
        ("by-author.md", "按作者", lambda b: [b.get("author") or "未详"]),
        ("by-dynasty.md", "按时代", lambda b: [b.get("work_dynasty") or "未详"]),
        ("by-category.md", "按分类", lambda b: b["categories"]),
        ("by-source.md", "按来源", lambda b: [b["source"]["source_id"]]),
    ]:
        (index_dir / filename).write_text(markdown_index(title, books, fn), encoding="utf-8")
    catalog = ["# 阴阳资料总库目录", "", "先按类定位，再读取具体章节；同一部书可有多个分类标签，但正文只存一处。", ""]
    for major in MAJORS:
        catalog.extend(["## " + major, ""])
        selected = [book for book in books if major in book["categories"]]
        if not selected:
            catalog.extend(["当前没有可再分发正文。", ""])
        for book in sorted(selected, key=lambda x: (x["categories"][1:] or [""], x["title"])):
            path = book["path"]
            label = book["title"].replace("[", "\\[").replace("]", "\\]")
            catalog.extend([f"### [{label}](<{path}/README.md>)",
                            f"- 作者：{book.get('author') or '未详'}；时代：{book.get('work_dynasty') or '未详'}",
                            f"- 分类：{'、'.join(book['categories'])}；来源：{book['source']['source_id']}",
                            f"- 章节：{book['statistics']['chapters']}；路径：`{path}`", ""])
    (ROOT / "CATALOG.md").write_text("\n".join(catalog), encoding="utf-8")
    duplicates = build_duplicates(books, files_by_id)
    major_counts = {key: sum(key in b["categories"] for b in books) for key in MAJORS}
    category_counts = Counter(cat for book in books for cat in book["categories"])
    source_counts = Counter(book["source"]["source_id"] for book in books)
    grades = Counter(book["quality"].get("grade", "E") for book in books)
    book_dirs = {p.parent for p in (ROOT / "corpus").rglob("metadata.json")}
    content_dirs = {p.parent for p in (ROOT / "corpus").rglob("full.md")}
    content_dirs.update(p.parent.parent for p in (ROOT / "corpus").rglob("chapters/*.md"))
    stats = {"books": len(books), "chapters": len(search),
             "characters": sum(b["statistics"]["characters"] for b in books),
             "major_categories": major_counts, "categories": dict(sorted(category_counts.items())),
             "sources": dict(sorted(source_counts.items())), "quality_grades": dict(sorted(grades.items())),
             "exact_duplicate_groups": len(duplicates["exact_groups"]),
             "duplicate_texts": sum(len(group["books"]) - 1 for group in duplicates["exact_groups"]),
             "near_duplicate_candidates": len(duplicates["near_candidates"]),
             "missing_metadata": len(content_dirs - book_dirs),
             "encoding_errors": 0,
             "empty_files": empty_files,
             "unverified_license_sources": sum(not s["license"]["verified"] for s in manifest.values()),
             "conversion_failures": sum(len(p.read_text(encoding="utf-8").splitlines())
                                        for p in (ROOT / "reports").glob("*_FAILED_ITEMS.txt"))}
    write_json(ROOT / "metadata/statistics.json", stats)
    (ROOT / "reports/COVERAGE_REPORT.md").write_text(
        "# 覆盖报告\n\n" + f"书目 {stats['books']}；章节/检索单元 {stats['chapters']}；正文字符 {stats['characters']}。\n\n"
        + "## 主类\n\n" + "\n".join(f"- {k}：{v}" for k, v in major_counts.items())
        + "\n\n## 子类\n\n" + "\n".join(f"- {k}：{v}" for k, v in sorted(category_counts.items())) + "\n",
        encoding="utf-8")
    (ROOT / "reports/DUPLICATE_REPORT.md").write_text(
        "# 重复与版本报告\n\n" + f"完全相同组 {len(duplicates['exact_groups'])}；同题名版本组 {len(duplicates['edition_groups'])}；近似候选 {len(duplicates['near_candidates'])}。\n\n"
        + "详情见 `metadata/duplicate-groups.json`。近似候选仅供人工判断，不自动删除正文。\n",
        encoding="utf-8")
    (ROOT / "reports/QUALITY_REPORT.md").write_text(
        "# 质量报告\n\n" + "\n".join(f"- {k}：{v} 部" for k, v in sorted(grades.items()))
        + f"\n\n转换失败 {stats['conversion_failures']}；精确重复组 {stats['exact_duplicate_groups']}；近重复候选 {stats['near_duplicate_candidates']}。\n"
        + "\nB 表示来源明确但本项目未逐字校勘；D 表示来源书目信息或版本仍待核验。详见各书 `metadata.json`。\n",
        encoding="utf-8")
    print(f"INDEXED {len(books)} books, {len(search)} units")


if __name__ == "__main__":
    build()
