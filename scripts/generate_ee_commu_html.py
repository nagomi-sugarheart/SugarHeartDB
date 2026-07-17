# -*- coding: utf-8 -*-
"""merged_ee_commu.json から EVERLASTING & EVERAFTER ページを生成する。

Deresute/GuestCommu/GuestCommu_EverlastingEverafter.html
2イベント×タブ形式。commu=shot付き / mv=映像のみ頭出し / logonly=ログのみ。
"""
import html, json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
MERGED = REPO / "scripts" / "merged_ee_commu.json"
OUT = REPO / "Deresute" / "GuestCommu" / "GuestCommu_EverlastingEverafter.html"
CDN = "https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/GuestCommu/EverlastingEverafter"
PIDMAP = {"everlasting": "Everlasting", "everafter": "Everafter"}


def esc(s):
    return html.escape(s or "", quote=True)


def furl(ev, frame):
    return f"{CDN}/{PIDMAP[ev]}/commu/{frame}"


def render_line(ev, e):
    sp = esc(e["speaker"]); text = esc(e["text"])
    dlg = (f'<div class="ud-dialogue"><span class="speaker" data-who="{sp}">{sp}</span>'
           f'<div class="line">{text}</div></div>')
    if e.get("frame"):
        return ('<div class="ev-dialog-row">'
                f'<div class="ev-shot"><img src="{furl(ev, e["frame"])}" alt="{sp}のセリフ" loading="lazy"></div>'
                f'<div class="ev-text">{dlg}</div></div>')
    return f'<div class="ev-dialog-row no-shot"><div class="ev-text">{dlg}</div></div>'


def render_stage(ev, e):
    text = esc(e["text"])
    if e.get("frame"):
        return ('<div class="ev-dialog-row">'
                f'<div class="ev-shot"><img src="{furl(ev, e["frame"])}" alt="{text}" loading="lazy"></div>'
                f'<div class="ev-text"><div class="dss-stage-text">{text}</div></div></div>')
    return f'<div class="ev-dialog-row no-shot"><div class="ev-text"><div class="dss-stage-text">{text}</div></div></div>'


def video_embed(video, start):
    return ('\n        <div class="video-container-mobamas">\n'
            f'            <iframe src="https://www.youtube.com/embed/{video}?start={start}" '
            'title="YouTube video player" frameborder="0" '
            'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>\n'
            '        </div>')


def build_panel(ev, video, sec, active):
    evid = ev
    title_card = ""
    if sec.get("title_frame"):
        title_card = (f'<div class="dss-title-card"><img class="lightbox-trigger" '
                      f'src="{furl(evid, sec["title_frame"])}" alt="{esc(sec["title"])} タイトルカード" loading="lazy"></div>')
    summary = esc(sec.get("summary", ""))
    summary_html = f'\n            <p class="dss-ep-summary">{summary}</p>' if summary else ""
    head = f'''        <div class="dss-ep-head">
            {title_card}<div class="dss-ep-meta">
                <div class="dss-ep-eyebrow">{esc(sec["eplabel"])}</div>
                <h3 class="dss-ep-title">{esc(sec["title"])}</h3>{summary_html}
            </div>
        </div>'''

    tab_id = f'ee-{sec["id"]}'
    act = " active" if active else ""

    if sec["kind"] == "mv":
        body = (video_embed(video, sec["start_s"]) +
                '\n        <p class="dss-note">この区間は楽曲MVです。上の動画で頭出し再生されます。</p>')
        return f'''    <div class="tab-panel{act}" data-tab="{tab_id}">
{head}{body}
    </div>'''

    rows = []
    for e in sec["entries"]:
        rows.append(render_line(evid, e) if e["type"] == "line" else render_stage(evid, e))
    rows_html = "\n            ".join(rows)

    if sec["kind"] == "logonly":
        video_html = ('\n        <p class="dss-note">※このコミュはスクショ未取得のため、'
                      'セリフのテキストとコミュログ画像で掲載しています。</p>')
    else:
        video_html = video_embed(video, sec["start_s"])

    log_html = (
        '\n        <details class="dss-log">\n'
        '            <summary>コミュログ画像を表示</summary>\n'
        f'            <img class="lightbox-trigger" src="{CDN}/{PIDMAP[evid]}/log/{sec["code"]}" '
        f'alt="{esc(sec["title"])} コミュログ" loading="lazy">\n'
        '        </details>')

    return f'''    <div class="tab-panel{act}" data-tab="{tab_id}">
{head}{video_html}
        <div class="dss-lines mobamas-shots">
            {rows_html}
        </div>{log_html}
    </div>'''


