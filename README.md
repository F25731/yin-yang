# 阴阳资料总库

面向 AI 检索与小说创作的中国阴阳、鬼神、志怪、道佛、术数与民间灵异资料库。

仓库目标不是把所有内容一次塞进模型上下文，而是让 GPT / Codex / Claude / Gemini / RAG Agent 能从大规模原始资料中快速定位真正相关的少量章节。

## 内容结构

- `corpus/01-志怪神异/`：志怪、神异、笔记、传奇
- `corpus/02-道藏/`：KR5 道藏体系
- `corpus/03-佛藏/`：CBETA 佛教电子文本
- `corpus/04-阴阳术数/`：
  - 周易
  - 八字四柱
  - 紫微斗数
  - 六爻
  - 梅花易数
  - 奇门遁甲
  - 大六壬
  - 太乙神数
  - 风水堪舆
  - 择日
  - 相术
  - 卜筮
- `corpus/05-现代民间灵异/`：现代网络/民间叙事的检索索引，与古籍严格分开

## AI 怎么读

推荐顺序：

```text
CATALOG.md
↓
indexes/catalog/ 或 ai/writing/TOPIC_INDEX.md
↓
indexes/by-topic.md / metadata/books.jsonl / indexes/search-manifest.jsonl
↓
少量命中的 corpus/ 原文章节
```

不要让模型一次读取整个道藏或佛藏。

详细规则见 [AGENTS.md](AGENTS.md)。

## 数据层

- `corpus/`：来源文本整理版，不混入 AI 创作
- `metadata/`：书目、版本、来源、统计和质量
- `indexes/`：标题、作者、时代、分类、主题及检索单元
- `ai/`：概念和写作导航
- `sources/provenance/`：来源版本、CBETA header/注记等追溯信息
- `reports/`：覆盖、质量、重复、导入与 Gap 报告
- `tools/`：可重复执行的导入、转换、索引和验证脚本

## 可信度

本库记录历史文献、宗教文本、传统术数及民间叙事，不对其中超自然、预测或历史传闻作真实性背书。

古籍正文保留来源字形和措辞；AI 生成的导航内容放在 `ai/`，不得当作古籍原文。

质量等级和来源信息写在每部书的 `metadata.json` 中。正式学术引用建议回查来源底本。

## 更新与验证

```bash
python tools/index/build_all.py
python tools/index/build_ai_indexes.py
python tools/reports/build_final.py
python tools/validate_all.py
```

第二阶段全量补充由 `.github/workflows/complete-corpus.yml` 执行，重点补齐术数核心典籍、志怪补充文本、CBETA 其他藏经系列和现代民间灵异索引。
