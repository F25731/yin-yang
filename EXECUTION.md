# EXECUTION.md — 阴阳资料总库 AI-Ready 仓库全面整理任务

> 目标仓库：`https://github.com/F25731/yin-yang`  
> 默认分支：`main`  
> 项目目标：将分散在多个公开古籍/宗教/术数项目中的资料，整理为一个**适合 Codex、ChatGPT、Claude、Gemini、RAG/Agent 直接检索和读取**的统一中文知识库。  
> 核心用途：小说创作、世界观设计、传统文化资料检索、志怪/鬼神/道佛/术数考据。  
> 这是一个“AI 可检索语料库”，不是普通电子书收藏仓库，也不是单纯镜像上游仓库。

---

# 0. Codex 总指令

你现在负责完整建设 `F25731/yin-yang`。

不要只写方案、不要只创建空目录、不要停留在 README。
请实际完成：

1. 调研并锁定全部上游来源。
2. 检查每个来源的许可证、版权说明和可再分发范围。
3. 拉取可合法使用的数据。
4. 解析源格式。
5. 清洗文本。
6. 去除代码、网页壳、导航、广告、无关说明。
7. 统一字符编码。
8. 建立规范目录。
9. 识别书名、作者、朝代、卷次、章节。
10. 生成统一 metadata。
11. 处理重复版本。
12. 按 AI 读取需求切分 Markdown。
13. 生成目录索引和机器可读索引。
14. 对全库进行完整性检查。
15. 编写导入脚本，使后续能够重新同步上游。
16. 编写验证脚本，确保数据不会因为后续更新被破坏。
17. 分阶段提交到本仓库。
18. 最后输出完整的建设报告。

除非遇到明确的法律/授权障碍，否则不要因为数据量大而只做 Demo。

**禁止将上游仓库直接作为 Git submodule 结束任务。**
最终 `yin-yang` 必须能够在没有上游仓库存在的情况下，被 AI 独立读取和检索。

---

# 1. 核心设计原则

## 1.1 原始文献与 AI 内容必须严格分离

绝对不允许将 AI 的解释、现代翻译、总结或推测混入古籍原文。

仓库必须区分：

- `corpus/`：可验证的原始文献清洗版
- `metadata/`：结构化元数据
- `indexes/`：机器生成的索引
- `ai/`：AI 辅助生成的概念索引、摘要、关系图等
- `tools/`：导入、转换、验证脚本
- `sources/`：来源与版本记录

任何位于 `corpus/` 的内容都必须能够追溯到具体来源。

---

## 1.2 不修改原文含义

清洗允许：

- 转 UTF-8
- 修复明显乱码
- 规范换行
- 去除 HTML 标签
- 去除网页导航
- 去除代码壳
- 去除重复页眉页脚
- 将 XML 结构转换为 Markdown
- 按卷、品、篇、章节进行结构化切分

默认不允许：

- 擅自现代汉语改写
- 将繁体统一转简体
- 将简体统一转繁体
- 擅自补字
- 根据模型记忆校改古籍
- 删除异体字
- 修改疑似错字
- 将不同版本强行合并为“正确版本”

如果发现明显 OCR 错误，只记录到 `metadata/quality/` 或校勘字段。
未经可靠底本佐证，不直接改正文。

---

## 1.3 默认保留原始字形

不同来源可能包含：

- 简体
- 繁体
- 异体字
- Unicode 扩展汉字

全部尽量保留。

如后续需要简繁统一检索，通过索引层处理，不破坏正文。

---

## 1.4 所有书必须可追溯

每一部书至少记录：

- 统一 ID
- 书名
- 别名
- 作者
- 作者时代
- 成书时代
- 分类
- 子分类
- 来源项目
- 来源 URL
- 来源文件
- 来源 commit SHA / tag / release（可获得时）
- 原格式
- 当前格式
- 字符集
- 卷数
- 章节数
- 字数
- 校勘/质量状态
- 授权信息
- 导入日期
- 数据生成脚本版本

---

# 2. 最终目录结构

必须以以下结构为主，不要随意改成英文大类名称。

