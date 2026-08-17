#!/usr/bin/env python3
"""収集した公式シェア投稿を集計し、上位15名の順位表を出力する。

直近のローリング窓（既定24時間）で、アイドル別のユニーク投稿者数を数える。
1回の検索で返るのは最大39〜40件で、遡れる時間幅が投稿量に反比例するため、
生の取得結果をそのまま比べると投稿の多いアイドルほど短い窓で評価されて
しまう。全190名が欠測なくカバーされている時間帯の交差を共通窓として
切り出すことでこのバイアスを除く。

暦日で区切った前日合計とのべ数ランキングは daily_report_vote_share.py が出す。

使い方:
    python3 scripts/rank_vote_share.py
    python3 scripts/rank_vote_share.py --window-hours 24 --days 2

詳細は docs/vote2026-tracking.md を参照。
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vote_share_lib as lib  # noqa: E402

RANKING = lib.OUTDIR / "ranking.json"
TOP_N = 15


def main() -> int:
    parser = argparse.ArgumentParser(description="公式シェア投稿を集計して順位表を出す")
    parser.add_argument("--date", help="対象日 (YYYY-MM-DD) の収集ファイルだけを使う")
    parser.add_argument("--days", type=int, default=2,
                        help="直近何日ぶんの収集ファイルを読むか（既定 2）")
    parser.add_argument("--top", type=int, default=TOP_N, help=f"表示件数（既定 {TOP_N}）")
    parser.add_argument("--focus", default="sato_shin", help="注目するアイドルの slug")
    parser.add_argument("--window-hours", type=float, default=24.0,
                        help="集計窓の長さ（時間、既定 24）。0で取得できている全期間。"
                             "短くするほどポアソンノイズが増え順位が読めなくなる")
    args = parser.parse_args()

    idols = lib.load_idols()
    stores = lib.load_stores(dates=[args.date] if args.date else None, days=args.days)
    posts = lib.merge_posts(stores)

    floors = lib.effective_coverage(stores)
    if not floors:
        raise SystemExit("coverage 情報がありません。collect_vote_share.py で再収集してください。")
    start = max(floors.values())
    end = lib.last_sweep_at(stores)
    if args.window_hours:
        # 収集がまだ窓の長さぶん貯まっていない場合は、貯まっている分だけを使う
        start = max(start, end - int(args.window_hours * 3600))
    if start >= end:
        raise SystemExit("共通窓が空です。収集間隔を詰めて再取得してください。")

    counts, used, inconsistent = lib.count_authors(posts, idols, start, end)
    total = sum(counts.values())
    if total == 0:
        raise SystemExit("共通窓に投稿がありません。収集間隔を詰めて再取得してください。")
    rows = lib.build_rows(counts, idols)
    saturated = sorted(lib.saturated_slugs(stores))

    hours = (end - start) / 3600
    print(f"共通窓: {lib.fmt(start)} 〜 {lib.fmt(end)} JST（{hours:.1f}時間）")
    print(f"投稿 {used:,}件 / ユニーク投稿者 {total:,}人 / 対象 {len(idols)}名")
    print(f"URL・本文の不一致（編集された投稿）: {inconsistent}件"
          f"（{inconsistent/max(used,1)*100:.2f}%）\n")

    print(f'{"順位":<5}{"アイドル":<14}{"人数":>5}{"シェア":>9}{"取りうる順位":>14}')
    print("-" * 54)
    for row in rows[:args.top]:
        if row["rank"] - 1 in lib.REWARD_BORDERS:
            print(f'{"":-<20} {row["rank"]-1}位ボーダー {"":-<21}')
        mark = " ←" if row["slug"] == args.focus else ""
        span = f'{row["rank_best"]}〜{row["rank_worst"]}位'
        print(f'{row["rank"]:>2}.  {row["name"]:<14}{row["users"]:>5}'
              f'{row["share"]:>8.2f}%{span:>12}{mark}')

    focus = next((row for row in rows if row["slug"] == args.focus), None)
    if focus:
        print(f'\n{focus["name"]}: 表示順{focus["rank"]}位 / {focus["users"]}人 / '
              f'シェア{focus["share"]:.2f}%')
        print(f'  取りうる順位: {focus["rank_best"]}位〜{focus["rank_worst"]}位')
        above = [b for b in lib.REWARD_BORDERS if b < focus["rank"] and len(rows) >= b]
        if above:
            border = max(above)
            print(f'  {border}位（{rows[border-1]["name"]}）との差: '
                  f'{rows[border-1]["users"] - focus["users"]}人')

    if saturated:
        print(f"\n警告: 取りこぼしの疑いが {len(saturated)}名 に記録されています。"
              f"投稿の多いアイドルほど実数より少なく出ます: "
              f"{', '.join(saturated[:10])}{' ...' if len(saturated) > 10 else ''}")

    print("\n※ この結果は公式シェア投稿から推定した投票人数の代理指標であり、"
          "公式の投票結果でも得票数でもありません。")
    print("※ 表示順の隣にある順位差の多くは、観測のばらつきの範囲内で"
          "意味がありません。「取りうる順位」の幅が実際の不確かさです。")

    RANKING.write_text(json.dumps({
        "generated_at": int(datetime.datetime.now(lib.JST).timestamp()),
        "window": {"start": start, "end": end, "hours": round(hours, 2)},
        "totals": {"posts": used, "unique_authors": total, "inconsistent": inconsistent},
        "saturated": saturated,
        "ranking": rows,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n{RANKING.relative_to(lib.ROOT)} に書き出しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
