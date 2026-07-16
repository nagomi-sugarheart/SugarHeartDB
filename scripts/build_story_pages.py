# -*- coding: utf-8 -*-
"""ストーリーコミュ2ページを組み立てる。
1) Deresute/Common/StoryCommu.html … 第58話 What is Sweetie？（単話・タブ無し）
2) Deresute/GuestCommu/GuestCommu_OtherIdolStory.html … 橘ありす/三船美優 2タブ
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
REPO=Path(__file__).parent.parent
S=REPO/"scripts"

def body(key): return (S/f"{key}_commu_body.html").read_text(encoding="utf-8")

HEAD=lambda title,desc: f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <base href="/SugarHeartDB/">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}｜SugarHeartDB</title>
    <meta name="description" content="{desc}">
    <meta name="author" content="なごみ（@nagomi_IMCG）">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}｜SugarHeartDB">
    <meta property="og:description" content="{desc}">
    <meta property="og:site_name" content="SugarHeartDB">
    <meta property="og:image" content="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/KonoyoDeTadaHitoriNoHeart+/KonoyoDeTadaHitoriNoHeart+">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{title}｜SugarHeartDB">
    <link rel="icon" type="image/png" sizes="32x32" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-32x32">
    <link rel="icon" type="image/png" sizes="16x16" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-16x16">
    <link rel="apple-touch-icon" sizes="180x180" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/apple-touch-icon">
    <link rel="stylesheet" href="style.css?v=20260708">
</head>
<body>
<script src="components/header.js"></script>
'''

FOOT='''
<div class="sh-lightbox" id="sh-lightbox">
    <span class="sh-lightbox-close" id="sh-lightbox-close">×</span>
    <img class="sh-lightbox-img" id="sh-lightbox-img" src="" alt="">
</div>

<script src="components/common.js"></script>
<script src="components/idol-badge.js"></script>
</body>
</html>
'''

def iframe(vid):
    return (f'<div class="video-container-landscape">\n'
            f'            <iframe src="https://www.youtube.com/embed/{vid}" title="YouTube video player" '
            f'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; '
            f'picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>\n'
            f'        </div>')

# ---------- 1) What is Sweetie（単話） ----------
sweetie=HEAD("ストーリーコミュ（デレステ）",
    "アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）が登場したデレステのストーリーコミュ第58話「What is Sweetie？」をまとめたページです。")
sweetie+=f'''
<section class="page-hero">
    <div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <a href="Deresute/index.html">DERESUTE</a> · <strong>ストーリーコミュ（デレステ）</strong></div>
    <h1>ストーリーコミュ（デレステ） <span class="sub">/ STORY COMMU · DERESUTE</span></h1>
    <p class="summary">デレステのストーリーコミュにおける心ちゃんの登場話をまとめています。</p>
</section>

<main class="page">

    <div class="sec-head">
        <div class="ic glyph-overview"></div>
        <h2>第58話「What is Sweetie？」 <span class="sub">/ AT-A-GLANCE</span></h2>
        <a class="anchor">#overview</a>
    </div>
    <div class="credit-strip">
        <div class="credit"><div class="l">実装日</div><div class="v">2019.10.10</div></div>
        <div class="credit"><div class="l">LIVE楽曲</div><div class="v">しゅがーはぁと☆レボリューション</div></div>
        <div class="credit"><div class="l">登場アイドル</div><div class="v">安部菜々・早坂美玲・佐藤心・喜多見柚・荒木比奈</div></div>
    </div>

    <div class="sec-head">
        <div class="ic glyph-movie"></div>
        <h2>動画 <span class="sub">/ MOVIE</span></h2>
        <a class="anchor">#movie</a>
    </div>
    <div class="box-area">
        <div class="box-title">ストーリーコミュ 第58話</div>
        {iframe("zEfKqfzkqX0")}
    </div>

    <div class="sec-head">
        <div class="ic glyph-dialogue"></div>
        <h2>ストーリーコミュ <span class="sub">/ COMMU</span></h2>
        <a class="anchor">#commu</a>
    </div>
    <section class="tab-group dss-commu">
    <div class="tab-panel active" data-tab="sweetie-ep">
{body("sweetie")}
    </div>
    </section>

    <div class="related-foot">
        <div class="nav-events">
            <a href="Deresute/index.html">◀ デレステTOPへ</a>
        </div>
    </div>

</main>
'''
sweetie+=FOOT
(REPO/"Deresute/Common/StoryCommu.html").write_text(sweetie,encoding="utf-8")
print("StoryCommu.html 書き出し完了")

# ---------- 2) 他アイドルストーリーコミュ（2タブ） ----------
ois=HEAD("他アイドルストーリーコミュ（デレステ）",
    "アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）が登場した、他アイドルのデレステ・ストーリーコミュ（橘ありす・三船美優）をまとめたページです。")
def tab_panel(tab_id, active, info, vid, key):
    a=" active" if active else ""
    return f'''    <div class="tab-panel{a}" data-tab="{tab_id}">
        <p class="box-text">{info}</p>
        {iframe(vid)}
{body(key)}
    </div>'''
ois+=f'''
<section class="page-hero">
    <div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <a href="Deresute/index.html">DERESUTE</a> · <a href="Deresute/GuestCommu/GuestCommu.html">GUEST COMMU</a> · <strong>他アイドルストーリーコミュ（デレステ）</strong></div>
    <h1>他アイドルストーリーコミュ（デレステ） <span class="sub">/ OTHER IDOL STORY · DERESUTE</span></h1>
    <p class="summary">他アイドルのストーリーコミュに登場する心ちゃんのシーンをまとめています。</p>
</section>

<main class="page">

    <div class="sec-head">
        <div class="ic glyph-dialogue"></div>
        <h2>ストーリーコミュ <span class="sub">/ COMMU</span></h2>
        <a class="anchor">#commu</a>
    </div>
    <section class="tab-group dss-commu">
        <div class="tab-list">
        <button class="tab-item active" onclick="switchTab(this,'ois-arisu')">橘ありす</button>
        <button class="tab-item" onclick="switchTab(this,'ois-miyu')">三船美優</button>
        </div>
{tab_panel("ois-arisu", True, "第40話「Be honest with yourself」／実装日 2017.01.28／LIVE楽曲「in fact」／登場アイドル：佐藤心・市原仁奈・橘ありす・龍崎薫・相葉夕美", "TVGdhC6rxfM", "arisu")}
{tab_panel("ois-miyu", False, "第53話「Step forward to the future」／実装日 2018.11.08／LIVE楽曲「Last Kiss」／登場アイドル：結城晴・市原仁奈・三船美優・佐藤心・大和亜季", "uttRQJukfhM", "miyu")}
    </section>

    <div class="related-foot">
        <div class="related">
            <span class="lbl">RELATED //</span>
            <a href="Deresute/GuestCommu/GuestCommu.html">ゲスト参加コミュ＆映り込みカード</a>
        </div>
        <div class="nav-events">
            <a href="Deresute/index.html">◀ デレステTOPへ</a>
        </div>
    </div>

</main>
'''
ois+=FOOT
(REPO/"Deresute/GuestCommu/GuestCommu_OtherIdolStory.html").write_text(ois,encoding="utf-8")
print("GuestCommu_OtherIdolStory.html 書き出し完了")
