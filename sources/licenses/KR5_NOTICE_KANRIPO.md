# NOTICE — Kanseki Repository 底本に関する表示

本リポジトリのテキストデータは、Kanseki Repository（漢籍リポジトリ、Kanripo）が公開するデータを底本とする再加工物である。CC BY-SA 4.0の条件（帰属表示・改変明示・同一ライセンス継承）に基づき、以下の通り出典と加工内容を表示する。

## 1. 底本の出典と版本情報

| 項目 | 内容 |
|---|---|
| 底本 | Kanseki Repository（1文献1リポジトリ構成） |
| 配布元 | https://github.com/kanripo |
| 採用ブランチ | master（3件のみZTDZ。全件のブランチ名と取得時コミットSHAは catalog.csv の witness・commit 列に記録） |
| 取得日 | 2026-08-02 |
| 収録範囲 | KR5道部のうちKR5a–h（正統道藏＋續道藏）1,541件＋KR5i（清代道教文獻）109件、計1,650件 |

masterブランチの実体は、KR5a–hでは正統道藏（三家本、1988年、涵芬楼系頁付け）、KR5iでは重刊道藏輯要（CK-KZ）を底本とするKanripoの基礎テキストである（各文献冒頭のプロパティによる）。一部文献は四庫全書文淵閣本（WYG）等を底本とする（catalog.csv の baseedition 列参照）。

## 2. 底本のライセンス

Kanseki Repositoryは、そのコンテンツを **CC BY-SA 4.0**（Creative Commons 表示–継承 4.0 国際）で公開している。典拠は以下の通り（2026-08-02確認）。

- GitHub組織プロフィール（https://github.com/kanripo ）:「Comprehensive collection of premodern Chinese texts. Licensed as CC BY SA 4.0.」
- 公式サイト（https://www.kanripo.org ）フッターのライセンス表示

なお、収録テキストの原典（正統道藏・續道藏等）は著作権保護期間を満了した公有文献であり、CC BY-SA 4.0が及ぶのはKanripoによる翻刻・校正・構造化等の作成部分である。

## 3. 本リポジトリでの加工内容

- mandoku形式のメタデータ行・画像リンク・版心行の除去（プレーンテキスト化）
- 頁マーカー `<pb:...>` の【　】形式への変換・保持
- 原本行末記号「¶」の除去と物理行の連結
- 巻ファイルの作品単位への統合、書誌情報の catalog.csv への集約
- 本文の文字そのものには改変を加えていない

## 4. 本リポジトリのライセンス

底本の条件を継承し、CC BY-SA 4.0 で公開する。ライセンス全文は同梱の `LICENSE` を参照。

- ライセンス正文: https://creativecommons.org/licenses/by-sa/4.0/legalcode
- Kanseki Repository: https://github.com/kanripo ／ https://www.kanripo.org
