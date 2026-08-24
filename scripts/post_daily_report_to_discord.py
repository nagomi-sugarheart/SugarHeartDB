#!/usr/bin/env python3
"""前日の日合計とのべ数ランキングをDiscordのチャンネルに投稿する。

`daily_report_vote_share.py` が書き出した `data/vote2026/daily-report.json` を読む。

**ウェブフックURLは絶対にリポジトリに書かないこと。**
環境変数 `DISCORD_WEBHOOK_URL` から読み込む。

    python3 scripts/daily_report_vote_share.py
    python3 scripts/post_daily_report_to_discord.py

詳細は docs/vote2026-tracking.md を参照。
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vote_share_lib as lib  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "data" / "vote2026" / "daily-report.json"

JST = datetime.timezone(datetime.timedelta(hours=9))
TOP_N = 15
USER_AGENT = "SugarHeartDB-vote2026/1.0"
REWARD_BORDERS = {5: "xRライブ", 7: "ソロ楽曲", 15: "ちびぐるみ"}
EMBED_COLOR = 0xF04E98  # 佐藤心のイメージカラー
DISCORD_LIMIT = 4096


def width(text: str) -> int:
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in text)


def table(ranking: list[dict], top: int, focus: str, head: str) -> str:
    lines = [f'{"順":>2} {"アイドル":<11}{head:>5}{"シェア":>8}  取りうる順位', "─" * 42]
    for row in ranking[:top]:
        border = REWARD_BORDERS.get(row["rank"] - 1)
        if border:
            lines.append(f'──── {row["rank"]-1}位ボーダー：{border} ────')
        mark = "◀" if row["slug"] == focus else " "
        pad = max(11 - width(row["name"]), 1)
        span = f'{row["rank_best"]}〜{row["rank_worst"]}位'
        lines.append(f'{row["rank"]:>2} {row["name"]}{" " * pad}'
                     f'{row["users"]:>4}{row["share"]:>7.2f}%{mark}{span:>9}')
    return "```\n" + "\n".join(lines) + "\n```"


def build_payload(data: dict, top: int, focus: str) -> dict:
    daily, total = data["daily"], data["cumulative"]
    target = data["target_date"]

    parts = [f'## {target} の日合計', table(daily["ranking"], top, focus, "人数")]
    if not daily["complete"]:
        parts.append(f'-# ⚠ この日は{daily["window"]["hours"]:.1f}時間ぶんしか収集できておらず、'
                     f'1日分に達していません（部分集計）。')

    parts.append(f'## のべ数ランキング（{total["from"]} 〜 {total["to"]}・{len(total["days"])}日）')
    parts.append(table(total["ranking"], top, focus, "のべ"))
    parts.append(f'のべ **{total["total"]:,}人**（同じ人でも別の日に投票報告すれば別に数えます）')
    if total["partial_days"]:
        parts.append(f'-# ⚠ {"、".join(total["partial_days"])} は部分集計を含みます。')
    if data.get("saturated"):
        parts.append(f'-# ⚠ 取りこぼしの疑いが {len(data["saturated"])}名 に記録されています。'
                     f'投稿が多いアイドルほど実数より少なく出ます。')

    daily_focus = next((r for r in daily["ranking"] if r["slug"] == focus), None)
    total_focus = next((r for r in total["ranking"] if r["slug"] == focus), None)
    if daily_focus and total_focus:
        parts.append(
            f'**{daily_focus["name"]}**：前日 **{daily_focus["rank"]}位**'
            f'（{daily_focus["users"]}人） / のべ **{total_focus["rank"]}位**'
            f'（{total_focus["users"]}人・取りうる順位 '
            f'{total_focus["rank_best"]}〜{total_focus["rank_worst"]}位）')

    description = "\n".join(parts)
    if len(description) > DISCORD_LIMIT:
        description = description[:DISCORD_LIMIT - 3] + "..."

    return {
        "username": "総選挙2026 投票傾向",
        "embeds": [{
            "title": f"日次サマリ（{target}）",
            "description": description,
            "color": EMBED_COLOR,
            "footer": {"text": "公式シェア投稿から推定した投票人数の代理指標です。"
                               "公式の投票結果でも得票数でもありません。"
                               "表示順の隣にある順位差の多くは観測のばらつきの範囲内で、"
                               "「取りうる順位」の幅が実際の不確かさです。"},
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="日次サマリをDiscordに投稿する")
    parser.add_argument("--top", type=int, default=TOP_N, help=f"表示件数（既定 {TOP_N}）")
    parser.add_argument("--focus", default="sato_shin", help="注目するアイドルの slug")
    parser.add_argument("--dry-run", action="store_true", help="投稿せず内容を表示する")
    args = parser.parse_args()

    if not REPORT.exists():
        raise SystemExit(f"{REPORT.relative_to(ROOT)} がありません。"
                         "先に scripts/daily_report_vote_share.py を実行してください。")
    payload = build_payload(json.loads(REPORT.read_text(encoding="utf-8")),
                            args.top, args.focus)

    if args.dry_run:
        embed = payload["embeds"][0]
        print(embed["title"])
        print(embed["description"])
        print(f'({embed["footer"]["text"]})')
        return 0

    lib.post_json(lib.webhook_url_from_env(), payload, USER_AGENT)

    print("Discordに投稿しました。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
