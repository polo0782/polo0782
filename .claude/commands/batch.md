複数日分のSNSポストをまとめて生成し、スプレッドシート用TSVに変換します。

## 引数

`$ARGUMENTS` で指定：
- 日数（必須）: 生成するバッチ数（例: 3）
- 開始日（任意）: YYYY-MM-DD 形式

例: `/batch 3 2026-07-05` → 2026-07-05から3日分（30本）

## ルール

**/generate（.claude/commands/generate.md）と完全に同一。** ルールの正はルートCLAUDE.md。ここにはコピーしない。
サブエージェントでの生成禁止も同様（全ポストをClaude自身が直接生成する）。

## 実行手順

1. /generateの手順1〜5を日数分くり返す（1ファイル10本、連番で保存、draftsにも同期）
2. 全ファイルをまとめて日内分散でTSV化：
   `cd postgen && python convert_tsv.py generated/generated_posts_A.txt generated/generated_posts_B.txt --per-day 10 -d YYYY-MM-DD --no-links -o generated/schedule_Ndays.tsv`
   （9〜23時に分散。早朝5〜9時の無人時間に置かない。昼12時・夜18〜23時を厚めに）
3. `python tsv_preview.py` でHTMLプレビューを生成し、TSVとともに送付
4. チャットに日別スケジュール表を書く
5. コミット・プッシュ

途中で確認を挟まず、ノンストップで完了まで進めてください。
