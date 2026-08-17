#!/usr/bin/env python3
"""シンデレラガール総選挙2026の投票対象アイドル辞書を生成する。

公式サイト（Next.js静的エクスポート）のJSチャンクには、投票対象アイドル全190名の
データがJSON配列としてそのまま埋め込まれている。そこから `idol_code`（投票URLの
スラッグ）と公式表記名の対応を抽出し、`data/idols.json` を生成する。

  投票URL: https://idolmaster-official.jp/cinderellagirls/vote2026/vote/idol/{slug}
  公式シェア文: "{name} さんに投票しました！"

チャンクのファイル名はビルドごとにハッシュが変わるため、ページのHTMLから
参照されているチャンクを毎回動的に探索する。

使い方:
    python scripts/generate_idols_json.py
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

BASE = "https://idolmaster-official.jp"
# アイドル一覧ページ。ここが読み込むチャンクのどれかに辞書が入っている。
ENTRY_PAGES = (
    "/cinderellagirls/vote2026/vote/idol",
    "/cinderellagirls/vote2026/vote",
)
OUTPUT = Path(__file__).resolve().parent.parent / "data" / "idols.json"

EXPECTED_COUNT = 190
UA = "Mozilla/5.0 (compatible; SugarHeartDB/1.0; +https://github.com/nagomi-sugarheart/SugarHeartDB)"

# 埋め込みJSON中の1アイドル分のオブジェクト。id で始まり note で終わる形。
IDOL_OBJECT_RE = re.compile(r'\{"id":"\d+","name":".*?"note":"[^"]*"\}')
CHUNK_RE = re.compile(r'/_next/static/[A-Za-z0-9_/.-]+\.js')

REQUIRED_KEYS = ("id", "name", "kana", "en", "attribute", "idol_code", "colorCode")


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def find_idols() -> list[dict]:
    """エントリページが参照するチャンクを順に走査し、アイドル辞書を見つける。"""
    seen_chunks: set[str] = set()
    for page in ENTRY_PAGES:
        html = fetch(BASE + page)
        for chunk in dict.fromkeys(CHUNK_RE.findall(html)):
            if chunk in seen_chunks:
                continue
            seen_chunks.add(chunk)
            body = fetch(BASE + chunk)
            if '"idol_code"' not in body:
                continue
            found = []
            for match in IDOL_OBJECT_RE.finditer(body):
                try:
                    found.append(json.loads(match.group(0)))
                except json.JSONDecodeError:
                    continue
            if len(found) >= EXPECTED_COUNT:
                print(f"  辞書を検出: {chunk} ({len(found)}件)", file=sys.stderr)
                return found
    raise SystemExit(
        "アイドル辞書を含むJSチャンクが見つかりませんでした。"
        "公式サイトの構成が変わった可能性があります。"
    )


def main() -> None:
    print("公式サイトを走査中...", file=sys.stderr)
    raw = find_idols()

    for entry in raw:
        missing = [key for key in REQUIRED_KEYS if key not in entry]
        if missing:
            raise SystemExit(f"想定外のスキーマです（欠損キー: {missing}）: {entry}")

    by_slug = {entry["idol_code"]: entry for entry in raw}
    if len(by_slug) != len(raw):
        raise SystemExit(f"スラッグが重複しています（{len(raw)}件中{len(by_slug)}件がユニーク）")

    idols = sorted(
        (
            {
                "slug": entry["idol_code"],
                "name": entry["name"],
                "kana": entry["kana"],
                "en": entry["en"],
                "attribute": entry["attribute"],
                "color": entry["colorCode"],
                "official_id": int(entry["id"]),
            }
            for entry in by_slug.values()
        ),
        key=lambda idol: idol["official_id"],
    )

    if len(idols) != EXPECTED_COUNT:
        print(
            f"警告: {EXPECTED_COUNT}名を想定していますが{len(idols)}名を抽出しました。"
            "公式サイト側で対象が変わっていないか確認してください。",
            file=sys.stderr,
        )

    names = [idol["name"] for idol in idols]
    if len(set(names)) != len(names):
        raise SystemExit("公式表記名が重複しています。本文パースでの識別ができません。")

    # 本文テキストでの集計時、ある名前が別の名前の部分文字列だと誤カウントする。
    collisions = [(a, b) for a in names for b in names if a != b and a in b]
    if collisions:
        print(f"警告: 名前の部分文字列衝突があります: {collisions}", file=sys.stderr)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(idols, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"{len(idols)}名を {OUTPUT.relative_to(OUTPUT.parent.parent)} に書き出しました。", file=sys.stderr)


if __name__ == "__main__":
    main()
