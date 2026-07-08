# -*- coding: utf-8 -*-
"""第1回 アイドルプロデュース イベントコミュHTML生成

scripts/idolproduce1st_texts.json（心）・idolproduce1st_nana_texts.json（菜々）から、
Deresute/Event/IdolProduce1st.html の
<!-- IP1-COMMU-START --> 〜 <!-- IP1-COMMU-END --> の間を差し替える。

構成:
- メインタブ: 予告 / OP / 心 / 菜々 / ED（予告・OP・EDはプレースホルダー、後日更新）
- 心・菜々タブ内サブタブ: 山中 / 村 / 若返りの湯 / 岬 / 上空 / 絆Lv
- 各場所: お仕事①〜⑧、コミュイベント①〜③（本編＋ノーマル/グッド/パーフェクト）、
  スペシャルコミュイベント①〜③（同）
- 上空のみ: お仕事①〜③、コミュイベント①、スペシャルコミュイベント①
- 絆Lv: アップセリフ①〜③、到達セリフ①〜③
- 心の45番（コミュイベント(村)②本編）はスクショ未取得のため注記を表示

画像は 演出一覧（アイプロ）の並び順の通し番号と1:1対応（心・菜々とも同一構成）:
山中1-32 / 村33-64 / 若返りの湯65-96 / 岬97-128 / 上空129-139 / 絆Lv140-145
"""
import html
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
PAGE = REPO / "Deresute" / "Event" / "IdolProduce1st.html"
CDN_ROOT = "https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/Event/IdolProduce1st"

IDOLS = [
    # (表示名, タブID接頭辞, テキストJSON, Cloudinaryサブフォルダ)
    ("心", "ip1", "idolproduce1st_texts.json", "commu"),
    ("菜々", "ip1n", "idolproduce1st_nana_texts.json", "commu_nana"),
]

BRANCHES = ["ノーマル", "グッド", "パーフェクト"]
CIRCLED = "①②③④⑤⑥⑦⑧"

# 場所ごとの構成（開始番号, お仕事数, コミュ数, スペシャル数）
LOCATIONS = [
    ("山中", "yama", 1, 8, 3, 3),
    ("村", "mura", 33, 8, 3, 3),
    ("若返りの湯", "yu", 65, 8, 3, 3),
    ("岬", "misaki", 97, 8, 3, 3),
    ("上空", "sky", 129, 3, 1, 1),
]


class IdolData:
    def __init__(self, name: str, prefix: str, json_name: str, cdn_sub: str):
        self.name = name
        self.prefix = prefix
        data = json.loads((REPO / "scripts" / json_name).read_text(encoding="utf-8"))
        self.texts = data["items"]
        self.missing = set(int(x) for x in data.get("missing", []))
        self.cdn = f"{CDN_ROOT}/{cdn_sub}"


def row(idol: IdolData, no: int, label: str, loc: str) -> str:
    """shot付きセリフ行を生成。撮り漏れ番号は注記を出す"""
    if no in idol.missing:
        return (
            '        <div class="ev-dialog-row no-shot"><div class="ev-text">'
            f'<div class="ev-condition"><span class="ev-label">{html.escape(label)}</span></div>'
            '<div class="dss-stage-text">このセリフはスクリーンショット未取得のため、後日追加予定です。</div>'
            "</div></div>"
        )
    text = idol.texts[str(no)]
    alt = f"{label}（{loc}） {idol.name}のセリフ" if loc else f"{label} {idol.name}のセリフ"
    return (
        f'        <div class="ev-dialog-row"><div class="ev-shot">'
        f'<img src="{idol.cdn}/{no:04d}" alt="{html.escape(alt)}" loading="lazy"></div>'
        f'<div class="ev-text">'
        f'<div class="ev-condition"><span class="ev-label">{html.escape(label)}</span></div>'
        f'<div class="ud-dialogue"><span class="speaker" data-who="{idol.name}">{idol.name}</span>'
        f'<div class="line">{html.escape(text)}</div></div>'
        f"</div></div>"
    )


def location_panel(idol: IdolData, name: str, tid: str, start: int,
                   n_work: int, n_commu: int, n_sp: int, active: bool) -> str:
    out = []
    cls = "tab-panel active" if active else "tab-panel"
    out.append(f'    <div class="{cls}" data-tab="{idol.prefix}-{tid}">')
    out.append('    <div class="dss-ep-head"><div class="dss-ep-meta">')
    out.append(f'        <div class="dss-ep-eyebrow">{"佐藤心" if idol.name == "心" else "安部菜々"} / IDOL PRODUCE</div>')
    out.append(f'        <h3 class="dss-ep-title">{name}</h3>')
    out.append("    </div></div>")
    no = start

    # お仕事
    out.append('    <div class="ip1-group">')
    out.append('    <div class="ip1-group-head">お仕事</div>')
    out.append('    <div class="dss-lines">')
    for i in range(n_work):
        out.append(row(idol, no, f"お仕事{CIRCLED[i]}", name))
        no += 1
    out.append("    </div>")
    out.append("    </div>")

    # コミュイベント / スペシャルコミュイベント
    for kind, count in (("コミュイベント", n_commu), ("スペシャルコミュイベント", n_sp)):
        for i in range(count):
            out.append('    <div class="ip1-group">')
            out.append(f'    <div class="ip1-group-head">{kind}{CIRCLED[i]}</div>')
            out.append('    <div class="dss-lines">')
            out.append(row(idol, no, "イベント発生", name))
            no += 1
            for br in BRANCHES:
                out.append(row(idol, no, br, name))
                no += 1
            out.append("    </div>")
            out.append("    </div>")

    out.append("    </div>")
    return "\n".join(out)


