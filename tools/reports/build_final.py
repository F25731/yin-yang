"""Build dynamic corpus completion reports from generated metadata."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/validate"))
from checks import validate_coverage

SUBCATS = ["周易","八字四柱","紫微斗数","六爻","梅花易数","奇门遁甲",
           "大六壬","太乙神数","风水堪舆","择日","相术","卜筮"]


def load_books():
    return [json.loads(p.read_text(encoding="utf-8")) for p in (ROOT/"corpus").rglob("metadata.json")]


def nonempty_report_files(pattern):
    rows = []
    for path in sorted((ROOT/"reports").glob(pattern)):
        try:
            lines = [x for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        except Exception:
            continue
        if lines:
            rows.append((path.name, len(lines)))
    return rows


def build():
    stats = json.loads((ROOT/"metadata/statistics.json").read_text(encoding="utf-8"))
    groups = json.loads((ROOT/"metadata/duplicate-groups.json").read_text(encoding="utf-8"))
    books = load_books()
    coverage_errors = validate_coverage()
    cbeta_collections = Counter(
        b.get("source", {}).get("cbeta_collection", "T")
        for b in books if b.get("source", {}).get("source_id") == "cbeta-xml-p5"
    )
    failed = nonempty_report_files("*FAILED_ITEMS.txt")
    withheld = nonempty_report_files("*WITHHELD*.txt")

    lines = [
        "# 建设报告","",
        "本报告由当前 corpus/metadata 自动生成，不再使用第一轮硬编码数字。","",
        "## 当前规模","",
        f"- 独立书目：**{stats['books']} 部**",
        f"- AI 检索单元：**{stats['chapters']} 个**",
        f"- 正文字符：**{stats['characters']}**",
        "- 主类：" + "、".join(f"{k} {v}" for k,v in stats["major_categories"].items()),
        "- 阴阳术数 12 类：" + "、".join(f"{k} {stats['categories'].get(k,0)}" for k in SUBCATS),
        "",
        "## 来源规模","",
    ]
    lines += [f"- {k}：{v} 部" for k,v in sorted(stats["sources"].items())]
    lines += ["","## CBETA 系列覆盖",""]
    lines += [f"- {k}：{v} 部" for k,v in sorted(cbeta_collections.items())]
    lines += [
        "",
        "## 数据质量","",
        "- 质量等级：" + "、".join(f"{k} {v}" for k,v in stats["quality_grades"].items()),
        f"- metadata 缺失：{stats['missing_metadata']}",
        f"- 编码异常：{stats['encoding_errors']}",
        f"- 空正文：{stats['empty_files']}",
        f"- 精确重复组：{stats['exact_duplicate_groups']}",
        f"- 近重复候选：{stats['near_duplicate_candidates']}",
        f"- 同题名版本组：{len(groups.get('edition_groups',[]))}",
        "",
        "## 核心覆盖验收","",
    ]
    if coverage_errors:
        lines += ["**尚有缺口：**",""] + [f"- {x}" for x in coverage_errors]
    else:
        lines += ["**PASS：四大古籍体系与阴阳术数 12 子类核心书目验收通过。**"]
    lines += ["","## 失败 / 暂缓项目",""]
    if not failed and not withheld:
        lines.append("- 无非空失败/暂缓清单。")
    else:
        lines += [f"- {name}：{count} 条" for name,count in failed]
        lines += [f"- {name}：{count} 条" for name,count in withheld]
    lines += [
        "",
        "## AI 使用方式","",
        "1. 先读根目录 CATALOG.md，它只保留小型分类入口。",
        "2. 再进入 indexes/catalog/ 对应分类；按主题可查 indexes/by-topic.md。",
        "3. 小说写作优先看 ai/writing/TOPIC_INDEX.md，随后打开词项中的真实原文章节。",
        "4. 精确搜索使用 metadata/books.jsonl 与 indexes/search-manifest.jsonl。",
        "5. corpus/ 为来源文本整理层，ai/ 只做导航，不得冒充古籍原文。",
        "",
        "## 已知边界","",
        "- 同题名不同版本默认并存，不自动认定某一版为唯一正确文本。",
        "- D/C 级文本应在正式引用前回查上游或影印底本。",
        "- 现代民间灵异材料只作叙事/民俗线索，不作为事实证据。",
        "- ghost 约 70GB 音频不镜像，只建立节目标题索引；AI 资料库优先保存可检索文本。",
        "",
    ]
    (ROOT/"reports/FINAL_REPORT.md").write_text("\n".join(lines),encoding="utf-8")

    gap = ["# Gap Report",""]
    if coverage_errors:
        gap += ["## 核心书目缺口",""] + [f"- {x}" for x in coverage_errors]
    else:
        gap += ["核心分类与指定核心书目：**PASS**。"]
    if failed or withheld:
        gap += ["","## 技术/来源异常",""]
        gap += [f"- {name}：{count} 条" for name,count in failed+withheld]
    else:
        gap += ["","没有非空失败/暂缓清单。"]
    (ROOT/"reports/GAP_REPORT.md").write_text("\n".join(gap)+"\n",encoding="utf-8")

    second = [
        "# Second Pass Report","",
        f"- 最终书目：**{stats['books']}**",
        f"- 最终检索单元：**{stats['chapters']}**",
        f"- 最终字符：**{stats['characters']}**",
        f"- xuanxue 实际入库：**{stats['sources'].get('xuanxue',0)}** 部",
        f"- CBETA 实际入库：**{stats['sources'].get('cbeta-xml-p5',0)}** 部",
        f"- 志怪神异：**{stats['major_categories'].get('志怪神异',0)}** 部",
        f"- 现代民间灵异：**{stats['major_categories'].get('现代民间灵异',0)}** 部",
        "- 核心覆盖：" + ("PASS" if not coverage_errors else f"FAIL ({len(coverage_errors)} gaps)"),
        "",
        "详细信息见 FINAL_REPORT.md、GAP_REPORT.md、COVERAGE_REPORT.md 与各来源导入报告。",
        "",
    ]
    (ROOT/"reports/SECOND_PASS_REPORT.md").write_text("\n".join(second),encoding="utf-8")

    import_lines = ["# 导入报告",""]
    for source_id,count in sorted(stats["sources"].items()):
        import_lines.append(f"- {source_id}：{count} 部")
    import_lines += ["",f"转换失败统计：{stats['conversion_failures']}。",""]
    (ROOT/"reports/IMPORT_REPORT.md").write_text("\n".join(import_lines),encoding="utf-8")
    print("REPORTS BUILT", "coverage=PASS" if not coverage_errors else f"coverage_gaps={len(coverage_errors)}")


if __name__ == "__main__":
    build()
