# -*- coding: utf-8 -*-
"""merged_eigyo_commu.json から営業コミュ（デレステ）の6タブHTML断片を生成する

出力: scripts/eigyo_commu_section.html（BusinessCommu.html に組み込む用）
各タブ = 1営業コミュ（タイトルカード＋エリア/実装日メタ＋YouTube動画＋スクショ付きログ＋ログ画像）
"""
import html
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
MERGED = REPO / "scripts" / "merged_eigyo_commu.json"
OUT = REPO / "Deresute" / "Common" / "BusinessCommu.html"

CDN = "https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/Eigyo"


def esc(s):
    return html.escape(s or "", quote=True)


def frame_url(pid, frame):
    return f"{CDN}/{pid}/commu/{frame.split('_')[0]}"


def render_line(pid, e):
    sp = esc(e["speaker"])
    text = esc(e["text"])
    dialogue = (f'<div class="ud-dialogue"><span class="speaker" data-who="{sp}">{sp}</span>'
                f'<div class="line">{text}</div></div>')
    if e.get("frame"):
        return ('<div class="ev-dialog-row">'
                f'<div class="ev-shot"><img src="{frame_url(pid, e["frame"])}" alt="{sp}のセリフ" loading="lazy"></div>'
                f'<div class="ev-text">{dialogue}</div></div>')
    return f'<div class="ev-dialog-row no-shot"><div class="ev-text">{dialogue}</div></div>'


def render_stage(pid, e):
    text = esc(e["text"])
    if e.get("frame"):
        return ('<div class="ev-dialog-row">'
                f'<div class="ev-shot"><img src="{frame_url(pid, e["frame"])}" alt="{text}" loading="lazy"></div>'
                '<div class="ev-text"><div class="dss-stage-text">' + text + '</div></div></div>')
    return f'<div class="ev-dialog-row no-shot"><div class="ev-text"><div class="dss-stage-text">{text}</div></div></div>'


def main():
    data = json.loads(MERGED.read_text(encoding="utf-8"))

    tabs_html = []
    panels_html = []
    for i, sec in enumerate(data):
        active = " active" if i == 0 else ""
        pid = sec["pid"]
        tab_id = f'eig-{sec["id"]}'
        tabs_html.append(
            f'        <button class="tab-item{active}" onclick="switchTab(this,\'{tab_id}\')">{esc(sec["tab"])}</button>')

        rows = []
        for e in sec["entries"]:
            if e["type"] == "line":
                rows.append(render_line(pid, e))
            else:  # stage / scene
                rows.append(render_stage(pid, e))
        rows_html = "\n            ".join(rows)

        # 動画（YouTubeがある場合のみ）
        if sec.get("youtube"):
            video_html = (
                '\n        <div class="video-container-mobamas">\n'
                f'            <iframe src="https://www.youtube.com/embed/{sec["youtube"]}" '
                'title="YouTube video player" frameborder="0" '
                'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
                'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>\n'
                '        </div>')
        else:
            video_html = ('\n        <p class="placeholder-text" style="text-align:center;">'
                          '※この営業コミュの動画は準備中です。</p>')

        summary = esc(sec.get("area_label", ""))
        summary_html = f'\n            <p class="dss-ep-summary">舞台：{summary}</p>' if summary else ""

        log_html = (
            '\n        <details class="dss-log">\n'
            '            <summary>コミュログ画像を表示</summary>\n'
            f'            <img class="lightbox-trigger" src="{CDN}/{pid}/log" '
            f'alt="{esc(sec["title"])} コミュログ" loading="lazy">\n'
            '        </details>')

        panels_html.append(f'''    <div class="tab-panel{active}" data-tab="{tab_id}">
        <div class="dss-ep-head">
            <div class="dss-title-card"><img class="lightbox-trigger" src="{frame_url(pid, sec["title_frame"])}" alt="{esc(sec["title"])} タイトルカード" loading="lazy"></div>
            <div class="dss-ep-meta">
                <div class="dss-ep-eyebrow">{esc(sec["area"])}エリア ・ {esc(sec["date"])} 実装</div>
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


DESC = ("アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）が登場するデレステの営業コミュを、"
        "動画とセリフログでまとめたページです。")

PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <base href="/SugarHeartDB/">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>営業コミュ（デレステ）｜SugarHeartDB</title>
    <meta name="description" content="''' + DESC + '''">
    <meta name="author" content="なごみ（@nagomi_IMCG）">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="営業コミュ（デレステ）｜SugarHeartDB">
    <meta property="og:description" content="''' + DESC + '''">
    <meta property="og:site_name" content="SugarHeartDB">
    <meta property="og:image" content="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/KonoyoDeTadaHitoriNoHeart+/KonoyoDeTadaHitoriNoHeart+">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="営業コミュ（デレステ）｜SugarHeartDB">
    <link rel="icon" type="image/png" sizes="32x32" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-32x32">
    <link rel="icon" type="image/png" sizes="16x16" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-16x16">
    <link rel="apple-touch-icon" sizes="180x180" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/apple-touch-icon">
    <link rel="stylesheet" href="style.css?v=20260716">
</head>
<body>
<script src="components/header.js"></script>

<section class="page-hero">
    <div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <a href="Deresute/index.html">DERESUTE</a> · <strong>営業コミュ（デレステ）</strong></div>
    <h1>営業コミュ（デレステ） <span class="sub">/ BUSINESS COMMU · DERESUTE</span></h1>
    <p class="summary">デレステの「営業」で佐藤心（しゅがーはぁと）が登場する営業コミュを、動画とスクショ付きのセリフログでまとめています。各営業のエリア・実装日ごとにタブで切り替えられます。</p>
</section>

<main class="page">

{section}

    <div class="related-foot">
        <div class="related">
            <span class="lbl">RELATED //</span>
            <a href="Deresute/Common/CommonCommu.html">共通コミュ</a>
            <a href="Deresute/Common/MemorialCommu.html">メモリアルコミュ</a>
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
