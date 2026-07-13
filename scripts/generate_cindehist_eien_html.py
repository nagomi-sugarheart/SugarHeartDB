# -*- coding: utf-8 -*-
"""シンデレラヒストリー「永遠に輝きを放つ乙女たち☆」のshot付きセリフブロック生成

merged_cindehist_eien_commu.json から .dss-lines ブロックを生成し、
Mobamas/CinderellaHistory.html の CH1-COMMU-START/END マーカー間を置き換える。
"""
import html
import json
from pathlib import Path

REPO = Path(__file__).parent.parent
PAGE = REPO / "Mobamas" / "CinderellaHistory.html"
MERGED = REPO / "scripts" / "merged_cindehist_eien_commu.json"
CDN = "https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto"

data = json.loads(MERGED.read_text(encoding="utf-8"))
BASE = data["cloudinary_base"]


def frame_url(frame: str) -> str:
    return f"{CDN}/{BASE}/{frame.split('_')[0]}"


rows = []
for e in data["entries"]:
    text = html.escape(e["text"])
    if e["type"] == "stage":
        rows.append(
            f'<div class="ev-dialog-row">'
            f'<div class="ev-shot"><img src="{frame_url(e["frame"])}" alt="{text}" loading="lazy"></div>'
            f'<div class="ev-text"><div class="dss-stage-text">{text}</div></div></div>')
        continue
    sp = html.escape(e["speaker"])
    dialogue = (f'<div class="ud-dialogue"><span class="speaker" data-who="{sp}">{sp}</span>'
                f'<div class="line">{text}</div></div>')
    if e.get("frame"):
        rows.append(
            f'<div class="ev-dialog-row">'
            f'<div class="ev-shot"><img src="{frame_url(e["frame"])}" alt="{sp}のセリフ" loading="lazy"></div>'
            f'<div class="ev-text">{dialogue}</div></div>')
    else:
        rows.append(f'<div class="ev-dialog-row no-shot"><div class="ev-text">{dialogue}</div></div>')

rows_html = "\n                ".join(rows)
fragment = (f'            <div class="dss-lines mobamas-shots">\n'
            f'                {rows_html}\n'
            f'            </div>')

page = PAGE.read_text(encoding="utf-8")
START = "<!-- CH1-COMMU-START -->"
END = "<!-- CH1-COMMU-END -->"
assert START in page and END in page, "マーカーが見つかりません"
before = page.split(START)[0]
after = page.split(END)[1]
PAGE.write_text(before + START + "\n" + fragment + "\n            " + END + after, encoding="utf-8")

print(f"生成完了: {len(rows)} 行を書き込みました")
