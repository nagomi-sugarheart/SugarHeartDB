# -*- coding: utf-8 -*-
"""歌唱曲一覧（General/SongList.html）を生成する。
データ: scripts/songlist_data/{song_data,gamerch_data,gamerch_jackets,lives_data}.json
"""
import json, os, html, re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DD = os.path.join(BASE, 'scripts', 'songlist_data')
song_data = json.load(open(os.path.join(DD, 'song_data.json'), encoding='utf-8'))
gj = json.load(open(os.path.join(DD, 'gamerch_data.json'), encoding='utf-8'))
lives = json.load(open(os.path.join(DD, 'lives_data.json'), encoding='utf-8'))

CLOUD = 'https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/'

# 名前 -> ローマ字（アイコン）
name2rom = {}
for line in open(os.path.join(BASE, 'scripts', 'gekijo_name2rom.tsv'), encoding='utf-8'):
    line = line.rstrip('\n')
    if not line or '\t' not in line:
        continue
    n, r = line.split('\t')
    name2rom[n] = r
name2rom['イヴ・サンタクロース'] = 'evesantaclaus'

ATTR_CLASS = {'キュート': 'cute', 'クール': 'cool', 'パッション': 'passion', '全タイプ': 'all', '全属性': 'all'}
ATTR_LABEL = {'キュート': 'キュート', 'クール': 'クール', 'パッション': 'パッション', '全タイプ': '全タイプ', '全属性': '全タイプ'}

# 難易度の表示順
DIFF_ORDER = ['DEBUT', 'REGULAR', 'PRO', 'MASTER', 'MASTER+', 'ⓁMASTER+', 'PIANO', 'FORTE', 'LIGHT', 'TRICK']

