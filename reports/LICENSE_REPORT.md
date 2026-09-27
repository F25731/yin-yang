# 来源授权审计

审计日期：2026-09-28。状态按来源数字化数据判断，不将原作公版状态等同于数字化版本授权。

| 来源 | 状态 | 依据 | 处理 |
|---|---|---|---|
| Kanripo 37 个独立文本仓库 | ATTRIBUTION_REQUIRED | [Kanripo 组织授权说明](https://github.com/kanripo)（CC BY-SA 4.0）；各仓库无独立 LICENSE | 保留出处、commit、版本与改动说明后导入 |
| kr5-corpus | ATTRIBUTION_REQUIRED | [README](https://github.com/tokushige-koyasan/kr5-corpus)、LICENSE、NOTICE_KANRIPO.md：CC BY-SA 4.0 | 导入，保留双重署名和公告 |
| CBETA xml-p5 | NONCOMMERCIAL_OR_RESTRICTED | [CBETA 版权宣告](https://cbeta.org/copyright)：大正藏 T 冊屬 A 類，採 CC BY-NC-SA 4.0；每份 XML 的 `<availability>` 明示僅限非商業並要求保留原 header | 導入上游 T01–T55、T85 共 2,459 部；每文件檢查 `<availability>`，在 `sources/provenance/cbeta/` 保存原始 `teiHeader` 與注記。其他藏經系列仍待逐冊審計 |
| yaya | UNCLEAR | [仓库](https://github.com/dreamsxin/yaya)无 LICENSE，README 未声明全文再分发权，且多为读书笔记 | 不提交正文 |
| xuanxue | UNCLEAR | [仓库](https://github.com/youngzs/xuanxue)无 LICENSE，README 无全文再分发声明 | 不提交正文 |
| 维基文库《梅花易數》《黃金策》《閱微草堂筆記》《聊齋志異》《增刪卜易》《奇门宝鉴御定》 | ATTRIBUTION_REQUIRED | [维基文库版权信息](https://zh.wikisource.org/wiki/Wikisource:版權信息)说明贡献以 CC BY-SA 4.0 / GFDL 发布；[《奇门宝鉴御定》固定修订版](https://zh.wikisource.org/w/index.php?title=奇门宝鉴御定&oldid=2353651)页脚亦注明 CC BY-SA 4.0 | 按修订 ID 和 SHA1 锁定，保留署名与修订链接后导入；编者注与正文分开保存。《增刪卜易》转录校对程度低，《奇门宝鉴御定》作者与年代存疑，见质量报告 |

这些分类是本项目的审计结论，不构成对上游权利状态的法律判定。重新同步时须复核条款和文件头。未清楚授权的来源保留 manifest、目录调查与导入器，不作为公开正文提交。
