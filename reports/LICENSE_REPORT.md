# 来源授权审计

审计日期：2026-09-27。状态按来源数字化数据判断，不将原作公版状态等同于数字化版本授权。

| 来源 | 状态 | 依据 | 处理 |
|---|---|---|---|
| Kanripo 七个指定仓库 | ATTRIBUTION_REQUIRED | [Kanripo 组织授权说明](https://github.com/kanripo)（CC BY-SA 4.0）；各仓库无独立 LICENSE | 保留出处、commit、版本与改动说明后导入 |
| kr5-corpus | ATTRIBUTION_REQUIRED | [README](https://github.com/tokushige-koyasan/kr5-corpus)、LICENSE、NOTICE_KANRIPO.md：CC BY-SA 4.0 | 导入，保留双重署名和公告 |
| CBETA xml-p5 | NONCOMMERCIAL_OR_RESTRICTED | [CBETA 版权宣告](https://cbeta.org/copyright)：通用 CC BY-NC-SA 4.0，底本例外；[项目 README](https://github.com/cbeta-org/xml-p5) 指向该条款 | 暂只登记来源；逐册筛查后方可选取可再分发文本 |
| yaya | UNCLEAR | [仓库](https://github.com/dreamsxin/yaya)无 LICENSE，README 未声明全文再分发权，且多为读书笔记 | 不提交正文 |
| xuanxue | UNCLEAR | [仓库](https://github.com/youngzs/xuanxue)无 LICENSE，README 无全文再分发声明 | 不提交正文 |

这些分类是本项目的审计结论，不构成对上游权利状态的法律判定。重新同步时须复核条款和文件头。未清楚授权的来源保留 manifest、目录调查与导入器，不作为公开正文提交。
