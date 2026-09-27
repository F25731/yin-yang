"""Import public-domain/classical-text material from youngzs/xuanxue for AI retrieval.

This importer is intentionally selective: it imports classical works and traditional
commentaries that fill the repository taxonomy. Modern tutorials/case studies are
not copied into corpus. Source glyphs and wording are preserved; only light
Markdown cleanup and deterministic chunking are performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ROOT, clean_path_part, read_manifest, write_book, write_json

SOURCE_ID = "xuanxue"

# upstream_dir: (display_title, taxonomy_dir, category_tags, topics, aliases, note)
BOOKS = {
    # 八字四柱
    "《渊海子平》": ("渊海子平", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["子平","八字","十神","格局","神煞"], [], ""),
    "子平真诠": ("子平真诠", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["子平","用神","格局","行运"], [], "上游含评注性内容，按来源保留"),
    "滴天髓-原文": ("滴天髓", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["命理","五行","干支"], [], ""),
    "滴天髓阐微": ("滴天髓阐微", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["命理","五行","干支"], [], ""),
    "穷通宝鉴": ("穷通宝鉴", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["调候","命理","五行"], [], ""),
    "五行精纪": ("五行精纪", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["五行","命理","神煞"], [], ""),
    "玉照定真经": ("玉照定真经", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["命理","干支"], [], ""),
    "星平会海": ("星平会海", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["星命","子平"], [], ""),
    "命理约言": ("命理约言", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["命理","子平"], [], ""),
    "子平管见": ("子平管见", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["命理","子平"], [], ""),
    "御定子平": ("御定子平", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["命理","子平"], [], ""),
    "李虚中命书": ("李虚中命书", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["命理","干支"], [], ""),
    "五行大义": ("五行大义", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["五行","阴阳"], [], ""),
    "神锋通考": ("神峰通考", "04-阴阳术数/02-八字四柱", ["阴阳术数","八字四柱"], ["命理","子平"], ["神锋通考"], "按通行书名作“神峰通考”，保留上游目录别名"),

    # 紫微斗数
    "斗数发微轮": ("斗数发微论", "04-阴阳术数/03-紫微斗数", ["阴阳术数","紫微斗数"], ["紫微斗数","星曜"], ["斗数发微轮"], "上游目录题名疑为“轮/论”异写"),
    "斗数骨髓赋": ("斗数骨髓赋", "04-阴阳术数/03-紫微斗数", ["阴阳术数","紫微斗数"], ["紫微斗数","星曜"], [], ""),
    "女命骨髓赋": ("女命骨髓赋", "04-阴阳术数/03-紫微斗数", ["阴阳术数","紫微斗数"], ["紫微斗数","女命"], [], ""),
    "十喻歌": ("十喻歌", "04-阴阳术数/03-紫微斗数", ["阴阳术数","紫微斗数"], ["紫微斗数"], [], ""),
    "玄微论": ("玄微论", "04-阴阳术数/03-紫微斗数", ["阴阳术数","紫微斗数"], ["紫微斗数"], [], ""),
    "增补太微赋": ("增补太微赋", "04-阴阳术数/03-紫微斗数", ["阴阳术数","紫微斗数"], ["紫微斗数"], [], ""),
    "重补斗数彀率": ("重补斗数彀率", "04-阴阳术数/03-紫微斗数", ["阴阳术数","紫微斗数"], ["紫微斗数"], [], ""),

    # 六爻 / 卜筮
    "卜筮全书": ("卜筮全书", "04-阴阳术数/12-卜筮", ["阴阳术数","卜筮","六爻"], ["六爻","纳甲","黄金策"], [], ""),
    "卜筮正宗": ("卜筮正宗", "04-阴阳术数/12-卜筮", ["阴阳术数","卜筮","六爻"], ["六爻","纳甲","用神","六亲"], [], ""),
    "黄金策": ("黄金策", "04-阴阳术数/04-六爻", ["阴阳术数","六爻","卜筮"], ["六爻","占验"], [], ""),
    "断易天机": ("断易天机", "04-阴阳术数/04-六爻", ["阴阳术数","六爻","卜筮"], ["六爻","断易"], [], ""),
    "易隐": ("易隐", "04-阴阳术数/04-六爻", ["阴阳术数","六爻","卜筮"], ["六爻","占验"], [], ""),
    "易冒": ("易冒", "04-阴阳术数/04-六爻", ["阴阳术数","六爻","卜筮"], ["六爻","占验"], [], ""),
    "易林补遗": ("易林补遗", "04-阴阳术数/12-卜筮", ["阴阳术数","卜筮"], ["占卜","易林"], [], ""),
    "筮学指要": ("筮学指要", "04-阴阳术数/12-卜筮", ["阴阳术数","卜筮"], ["卜筮","易学"], [], ""),
    "洞林秘诀": ("洞林秘诀", "04-阴阳术数/12-卜筮", ["阴阳术数","卜筮"], ["卜筮"], [], ""),
    "京氏易传": ("京氏易传", "04-阴阳术数/12-卜筮", ["阴阳术数","卜筮","周易"], ["京房易","卦气","纳甲"], [], ""),

    # 梅花 / 易学
    "梅花易数": ("梅花易数", "04-阴阳术数/05-梅花易数", ["阴阳术数","梅花易数"], ["梅花易数","起卦","体用"], [], ""),
    "皇极经世": ("皇极经世", "04-阴阳术数/05-梅花易数", ["阴阳术数","梅花易数","周易"], ["邵雍","象数","皇极"], [], ""),

    # 奇门遁甲
    "奇门法窍": ("奇门法窍", "04-阴阳术数/06-奇门遁甲", ["阴阳术数","奇门遁甲"], ["九宫","八门","九星","三奇六仪"], [], ""),
    "奇门遁甲元灵经": ("奇门遁甲元灵经", "04-阴阳术数/06-奇门遁甲", ["阴阳术数","奇门遁甲"], ["九宫","八门","三奇六仪"], [], ""),
    "奇门遁甲秘笈大全": ("奇门遁甲秘笈大全", "04-阴阳术数/06-奇门遁甲", ["阴阳术数","奇门遁甲"], ["九宫","八门","九星","三奇六仪"], [], ""),
    "奇门遁甲统宗大全": ("奇门遁甲统宗大全", "04-阴阳术数/06-奇门遁甲", ["阴阳术数","奇门遁甲"], ["九宫","八门","九星","三奇六仪"], [], "上游明确标有卷四至卷九缺失，保留缺卷说明"),
    "御定奇门宝鉴": ("御定奇门宝鉴", "04-阴阳术数/06-奇门遁甲", ["阴阳术数","奇门遁甲"], ["九宫","八门","九星","烟波钓叟歌"], [], ""),

    # 大六壬
    "六壬大全": ("六壬大全", "04-阴阳术数/07-大六壬", ["阴阳术数","大六壬"], ["六壬","四课三传","毕法赋"], [], ""),
    "六壬粹言": ("六壬粹言", "04-阴阳术数/07-大六壬", ["阴阳术数","大六壬"], ["六壬","毕法"], [], ""),
    "壬归": ("壬归", "04-阴阳术数/07-大六壬", ["阴阳术数","大六壬"], ["六壬"], [], ""),
    "大六壬心境": ("大六壬心镜", "04-阴阳术数/07-大六壬", ["阴阳术数","大六壬"], ["六壬"], ["大六壬心境"], "上游目录作“大六壬心境”，按通行题名建立别名"),
    "大六壬探原": ("大六壬探原", "04-阴阳术数/07-大六壬", ["阴阳术数","大六壬"], ["六壬","占验"], [], ""),
    "大六壬断案": ("大六壬断案", "04-阴阳术数/07-大六壬", ["阴阳术数","大六壬"], ["六壬","占验"], [], ""),
    "注解大六壬指南": ("注解大六壬指南", "04-阴阳术数/07-大六壬", ["阴阳术数","大六壬"], ["六壬","指南"], [], ""),
    "毕法赋": ("毕法赋", "04-阴阳术数/07-大六壬", ["阴阳术数","大六壬"], ["六壬","毕法"], [], ""),
    "壬学锁记": ("壬学锁记", "04-阴阳术数/07-大六壬", ["阴阳术数","大六壬"], ["六壬"], [], ""),

    # 风水堪舆
    "发微论": ("发微论", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","堪舆"], [], ""),
    "撼龙经": ("撼龙经", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["龙脉","疑龙","峦头"], [], ""),
    "博山篇": ("博山篇", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","峦头"], [], ""),
    "催官篇": ("催官篇", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","理气"], [], ""),
    "地理正宗": ("地理正宗", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","地理"], [], ""),
    "入地眼全书": ("入地眼全书", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","龙穴砂水"], [], ""),
    "水龙经": ("水龙经", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","水法"], [], ""),
    "雪心赋": ("雪心赋", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","峦头"], [], ""),
    "阳宅十书": ("阳宅十书", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["阳宅","择日","风水"], [], ""),
    "玉尺经": ("玉尺经", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","理气"], [], ""),
    "葬法倒杖": ("葬法倒杖", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["阴宅","葬法"], [], ""),
    "葬经": ("葬经", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["阴宅","葬法"], ["葬书"], ""),
    "葬经翼": ("葬经翼", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["阴宅","龙穴砂水"], [], ""),
    "宅经": ("宅经", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["阳宅","宅法"], [], ""),
    "青囊经": ("青囊经", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","青囊"], [], ""),
    "金锁玉关经": ("金锁玉关经", "04-阴阳术数/09-风水堪舆", ["阴阳术数","风水堪舆"], ["风水","金锁玉关"], [], ""),

    # 相术
    "柳庄神相": ("柳庄神相", "04-阴阳术数/11-相术", ["阴阳术数","相术"], ["面相","人相"], [], ""),
    "麻衣神相": ("麻衣神相", "04-阴阳术数/11-相术", ["阴阳术数","相术"], ["面相","人相"], [], ""),
    "神相全编": ("神相全编", "04-阴阳术数/11-相术", ["阴阳术数","相术"], ["面相","人相"], [], ""),
    "神相铁关刀": ("神相铁关刀", "04-阴阳术数/11-相术", ["阴阳术数","相术"], ["面相","人相"], [], ""),
    "太清神鉴": ("太清神鉴", "04-阴阳术数/11-相术", ["阴阳术数","相术"], ["面相","人相"], [], ""),
    "公笃相法": ("公笃相法", "04-阴阳术数/11-相术", ["阴阳术数","相术"], ["面相","人相"], [], ""),
    "冰鉴": ("冰鉴", "04-阴阳术数/11-相术", ["阴阳术数","相术"], ["识人","人相"], [], ""),
    "金姣剪": ("金姣剪", "04-阴阳术数/11-相术", ["阴阳术数","相术"], ["相术"], [], ""),
}


def git(*args, cwd=None):
    subprocess.run(["git", *args], cwd=cwd, check=True)


def ensure_source(source, fetch=False):
    root = ROOT / ".work" / "xuanxue"
    if fetch:
        if root.exists():
            shutil.rmtree(root)
        root.parent.mkdir(parents=True, exist_ok=True)
        git("clone", "--filter=blob:none", "--no-checkout", source["url"], str(root))
        git("checkout", source["imported_commit"], cwd=root)
    if not root.exists():
        raise FileNotFoundError(f"{root} missing; use --fetch")
    return root


def clean_markdown(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Images and site-only navigation are not useful to text retrieval.
    text = re.sub(r"!\[[^\]]*\]\([^\n)]+\)", "", text)
    text = re.sub(r"<img\b[^>]*>", "", text, flags=re.I)
    text = re.sub(r"^\s*\[?(?:上一篇|下一篇|返回目录|目录)\]?[:：]?.*$", "", text, flags=re.M)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip() + "\n"


def stable_id(upstream_dir):
    return "xuanxue-" + hashlib.sha1(upstream_dir.encode("utf-8")).hexdigest()[:12]


def remove_existing_source_books():
    for meta_file in list((ROOT / "corpus").rglob("metadata.json")):
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        if meta.get("source", {}).get("source_id") == SOURCE_ID:
            shutil.rmtree(meta_file.parent)


def run(fetch=False):
    source = read_manifest()[SOURCE_ID]
    src = ensure_source(source, fetch)
    remove_existing_source_books()
    imported, failures, imported_files = [], [], 0

    for upstream_dir, spec in BOOKS.items():
        title, category_path, categories, topics, aliases, note = spec
        base = src / "docs" / upstream_dir
        if not base.exists():
            failures.append(f"{upstream_dir}: source directory missing")
            continue

        paths = sorted(
            p for p in base.rglob("*.md")
            if p.name.lower() != "index.md" and p.is_file()
        )
        units = []
        for path in paths:
            try:
                text = clean_markdown(path.read_text(encoding="utf-8-sig"))
            except Exception as exc:
                failures.append(f"{upstream_dir}/{path.name}: {exc}")
                continue
            if len(re.sub(r"\s+", "", text)) < 20:
                continue
            rel = path.relative_to(src).as_posix()
            label = path.stem
            units.append((rel, label, text, {"upstream_dir": upstream_dir}))
        if not units:
            failures.append(f"{upstream_dir}: no usable markdown")
            continue

        target = ROOT / "corpus" / category_path / clean_path_part(title)
        if target.exists():
            # Only replace the same source's previous generated edition. If a
            # different source already owns this exact title path, keep both by suffix.
            meta = target / "metadata.json"
            if meta.exists():
                try:
                    old = json.loads(meta.read_text(encoding="utf-8"))
                except Exception:
                    old = {}
                if old.get("source", {}).get("source_id") != SOURCE_ID:
                    target = ROOT / "corpus" / category_path / clean_path_part(title + "（xuanxue版）")
                    if target.exists():
                        shutil.rmtree(target)
                else:
                    shutil.rmtree(target)

        directory_name = target.name
        known = ["未与纸本或影印本逐字校勘", "来源为公开 GitHub Markdown 整理"]
        if note:
            known.append(note)
        try:
            meta = write_book(
                stable_id(upstream_dir), title, category_path, source, units,
                categories=categories, aliases=aliases, topics=topics,
                quality={"grade": "D", "ocr": False, "known_issues": known},
                original_format="Markdown", directory_name=directory_name,
                processing_changes="Removed site-only image/navigation markup; preserved wording and source glyphs",
            )
            # Some upstream directories mix original text and editorial/modern commentary.
            if upstream_dir in {"子平真诠", "公笃相法"}:
                meta["text_type"] = "mixed_classical_commentary"
                write_json(target / "metadata.json", meta)
            imported.append({"title": title, "dir": upstream_dir, "chapters": len(units), "categories": categories})
            imported_files += len(units)
        except Exception as exc:
            failures.append(f"{upstream_dir}: {exc}")

    report = [
        "# xuanxue 导入报告", "",
        f"- 来源：{source['url']}",
        f"- commit：`{source['imported_commit']}`",
        f"- 导入书目：**{len(imported)}**",
        f"- 导入章节：**{imported_files}**",
        f"- 失败项：**{len(failures)}**", "",
        "## 已导入", "",
    ]
    report += [f"- {x['title']}：{x['chapters']} 章；{' / '.join(x['categories'])}" for x in imported]
    if failures:
        report += ["", "## 失败项", ""] + [f"- {x}" for x in failures]
    (ROOT / "reports/XUANXUE_IMPORT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (ROOT / "reports/XUANXUE_FAILED_ITEMS.txt").write_text("\n".join(failures) + ("\n" if failures else ""), encoding="utf-8")
    print(f"XUANXUE imported={len(imported)} chapters={imported_files} failures={len(failures)}")
    if not imported:
        raise SystemExit("no xuanxue books imported")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()
    run(args.fetch)
