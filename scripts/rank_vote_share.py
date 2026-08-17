#!/usr/bin/env python3
"""収集した公式シェア投稿を集計し、上位15名の順位表を出力する。

`data/vote2026/YYYY-MM-DD.json` を読み、**全190名が確実にカバーされている
時間帯の交差**を共通窓として切り出したうえで、アイドル別のユニーク投稿者数を
数える。1回の検索で返るのは最大40件で、遡れる時間幅が投稿量に反比例するため、
生の取得結果をそのまま比べると投稿の多いアイドルほど短い窓で評価されてしまう。
共通窓を取ることでこのバイアスを除く。

順位は同時に「帯」に分類する。投稿の到着はポアソン過程なので、件数差が
小さいアイドル同士は観測期間内では区別できない。区別できない相手を同じ帯に
まとめ、順位が確定的に読めるものだけを分けて示す。

使い方:
    python scripts/rank_vote_share.py            # 当日分
    python scripts/rank_vote_share.py --date 2026-08-17
    python scripts/rank_vote_share.py --days 7   # 直近7日ぶんをプール

詳細は docs/vote2026-tracking.md を参照。
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDOLS = ROOT / "data" / "idols.json"
OUTDIR = ROOT / "data" / "vote2026"
RANKING = OUTDIR / "ranking.json"

JST = datetime.timezone(datetime.timedelta(hours=9))
TOP_N = 15
Z = 1.96  # 95%
# 報酬の段階閾値（docs/vote2026-tracking.md §1.2）
REWARD_BORDERS = (5, 7, 15)


def load_stores(days: int, date: str | None) -> list[dict]:
    if date:
        paths = [OUTDIR / f"{date}.json"]
    else:
        paths = sorted(OUTDIR.glob("????-??-??.json"))[-days:]
    stores = []
    for path in paths:
        if not path.exists():
            raise SystemExit(f"{path} がありません。先に collect_vote_share.py を実行してください。")
        stores.append(json.loads(path.read_text(encoding="utf-8")))
    if not stores:
        raise SystemExit("集計対象のデータがありません。先に collect_vote_share.py を実行してください。")
    return stores


def common_window(stores: list[dict], window_hours: float | None) -> tuple[int, int]:
    """全アイドルが確実にカバーされている時間帯の交差を返す。

    window_hours を指定すると、その時間ぶんだけを切り出す（ローリング窓）。
    集計窓が短いほどポアソンノイズが増え、順位差が読めなくなる。
    """
    # 下限：最も遡れていないアイドルの最古時刻（＝そこより前は欠測がありうる）
    floors = [ts for store in stores for ts in store.get("coverage", {}).values()]
    if not floors:
        raise SystemExit("coverage 情報がありません。collect_vote_share.py で再収集してください。")
    start = max(floors)
    # 上限：最後のスイープ開始時刻（それ以降は未取得のアイドルがありうる）
    ends = [sweep["collected_at"] for store in stores for sweep in store.get("sweeps", [])]
    if not ends:
        raise SystemExit("sweeps 情報がありません。")
    end = max(ends)
    if window_hours:
        # 収集がまだ窓の長さぶん貯まっていない場合は、貯まっている分だけを使う
        start = max(start, end - int(window_hours * 3600))
    if start >= end:
        raise SystemExit(
            "共通窓が空です。収集が1回だけか、取りこぼしが大きい可能性があります。"
            "収集間隔を詰めて再取得してください。")
    return start, end


def distinguishable(count_a: int, count_b: int) -> bool:
    """2つの計数がポアソンノイズを超えて有意に違うか。"""
    if count_a + count_b == 0:
        return False
    return abs(count_a - count_b) > Z * math.sqrt(count_a + count_b)


def assign_bands(rows: list[dict]) -> None:
    """区別できない相手をまとめて帯に分類する。"""
    band = 0
    anchor = None
    for row in rows:
        if anchor is None or distinguishable(anchor["users"], row["users"]):
            band += 1
            anchor = row
        row["band"] = band


def main() -> int:
    parser = argparse.ArgumentParser(description="公式シェア投稿を集計して順位表を出す")
    parser.add_argument("--date", help="対象日 (YYYY-MM-DD)。既定は最新")
    parser.add_argument("--days", type=int, default=1, help="直近何日ぶんをプールするか（既定 1）")
    parser.add_argument("--top", type=int, default=TOP_N, help=f"表示件数（既定 {TOP_N}）")
    parser.add_argument("--focus", default="sato_shin", help="注目するアイドルの slug")
    parser.add_argument("--window-hours", type=float, default=24.0,
                        help="集計窓の長さ（時間、既定 24）。0で全期間。"
                             "短くするほどポアソンノイズが増え順位が読めなくなる")
    args = parser.parse_args()

    idols = {idol["slug"]: idol for idol in json.loads(IDOLS.read_text(encoding="utf-8"))}
    stores = load_stores(args.days, args.date)
    start, end = common_window(stores, args.window_hours or None)

    posts: dict[str, dict] = {}
    for store in stores:
        posts.update(store["posts"])

    authors: dict[str, set[str]] = {slug: set() for slug in idols}
    inconsistent = 0
    used = 0
    for post in posts.values():
        if not (start <= post["created_at"] <= end):
            continue
        slug = post["slug"]
        if slug not in authors:
            continue
        used += 1
        if not post.get("is_consistent", True):
            inconsistent += 1
        authors[slug].add(post["author_id"])

    total = sum(len(users) for users in authors.values())
    if total == 0:
        raise SystemExit("共通窓に投稿がありません。収集間隔を詰めて再取得してください。")

    rows = [{"slug": slug, "name": idols[slug]["name"], "color": idols[slug]["color"],
             "users": len(users)} for slug, users in authors.items()]
    rows.sort(key=lambda row: -row["users"])
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
        row["share"] = row["users"] / total * 100
        # ポアソン計数の95%区間をシェアに換算
        row["margin"] = (Z * math.sqrt(row["users"]) / total * 100) if row["users"] else 0.0
    assign_bands(rows)

    hours = (end - start) / 3600
    win_from = datetime.datetime.fromtimestamp(start, JST)
    win_to = datetime.datetime.fromtimestamp(end, JST)

    print(f"共通窓: {win_from:%m/%d %H:%M} 〜 {win_to:%m/%d %H:%M} JST（{hours:.1f}時間）")
    print(f"投稿 {used:,}件 / ユニーク投稿者 {total:,}人 / 対象 {len(idols)}名")
    print(f"URL・本文の不一致（編集された投稿）: {inconsistent}件"
          f"（{inconsistent/max(used,1)*100:.2f}%）\n")

    print(f'{"順位":<5}{"帯":<4}{"アイドル":<14}{"人数":>6}{"シェア":>9}{"±95%":>8}')
    print("-" * 50)
    for row in rows[:args.top]:
        if row["rank"] - 1 in REWARD_BORDERS:
            print(f'{"":-<20} {row["rank"]-1}位ボーダー {"":-<17}')
        mark = " ←" if row["slug"] == args.focus else ""
        print(f'{row["rank"]:>2}.  {row["band"]:<4}{row["name"]:<14}'
              f'{row["users"]:>6}{row["share"]:>8.2f}%{row["margin"]:>7.2f}{mark}')

    focus = next((row for row in rows if row["slug"] == args.focus), None)
    if focus:
        print(f'\n{focus["name"]}: {focus["rank"]}位 / 帯{focus["band"]} / '
              f'{focus["users"]}人 / シェア{focus["share"]:.2f}%')
        same = [r["name"] for r in rows if r["band"] == focus["band"] and r["slug"] != focus["slug"]]
        print(f'  同じ帯（区別できない相手）: {", ".join(same) if same else "なし"}')
        for border in REWARD_BORDERS:
            if focus["rank"] > border and len(rows) >= border:
                gap = rows[border - 1]["users"] - focus["users"]
                print(f'  {border}位（{rows[border-1]["name"]}）との差: {gap}人')

    print("\n※ この結果は公式シェア投稿から推定した投票人数の代理指標であり、"
          "公式の投票結果でも得票数でもありません。")
    print("※ 同じ帯のアイドル同士は、観測されたばらつきの範囲内で区別できません。"
          "帯をまたがない順位の上下に意味はありません。")

    RANKING.parent.mkdir(parents=True, exist_ok=True)
    RANKING.write_text(json.dumps({
        "generated_at": int(datetime.datetime.now(JST).timestamp()),
        "window": {"start": start, "end": end, "hours": round(hours, 2)},
        "totals": {"posts": used, "unique_authors": total, "inconsistent": inconsistent},
        "ranking": rows,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\n{RANKING.relative_to(ROOT)} に書き出しました。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