```text
yin-yang/
│
├── README.md
├── CATALOG.md
├── CONTRIBUTING.md
├── LICENSES.md
├── SOURCES.md
├── AGENTS.md
│
├── corpus/
│   │
│   ├── 01-志怪神异/
│   │   ├── 搜神记/
│   │   ├── 搜神后记/
│   │   ├── 太平广记/
│   │   ├── 聊斋志异/
│   │   ├── 山海经/
│   │   ├── 博物志/
│   │   ├── 述异记/
│   │   ├── 阅微草堂笔记/
│   │   ├── 夷坚志/
│   │   └── 其他/
│   │
│   ├── 02-道藏/
│   │   ├── 洞真部/
│   │   ├── 洞玄部/
│   │   ├── 洞神部/
│   │   ├── 太玄部/
│   │   ├── 太平部/
│   │   ├── 太清部/
│   │   ├── 正一部/
│   │   ├── 续道藏/
│   │   └── 其他/
│   │
│   ├── 03-佛藏/
│   │   ├── 阿含/
│   │   ├── 本缘/
│   │   ├── 般若/
│   │   ├── 法华/
│   │   ├── 华严/
│   │   ├── 宝积/
│   │   ├── 涅槃/
│   │   ├── 密教/
│   │   ├── 律部/
│   │   ├── 论部/
│   │   ├── 净土/
│   │   ├── 禅宗/
│   │   ├── 史传/
│   │   ├── 诸宗/
│   │   ├── 藏外/
│   │   └── 其他/
│   │
│   └── 04-阴阳术数/
│       │
│       ├── 01-周易/
│       ├── 02-八字四柱/
│       ├── 03-紫微斗数/
│       ├── 04-六爻/
│       ├── 05-梅花易数/
│       ├── 06-奇门遁甲/
│       ├── 07-大六壬/
│       ├── 08-太乙神数/
│       ├── 09-风水堪舆/
│       ├── 10-择日/
│       ├── 11-相术/
│       └── 12-卜筮/
│
├── metadata/
│   ├── books.jsonl
│   ├── sources.json
│   ├── taxonomy.json
│   ├── aliases.json
│   ├── statistics.json
│   ├── duplicate-groups.json
│   └── quality/
│
├── indexes/
│   ├── by-title.md
│   ├── by-author.md
│   ├── by-dynasty.md
│   ├── by-category.md
│   ├── by-source.md
│   ├── keywords.json
│   ├── titles.json
│   └── search-manifest.jsonl
│
├── ai/
│   ├── README.md
│   ├── concepts/
│   ├── relations/
│   ├── summaries/
│   └── writing/
│
├── sources/
│   ├── manifest.yaml
│   ├── licenses/
│   └── provenance/
│
├── tools/
│   ├── import/
│   ├── convert/
│   ├── normalize/
│   ├── index/
│   ├── validate/
│   └── reports/
│
└── reports/
    ├── IMPORT_REPORT.md
    ├── COVERAGE_REPORT.md
    ├── DUPLICATE_REPORT.md
    ├── LICENSE_REPORT.md
    ├── QUALITY_REPORT.md
    └── FINAL_REPORT.md
```

---

# 3. 数据来源

## 3.1 志怪神异

主要来源：

### A. yaya

```text
https://github.com/dreamsxin/yaya
```

重点查找并导入志怪、神异、笔记小说类内容，包括但不限于：

- 搜神记
- 搜神后记
- 聊斋志异
- 述异记
- 博物志
- 山海经
- 太平广记相关文本
- 阅微草堂笔记
- 夷坚志
- 其他神怪、鬼神、异闻、志怪典籍

不能把整个 yaya 无差别复制进来。
只导入与本库主题直接相关的文本。

### B. Kanripo《搜神记》

```text
https://github.com/kanripo/KR3l0099
```

### C. Kanripo《太平广记》

```text
https://github.com/kanripo/KR3l0118
```

对于 yaya 与 Kanripo 出现的重复文本：

- 不要保留两份相同正文作为普通书籍。
- 建立 duplicate group。
- 优先保留结构更完整、来源信息更明确、卷次更稳定的版本作为 `primary`。
- 其他版本保留 provenance 和版本差异信息。
- 如文本差异显著，可保存为独立 edition。

---

# 4. 道藏

主要来源：

```text
https://github.com/tokushige-koyasan/kr5-corpus
```

这是本项目道藏主语料来源。

目标分类：

- 洞真部
- 洞玄部
- 洞神部
- 太玄部
- 太平部
- 太清部
- 正一部
- 续道藏
- 其他

Codex 必须首先研究其原始目录结构、文件命名和元数据规则，再写 importer。

不要仅按文件夹名称猜测书名。

尽量保留：

- 原 Kanripo ID
- 道藏部类
- 书名
- 卷号
- 版本信息
- 原始来源 URL

如果原项目中有目录/metadata，优先程序化使用。

