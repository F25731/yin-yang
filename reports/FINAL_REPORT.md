# 建设报告

本报告由当前 corpus/metadata 自动生成，不再使用第一轮硬编码数字。

## 当前规模

- 独立书目：**6682 部**
- AI 检索单元：**26135 个**
- 正文字符：**325570230**
- 主类：志怪神异 9、道藏 1650、佛藏 4917、阴阳术数 106、现代民间灵异 1
- 阴阳术数 12 类：周易 3、八字四柱 22、紫微斗数 8、六爻 10、梅花易数 3、奇门遁甲 7、大六壬 10、太乙神数 1、风水堪舆 25、择日 1、相术 12、卜筮 16

## 来源规模

- cbeta-xml-p5：4917 部
- kanripo-KR1a0001：1 部
- kanripo-KR3g0019：1 部
- kanripo-KR3g0020：1 部
- kanripo-KR3g0021：1 部
- kanripo-KR3g0022：1 部
- kanripo-KR3g0023：1 部
- kanripo-KR3g0024：1 部
- kanripo-KR3g0025：1 部
- kanripo-KR3g0026：1 部
- kanripo-KR3g0027：1 部
- kanripo-KR3g0028：1 部
- kanripo-KR3g0029：1 部
- kanripo-KR3g0030：1 部
- kanripo-KR3g0031：1 部
- kanripo-KR3g0032：1 部
- kanripo-KR3g0033：1 部
- kanripo-KR3g0034：1 部
- kanripo-KR3g0035：1 部
- kanripo-KR3g0036：1 部
- kanripo-KR3g0037：1 部
- kanripo-KR3g0038：1 部
- kanripo-KR3g0039：1 部
- kanripo-KR3g0042：1 部
- kanripo-KR3g0043：1 部
- kanripo-KR3g0044：1 部
- kanripo-KR3g0045：1 部
- kanripo-KR3g0046：1 部
- kanripo-KR3g0047：1 部
- kanripo-KR3g0048：1 部
- kanripo-KR3g0051：1 部
- kanripo-KR3l0090：1 部
- kanripo-KR3l0099：1 部
- kanripo-KR3l0100：1 部
- kanripo-KR3l0118：1 部
- kanripo-KR3l0122：1 部
- kanripo-KR3l0123：1 部
- kanripo-KR3l0124：1 部
- kr5-corpus：1650 部
- supernatural-tianya：1 部
- wikisource-huangjince：1 部
- wikisource-liaozhai：1 部
- wikisource-meihua：1 部
- wikisource-qimenbaojian：1 部
- wikisource-yuewei：1 部
- wikisource-zengshan：1 部
- xuanxue：71 部

## CBETA 系列覆盖

- A：12 部
- B：204 部
- C：12 部
- CC：6 部
- D：64 部
- F：27 部
- G：69 部
- GA：58 部
- GB：2 部
- I：1 部
- J：287 部
- K：10 部
- L：26 部
- LC：8 部
- M：1 部
- N：83 部
- P：20 部
- S：2 部
- T：2459 部
- TX：40 部
- U：3 部
- X：1236 部
- Y：44 部
- YP：40 部
- ZS：1 部
- ZW：202 部

## 数据质量

- 质量等级：B 4954、C 5、D 1723
- metadata 缺失：0
- 编码异常：0
- 空正文：0
- 精确重复组：5
- 近重复候选：9
- 同题名版本组：151

## 核心覆盖验收

**PASS：四大古籍体系与阴阳术数 12 子类核心书目验收通过。**

## 失败 / 暂缓项目

- CBETA_EXTRA_WITHHELD.txt：100 条

## AI 使用方式

1. 先读根目录 CATALOG.md，它只保留小型分类入口。
2. 再进入 indexes/catalog/ 对应分类；按主题可查 indexes/by-topic.md。
3. 小说写作优先看 ai/writing/TOPIC_INDEX.md，随后打开词项中的真实原文章节。
4. 精确搜索使用 metadata/books.jsonl 与 indexes/search-manifest.jsonl。
5. corpus/ 为来源文本整理层，ai/ 只做导航，不得冒充古籍原文。

## 已知边界

- 同题名不同版本默认并存，不自动认定某一版为唯一正确文本。
- D/C 级文本应在正式引用前回查上游或影印底本。
- 现代民间灵异材料只作叙事/民俗线索，不作为事实证据。
- ghost 约 70GB 音频不镜像，只建立节目标题索引；AI 资料库优先保存可检索文本。
