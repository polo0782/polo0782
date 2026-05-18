#!/usr/bin/env python3
"""STEP5: Threads APIで朝7時・昼12時・夜21時に自動投稿するスケジューラー"""

import os
import json
import time
import logging
import requests
import schedule
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from generate_posts import generate_posts

BASE_DIR = Path(__file__).parent.parent
CONFIG = BASE_DIR / "config" / "account_design.json"
HISTORY = BASE_DIR / "data" / "posts_history.json"

THREADS_API_BASE = "https://graph.threads.net/v1.0"
JST = ZoneInfo("Asia/Tokyo")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "data" / "scheduler.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


def get_next_unposted_post() -> tuple[str, int, int] | None:
    """未投稿の投稿を1件取得する (text, batch_index, post_index)"""
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    for bi, batch in enumerate(history["posts"]):
        for pi, posted in enumerate(batch["posted"]):
            if not posted:
                return batch["posts"][pi], bi, pi
    return None


def mark_as_posted(batch_index: int, post_index: int):
    history = json.loads(HISTORY.read_text(encoding="utf-8"))
    history["posts"][batch_index]["posted"][post_index] = True
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")


def post_to_threads(text: str) -> bool:
    """Threads APIで投稿する"""
    access_token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = os.environ.get("THREADS_USER_ID")

    if not access_token or not user_id:
        log.error("THREADS_ACCESS_TOKEN または THREADS_USER_ID が設定されていません")
        return False

    # Step1: メディアコンテナ作成
    create_url = f"{THREADS_API_BASE}/{user_id}/threads"
    resp = requests.post(create_url, params={
        "media_type": "TEXT",
        "text": text,
        "access_token": access_token
    })

    if resp.status_code != 200:
        log.error(f"コンテナ作成失敗: {resp.status_code} {resp.text}")
        return False

    container_id = resp.json().get("id")
    log.info(f"コンテナ作成成功: {container_id}")

    # Threads APIの推奨待機時間
    time.sleep(5)

    # Step2: 公開
    publish_url = f"{THREADS_API_BASE}/{user_id}/threads_publish"
    resp = requests.post(publish_url, params={
        "creation_id": container_id,
        "access_token": access_token
    })

    if resp.status_code != 200:
        log.error(f"公開失敗: {resp.status_code} {resp.text}")
        return False

    post_id = resp.json().get("id")
    log.info(f"投稿成功: {post_id}")
    return True


def auto_post_job():
    """スケジューラーから呼ばれる投稿ジョブ"""
    now = datetime.now(JST).strftime("%Y-%m-%d %H:%M")
    log.info(f"投稿ジョブ開始: {now}")

    result = get_next_unposted_post()

    if result is None:
        # 未投稿ストックがなければ自動生成
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        themes = config["themes_bank"]
        # 直近に使ったテーマを避けて選ぶ
        import random
        theme = random.choice(themes)
        log.info(f"新規生成: テーマ「{theme}」")
        generate_posts(theme)
        result = get_next_unposted_post()

    if result is None:
        log.error("投稿ストックの取得に失敗しました")
        return

    text, bi, pi = result
    log.info(f"投稿内容:\n{text}")

    if post_to_threads(text):
        mark_as_posted(bi, pi)
        log.info("投稿完了・履歴更新")
    else:
        log.error("投稿に失敗しました")


def start_scheduler():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    times = config["posting_schedule"]["times"]

    for t in times:
        schedule.every().day.at(t, "Asia/Tokyo").do(auto_post_job)
        log.info(f"スケジュール登録: 毎日 {t} JST")

    log.info("スケジューラー起動完了")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        log.info("テスト投稿実行")
        auto_post_job()
    else:
        start_scheduler()
