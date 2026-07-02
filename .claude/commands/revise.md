生成済みバッチへの修正指示（「3は〜にして」「6は差し替え」等）を反映します。

## ルール

- 修正後の文もルートCLAUDE.mdの口調・禁止ルールに完全準拠させる
- 修正時に再チェックする頻出違反：文末の「だ。」（んだ。なんだ。含む）／「——」ダッシュ／「彼女」呼び（→「この人」）／「これ、〇〇じゃない。」型の同一投稿内2回以上／治る・治療／擬人化／文字数
- 差し替え指示の場合、ルートCLAUDE.mdの「扱わないテーマ」に当たらない新ネタを選ぶ
- サブエージェント不使用

## 実行手順

1. 対象の `postgen/generated/generated_posts_XXXX.txt` をEditで修正
2. `posts/drafts/` の対応ファイルに `cp` で同期
3. TSV・HTMLを再生成：
   `cd postgen && python convert_tsv.py generated/generated_posts_XXXX.txt --no-links -o generated/generated_posts_XXXX.tsv && python tsv_preview.py generated/generated_posts_XXXX.tsv`
4. 発行済みの `_seqNNN.tsv` がある場合、同じ番号・日時設定で再生成して両方送付（番号と日時は変えない）
5. HTMLをユーザーに送付し、チャットに変更点を番号ごとに箇条書きで報告
6. コミット・プッシュ

## 出力形式

更新版HTML（＋必要ならseq付きTSV）＋変更点の箇条書き
