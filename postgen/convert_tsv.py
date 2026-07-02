"""生成ポストファイルをTSV形式に変換するスクリプト"""
import json
import random
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta


def parse_posts(text: str) -> list[dict]:
    """[ポスト本文]...==========形式からポストを抽出"""
    posts = []
    blocks = re.split(r'={5,}|─{5,}', text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if block.startswith('[ポスト本文]'):
            block = block[len('[ポスト本文]'):].strip()
        if not block:
            continue

        # ■Nツイート目 でツリー判定
        thread_parts = re.split(r'■\d+ツイート目\s*', block)
        # thread_parts[0] はヘッダー前のテキスト（通常空）
        tweets = [p.strip() for p in thread_parts if p.strip()]

        if len(tweets) > 1:
            posts.append({"is_thread": True, "tweets": tweets})
        else:
            posts.append({"is_thread": False, "tweets": [block]})
    return posts


def day_slot_times(start_date, per_day, day_start, day_end, n):
    """1日 per_day 本を day_start〜day_end 時に均等配置した時刻リストを返す"""
    times = []
    day = 0
    while len(times) < n:
        base = start_date + timedelta(days=day)
        if per_day <= 1:
            times.append(base.replace(hour=day_start, minute=0))
        else:
            span = (day_end - day_start) * 60
            step = span / (per_day - 1)
            for i in range(per_day):
                times.append(base.replace(hour=day_start, minute=0)
                             + timedelta(minutes=int(round(step * i))))
        day += 1
    return times[:n]


def build_tsv(posts, config, links, start_num=1):
    """ポストリストからTSV行を構築"""
    sch = config['schedule']
    start_date = datetime.strptime(sch['start_date'], '%Y-%m-%d')

    # 日内分散モード（posts_per_day 指定時）
    per_day = sch.get('posts_per_day', 0)
    if per_day and per_day > 0:
        day_start = sch.get('day_start_hour', 9)
        day_end = sch.get('day_end_hour', 23)
        slots = day_slot_times(start_date, per_day, day_start, day_end, len(posts))
        lines = []
        for idx, post in enumerate(posts):
            t = slots[idx]
            d, h, m = t.strftime('%Y/%m/%d'), f"{t.hour}", f"{t.minute}"
            for tweet in post['tweets']:
                cell = tweet.strip().replace('\n', '\r').replace('"', '""')
                lines.append(f'{idx + start_num}\t"{cell}"\t{d}\t{h}\t{m}')
        return '\n'.join(lines)

    start_hour = sch['start_hour']
    interval = sch['interval']
    random_min = sch.get('random_minutes', True)
    links_enabled = sch.get('links_enabled', True)
    links_per_day = sch.get('links_per_day', 3) if links_enabled else 0
    delay_min = sch.get('link_delay_min', 30)
    delay_max = sch.get('link_delay_max', 60)

    minute = random.randint(0, 59) if random_min else sch.get('start_minute', 0)
    current_time = start_date.replace(hour=start_hour, minute=minute)
    current_day = current_time.date()
    links_today = 0
    group_num = start_num
    lines = []

    for post in posts:
        if current_time.date() != current_day:
            current_day = current_time.date()
            links_today = 0

        d = current_time.strftime('%Y/%m/%d')
        h = f"{current_time.hour}"
        m = f"{current_time.minute}"

        for tweet in post['tweets']:
            # \n → \r に変換（Google Sheetsでセル内改行として扱われる）
            cell_text = tweet.strip().replace('\n', '\r')
            escaped = cell_text.replace('"', '""')
            lines.append(f'{group_num}\t"{escaped}"\t{d}\t{h}\t{m}')

        # リンク行
        if links_today < links_per_day and links:
            link = random.choice(links)
            link_delay = random.randint(delay_min, delay_max)
            lt = current_time + timedelta(minutes=link_delay)
            link_text = f'{link["text"]}\r{link["url"]}'
            escaped_link = link_text.replace('"', '""')
            lines.append(
                f'{group_num}\t"{escaped_link}"\t'
                f'{lt.strftime("%Y/%m/%d")}\t{lt.hour}\t{lt.minute}'
            )
            links_today += 1

        group_num += 1
        current_time += timedelta(minutes=interval)
        if random_min:
            current_time = current_time.replace(minute=random.randint(0, 59))

    return '\n'.join(lines)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description='生成ポスト→TSV変換')
    parser.add_argument('files', nargs='+', help='generated_posts_XXXX.txt')
    parser.add_argument('-d', '--start-date', help='開始日 (YYYY-MM-DD)')
    parser.add_argument('--start-hour', type=int, help='開始時 (0-23)')
    parser.add_argument('--start-minute', type=int, help='開始分 (0-59)。指定で分ランダム無効＋間隔モード')
    parser.add_argument('--interval', type=int, help='投稿間隔（分）。指定で日内分散モードを無効化')
    parser.add_argument('--start-num', type=int, help='A列の開始番号（デフォルト1。前バッチの続き番号に使う）')
    parser.add_argument('--no-random', action='store_true', help='分のランダムを無効化')
    parser.add_argument('--exclude', help='除外する投稿番号（1始まり・カンマ区切り。例: 7 / 2,5）')
    parser.add_argument('--per-day', type=int, help='1日あたりの投稿数（指定で日内分散モード）')
    parser.add_argument('--day-start', type=int, help='1日の投稿開始時 (時)')
    parser.add_argument('--day-end', type=int, help='1日の投稿終了時 (時)')
    parser.add_argument('-c', '--clipboard', action='store_true', help='クリップボードにコピー')
    parser.add_argument('-o', '--output', help='出力ファイルパス')
    parser.add_argument('--links', action='store_true', default=None, help='リンク挿入を強制ON')
    parser.add_argument('--no-links', action='store_true', help='リンク挿入を強制OFF')
    args = parser.parse_args()

    base = Path(__file__).parent
    with open(base / 'config.json', encoding='utf-8') as f:
        config = json.load(f)
    with open(base / 'links.json', encoding='utf-8') as f:
        links = json.load(f)

    if args.start_date:
        config['schedule']['start_date'] = args.start_date
    if args.start_hour is not None:
        config['schedule']['start_hour'] = args.start_hour
    if args.start_minute is not None:
        config['schedule']['start_minute'] = args.start_minute
        config['schedule']['random_minutes'] = False
    if args.interval is not None:
        config['schedule']['interval'] = args.interval
    if args.no_random:
        config['schedule']['random_minutes'] = False
    # 間隔・開始分の明示指定は間隔モードを意味する（--per-day 明示があればそちらを優先）
    if (args.interval is not None or args.start_minute is not None) and args.per_day is None:
        config['schedule']['posts_per_day'] = 0
    if args.per_day is not None:
        config['schedule']['posts_per_day'] = args.per_day
    if args.day_start is not None:
        config['schedule']['day_start_hour'] = args.day_start
    if args.day_end is not None:
        config['schedule']['day_end_hour'] = args.day_end
    if args.no_links:
        config['schedule']['links_enabled'] = False
    elif args.links:
        config['schedule']['links_enabled'] = True

    all_posts = []
    for fp in args.files:
        text = Path(fp).read_text(encoding='utf-8')
        all_posts.extend(parse_posts(text))

    if args.exclude:
        excluded = {int(x) for x in args.exclude.split(',')}
        all_posts = [p for i, p in enumerate(all_posts, 1) if i not in excluded]
        print(f'{sorted(excluded)}番を除外（残り{len(all_posts)}本）', file=sys.stderr)

    tsv = build_tsv(all_posts, config, links, start_num=args.start_num or 1)

    if args.clipboard:
        import pyperclip
        pyperclip.copy(tsv)
        print(f'{len(all_posts)}件のポストをクリップボードにコピーしました', file=sys.stderr)

    if args.output:
        Path(args.output).write_text(tsv, encoding='utf-8')
        print(f'{args.output} に出力しました', file=sys.stderr)

    if not args.clipboard and not args.output:
        print(tsv)


if __name__ == '__main__':
    main()
