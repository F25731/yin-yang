# 阴阳资料总库

中国阴阳、鬼神、志怪、道佛与术数文献的 AI 可检索资料库。正文在 `corpus/`，书目在 `metadata/`，检索入口在 `CATALOG.md` 与 `indexes/`。本库记录历史文献，不提供预测服务，也不对文献中的说法作真实性背书。

## 检索

先读 [CATALOG.md](CATALOG.md)，再搜索 `metadata/books.jsonl` 或 `indexes/search-manifest.jsonl`，最后只读取命中的章节。引用时注明书名、卷次、章节路径和来源版本。`ai/` 是辅助索引，不能当作原文。

## 数据与授权

各来源的授权不同。使用和再分发正文前，请读 [LICENSES.md](LICENSES.md) 及 [授权审计](reports/LICENSE_REPORT.md)。有些来源仅收录书目，不提交正文。

## 更新

导入器从 `.work/` 中的上游检出目录读取，见 [贡献说明](CONTRIBUTING.md)。运行 `python tools/validate_all.py` 检查文本与索引。
