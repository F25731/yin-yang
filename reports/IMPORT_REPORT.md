# 导入报告

本轮使用锁定来源版本，先审计授权，再在 `.work/` 中获取上游，转换后仅提交可检索正文。

| 来源 | 原格式 | 导入 | 处理 |
|---|---|---:|---|
| Kanripo KR3l、KR3g、KR1a | mandoku 按卷文本 | 37 | 清除源格式指令，保留原字形与卷次 |
| kr5-corpus | UTF-8 文本 + catalog.csv | 1,650 | 按部类和书名建档，按长度切分 |
| CBETA 大正藏 T01–T55、T85 | TEI P5 XML | 2459 | XML parser 按卷转换，保留原 header 和注记；逐文件检查授权字段 |
| 维基文库 | revision-pinned wikitext | 5 | 按卷/章节转换，校验 SHA1 |
| yaya、xuanxue | Markdown/PDF 等 | 0 | 授权不明，仅登记候选路径 |

转换失败：0。`KR3l0122_ext.txt` 是非卷次的辅助元数据片段，未作为正文导入。
