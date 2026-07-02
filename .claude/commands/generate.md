SNSポスト（Threads）を10本生成し、drafts保存・TSV/HTMLプレビューまで行います。

## ルールの正（Single Source of Truth）

生成ルール・口調・禁止ワード・CTA・文字数・型は **ルートCLAUDE.mdだけ** に書かれている。必ず読み、完全に従うこと。
このファイルにはルールをコピーしない（コピーは陳腐化して品質ブレの原因になる）。

必読ファイル：
1. ルート `CLAUDE.md` … キャラ設定・口調・禁止・CTA・文字数・フックの型（唯一の正）
2. `docs/日本語ルール抜粋.md` … 読点・改行・助詞の細部
3. `knowledge/禁止リスト_頻出ワード.md` … 伸びない投稿パターン＋頻出ワード
4. `knowledge/episodes/`（`使用済み: no` を優先）・`knowledge/insights/`・`knowledge/buzz/` … ネタ元

## 絶対禁止

- **Task tool（サブエージェント）でのポスト生成**（ルール未伝達で低品質になる。全ポストをClaude自身が直接生成する）

## 実行手順

1. 上記の必読ファイルを読む
2. ネタを選び、10本の型を割り当てる（1本目は施術エピソード型。同じ型は1バッチで2回まで使わない。型はルートCLAUDE.md「フックの型」参照）
3. 生成する。150〜250字が主役（6〜7本）＋長め深掘り2〜3本（上限500字）
4. `postgen/generated/generated_posts_XXXX.txt` に保存（XXXXは既存最大連番+1）
5. `posts/drafts/YYYY-MM-DD_テーマ.md` にコピー。使ったエピソードは `使用済み: yes` に更新
6. TSVとHTMLプレビューを生成：
   `cd postgen && python convert_tsv.py generated/generated_posts_XXXX.txt --no-links -o generated/generated_posts_XXXX.tsv && python tsv_preview.py generated/generated_posts_XXXX.tsv`
7. HTMLをユーザーに送付し、チャットに10本の内訳（型・テーマ・狙い）を書く
8. コミット・プッシュ

## 出力フォーマット

```
[ポスト本文]
（本文）
==========
```
ツリーの場合は `■1ツイート目` `■2ツイート目` で区切る。

※ `paste_to_sheet.py`（Seleniumシート貼り付け）と `--clipboard` はローカルPC専用。この環境では実行しない。

## 引数

- `$ARGUMENTS` に日付が指定されている場合、TSVの `--start-date` に使う。なければ今日の日付

途中で確認を挟まず、ノンストップで完了まで進めてください。
