#!/usr/bin/env python3
"""前日の日合計と、これまでの全日ののべ数ランキングを集計する。

4時間おきの速報（rank_vote_share.py）が直近24時間のローリング窓を見るのに対し、
こちらは JST の暦日で区切って集計する。

- 日合計：対象日（既定は前日）の、アイドル別ユニーク投稿者数
- のべ数：収集開始日から対象日までの各日のユニーク投稿者数を足し上げたもの。
  同じ人が別の日に投稿すれば別に数える（投票報告は日次ミッションのため、
  のべ数は「延べ何人日ぶんの投票報告があったか」を表す）

出力：data/vote2026/daily-report.json

使い方:
    python3 scripts/daily_report_vote_share.py            # 前日
    python3 scripts/daily_report_vote_share.py --date 2026-08-17

詳細は docs/vote2026-tracking.md を参照。
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import vote_share_lib as lib  # noqa: E402

REPORT = lib.OUTDIR / "daily-report.json"
TOP_N = 15


def day_window(day: datetime.date, floor: int, end: int):
    """その日の、実際に集計できる窓と完全性を返す。"""
    day_start, day_end = lib.jst_day_bounds(day)
    start = max(day_start, floor)
    stop = min(day_end, end)
    complete = floor <= day_start and end >= day_end
    return start, stop, complete


def main() -> int:
    parser = argparse.ArgumentParser(description="前日の日合計とのべ数ランキングを集計する")
    parser.add_argument("--date", help="対象日 (YYYY-MM-DD)。既定は前日")
    parser.add_argument("--top", type=int, default=TOP_N, help=f"表示件数（既定 {TOP_N}）")
    parser.add_argument("--focus", default="sato_shin", help="注目するアイドルの slug")
    args = parser.parse_args()

    idols = lib.load_idols()
    stores = lib.load_stores()
    posts = lib.merge_posts(stores)

    floors = lib.effective_coverage(stores)
    if not floors:
        raise SystemExit("coverage 情報がありません。collect_vote_share.py で再収集してください。")
    floor = max(floors.values())
    end = lib.last_sweep_at(stores)

    if args.date:
        target = datetime.date.fromisoformat(args.date)
    else:
        target = datetime.datetime.now(lib.JST).date() - datetime.timedelta(days=1)

    first = min(datetime.date.fromisoformat(store["date"]) for store in stores)
    # 収集データの最初の日より前は存在しない
    first = max(first, datetime.datetime.fromtimestamp(floor, lib.JST).date())
    if target < first:
        raise SystemExit(f"{target} のデータがありません（収集開始は {first}）。")

    # --- 各日を集計し、のべ数を積み上げる ---
    cumulative: dict[str, int] = {slug: 0 for slug in idols}
    days: list[dict] = []
    target_counts: dict[str, int] = {}
    target_meta: dict = {}

    day = first
    while day <= target:
        start, stop, complete = day_window(day, floor, end)
        if stop > start:
            counts, used, inconsistent = lib.count_authors(posts, idols, start, stop)
            for slug, value in counts.items():
                cumulative[slug] += value
            days.append({
                "date": day.isoformat(),
                "complete": complete,
                "hours": round((stop - start) / 3600, 2),
                "unique_authors": sum(counts.values()),
                "posts": used,
                "inconsistent": inconsistent,
            })
            if day == target:
                target_counts = counts
                target_meta = {
                    "window": {"start": start, "end": stop,
                               "hours": round((stop - start) / 3600, 2)},
                    "complete": complete,
                    "posts": used,
                    "inconsistent": inconsistent,
                    "unique_authors": sum(counts.values()),
                }
        day += datetime.timedelta(days=1)

    if not target_counts:
        raise SystemExit(f"{target} に集計できる投稿がありません。")

    daily_rows = lib.build_rows(target_counts, idols)
    cumulative_rows = lib.build_rows(cumulative, idols)
    saturated = sorted(lib.saturated_slugs(stores))

    # --- 表示 ---
    meta = target_meta
    flag = "" if meta["complete"] else "  ※部分集計（1日ぶんに満たない）"
    print(f"■ {target} の日合計{flag}")
    print(f"  集計窓: {lib.fmt(meta['window']['start'])} 〜 {lib.fmt(meta['window']['end'])} JST"
          f"（{meta['window']['hours']:.1f}時間）")
    print(f"  ユニーク投稿者 {meta['unique_authors']:,}人 / 投稿 {meta['posts']:,}件 / "
          f"不一致 {meta['inconsistent']}件\n")
    print(f'{"順位":<5}{"アイドル":<14}{"人数":>5}{"シェア":>9}{"取りうる順位":>14}')
    print("-" * 54)
    for row in daily_rows[:args.top]:
        if row["rank"] - 1 in lib.REWARD_BORDERS:
            print(f'{"":-<20} {row["rank"]-1}位ボーダー {"":-<21}')
        mark = " ←" if row["slug"] == args.focus else ""
        span = f'{row["rank_best"]}〜{row["rank_worst"]}位'
        print(f'{row["rank"]:>2}.  {row["name"]:<14}{row["users"]:>5}'
              f'{row["share"]:>8.2f}%{span:>12}{mark}')

    total_days = len(days)
    partial = [d["date"] for d in days if not d["complete"]]
    print(f"\n■ のべ数ランキング（{days[0]['date']} 〜 {target} / {total_days}日）")
    print(f"  のべ {sum(cumulative.values()):,}人")
    if partial:
        print(f"  ※ {', '.join(partial)} は1日ぶんに満たない部分集計を含む")
    print()
    print(f'{"順位":<5}{"アイドル":<14}{"のべ":>6}{"シェア":>9}{"取りうる順位":>14}')
    print("-" * 55)
    for row in cumulative_rows[:args.top]:
        if row["rank"] - 1 in lib.REWARD_BORDERS:
            print(f'{"":-<20} {row["rank"]-1}位ボーダー {"":-<22}')
        mark = " ←" if row["slug"] == args.focus else ""
        span = f'{row["rank_best"]}〜{row["rank_worst"]}位'
        print(f'{row["rank"]:>2}.  {row["name"]:<14}{row["users"]:>6}'
              f'{row["share"]:>8.2f}%{span:>12}{mark}')

    focus_daily = next((r for r in daily_rows if r["slug"] == args.focus), None)
    focus_total = next((r for r in cumulative_rows if r["slug"] == args.focus), None)
    if focus_daily and focus_total:
        print(f'\n{focus_daily["name"]}: 前日 {focus_daily["rank"]}位（{focus_daily["users"]}人）'
              f' / のべ {focus_total["rank"]}位（{focus_total["users"]}人・'
              f'取りうる順位 {focus_total["rank_best"]}〜{focus_total["rank_worst"]}位）')

    if saturated:
        print(f"\n警告: 取りこぼしの疑いが記録されたアイドルが {len(saturated)}名います: "
              f"{', '.join(saturated[:10])}{' ...' if len(saturated) > 10 else ''}")

    print("\n※ この結果は公式シェア投稿から推定した投票人数の代理指標であり、"
          "公式の投票結果でも得票数でもありません。")

    REPORT.write_text(json.dumps({
        "generated_at": int(datetime.datetime.now(lib.JST).timestamp()),
        "target_date": target.isoformat(),
        "daily": {**target_meta, "ranking": daily_rows},
        "cumulative": {
            "from": days[0]["date"], "to": target.isoformat(),
            "days": days, "total": sum(cumulative.values()),
            "partial_days": partial, "ranking": cumulative_rows,
        },
        "saturated": saturated,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n{REPORT.relative_to(lib.ROOT)} に書き出しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
