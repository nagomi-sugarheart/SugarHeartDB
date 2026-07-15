# -*- coding: utf-8 -*-
"""でれぽ元スクショから各投稿のアバターと添付写真を切り出す。

- アバター: 枠 x[26,137]、上端=検出アイコン上端、111px角
- 写真: 投稿のテキスト下に現れる大きな色付き画像帯（x[140,1060]の平均彩度が高い連続行）
出力: scripts/derepo_img/{N}_{i}_av.png / {N}_{i}_photo.png
検出結果（写真の有無・box）は scripts/derepo_boxes/{N}.json に保存。
"""
import sys, json
import numpy as np
from PIL import Image
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from derepo_detect import detect_icons, src_path

REPO = Path(__file__).parent.parent
IMGDIR = REPO / "scripts" / "derepo_img"
BOXDIR = REPO / "scripts" / "derepo_boxes"
TEXTDIR = REPO / "scripts" / "derepo_text"
IMGDIR.mkdir(exist_ok=True); BOXDIR.mkdir(exist_ok=True)

def load_hints(n):
    """書き起こしJSONの各投稿 att（"photo"/"stamp"）をヒントとして返す。"""
    p = TEXTDIR / f"{n}.json"
    if not p.exists(): return None
    posts = json.loads(p.read_text(encoding="utf-8")).get("posts", [])
    return [pp.get("att") for pp in posts]

CROP_X0, CROP_X1, CROP_H = 26, 137, 111
PH_X0, PH_X1 = 122, 1088             # 添付写真の切り出しx範囲
DET_X0 = 140                          # 添付検出のx開始（アバター枠 x..137 を避ける）

def _runs(mask, gap, minlen):
    """Trueの連続run（ギャップ<=gapを連結、長さ>=minlen）を返す。"""
    n = len(mask); f = mask.copy(); y = 0
    while y < n:
        if not f[y]:
            s = y
            while y < n and not f[y]: y += 1
            if 0 < s and y < n and (y - s) <= gap: f[s:y] = True
        else:
            y += 1
    out = []; y = 0
    while y < n:
        if f[y]:
            s = y
            while y < n and f[y]: y += 1
            if (y - s) >= minlen: out.append((s, y))
        else:
            y += 1
    return out

def detect_attachment(a, y0, y1):
    """[y0,y1)内で添付画像（写真/スタンプ）を探す。
    彩度コアで検出→輪郭込みで全体を切り出す。横に広い(>500px)=写真、狭い=スタンプ。
    返り値 (kind, (x0,y0,x1,y1)) or None。"""
    if y1 - y0 < 55: return None
    seg = a[y0:y1, DET_X0:PH_X1, :]         # アバター枠を避けて検出
    sat = seg.max(2) - seg.min(2)
    gray = seg.mean(2)
    core = sat > 80                          # 絵柄の彩度コア（淡い背景を除外）
    runs = _runs(core.sum(axis=1) > 10, 20, 44)
    if not runs: return None
    s, e = max(runs, key=lambda r: r[1] - r[0])
    # x範囲（コアの色付き列）
    colf = core[s:e].mean(axis=0)
    cols = np.where(colf > 0.15)[0]
    if len(cols) == 0: return None
    xl, xr = int(cols.min()), int(cols.max())
    width = xr - xl
    # 輪郭込みで全体に拡張（彩度 or 暗い輪郭）。写真はフル幅、スタンプはx範囲内で。
    content = (sat > 60) | (gray < 140)
    if width > 500:                          # 写真
        rc = content.sum(axis=1) > 60
        rr = _runs(rc, 12, 100)
        if rr:
            s, e = max(rr, key=lambda r: r[1] - r[0])
        return ("photo", (PH_X0, y0 + max(0, s - 3), PH_X1, y0 + e + 3))
    # スタンプ: x[xl,xr]内の content 行で上下に拡張
    sub = content[:, xl:xr + 1].sum(axis=1) > max(6, (xr - xl) * 0.12)
    rr = _runs(sub, 14, 40)
    if rr:
        s, e = max(rr, key=lambda r: r[1] - r[0])
    x0 = max(PH_X0, DET_X0 + xl - 14); x1 = min(PH_X1, DET_X0 + xr + 14)
    return ("stamp", (x0, y0 + max(0, s - 6), x1, y0 + e + 6))

def fallback_box(a, t, y_next, kind):
    """自動検出が拾えなかった添付の箱を、輪郭(暗い)＋彩度で推定する。
    kind='photo' はフル幅、'stamp' はアバター右の絵柄範囲。"""
    H = a.shape[0]
    y0 = min(H, t + 46)                       # 名前行の下から
    y1 = min(H, y_next - 2)
    if y1 - y0 < 30: return None
    x0d = DET_X0
    seg = a[y0:y1, x0d:PH_X1, :]
    sat = seg.max(2) - seg.min(2); gray = seg.mean(2)
    content = (sat > 45) | (gray < 150)
    rows = _runs(content.sum(axis=1) > 25, 18, 40)
    if not rows: return None
    s, e = max(rows, key=lambda r: r[1] - r[0])
    colf = content[s:e].mean(axis=0)
    cols = np.where(colf > 0.12)[0]
    if kind == "stamp":                        # スタンプは左側。右のタイムスタンプを除外
        cols = cols[cols < (620 - x0d)]
    if len(cols) == 0: return None
    xl, xr = int(cols.min()), int(cols.max())
    ay0, ay1 = y0 + max(0, s - 5), y0 + e + 5
    if kind == "photo":
        return (PH_X0, ay0, PH_X1, ay1)
    return (max(PH_X0, x0d + xl - 14), ay0, min(PH_X1, x0d + xr + 14), ay1)

def process(n, save=True, hints=None):
    if hints is None:
        hints = load_hints(n)
    img = Image.open(src_path(n)).convert("RGB")
    a = np.asarray(img).astype(int)
    H = img.size[1]
    tops = detect_icons(img)
    posts = []
    for i, t in enumerate(tops):
        y_next = tops[i + 1] if i + 1 < len(tops) else H
        box_av = (CROP_X0, max(0, t), CROP_X1, min(H, t + CROP_H))
        att = detect_attachment(a, min(H, t + 8), y_next)   # (kind, box) or None
        hint = hints[i] if (hints and i < len(hints)) else None
        kind, box = (att if att else (None, None))
        if hint in ("photo", "stamp"):        # 書き起こし側の判定を優先
            kind = hint
            if box is None:
                box = fallback_box(a, t, y_next, hint)
        elif hint is False:                    # 添付なしと明示
            kind, box = None, None
        rec = {"i": i, "parent": i == 0, "icon_top": t, "photo": None, "stamp": None}
        if save:
            img.crop(box_av).save(IMGDIR / f"{n}_{i}_av.png")
        if kind and box:
            rec[kind] = list(box)
            if save:
                img.crop(tuple(box)).save(IMGDIR / f"{n}_{i}_{kind}.png")
        posts.append(rec)
    if save:
        (BOXDIR / f"{n}.json").write_text(json.dumps({"image": n, "size": img.size, "posts": posts},
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
    return posts

def main():
    n = int(sys.argv[1])
    posts = process(n)
    print(f"画像{n}: {len(posts)}投稿")
    for p in posts:
        att = "photo" if p["photo"] else ("stamp" if p["stamp"] else "-")
        print(f"  [{p['i']}] {'親' if p['parent'] else '返信'} top={p['icon_top']} 添付={att}")

if __name__ == "__main__":
    main()
