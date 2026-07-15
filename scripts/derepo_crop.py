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
IMGDIR.mkdir(exist_ok=True); BOXDIR.mkdir(exist_ok=True)

CROP_X0, CROP_X1, CROP_H = 26, 137, 111
PH_X0, PH_X1 = 122, 1088             # 添付写真の想定x範囲

def detect_photo(a, y0, y1):
    """[y0,y1)内で添付写真の帯を探す。x[140,1060]の平均彩度が高い連続行。"""
    seg = a[y0:y1, 140:1060, :]
    if seg.shape[0] < 60: return None
    sat = seg.max(2) - seg.min(2)
    rowsat = sat.mean(axis=1)
    on = rowsat > 45
    best = None
    y = 0; n = len(on)
    while y < n:
        if on[y]:
            s = y
            while y < n and on[y]: y += 1
            if (y - s) >= 120:               # 十分な高さ=写真
                if best is None or (y - s) > (best[1] - best[0]):
                    best = (s, y)
        else:
            y += 1
    if best:
        s, e = best
        # 低閾値で上下端まで拡張（写真の淡い縁を取りこぼさない）
        while s > 0 and rowsat[s - 1] > 26: s -= 1
        while e < n and rowsat[e] > 26: e += 1
        return (y0 + max(0, s - 3), y0 + e + 3)
    return None

def process(n, save=True):
    img = Image.open(src_path(n)).convert("RGB")
    a = np.asarray(img).astype(int)
    H = img.size[1]
    tops = detect_icons(img)
    posts = []
    for i, t in enumerate(tops):
        y_next = tops[i + 1] if i + 1 < len(tops) else H
        # アバター
        box_av = (CROP_X0, max(0, t), CROP_X1, min(H, t + CROP_H))
        # 写真: このアイコン下端〜次アイコンの手前で探索
        ph = detect_photo(a, min(H, t + CROP_H + 4), y_next)
        rec = {"i": i, "parent": i == 0, "icon_top": t, "photo": None}
        if save:
            img.crop(box_av).save(IMGDIR / f"{n}_{i}_av.png")
        if ph:
            rec["photo"] = [PH_X0, ph[0], PH_X1, ph[1]]
            if save:
                img.crop((PH_X0, ph[0], PH_X1, ph[1])).save(IMGDIR / f"{n}_{i}_photo.png")
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
        print(f"  [{p['i']}] {'親' if p['parent'] else '返信'} top={p['icon_top']} photo={p['photo']}")

if __name__ == "__main__":
    main()
