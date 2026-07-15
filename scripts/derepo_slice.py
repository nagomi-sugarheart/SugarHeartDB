# -*- coding: utf-8 -*-
"""でれぽ書き起こし支援: 指定画像の検出構造を表示し、読み取り用スライスを出力する。

- 投稿数・各投稿の写真/スタンプ有無を表示（書き起こしJSONはこの投稿数・順序に一致させる）
- scripts/derepo_slices/{N}/s{k}.png に、全体を読める幅で縦分割して保存
usage: python derepo_slice.py <N>
"""
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
from derepo_detect import src_path
from derepo_crop import process

REPO = Path(__file__).parent.parent
SLICEDIR = REPO / "scripts" / "derepo_slices"

def main():
    n = int(sys.argv[1])
    posts = process(n, save=False)                 # 検出のみ（切り出し保存なし）
    img = Image.open(src_path(n)).convert("RGB")
    w, h = img.size
    outdir = SLICEDIR / str(n)
    outdir.mkdir(parents=True, exist_ok=True)
    for f in outdir.glob("*.png"): f.unlink()
    scale = 0.62
    step = 1000                                    # native 1000pxごと（重なり120px）
    k = 0; y = 0
    while y < h:
        b = min(h, y + step + 120)
        c = img.crop((0, y, w, b)).resize((int(w * scale), int((b - y) * scale)))
        c.save(outdir / f"s{k}.png")
        k += 1
        if b >= h: break
        y += step
    print(f"画像{n}: 投稿数={len(posts)}  スライス={k}枚 -> {outdir}")
    for p in posts:
        att = "写真" if p["photo"] else ("スタンプ" if p["stamp"] else "-")
        print(f"  [{p['i']}] {'親' if p['parent'] else '返信'} 添付={att}")

if __name__ == "__main__":
    main()