---

# 5. 佛藏

主来源：

```text
https://github.com/cbeta-org/xml-p5
```

CBETA 不允许简单粗暴地用正则删除 XML 标签。

必须使用 XML Parser。

建议 Python：

- `lxml`
- 或标准库 XML parser

必须识别和尽量保留：

- 经名
- CBETA 编号
- 藏经编号
- 卷
- 品
- 译者
- 作者
- 序
- 正文
- 偈颂
- 注记对应关系
- page/line 定位信息（至少在 metadata/provenance 中保留）
- 原始 XML 路径

## 5.1 AI 阅读版转换

CBETA XML 转换后的 Markdown 需要做到：

```markdown
---
id: cbeta-T0001
title: 长阿含经
source: CBETA
source_file: ...
canonical_id: ...
---

# 长阿含经

## 卷一

正文……

## 卷二

正文……
```

不要把 XML 技术标记大量混进正文。

但不可丢失关键结构信息。

## 5.2 切分

长经不得形成几十 MB 的单个 Markdown。

优先按：

1. 经
2. 卷
3. 品
4. 自然结构

进行切分。

---

# 6. 阴阳术数总来源

核心总仓：

```text
https://github.com/youngzs/xuanxue
```

该仓库不是整仓直接复制。

Codex 需要：

1. 盘点全部典籍。
2. 根据本项目 taxonomy 重新分类。
3. 剔除不属于本项目目标的无关内容。
4. 保留来源信息。
5. 对重复古籍进行去重。
6. 对 EPUB/PDF/MOBI 等不适合直接读取的格式，如许可允许，转为 UTF-8 Markdown；若无法可靠解析，则记录为待处理，不得伪造正文。

---

# 7. 阴阳术数分类要求

## 7.1 周易

至少包括：

- 周易正文
- 系辞传
- 说卦传
- 序卦传
- 杂卦传

来源：

```text
https://github.com/kanripo/KR1a0001
```

如 xuanxue 中存在相关版本，也纳入版本比较，但避免重复正文。

---

## 7.2 八字四柱

重点收录：

- 渊海子平
- 三命通会
- 子平真诠
- 穷通宝鉴
- 滴天髓
- 滴天髓阐微
- 神峰通考
- 李虚中命书
- 五行大义
- 五行精纪
- 玉照定真经
- 星平会海
- 命理约言
- 子平管见
- 御定子平
- 以及 xuanxue 中同类可靠文本

补充来源：

```text
https://github.com/kanripo/KR3g0042
```

即《三命通会》。

---

## 7.3 紫微斗数

重点收录：

- 斗数发微论
- 斗数骨髓赋
- 女命骨髓赋
- 十喻歌
- 玄微论
- 增补太微赋
- 重补斗数彀率
- xuanxue 中其他紫微文本

如果只有现代排盘程序而没有原典，不要把代码放进 `corpus/`。

算法实现可记录在 `SOURCES.md`，但本仓库的核心是文献。

---

## 7.4 六爻

重点收录：

- 增删卜易
- 卜筮正宗
- 卜筮全书
- 黄金策
- 断易天机
- 易隐
- 易冒
- 易林补遗
- 筮学指要
- 洞林秘诀

六爻和卜筮有交叉。

原则：

- 一部书只保留一个正文实体。
- 可拥有多个 category 标签。
- 不允许为了分类方便复制两份正文。

例如：

```json
"categories": ["六爻", "卜筮"]
```

---

## 7.5 梅花易数

至少包括：

- 梅花易数
- 相关原典/可靠古籍版本

重点检查 xuanxue。

现代算法实现仅作为辅助来源，不代替古籍。

---

## 7.6 奇门遁甲

至少包括：

- 御定奇门宝鉴
- 奇门法窍
- 奇门遁甲元灵经
- 奇门遁甲秘笈大全
- 奇门遁甲统宗大全
- 遁甲演义

额外来源：

```text
https://github.com/kanripo/KR3g0048
```

《遁甲演义》。

---

## 7.7 大六壬

至少包括：

- 六壬大全
- 六壬粹言
- 壬归
- 大六壬心镜
- 大六壬探原
- 大六壬断案
- 注解大六壬指南
- xuanxue 中其他六壬文献

如版本重复，使用 edition 机制，不复制同一正文。

---

## 7.8 太乙神数

核心原典：

```text
https://github.com/kanripo/KR3g0047
```

《太乙金镜式经》。

必须完整收录可合法使用的全部卷次。

