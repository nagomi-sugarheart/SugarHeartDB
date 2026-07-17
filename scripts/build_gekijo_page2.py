# -*- coding: utf-8 -*-
"""シンデレラガールズ劇場ページの本体（gekijo-list）を再生成する。
無印/わいど☆の各話に タイトル(無印)・実装日・出演アイドル(アイコン)・関連リンク を付与。"""
import json, re, io

BASE = './'
CDN = 'https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/'

def load(p):
    j = json.loads(open(p, encoding='utf-8').read())
    return json.loads(j) if isinstance(j, str) else j

mu = load('scripts/gekijo_mujirushi.json')
wd = load('scripts/gekijo_wide.json')

# name -> romaji
name2rom = {}
for line in open('scripts/gekijo_name2rom.tsv', encoding='utf-8'):
    if '\t' in line:
        n, r = line.rstrip('\n').split('\t'); name2rom[n] = r
NOICON = {'千川ちひろ'}

# 佐藤心 自身の関連ページ（既存のキュレート済みリンク）: (type,ep) -> (href,label)
existing_rel = {
 ('mujirushi','246'):('Mobamas/SatoShin/SatoShin.html','佐藤心'),
 ('mujirushi','329'):('Mobamas/TBSweetie/TBSweetie.html','[T.B.ｽｳｨｰﾃｨｰ]佐藤心'),
 ('mujirushi','391'):('Mobamas/HeartModel/HeartModel.html','[ﾊｰﾄ･ﾓﾃﾞﾙ]佐藤心'),
 ('mujirushi','447'):('Mobamas/AngelHeart/AngelHeart.html','[えんじぇるはぁと]佐藤心'),
 ('mujirushi','521'):('Mobamas/HeartNoYomeiri/HeartNoYomeiri.html','[はぁとの嫁入り]佐藤心'),
 ('mujirushi','604'):('Mobamas/SweetieRoyal/SweetieRoyal.html','[ｽｳｨｰﾃｨｰ･ﾛﾜｲﾔﾙ]佐藤心'),
 ('mujirushi','671'):('Mobamas/WorkingSweetie/WorkingSweetie.html','[ﾜｰｷﾝｸﾞ･ｽｳｨｰﾃｨｰ]佐藤心'),
 ('mujirushi','750'):('Mobamas/TokonatsuParadise/TokonatsuParadise.html','[常夏ﾊﾟﾗﾀﾞｲｽ]佐藤心'),
 ('mujirushi','843'):('Mobamas/ChikuttoSweetie/ChikuttoSweetie.html','[ﾁｸｯとｽｳｨｰﾃｨｰ]佐藤心'),
 ('mujirushi','1008'):('Mobamas/6thAnniversary/6thAnniversary.html','[6thｱﾆﾊﾞｰｻﾘｰ]佐藤心'),
 ('mujirushi','1083'):('Mobamas/FallingHeart/FallingHeart.html','[ふぉーりんはぁと]佐藤心'),
 ('mujirushi','1218'):('Mobamas/ShinshunHeartful/ShinshunHeartful.html','[新春はぁとふる]佐藤心'),
 ('mujirushi','1311'):('Mobamas/NatsuiroHeart/NatsuiroHeart.html','[夏色はぁと]佐藤心'),
 ('mujirushi','1400'):('Mobamas/SweetieNewYear/SweetieNewYear.html','[ｽｳｨｰﾃｨｰ･ﾆｭｰｲﾔｰ]佐藤心'),
 ('mujirushi','1476'):('Mobamas/MerryChristmasHeart/MerryChristmasHeart.html','[ﾒﾘｸﾘ☆ﾊｰﾄ]佐藤心'),
 ('mujirushi','1595'):('Mobamas/StylishHeart/StylishHeart.html','[ｽﾀｲﾘｯｼｭ･はぁと]佐藤心'),
 ('wide','30'):('Deresute/DekobokoSpeedStar/DekobokoSpeedStar.html','[凸凹スピードスター]佐藤心'),
 ('wide','57'):('Deresute/OrderMadeHeart/OrderMadeHeart.html','[オーダーメイド・はぁと]佐藤心'),
 ('wide','219'):('Deresute/BrilliantHeart/BrilliantHeart.html','[ブリリアント・はぁと]佐藤心'),
 ('wide','371'):('Deresute/OdoruFLAGSHIP/OdoruFlagship.html','[躍るFLAGSHIP]佐藤心'),
 ('wide','376'):('Deresute/HeartfulSweeteen/HeartfulSweeteen.html','[はぁとふるsweeteen☆]佐藤心'),
 ('wide','486'):('Deresute/CoCoNatsuNatsuNatsuHoliday/CoCoNatsuNatsuNatsuHoliday.html','[CoCo夏夏夏Holiday]佐藤心'),
 ('wide','541'):('Deresute/KoisuruSweetieSummer/KoisuruSweetieSummer.html','[恋するスウィーティーサマー]佐藤心'),
 ('wide','669'):('Deresute/AisareQueenHeart/AisareQueenHeart.html','[愛されクイーン・はぁと]佐藤心'),
}

