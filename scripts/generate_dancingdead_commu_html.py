# -*- coding: utf-8 -*-
"""merged_dancingdead_commu.json から ダンシング・デッド のイベントコミュHTMLを生成する

出力: scripts/dancingdead_commu_section.html（ページに手動で組み込む用の断片）
"""
import html
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
MERGED = REPO / "scripts" / "merged_dancingdead_commu.json"
OUT = REPO / "scripts" / "dancingdead_commu_section.html"

CDN = "https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/Event/DancingDead"

EPISODE_LABELS = {
    "trailer": "予告", "op": "オープニング",
    "ep1": "第1話", "ep2": "第2話", "ep3": "第3話", "ep4": "第4話", "ep5": "第5話",
    "ed": "エンディング",
}
LOG_LABELS = {"Tr1": "予告1", "Tr2": "予告2", "OP": "OP",
              "1": "第1話", "2": "第2話", "3": "第3話", "4": "第4話", "5": "第5話", "ED": "ED"}


def esc(s):
    return html.escape(s, quote=True)


def frame_url(frame):
    return f"{CDN}/commu/{frame.split('_')[0]}"


def render_line(e):
    sp = esc(e["speaker"])
    text = esc(e["text"])
    dialogue = (f'<div class="ud-dialogue"><span class="speaker" data-who="{sp}">{sp}</span>'
                f'<div class="line">{text}</div></div>')
    if e.get("frame"):
        return (f'<div class="ev-dialog-row">'
                f'<div class="ev-shot"><img src="{frame_url(e["frame"])}" alt="{sp}のセリフ" loading="lazy"></div>'
                f'<div class="ev-text">{dialogue}</div></div>')
    return (f'<div class="ev-dialog-row no-shot">'
            f'<div class="ev-text">{dialogue}</div></div>')


def render_stage(e):
    text = esc(e["text"])
    if e.get("frame"):
        return (f'<div class="ev-dialog-row">'
                f'<div class="ev-shot"><img src="{frame_url(e["frame"])}" alt="{text}" loading="lazy"></div>'
                f'<div class="ev-text"><div class="dss-stage-text">{text}</div></div></div>')
    return (f'<div class="ev-dialog-row no-shot">'
            f'<div class="ev-text"><div class="dss-stage-text">{text}</div></div></div>')


def render_note(e):
    return f'<div class="dss-branch-note"><span class="dss-branch-ic">⑂</span>{esc(e["text"])}</div>'


def main():
    data = json.loads(MERGED.read_text(encoding="utf-8"))

    tabs_html = []
    panels_html = []
    for i, sec in enumerate(data):
        active = " active" if i == 0 else ""
        tabs_html.append(
            f'        <button class="tab-item{active}" onclick="switchTab(this,\'dd-{sec["id"]}\')">{esc(sec["tab"])}</button>')

        used = {sec.get("title_frame")}
        for e in sec["entries"]:
            if e["type"] in ("line", "stage", "scene") and e.get("frame"):
                used.add(e["frame"])

        rows = []
        for e in sec["entries"]:
            if e["type"] == "line":
                rows.append(render_line(e))
            elif e["type"] in ("stage", "scene", "header"):
                rows.append(render_stage(e))
            elif e["type"] == "note":
                rows.append(render_note(e))
            elif e["type"] == "sub":
                if e.get("frame") and e["frame"] not in used:
                    used.add(e["frame"])
                    rows.append(
                        f'<div class="ev-dialog-row">'
                        f'<div class="ev-shot"><img src="{frame_url(e["frame"])}" alt="{esc(e["text"])}" loading="lazy"></div>'
                        f'<div class="ev-text"><div class="ev-condition"><span class="ev-label">{esc(e["text"])}</span></div></div></div>')
                else:
                    rows.append(f'<div class="ev-condition"><span class="ev-label">{esc(e["text"])}</span></div>')

        summary_html = f'\n            <p class="dss-ep-summary">{esc(sec["summary"])}</p>' if sec["summary"] else ""
        logs = "\n".join(
            f'    <details class="dss-log">\n'
            f'        <summary>コミュログ画像を表示（{LOG_LABELS[c]}）</summary>\n'
            f'        <img class="lightbox-trigger" src="{CDN}/log/{c}" alt="{esc(sec["tab"])} コミュログ（{LOG_LABELS[c]}）" loading="lazy">\n'
            f'    </details>' for c in sec["log"])

        rows_html = "\n        ".join(rows)
        panels_html.append(f'''    <div class="tab-panel{active}" data-tab="dd-{sec["id"]}">
    <div class="dss-ep-head">
        <div class="dss-title-card"><img class="lightbox-trigger" src="{frame_url(sec["title_frame"])}" alt="{esc(sec["title"])} タイトルカード" loading="lazy"></div>
        <div class="dss-ep-meta">
            <div class="dss-ep-eyebrow">{EPISODE_LABELS[sec["id"]]}</div>
            <h3 class="dss-ep-title">{esc(sec["title"])}</h3>{summary_html}
            <button class="dss-play" data-start="{sec["start_s"]}">▶ この話からYouTubeで再生</button>
        </div>
    </div>
    <div class="dss-lines">
        {rows_html}
    </div>
{logs}
    </div>''')

    section = ('    <section class="tab-group dss-commu">\n'
               '        <div class="tab-list">\n'
               + "\n".join(tabs_html) + "\n"
               '        </div>\n'
               + "\n".join(panels_html) + "\n"
               '    </section>')

    OUT.write_text(section, encoding="utf-8")
    print(f"生成完了: {OUT} ({len(section)} chars)")


if __name__ == "__main__":
    main()