继续检查 xuanxue 是否还有：

- 太乙
- 太乙神数
- 太乙统宗
- 太乙金镜
- 相关古籍

发现后纳入，但标明版本。

---

## 7.9 风水堪舆

重点收录：

- 博山篇
- 催官篇
- 地理正宗
- 发微论
- 撼龙经
- 金锁玉关经
- 青囊经
- 入地眼全书
- 水龙经
- 雪心赋
- 阳宅十书
- 玉尺经
- 葬法倒杖
- 葬经
- 葬经翼
- 宅经
- xuanxue 中其他堪舆文献

必须区分：

- 阳宅
- 阴宅
- 峦头
- 理气
- 水法
- 玄空
- 三合
- 葬法

这些可作为 `topics`，不要强行创建重复正文。

---

## 7.10 择日

核心来源：

```text
https://github.com/kanripo/KR3g0051
```

《钦定协纪辨方书》。

同时检查 xuanxue 内择日、选择、通书类古籍。

分类关键词至少包括：

- 择日
- 选择
- 宜忌
- 神煞
- 历法

---

## 7.11 相术

重点收录：

- 冰鉴
- 公笃相法
- 观人于微
- 金姣剪
- 柳庄神相
- 麻衣神相
- 神相全编
- 神相铁关刀
- 太清神鉴
- 其他人相、骨相、手相古籍

如果文本中混有现代作者解释，必须区分 `classical_text` 与 `modern_commentary`。

---

## 7.12 卜筮

重点包括：

- 增删卜易
- 卜筮全书
- 卜筮正宗
- 黄金策
- 断易天机
- 筮学指要
- 京氏易传
- 易林补遗
- 易隐
- 其他古代卜筮文献

与六爻交叉时使用多标签，不复制正文。

---

# 8. Source Manifest

创建：

```text
sources/manifest.yaml
```

每个来源至少：

```yaml
- id: kr5-corpus
  name: Kanripo KR5 Corpus
  url: https://github.com/tokushige-koyasan/kr5-corpus
  type: git
  categories:
    - 道藏
  license:
    name: unknown
    verified: false
  imported_commit: ""
  importer: tools/import/import_kr5.py
  enabled: true
```

其他来源同样登记。

必须记录实际导入时的 commit SHA。

这样未来可以判断上游是否更新。

---

# 9. 许可证与版权检查

这是强制步骤，不得跳过。

对每个来源检查：

- LICENSE
- README 中授权声明
- 文本文件头部版权声明
- 上游来源说明
- CBETA 使用规范
- Kanripo 使用说明
- 其他数据项目的再分发要求

输出：

```text
reports/LICENSE_REPORT.md
```

分类：

```text
OK_TO_REDISTRIBUTE
ATTRIBUTION_REQUIRED
NONCOMMERCIAL_OR_RESTRICTED
UNCLEAR
DO_NOT_REDISTRIBUTE
```

## 9.1 遇到授权不明确

不要凭“古籍已经公版”就判断数字化版本一定可自由再发布。

如果某个数字化数据集本身授权不明确：

1. 不删除它。
2. 在 `sources/manifest.yaml` 中记录。
3. 在 `LICENSE_REPORT.md` 中说明。
4. 若不适合直接提交正文，则只提交：
   - metadata
   - importer
   - provenance
   - source URL
5. 不要把明显受限制的数据强行推到公开仓库。

---

# 10. 每本书的目录规范

每部书使用：

```text
书名/
├── README.md
├── metadata.json
├── full.md
└── chapters/
    ├── 001.md
    ├── 002.md
    └── ...
```

如果书很短，可以只有：

```text
书名/
├── README.md
├── metadata.json
└── full.md
```

如果书非常长：

- `full.md` 可以不生成。
- 以 `chapters/` 为主。
- README 中说明。

不要创建超过 GitHub 单文件安全范围的大文件。

建议：

- 普通章节：20KB～200KB
- 尽量不超过 500KB
- 极端情况下不得超过 1MB，除非结构不允许合理再切分

---

# 11. metadata.json 规范

统一 schema：

