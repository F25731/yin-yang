"""Validation shared by single-purpose CLI wrappers and validate_all.py."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def books():
    return [json.loads(p.read_text(encoding="utf-8")) for p in (ROOT / "corpus").rglob("metadata.json")]


def validate_encoding():
    errors = []
    for base in ("corpus", "metadata", "indexes", "ai", "sources", "reports", "tools"):
        for path in (ROOT / base).rglob("*"):
            if path.is_file() and path.suffix in {".md", ".json", ".jsonl", ".yaml", ".txt", ".py", ".xml", ".html"}:
                try:
                    path.read_text(encoding="utf-8")
                except UnicodeError:
                    errors.append(f"invalid UTF-8: {path.relative_to(ROOT)}")
    return errors


def validate_metadata():
    errors, seen = [], set()
    manifest = {s["id"]: s for s in json.loads((ROOT / "sources/manifest.yaml").read_text(encoding="utf-8"))}
    required = {"schema_version", "id", "title", "categories", "source", "license", "processing", "statistics", "quality"}
    for meta_file in (ROOT / "corpus").rglob("metadata.json"):
        try:
            book = json.loads(meta_file.read_text(encoding="utf-8"))
        except (UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"invalid metadata {meta_file}: {exc}")
            continue
        missing = required - set(book)
        if missing:
            errors.append(f"{meta_file}: missing {sorted(missing)}")
            continue
        bid = book["id"]
        if bid in seen:
            errors.append(f"duplicate book id: {bid}")
        seen.add(bid)
        if book["schema_version"] != "1.0" or not book["title"] or not book["categories"]:
            errors.append(f"bad basic fields: {bid}")
        if book["source"].get("source_id") not in manifest:
            errors.append(f"source not registered: {bid}")
        if not re.fullmatch(r"[0-9a-f]{40}", book["source"].get("commit", "")):
            errors.append(f"missing source commit: {bid}")
        if book["license"].get("status") not in {"OK_TO_REDISTRIBUTE", "ATTRIBUTION_REQUIRED", "NONCOMMERCIAL_OR_RESTRICTED", "SOURCE_TERMS_UNCLEAR"}:
            errors.append(f"unapproved license for corpus: {bid}")
        if book["processing"].get("ai_modified_text") is not False:
            errors.append(f"AI-modified text marked: {bid}")
        if book["quality"].get("grade") not in {"A", "B", "C", "D", "E"}:
            errors.append(f"invalid quality grade: {bid}")
    return errors


def validate_corpus():
    errors = []
    paths = {}
    for meta_file in (ROOT / "corpus").rglob("metadata.json"):
        item = json.loads(meta_file.read_text(encoding="utf-8"))
        paths[item["id"]] = meta_file.parent
    for book in books():
        bid = book["id"]
        path = paths.get(bid)
        if path is None:
            errors.append(f"no book directory: {bid}")
            continue
        units = sorted((path / "chapters").glob("*.md")) if (path / "chapters").exists() else [path / "full.md"]
        if not units or any(not p.exists() for p in units):
            errors.append(f"missing text: {bid}")
            continue
        if len(units) != book["statistics"]["chapters"]:
            errors.append(f"chapter count mismatch: {bid}")
        for file in units:
            if file.stat().st_size > 1_000_000:
                errors.append(f"oversized text: {file.relative_to(ROOT)}")
            text = file.read_text(encoding="utf-8")
            if not text.startswith("---\n") or f'book_id: "{bid}"' not in text[:500]:
                errors.append(f"frontmatter mismatch: {file.relative_to(ROOT)}")
            if not text.split("---", 2)[-1].strip():
                errors.append(f"empty text: {file.relative_to(ROOT)}")
            if "<pb:" in text or "<lb:" in text or "#+PROPERTY" in text:
                errors.append(f"source markup retained: {file.relative_to(ROOT)}")
    for git in (ROOT / "corpus").rglob(".git"):
        errors.append(f"nested git: {git.relative_to(ROOT)}")
    return errors


def validate_duplicates():
    data = json.loads((ROOT / "metadata/duplicate-groups.json").read_text(encoding="utf-8"))
    return [f"exact duplicate group: {group['books']}" for group in data["exact_groups"]]


def validate_indexes():
    errors = []
    corpus_books = books()
    ids = {book["id"] for book in corpus_books}
    index_books = [json.loads(line) for line in (ROOT / "metadata/books.jsonl").read_text(encoding="utf-8").splitlines()]
    if {book["id"] for book in index_books} != ids:
        errors.append("books.jsonl IDs differ from corpus metadata")
    units = [json.loads(line) for line in (ROOT / "indexes/search-manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    if len(units) != sum(book["statistics"]["chapters"] for book in corpus_books):
        errors.append("search-manifest unit count differs from corpus metadata")
    if len({unit["id"] for unit in units}) != len(units):
        errors.append("search-manifest has duplicate IDs")
    for unit in units:
        if unit["book_id"] not in ids or not (ROOT / unit["path"]).is_file():
            errors.append(f"bad search unit: {unit['id']}")
    stats = json.loads((ROOT / "metadata/statistics.json").read_text(encoding="utf-8"))
    if stats["books"] != len(ids) or stats["chapters"] != len(units):
        errors.append("statistics counts differ from indexes")
    return errors


def validate_links():
    errors = []
    for path in [ROOT / "README.md", ROOT / "CATALOG.md", ROOT / "LICENSES.md"]:
        if not path.exists():
            errors.append(f"missing {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        links = re.findall(r"\]\(<([^>]+)>\)|\]\(([^)]+)\)", text)
        for angled, plain in links:
            target = angled or plain
            if target.startswith(("https://", "http://", "#")):
                continue
            if not (path.parent / target).exists():
                errors.append(f"broken link: {path.name} -> {target}")
    return errors


REQUIRED_METAPHYSICS_CATEGORIES = [
    "周易", "八字四柱", "紫微斗数", "六爻", "梅花易数", "奇门遁甲",
    "大六壬", "太乙神数", "风水堪舆", "择日", "相术", "卜筮",
]

# Each inner tuple is satisfied when any title/alias contains one alternative.
REQUIRED_WORK_GROUPS = {
    "志怪神异": [
        ("搜神記", "搜神记"), ("太平廣記", "太平广记"), ("聊齋志異", "聊斋志异"),
        ("山海經", "山海经"), ("博物志",), ("述異記", "述异记"), ("閱微草堂筆記", "阅微草堂笔记"),
    ],
    "八字四柱": [
        ("三命通會", "三命通会"), ("淵海子平", "渊海子平"), ("子平真詮", "子平真诠"),
        ("滴天髓",), ("窮通寶鑑", "穷通宝鉴"), ("五行精紀", "五行精纪"),
    ],
    "紫微斗数": [("斗數骨髓賦", "斗数骨髓赋"), ("玄微論", "玄微论"), ("太微賦", "太微赋")],
    "六爻": [("增刪卜易", "增删卜易"), ("卜筮正宗",), ("卜筮全書", "卜筮全书"), ("黃金策", "黄金策")],
    "梅花易数": [("梅花易數", "梅花易数")],
    "奇门遁甲": [("遁甲演義", "遁甲演义"), ("奇門法竅", "奇门法窍"), ("奇門遁甲元靈經", "奇门遁甲元灵经")],
    "大六壬": [("六壬大全",), ("六壬粹言",), ("大六壬心鏡", "大六壬心镜", "大六壬心境")],
    "太乙神数": [("太乙金鏡式經", "太乙金镜式经")],
    "风水堪舆": [("葬書", "葬书", "葬經", "葬经"), ("撼龍經", "撼龙经"), ("陽宅十書", "阳宅十书"), ("青囊經", "青囊经")],
    "择日": [("協紀辨方書", "协纪辨方书")],
    "相术": [("麻衣神相",), ("神相全編", "神相全编"), ("柳莊神相", "柳庄神相")],
    "卜筮": [("卜筮正宗",), ("京氏易傳", "京氏易传")],
}


def validate_coverage():
    errors = []
    corpus = books()
    counts = {cat: sum(cat in b.get("categories", []) for b in corpus) for cat in REQUIRED_METAPHYSICS_CATEGORIES}
    for cat, count in counts.items():
        if count == 0:
            errors.append(f"empty metaphysics category: {cat}")

    def labels(book):
        return [book.get("title", "")] + list(book.get("aliases", []))

    for cat, groups in REQUIRED_WORK_GROUPS.items():
        scoped = [b for b in corpus if cat in b.get("categories", []) or cat == "志怪神异" and "志怪神异" in b.get("categories", [])]
        all_labels = [label for b in scoped for label in labels(b)]
        for alternatives in groups:
            if not any(any(alt in label for alt in alternatives) for label in all_labels):
                errors.append(f"missing core work in {cat}: {' / '.join(alternatives)}")
    return errors
