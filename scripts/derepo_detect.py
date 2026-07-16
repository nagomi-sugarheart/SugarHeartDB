# -*- coding: utf-8 -*-
"""でれぽ元スクショから投稿（アイコン枠）を検出する。

各でれぽ投稿は左端に固定位置の角丸正方形アイコン（枠 x[27,136]、約109px角）を持つ。
枠は彩度の高い色付き境界なので、x[27,136]の彩度>閾値の行連続からアイコン上端を検出する。
各画像 = 1スレッド（先頭=親、以降=返信）。

usage: python derepo_detect.py <image_number>   # 検証用に境界を表示
"""
import sys, json
import numpy as np
from PIL import Image
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
SRC = Path(r"G:\マイドライブ\でれぽ")

ICON_X0, ICON_X1 = 27, 136          # アイコン枠の左右（UI固定）
CROP_X0, CROP_X1 = 26, 137          # 切り出し（枠に左右均等の余白）
CROP_H = 111

def src_path(n):
    p = SRC / f"{n}.jpeg"
    if p.exists(): return p
    # 54_2021.09.10.jpeg のような日付入り
    for q in SRC.glob(f"{n}_*.jpeg"): return q
    raise FileNotFoundError(n)

def detect_icons(img, thr=22):
    """アイコン列 x[18,118] の行方向分散でアイコン（＝投稿）の上端を検出。
    アイコンは絵柄で高分散、背景（白/薄ピンク）は低分散。返り値は枠上端yのリスト。"""
    g = np.asarray(img.convert("L")).astype(float)
    h = g.shape[0]
    rowstd = g[:, 18:118].std(axis=1)
    on = rowstd > thr
    tops = []
    y = 0
    while y < h:
        if on[y]:
            s = y
            while y < h and on[y]: y += 1
            if (y - s) >= 70:               # アイコン高さ ~100-113
                tops.append(s - 5)          # 分散上端は枠上端より約5px下
        else:
            y += 1
    return tops

def detect_icons_n(img, target):
    """書き起こしの投稿数 target に一致する閾値でアイコンを検出する。
    淡いアイコンを取りこぼす/背景を拾う場合に閾値を調整して数を合わせる。"""
    if target is None:
        return detect_icons(img)
    for thr in [22, 21, 20, 19, 18, 23, 24, 17, 25, 16, 26]:
        tops = detect_icons(img, thr)
        if len(tops) == target:
            return tops
    return detect_icons(img)                  # 合わなければ既定

def main():
    n = int(sys.argv[1])
    img = Image.open(src_path(n))
    tops = detect_icons(img)
    print(f"画像{n}: サイズ{img.size} 検出アイコン数={len(tops)}")
    for i, t in enumerate(tops):
        role = "親" if i == 0 else "返信"
        print(f"  [{i}] {role} icon_top={t}")

if __name__ == "__main__":
    main()