```json
{
  "schema_version": "1.0",
  "id": "zhiguai-soushenji",
  "title": "搜神记",
  "aliases": [],
  "author": "干宝",
  "author_dynasty": "东晋",
  "work_dynasty": "东晋",
  "categories": [
    "志怪神异"
  ],
  "topics": [
    "鬼神",
    "妖异",
    "魂魄",
    "民间信仰"
  ],
  "text_type": "classical_text",
  "language": "classical_chinese",
  "script": "traditional_or_source_preserved",
  "edition": {
    "name": "",
    "base_text": "",
    "volume_count": null
  },
  "source": {
    "source_id": "kanripo-KR3l0099",
    "repository": "https://github.com/kanripo/KR3l0099",
    "commit": "",
    "original_path": ""
  },
  "license": {
    "status": "",
    "name": "",
    "notice": ""
  },
  "processing": {
    "importer_version": "1.0",
    "normalized": true,
    "ai_modified_text": false
  },
  "statistics": {
    "characters": 0,
    "chapters": 0
  },
  "quality": {
    "status": "unchecked",
    "ocr": false,
    "known_issues": []
  }
}
```

---

# 12. Markdown 正文规范

每个章节开头使用 YAML Front Matter。

例如：

```markdown
---
book_id: zhiguai-soushenji
title: 搜神记
volume: 1
chapter: 1
categories:
  - 志怪神异
source_id: kanripo-KR3l0099
---

# 卷一

原文……
```

**正文内部不增加 AI 解释。**

如果原文没有标题，不要让 AI 编一个看起来像原典标题的标题。

可以使用：

```text
第001则
第002则
```

但必须在 metadata 标明这是“整理编号”，不是原书标题。

---

# 13. 去重策略

去重不是简单比较文件 SHA。

至少实现三层：

## 第一层：完全相同

对 normalize 后正文：

- 去 BOM
- 统一换行
- 去首尾空白

计算 SHA-256。

完全一致即 duplicate。

## 第二层：近似相同

生成用于比较的临时文本：

- 去 Markdown 标记
- 去标点
- 去空格
- 不做简繁转换

计算：

- 长度比
- SimHash / MinHash
- n-gram 相似度

高相似文本进入待判断列表。

## 第三层：版本关系

如果书名相同但正文不同：

不要删除。

建立：

```json
{
  "canonical_work": "三命通会",
  "editions": [
    "...",
    "..."
  ]
}
```

区分：

- 同一版重复
- 不同版本
- 节本
- 摘抄
- 注本
- 现代整理本

输出：

```text
reports/DUPLICATE_REPORT.md
```

---

# 14. AI 检索设计

本仓库不预先要求生成向量数据库。

先做好“文本 + 结构化 metadata + 搜索索引”。

因为 Codex / Agent 可以直接使用：

- 文件路径
- ripgrep
- title index
- JSONL
- metadata

## 14.1 search-manifest.jsonl

每个可检索单元一行：

```json
{"id":"...","book":"搜神记","path":"corpus/01-志怪神异/搜神记/chapters/001.md","categories":["志怪神异"],"topics":["鬼神","魂魄"],"characters":12345}
```

这样 Agent 可以：

1. 先搜索引。
2. 找候选文件。
3. 只读取相关章节。

而不是扫描全库。

---

# 15. CATALOG.md

必须自动生成，不要手工维护。

结构：

```markdown
# 阴阳资料总库目录

## 志怪神异

### 搜神记
- 作者：干宝
- 朝代：东晋
- 卷数：20
- 来源：Kanripo
- 路径：...
- 标签：鬼神、妖异、魂魄

### 太平广记
...

## 道藏
...

## 佛藏
...

## 阴阳术数

### 周易
...

### 八字四柱
...
```

CATALOG 的目标是：

**AI 进入仓库后只看这个文件，就知道去哪找资料。**

---

# 16. AGENTS.md

在仓库根目录创建 `AGENTS.md`，告诉 Codex / Agent 如何使用资料。

至少包含：

```markdown
# AI 使用规则

当任务涉及中国古代鬼神、阴阳、志怪、道教、佛教、术数、
丧葬、魂魄、轮回、风水、占卜、民俗时：

1. 优先搜索本仓库。
2. 先搜索 metadata / indexes。
3. 再读取具体原文。
4. 不要一次读取整个 corpus。
5. 区分古籍原文、现代整理和 AI 内容。
6. `corpus/` 是来源文本。
7. `ai/` 是辅助材料，不可伪装成古籍。
8. 引用传统文化设定时尽量给出书名、卷次、章节路径。
9. 不得根据模型记忆伪造古籍原句。
10. 找不到依据时明确说“当前仓库未找到直接依据”。
```

---

# 17. ai/ 目录

第一阶段不要花大量 token 对全库逐书做长摘要。

只建立基础设施。

建议：

