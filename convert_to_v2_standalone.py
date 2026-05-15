#!/usr/bin/env python3
"""
Batch-converts HTML pages to V2 design:
1. Removes old Google Fonts link lines from <head>
2. Replaces <h1 class="sub-title">TEXT</h1> with a <section class="page-hero"> block
"""

import os
import re
import subprocess

# Files to skip (already V2 or special pages)
SKIP_FILES = {
    "/home/user/SugarHeartDB/index.html",
    "/home/user/SugarHeartDB/updates.html",
    "/home/user/SugarHeartDB/SugarHeartHistory.html",
    "/home/user/SugarHeartDB/Mobamas/CinderellaHistory.html",
    "/home/user/SugarHeartDB/Mobamas/PuchiDerela.html",
}

FONT_LINES = [
    r'\s*<link\s+rel="preconnect"\s+href="https://fonts\.googleapis\.com"\s*>\s*\n',
    r'\s*<link\s+rel="preconnect"\s+href="https://fonts\.gstatic\.com"\s+crossorigin\s*>\s*\n',
    r'\s*<link\s+href="https://fonts\.googleapis\.com/css2\?family=Yusei\+Magic[^"]*"\s+rel="stylesheet"\s*>\s*\n',
]

BASE = "/home/user/SugarHeartDB"


def get_rule(filepath):
    """Return (breadcrumb_template, sub_text, summary) for the given file path."""
    # Normalize to relative path from BASE
    rel = filepath[len(BASE):]  # e.g. /Mobamas/ComingTV.html

    # Mobamas/NaganoArea/
    if rel.startswith("/Mobamas/NaganoArea/"):
        return (
            lambda title: f'<a href="/">HOME</a> · <a href="/Mobamas/CardList.html">MOBAMAS</a> · <strong>{title}</strong>',
            "/ BOSS LINES · MOBAMAS",
            "モバマス内の長野エリアボスとして登場する心ちゃんのセリフを掲載しています。",
        )

    # Mobamas/SeasonalEvents/
    if rel.startswith("/Mobamas/SeasonalEvents/"):
        return (
            lambda title: f'<a href="/">HOME</a> · <a href="/Mobamas/CardList.html">MOBAMAS</a> · <strong>{title}</strong>',
            "/ SEASONAL · MOBAMAS",
            "モバマスの季節イベントにおける心ちゃんの登場・セリフをまとめています。",
        )

    # Mobamas/Event/
    if rel.startswith("/Mobamas/Event/"):
        return (
            lambda title: f'<a href="/">HOME</a> · <a href="/Mobamas/CardList.html">MOBAMAS</a> · <a href="/Mobamas/Event/EventList.html">EVENTS</a> · <strong>{title}</strong>',
            "/ EVENT · MOBAMAS",
            "モバマスのイベントにおける心ちゃんの登場・特記事項をまとめています。",
        )

    # Specific Mobamas root files
    mobamas_misc = {
        "/Mobamas/ComingTV.html",
        "/Mobamas/OtherCommu.html",
        "/Mobamas/OtherGameCenter.html",
        "/Mobamas/RefreshRoom.html",
        "/Mobamas/UnitList.html",
    }
    if rel in mobamas_misc:
        return (
            lambda title: f'<a href="/">HOME</a> · <a href="/Mobamas/CardList.html">MOBAMAS</a> · <strong>{title}</strong>',
            "/ MOBAMAS",
            "モバマスにおける心ちゃんの関連コンテンツをまとめたページです。",
        )

    # Deresute/Event/
    if rel.startswith("/Deresute/Event/"):
        return (
            lambda title: f'<a href="/">HOME</a> · <a href="/Deresute/CardList.html">DERESUTE</a> · <a href="/Deresute/Event/EventList.html">EVENTS</a> · <strong>{title}</strong>',
            "/ EVENT · DERESUTE",
            "デレステのイベントにおける心ちゃんの登場・特記事項をまとめています。",
        )

    # Deresute/Common/
    if rel.startswith("/Deresute/Common/"):
        return (
            lambda title: f'<a href="/">HOME</a> · <a href="/Deresute/CardList.html">DERESUTE</a> · <strong>{title}</strong>',
            "/ COMMON COMMU · DERESUTE",
            "デレステの共通コミュにおける心ちゃんのセリフ・登場シーンをまとめています。",
        )

    # Deresute/GuestCommu/
    if rel.startswith("/Deresute/GuestCommu/"):
        return (
            lambda title: f'<a href="/">HOME</a> · <a href="/Deresute/CardList.html">DERESUTE</a> · <strong>{title}</strong>',
            "/ GUEST COMMU · DERESUTE",
            "デレステのゲストコミュにおける心ちゃんの登場シーンをまとめています。",
        )

    # Deresute/Other/
    if rel.startswith("/Deresute/Other/"):
        return (
            lambda title: f'<a href="/">HOME</a> · <a href="/Deresute/CardList.html">DERESUTE</a> · <strong>{title}</strong>',
            "/ OTHER · DERESUTE",
            "デレステのその他コンテンツにおける心ちゃんの登場をまとめています。",
        )

    # Deresute/CostumeList.html
    if rel == "/Deresute/CostumeList.html":
        return (
            lambda title: f'<a href="/">HOME</a> · <a href="/Deresute/CardList.html">DERESUTE</a> · <strong>{title}</strong>',
            "/ COSTUME LIST · DERESUTE",
            "デレステにおける心ちゃんの衣装一覧です。",
        )

    # General/
    if rel.startswith("/General/"):
        return (
            lambda title: f'<a href="/">HOME</a> · <strong>{title}</strong>',
            "/ GENERAL",
            "しゅがーはぁと（佐藤心）の関連情報をまとめたページです。",
        )

    # Popmas/
    if rel.startswith("/Popmas/"):
        return (
            lambda title: f'<a href="/">HOME</a> · <strong>{title}</strong>',
            "/ POPMAS",
            "ポプマスにおける心ちゃんの関連情報をまとめたページです。",
        )

    return None


