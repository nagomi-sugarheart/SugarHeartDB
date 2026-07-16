# -*- coding: utf-8 -*-
"""でれぽページ(Deresute/CinderellaTheater/Derepo.html)を生成する。

- scripts/derepo_text/{N}.json（書き起こし）と derepo_boxes/{N}.json（写真box）を読む
- 各画像 = 1スレッド（先頭=親、以降=返信）。新しい画像ほど番号が小さい → 0,1,2..順に表示
- 年の特定: 画像番号が小さいほど新しい。基準 54=2021-09-10。時系列(古→新)で月が
  12→1 に戻るたびに年+1。データが54を含まなければ最新(画像0)側を2024として後方へ割当。
"""
import sys, json, html
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).parent.parent
TEXT = REPO / "scripts" / "derepo_text"
BOX = REPO / "scripts" / "derepo_boxes"
OUT = REPO / "Deresute" / "CinderellaTheater" / "Derepo.html"
CDN = "https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/Derepo"

ANCHOR_IMG, ANCHOR_YEAR = 54, 2021    # 54_2021.09.10
NEWEST_YEAR = 2024                     # 画像0側（範囲は2018-04-27〜2024-03-31）

def esc(s): return html.escape(s, quote=True)

def load():
    imgs = {}
    for p in sorted(TEXT.glob("*.json"), key=lambda x: int(x.stem)):
        n = int(p.stem)
        t = json.loads(p.read_text(encoding="utf-8"))
        b = json.loads((BOX / f"{n}.json").read_text(encoding="utf-8")) if (BOX / f"{n}.json").exists() else {"posts": []}
        photos = {pp["i"]: bool(pp.get("photo")) for pp in b["posts"]}
        stamps = {pp["i"]: bool(pp.get("stamp")) for pp in b["posts"]}
        for i, post in enumerate(t["posts"]):
            post["photo"] = photos.get(i, False)
            post["stamp"] = stamps.get(i, False)
        imgs[n] = t["posts"]
    return imgs

def assign_years(imgs):
    """(image,post) を古→新に並べ、月の巻き戻りで年を割当てる。"""
    order = []                                   # 古い順: 画像降順・投稿昇順
    for n in sorted(imgs, reverse=True):
        for i, p in enumerate(imgs[n]):
            order.append((n, i, int(p["md"].split("-")[0])))
    if not order: return {}
    years = [None] * len(order)
    # まず相対的に年を割当（最初を0基準、月が減れば+1＝新しい年へ）
    y = 0; years[0] = 0
    for k in range(1, len(order)):
        if order[k][2] < order[k-1][2]:          # 月が 12→1 等に戻った＝翌年
            y += 1
        years[k] = y
    # 基準合わせ: アンカー画像があればそれで、無ければ最新(=最大y)をNEWEST_YEARに
    base = None
    for k, (n, i, mo) in enumerate(order):
        if n == ANCHOR_IMG:
            base = ANCHOR_YEAR - years[k]; break
    if base is None:
        base = NEWEST_YEAR - max(years)
    result = {}
    for k, (n, i, mo) in enumerate(order):
        result[(n, i)] = base + years[k]
    return result

def render_post(n, i, p, year, is_first, indent=False, side=False):
    is_parent = is_first
    date = f"{year}-{p['md']} {p.get('time','')}".strip()
    text = esc(p["text"])
    # #タグを強調
    import re
    text = re.sub(r"(#[^\s#]+)", r'<span class="dp-tag">\1</span>', text)
    star = p.get("star")
    star_html = f'<div class="dp-star"><b>★</b>{star}</div>' if star is not None else ""
    photo_html = ""
    cls = "dp"
    stamp_html = ""
    if p.get("stamp"):
        # スタンプ（小さな一枚絵）は本文下にインラインで表示
        stamp_html = f'\n        <div class="dp-stamp"><img class="lightbox-trigger" src="{CDN}/{n}/stamp{i}" alt="{esc(p["name"])}のスタンプ" loading="lazy"></div>'
    if p.get("photo"):
        photo_html = f'<div class="dp-photo"><img class="lightbox-trigger" src="{CDN}/{n}/photo{i}" alt="{esc(p["name"])}の投稿画像" loading="lazy"></div>'
        if side:                              # 親のみPCで本文と写真を横並び
            cls = "dp has-photo"
    src_html = (f'<div class="dp-src"><a href="{CDN}/src/{n}" target="_blank" rel="noopener">'
                f'📷 元の公式スクリーンショットを見る</a></div>') if is_first else ""
    reply_cls = " dp-reply" if indent else ""
    return (f'<article class="{cls}{reply_cls}">\n'
            f'      <div class="dp-body">\n'
            f'        <div class="dp-top">\n'
            f'          <img class="dp-avatar" src="{CDN}/{n}/av{i}" alt="{esc(p["name"])}" loading="lazy">\n'
            f'          <div class="dp-id"><div class="dp-name">{esc(p["name"])}</div><div class="dp-time">{esc(date)}</div></div>\n'
            f'          {star_html}\n'
            f'        </div>\n'
            f'        <div class="dp-text">{text}</div>{stamp_html}\n'
            f'        {src_html}\n'
            f'      </div>\n'
            f'      {photo_html}\n'
            f'    </article>')

