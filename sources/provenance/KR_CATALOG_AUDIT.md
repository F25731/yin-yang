# Kanripo 目录调查

官方目录仓库：<https://github.com/kanripo/KR-Catalog>，调查 commit `a9428c02c3ed92cf65a73fd051edb8e616c84dc3`。

- `KR/KR3g.txt` 提供术数原典的 Kanripo ID、书名、时代和作者字段。所选 KR3g0019–0039、0043–0046 逐仓导入，来源 commit 记录在 `sources/manifest.yaml`。
- `KR/KR3l.txt` 提供《山海經》《搜神後記》《夷堅志甲》《博物志》《述異記》的 ID，逐仓导入。
- 书目署名照录目录，不视为本项目独立校勘结论。作者未核实的志怪作品在 `metadata.json` 留空。

目录本身不作为正文来源；每部正文均指向独立上游仓库。