def build_event(ev):
    tabs = []
    panels = []
    for i, sec in enumerate(ev["sections"]):
        active = (i == 0)
        tab_id = f'ee-{sec["id"]}'
        tabs.append(f'        <button class="tab-item{" active" if active else ""}" '
                    f'onclick="switchTab(this,\'{tab_id}\')">{esc(sec["tab"])}</button>')
        panels.append(build_panel(ev["id"], ev["video"], sec, active))
    return (f'''    <section class="ee-block">
        <div class="ee-head"><h2>{esc(ev["name"])}</h2></div>
    <section class="tab-group dss-commu">
        <div class="tab-list">
''' + "\n".join(tabs) + '''
        </div>
''' + "\n".join(panels) + '''
    </section>
    </section>''')


def main():
    data = json.loads(MERGED.read_text(encoding="utf-8"))
    blocks = "\n\n".join(build_event(ev) for ev in data)
    page = PAGE_TEMPLATE.format(blocks=blocks)
    OUT.write_text(page, encoding="utf-8")
    print(f"生成完了: {OUT} ({len(page)} chars)")


DESC = ("アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）が登場するデレステの"
        "アニバーサリーイベント「EVERLASTING & EVERAFTER」のコミュを、動画とセリフログでまとめたページです。")

PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <base href="/SugarHeartDB/">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EVERLASTING ＆ EVERAFTER（デレステ）｜SugarHeartDB</title>
    <meta name="description" content="''' + DESC + '''">
    <meta name="author" content="なごみ（@nagomi_IMCG）">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="EVERLASTING ＆ EVERAFTER（デレステ）｜SugarHeartDB">
    <meta property="og:description" content="''' + DESC + '''">
    <meta property="og:site_name" content="SugarHeartDB">
    <meta property="og:image" content="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/KonoyoDeTadaHitoriNoHeart+/KonoyoDeTadaHitoriNoHeart+">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="EVERLASTING ＆ EVERAFTER（デレステ）｜SugarHeartDB">
    <link rel="icon" type="image/png" sizes="32x32" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-32x32">
    <link rel="icon" type="image/png" sizes="16x16" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-16x16">
    <link rel="apple-touch-icon" sizes="180x180" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/apple-touch-icon">
    <link rel="stylesheet" href="style.css?v=20260717d">
</head>
<body>
<script src="components/header.js"></script>

<section class="page-hero">
    <div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <a href="Deresute/index.html">DERESUTE</a> · <a href="Deresute/GuestCommu/GuestCommu.html">ゲストコミュ</a> · <strong>EVERLASTING ＆ EVERAFTER</strong></div>
    <h1>EVERLASTING ＆ EVERAFTER <span class="sub">/ GUEST COMMU · DERESUTE</span></h1>
    <p class="summary">シンデレラガールズ アニバーサリーイベント「EVERLASTING & EVERAFTER」で佐藤心（しゅがーはぁと）が登場するコミュを、動画とスクショ付きのセリフログでまとめています。EVERLASTINGは第5話・第10話、EVERAFTERはOP・楽曲MV・1話・5話・EDを掲載しています。</p>
</section>

<main class="page">

{blocks}

    <div class="related-foot">
        <div class="related">
            <span class="lbl">RELATED //</span>
            <a href="Deresute/GuestCommu/GuestCommu.html">ゲストコミュ一覧</a>
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
