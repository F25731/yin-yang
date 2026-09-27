"""Build AI-readable indexes for modern folklore sources without mirroring large media."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, read_manifest, write_book, write_json


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "yin-yang-corpus-builder/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def tianya_index(source):
    raw = fetch_text(
        "https://raw.githubusercontent.com/exposir/supernatural_tianya/"
        + source["imported_commit"] + "/README.md"
    )
    # Retain only post headings and tiny contextual labels, not the copied forum body.
    headings = []
    for line in raw.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            headings.append(m.group(1))
    text = (
        "# 天涯灵异帖子索引\n\n"
        "来源为 GitHub 上的天涯旧帖脱水整理。本库只保存帖子标题/楼层索引与来源，"
        "不复制完整论坛正文。需要具体内容时由 AI 依据来源链接按需核对。\n\n"
        + "\n".join(f"- {x}" for x in headings)
        + "\n"
    )
    meta = write_book(
        "modern-tianya-supernatural-index",
        "天涯灵异帖子索引",
        "05-现代民间灵异/天涯灵异",
        source,
        [("README.md", "帖子索引", text, {})],
        categories=["现代民间灵异"],
        topics=["民间灵异","网络怪谈","都市传说","罗布泊","鬼神","奇闻"],
        quality={"grade":"C","ocr":False,"known_issues":["仅索引，不代表帖文真实性；完整正文未镜像"]},
        original_format="Markdown",
        directory_name="中国有没有调查异事件的官方机构-索引",
        processing_changes="Extracted heading-level post index only; full forum body not mirrored",
    )
    meta["text_type"] = "modern_folklore_index"
    path = ROOT / "corpus/05-现代民间灵异/天涯灵异/中国有没有调查异事件的官方机构-索引/metadata.json"
    write_json(path, meta)
    return len(headings)


def ghost_index(source):
    api = (
        "https://api.github.com/repos/Justsenger/ghost/git/trees/"
        + source["imported_commit"] + "?recursive=1"
    )
    data = json.loads(fetch_text(api))
    rows = []
    for item in data.get("tree", []):
        path = item.get("path", "")
        if item.get("type") != "blob" or not path.lower().endswith((".mp3",".m4a",".wav",".flac")):
            continue
        name = Path(path).name
        m = re.match(r"\((\d+)\)\s*(.+?)\s*-\s*.+?\.(?:mp3|m4a|wav|flac)$", name, flags=re.I)
        if m:
            episode, title = m.group(1), m.group(2).strip()
        else:
            episode, title = "", Path(name).stem
        rows.append({"episode": episode, "title": title, "path": path})
    rows.sort(key=lambda x: (x["episode"], x["path"]))
    index_dir = ROOT / "indexes"
    index_dir.mkdir(exist_ok=True)
    (index_dir / "ghost-audio-titles.jsonl").write_text(
        "".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows),
        encoding="utf-8",
    )
    md = [
        "# 灵异事件簿音频标题索引", "",
        f"来源：{source['url']}，commit `{source['imported_commit']}`。",
        "仅建立标题索引，不镜像约 70GB 的音频文件。标题只能作为写作检索线索，不能视作事实证据。", "",
    ]
    md += [f"- {x['episode']} {x['title']}".strip() for x in rows]
    (index_dir / "ghost-audio-titles.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return len(rows)


def run():
    manifest = read_manifest()
    a = tianya_index(manifest["supernatural-tianya"])
    b = ghost_index(manifest["ghost-audio"])
    report = (
        "# 现代民间灵异索引报告\n\n"
        f"- 天涯帖子标题索引：{a} 条\n"
        f"- ghost 音频标题索引：{b} 条\n"
        "- 现代网络叙事与古籍正文严格分开；这些材料不作为历史事实背书。\n"
    )
    (ROOT / "reports/MODERN_FOLKLORE_REPORT.md").write_text(report, encoding="utf-8")
    print(f"MODERN_FOLKLORE tianya={a} ghost_titles={b}")


if __name__ == "__main__":
    run()
