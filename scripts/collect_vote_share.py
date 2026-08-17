#!/usr/bin/env python3
"""シンデレラガール総選挙2026の公式シェア投稿を収集する。

Yahoo!リアルタイム検索で `"{公式表記名} さんに投票しました"` を190名分検索し、
投稿を `data/vote2026/YYYY-MM-DD.json` に追記する（`post_id` で重複排除）。

1回の検索で返るのは最大40件で、40件がカバーする時間幅は投稿量に反比例する。
実測では最多のアイドルでも40件で9.6時間ぶんを含んでいたため、4時間おきに
実行すれば取りこぼさずに全数を取得できる。返却が40件に達した場合は
取りこぼしの疑いがあるため警告を出す。

使い方:
    python scripts/collect_vote_share.py

詳細は docs/vote2026-tracking.md を参照。
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDOLS = ROOT / "data" / "idols.json"
OUTDIR = ROOT / "data" / "vote2026"

ENDPOINT = "https://search.yahoo.co.jp/realtime/search"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")
NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.S)
SLUG_FROM_URL = re.compile(r"/idol/([a-z_]+)")
NAME_FROM_TEXT = re.compile(r"^(.+?)\s*さんに投票しました")

JST = datetime.timezone(datetime.timedelta(hours=9))
RETURN_LIMIT = 40          # これに達したら取りこぼしの疑い
REQUEST_INTERVAL = 1.5     # 秒。これ以上詰めないこと


def fetch(query: str) -> dict:
    url = f"{ENDPOINT}?" + urllib.parse.urlencode({"p": query, "rkf": 3})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "ja"})
    with urllib.request.urlopen(req, timeout=30) as res:
        html = res.read().decode("utf-8", errors="replace")
    match = NEXT_DATA.search(html)
    if not match:
        raise RuntimeError("__NEXT_DATA__ が見つかりません。Yahoo側の仕様変更の可能性があります。")
    return json.loads(match.group(1))["props"]["pageProps"]["pageData"]


def clean_text(raw: str | None) -> str:
    # Yahooは検索語を \tSTART\t ... \tEND\t で囲んで返す
    return (raw or "").replace("\tSTART\t", "").replace("\tEND\t", "")


def parse_entry(entry: dict, idol: dict) -> dict:
    text = clean_text(entry.get("displayTextBody") or entry.get("displayText"))

    # 本文中のリンクは t.co に短縮されているため、展開済みの expandedUrl を見る。
    # url キーは短縮URLなので使わない。
    slug_from_url = None
    for link in entry.get("urls") or []:
        if isinstance(link, dict):
            target = link.get("expandedUrl") or link.get("url") or ""
        else:
            target = str(link)
        found = SLUG_FROM_URL.search(target)
        if found:
            slug_from_url = found.group(1)
            break

    name_match = NAME_FROM_TEXT.match(text.strip())
    name_from_text = name_match.group(1).strip() if name_match else None

    return {
        "post_id": entry["id"],
        "author_id": entry["userId"],
        "created_at": entry["createdAt"],
        "slug": idol["slug"],
        "slug_from_url": slug_from_url,
        "name_from_text": name_from_text,
        "is_consistent": slug_from_url == idol["slug"] and name_from_text == idol["name"],
        "text": text,
    }


def load_store(path: Path, date_label: str) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"date": date_label, "sweeps": [], "posts": {}, "coverage": {}}


def main() -> int:
    parser = argparse.ArgumentParser(description="総選挙2026の公式シェア投稿を収集する")
    parser.add_argument("--interval", type=float, default=REQUEST_INTERVAL,
                        help=f"リクエスト間隔（秒、既定 {REQUEST_INTERVAL}）")
    args = parser.parse_args()
    if args.interval < REQUEST_INTERVAL:
        parser.error(f"リクエスト間隔は {REQUEST_INTERVAL} 秒以上にしてください")

    idols = json.loads(IDOLS.read_text(encoding="utf-8"))
    started = datetime.datetime.now(JST)
    date_label = started.strftime("%Y-%m-%d")
    OUTDIR.mkdir(parents=True, exist_ok=True)
    path = OUTDIR / f"{date_label}.json"
    store = load_store(path, date_label)

    previous_sweep_at = max((sweep["collected_at"] for sweep in store["sweeps"]), default=None)

    print(f"収集開始 {started:%Y-%m-%d %H:%M:%S} JST / 対象 {len(idols)}名", file=sys.stderr)

    added = 0
    saturated: list[str] = []
    failed: list[str] = []

    for index, idol in enumerate(idols, 1):
        query = f'"{idol["name"]} さんに投票しました"'
        page = None
        for attempt in range(3):
            try:
                page = fetch(query)
                break
            except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as exc:
                if attempt == 2:
                    failed.append(idol["slug"])
                    print(f"  失敗 {idol['name']}: {exc}", file=sys.stderr)
                else:
                    time.sleep(4 * (attempt + 1))
        if page is None:
            time.sleep(args.interval)
            continue

        entries = page.get("timeline", {}).get("entry") or []

        oldest = None
        for entry in entries:
            record = parse_entry(entry, idol)
            if record["post_id"] not in store["posts"]:
                added += 1
            store["posts"][record["post_id"]] = record
            oldest = record["created_at"] if oldest is None else min(oldest, record["created_at"])

        # 返却が上限に達していても、前回スイープの時刻より前まで遡れていれば
        # 取りこぼしはない。当日の初回スイープは必ず上限に達するが、これは
        # 遡れる限界まで取っただけなので警告しない。
        if len(entries) >= RETURN_LIMIT and previous_sweep_at is not None \
                and oldest is not None and oldest > previous_sweep_at:
            saturated.append(idol["slug"])

        if oldest is not None:
            previous = store["coverage"].get(idol["slug"])
            # そのアイドルについて確実に遡れている最古時刻
            store["coverage"][idol["slug"]] = min(previous, oldest) if previous else oldest

        if index % 20 == 0:
            elapsed = (datetime.datetime.now(JST) - started).seconds
            print(f"  [{index}/{len(idols)}] 経過 {elapsed}s / 新規 {added}件", file=sys.stderr)
        time.sleep(args.interval)

    store["sweeps"].append({
        "collected_at": int(started.timestamp()),
        "finished_at": int(datetime.datetime.now(JST).timestamp()),
        "added": added,
        "saturated": saturated,
        "failed": failed,
    })
    path.write_text(json.dumps(store, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"完了 {datetime.datetime.now(JST):%H:%M:%S} / 新規 {added}件 "
          f"/ 累計 {len(store['posts'])}件 → {path.relative_to(ROOT)}", file=sys.stderr)

    if saturated:
        print(f"警告: {len(saturated)}名で返却が{RETURN_LIMIT}件に達しました。"
              f"前回スイープ以降に取りこぼしがあります。収集間隔を詰めてください: "
              f"{', '.join(saturated[:10])}{' ...' if len(saturated) > 10 else ''}",
              file=sys.stderr)
    if failed:
        print(f"警告: {len(failed)}名の取得に失敗しました: {', '.join(failed)}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
