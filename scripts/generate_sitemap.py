#!/usr/bin/env python3
"""
generate_sitemap.py
サイト内のすべてのHTMLページを走査して sitemap.xml を生成するスクリプト。

- リポジトリ内の *.html を再帰的に収集する。
- <meta name="robots" content="...noindex..."> を含むページは除外する。
- URL は GitHub Pages の公開URL（BASE_URL）を基準に生成する。
- index.html はディレクトリURL（末尾スラッシュ）に正規化する。
- lastmod には各ファイルの Git 最終コミット日（YYYY-MM-DD）を使う。
  （Git 情報が取れない場合はファイルの更新日時にフォールバック）

使い方:
  python generate_sitemap.py

ページを追加・削除・大幅更新したら、このスクリプトを再実行して
sitemap.xml を更新すること。
"""

import os
import re
import glob
import subprocess
from datetime import datetime, timezone
from xml.sax.saxutils import escape

# このスクリプトは scripts/ 配下にあるため、リポジトリ直下を親ディレクトリとして参照する
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# GitHub Pages の公開URL（末尾スラッシュ必須）
BASE_URL = "https://nagomi-sugarheart.github.io/SugarHeartDB/"

OUTPUT_FILE = os.path.join(BASE_DIR, "sitemap.xml")

# 走査対象から除外するディレクトリ（先頭一致）
EXCLUDE_DIRS = (".git", "node_modules", "__pycache__")

# ファイル名で除外するもの（部分HTML・テンプレート等があればここに追加）
EXCLUDE_FILES = set()

NOINDEX_RE = re.compile(
    r'<meta[^>]+name=["\']robots["\'][^>]+content=["\'][^"\']*noindex',
    re.IGNORECASE,
)


def collect_html_files():
    """リポジトリ内のHTMLファイル（相対パス）を返す。"""
    files = []
    for path in glob.glob(os.path.join(BASE_DIR, "**", "*.html"), recursive=True):
        rel = os.path.relpath(path, BASE_DIR)
        parts = rel.split(os.sep)
        if parts[0] in EXCLUDE_DIRS:
            continue
        if os.path.basename(rel) in EXCLUDE_FILES:
            continue
        files.append(rel)
    return sorted(files)


def is_noindex(path):
    """robots メタタグに noindex を含むページかどうか。"""
    try:
        with open(path, encoding="utf-8") as f:
            head = f.read(4096)
    except OSError:
        return False
    return bool(NOINDEX_RE.search(head))


def to_url(rel_path):
    """相対パスを公開URLに変換する。index.html はディレクトリURLに正規化。"""
    url_path = rel_path.replace(os.sep, "/")
    if url_path == "index.html":
        url_path = ""
    elif url_path.endswith("/index.html"):
        url_path = url_path[: -len("index.html")]  # 末尾スラッシュを残す
    return BASE_URL + url_path


def git_lastmod(rel_path):
    """Git の最終コミット日（YYYY-MM-DD）。取れなければファイル更新日。"""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel_path],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        date = out.stdout.strip()
        if date:
            return date
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    ts = os.path.getmtime(os.path.join(BASE_DIR, rel_path))
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def priority_for(url):
    """URLの階層の浅さからおおまかな優先度を決める（任意項目）。"""
    if url == BASE_URL:
        return "1.0"
    depth = url[len(BASE_URL):].strip("/").count("/")
    if depth == 0:
        return "0.8"
    if depth == 1:
        return "0.6"
    return "0.5"


def main():
    files = collect_html_files()
    entries = []
    for rel in files:
        abs_path = os.path.join(BASE_DIR, rel)
        if is_noindex(abs_path):
            continue
        url = to_url(rel)
        entries.append((url, git_lastmod(rel), priority_for(url)))

    # ルート（トップページ）を先頭に、あとはURL順で安定出力
    entries.sort(key=lambda e: (e[0] != BASE_URL, e[0]))

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url, lastmod, priority in entries:
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(url)}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"生成完了: {OUTPUT_FILE}")
    print(f"URL件数: {len(entries)} 件（除外 noindex 含む走査 {len(files)} ファイル）")


if __name__ == "__main__":
    main()
