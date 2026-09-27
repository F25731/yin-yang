"""Create citation-first concept entry points from actual lexical hits."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONCEPTS = {
    "魂": ["魂", "亡魂", "還魂"], "魄": ["魄"], "三魂七魄": ["三魂", "七魄"],
    "鬼": ["鬼"], "神": ["神"], "妖": ["妖"], "精": ["精"],
    "阴阳": ["陰陽", "阴阳"], "五行": ["五行"], "黄泉": ["黃泉", "黄泉"],
    "地府": ["地府", "冥府"], "轮回": ["輪迴", "轮回"], "尸解": ["尸解", "屍解"],
    "招魂": ["招魂", "召魂"], "托梦": ["託夢", "托梦", "夢告"],
    "超度": ["超度", "濟度"], "镇煞": ["鎮煞", "镇煞", "鎮邪"], "丧葬": ["喪葬", "丧葬", "葬"]
}
RELATIONS = {
    "死亡体系": ["魂", "魄", "鬼", "黄泉", "丧葬"],
    "魂魄体系": ["魂", "魄", "三魂七魄", "招魂"],
    "鬼神体系": ["鬼", "神", "妖", "精"],
    "地府体系": ["地府", "黄泉", "鬼"],
    "轮回体系": ["轮回", "超度", "地府"],
    "道教神仙体系": ["神", "尸解", "魂"],
    "驱邪镇煞体系": ["镇煞", "鬼", "妖"],
    "占卜体系": ["阴阳", "五行"],
    "风水体系": ["阴阳", "五行", "丧葬"],
}


def build():
    manifest = [json.loads(line) for line in (ROOT / "indexes/search-manifest.jsonl").read_text(encoding="utf-8").splitlines()]
    hits = {concept: defaultdict(list) for concept in CONCEPTS}
    for item in manifest:
        file = ROOT / item["path"]
        text = file.read_text(encoding="utf-8")
        if text.startswith("---\n"):
            text = text.split("---\n", 2)[-1]
        major = item["categories"][0]
        for concept, words in CONCEPTS.items():
            if len(hits[concept][major]) >= 3:
                continue
            if any(word in text for word in words):
                hits[concept][major].append(item)
    concepts_dir = ROOT / "ai/concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    for concept, words in CONCEPTS.items():
        lines = [f"# {concept}", "", "> AI 辅助词项索引；以下仅为关键词命中，不等于语义、版本或历史结论。", "",
                 "## 检索词", "", "、".join(words), "", "## 原文候选", ""]
        for major in ("志怪神异", "道藏", "佛藏", "阴阳术数"):
            for item in hits[concept][major]:
                lines.append(f"- {item['book']}：[`{item['path']}`](../../{item['path']})")
        if not any(hits[concept].values()):
            lines.append("当前仓库未找到直接关键词命中。")
        lines.extend(["", "引用前必须打开章节核对上下文与出处。", ""])
        (concepts_dir / f"{concept}.md").write_text("\n".join(lines), encoding="utf-8")
    relations_dir = ROOT / "ai/relations"
    relations_dir.mkdir(parents=True, exist_ok=True)
    for name, concepts in RELATIONS.items():
        lines = ["# " + name, "", "> AI 辅助检索导航；本页不构成古籍所述统一理论。", "", "## 相关词项", ""]
        lines += [f"- [{item}](../concepts/{item}.md)" for item in concepts]
        lines += ["", "按相关词项进入原文候选，再核对具体章节。", ""]
        (relations_dir / f"{name}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"AI INDEXED {len(CONCEPTS)} concepts, {len(RELATIONS)} relation entry points")


if __name__ == "__main__":
    build()
