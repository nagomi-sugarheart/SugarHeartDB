#!/usr/bin/env python3
"""収集データの読み込みと集計を共通化するモジュール。

rank_vote_share.py（4時間おきの速報）と daily_report_vote_share.py（0時の
日次サマリ）が同じ集計規則を使うためのもの。単体では実行しない。

詳細は docs/vote2026-tracking.md を参照。
"""

from __future__ import annotations

import datetime
import json
import urllib.request
import urllib.error
import re
import os
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


def all_sweeps(stores: list[dict]) -> list[dict]:
    """全ストアのスイープを時刻順に並べて返す。

    古い収集データはスイープごとの到達時刻（oldest）を持たないため、
    ストア単位の coverage から擬似的なスイープを1つ組み立てて補う。
    """
    sweeps: list[dict] = []
    for store in stores:
        recorded = store.get("sweeps", [])
        sweeps.extend(sweep for sweep in recorded if "oldest" in sweep)
        # 同じストアに旧形式と新形式が混在しうるので、旧形式ぶんは
        # まとめて擬似スイープ1つに畳む（捨ててはいけない）
        legacy = [sweep for sweep in recorded if "oldest" not in sweep]
        if legacy and store.get("coverage"):
            sweeps.append({
                "collected_at": max(sweep["collected_at"] for sweep in legacy),
                "oldest": store["coverage"],
                "scope": "legacy",
            })
    sweeps.sort(key=lambda sweep: sweep["collected_at"])
    return sweeps


def effective_coverage(stores: list[dict]) -> dict[str, int]:
    """アイドルごとに、欠測なく遡れている最古時刻を返す。

    そのアイドルを対象にしたスイープだけを新しい順にたどり、後のスイープで
    遡れた時刻が前のスイープの実行時刻以前であれば連続しているとみなして
    さらに遡る。そうでなければその間に欠測があるため、そこで打ち切る。

    対象を絞ったスイープ（上位N名だけの高頻度収集）が混ざるため、
    「直前のスイープ」ではなく「そのアイドルを対象にした直前のスイープ」と
    比べなければならない。ここを取り違えると、収集していないアイドルまで
    カバーされたことになってしまう。
    """
    sweeps = all_sweeps(stores)
    per_slug: dict[str, list[tuple[int, int]]] = {}
    for sweep in sweeps:
        for slug, oldest in (sweep.get("oldest") or {}).items():
            per_slug.setdefault(slug, []).append((sweep["collected_at"], oldest))

    floors: dict[str, int] = {}
    for slug, entries in per_slug.items():
        entries.sort()
        floor = entries[-1][1]
        for collected_at, oldest in reversed(entries[:-1]):
            if floor <= collected_at:
                floor = min(floor, oldest)
            else:
                break
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


def coverage_end(stores: list[dict]) -> dict[str, int]:
    """アイドルごとに、最後にそのアイドルを収集した時刻を返す。"""
    ends: dict[str, int] = {}
    for sweep in all_sweeps(stores):
        for slug in sweep.get("oldest") or {}:
            ends[slug] = max(ends.get(slug, 0), sweep["collected_at"])
    return ends


def last_sweep_at(stores: list[dict]) -> int:
    """全アイドルが収集済みである最新時刻。

    対象を絞ったスイープ（上位N名だけの高頻度収集）が混ざるため、単純に
    最後のスイープ時刻を使うと、そこに含まれなかったアイドルだけが
    過少に数えられる。全員の中で最も古い「最終収集時刻」を採る。
    """
    ends = coverage_end(stores)
    if not ends:
        raise SystemExit("sweeps 情報がありません。")
    return min(ends.values())


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


# --- Discordへの送信 ---------------------------------------------------------
# ウェブフックURLは秘密情報で、リポジトリは公開されている。値が例外メッセージや
# トレースバック経由でログに出ると、そのチャンネルに誰でも投稿できるようになる。
# 実際に InvalidURL の例外メッセージからActionsの公開ログへ漏れたことがあるため、
# 読み込みと送信をここに集約し、値が外へ出る経路を1か所に閉じ込めている。

WEBHOOK_RE = re.compile(
    r"^https://(?:discord|discordapp)\.com/api/webhooks/\d+/[A-Za-z0-9_-]+$")


def webhook_url_from_env(var: str = "DISCORD_WEBHOOK_URL") -> str:
    """環境変数からウェブフックURLを読む。値はエラー文にも出さない。"""
    raw = os.environ.get(var, "")
    # 貼り付けやシークレット登録の際に改行や余分な行が混ざることがある。
    # 最初の非空行だけを使い、それが形式に合わなければ落とす。
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if not lines:
        raise SystemExit(
            f"環境変数 {var} が設定されていません。\n"
            f"  export {var}='https://discord.com/api/webhooks/...'\n"
            "URLは秘密情報です。リポジトリには絶対に書き込まないでください。")
    url = lines[0]
    if not WEBHOOK_RE.match(url):
        raise SystemExit(
            f"{var} がDiscordのウェブフックURLの形式ではありません。"
            "改行や余分な文字が混ざっていないか確認してください。"
            "（値そのものは表示しません）")
    return url


def post_json(url: str, payload: dict, user_agent: str) -> None:
    """Discordへ送る。どの失敗経路でもURLを出力しない。"""
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            if res.status not in (200, 204):
                raise SystemExit(f"Discordが status={res.status} を返しました")
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"投稿に失敗しました: HTTP {exc.code} {exc.reason}") from None
    except urllib.error.URLError as exc:
        raise SystemExit(f"投稿に失敗しました: {exc.reason}") from None
    except Exception as exc:
        # InvalidURL のように例外メッセージ自体にURLが載る種類がある。
        # 種別だけを出し、内容は出さない。
        raise SystemExit(
            f"投稿に失敗しました: {type(exc).__name__}"
            "（メッセージにURLが含まれうるため表示しません）") from None
