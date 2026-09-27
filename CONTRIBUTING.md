# 贡献与同步

1. 在 `sources/manifest.yaml` 登记来源、授权依据、具体 commit。
2. 将上游检出到 `.work/<来源 ID>/`；该目录不会提交。也可运行 `python tools/import/import_all.py --source <source-id> --fetch` 获取 manifest 锁定版本。
3. 只在确认再分发条件后运行 `python tools/import/import_all.py --source <source-id>` 或对应导入器。不要修饰、翻译或擅自校改原文。
4. 运行 `python tools/index/build_all.py`、`python tools/index/build_ai_indexes.py`、`python tools/reports/build_final.py` 和 `python tools/validate_all.py`。
5. 提交转换后的 UTF-8 文本、元数据、来源说明及必要的授权公告。每个来源单独提交。

缺字、OCR 错误、版本疑问记录到 `metadata/quality/`，不要无依据修改正文。