# ---- 楽曲メタデータ（キュレーション） ----
# m765: song_data.json のキー / gj: gamerch_data.json のキー
SONGS = [
 dict(title='命燃やして恋せよ乙女', m765='命燃やして恋せよ乙女', gj='命燃やして恋せよ乙女',
      slug='inochi', unit='宵乙女', event='InochiMoyashiteKoiseyoOtome.html',
      singers=['高垣楓', '佐藤心', '三船美優', '安部菜々', '片桐早苗']),
 dict(title='Take me☆Take you', m765='Take me☆Take you', gj='Take me☆Take you',
      slug='takeme', unit='第5回シンデレラガール総選挙曲', event='TakeMeTakeYou.html',
      singers=['高垣楓', '三船美優', '森久保乃々', '島村卯月', '安部菜々', '前川みく', '依田芳乃', '本田未央', '佐藤心']),
 dict(title='SUN♡FLOWER', m765='SUN♡FLOWER', gj='SUN♡FLOWER',
      slug='sunflower', unit='しんげき1期 パッション属性ED', event='SunFlower.html',
      singers=['本田未央', '片桐早苗', '佐藤心', '城ヶ崎美嘉', '諸星きらり']),
 dict(title='Happy New Yeah!', m765='Happy New Yeah!', gj='Happy New Yeah!',
      slug='happynewyeah', unit=None, event='HappyNewYeah.html',
      singers=['島村卯月', '渋谷凛', '本田未央', '佐藤心', '三村かな子']),
 dict(title='CoCo夏夏夏Holiday', m765='CoCo夏夏夏 Holiday', gj='CoCo夏夏夏 Holiday',
      slug='coconatsu', unit='MASTER SEASONS SUMMER!', event='CoCoNatsuHoliday.html',
      singers=['上田鈴帆', '佐藤心', '十時愛梨']),
 dict(title='凸凹スピードスター', m765='凸凹スピードスター', gj='凸凹スピードスター',
      slug='dekoboko', unit='しゅがしゅが☆み～ん', event='DekobokoSpeedStar.html',
      singers=['安部菜々', '佐藤心']),
 dict(title='しゅがーはぁと☆レボリューション', m765='しゅがーはぁと☆レボリューション', gj='しゅがーはぁと☆レボリューション',
      slug='sugarheart_revo', unit='佐藤心 ソロ曲', event=None,
      singers=['佐藤心']),
 dict(title='躍るFLAGSHIP', m765='躍るFLAGSHIP', gj='躍るFLAGSHIP',
      slug='flagship', unit='3chord for the Dance!', event='OdoruFlagship.html',
      singers=['小日向美穂', '佐藤心', '北条加蓮']),
 dict(title='オウムアムアに幸運を', m765='オウムアムアに幸運を', gj='オウムアムアに幸運を',
      slug='oumuamua', unit='アニメ「Spin-off!」テーマソング', event='OumuamuaKooun.html',
      singers=['一ノ瀬志希', '神谷奈緒', '黒埼ちとせ', '佐藤心', '的場梨沙']),
 dict(title='Go Just Go!', m765='Go Just Go!', gj='Go Just Go!',
      slug='gojustgo', unit='スターライトステージ5周年曲', event='GoJustGo.html',
      singers=['夢見りあむ', '大槻唯', '北条加蓮', '佐藤心', '一ノ瀬志希', '鷹富士茄子', '棟方愛海', '川島瑞樹', '五十嵐響子']),
 dict(title='ダンシング・デッド', m765='ダンシング・デッド', gj='ダンシング・デッド',
      slug='dancingdead', unit='Fav+rica', event='DancingDead.html',
      singers=['及川雫', '佐藤心', '諸星きらり']),
 dict(title='世界はそれを愛と呼ぶんだぜ', m765='世界はそれを愛と呼ぶんだぜ', gj='世界はそれを愛と呼ぶんだぜ',
      slug='sekaiwa', unit='カバー曲（佐藤心 ソロ）', event=None, cover='サンボマスター',
      singers=['佐藤心']),
 dict(title='認めてくれなくたっていいよ', m765='認めてくれなくたっていいよ', gj='認めてくれなくたっていいよ',
      slug='mitomete', unit='jewelries! 004 シリーズ共通曲', event=None,
      note='デレステではキュート／クール／パッションの3バージョンがあり、佐藤心はパッションver.（2025/07/08実装）を歌唱。',
      singers=['依田芳乃', '村上巴', '佐藤心', '夢見りあむ', '久川凪']),
 dict(title='熱情エナモラル', m765='熱情エナモラル', gj='熱情エナモラル',
      slug='enamorar', unit='Passion jewelries! 004', event='NetsujouEnamorar.html',
      singers=['依田芳乃', '村上巴', '佐藤心', '夢見りあむ', '久川凪']),
 # --- 以下4曲はデレステ情報なし ---
 dict(title='Sweet memories', m765='SWEET MEMORIES', gj=None,
      slug=None, unit='カバー曲（佐藤心 ソロ）', event=None, cover='松田聖子',
      note='Passion jewelries! 004 収録のカバー曲。カバー曲はプロデューサーからのリクエスト応募により選出。',
      singers=['佐藤心']),
 dict(title='ダンス・ダンス・ダンス', m765='ダンス・ダンス・ダンス', gj=None,
      slug=None, unit='スターリットシーズン DLC曲', event=None,
      note='原曲に佐藤心は不参加。「THE IDOLM@STER M@STER EXPO 会場オリジナルCD【シンデレラガールズ】」（2024/12/14）に佐藤心 ソロ・リミックスを収録。',
      singers_text='高垣楓、如月千早、秋月律子、三浦あずさ、四条貴音、神崎蘭子、最上静香、白石紬、白瀬咲耶、杜野凛世、奥空心白、玲音',
      singers=['佐藤心']),
 dict(title='もしも「カワイイ」が世界からなくなっても', m765='もしも「カワイイ」が世界からなくなっても', gj=None,
      slug=None, unit='カワスウィーティーなボクはぁと(仮)', event=None,
      note='xRライブ「CINDERELLA GIRLS fes. Once Upon a St@rs」の新曲4曲のうちの1曲。2025/10/24の生配信で初お披露目。',
      singers=['輿水幸子', '佐藤心']),
 dict(title='シンデレラNo.1', m765='シンデレラNo.1', gj=None,
      slug=None, unit='シンデレラガール総選挙2026 応援楽曲', event=None,
      note='アイドルの自己紹介ソング。190人分の専用歌詞が用意され、佐藤心を含む各アイドルのソロ・リミックスが順次公開されている。オリジナル音源は下記3人が歌唱。',
      singers=['安部菜々', 'イヴ・サンタクロース', '神崎蘭子']),
]

