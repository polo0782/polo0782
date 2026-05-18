#!/usr/bin/env python3
"""STEP4: バズ投稿を分析してCLAUDE.mdを自動更新する（週1実行）"""

import os
import json
from pathlib import Path
from datetime import datetime
import anthropic

BASE_DIR = Path(__file__).parent.parent
CLAUDE_MD = BASE_DIR / "CLAUDE.md"
BUZZ_DATA = BASE_DIR / "data" / "buzz_posts.json"


def add_buzz_post(text: str, likes: int, reposts: int, replies: int):
    """バズ投稿を手動で追加する"""
    data = json.loads(BUZZ_DATA.read_text(encoding="utf-8"))
    data["buzz_posts"].append({
        "text": text,
        "likes": likes,
        "reposts": reposts,
        "replies": replies,
        "added_at": datetime.now().isoformat()
    })
    BUZZ_DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"追加完了（現在{len(data['buzz_posts'])}件）")


def analyze_and_update():
    """バズ投稿を分析してCLAUDE.mdのバズ共通点セクションを更新する"""
    data = json.loads(BUZZ_DATA.read_text(encoding="utf-8"))
    posts = data["buzz_posts"]

    if len(posts) < 3:
        print(f"投稿が少なすぎます（現在{len(posts)}件、最低3件必要）")
        return

    posts_text = "\n\n".join([
        f"いいね:{p['likes']} リポスト:{p['reposts']} リプ:{p['replies']}\n{p['text']}"
        for p in sorted(posts, key=lambda x: x["likes"], reverse=True)
    ])

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    analysis = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": f"""以下のバズ投稿を分析して、共通点・パターンを抽出してください。

{posts_text}

以下の形式で出力してください：

## バズ投稿の共通点（週次更新）
最終分析：{datetime.now().strftime('%Y-%m-%d')}

### 伸びるフックの特徴
- （箇条書き3〜5個）

### 伸びる構成パターン
- （箇条書き3〜5個）

### 伸びるCTA
- （箇条書き2〜3個）

### 次の投稿で意識すること
- （箇条書き3個）"""
        }]
    ).content[0].text

    _update_claude_md(analysis)
    data["last_analyzed"] = datetime.now().isoformat()
    BUZZ_DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("分析完了・CLAUDE.md更新済み")
    print(analysis)


def _update_claude_md(analysis: str):
    content = CLAUDE_MD.read_text(encoding="utf-8")
    marker = "## バズ投稿の共通点（週次更新）"

    if marker in content:
        before = content[:content.index(marker)]
        CLAUDE_MD.write_text(before + analysis + "\n", encoding="utf-8")
    else:
        CLAUDE_MD.write_text(content + "\n\n" + analysis + "\n", encoding="utf-8")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        print("バズ投稿を追加します")
        text = input("投稿本文（複数行はCtrl+Dで終了）：\n")
        likes = int(input("いいね数："))
        reposts = int(input("リポスト数："))
        replies = int(input("リプライ数："))
        add_buzz_post(text, likes, reposts, replies)
    else:
        analyze_and_update()