# 佐藤心が参加したイベントページ（関連フィールドに含まれれば付与）
EVENT_MAP = [
 ('SUN♡FLOWER','Deresute/Event/SunFlower.html','SUN♡FLOWER'),
 ('凸凹スピードスター','Deresute/Event/DekobokoSpeedStar.html','凸凹スピードスター'),
 ('オウムアムアに幸運を','Deresute/Event/OumuamuaKooun.html','オウムアムアに幸運を'),
 ('Go Just Go','Deresute/Event/GoJustGo.html','Go Just Go！'),
 ('躍るFLAGSHIP','Deresute/Event/OdoruFlagship.html','躍るFLAGSHIP'),
 ('ダンシング・デッド','Deresute/Event/DancingDead.html','ダンシング・デッド'),
 ('Next Chapter','Deresute/Event/NextChapter.html','Next Chapter'),
 ('CoCo夏夏夏','Deresute/Event/CoCoNatsuHoliday.html','CoCo夏夏夏Holiday'),
]

# 映り込みアンカー（関連フィールドのカード名に一致すれば付与）
UTSURI_BASE = 'Deresute/GuestCommu/GuestCommu_Utsurikomi.html#'
# (関連に含まれる部分文字列, anchor, ラベル)
UTSURI_MAP = [
 ('姉御の心粋', 'anegono-kokoroiki', '[姉御の心粋]村上巴'),
 ('聖夜の約束', 'seiya-yakusoku', '[聖夜の約束]三船美優'),
 ('ありすの物語', 'arisu-monogatari', '[ありすの物語]橘ありす'),
 ('祝宴の白姫', 'shukuen-shirohime', '[祝宴の白姫]神崎蘭子'),
 ('愛されたがりベイビー', 'aisaretagari-baby', '[愛されたがりベイビー]棟方愛海'),
]

def norm(s):
    return s.replace('［','[').replace('］',']').replace('　','').strip()

def cast_html(names):
    # 佐藤心を先頭へ
    ordered = ['佐藤心'] + [n for n in names if n != '佐藤心']
    parts = []
    for n in ordered:
        cls = 'idol shin' if n == '佐藤心' else 'idol'
        if n in NOICON:
            parts.append(f'<div class="idol no-icon"><span class="nm">{n}</span></div>')
        else:
            rom = name2rom.get(n)
            if not rom:
                parts.append(f'<div class="idol no-icon"><span class="nm">{n}</span></div>')
            else:
                parts.append(f'<div class="{cls}"><img src="{CDN}data/iconimg/{rom}_icon01" alt="{n}" loading="lazy"><span class="nm">{n}</span></div>')
    return '\n'.join('                        ' + p for p in parts)

