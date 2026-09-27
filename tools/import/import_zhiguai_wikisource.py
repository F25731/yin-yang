"""Fill the zhiguai shelf from revision-tracked Chinese Wikisource pages.

Rendered HTML is converted to plain Markdown-ish text, source revisions are stored
in provenance, and the manifest snapshot hash is recomputed from revision SHA1s.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import urllib.parse
import urllib.request
import urllib.error
import time
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, chunks, clean_path_part, read_manifest, write_book, write_json

API = "https://zh.wikisource.org/w/api.php"
SOURCE_ID = "wikisource-zhiguai-bulk"

WORKS = {
    "神異經": {"author": "傳東方朔", "dynasty": "漢", "topics": ["神怪","異獸","異聞"]},
    "拾遺記": {"author": "王嘉", "dynasty": "晉", "topics": ["志怪","神仙","異聞"]},
    "酉陽雜俎": {"author": "段成式", "dynasty": "唐", "topics": ["志怪","妖異","博物"]},
    "夷堅志": {"author": "洪邁", "dynasty": "宋", "topics": ["鬼神","民間傳說","異聞"]},
    "子不語": {"author": "袁枚", "dynasty": "清", "topics": ["鬼怪","志怪","民間傳說"]},
    "夜譚隨錄": {"author": "和邦額", "dynasty": "清", "topics": ["鬼怪","志怪"]},
    "耳食錄": {"author": "樂鈞", "dynasty": "清", "topics": ["志怪","鬼怪"]},
    "螢窗異草": {"author": None, "dynasty": "清", "topics": ["志怪","鬼怪"]},
    "剪燈新話": {"author": "瞿佑", "dynasty": "明", "topics": ["傳奇","志怪","鬼怪"]},
    "剪燈餘話": {"author": "李昌祺", "dynasty": "明", "topics": ["傳奇","志怪","鬼怪"]},
    "宣室志": {"author": "張讀", "dynasty": "唐", "topics": ["志怪","鬼神"]},
    "玄怪錄": {"author": "牛僧孺", "dynasty": "唐", "topics": ["志怪","傳奇"]},
    "廣異記": {"author": "戴孚", "dynasty": "唐", "topics": ["志怪","鬼神"]},
    "集異記": {"author": "薛用弱", "dynasty": "唐", "topics": ["志怪","傳奇"]},
    "獨異志": {"author": "李亢", "dynasty": "唐", "topics": ["志怪","異聞"]},
    "幽明錄": {"author": "劉義慶", "dynasty": "南朝宋", "topics": ["鬼神","志怪"]},
    "異苑": {"author": "劉敬叔", "dynasty": "南朝宋", "topics": ["鬼神","志怪"]},
    "冥報記": {"author": "唐臨", "dynasty": "唐", "topics": ["因果","冥界","鬼神"]},
    "朝野僉載": {"author": "張鷟", "dynasty": "唐", "topics": ["異聞","筆記"]},
}


def api(params):
    params = dict(params)
    params.update({"format": "json", "formatversion": "2", "maxlag": "5"})
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "YinYangCorpus/2.1 (F25731/yin-yang; batch importer)"})
    last = None
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            time.sleep(0.18)
            return payload
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            retry = exc.headers.get("Retry-After")
            delay = float(retry) if retry and retry.isdigit() else min(60, 2 ** attempt)
            time.sleep(delay)
        except urllib.error.URLError as exc:
            last = exc
            time.sleep(min(30, 2 ** attempt))
    raise last


def list_subpages(title):
    result, cont = [], None
    while True:
        params = {"action": "query", "list": "allpages", "apprefix": title + "/", "aplimit": "max", "apnamespace": 0}
        if cont:
            params["apcontinue"] = cont
        data = api(params)
        result.extend(x["title"] for x in data.get("query", {}).get("allpages", []))
        cont = data.get("continue", {}).get("apcontinue")
        if not cont:
            break
    return result


def revisions(titles):
    result = {}
    for offset in range(0, len(titles), 40):
        batch = titles[offset:offset + 40]
        data = api({
            "action": "query", "prop": "revisions", "titles": "|".join(batch),
            "rvprop": "ids|sha1", "rvslots": "main",
        })
        for page in data.get("query", {}).get("pages", []):
            if page.get("missing") or not page.get("revisions"):
                continue
            rev = page["revisions"][0]
            result[page["title"]] = {
                "title": page["title"], "revid": rev.get("revid"), "sha1": rev.get("sha1")
            }
    return [result[t] for t in titles if t in result]


def rendered_text(title):
    data = api({"action":"parse","page":title,"prop":"text|revid","disableeditsection":1})
    parsed = data.get("parse")
    if not parsed:
        raise ValueError("page parse failed")
    html = parsed.get("text", "")
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one(".mw-parser-output") or soup
    for selector in [
        "script","style",".mw-editsection",".ws-noexport",".noprint",".navbox",
        ".toc",".reference",".mw-cite-backlink",".sistersitebox",".ambox"
    ]:
        for node in root.select(selector):
            node.decompose()
    for h in root.find_all(["h1","h2","h3","h4","h5","h6"]):
        level = min(int(h.name[1]) + 1, 6)
        h.insert_before("\n" + "#" * level + " ")
        h.append("\n")
    text = root.get_text("\n")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n", parsed.get("revid")


def update_source_snapshot(lock):
    path = ROOT / "sources/manifest.yaml"
    data = json.loads(path.read_text(encoding="utf-8"))
    digest = hashlib.sha1(
        "\n".join(f"{x['title']}\t{x.get('revid')}\t{x.get('sha1')}" for x in lock).encode("utf-8")
    ).hexdigest()
    for item in data:
        if item["id"] == SOURCE_ID:
            item["imported_commit"] = digest
            item["snapshot_pages"] = len(lock)
            break
    else:
        raise KeyError(SOURCE_ID)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return digest


def run():
    plan, missing = {}, []
    lock = []
    for work in WORKS:
        pages = list_subpages(work)
        if not pages:
            pages = [work]
        revs = revisions(pages)
        lock.extend(revs)
        if revs:
            plan[work] = revs
        else:
            missing.append(work)

    snapshot = update_source_snapshot(lock)
    source = read_manifest()[SOURCE_ID]
    if source["imported_commit"] != snapshot:
        raise RuntimeError("manifest snapshot update failed")

    provenance = ROOT / "sources/provenance/wikisource-zhiguai"
    provenance.mkdir(parents=True, exist_ok=True)
    write_json(provenance / "revisions.json", {"snapshot": snapshot, "pages": lock})

    imported, failures = [], []
    for work, revs in plan.items():
        spec = WORKS[work]
        units = []
        for info in revs:
            try:
                text, parsed_revid = rendered_text(info["title"])
                if len(re.sub(r"\s+", "", text)) < 40:
                    continue
                parts = list(chunks(text))
                for n, part in enumerate(parts, 1):
                    label = info["title"] + (f"・整理分段{n}" if len(parts) > 1 else "")
                    units.append((
                        info["title"], label, part,
                        {"revision_id": info["revid"], "revision_sha1": info["sha1"],
                         "parsed_revision_id": parsed_revid, "editorial_segment": len(parts) > 1},
                    ))
            except Exception as exc:
                failures.append(f"{work} / {info['title']}: {exc}")
        if not units:
            failures.append(f"{work}: no usable text")
            continue
        try:
            meta = write_book(
                "wikisource-zhiguai-" + hashlib.sha1(work.encode("utf-8")).hexdigest()[:12],
                work, "01-志怪神异", source, units,
                categories=["志怪神异"],
                author=spec["author"], work_dynasty=spec["dynasty"],
                topics=spec["topics"] + ["志怪神异"],
                edition={"name":"中文維基文庫渲染文本","base_text":None,"volume_count":len(revs),
                         "snapshot":snapshot},
                quality={"grade":"C","ocr":False,
                         "known_issues":["Wikisource transcription not independently collated by this project",
                                         "Rendered-page cleanup may omit navigation/editorial apparatus"]},
                original_format="MediaWiki rendered HTML",
                processing_changes="Removed navigation/edit controls; converted headings to Markdown; preserved rendered wording",
                directory_name=work,
            )
            imported.append({"title":work,"chapters":meta["statistics"]["chapters"]})
        except Exception as exc:
            failures.append(f"{work}: {exc}")

    (ROOT / "reports/WIKISOURCE_ZHIGUAI_FAILED_ITEMS.txt").write_text(
        "\n".join(failures + [f"missing page: {x}" for x in missing]) + ("\n" if failures or missing else ""),
        encoding="utf-8")
    lines = ["# 志怪补充导入报告","",f"- snapshot：`{snapshot}`",
             f"- 目标：{len(WORKS)} 部",f"- 成功：{len(imported)} 部",
             f"- 找不到页面：{len(missing)} 部",f"- 其他失败：{len(failures)} 项","",
             "## 已导入",""] + [f"- {x['title']}：{x['chapters']} 个检索单元" for x in imported]
    if missing:
        lines += ["","## 未找到",""] + [f"- {x}" for x in missing]
    (ROOT / "reports/WIKISOURCE_ZHIGUAI_REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(f"WIKISOURCE ZHIGUAI imported={len(imported)} missing={len(missing)} failures={len(failures)}")


if __name__ == "__main__":
    run()
