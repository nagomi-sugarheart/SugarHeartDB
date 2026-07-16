# -*- coding: utf-8 -*-
"""merged_{key}_commu.json からストーリーコミュのHTML断片を生成する。
出力: scripts/{key}_commu_body.html（dss-ep-head + dss-lines + log の断片）"""
import html, json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO=Path(__file__).parent.parent

CDN_BASE={
    "sweetie":"https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/StoryCommu/WhatIsSweetie",
    "arisu":"https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/GuestCommu/OtherIdolStory/arisu",
    "miyu":"https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/GuestCommu/OtherIdolStory/miyu",
}
EYEBROW={"sweetie":"第58話","arisu":"第40話","miyu":"第53話"}

def esc(s): return html.escape(s, quote=True)

def main():
    for key in ["sweetie","arisu","miyu"]:
        cdn=CDN_BASE[key]
        sec=json.loads((REPO/"scripts"/f"merged_{key}_commu.json").read_text(encoding="utf-8"))
        def furl(fr): return f"{cdn}/commu/{fr.split('_')[0]}"
        rows=[]
        for e in sec["entries"]:
            if e["type"]=="line":
                sp=esc(e["speaker"]); text=esc(e["text"])
                dialogue=(f'<div class="ud-dialogue"><span class="speaker" data-who="{sp}">{sp}</span>'
                          f'<div class="line">{text}</div></div>')
                rows.append(f'<div class="ev-dialog-row"><div class="ev-shot">'
                            f'<img src="{furl(e["frame"])}" alt="{sp}のセリフ" loading="lazy"></div>'
                            f'<div class="ev-text">{dialogue}</div></div>')
            else:  # scene / stage
                text=esc(e["text"])
                rows.append(f'<div class="ev-dialog-row"><div class="ev-shot">'
                            f'<img src="{furl(e["frame"])}" alt="{text}" loading="lazy"></div>'
                            f'<div class="ev-text"><div class="dss-stage-text">{text}</div></div></div>')
        rows_html="\n        ".join(rows)
        title_card=(f'<div class="dss-title-card"><img class="lightbox-trigger" '
                    f'src="{furl(sec["title_frame"])}" alt="{esc(sec["title"])} タイトルカード" loading="lazy"></div>')
        head=(f'    <div class="dss-ep-head">\n        {title_card}\n'
              f'        <div class="dss-ep-meta">\n'
              f'            <div class="dss-ep-eyebrow">{EYEBROW[key]}</div>\n'
              f'            <h3 class="dss-ep-title">{esc(sec["title"])}</h3>\n'
              f'            <p class="dss-ep-summary">{esc(sec["summary"])}</p>\n'
              f'        </div>\n    </div>')
        log=(f'    <details class="dss-log">\n'
             f'        <summary>コミュログ画像を表示</summary>\n'
             f'        <img class="lightbox-trigger" src="{cdn}/log/OP" alt="{esc(sec["title"])} コミュログ" loading="lazy">\n'
             f'    </details>')
        body=f'{head}\n    <div class="dss-lines">\n        {rows_html}\n    </div>\n{log}'
        (REPO/"scripts"/f"{key}_commu_body.html").write_text(body,encoding="utf-8")
        print(f"{key}: {len(rows)}行 生成")

if __name__=="__main__":
    main()