def build_page_hero(title, breadcrumb_fn, sub, summary):
    breadcrumb = breadcrumb_fn(title)
    return (
        f'\n<section class="page-hero">\n'
        f'    <div class="breadcrumb">{breadcrumb}</div>\n'
        f'    <h1>{title} <span class="sub">{sub}</span></h1>\n'
        f'    <p class="summary">{summary}</p>\n'
        f'</section>'
    )


def convert_file(filepath):
    rule = get_rule(filepath)
    if rule is None:
        print(f"  SKIP (no rule): {filepath}")
        return False

    breadcrumb_fn, sub, summary = rule

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Skip if already V2
    if "page-hero" in content:
        print(f"  SKIP (already v2): {filepath}")
        return False

    # Skip if no h1.sub-title
    if '<h1 class="sub-title">' not in content:
        print(f"  SKIP (no h1.sub-title): {filepath}")
        return False

    original = content

    # Step 1: Remove font link lines (remove each line individually)
    # Handle all three lines together as a block, or individually
    # Use a combined pattern to remove all three in one go (order matters)
    font_block_pattern = re.compile(
        r'[ \t]*<link\s+rel="preconnect"\s+href="https://fonts\.googleapis\.com"\s*>\s*\n'
        r'[ \t]*<link\s+rel="preconnect"\s+href="https://fonts\.gstatic\.com"\s+crossorigin\s*>\s*\n'
        r'[ \t]*<link\s+href="https://fonts\.googleapis\.com/css2\?family=Yusei\+Magic[^"]*"\s+rel="stylesheet"\s*>\s*\n',
        re.MULTILINE,
    )
    content = font_block_pattern.sub("", content)

    # Step 2: Replace <h1 class="sub-title">TEXT</h1> (single or multiline) with page-hero
    # Match h1 that may span multiple lines
    h1_pattern = re.compile(
        r'<h1\s+class="sub-title">(.*?)</h1>',
        re.DOTALL,
    )

    def replace_h1(m):
        title = m.group(1).strip()
        return build_page_hero(title, breadcrumb_fn, sub, summary)

    new_content = h1_pattern.sub(replace_h1, content)

    if new_content == original:
        print(f"  SKIP (no change): {filepath}")
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  CONVERTED: {filepath}")
    return True


def main():
    # Get list of files with h1.sub-title
    result = subprocess.run(
        ["grep", "-rl", '<h1 class="sub-title">', BASE, "--include=*.html"],
        capture_output=True,
        text=True,
    )
    files = sorted(result.stdout.strip().split("\n"))

    converted = []
    skipped = []

    for filepath in files:
        if not filepath:
            continue
        if filepath in SKIP_FILES:
            print(f"  SKIP (explicit): {filepath}")
            skipped.append(filepath)
            continue

        changed = convert_file(filepath)
        if changed:
            converted.append(filepath)
        else:
            skipped.append(filepath)

    print(f"\n=== SUMMARY ===")
    print(f"Converted: {len(converted)}")
    print(f"Skipped:   {len(skipped)}")
    print(f"\nConverted files:")
    for f in converted:
        print(f"  {f}")


if __name__ == "__main__":
    main()
