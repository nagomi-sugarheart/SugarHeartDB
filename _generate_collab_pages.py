#!/usr/bin/env python3
"""Generate individual collab detail pages under General/Collab/."""
import os

BASE_DIR = "/home/user/SugarHeartDB"

# (id, folder_name) mapping
ENTRIES = [
    ("tokyuhands-2018",                    "20181006_tokyuhands"),
    ("itaindo-3rd-2018",                   "20181025_itaindo3rd"),
    ("natsupara-figure-2018",              "20181201_natsupara-figure"),
    ("heartoheart-figure-2019",            "20191101_heartoheart-figure"),
    ("acrylic-petit-13-2019",              "20190401_acrylic-petit13"),
    ("pubmirror-ordermade-2020",           "20200722_pubmirror"),
    ("atre-akihabara-2020",                "20200901_atre-akihabara"),
    ("animate-crossjapan-2020",            "20200926_animate-crossjapan"),
    ("go-just-go-2020",                    "20201117_go-just-go"),
    ("grafart-2020",                       "20201121_grafart"),
    ("capsule-rubber-name-2020",           "20201215_capsule-rubber-name"),
    ("acrylic-petit-20-2020",              "20201101_acrylic-petit20"),
    ("unit-ring-sugasuga-2021",            "20210330_unit-ring-sugasuga"),
    ("tanita-2021",                        "20210915_tanita"),
    ("prize-figure-brilliant-2021",        "20211021_prize-figure-brilliant"),
    ("sanrio-animate-2021",                "20211113_sanrio-animate"),
    ("lawson-2021",                        "20211116_lawson"),
    ("costume-memories-2021",              "20211119_costume-memories"),
    ("atre-akihabara-2021",                "20211120_atre-akihabara"),
    ("tshirt-10th-2021",                   "20211129_tshirt-10th"),
    ("magical-wonderland-preorder-2021",   "20211228_magical-wonderland-preorder"),
    ("capsule-rubber-10th-2022",           "20220111_capsule-rubber-10th"),
    ("tshirt-10th-resale-2022",            "20220224_tshirt-10th-resale"),
    ("magical-wonderland-goods-2022",      "20220403_magical-wonderland-goods"),
    ("seiko-watch-10th-2022",              "20220403_seiko-watch-10th"),
    ("acrylic-28-2022",                    "20220601_acrylic-petit28"),
    ("tower-records-2022",                 "20220623_tower-records"),
    ("popmas-final-2022",                  "20220720_popmas-final"),
    ("donzara-2022",                       "20221126_donjara"),
    ("mini-tapestry-2022",                 "20221214_mini-tapestry"),
    ("garapon-sd-2023",                    "20230208_garapon-sd"),
    ("glass-ono-shiga-2023",               "20230310_glass-ono-shiga"),
    ("arigato-exhibition-2023",            "20230421_arigato-exhibition"),
    ("oh-my-glasses-2023",                 "20230421_oh-my-glasses"),
    ("volks-dollfie-2023",                 "20230423_volks-dollfie"),
    ("animate-cafe-birthday-2023",         "20230702_animate-cafe-birthday"),
    ("kotobukiya-clock-2023",              "20230722_kotobukiya-clock"),
    ("shadowverse-evolve-2023",            "20230825_shadowverse-evolve"),
    ("cinderella-master-campaign-2023",    "20230911_cinderella-master-campaign"),
    ("hiromedo-winery-1-2023",             "20231110_hiromedo-winery1"),
    ("cure-maid-cafe-2023",                "20231123_cure-maid-cafe"),
    ("kotobukiya-popup-2023",              "20231208_kotobukiya-popup"),
    ("animate-cafe-chinese-2023",          "20231225_animate-cafe-chinese"),
    ("gift-plush-2023",                    "20231230_gift-plush"),
    ("village-vanguard-2024",              "20240628_village-vanguard"),
    ("hiromedo-winery-2-2024",             "20240703_hiromedo-winery2"),
    ("hub-rose-shot-2024",                 "20240902_hub-rose-shot"),
    ("yokohama-worldporters-2024",         "20240913_yokohama-worldporters"),
    ("jr-tokai-2024",                      "20241115_jr-tokai"),
    ("glass-ono-shoe-2024",                "20241126_glass-ono-shoe"),
    ("yurakucho-marui-2025",               "20250111_yurakucho-marui"),
    ("deresute-10th-goods-2025",           "20250121_deresute-10th-goods"),
    ("deresute-10th-garapon-2025",         "20250131_deresute-10th-garapon"),
    ("fragments-exhibition-2025",          "20250207_fragments-exhibition"),
    ("bushiroad-card-supply-2025",         "20250207_bushiroad-card-supply"),
    ("okinawa-orion-2025",                 "20250606_okinawa-orion"),
    ("leisurefes-2025",                    "20250604_leisurefes"),
    ("seibu-en-2025",                      "20250606_seibu-en"),
    ("birthday-collection-zodiac-2025",    "20250620_birthday-collection-zodiac"),
    ("karikoe-2025",                       "20250801_karikoe"),
    ("shadowverse-evolve-2025",            "20250822_shadowverse-evolve2"),
    ("amiami-popup-2025",                  "20250829_amiami-popup"),
    ("card-folio-2025",                    "20250906_card-folio"),
    ("seiko-watch-2025",                   "20250906_seiko-watch"),
    ("cinderella-fes-preorder-2025",       "20250908_cinderella-fes-preorder"),
    ("kyomaf-2025",                        "20250920_kyomaf"),
    ("customize-tshirt-2025",              "20251128_customize-tshirt"),
    ("onkyo-earphone-2025",                "20251128_onkyo-earphone"),
    ("takeup-jewelry-2025",                "20251129_takeup-jewelry"),
    ("starlight-alliance-merch-2025",      "20251129_starlight-alliance-merch"),
    ("starlight-stage-with-2025",          "20251213_starlight-stage-with"),
    ("pubmirror-konoyode-2025",            "20251218_pubmirror-konoyode"),
    ("sweets-paradise-2026",               "20260116_sweets-paradise"),
    ("rascal-collab-2026",                 "20260328_rascal"),
    ("once-upon-memorial-cafe-2026",       "20260417_once-upon-memorial-cafe"),
    ("astromeda-tbd",                      "99991231_astromeda"),
]

