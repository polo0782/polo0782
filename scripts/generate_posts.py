#!/usr/bin/env python3
"""STEP3: テーマを渡すと投稿3本を生成する"""

import os
import sys
import json
from pathlib import Path
import anthropic

BASE_DIR = Path(__file__).parent.parent
CLAUDE_MD = BASE_DIR / "CLAUDE.md"
CONFIG = BASE_DIR / "config" / "account_design.json"
HISTORY = BASE_DIR / "data" / "posts_history.json"


def load_claude_md() -> str:
    return CLAUDE_MD.read_text(encoding="utf-8")


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def generate_posts(theme: str) -> list[str]:
    persona = load_claude_md()
    config = load_config()
    note_url = config["account"]["note_url"]

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = f"""以下のキャラクター設定・投稿ルールに従い、テーマ「{theme}」でThreads投稿を3本作成してください。

{persona}

【追加情報】
noteURL: {note_url}

【出力形式】
投稿1:
（本文のみ）

投稿2:
（本文のみ）

投稿3:
（本文のみ）

必ずフックの型を変えて3バリエーション作ること。説明・解説は不要。本文のみ出力。"""

    message = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text
    posts = _parse_posts(raw)
    _save_to_history(theme, posts)
    return posts


def _parse_posts(raw: str) -> list[str]:
    posts = []
    current = []
    for line in raw.split("\n"):
        if line.strip().startswith("投稿") and ":" in line:
            if current:
                posts.append("\n".join(current).strip())
            current = []
        else:
            current.append(line)
    if current:
        posts.append("\n".join(current).strip())
    return [p for p in posts if p]


def _save_to_history(theme: str, posts: list[str]):
    from datetime import datetime
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    history["posts"].append({
        "theme": theme,
        "generated_at": datetime.now().isoformat(),
        "posts": posts,
        "posted": [False, False, False]
    })
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    theme = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("今日のテーマ：")
    posts = generate_posts(theme)
    print("\n" + "="*40)
    for i, post in enumerate(posts, 1):
        print(f"\n【投稿{i}】\n{post}")
        print("-"*40)
