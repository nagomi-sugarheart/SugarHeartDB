#!/usr/bin/env python3
"""集計した順位表をDiscordのチャンネルに投稿する。

`rank_vote_share.py` が書き出した `data/vote2026/ranking.json` を読み、
Discordのウェブフック経由で上位15名の順位表を投稿する。

**ウェブフックURLは絶対にリポジトリに書かないこと。**
このリポジトリは公開されているため、URLが漏れると誰でもそのチャンネルに
投稿できるようになる。環境変数 `DISCORD_WEBHOOK_URL` から読み込む。

    export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/...'
    python scripts/rank_vote_share.py
    python scripts/post_vote_share_to_discord.py

ウェブフックの作り方:
    投稿したいチャンネルの「チャンネルの編集」→「連携サービス」→
    「ウェブフックを作成」→「ウェブフックURLをコピー」

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
RANKING = ROOT / "data" / "vote2026" / "ranking.json"

JST = datetime.timezone(datetime.timedelta(hours=9))
TOP_N = 15
REWARD_BORDERS = {5: "xRライブ・新規楽曲・専用衣装", 7: "ソロ楽曲・M@STER ARTIST", 15: "ちびぐるみ"}
EMBED_COLOR = 0xF04E98  # 佐藤心のイメージカラー
DISCORD_LIMIT = 4096    # embed description の上限
USER_AGENT = "SugarHeartDB-vote2026/1.0"


def build_table(ranking: list[dict], top: int, focus: str) -> str:
    lines = [f'{"順":>2} {"アイドル":<11}{"人数":>4}{"シェア":>8}  取りうる順位']
    lines.append("─" * 42)
    for row in ranking[:top]:
        border = REWARD_BORDERS.get(row["rank"] - 1)
        if border:
            lines.append(f'──── {row["rank"]-1}位ボーダー：{border} ────')
        mark = "◀" if row["slug"] == focus else " "
        name = row["name"]
        # 全角換算で桁を揃える
        pad = 11 - sum(2 if ord(ch) > 0x2E80 else 1 for ch in name)
        span = f'{row["rank_best"]}〜{row["rank_worst"]}位'
        lines.append(f'{row["rank"]:>2} {name}{" " * max(pad, 1)}'
                     f'{row["users"]:>4}{row["share"]:>7.2f}%{mark}{span:>9}')
    return "```\n" + "\n".join(lines) + "\n```"


def build_payload(data: dict, top: int, focus: str) -> dict:
    ranking = data["ranking"]
    window = data["window"]
    totals = data["totals"]

    start = datetime.datetime.fromtimestamp(window["start"], JST)
    end = datetime.datetime.fromtimestamp(window["end"], JST)

    parts = [build_table(ranking, top, focus)]

    target = next((row for row in ranking if row["slug"] == focus), None)
    if target:
        parts.append(
            f'**{target["name"]}：表示順{target["rank"]}位**'
            f'（{target["users"]}人 / シェア{target["share"]:.2f}%）')
        parts.append(
            f'**取りうる順位：{target["rank_best"]}位〜{target["rank_worst"]}位**'
            f'（この幅が現時点の不確かさです）')

        # 直上のボーダー（順位より小さい閾値のうち最大のもの）との差を出す
        above = [border for border in REWARD_BORDERS
                 if border < target["rank"] and len(ranking) >= border]
        if above:
            border = max(above)
            gap = ranking[border - 1]["users"] - target["users"]
            parts.append(
                f'{border}位（{ranking[border-1]["name"]}）との差：{gap}人'
                f' — {REWARD_BORDERS[border]}')

    # 取りこぼしは投稿の多いアイドルほど起きるため、順位を直接歪める。
    # ログを読む人がいなくても気づけるよう、投稿本文に出す。
    if data.get("saturated"):
        parts.append(f'-# ⚠ 取りこぼしの疑いが {len(data["saturated"])}名 に記録されています。'
                     "該当するアイドルは実数より少なく出ています。")

    description = "\n".join(parts)
    if len(description) > DISCORD_LIMIT:
        description = description[:DISCORD_LIMIT - 3] + "..."

    return {
        "username": "総選挙2026 投票傾向",
        "embeds": [{
            "title": f"シンデレラガール総選挙2026 投票傾向（{end:%m/%d %H:%M} 時点）",
            "description": description,
            "color": EMBED_COLOR,
            "fields": [
                {"name": "集計窓", "inline": True,
                 "value": f'{start:%m/%d %H:%M} 〜 {end:%m/%d %H:%M}\n（{window["hours"]:.1f}時間）'},
                {"name": "ユニーク投稿者", "inline": True,
                 "value": f'{totals["unique_authors"]:,}人 / {totals["posts"]:,}投稿'},
            ],
            "footer": {"text": "公式シェア投稿から推定した投票人数の代理指標です。"
                               "公式の投票結果でも得票数でもありません。"
                               "表示順の隣にある順位差の多くは観測のばらつきの範囲内で、"
                               "「取りうる順位」の幅が実際の不確かさです。"},
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="順位表をDiscordに投稿する")
    parser.add_argument("--top", type=int, default=TOP_N, help=f"投稿件数（既定 {TOP_N}）")
    parser.add_argument("--focus", default="sato_shin", help="注目するアイドルの slug")
    parser.add_argument("--dry-run", action="store_true",
                        help="投稿せず、送信内容を標準出力に表示する")
    args = parser.parse_args()

    if not RANKING.exists():
        raise SystemExit(
            f"{RANKING.relative_to(ROOT)} がありません。"
            "先に scripts/rank_vote_share.py を実行してください。")
    data = json.loads(RANKING.read_text(encoding="utf-8"))
    payload = build_payload(data, args.top, args.focus)

    if args.dry_run:
        embed = payload["embeds"][0]
        print(embed["title"])
        print(embed["description"])
        for field in embed["fields"]:
            print(f'{field["name"]}: {field["value"]}')
        print(f'({embed["footer"]["text"]})')
        return 0

    lib.post_json(lib.webhook_url_from_env(), payload, USER_AGENT)

    print("Discordに投稿しました。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