TEMPLATE = '''\
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <base href="/SugarHeartDB/">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>コラボ詳細｜SugarHeartDB</title>
    <meta name="description" content="アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）のコラボ・グッズ詳細ページです。">
    <meta name="author" content="なごみ（@nagomi_IMCG）">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="コラボ詳細｜SugarHeartDB">
    <meta property="og:description" content="アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）のコラボ・グッズ詳細ページです。">
    <meta property="og:site_name" content="SugarHeartDB">
    <meta property="og:image" content="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/KonoyoDeTadaHitoriNoHeart+/KonoyoDeTadaHitoriNoHeart+">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="コラボ詳細｜SugarHeartDB">
    <link rel="icon" type="image/png" sizes="32x32" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-32x32">
    <link rel="icon" type="image/png" sizes="16x16" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-16x16">
    <link rel="apple-touch-icon" sizes="180x180" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/apple-touch-icon">
    <link rel="stylesheet" href="style.css">
</head>
<body>
<script src="components/header.js"></script>

<div id="detail-root" class="sh-container">
    <div style="color:var(--sh-text-mute); padding:60px 0; text-align:center; font-size:0.95rem;">読み込み中…</div>
</div>

<script src="General/collab-data.js"></script>
<script>
/* ======== このページの設定 ======== */
var ENTRY_ID   = '__ENTRY_ID__';
var ENTRY_PATH = '__ENTRY_PATH__';

/* ======== 画像ファイル一覧
   このフォルダに画像を追加した後、ファイル名をここに記入してください。
   例: var PAGE_IMAGES = ["image1.jpg", "image2.png"];          */
var PAGE_IMAGES = [];

/* ======== 以下は変更不要 ======== */
(function () {
    function esc(s) {
        return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    function typeLabel(t) {
        if (t === 'collab')   return '<span class="sh-tag" data-tag="collab">コラボ</span>';
        if (t === 'goods')    return '<span class="sh-tag" data-tag="goods">グッズ</span>';
        if (t === 'campaign') return '<span class="sh-tag" data-tag="ranking">キャンペーン</span>';
        return '';
    }

    function accentBorderColor(types) {
        if (types.indexOf('campaign') !== -1) return 'var(--tag-ranking)';
        if (types.indexOf('collab')   !== -1) return 'var(--tag-collab)';
        return 'var(--sh-pink)';
    }

    function findIndex(id) {
        for (var i = 0; i < COLLAB_DATA.length; i++) {
            if (COLLAB_DATA[i].id === id) return i;
        }
        return -1;
    }

    var root = document.getElementById('detail-root');
    var idx  = findIndex(ENTRY_ID);
    var d    = idx !== -1 ? COLLAB_DATA[idx] : null;

    if (!d) {
        root.innerHTML = '<div class="page-hero"><div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> &middot; <a href="General/CollabList.html">コラボ・グッズ一覧</a></div><h1>404 &mdash; 見つかりません</h1><p class="summary" style="color:var(--sh-text-mute);">指定されたページが見つかりませんでした。<br><a href="General/CollabList.html" class="sh-pill primary" style="display:inline-flex;margin-top:12px;">一覧へ戻る ▶</a></p></div>';
        return;
    }

    document.title = d.title + '｜SugarHeartDB';
    document.querySelector('meta[property="og:title"]').setAttribute('content', d.title + '｜SugarHeartDB');
    document.querySelector('meta[name="description"]').setAttribute('content', d.title + '（' + d.dateDisplay + '）— SugarHeartDB');

    var prev   = idx > 0 ? COLLAB_DATA[idx - 1] : null;
    var next   = idx < COLLAB_DATA.length - 1 ? COLLAB_DATA[idx + 1] : null;
    var badges = d.types.map(typeLabel).join(' ');
    var border = accentBorderColor(d.types);

    /* ヒーロー */
    var heroHtml = '<div class="collab-detail-hero" style="border-left:4px solid ' + border + ';">';
    heroHtml += '<div class="tag-row">' + badges + '</div>';
    heroHtml += '<h1>' + esc(d.title) + '</h1>';
    if (d.subtitle) {
        heroHtml += '<div style="font-size:0.92rem; color:var(--sh-text-soft); margin-bottom:8px;">' + esc(d.subtitle) + '</div>';
    }
    heroHtml += '<div class="date-row"><span class="icon">\\uD83D\\uDCC5</span><span>' + esc(d.dateDisplay) + '</span></div>';
    heroHtml += '</div>';

    /* 画像ギャラリー */
    var galleryHtml = '';
    if (typeof PAGE_IMAGES !== 'undefined' && PAGE_IMAGES.length > 0) {
        galleryHtml += '<div class="box-area" style="margin-bottom:16px;">';
        galleryHtml += '<div class="box-title">画像</div>';
        galleryHtml += '<div class="collab-image-gallery">';
        PAGE_IMAGES.forEach(function (img) {
            var src = ENTRY_PATH + '/' + img;
            galleryHtml += '<a href="' + esc(src) + '" target="_blank" rel="noopener">';
            galleryHtml += '<img src="' + esc(src) + '" alt="' + esc(d.title) + '" loading="lazy">';
            galleryHtml += '</a>';
        });
        galleryHtml += '</div>';
        galleryHtml += '</div>';
    }

    /* メモ */
    var noteHtml = '';
    if (d.note) {
        noteHtml += '<div class="box-area" style="margin-bottom:16px;">';
        noteHtml += '<div class="box-title">メモ</div>';
        noteHtml += '<p class="box-text">' + esc(d.note) + '</p>';
        noteHtml += '</div>';
    }

    /* リンク */
    var linksHtml = '';
    if (d.links && d.links.length > 0) {
        linksHtml += '<div class="box-area" style="margin-bottom:16px;">';
        linksHtml += '<div class="box-title">関連リンク</div>';
        linksHtml += '<div class="collab-link-list">';
        d.links.forEach(function (lk) {
            linksHtml += '<a href="' + esc(lk.url) + '" target="_blank" rel="noopener noreferrer">' + esc(lk.label) + '</a>';
        });
        linksHtml += '</div>';
        linksHtml += '</div>';
    } else {
        linksHtml += '<div class="box-area" style="margin-bottom:16px;">';
        linksHtml += '<div class="box-title">関連リンク</div>';
        linksHtml += '<p class="box-text" style="color:var(--sh-text-mute);">公式リンク情報はありません。</p>';
        linksHtml += '</div>';
    }

    /* 前後ナビ */
    var navHtml = '<div class="card-navigation" style="margin-top:24px;">';
    if (prev && prev.path) {
        navHtml += '<a href="' + prev.path + '/" class="nav-card nav-prev">';
        navHtml += '<span class="nav-arrow">\\u2190</span>';
        navHtml += '<div class="nav-card-info"><span class="nav-label">\\u2190 PREV</span><span class="nav-card-name">' + esc(prev.title) + '</span></div>';
        navHtml += '</a>';
    }
    if (next && next.path) {
        navHtml += '<a href="' + next.path + '/" class="nav-card nav-next">';
        navHtml += '<div class="nav-card-info"><span class="nav-label">NEXT \\u2192</span><span class="nav-card-name">' + esc(next.title) + '</span></div>';
        navHtml += '<span class="nav-arrow">\\u2192</span>';
        navHtml += '</a>';
    }
    navHtml += '</div>';

    root.innerHTML =
        '<section class="page-hero">' +
            '<div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <a href="General/CollabList.html">コラボ・グッズ一覧</a> · <strong>' + esc(d.title) + '</strong></div>' +
        '</section>' +
        heroHtml +
        galleryHtml +
        noteHtml +
        linksHtml +
        '<div style="margin-top:20px;"><a href="General/CollabList.html" class="sh-pill ghost">← 一覧へ戻る</a></div>' +
        navHtml;
})();
</script>
</body>
</html>
'''

def make_page(entry_id, folder):
    rel_path = f"General/Collab/{folder}"
    html = TEMPLATE.replace('__ENTRY_ID__', entry_id).replace('__ENTRY_PATH__', rel_path)
    full_dir = os.path.join(BASE_DIR, rel_path)
    os.makedirs(full_dir, exist_ok=True)
    with open(os.path.join(full_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    return rel_path

if __name__ == "__main__":
    for entry_id, folder in ENTRIES:
        path = make_page(entry_id, folder)
        print(f"Created: {path}/index.html")
    print(f"\nDone: {len(ENTRIES)} pages created.")
