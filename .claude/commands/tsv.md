スプレッドシート貼り付け用TSVを発行します。

## 引数

`$ARGUMENTS` で指定（例: `/tsv 118 2026-07-02 05:05 86`）：
- 開始番号（「続きから」の場合は前回の最終番号+1）
- 日付・開始時刻・間隔（分）
- 除外投稿があれば「7を除く」のように

## 実行手順

1. 開始番号が「続きから」の場合、`postgen/generated/*_seq*.tsv` の最終番号を確認して+1
2. convert_tsv.pyで一発生成：
   `cd postgen && python convert_tsv.py generated/generated_posts_XXXX.txt --no-links --start-num N -d YYYY-MM-DD --start-hour H --start-minute M --interval I -o generated/generated_posts_XXXX_seqN.tsv`
   除外指定があれば `--exclude 7`（複数は `--exclude 2,5`）を付ける
3. `python tsv_preview.py generated/generated_posts_XXXX_seqN.tsv` で確認用HTMLを生成
4. `.tsv`（貼り付け用）と `.html`（確認用）を両方送付し、番号×日時の一覧表をチャットに書く
5. 配置が早朝5〜9時（無人時間帯）にかかる場合は一言注意を添える（指定どおり作りはする）
6. コミット・プッシュ

## 出力形式

- TSV：A列=投稿番号 / B列=本文（セル内改行は\r、`"` は `""` にエスケープ）/ C列=日付 / D列=時 / E列=分。リンク行なし
- チャット：番号×日付×時刻の表