```text
ai/
├── README.md
├── concepts/
│   ├── 魂.md
│   ├── 魄.md
│   ├── 三魂七魄.md
│   ├── 鬼.md
│   ├── 神.md
│   ├── 妖.md
│   ├── 精.md
│   ├── 阴阳.md
│   ├── 五行.md
│   ├── 黄泉.md
│   ├── 地府.md
│   ├── 轮回.md
│   ├── 尸解.md
│   ├── 招魂.md
│   ├── 托梦.md
│   ├── 超度.md
│   ├── 镇煞.md
│   └── 丧葬.md
│
├── relations/
│   ├── 死亡体系.md
│   ├── 魂魄体系.md
│   ├── 鬼神体系.md
│   ├── 地府体系.md
│   ├── 轮回体系.md
│   ├── 道教神仙体系.md
│   ├── 驱邪镇煞体系.md
│   ├── 占卜体系.md
│   └── 风水体系.md
│
├── summaries/
└── writing/
```

第一阶段这些文件可以是索引型，而不是大段 AI 发挥。

例如：

```markdown
# 招魂

> 本文为 AI 辅助索引，不是古籍原文。

## 相关文献

- 《楚辞·招魂》
- 《搜神记》……
- 道藏……
- CBETA……

## 检索关键词

招魂、复魂、魂归、亡魂、魂魄……

## 原文位置

- `corpus/...`
```

没有可靠依据的内容不要填。

---

# 18. 写作专用入口

创建：

```text
ai/writing/WRITING_GUIDE.md
```

目标是支持小说创作。

规则：

当作者提出：

> 我要写一个死人不知道自己已经死了的副本。

AI 应：

```text
问题
↓
查 concepts
↓
查 indexes
↓
找到相关书目
↓
读取具体原文
↓
区分：
  古籍明确记载
  后世解释
  民间说法
  小说可改编部分
↓
提供创作素材
```

不能直接把现代网文设定冒充古代传统。

---

# 19. 导入脚本

所有导入必须可重复执行。

至少建立：

```text
tools/import/
├── import_yaya.py
├── import_kanripo.py
├── import_kr5.py
├── import_cbeta.py
├── import_xuanxue.py
└── import_all.py
```

以及：

```text
tools/index/
├── build_catalog.py
├── build_metadata_index.py
├── build_search_manifest.py
└── build_statistics.py
```

和：

```text
tools/validate/
├── validate_metadata.py
├── validate_links.py
├── validate_duplicates.py
├── validate_encoding.py
└── validate_corpus.py
```

脚本必须：

- 可重复执行
- 尽量幂等
- 有日志
- 出错不中途默默忽略
- 输出 failed items
- 支持单来源运行
- 不依赖 AI API 才能完成基础导入

---

# 20. 临时下载目录

上游仓库不要直接 clone 到最终 corpus 目录。

使用：

```text
.work/
.cache/
tmp/
```

并加入 `.gitignore`。

流程：

```text
clone upstream
↓
解析
↓
转换
↓
验证
↓
写入 corpus
↓
删除/忽略临时源码仓库
```

最终仓库不保留嵌套 `.git/`。

---

# 21. Git 仓库体积控制

本项目目标是 AI 可读。

所以：

## 不要

- 提交整个上游 `.git`
- 提交 node_modules
- 提交 Python venv
- 提交大型 ZIP
- 提交重复 PDF
- 提交重复 EPUB
- 提交扫描图片
- 为了“备份”保留三份同样文本
- 默认把全文塞进 Git LFS

Git LFS 会降低普通文本检索体验。

## 优先

保存：

- UTF-8 Markdown
- JSON/JSONL
- YAML
- TXT（必要时）
- provenance

如果源数据是巨大 XML：

- 原 XML 不需要完整镜像进仓库。
- 保留其来源、commit、原始路径。
- 提交转换后的 AI-readable 文本。
- 许可证要求保留的 notice 必须保留。

---

# 22. README.md

README 必须明确：

## 项目是什么

“中国阴阳、鬼神、志怪、道佛、术数文献 AI-ready 资料库”。

## 项目不是什么

- 不是迷信宣传项目
- 不是预测服务
- 不是现代算命平台
- 不是对古籍内容真实性的背书

仓库记录的是历史文献、传统文化、宗教和民间文本。

## 使用方式

推荐 AI：

```text
先读 CATALOG.md
↓
搜索 metadata/books.jsonl
↓
定位章节
↓
读取 corpus
```

---

# 23. 数据质量等级

每部文本增加质量状态：