def esc(s):
    return html.escape(s or '', quote=True)

def icon_html(name):
    rom = name2rom.get(name)
    cls = 'idol shin' if name == '佐藤心' else 'idol'
    if rom:
        img = f'<img src="{CLOUD}data/iconimg/{rom}_icon01" alt="{esc(name)}" loading="lazy">'
        return f'<div class="{cls}"><span class="ic">{img}</span><span class="nm">{esc(name)}</span></div>'
    # アイコン無し（非CG等）はピンク丸プレースホルダー
    return f'<div class="idol no-icon"><span class="nm">{esc(name)}</span></div>'

def singers_html(s):
    return '\n'.join('          ' + icon_html(n) for n in s['singers'])

def credits_of(m765key):
    return song_data.get(m765key, {}).get('credits', {})

def meta_rows(s):
    c = credits_of(s['m765'])
    rows = []
    if s.get('unit'):
        rows.append(('区分', s['unit']))
    if s.get('cover'):
        rows.append(('原曲歌唱', s['cover']))
    if c.get('作詞'):
        rows.append(('作詞', c['作詞']))
    if c.get('作曲'):
        rows.append(('作曲', c['作曲']))
    if c.get('編曲') and c.get('編曲') not in ('-', ''):
        rows.append(('編曲', c['編曲']))
    rel = c.get('CD初出') or c.get('GAME初出') or ''
    if rel:
        rows.append(('CD／配信', rel))
    out = []
    for k, v in rows:
        out.append(f'          <div class="song-mrow"><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>')
    return '\n'.join(out)

def deresute_html(s):
    if not s.get('gj'):
        return ''
    g = gj.get(s['gj'], {})
    attr = g.get('type', '')
    ac = ATTR_CLASS.get(attr, 'all')
    al = ATTR_LABEL.get(attr, attr)
    info = []
    info.append(f'<span class="dere-attr attr-{ac}">{esc(al)}</span>')
    if g.get('release'):
        info.append(f'<span class="dere-fact"><b>実装日</b>{esc(g["release"])}</span>')
    if g.get('bpm'):
        info.append(f'<span class="dere-fact"><b>BPM</b>{esc(g["bpm"])}</span>')
    if g.get('time'):
        info.append(f'<span class="dere-fact"><b>時間</b>{esc(g["time"])}</span>')
    levels = g.get('levels', {})
    cells = []
    for d in DIFF_ORDER:
        if d in levels:
            cells.append(f'<div class="dere-lv"><span class="lv-name">{esc(d)}</span><span class="lv-num">{esc(levels[d])}</span></div>')
    lv_html = '\n'.join('            ' + c for c in cells)
    return f'''        <div class="song-dere">
          <h4 class="song-sub">デレステ</h4>
          <div class="dere-info">
            {'\n            '.join(info)}
          </div>
          <div class="dere-levels">
{lv_html}
          </div>
        </div>'''

def lives_html(s):
    lv = lives.get(s['m765'], [])
    if not lv:
        return ''
    rows = []
    for e in lv:
        tag = f'<span class="lv-tag">{esc(e["tag"])}</span>' if e.get('tag') else ''
        venue = f'<span class="live-venue">{esc(e["venue"])}</span>' if e.get('venue') else ''
        rows.append(
            f'            <div class="live-row"><div class="live-date">{esc(e["date"])}{tag}</div>'
            f'<div class="live-ev">{esc(e["event"])}{venue}</div>'
            f'<div class="live-perf">{esc(e["performers"])}</div></div>')
    body = '\n'.join(rows)
    return f'''        <details class="song-lives">
          <summary>LIVEでの披露一覧（{len(lv)}回）</summary>
          <div class="live-table">
{body}
          </div>
        </details>'''

def singers_note(s):
    if s.get('singers_text'):
        return f'        <p class="song-orig-singers"><b>原曲歌唱：</b>{esc(s["singers_text"])}</p>\n'
    return ''

