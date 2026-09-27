"""Build the human-readable final status from generated statistics."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def build():
    stats = json.loads((ROOT / "metadata/statistics.json").read_text(encoding="utf-8"))
    groups = json.loads((ROOT / "metadata/duplicate-groups.json").read_text(encoding="utf-8"))
    wiki_count = sum(value for key, value in stats["sources"].items() if key.startswith("wikisource-"))
    subcats = ["周易", "八字四柱", "紫微斗数", "六爻", "梅花易数", "奇门遁甲",
               "大六壬", "太乙神数", "风水堪舆", "择日", "相术", "卜筮"]
    lines = ["# 建设报告", "", "生成依据：`metadata/statistics.json`、`metadata/duplicate-groups.json` 与来源审计。",
             "", "## 已导入规模", "",
             f"- 独立正文：**{stats['books']} 部**；检索单元：**{stats['chapters']} 个**；正文字符：**{stats['characters']} 个**。",
             "- 主类书目数（多标签可重复计数）：" + "、".join(f"{k} {v}" for k, v in stats["major_categories"].items()) + "。",
             "- 术数 12 子类：" + "、".join(f"{k} {stats['categories'].get(k, 0)}" for k in subcats) + "。",
             f"- 来源：kr5-corpus 1,650 部；CBETA 大正藏 T 部 {stats['sources'].get('cbeta-xml-p5', 0)} 部；Kanripo 独立仓库 37 部；维基文库 {wiki_count} 部。",
             "", "## 授权与质量", "",
             "- `yaya` 和 `xuanxue` 缺乏覆盖全文的明确再分发许可，只保存来源和目录调查，不提交正文。",
             "- CBETA 导入 xml-p5 仓库所含大正藏 T01–T55、T85，逐文件核对非商业使用及保留 header 的授权字段；保留每部原始 TEI header 和注记。其他藏经系列未导入。",
             "- 质量等级：" + "、".join(f"{k} {v}" for k, v in stats["quality_grades"].items()) + "。道藏 D 主要表示上游书目数据为机器生成且未逐书校核，并不等于已发现正文 OCR 错误。",
             f"- 缺失 metadata {stats['missing_metadata']}；编码异常 {stats['encoding_errors']}；空正文文件 {stats['empty_files']}；转换失败 {stats['conversion_failures']}。",
             "", "## 重复与版本", "",
             f"- 精确重复文本 {stats['duplicate_texts']}；近重复候选 {stats['near_duplicate_candidates']}；同题名版本组 {len(groups['edition_groups'])}。",
             "- 同题名不自动合并。例：《山海經》在 KR3l 和 KR5d 中均有正文，分别保留来源与版本；其他版本组见 `metadata/duplicate-groups.json`。",
             "", "## 仍需完成的覆盖", "",
             "- 12 个术数子类目前均有可检索正文或跨类标签，但这不等于文档所列核心书单已齐。六爻、紫微斗数、奇门、大六壬、太乙、择日等类的作品数量和版本仍偏少。",
             "- 《卜筮正宗》未完整导入；《奇门宝鉴御定》仅有维基文库单页转录，尚未与指定的《御定奇門寶鑑》印本核对完整性。紫微、六爻、奇门等类仍缺多部指定经典。",
             "- 佛藏已覆盖上游 xml-p5 的 T 部，但 CBETA 其他藏经系列尚未做逐文件授权审查及导入。部分佛典部类跨卷，目录按经号分配 T09、T12、T47，其他卷仍按卷号粗分；需继续核对官方部类目录。",
             "- 维基文库《梅花易數》保留原繁体字形和修订 SHA1；《黃金策》采用维基文库所载《卜筮正宗》本文字，版本与署名仍需人工校核。",
             "- 维基文库《閱微草堂筆記》导入全部 24 卷；6 条维基文库编者注单独保留在 provenance，正文保留原字形和逐卷修订 SHA1。",
             "- 维基文库《聊齋志異》导入锁定版全部 12 卷、493 个篇目标题；本版篇目数与常见 496 篇说法有差异，需做版本比对。现代释词、编者注与异文标记单独保留在 provenance。",
             "- 维基文库《增刪卜易》导入卷一分章及卷二至四的连续转录；上游标注主页面 25%、分章页 50% 校对程度，故列为 D 级并须继续与可靠底本对校。",
             "- 维基文库《奇门宝鉴御定》导入单页转录；来源署名‘唐 徐道符’与正文提及明代人物矛盾，故作者、成书时代留空并列为 D 级，完整性及底本待校。",
             "", "## 增量更新和检索", "",
             "1. 先复核来源授权与 `sources/manifest.yaml` 中的 commit 或 revision。",
             "2. 上游检出到 `.work/` 后运行 `python tools/import/import_all.py --source <source-id>`；需要按锁定版本下载时加 `--fetch`。",
             "3. 运行 `python tools/index/build_all.py`、`python tools/index/build_ai_indexes.py` 和 `python tools/validate_all.py`。",
             "4. AI 检索先读 `CATALOG.md`，再查 `metadata/books.jsonl` 或 `indexes/search-manifest.jsonl`，最后打开少数命中章节；引用须标书名、卷次和来源。",
             "", "## 已知限制与验收状态", "",
             "- 道藏页码仅在章节 front matter 中保存起止范围；页内逐行位置须回查上游。CBETA 页行起止范围和注记另存 provenance。",
             "- Kanripo 署名、时代沿用上游目录或留空，未在本项目独立考证；古籍正文未做 AI 改写。",
             "- 本轮完成了四大主类、12 个术数标签、UTF-8、metadata、索引、授权报告与自动校验。由于上述核心书单及其他佛藏系列的覆盖缺口，`EXECUTION.md` 的全部最终验收项**尚未完成**。",
             ""]
    (ROOT / "reports/FINAL_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    import_report = ["# 导入报告", "", "本轮使用锁定来源版本，先审计授权，再在 `.work/` 中获取上游，转换后仅提交可检索正文。", "",
                     "| 来源 | 原格式 | 导入 | 处理 |", "|---|---|---:|---|",
                     "| Kanripo KR3l、KR3g、KR1a | mandoku 按卷文本 | 37 | 清除源格式指令，保留原字形与卷次 |",
                     "| kr5-corpus | UTF-8 文本 + catalog.csv | 1,650 | 按部类和书名建档，按长度切分 |",
                     f"| CBETA 大正藏 T01–T55、T85 | TEI P5 XML | {stats['sources'].get('cbeta-xml-p5', 0)} | XML parser 按卷转换，保留原 header 和注记；逐文件检查授权字段 |",
                     f"| 维基文库 | revision-pinned wikitext | {wiki_count} | 按卷/章节转换，校验 SHA1 |",
                     "| yaya、xuanxue | Markdown/PDF 等 | 0 | 授权不明，仅登记候选路径 |", "",
                     "转换失败：" + str(stats["conversion_failures"]) + "。`KR3l0122_ext.txt` 是非卷次的辅助元数据片段，未作为正文导入。", ""]
    (ROOT / "reports/IMPORT_REPORT.md").write_text("\n".join(import_report), encoding="utf-8")
    print("REPORTS BUILT")


if __name__ == "__main__":
    build()
