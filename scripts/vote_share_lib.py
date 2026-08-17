#!/usr/bin/env python3
"""収集データの読み込みと集計を共通化するモジュール。

rank_vote_share.py（4時間おきの速報）と daily_report_vote_share.py（0時の
日次サマリ）が同じ集計規則を使うためのもの。単体では実行しない。

詳細は docs/vote2026-tracking.md を参照。
"""

from __future__ import annotations

import datetime
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDOLS = ROOT / "data" / "idols.json"
OUTDIR = ROOT / "data" / "vote2026"

JST = datetime.timezone(datetime.timedelta(hours=9))
Z = 1.96  # 95%
# 報酬の段階閾値（docs/vote2026-tracking.md §1.2）
REWARD_BORDERS = (5, 7, 15)


def load_idols() -> dict:
    return {idol["slug"]: idol for idol in json.loads(IDOLS.read_text(encoding="utf-8"))}


def load_stores(dates: list[str] | None = None, days: int | None = None) -> list[dict]:
    """収集データを日付順に読み込む。"""
    if dates:
        paths = [OUTDIR / f"{date}.json" for date in dates]
    else:
        paths = sorted(OUTDIR.glob("????-??-??.json"))
        if days:
            paths = paths[-days:]
    stores = [json.loads(path.read_text(encoding="utf-8")) for path in paths if path.exists()]
    if not stores:
        raise SystemExit(
            "集計対象のデータがありません。先に collect_vote_share.py を実行してください。")
    stores.sort(key=lambda store: store["date"])
    return stores


def effective_coverage(stores: list[dict]) -> dict[str, int]:
    """アイドルごとに、欠測なく遡れている最古時刻を返す。

    ストアをまたぐ場合、後のストアで遡れた時刻が前のストアの最終スイープ時刻
    以前であれば連続しているとみなして前のストアまで遡る。そうでなければ
    その間に欠測があるため、そこで打ち切る。日付ファイルの境界と収集の
    タイミングは一致しないので、この判定なしに複数日をまたぐと窓を
    誤る（保守的すぎるか、逆に欠測を見落とす）。
    """
    ordered = sorted(stores, key=lambda store: store["date"])
    last_sweep = [
        max((sweep["collected_at"] for sweep in store.get("sweeps", [])), default=None)
        for store in ordered
    ]
    slugs = {slug for store in ordered for slug in store.get("coverage", {})}

    floors: dict[str, int] = {}
    for slug in slugs:
        floor = None
        for index in range(len(ordered) - 1, -1, -1):
            covered = ordered[index].get("coverage", {}).get(slug)
            if covered is None:
                continue
            if floor is None:
                floor = covered
                continue
            # ひとつ前のストアの最終スイープまで届いていれば連続している
            if last_sweep[index] is not None and floor <= last_sweep[index]:
                floor = min(floor, covered)
            else:
                break
        if floor is not None:
            floors[slug] = floor
    return floors


def saturated_slugs(stores: list[dict]) -> set[str]:
    """取りこぼしの疑いが記録されたアイドル。"""
    return {
        slug
        for store in stores
        for sweep in store.get("sweeps", [])
        for slug in sweep.get("saturated", [])
    }


def last_sweep_at(stores: list[dict]) -> int:
    ends = [sweep["collected_at"] for store in stores for sweep in store.get("sweeps", [])]
    if not ends:
        raise SystemExit("sweeps 情報がありません。")
    return max(ends)


def merge_posts(stores: list[dict]) -> dict:
    posts: dict[str, dict] = {}
    for store in stores:
        posts.update(store["posts"])
    return posts


def count_authors(posts: dict, idols: dict, start: int, end: int):
    """窓内のアイドル別ユニーク投稿者数を数える。"""
    authors: dict[str, set] = {slug: set() for slug in idols}
    used = 0
    inconsistent = 0
    for post in posts.values():
        if not (start <= post["created_at"] < end):
            continue
        slug = post["slug"]
        if slug not in authors:
            continue
        used += 1
        if not post.get("is_consistent", True):
            inconsistent += 1
        authors[slug].add(post["author_id"])
    return {slug: len(users) for slug, users in authors.items()}, used, inconsistent


def distinguishable(count_a: int, count_b: int) -> bool:
    """2つの計数がポアソンノイズを超えて有意に違うか。"""
    if count_a + count_b == 0:
        return False
    return abs(count_a - count_b) > Z * math.sqrt(count_a + count_b)


def build_rows(counts: dict[str, int], idols: dict) -> list[dict]:
    """順位・シェア・取りうる順位を付けた行を返す。

    表示順の隣にある順位差の多くは意味がない。投稿の到着はポアソン過程なので、
    件数差が小さいアイドル同士は観測期間内では区別できないためである。
    自分より有意に多いアイドルの数から最良順位、有意に少ないアイドルの数から
    最悪順位を決め、その幅を不確かさとして示す。
    """
    total = sum(counts.values())
    rows = [
        {"slug": slug, "name": idols[slug]["name"], "color": idols[slug]["color"],
         "users": counts.get(slug, 0)}
        for slug in idols
    ]
    rows.sort(key=lambda row: -row["users"])
    values = [row["users"] for row in rows]
    for rank, row in enumerate(rows, 1):
        row["rank"] = rank
        row["share"] = row["users"] / total * 100 if total else 0.0
        row["margin"] = (Z * math.sqrt(row["users"]) / total * 100) if total and row["users"] else 0.0
        mine = row["users"]
        above = sum(1 for other in values if other > mine and distinguishable(other, mine))
        below = sum(1 for other in values if other < mine and distinguishable(other, mine))
        row["rank_best"] = above + 1
        row["rank_worst"] = len(values) - below
    return rows


def jst_day_bounds(day: datetime.date) -> tuple[int, int]:
    start = datetime.datetime.combine(day, datetime.time.min, tzinfo=JST)
    return int(start.timestamp()), int((start + datetime.timedelta(days=1)).timestamp())


def fmt(ts: int, pattern: str = "%m/%d %H:%M") -> str:
    return datetime.datetime.fromtimestamp(ts, JST).strftime(pattern)
