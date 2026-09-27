# 来源授权审计

审计日期：2026-09-27。状态按来源数字化数据判断，不将原作公版状态等同于数字化版本授权。

| 来源 | 状态 | 依据 | 处理 |
|---|---|---|---|
| Kanripo 37 个独立文本仓库 | ATTRIBUTION_REQUIRED | [Kanripo 组织授权说明](https://github.com/kanripo)（CC BY-SA 4.0）；各仓库无独立 LICENSE | 保留出处、commit、版本与改动说明后导入 |
| kr5-corpus | ATTRIBUTION_REQUIRED | [README](https://github.com/tokushige-koyasan/kr5-corpus)、LICENSE、NOTICE_KANRIPO.md：CC BY-SA 4.0 | 导入，保留双重署名和公告 |
| CBETA xml-p5 | NONCOMMERCIAL_OR_RESTRICTED | [CBETA 版权宣告](https://cbeta.org/copyright)：通用 CC BY-NC-SA 4.0，底本例外；T01 各 XML 的 `<availability>` 明示仅限非商业并要求保留原 header | 仅导入 T01 的 98 部；逐文件检查 `<availability>`，并在 `sources/provenance/cbeta/` 保存每部原始 `teiHeader`。其他部类待逐册审计 |
| yaya | UNCLEAR | [仓库](https://github.com/dreamsxin/yaya)无 LICENSE，README 未声明全文再分发权，且多为读书笔记 | 不提交正文 |
| xuanxue | UNCLEAR | [仓库](https://github.com/youngzs/xuanxue)无 LICENSE，README 无全文再分发声明 | 不提交正文 |
| 维基文库《梅花易數》《黃金策》 | ATTRIBUTION_REQUIRED | [维基文库版权信息](https://zh.wikisource.org/wiki/Wikisource:版權信息)说明贡献以 CC BY-SA 4.0 / GFDL 发布；作品页面标明旧作公版 | 按修订 ID 和 SHA1 锁定，保留署名与修订链接后导入 |

这些分类是本项目的审计结论，不构成对上游权利状态的法律判定。重新同步时须复核条款和文件头。未清楚授权的来源保留 manifest、目录调查与导入器，不作为公开正文提交。
