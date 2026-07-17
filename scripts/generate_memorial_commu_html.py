# -*- coding: utf-8 -*-
"""merged_memorial_commu.json からメモリアルコミュ（デレステ）のページを生成する。

出力: Deresute/MemorialCommu.html（全6タブ。5話は良い知らせ／悪い知らせの2分岐）
各タブ = タイトルカード＋話メタ＋YouTube動画（同一動画を?start=で頭出し）＋スクショ付きログ＋ログ画像
"""
import html
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
MERGED = REPO / "scripts" / "merged_memorial_commu.json"
OUT = REPO / "Deresute" / "MemorialCommu.html"

CDN = "https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/Memorial"
VIDEO_ID = "7bvsgbdut3Q"


def esc(s):
    return html.escape(s or "", quote=True)


def frame_url(frame):
    return f"{CDN}/commu/{frame}"


def render_line(e):
    sp = esc(e["speaker"])
    text = esc(e["text"])
    dialogue = (f'<div class="ud-dialogue"><span class="speaker" data-who="{sp}">{sp}</span>'
                f'<div class="line">{text}</div></div>')
    if e.get("frame"):
        return ('<div class="ev-dialog-row">'
                f'<div class="ev-shot"><img src="{frame_url(e["frame"])}" alt="{sp}のセリフ" loading="lazy"></div>'
                f'<div class="ev-text">{dialogue}</div></div>')
    return f'<div class="ev-dialog-row no-shot"><div class="ev-text">{dialogue}</div></div>'


def render_stage(e):
    text = esc(e["text"])
    if e.get("frame"):
        return ('<div class="ev-dialog-row">'
                f'<div class="ev-shot"><img src="{frame_url(e["frame"])}" alt="{text}" loading="lazy"></div>'
                '<div class="ev-text"><div class="dss-stage-text">' + text + '</div></div></div>')
    return f'<div class="ev-dialog-row no-shot"><div class="ev-text"><div class="dss-stage-text">{text}</div></div></div>'


def log_code(code):
    return code.replace("_", "")  # 5_B -> 5B


def main():
    data = json.loads(MERGED.read_text(encoding="utf-8"))

    tabs_html = []
    panels_html = []
    for i, sec in enumerate(data):
        active = " active" if i == 0 else ""
        tab_id = f'mc-{sec["id"]}'
        tabs_html.append(
            f'        <button class="tab-item{active}" onclick="switchTab(this,\'{tab_id}\')">{esc(sec["tab"])}</button>')

        rows = []
        for e in sec["entries"]:
            if e["type"] == "line":
                rows.append(render_line(e))
            else:  # stage / scene
                rows.append(render_stage(e))
        rows_html = "\n            ".join(rows)

        start = sec.get("start_s", 0)
        video_html = (
            '\n        <div class="video-container-mobamas">\n'
            f'            <iframe src="https://www.youtube.com/embed/{VIDEO_ID}?start={start}" '
            'title="YouTube video player" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>\n'
            '        </div>')

        summary = esc(sec.get("summary", ""))
        summary_html = f'\n            <p class="dss-ep-summary">{summary}</p>' if summary else ""

        log_html = (
            '\n        <details class="dss-log">\n'
            '            <summary>コミュログ画像を表示</summary>\n'
            f'            <img class="lightbox-trigger" src="{CDN}/log/{log_code(sec["code"])}" '
            f'alt="{esc(sec["title"])} コミュログ" loading="lazy">\n'
            '        </details>')

        panels_html.append(f'''    <div class="tab-panel{active}" data-tab="{tab_id}">
        <div class="dss-ep-head">
            <div class="dss-title-card"><img class="lightbox-trigger" src="{frame_url(sec["title_frame"])}" alt="{esc(sec["title"])} タイトルカード" loading="lazy"></div>
            <div class="dss-ep-meta">
                <div class="dss-ep-eyebrow">メモリアルコミュ</div>
                <h3 class="dss-ep-title">{esc(sec["title"])}</h3>{summary_html}
            </div>
        </div>{video_html}
        <div class="dss-lines mobamas-shots">
            {rows_html}
        </div>{log_html}
    </div>''')

    section = ('    <section class="tab-group dss-commu">\n'
               '        <div class="tab-list">\n'
               + "\n".join(tabs_html) + "\n"
               '        </div>\n'
               + "\n".join(panels_html) + "\n"
               '    </section>')

    page = PAGE_TEMPLATE.format(section=section)
    OUT.write_text(page, encoding="utf-8")
    print(f"生成完了: {OUT} ({len(page)} chars, {len(data)}タブ)")


DESC = ("アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）のメモリアルコミュを、"
        "動画とスクショ付きセリフログでまとめたページです。")

PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <base href="/SugarHeartDB/">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>メモリアルコミュ｜SugarHeartDB</title>
    <meta name="description" content="''' + DESC + '''">
    <meta name="author" content="なごみ（@nagomi_IMCG）">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="メモリアルコミュ｜SugarHeartDB">
    <meta property="og:description" content="''' + DESC + '''">
    <meta property="og:site_name" content="SugarHeartDB">
    <meta property="og:image" content="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/KonoyoDeTadaHitoriNoHeart+/KonoyoDeTadaHitoriNoHeart+">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="メモリアルコミュ｜SugarHeartDB">
    <link rel="icon" type="image/png" sizes="32x32" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-32x32">
    <link rel="icon" type="image/png" sizes="16x16" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-16x16">
    <link rel="apple-touch-icon" sizes="180x180" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/apple-touch-icon">
    <link rel="stylesheet" href="style.css?v=20260717c">
</head>
<body>
<script src="components/header.js"></script>

<section class="page-hero">
    <div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <a href="Deresute/index.html">DERESUTE</a> · <strong>メモリアルコミュ</strong></div>
    <h1>メモリアルコミュ <span class="sub">/ MEMORIAL COMMU · DERESUTE</span></h1>
    <p class="summary">佐藤心（しゅがーはぁと）のメモリアルコミュ全5話を、動画とスクショ付きのセリフログでまとめています。第5話は選択肢で「良い知らせ」「悪い知らせ」の2分岐に分かれます。</p>
</section>

<main class="page">

{section}

    <div class="related-foot">
        <div class="related">
            <span class="lbl">RELATED //</span>
            <a href="Deresute/Common/CommonCommu.html">共通コミュ</a>
            <a href="Deresute/Common/StoryCommu.html">ストーリーコミュ</a>
            <a href="Deresute/Common/BusinessCommu.html">営業コミュ</a>
        </div>
        <div class="nav-events">
            <a href="Deresute/index.html">◀ デレステTOPへ</a>
        </div>
    </div>

</main>

<div class="sh-lightbox" id="sh-lightbox">
    <span class="sh-lightbox-close" id="sh-lightbox-close">×</span>
    <img class="sh-lightbox-img" id="sh-lightbox-img" src="" alt="">
</div>

<script src="components/common.js"></script>
<script src="components/idol-badge.js"></script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
