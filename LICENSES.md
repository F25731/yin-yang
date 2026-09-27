# 资料授权

仓库不对所有内容施加统一许可证。每部书以其 `metadata.json` 的 `license` 字段和上游条款为准。

- Kanripo 文本：遵守 Kanseki Repository 标明的 CC BY-SA 条件，注明 Kanripo、原仓库、commit 与整理变更。具体版本见 `sources/manifest.yaml`。
- `kr5-corpus`：CC BY-SA 4.0，注明 Kanripo 与 `tokushige-koyasan/kr5-corpus`，保留其授权公告。
- CBETA：大正藏 T 部按其版权宣告属 CC BY-NC-SA 4.0，须非商业使用、署名及相同方式共享，并保留原始 TEI header。本库导入上游 `xml-p5` 的 T01–T55、T85 共 2,459 部，逐文件检查授权字段；原 header 和注记保存在 `sources/provenance/cbeta/`。其他藏经系列尚未完成逐册授权筛查。
- `yaya`、`xuanxue`：未见覆盖全部文本的明确再分发许可，现阶段仅登记书目与来源。
- 维基文库《梅花易數》：旧作正文标为公版，维基文库贡献遵守 CC BY-SA 4.0 / GFDL；本库记录四页修订 ID 和 SHA1，须注明维基文库及修订链接。

完整核查与依据见 [LICENSE_REPORT.md](reports/LICENSE_REPORT.md)。
