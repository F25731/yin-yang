"""Create citation-first concept entry points from actual lexical hits."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONCEPTS = {
    "魂": ["魂", "亡魂", "還魂", "还魂"], "魄": ["魄"], "三魂七魄": ["三魂", "七魄"],
    "死亡": ["死", "亡者", "亡人"], "还魂与复生": ["還魂", "还魂", "復生", "复生", "死而復生", "死而复生"],
    "鬼": ["鬼"], "神": ["神"], "妖": ["妖"], "精怪": ["精怪", "精魅", "物魅"],
    "阴阳": ["陰陽", "阴阳"], "五行": ["五行"], "黄泉": ["黃泉", "黄泉"],
    "冥界": ["冥界", "冥府", "幽冥"], "地府": ["地府", "冥府"], "地狱": ["地獄", "地狱"],
    "轮回": ["輪迴", "轮回", "六道"], "中阴": ["中陰", "中阴"],
    "尸解": ["尸解", "屍解"], "尸变": ["屍變", "尸变", "僵尸", "殭屍"],
    "招魂": ["招魂", "召魂", "復魂", "复魂"], "托梦": ["託夢", "托梦", "夢告", "梦告"],
    "超度": ["超度", "濟度", "济度", "度亡"], "镇煞": ["鎮煞", "镇煞", "鎮邪", "镇邪"],
    "驱邪": ["驅邪", "驱邪", "辟邪"], "符箓": ["符籙", "符箓", "符咒"], "雷法": ["雷法", "雷霆"],
    "丧葬": ["喪葬", "丧葬", "葬", "送葬"], "停灵守灵": ["停靈", "停灵", "守靈", "守灵"],
    "头七": ["頭七", "头七", "七七"], "纸扎烧纸": ["紙紮", "纸扎", "燒紙", "烧纸"],
    "冥婚": ["冥婚", "陰婚", "阴婚"], "鬼门中元": ["鬼門", "鬼门", "中元", "七月半"],
    "附体": ["附體", "附体", "憑附", "凭附"], "业与因果": ["業報", "业报", "因果", "業力", "业力"],
    "阎罗鬼王": ["閻羅", "阎罗", "鬼王"], "夜叉罗刹": ["夜叉", "羅剎", "罗刹"],
    "神煞": ["神煞", "煞"], "太岁": ["太歲", "太岁"],
    "龙穴砂水": ["龍脈", "龙脉", "穴", "砂", "水口"],
    "占卜预兆": ["占卜", "卜", "兆", "占驗", "占验"],
}
RELATIONS = {
    "死亡体系": ["死亡", "魂", "魄", "鬼", "黄泉", "丧葬", "还魂与复生"],
    "魂魄体系": ["魂", "魄", "三魂七魄", "招魂", "托梦", "附体"],
    "鬼神体系": ["鬼", "神", "妖", "精怪", "阎罗鬼王", "夜叉罗刹"],
    "地府体系": ["冥界", "地府", "黄泉", "地狱", "阎罗鬼王"],
    "轮回体系": ["轮回", "中阴", "业与因果", "超度", "地府"],
    "道教神仙体系": ["神", "尸解", "符箓", "雷法", "魂"],
    "驱邪镇煞体系": ["镇煞", "驱邪", "符箓", "雷法", "鬼", "妖"],
    "丧葬民俗体系": ["丧葬", "停灵守灵", "头七", "纸扎烧纸", "冥婚", "鬼门中元"],
    "占卜体系": ["阴阳", "五行", "占卜预兆", "神煞", "太岁"],
    "风水体系": ["阴阳", "五行", "龙穴砂水", "丧葬"],
}

WRITING_TOPICS = {
    "死人不知道自己已经死了": ["死亡", "魂", "鬼", "冥界", "中阴"],
    "亡者还魂或死而复生": ["还魂与复生", "招魂", "魂", "魄"],
    "死者托梦给活人": ["托梦", "魂", "鬼"],
    "魂魄不全与失魂": ["魂", "魄", "三魂七魄", "招魂"],
    "阴间与地府场景": ["冥界", "地府", "黄泉", "地狱", "阎罗鬼王"],
    "轮回与往生": ["轮回", "中阴", "业与因果", "超度"],
    "尸体异变与尸解": ["尸变", "尸解", "死亡"],
    "妖怪精魅与附体": ["妖", "精怪", "附体"],
    "驱邪镇煞与符法": ["驱邪", "镇煞", "符箓", "雷法"],
    "停灵守灵与送葬": ["丧葬", "停灵守灵", "头七"],
    "纸扎烧纸与亡者供奉": ["纸扎烧纸", "丧葬", "鬼"],
    "冥婚与阴婚": ["冥婚", "丧葬"],
    "中元鬼门与七月半": ["鬼门中元", "鬼"],
    "风水阴宅与墓葬": ["龙穴砂水", "丧葬", "阴阳"],
    "占卜预兆与凶吉": ["占卜预兆", "神煞", "太岁", "阴阳", "五行"],
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
            if len(hits[concept][major]) >= 5:
                continue
            if any(word in text for word in words):
                hits[concept][major].append(item)
    concepts_dir = ROOT / "ai/concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)
    for concept, words in CONCEPTS.items():
        lines = [f"# {concept}", "", "> AI 辅助词项索引；以下仅为关键词命中，不等于语义、版本或历史结论。", "",
                 "## 检索词", "", "、".join(words), "", "## 原文候选", ""]
        for major in ("志怪神异", "道藏", "佛藏", "阴阳术数", "现代民间灵异"):
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
    writing = ROOT / "ai/writing"
    writing.mkdir(parents=True, exist_ok=True)
    lines = ["# 小说写作主题入口", "",
             "> 先按问题进入词项，再打开词项中的原文候选。这里是检索导航，不把不同传统强行合成统一设定。", ""]
    for topic, concepts in WRITING_TOPICS.items():
        lines += [f"## {topic}", ""]
        lines += [f"- [{concept}](../concepts/{concept}.md)" for concept in concepts]
        lines.append("")
    (writing / "TOPIC_INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"AI INDEXED {len(CONCEPTS)} concepts, {len(RELATIONS)} relation entry points, {len(WRITING_TOPICS)} writing topics")


if __name__ == "__main__":
    build()
