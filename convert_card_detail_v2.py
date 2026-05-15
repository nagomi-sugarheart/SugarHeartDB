#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_card_detail_v2.py
Mobamas/Deresute カード詳細HTMLをV2デザインに変換するスクリプト
"""

import os
import re
import json
from pathlib import Path

REPO_ROOT = Path('/home/user/SugarHeartDB')

# 変換対象ファイル一覧
MOBAMAS_FILES = [
    'Mobamas/6thAnniversary+/6thAnniversary+.html',
    'Mobamas/6thAnniversary+/6thAnniversaryS+.html',
    'Mobamas/6thAnniversary/6thAnniversary.html',
    'Mobamas/6thAnniversary/6thAnniversaryS.html',
    'Mobamas/AngelHeart+/AngelHeart+.html',
    'Mobamas/AngelHeart/AngelHeart.html',
    'Mobamas/BrilliantHeart+/BrilliantHeart+.html',
    'Mobamas/BrilliantHeart/BrilliantHeart.html',
    'Mobamas/ChikuttoSweetie+/ChikuttoSweetie+.html',
    'Mobamas/ChikuttoSweetie/ChikuttoSweetie.html',
    'Mobamas/FallingHeart+/FallingHeart+.html',
    'Mobamas/FallingHeart/FallingHeart.html',
    'Mobamas/HeartModel+/HeartModel+.html',
    'Mobamas/HeartModel+/HeartModelS+.html',
    'Mobamas/HeartModel/HeartModel.html',
    'Mobamas/HeartModel/HeartModelS.html',
    'Mobamas/HeartNoYomeiri+/HeartNoYomeiri+.html',
    'Mobamas/HeartNoYomeiri/HeartNoYomeiri.html',
    'Mobamas/MerryChristmasHeart+/MerryChristmasHeart+.html',
    'Mobamas/MerryChristmasHeart/MerryChristmasHeart.html',
    'Mobamas/NatsuiroHeart+/NatsuiroHeart+.html',
    'Mobamas/NatsuiroHeart/NatsuiroHeart.html',
    'Mobamas/ShinshunHeartful+/ShinshunHeartful+.html',
    'Mobamas/ShinshunHeartful/ShinshunHeartful.html',
    'Mobamas/StylishHeart+/StylishHeart+.html',
    'Mobamas/StylishHeart/StylishHeart.html',
    'Mobamas/SweetieNewYear+/SweetieNewYear+.html',
    'Mobamas/SweetieNewYear/SweetieNewYear.html',
    'Mobamas/SweetieRoyal+/SweetieRoyal+.html',
    'Mobamas/SweetieRoyal/SweetieRoyal.html',
    'Mobamas/TokonatsuParadise+/TokonatsuParadise+.html',
    'Mobamas/TokonatsuParadise/TokonatsuParadise.html',
    'Mobamas/WorkingSweetie+/WorkingSweetie+.html',
    'Mobamas/WorkingSweetie/WorkingSweetie.html',
    'Mobamas/SatoShin+/SatoShin+.html',
    'Mobamas/SatoShin/SatoShin.html',
    'Mobamas/TBSweetie+/TBSweetie+.html',
    'Mobamas/TBSweetie/TBSweetie.html',
    'Mobamas/NextStarIC+/NextStarIC+.html',
]

DERESUTE_FILES = [
    'Deresute/AisareQueenHeart+/AisareQueenHeart+.html',
    'Deresute/AisareQueenHeart/AisareQueenHeart.html',
    'Deresute/BrilliantHeart+/BrilliantHeart+.html',
    'Deresute/BrilliantHeart/BrilliantHeart.html',
    'Deresute/CoCoNatsuNatsuNatsuHoliday+/CoCoNatsuNatsuNatsuHoliday+.html',
    'Deresute/CoCoNatsuNatsuNatsuHoliday/CoCoNatsuNatsuNatsuHoliday.html',
    'Deresute/DancingDead+/DancingDead+.html',
    'Deresute/DancingDead/DancingDead.html',
    'Deresute/DekobokoSpeedStar+/DekobokoSpeedStar+.html',
    'Deresute/DekobokoSpeedStar/DekobokoSpeedStar.html',
    'Deresute/DokonjyoReporter+/DokonjyoReporter+.html',
    'Deresute/DokonjyoReporter/DokonjyoReporter.html',
    'Deresute/GoJustGo+/GoJustGo+.html',
    'Deresute/GoJustGo/GoJustGo.html',
    'Deresute/HappyNewYeah+/HappyNewYeah+.html',
    'Deresute/HappyNewYeah/HappyNewYeah.html',
    'Deresute/HeartModel+/HeartModel+.html',
    'Deresute/HeartModel/HeartModel.html',
    'Deresute/HeartNoYomeiri+/HeartNoYomeiri+.html',
    'Deresute/HeartNoYomeiri/HeartNoYomeiri.html',
    'Deresute/HeartToHeart+/HeartToHeart+.html',
    'Deresute/HeartToHeart/HeartToHeart.html',
    'Deresute/HeartfulSweeteenSatoShin+/HeartfulSweeteenSatoShin+.html',
    'Deresute/HeartfulSweeteenSatoShin/HeartfulSweeteenSatoShin.html',
    'Deresute/KoisuruSweetieSummer+/KoisuruSweetieSummer+.html',
    'Deresute/KoisuruSweetieSummer/KoisuruSweetieSummer.html',
    'Deresute/KonoyoDeTadaHitoriNoHeart+/KonoyoDeTadaHitoriNoHeart+.html',
    'Deresute/KonoyoDeTadaHitoriNoHeart/KonoyoDeTadaHitoriNoHeart.html',
    'Deresute/LuxuryHeart+/LuxuryHeart+.html',
    'Deresute/LuxuryHeart/LuxuryHeart.html',
    'Deresute/ManatsunoHeartMeetsHeart+/ManatsunoHeartMeetsHeart+.html',
    'Deresute/ManatsunoHeartMeetsHeart/ManatsunoHeartMeetsHeart.html',
    'Deresute/OdoruFlagship+/OdoruFlagship+.html',
    'Deresute/OdoruFlagship/OdoruFlagship.html',
    'Deresute/OrderMadeHeart+/OrderMadeHeart+.html',
    'Deresute/OrderMadeHeart/OrderMadeHeart.html',
    'Deresute/SatoShin+/SatoShin+.html',
    'Deresute/SatoShin/SatoShin.html',
    'Deresute/DokonjoReporter+/DokonjoReporter+.html',
    'Deresute/DokonjoReporter/DokonjoReporter.html',
]


def read_file(filepath):
    """Read from git HEAD (original), falling back to disk if not in git."""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'show', f'HEAD:{filepath}'],
            capture_output=True, text=True, encoding='utf-8',
            cwd=str(REPO_ROOT)
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except Exception:
        pass
    # fallback to disk
    with open(REPO_ROOT / filepath, 'r', encoding='utf-8') as f:
        return f.read()


def extract_card_name(html):
    """breadcrumbの<strong>タグの中身"""
    m = re.search(r'<div class="breadcrumb"[^>]*>.*?<strong>(.*?)</strong>', html, re.DOTALL)
    if m:
        name = m.group(1).strip()
        # Remove trailing garbage like " カード詳細｜SugarHeartDB"
        name = re.sub(r'\s*[- ]+カード詳細.*', '', name)
        name = re.sub(r'\s*｜.*', '', name)
        return name.strip()
    # fallback: page-hero内
    m = re.search(r'<section class="page-hero"[^>]*>.*?<strong>(.*?)</strong>', html, re.DOTALL)
    if m:
        name = m.group(1).strip()
        name = re.sub(r'\s*[- ]+カード詳細.*', '', name)
        name = re.sub(r'\s*｜.*', '', name)
        return name.strip()
    # fallback: h1 in sub-title
    m = re.search(r'<div class="sub-title">\s*<h1>(.*?)</h1>', html, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ''


def extract_card_date(html):
    """sub-title-dateの中身"""
    m = re.search(r'<span class="sub-title-date">(.*?)</span>', html)
    if m:
        return m.group(1).strip()
    return ''


def extract_card_images(html):
    """const cardImages = [...] 配列"""
    m = re.search(r'const cardImages\s*=\s*(\[.*?\]);', html, re.DOTALL)
    if m:
        arr_str = m.group(1)
        # Extract quoted strings
        items = re.findall(r"['\"]([^'\"]+)['\"]", arr_str)
        return items
    return []


def extract_nav_card(html, nav_class):
    """nav-prev or nav-next の情報を抽出"""
    pattern = r'<a\s+href="([^"]+)"\s+class="nav-card\s+' + nav_class + r'"[^>]*>.*?<img\s+src="([^"]+)"[^>]*>.*?<span class="nav-card-name">(.*?)</span>'
    m = re.search(pattern, html, re.DOTALL)
    if m:
        return {'href': m.group(1), 'img': m.group(2), 'name': m.group(3).strip()}
    # Also try reversed attribute order
    pattern2 = r'<a\s+class="nav-card\s+' + nav_class + r'"\s+href="([^"]+)"[^>]*>.*?<img\s+src="([^"]+)"[^>]*>.*?<span class="nav-card-name">(.*?)</span>'
    m = re.search(pattern2, html, re.DOTALL)
    if m:
        return {'href': m.group(1), 'img': m.group(2), 'name': m.group(3).strip()}
    return None


def extract_accordion_items(html):
    """accordion-itemブロックごとに(label, content_html)を抽出"""
    items = []
    # Find the first dialogue-tab-content (the text tab)
    text_tab_m = re.search(r'<div class="dialogue-tab-content dialogue-content1">(.*?)</div>\s*\n\s*<!-- タブ2', html, re.DOTALL)
    if not text_tab_m:
        text_tab_m = re.search(r'<div class="dialogue-tab-content dialogue-content1">(.*?)<!-- タブ2', html, re.DOTALL)
    if not text_tab_m:
        # Try to find within dialogue area
        text_tab_m = re.search(r'<div class="dialogue-tab-content dialogue-content1">(.*?)</div>\s*\n\s*</div>\s*\n\s*<!-- タブ2', html, re.DOTALL)

    if text_tab_m:
        content = text_tab_m.group(1)
    else:
        content = html

    # Find all accordion-item blocks
    accord_blocks = re.findall(r'<div class="accordion-item">(.*?)</div>\s*(?=\s*(?:<div class="accordion-item">|</div>))', content, re.DOTALL)
    if not accord_blocks:
        accord_blocks = re.findall(r'<div class="accordion-item">(.*?)</div>\s*\n\s*(?=\s*(?:<div class="accordion-item">|</div>|\s*$))', content, re.DOTALL)

    if not accord_blocks:
        # Try another approach: find accordion-items by splitting
        splits = re.split(r'(?=<div class="accordion-item">)', content)
        for s in splits:
            if '<div class="accordion-item">' in s:
                accord_blocks.append(s)

    for block in accord_blocks:
        # Extract label: the first <span> in <label for="accordion?">
        label_m = re.search(r'<label[^>]*>\s*<span>(.*?)</span>', block, re.DOTALL)
        label = label_m.group(1).strip() if label_m else ''

        # Extract accordion-inner content
        inner_m = re.search(r'<div class="accordion-inner">(.*?)</div>\s*</div>\s*</div>', block, re.DOTALL)
        if not inner_m:
            inner_m = re.search(r'<div class="accordion-inner">(.*?)</div>\s*</div>', block, re.DOTALL)
        if not inner_m:
            inner_m = re.search(r'<div class="accordion-inner">(.*)', block, re.DOTALL)

        content_html = inner_m.group(1).strip() if inner_m else ''
        items.append((label, content_html))

    return items


def extract_gallery_imgs(html):
    """image-scroll-area内のimg src"""
    m = re.search(r'<div class="image-scroll-area">(.*?)</div>', html, re.DOTALL)
    if not m:
        return []
    area = m.group(1)
    return re.findall(r'<img\s+src="([^"]+)"', area)


def extract_theater_img(html):
    """theater-accordion-content内のimg src"""
    m = re.search(r'<div class="theater-accordion-content">(.*?)</div>', html, re.DOTALL)
    if not m:
        return None
    area = m.group(1)
    img_m = re.search(r'<img\s+src="([^"]+)"', area)
    return img_m.group(1) if img_m else None


def extract_related_links(html):
    """link-list内のa要素"""
    m = re.search(r'<div class="link-list">(.*?)</div>', html, re.DOTALL)
    if not m:
        return []
    area = m.group(1)
    links = []
    for am in re.finditer(r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>', area, re.DOTALL):
        href = am.group(1)
        text = re.sub(r'<[^>]+>', '', am.group(2)).strip()
        # Remove leading ▶
        text = re.sub(r'^▶\s*', '', text)
        links.append({'href': href, 'text': text})
    return links


def extract_box_items(html):
    """カード性能のbox-area内のbox-item"""
    # Find the カード性能 heading position
    start_marker = '<h3 class="box-title">カード性能</h3>'
    start_idx = html.find(start_marker)
    if start_idx == -1:
        return []

    # Extract area from that point to next box-area or 関連ページ
    area_html = html[start_idx:]

    # Find all box-items in this area (stop at 関連ページ or next major section)
    end_markers = ['<!-- 関連', '<h3 class="box-title">関連', '</div>\n            \n        </div>']
    end_idx = len(area_html)
    for marker in end_markers:
        idx = area_html.find(marker)
        if idx != -1 and idx < end_idx:
            end_idx = idx

    area = area_html[:end_idx]

    items = []
    for bm in re.finditer(r'<div class="box-item">\s*<span class="box-subtitle">(.*?)</span>\s*<span class="box-text">(.*?)</span>\s*</div>', area, re.DOTALL):
        subtitle = bm.group(1).strip()
        text = bm.group(2).strip()
        items.append({'subtitle': subtitle, 'text': text})
    return items


def extract_sidebar_items(html, current_rel_path):
    """sidebar-cardlist内のa要素"""
    m = re.search(r'<aside class="sidebar-cardlist">(.*?)</aside>', html, re.DOTALL)
    if not m:
        return []
    area = m.group(1)
    items = []
    for am in re.finditer(r'<a\s+href="([^"]+)"(?:\s+class="([^"]*)")?[^>]*>(.*?)</a>', area, re.DOTALL):
        href = am.group(1)
        cls = am.group(2) or ''
        text = re.sub(r'<[^>]+>', '', am.group(3)).strip()
        is_active = 'active' in cls or href == current_rel_path
        items.append({'href': href, 'text': text, 'is_active': is_active})
    return items


def transform_accordion_content(content_html):
    """accordion-inner の中身を変換:
    <h2 class="box-title">TEXT</h2> -> <div class="accord-sub">TEXT</div>
    """
    result = re.sub(
        r'<h2 class="box-title">(.*?)</h2>',
        r'<div class="accord-sub">\1</div>',
        content_html
    )
    return result


def build_sidebar_html(sidebar_items):
    lines = []
    for item in sidebar_items:
        href = item['href']
        text = item['text']
        is_active = item['is_active']
        active_class = ' active' if is_active else ''

        # Generate icon path
        icon_path = href.replace('.html', 'Icon.jpg')
        icon_full = REPO_ROOT / icon_path

        if icon_full.exists():
            img_tag = f'                <img class="sb-icon" src="{icon_path}" alt="">\n'
        else:
            img_tag = ''

        lines.append(f'            <a class="sb-item{active_class}" href="{href}">')
        if img_tag:
            lines.append(f'                <img class="sb-icon" src="{icon_path}" alt="">')
        lines.append(f'                <div class="nm">{text}</div>')
        lines.append(f'            </a>')

    return '\n'.join(lines)


def build_nav_cards_html(nav_prev, nav_next):
    if not nav_prev and not nav_next:
        return ''

    lines = ['        <nav class="v2-card-nav">']

    if nav_prev:
        lines.append(f'            <a class="v2-nav-card" href="{nav_prev["href"]}">')
        lines.append(f'                <span class="v2-nav-arrow">←</span>')
        lines.append(f'                <img class="v2-nav-icon" src="{nav_prev["img"]}" alt="">')
        lines.append(f'                <div>')
        lines.append(f'                    <div class="v2-nav-label">前のカード</div>')
        lines.append(f'                    <div class="v2-nav-name">{nav_prev["name"]}</div>')
        lines.append(f'                </div>')
        lines.append(f'            </a>')

    if nav_next:
        lines.append(f'            <a class="v2-nav-card v2-nav-next" href="{nav_next["href"]}">')
        lines.append(f'                <div>')
        lines.append(f'                    <div class="v2-nav-label">次のカード</div>')
        lines.append(f'                    <div class="v2-nav-name">{nav_next["name"]}</div>')
        lines.append(f'                </div>')
        lines.append(f'                <img class="v2-nav-icon" src="{nav_next["img"]}" alt="">')
        lines.append(f'                <span class="v2-nav-arrow">→</span>')
        lines.append(f'            </a>')

    lines.append('        </nav>')
    return '\n'.join(lines)


def build_accordions_html(accordion_items):
    lines = []
    for i, (label, content_html) in enumerate(accordion_items):
        is_first = (i == 0)
        open_class = ' open' if is_first else ''
        transformed = transform_accordion_content(content_html)
        lines.append(f'                <div class="v2-accord{open_class}">')
        lines.append(f'                    <div class="v2-accord-head">')
        lines.append(f'                        <span class="v2-accord-lbl">{label}</span>')
        lines.append(f'                        <span class="v2-accord-arrow">▾</span>')
        lines.append(f'                    </div>')
        lines.append(f'                    <div class="v2-accord-body">')
        lines.append(f'                        {transformed}')
        lines.append(f'                    </div>')
        lines.append(f'                </div>')
    return '\n'.join(lines)


def build_box_items_html(box_items):
    lines = []
    for item in box_items:
        lines.append(f'                    <div class="v2-meta-row"><span class="v2-meta-k">{item["subtitle"]}</span><span class="v2-meta-v">{item["text"]}</span></div>')
    return '\n'.join(lines)


def build_theater_html(theater_img):
    if not theater_img:
        return ''
    return f'''        <section class="v2-theater">
            <h2>シンデレラガールズ劇場</h2>
            <img src="{theater_img}" alt="シンデレラガールズ劇場">
        </section>'''


def build_gallery_html_section(gallery_imgs, card_name):
    if not gallery_imgs:
        return ''
    lines = ['        <section class="v2-gallery">']
    lines.append('            <h2>関連ギャラリー</h2>')
    lines.append('            <div class="gallery-scroll">')
    for src in gallery_imgs:
        lines.append(f'                <img class="gallery-img" src="{src}" alt="{card_name}">')
    lines.append('            </div>')
    lines.append('        </section>')
    return '\n'.join(lines)


def build_related_html(related_links):
    if not related_links:
        return ''
    lines = ['        <section class="v2-related">']
    lines.append('            <h2>関連ページ</h2>')
    lines.append('            <div class="v2-related-links">')
    for link in related_links:
        lines.append(f'                <a href="{link["href"]}">{link["text"]}</a>')
    lines.append('            </div>')
    lines.append('        </section>')
    return '\n'.join(lines)


def build_card_images_js(card_images):
    items = [f"'{img}'" for img in card_images]
    return '[' + ', '.join(items) + ']'


def convert_file(rel_path):
    full_path = REPO_ROOT / rel_path
    if not full_path.exists():
        print(f'  [SKIP] File not found: {rel_path}')
        return False

    # Skip CommonCommu.html
    if 'Common/CommonCommu.html' in rel_path:
        print(f'  [SKIP] Excluded: {rel_path}')
        return False

    html = read_file(rel_path)

    # Determine game type
    if rel_path.startswith('Mobamas/'):
        game_type = 'Mobamas'
        game_label = 'MOBAMAS'
        game_url = 'Mobamas/index.html'
    else:
        game_type = 'Deresute'
        game_label = 'DERESUTE'
        game_url = 'Deresute/index.html'

    # Extract data
    card_name = extract_card_name(html)
    card_date = extract_card_date(html)
    card_images = extract_card_images(html)
    nav_prev = extract_nav_card(html, 'nav-prev')
    nav_next = extract_nav_card(html, 'nav-next')
    accordion_items = extract_accordion_items(html)
    gallery_imgs = extract_gallery_imgs(html)
    theater_img = extract_theater_img(html)
    related_links = extract_related_links(html)
    box_items = extract_box_items(html)
    sidebar_items = extract_sidebar_items(html, rel_path)

    # Fallbacks
    if not card_images:
        # Try to find from first image in card-image-area
        m = re.search(r'<div class="card-image-area">\s*<img\s+src="([^"]+)"', html)
        if m:
            card_images = [m.group(1)]

    first_image = card_images[0] if card_images else ''
    image_count = len(card_images)
    card_count = len(sidebar_items)

    # Build HTML parts
    sidebar_html = build_sidebar_html(sidebar_items)
    nav_cards_html = build_nav_cards_html(nav_prev, nav_next)
    accordions_html = build_accordions_html(accordion_items)
    box_items_html = build_box_items_html(box_items)
    theater_html = build_theater_html(theater_img)
    gallery_html_section = build_gallery_html_section(gallery_imgs, card_name)
    related_html = build_related_html(related_links)
    card_images_js = build_card_images_js(card_images)

    # Build full HTML
    output = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
\t<base href="/SugarHeartDB/">
\t<meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{card_name}｜SugarHeartDB</title>
    <meta name="description" content="アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）{card_name}のカード詳細ページです。">
    <meta name="author" content="なごみ（@nagomi_IMCG）">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{card_name}｜SugarHeartDB">
    <meta property="og:description" content="アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）{card_name}のカード詳細ページです。">
    <meta property="og:site_name" content="SugarHeartDB">
    <meta property="og:image" content="https://nagomi-sugarheart.github.io/SugarHeartDB/{first_image}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="SugarHeartDB">
    <link rel="icon" type="image/png" sizes="32x32" href="Favicon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="Favicon/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="Favicon/apple-touch-icon.png">
    <link rel="stylesheet" href="style.css">
</head>
<body>
<script src="components/header.js"></script>

<div class="v2-detail-layout">

    <aside class="v2-sidebar">
        <h3>カード一覧 <span class="sb-count">{card_count}</span></h3>
        <div class="sb-list">
{sidebar_html}
        </div>
    </aside>

    <main class="v2-detail-main">

        <div class="v2-title-block">
            <div class="v2-breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <a href="{game_url}">{game_label}</a> · <strong>{card_name}</strong></div>
            <h1>{card_name} <span class="v2-date">{card_date}</span></h1>
        </div>

{nav_cards_html}

        <section class="v2-card-hero">
            <div class="v2-main-img-area">
                <img src="{first_image}" alt="{card_name}" id="v2-card-main-img">
                <p class="v2-img-hint">タップで切り替え（<span id="v2-img-counter">1</span> / <span id="v2-img-total">{image_count}</span>）</p>
            </div>
            <div class="v2-meta-panel">
                <h2>カード情報</h2>
                <div class="v2-meta-grid">
{box_items_html}
                </div>
            </div>
        </section>

        <section class="v2-dialogue-block">
            <div class="v2-dialogue-tabs">
                <button class="v2-dialogue-tab active" onclick="v2SwitchTab(0,this)">セリフ（テキスト）</button>
                <button class="v2-dialogue-tab" onclick="v2SwitchTab(1,this)">セリフ（画像）</button>
            </div>
            <div class="v2-dialogue-content">
{accordions_html}
            </div>
            <div class="v2-dialogue-content" style="display:none">
                <p style="color:var(--sh-text-mute);padding:20px 0;font-size:14px;">画像のご提供を募集しております。</p>
            </div>
        </section>

{theater_html}

{gallery_html_section}

{related_html}

{nav_cards_html}

    </main>
</div>

<script>
const v2CardImages = {card_images_js};
let v2ImgIdx = 0;
(function(){{
    const img = document.getElementById('v2-card-main-img');
    const counter = document.getElementById('v2-img-counter');
    const total = document.getElementById('v2-img-total');
    if(total) total.textContent = v2CardImages.length;
    if(img && v2CardImages.length > 1){{
        img.style.cursor = 'pointer';
        img.addEventListener('click', function(){{
            v2ImgIdx = (v2ImgIdx + 1) % v2CardImages.length;
            img.style.opacity = '0.5';
            setTimeout(function(){{
                img.src = v2CardImages[v2ImgIdx];
                img.style.opacity = '1';
                if(counter) counter.textContent = v2ImgIdx + 1;
            }}, 150);
        }});
    }}
    // accordion toggle
    document.querySelectorAll('.v2-accord-head').forEach(function(h){{
        h.addEventListener('click', function(){{
            h.parentElement.classList.toggle('open');
        }});
    }});
}}());
function v2SwitchTab(idx, btn){{
    var tabs = btn.parentElement.querySelectorAll('.v2-dialogue-tab');
    var contents = btn.closest('.v2-dialogue-block').querySelectorAll('.v2-dialogue-content');
    tabs.forEach(function(t){{ t.classList.remove('active'); }});
    contents.forEach(function(c){{ c.style.display='none'; }});
    btn.classList.add('active');
    contents[idx].style.display = '';
}}
</script>
</body>
</html>'''

    # Write output
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f'  [OK] {rel_path}')
    return True


def main():
    all_files = []

    # Read from list files if they exist, otherwise use hardcoded lists
    mobamas_txt = Path('/tmp/mobamas_cards.txt')
    deresute_txt = Path('/tmp/deresute_cards.txt')

    if mobamas_txt.exists():
        with open(mobamas_txt) as f:
            mobamas_files = [
                line.strip().replace('/home/user/SugarHeartDB/', '')
                for line in f if line.strip() and '.html' in line
            ]
    else:
        mobamas_files = MOBAMAS_FILES

    if deresute_txt.exists():
        with open(deresute_txt) as f:
            deresute_files = [
                line.strip().replace('/home/user/SugarHeartDB/', '')
                for line in f if line.strip() and '.html' in line
            ]
    else:
        deresute_files = DERESUTE_FILES

    # Filter out Common/
    deresute_files = [f for f in deresute_files if 'Deresute/Common/' not in f]

    all_files = mobamas_files + deresute_files

    print(f'変換対象: {len(all_files)} ファイル')
    print(f'  Mobamas: {len(mobamas_files)} ファイル')
    print(f'  Deresute: {len(deresute_files)} ファイル')
    print()

    success = 0
    skipped = 0
    errors = []

    for rel_path in all_files:
        try:
            result = convert_file(rel_path)
            if result:
                success += 1
            else:
                skipped += 1
        except Exception as e:
            print(f'  [ERROR] {rel_path}: {e}')
            import traceback
            traceback.print_exc()
            errors.append((rel_path, str(e)))

    print()
    print(f'完了: {success} 件変換, {skipped} 件スキップ, {len(errors)} 件エラー')
    if errors:
        print('エラー一覧:')
        for path, err in errors:
            print(f'  {path}: {err}')


if __name__ == '__main__':
    main()