def song_block(s):
    g = gj.get(s['gj'], {}) if s.get('gj') else {}
    attr = g.get('type', '')
    ac = ATTR_CLASS.get(attr, '')
    # ジャケット or プレースホルダー
    if s.get('slug'):
        jacket = f'<img class="song-jk-img" src="{CLOUD}Deresute/SongList/jacket/{s["slug"]}" alt="{esc(s["title"])} ジャケット" loading="lazy">'
        jk = f'<div class="song-jk">{jacket}</div>'
    else:
        jk = '<div class="song-jk song-jk-none"><span>♪</span></div>'
    attr_badge = f'<span class="song-attr attr-{ac}">{esc(ATTR_LABEL.get(attr, ""))}</span>' if ac else ''
    note = f'        <p class="song-note">{esc(s["note"])}</p>\n' if s.get('note') else ''
    event_btn = ''
    if s.get('event'):
        event_btn = f'''        <div class="song-rel">
          <a class="rel-btn" href="Deresute/Event/{s["event"]}">イベントページを見る</a>
        </div>\n'''
    return f'''      <details class="song-item"{f' data-attr="{ac}"' if ac else ''}>
        <summary class="song-head">
          {jk}
          <div class="song-headmain">
            <div class="song-title">{esc(s["title"])}{attr_badge}</div>
            <div class="song-singers gekijo-cast">
{singers_html(s)}
            </div>
          </div>
          <span class="song-caret" aria-hidden="true"></span>
        </summary>
        <div class="song-body">
{note}{singers_note(s)}          <dl class="song-meta">
{meta_rows(s)}
          </dl>
{deresute_html(s)}
{event_btn}{lives_html(s)}
        </div>
      </details>'''

blocks = '\n'.join(song_block(s) for s in SONGS)

HTML = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
	<base href="/SugarHeartDB/">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>歌唱曲一覧｜SugarHeartDB</title>
    <meta name="description" content="アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）が歌唱する楽曲の一覧です。曲名・歌唱者・作詞作曲・発売日・デレステ実装情報・LIVE披露履歴をまとめています。">
    <meta name="author" content="なごみ（@nagomi_IMCG）">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="歌唱曲一覧｜SugarHeartDB">
    <meta property="og:description" content="アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）が歌唱する楽曲の一覧です。">
    <meta property="og:site_name" content="SugarHeartDB">
    <meta property="og:image" content="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Deresute/KonoyoDeTadaHitoriNoHeart+/KonoyoDeTadaHitoriNoHeart+">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="歌唱曲一覧｜SugarHeartDB">
    <link rel="icon" type="image/png" sizes="32x32" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-32x32">
    <link rel="icon" type="image/png" sizes="16x16" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/favicon-16x16">
    <link rel="apple-touch-icon" sizes="180x180" href="https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/Favicon/apple-touch-icon">
    <link rel="stylesheet" href="style.css?v=20260718a">
</head>
<body>
<script src="components/header.js"></script>


<section class="page-hero">
    <div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <strong>歌唱曲一覧</strong></div>
    <h1>歌唱曲一覧 <span class="sub">/ GENERAL</span></h1>
    <p class="summary">佐藤心（しゅがーはぁと）が歌唱する楽曲の一覧です。曲名をタップすると、作詞・作曲・発売日、デレステ実装情報（属性・難易度・実装日・ジャケット）、LIVEでの披露履歴を確認できます。</p>
</section>

<div class="page">
  <div class="box-area">
    <div class="song-list">
{blocks}
    </div>
    <p class="song-source">※デレステ楽曲情報は「デレステ攻略Wiki（Gamerch）」、CD・作詞作曲・LIVE披露情報は「アイドルマスター楽曲メモ（music765plus）」を参照しています。</p>
  </div>
</div>


</body>
</html>
'''

open(os.path.join(BASE, 'General', 'SongList.html'), 'w', encoding='utf-8', newline='\n').write(HTML)
print('wrote General/SongList.html  (%d songs)' % len(SONGS))
# 未解決アイコンの警告
miss = set()
for s in SONGS:
    for n in s['singers']:
        if n not in name2rom:
            miss.add(n)
print('icon未解決:', sorted(miss) if miss else 'なし')
