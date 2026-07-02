# SNSポスト生成・TSV変換システム

Claude CodeでThreads投稿を生成し、スプレッドシート貼り付け用TSVに変換するシステム。

## ルールの正（Single Source of Truth）

生成に関わるルールはここにコピーしない。以下を参照する：

| 内容 | 場所 |
|---|---|
| ペルソナ・口調・禁止ワード・CTA・文字数・フックの型 | **ルート `CLAUDE.md`**（唯一の正） |
| 読点・改行・助詞の細部 | `docs/日本語ルール抜粋.md` |
| 伸びない投稿パターン（禁止リスト）＋頻出ワード | `knowledge/禁止リスト_頻出ワード.md` |
| ネタ元（エピソード・見立て軸・バズ分析・参考アカウント） | `knowledge/`（episodes / insights / buzz / themes） |
| 本人アカウントのテーマ120選・語彙参考 | `skills/themes.txt` |

## 基本ルール

- ポスト生成はClaude自身が行う。**Task tool（サブエージェント）でのポスト生成は禁止**（ルール未伝達で低品質になる。/batchでも同様）
- 生成ポストは `generated/` に保存し、`posts/drafts/` に同期する。貼り付け済みは `generated/posted/` に移動する
- `paste_to_sheet.py`（Seleniumシート貼り付け）と `--clipboard` は**ローカルPC専用**。リモート環境ではTSVファイルの送付までを行う

## コマンド（.claude/commands/）

| コマンド | 用途 |
|---|---|
| `/generate` | 1バッチ10本生成 → drafts同期 → TSV/HTMLプレビュー |
| `/batch N` | N日分まとめて生成 → 日内分散TSV |
| `/revise` | 番号指定の修正を反映 → 再生成・再送付 |
| `/tsv` | 番号・日時・間隔指定で貼り付け用TSV発行 |
| `/log-episode` | 施術メモを `knowledge/episodes/` に登録 |

## convert_tsv.py の主なオプション

```
python convert_tsv.py generated/generated_posts_XXXX.txt [オプション]
```

- `-d YYYY-MM-DD` / `--start-hour H` / `--start-minute M` / `--interval 分`：開始日時と間隔（分・間隔を指定すると間隔モードになる）
- `--start-num N`：A列の開始番号（前バッチの続き番号に使う）
- `--exclude 7`／`--exclude 2,5`：指定番号の投稿を除外（1始まり）
- `--no-links`：リンク行なし ／ `--no-random`：分のランダム無効
- `--per-day 10 --day-start 9 --day-end 23`：日内分散モード（複数日バッチ用）
- `-o ファイル`：出力先

確認用HTML：`python tsv_preview.py generated/xxx.tsv`（同名.htmlを生成）

例（前回117の続き・7/2の5:05から86分おき・7番除外）：
```
python convert_tsv.py generated/generated_posts_0017.txt --no-links \
  --start-num 118 -d 2026-07-02 --start-hour 5 --start-minute 5 --interval 86 --exclude 7 \
  -o generated/generated_posts_0017_seq118.tsv
```

## ポスト抽出ルール

### フォーマット1（推奨）
```
[ポスト本文]
（ポスト内容）
==========
```
`[ポスト本文]` と `==========` の間のテキストを抽出。

### ツリーポストの分割
`■Nツイート目` で始まる行がある場合、各ツイートを個別行として扱う。
同じツリー内のツイートは同じA列番号を共有する。

## ファイル構成

```
postgen/
├── CLAUDE.md              ← このファイル
├── config.json            ← 設定（スケジュール既定値。実運用は都度オプションで上書き）
├── convert_tsv.py         ← TSV変換スクリプト
├── tsv_preview.py         ← TSV→スプレッドシート風HTMLプレビュー
├── paste_to_sheet.py      ← Seleniumシート貼り付け（ローカルPC専用）
├── links.json             ← 宣伝リンクパターン（現在リンクは不使用）
├── skills/
│   └── themes.txt         ← 本人アカウント分析（テーマ120選・語彙参考）
├── generated/             ← 生成ポスト・TSV・HTML保存先
│   └── posted/            ← 貼り付け済み
└── manual/manual.pdf      ← 元システムのマニュアル
```

※ 旧 `skills/prompt.md`・`skills/knowledge.txt`（型01〜21）・`skills/themes_*.txt` は2026-07-02の再設計で削除（経緯は `docs/2026-07-02_Skill監査と再設計.md`。日本語ルールは `docs/日本語ルール抜粋.md` に、禁止リストは `knowledge/禁止リスト_頻出ワード.md` に移設。参考アカウント分析は `knowledge/themes/` が正）
