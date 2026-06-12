複数日分のSNSポストをまとめて生成し、スプレッドシート用TSVに変換します。

## 引数
`$ARGUMENTS` で以下を指定できます：
- 日数（必須）: 生成するバッチ数（例: 10）
- 開始日（任意）: YYYY-MM-DD 形式（例: 2026-03-11）

例: `/batch 10 2026-03-11` → 2026-03-11から10日分を生成

---

## ⚠️ 絶対に守るルール

`/generate`（.claude/commands/generate.md）のルールをすべて適用する：

- **Task tool（サブエージェント）でポスト生成をしてはいけない**。全ポストをClaude自身が直接生成する
- 生成前に `postgen/skills/prompt.md`・`postgen/skills/knowledge.txt`・`postgen/skills/themes.txt`（禁止リスト含む）・ルート `CLAUDE.md` を読み込む
- 単ツイート200〜500字、ツリー1ツイートあたり200〜500字
- 1ファイル10本の中で同じ型を2回使わない。形式A 6〜7本 + 形式B 3〜4本
- 頻出ワードはthemes.txtのカテゴリ1・2から各投稿に2〜3個。カテゴリ6（スピ系）は1投稿1回まで
- themes.txt末尾の「伸びない投稿パターン（禁止リスト）」に該当する投稿を作らない
- note誘導・アフィリンク禁止。CTAは「フォロー保存」か「DM予約」
- 出力フォーマットは `[ポスト本文]` 〜 `==========`

---

## 実行手順

1. 上記ファイルを読み込む
2. `postgen/generated/` の既存ファイルの最大連番を確認する
3. **Claude自身が**指定日数分のバッチを連続生成し、`postgen/generated/generated_posts_XXXX.txt` に保存する（1ファイル10本）
4. 全ファイルをまとめて変換：
   `cd postgen && python convert_tsv.py generated/generated_posts_A.txt ...`
   （--clipboard と paste_to_sheet.py はローカルPCでのみ実行可能）

途中で確認を挟まず、ノンストップで完了まで進めてください。