def main():
    imgs = load()
    years = assign_years(imgs)
    threads = []
    for n in sorted(imgs):                        # 0,1,2.. = 新→古
        posts = imgs[n]
        if not posts: continue
        names = {p["name"] for p in posts}
        mixed = len(names) > 1                     # 複数アイドル→親＋返信、単独→フラット
        parent = render_post(n, 0, posts[0], years[(n, 0)], True, indent=False, side=mixed)
        rest = ""
        if len(posts) > 1:
            body = "\n    ".join(
                render_post(n, i, posts[i], years[(n, i)], False, indent=mixed, side=False)
                for i in range(1, len(posts)))
            if mixed:
                rest = f'\n    <div class="dp-replies">\n    {body}\n    </div>'
            else:
                rest = f'\n    {body}'
        threads.append(f'  <section class="dp-thread">\n    {parent}{rest}\n  </section>')
    feed = "\n".join(threads)
    n_posts = sum(len(v) for v in imgs.values())
    page = PAGE.replace("{{FEED}}", feed).replace("{{NIMG}}", str(len(imgs))).replace("{{NPOST}}", str(n_posts))
    OUT.write_text(page, encoding="utf-8")
    print(f"生成: {OUT}  スレッド{len(imgs)} 投稿{n_posts}")

PAGE = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <base href="/SugarHeartDB/">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>でれぽ（デレステ）｜SugarHeartDB</title>
    <meta name="description" content="アイドルマスターシンデレラガールズ デレステの「でれぽ」投稿を、書き起こしテキストとあわせてまとめたページです。">
    <meta name="author" content="なごみ（@nagomi_IMCG）">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="でれぽ（デレステ）｜SugarHeartDB">
    <meta property="og:description" content="デレステの「でれぽ」投稿を書き起こしとあわせてまとめたページです。">
    <meta property="og:site_name" content="SugarHeartDB">
    <meta property="og:image" content="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/KonoyoDeTadaHitoriNoHeart+/KonoyoDeTadaHitoriNoHeart+">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="でれぽ（デレステ）｜SugarHeartDB">
    <link rel="icon" type="image/png" sizes="32x32" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-32x32">
    <link rel="icon" type="image/png" sizes="16x16" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-16x16">
    <link rel="apple-touch-icon" sizes="180x180" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/apple-touch-icon">
    <link rel="stylesheet" href="style.css?v=20260708">
<style>
.derepo-wrap{max-width:720px;margin-inline:auto;padding:0 16px;}
.derepo-lead{padding:14px 2px 8px;color:var(--muted,#a99fb0);font-size:13px;}
.derepo-feed{padding:6px 0 60px;}
.dp-thread{margin-bottom:18px;}
.dp{background:#fff;border-radius:16px;box-shadow:0 2px 10px rgba(180,120,150,.10);
  overflow:hidden;display:grid;grid-template-columns:1fr;}
.dp.has-photo{grid-template-columns:1fr 300px;}
.dp-body{padding:16px 18px;min-width:0;}
.dp-top{display:flex;align-items:center;gap:12px;}
.dp-avatar{width:56px;height:56px;border-radius:14px;object-fit:cover;flex:none;
  box-shadow:0 1px 4px rgba(180,120,150,.18);}
.dp-id{flex:1;min-width:0;}
.dp-name{font-weight:700;font-size:16px;line-height:1.25;color:#3a3340;}
.dp-time{color:#a99fb0;font-size:12px;margin-top:3px;font-variant-numeric:tabular-nums;}
.dp-star{flex:none;display:flex;align-items:center;gap:4px;color:#a99fb0;font-size:13px;font-weight:600;}
.dp-star b{color:#ffb547;font-size:16px;font-weight:400;}
.dp-text{margin:12px 2px 0;font-size:15px;line-height:1.7;color:#3a3340;white-space:pre-wrap;word-break:break-word;}
.dp-tag{color:#ff8bb3;font-weight:600;}
.dp-src{margin:12px 2px 0;}
.dp-src a{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:#a99fb0;
  text-decoration:none;border:1px solid #f0e3ea;border-radius:999px;padding:4px 11px;}
.dp-src a:hover{color:#ff8bb3;border-color:#ff8bb3;}
.dp-photo{background:#f7eef3;}
.dp-photo img{display:block;width:100%;height:100%;object-fit:cover;cursor:zoom-in;}
.dp-stamp{margin:10px 2px 0;}
.dp-stamp img{display:block;width:auto;max-width:150px;max-height:170px;border-radius:10px;cursor:zoom-in;}
.dp-replies{margin:8px 0 0 34px;padding-left:16px;border-left:2px solid #f0e3ea;
  display:flex;flex-direction:column;gap:10px;}
.dp-reply .dp-avatar{width:46px;height:46px;border-radius:12px;}
.dp-reply .dp-name{font-size:15px;}
.dp-reply .dp-body{padding:13px 15px;}
.dp-reply.has-photo,.dp-reply{grid-template-columns:1fr;}
@media (max-width:640px){
  .dp,.dp.has-photo{grid-template-columns:1fr;}
  .dp-photo{order:2;}
  .dp-photo img{height:auto;}
  .dp-body{padding:14px 15px 13px;}
  .dp-name{font-size:15px;}
  .derepo-wrap{padding:0 14px;}
  .dp-replies{margin-left:16px;padding-left:11px;}
}
</style>
</head>
<body>
<script src="components/header.js"></script>

<section class="page-hero">
    <div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <a href="Deresute/index.html">DERESUTE</a> · <a href="Deresute/CinderellaTheater/CinderellaTheater.html">シンデレラシアター</a> · <strong>でれぽ</strong></div>
    <h1>でれぽ <span class="sub">/ DEREPO · DERESUTE</span></h1>
    <p class="summary">デレステの「でれぽ」投稿を、書き起こしテキストとあわせてまとめています。</p>
</section>

<div class="derepo-wrap">
  <div class="derepo-lead">全{{NIMG}}スレッド・{{NPOST}}投稿（新しい順）。各スレッドの一番上が親投稿、その下がぶら下がりの返信です。</div>
  <div class="derepo-feed">
{{FEED}}
  </div>
</div>

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
