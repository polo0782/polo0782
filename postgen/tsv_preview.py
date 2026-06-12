"""TSVをスプレッドシート風のHTMLプレビューに変換するスクリプト

使い方: python tsv_preview.py generated/generated_posts_0001.tsv
出力:   同名の .html ファイル（ブラウザで開くと表形式で確認できる）
"""
import html
import sys
from pathlib import Path

HEADERS = ['A（連番）', 'B（本文）', 'C（日付）', 'D（時）', 'E（分）']

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ font-family: "Hiragino Sans", "Yu Gothic", Meiryo, sans-serif; margin: 0; background: #f8f9fa; }}
  h1 {{ font-size: 16px; padding: 12px 16px; margin: 0; background: #fff; border-bottom: 1px solid #ddd; }}
  table {{ border-collapse: collapse; width: 100%; background: #fff; }}
  th {{ background: #f1f3f4; font-size: 12px; font-weight: normal; color: #555;
       border: 1px solid #d0d0d0; padding: 6px 10px; position: sticky; top: 0; }}
  td {{ border: 1px solid #d0d0d0; padding: 8px 10px; vertical-align: top; font-size: 13px; }}
  td.num {{ text-align: center; color: #666; white-space: nowrap; }}
  td.body {{ max-width: 480px; line-height: 1.7; }}
  tr:nth-child(even) td {{ background: #fafbfc; }}
  .rowhead {{ background: #f1f3f4; text-align: center; color: #888; font-size: 12px; width: 36px; }}
</style>
</head>
<body>
<h1>{title}（{count}行）</h1>
<table>
<tr><th></th>{header_cells}</tr>
{rows}
</table>
</body>
</html>
"""


def main():
    src = Path(sys.argv[1])
    rows_html = []
    # \r はセル内改行なので行区切りにしない（splitlines禁止）
    with open(src, encoding='utf-8', newline='') as f:
        lines = [l for l in f.read().split('\n') if l.strip()]
    for i, line in enumerate(lines, 1):
        cols = line.split('\t')
        # B列: 先頭末尾の引用符を外し、\r を改行表示に戻す
        body = cols[1].strip('"').replace('""', '"')
        body_html = html.escape(body).replace('\r', '<br>')
        cells = [
            f'<td class="rowhead">{i}</td>',
            f'<td class="num">{html.escape(cols[0])}</td>',
            f'<td class="body">{body_html}</td>',
            f'<td class="num">{html.escape(cols[2])}</td>',
            f'<td class="num">{html.escape(cols[3])}</td>',
            f'<td class="num">{html.escape(cols[4])}</td>',
        ]
        rows_html.append('<tr>' + ''.join(cells) + '</tr>')

    out = src.with_suffix('.html')
    out.write_text(TEMPLATE.format(
        title=src.stem,
        count=len(lines),
        header_cells=''.join(f'<th>{h}</th>' for h in HEADERS),
        rows='\n'.join(rows_html),
    ), encoding='utf-8')
    print(f'{out} に出力しました')


if __name__ == '__main__':
    main()
