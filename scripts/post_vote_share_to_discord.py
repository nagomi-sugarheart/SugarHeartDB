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

ROOT = Path(__file__).resolve().parent.parent
RANKING = ROOT / "data" / "vote2026" / "ranking.json"

JST = datetime.timezone(datetime.timedelta(hours=9))
TOP_N = 15
REWARD_BORDERS = {5: "xRライブ・新規楽曲・専用衣装", 7: "ソロ楽曲・M@STER ARTIST", 15: "ちびぐるみ"}
EMBED_COLOR = 0xF04E98  # 佐藤心のイメージカラー
DISCORD_LIMIT = 4096    # embed description の上限


def build_table(ranking: list[dict], top: int, focus: str) -> str:
    lines = [f'{"順":>2} {"帯":>2} {"アイドル":<11}{"人数":>5}{"シェア":>8}']
    lines.append("─" * 34)
    for row in ranking[:top]:
        border = REWARD_BORDERS.get(row["rank"] - 1)
        if border:
            lines.append(f'──── {row["rank"]-1}位ボーダー：{border} ────')
        mark = "◀" if row["slug"] == focus else " "
        name = row["name"]
        # 全角換算で桁を揃える
        pad = 11 - sum(2 if ord(ch) > 0x2E80 else 1 for ch in name)
        lines.append(f'{row["rank"]:>2} {row["band"]:>2} {name}{" " * max(pad, 1)}'
                     f'{row["users"]:>5}{row["share"]:>7.2f}%{mark}')
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
            f'**{target["name"]}：{target["rank"]}位**（帯{target["band"]} / '
            f'{target["users"]}人 / シェア{target["share"]:.2f}%）')

        # 同じ帯は数十名になることがあるので、表に出ている範囲だけ名前を挙げる
        same = [row["name"] for row in ranking
                if row["band"] == target["band"] and row["slug"] != focus]
        shown = [row["name"] for row in ranking[:top]
                 if row["band"] == target["band"] and row["slug"] != focus]
        rest = len(same) - len(shown)
        if same:
            label = "、".join(shown) if shown else ""
            if rest > 0:
                label = f'{label}{" ほか" if label else ""}{rest}名'
            parts.append(f'同じ帯で区別できない相手：{label}')
        else:
            parts.append("同じ帯で区別できない相手：なし")

        # 直上のボーダー（順位より小さい閾値のうち最大のもの）との差を出す
        above = [border for border in REWARD_BORDERS
                 if border < target["rank"] and len(ranking) >= border]
        if above:
            border = max(above)
            gap = ranking[border - 1]["users"] - target["users"]
            parts.append(
                f'{border}位（{ranking[border-1]["name"]}）との差：{gap}人'
                f' — {REWARD_BORDERS[border]}')

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
                               "同じ帯のアイドル同士は区別できません。"},
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }],
    }


def post(url: str, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "User-Agent": "SugarHeartDB-vote2026/1.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        if res.status not in (200, 204):
            raise RuntimeError(f"Discordが status={res.status} を返しました")


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

    url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not url:
        raise SystemExit(
            "環境変数 DISCORD_WEBHOOK_URL が設定されていません。\n"
            "  export DISCORD_WEBHOOK_URL='https://discord.com/api/webhooks/...'\n"
            "URLは秘密情報です。リポジトリには絶対に書き込まないでください。")
    if not url.startswith("https://discord.com/api/webhooks/") and \
       not url.startswith("https://discordapp.com/api/webhooks/"):
        raise SystemExit("DISCORD_WEBHOOK_URL がDiscordのウェブフックURLの形式ではありません。")

    try:
        post(url, payload)
    except urllib.error.HTTPError as exc:
        # 本文にURLが含まれる可能性があるので、そのままは出さない
        raise SystemExit(f"投稿に失敗しました: HTTP {exc.code} {exc.reason}") from None
    except urllib.error.URLError as exc:
        raise SystemExit(f"投稿に失敗しました: {exc.reason}") from None

    print("Discordに投稿しました。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