def rel_html(typ, ep, relfield):
    btns = []
    seen = set()
    key = (typ, ep)
    if key in existing_rel:
        href, label = existing_rel[key]
        btns.append((href, label)); seen.add(href)
    if relfield:
        nf = norm(relfield)
        for needle, href, label in EVENT_MAP:
            if norm(needle) in nf and href not in seen:
                btns.append((href, label)); seen.add(href)
        for needle, anchor, label in UTSURI_MAP:
            href = UTSURI_BASE + anchor
            if norm(needle) in nf and href not in seen:
                btns.append((href, label)); seen.add(href)
    if not btns:
        return ''
    inner = '\n'.join(f'                        <a class="rel-btn" href="{h}">{l}</a>' for h, l in btns)
    return '                    <div class="gekijo-rel">\n' + inner + '\n                    </div>\n'

def fmt_date(d):
    d = d.split()[0].replace('/', '.').replace('-', '.')
    return d

blocks = []

# 無印: APIの id が CinGeki画像番号と一致（既存ページ準拠）
MUJI_EPS = {246,329,391,447,521,527,604,671,750,841,843,931,1001,1008,1040,1083,1218,1311,1323,1400,1470,1476,1498,1595,1622}
for r in sorted(mu['rows'], key=lambda x: x['date']):
    ep = r['id']; eps = str(ep); title = r['title']; date = fmt_date(r['date'])
    assert ep in MUJI_EPS, ep
    img = f'{CDN}CinGeki/CinGeki{ep}'
    cast = cast_html(r['chars'])
    rel = rel_html('mujirushi', eps, r.get('comment',''))
    b = f'''            <article class="gekijo-block" data-type="mujirushi" data-ep="{ep}">
                <div class="gekijo-thumb"><img class="lightbox-trigger" src="{img}" alt="シンデレラガールズ劇場無印 第{ep}話「{title}」" loading="lazy"></div>
                <div class="gekijo-meta">
                    <div class="gekijo-head"><span class="gekijo-ep">第{ep}話</span><span class="gekijo-type type-mujirushi">無印</span><span class="gekijo-date">{date}</span></div>
                    <div class="gekijo-title">{title}</div>
                    <div class="gekijo-cast">
{cast}
                    </div>
{rel}                </div>
            </article>'''
    blocks.append((date, b))

# わいど☆（特別イラストは除外＝話数リストのみ）
DATE_FIX = {'578wide':None}
for r in wd['rows']:
    wa = r[0]
    m = re.match(r'第(\d+)話', wa)
    if not m:
        continue  # 特別イラスト等
    ep = m.group(1)
    idols = r[1].split()
    rel_src = r[2]
    date = fmt_date(r[3])
    # 日付補正
    if ep == '274':
        date = '2020.06.30'  # 元データ 2020/06/31（存在しない日）
    if ep == '728':
        date = '2024.01.22'  # 元データ 2023/01/22（話数順と矛盾、年の誤り）
    img = f'{CDN}CinGeki/CinGekiWide{ep}'
    cast = cast_html(idols)
    rel = rel_html('wide', ep, rel_src)
    b = f'''            <article class="gekijo-block" data-type="wide" data-ep="{ep}">
                <div class="gekijo-thumb"><img class="lightbox-trigger" src="{img}" alt="シンデレラガールズ劇場わいど☆ 第{ep}話" loading="lazy"></div>
                <div class="gekijo-meta">
                    <div class="gekijo-head"><span class="gekijo-ep">第{ep}話</span><span class="gekijo-type type-wide">わいど☆</span><span class="gekijo-date">{date}</span></div>
                    <div class="gekijo-cast">
{cast}
                    </div>
{rel}                </div>
            </article>'''
    blocks.append((date, b))

count = len(blocks)
list_html = '\n'.join(b for _, b in blocks)
out = f'''    <p style="font-size: 0.82rem; color: var(--sh-text-mute); margin-bottom: 12px; font-family: monospace;">
        <span id="gekijo-count">{count}</span>話 表示中
    </p>

    <div class="gekijo-list" id="gekijo-list">
{list_html}
    </div>
    <p id="gekijo-empty" class="list-empty" style="display:none;">この区分はまだ準備中です。</p>'''

open('scripts/_gekijo_list.html', 'w', encoding='utf-8').write(out)
print('generated blocks:', count)