```text
A = 来源清楚，结构完整，文本稳定
B = 来源清楚，存在轻微格式问题
C = OCR/转录文本，可能有错字
D = 来源或版本信息不足
E = 暂不可验证
```

记录到：

```json
"quality": {
  "grade": "A",
  "ocr": false,
  "known_issues": []
}
```

不要为了让库“看起来完整”而隐藏低质量问题。

---

# 24. 完整性检查

最终必须统计：

- 总书目数
- 总章节数
- 总字符数
- 各大类书目数
- 各子类书目数
- 各来源导入数量
- 缺失 metadata 数
- 编码异常数
- 空文件数
- 重复文本数
- 近重复文本数
- 许可证未确认数
- 转换失败数

写入：

```text
metadata/statistics.json
reports/COVERAGE_REPORT.md
reports/QUALITY_REPORT.md
```

---

# 25. 自动验证

至少实现以下检查：

```bash
python tools/validate/validate_encoding.py
python tools/validate/validate_metadata.py
python tools/validate/validate_corpus.py
python tools/validate/validate_duplicates.py
```

总入口：

```bash
python tools/validate_all.py
```

成功时必须明确输出：

```text
PASS
```

失败时返回非 0 exit code。

---

# 26. 可选 GitHub Actions

如果不会造成大量计算资源消耗，可添加：

```text
.github/workflows/validate.yml
```

仅做：

- metadata schema 验证
- UTF-8 验证
- 链接/路径一致性验证
- 索引是否需要重建检测

不要每次 push 都重新下载整个 CBETA / 道藏。

---

# 27. Git 提交策略

不要一个超大 commit 一把塞完。

推荐：

### Commit 1

```text
chore: initialize AI-ready corpus structure
```

包括：

- README
- AGENTS
- taxonomy
- source manifest
- tools skeleton

### Commit 2

```text
feat: import zhiguai corpus
```

### Commit 3

```text
feat: import Taoist canon corpus
```

### Commit 4

```text
feat: import CBETA Buddhist corpus
```

### Commit 5

```text
feat: import Chinese metaphysics corpus
```

### Commit 6

```text
feat: build metadata and search indexes
```

### Commit 7

```text
docs: add corpus reports and AI usage guide
```

如数据量太大，可继续按子分类拆 commit。

---

# 28. 不要做的事情

Codex 必须避免以下问题：

1. 不要只给我一个建议然后停止。
2. 不要只建立空目录。
3. 不要只写 importer 不执行。
4. 不要让 AI 重写古文。
5. 不要把 AI 摘要混进 corpus。
6. 不要擅自简繁转换。
7. 不要因为文件名相同就直接删除一个版本。
8. 不要因为书名相同就认定正文重复。
9. 不要用正则粗暴解析 CBETA XML。
10. 不要提交嵌套 `.git`。
11. 不要把所有上游仓库作为 submodule。
12. 不要下载几十 GB 图片/扫描件进入仓库。
13. 不要提交临时缓存。
14. 不要伪造作者、朝代、卷数。
15. 不确定的字段用 `null` 或 `unknown`。
16. 不要凭 AI 常识修改古籍原文。
17. 不要删除 provenance。
18. 不要把现代排盘代码当成古籍正文。
19. 不要为了目录整齐复制同一本书到多个分类。
20. 不要省略最终质量检查。

---

# 29. 执行顺序

必须按以下顺序推进。

## Phase 1 — 仓库初始化

- 检查当前仓库。
- 创建目录。
- 建立 taxonomy。
- 建立 metadata schema。
- 建立 source manifest。
- 建立 LICENSE 检查机制。
- 编写 AGENTS.md。

## Phase 2 — 来源审计

逐个检查：

- yaya
- Kanripo 搜神记
- Kanripo 太平广记
- kr5-corpus
- CBETA xml-p5
- xuanxue
- Kanripo 周易
- Kanripo 三命通会
- Kanripo 太乙金镜式经
- Kanripo 遁甲演义
- Kanripo 协纪辨方书

记录：

- commit
- license
- 数据格式
- 规模
- 目录规律

## Phase 3 — Importer

先写通用框架，再写各来源 importer。

不要一开始手工复制文件。

## Phase 4 — 志怪神异

导入、去重、验证。

## Phase 5 — 道藏

导入、分类、验证。

## Phase 6 — 佛藏

解析 CBETA、切卷/品、验证。

## Phase 7 — 阴阳术数

按 12 类逐项导入并补足。

## Phase 8 — 去重

全库去重与版本关系处理。

