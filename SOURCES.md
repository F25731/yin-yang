# 来源

机器可读来源表：`sources/manifest.yaml`。逐书 provenance 见各书 `metadata.json` 与 `sources/provenance/`。

导入的数据是来源版本的结构化清洗版，不是校勘定本。数字化版本的授权与古籍原作的公版状态应分别判断。

`sources/provenance/KR_CATALOG_AUDIT.md` 记录 Kanripo 官方目录调查。`sources/provenance/yaya-inventory.json` 和 `xuanxue-inventory.json` 记录未获明确全文再分发授权的候选路径。

佛藏分类以 [CBETA 电子佛典部类目录](https://www.cbeta-org-tw.cbeta.org/data/cbeta/cbeta_toc.htm) 为参照。T09、T12、T47 按经号细分；其他跨部类卷册暂按卷号归档，具体经号与原始 XML 均见逐书元数据。

《閱微草堂筆記》取自维基文库 24 卷页面，每卷修订 ID 与 SHA1 锁定在 manifest；维基文库编者注另存 `sources/provenance/yuewei-notes.jsonl`。

《聊齋志異》取自维基文库 12 卷页面，按 493 个篇目标题切分，逐卷修订 ID 与 SHA1 锁定在 manifest。现代释词和异文记录另存 `sources/provenance/liaozhai-editorial-notes.jsonl`；本版篇目数与常见 496 篇说法仍需版本比对。

《增刪卜易》取自维基文库卷一分章页、八卦图子页及主页面卷二至四；排除了主页面的现代录入者前言。上游标注主页面 25%、分章页 50% 的校对程度，本库列为 D 级转录。