def kizuna_panel(idol: IdolData) -> str:
    out = []
    out.append(f'    <div class="tab-panel" data-tab="{idol.prefix}-kizuna">')
    out.append('    <div class="dss-ep-head"><div class="dss-ep-meta">')
    out.append(f'        <div class="dss-ep-eyebrow">{"佐藤心" if idol.name == "心" else "安部菜々"} / IDOL PRODUCE</div>')
    out.append('        <h3 class="dss-ep-title">絆Lv</h3>')
    out.append("    </div></div>")
    no = 140
    for kind in ("絆Lvアップセリフ", "絆Lv到達セリフ"):
        out.append('    <div class="ip1-group">')
        out.append(f'    <div class="ip1-group-head">{kind}</div>')
        out.append('    <div class="dss-lines">')
        for i in range(3):
            out.append(row(idol, no, f"{kind}{CIRCLED[i]}", ""))
            no += 1
        out.append("    </div>")
        out.append("    </div>")
    out.append("    </div>")
    return "\n".join(out)


def idol_panel(idol: IdolData, active: bool) -> str:
    """メインタブ1枚分（サブタブ入り）"""
    out = []
    cls = "tab-panel active" if active else "tab-panel"
    out.append(f'    <div class="{cls}" data-tab="{idol.prefix}-main">')
    out.append('    <div class="tab-group ip1-sub">')
    out.append('        <div class="tab-list">')
    tabs = [("yama", "山中"), ("mura", "村"), ("yu", "若返りの湯"),
            ("misaki", "岬"), ("sky", "上空"), ("kizuna", "絆Lv")]
    for i, (tid, name) in enumerate(tabs):
        c = "tab-item active" if i == 0 else "tab-item"
        out.append(f'            <button class="{c}" onclick="switchTab(this,\'{idol.prefix}-{tid}\')">{name}</button>')
    out.append("        </div>")
    for name, tid, start, w, c, s in LOCATIONS:
        out.append(location_panel(idol, name, tid, start, w, c, s, tid == "yama"))
    out.append(kizuna_panel(idol))
    out.append("    </div>")
    out.append("    </div>")
    return "\n".join(out)


def placeholder_panel(tid: str, label: str) -> str:
    return (
        f'    <div class="tab-panel" data-tab="{tid}">\n'
        f'        <p class="box-text placeholder-text">{label}のコミュは後日更新予定です。</p>\n'
        f"    </div>"
    )


idols = [IdolData(*args) for args in IDOLS]

frag = []
frag.append('<section class="tab-group dss-commu">')
frag.append('    <div class="tab-list">')
frag.append('        <button class="tab-item" onclick="switchTab(this,\'ip1-trailer\')">予告</button>')
frag.append('        <button class="tab-item" onclick="switchTab(this,\'ip1-op\')">OP</button>')
frag.append('        <button class="tab-item active" onclick="switchTab(this,\'ip1-main\')">心</button>')
frag.append('        <button class="tab-item" onclick="switchTab(this,\'ip1n-main\')">菜々</button>')
frag.append('        <button class="tab-item" onclick="switchTab(this,\'ip1-ed\')">ED</button>')
frag.append("    </div>")
frag.append(placeholder_panel("ip1-trailer", "予告"))
frag.append(placeholder_panel("ip1-op", "OP"))
frag.append(idol_panel(idols[0], active=True))
frag.append(idol_panel(idols[1], active=False))
frag.append(placeholder_panel("ip1-ed", "ED"))
frag.append("</section>")
fragment = "\n".join(frag)

page = PAGE.read_text(encoding="utf-8")
START = "<!-- IP1-COMMU-START -->"
END = "<!-- IP1-COMMU-END -->"
assert START in page and END in page, "マーカーが見つかりません"
before = page.split(START)[0]
after = page.split(END)[1]
PAGE.write_text(before + START + "\n" + fragment + "\n" + END + after, encoding="utf-8")

n_rows = fragment.count("ev-dialog-row")
print(f"生成完了: {n_rows} 行（うち注記 {fragment.count('no-shot')} 行）を書き込みました")