## Phase 9 — 索引

生成：

- CATALOG
- books.jsonl
- search-manifest
- author/title/category indexes
- statistics

## Phase 10 — AI 层

只建立可靠、引用型的概念入口。
不要无依据大规模生成内容。

## Phase 11 — 全库验证

执行全部校验。

## Phase 12 — 最终报告

生成 `reports/FINAL_REPORT.md`。

---

# 30. 最终验收标准

任务不能仅以“代码写完”作为完成。

满足以下条件才能视为完成：

- [ ] 四大主类均存在有效正文。
- [ ] 阴阳术数 12 个子类均有资料。
- [ ] 周易完整导入。
- [ ] 八字四柱核心典籍已覆盖。
- [ ] 紫微斗数核心典籍已覆盖。
- [ ] 六爻核心典籍已覆盖。
- [ ] 梅花易数已覆盖。
- [ ] 奇门核心典籍已覆盖。
- [ ] 大六壬核心典籍已覆盖。
- [ ] 太乙金镜式经已覆盖。
- [ ] 风水堪舆核心典籍已覆盖。
- [ ] 协纪辨方书已覆盖。
- [ ] 相术核心典籍已覆盖。
- [ ] 卜筮核心典籍已覆盖。
- [ ] 道藏完成主要语料导入。
- [ ] 佛藏完成合法可再分发部分的结构化导入。
- [ ] 志怪神异完成核心典籍导入。
- [ ] 所有书存在可追溯来源。
- [ ] 没有 AI 内容混入古籍原文。
- [ ] 没有嵌套 Git 仓库。
- [ ] 没有明显重复正文。
- [ ] 所有正文是有效 UTF-8。
- [ ] metadata schema 验证通过。
- [ ] CATALOG 可用。
- [ ] AGENTS.md 可指导 AI 检索。
- [ ] search-manifest 可被程序读取。
- [ ] LICENSE_REPORT 完成。
- [ ] QUALITY_REPORT 完成。
- [ ] FINAL_REPORT 完成。
- [ ] 所有 validation PASS。
- [ ] 所有改变已提交到 `F25731/yin-yang`。

---

# 31. 最终报告要求

`reports/FINAL_REPORT.md` 至少回答：

1. 最终导入多少部书？
2. 总字符数多少？
3. 每个分类多少部？
4. 每个来源导入多少？
5. 哪些来源因授权没有提交全文？
6. 哪些文本质量较低？
7. 哪些书存在多个版本？
8. 哪些数据转换失败？
9. 哪些类别仍然存在明显缺口？
10. 后续如何增量更新？
11. AI 应如何检索该仓库？
12. 有哪些已知问题？

---

# 32. 给 Codex 的工作方式

这是长任务。

不要一次性把所有古籍读进模型上下文。

正确工作方式：

```text
程序扫描
→ 建 manifest
→ 解析 metadata
→ 自动分类
→ 自动转换
→ 自动切分
→ hash / 相似度去重
→ 自动建索引
→ 只对异常项进行模型判断
```

优先用程序解决机械问题。

模型只处理：

- 无法程序判断的分类
- 模糊书名
- 版本关系
- 异常文本
- 少量概念索引

这样可以显著减少 token 消耗。

---

# 33. 面向小说写作的最终目标

本仓库最终要支持类似这样的任务：

> 查找中国传统文献中关于“亡者不知道自己已经死亡”的相关记载。

AI 应能够：

```text
读取 CATALOG
↓
检索 魂 / 鬼 / 亡者 / 还魂 / 冥界
↓
搜索 metadata + search manifest
↓
定位《搜神记》《太平广记》、道藏、佛藏相关章节
↓
读取少量真正相关的原文
↓
输出：
  1. 文献出处
  2. 原文依据
  3. 传统解释
  4. 不同体系差异
  5. 可用于小说的改编方向
```

而不是：

```text
一次读取整个道藏 + 整个佛藏
```

这就是本项目所有整理工作的最终标准。

---

# 34. 开始执行

首先：

1. 检查 `F25731/yin-yang` 当前状态。
2. 建立项目基础结构。
3. 读取所有上游仓库的 README / LICENSE / 目录。
4. 输出第一份 `reports/LICENSE_REPORT.md` 和 `sources/manifest.yaml`。
5. 写 import 框架。
6. 从“志怪神异”开始真正导入。
7. 一类完成并验证后再进入下一类。
8. 不要停留在规划阶段。
9. 一直推进到最终验收项完成。
