#!/usr/bin/env python3
"""
generate_unit_pages.py
作業1: Unit/ 配下の各ユニット詳細HTMLページを生成
作業2: Mobamas/Unit/UnitList.html のユニットカードを更新
作業3: Mobamasカード詳細HTMLの v2-related-links セクションを再構築
"""

import os
import re
import csv
from pathlib import Path

# ============================================================
# 定数
# ============================================================

BASE_DIR = Path('/home/user/SugarHeartDB')
UNIT_DIR = BASE_DIR / 'Unit'
MOBAMAS_DIR = BASE_DIR / 'Mobamas'

FOLDER_TO_JA = {
    'AgentCoalSKS': 'エージェント・コール・SKS',
    'BeachAngel': 'ビーチエンジェル',
    'BridalModelAge26': 'ブライダルモデル Age26',
    'CatchYOU': 'キャッチYOU!',
    'CharismaDesigners': '衣装担当☆カリスマデザイナーズ',
    'ComingofAge': 'カミング・オブ・エイジ！',
    'CuticleGirls': 'キューティクル・ガールズ',
    'DokaPokaKoumuten': 'どかぽか工務店（校内工事中☆）',
    'EternalHeartAge': 'エターナルハァトエイジ',
    'EternalLadiate': 'エターナルレディエイト',
    'FascinerPresage': 'ファシネ・プレサージュ',
    'FurusatoOuenIdolBu': 'ふるさと応援アイドル部',
    'HamidashimononoKenkyuugyo': 'はみだし者の研究魚',
    'HappiFura': 'はぴ☆☆☆ふら',
    'KarenSousakutai': '花恋創作隊',
    'KawaSweetieNaBokuHeart': 'カワスウィーティなボクはぁと',
    'KiraKiraModelfromNSC': 'きらきらモデルfrom NSC',
    'KisekaeNingyoandShitateyaSan': '着せ替え人形と仕立て屋さん',
    'KoredemoKurae': 'これでもくらえ☆',
    'KoredemoKuraeWithAnastasia': 'これでもくらえ☆with アナスタシア',
    'LoveAngels': '愛の使徒～ラヴ・エンジェルズ',
    'MajonoYakata-DarkMagic': '魔女の館/Dark Magic',
    'MarinalOuendan': '☆マリナル応援団☆',
    'MoulinRouge': 'ムーランルージュ',
    'OTONAWedding': 'OTONA・ウェディング',
    'OnlyOneCollection': 'オンリーワン・コレクション',
    'OtomenaOtonanoNatsumoyou': 'オトメなオトナのナツモヨウ☆',
    'OuchinoJikan': 'おうちのじかん',
    'PinkyBounce': 'ピンキーバウンス',
    'QueensClassmate_Bride': '女王の同級生（花嫁）',
    'ReadyAfter': 'Ready? After!',
    'ShinshunNadeshiko': '新春なでし娘',
    'ShougatsuMijikashiAsobeyoOtome': '正月短し遊べよ乙女☆',
    'SweetOperation': 'スウィート☆オペレーション',
    'SweetieMilkeyWay': 'スウィーティー☆ミルキーウェイ',
    'TatakauOtometachi': '戦う乙女たち',
    'TreasureTriangle': 'トレジャートライアングル',
    'ValentineFurikaeriKai': 'バレンタイン振り返り会',
    'WonderColors': '志希を応援！ワンダーカラーズ',
}

NAME_TO_FOLDER = {
    'エージェント・コール・SKS': 'AgentCoalSKS',
    'ビーチエンジェル': 'BeachAngel',
    'ブライダルモデル Age26': 'BridalModelAge26',
    'キャッチYOU!': 'CatchYOU',
    '衣装担当☆カリスマデザイナーズ': 'CharismaDesigners',
    'カミング・オブ・エイジ！': 'ComingofAge',
    'キューティクル・ガールズ': 'CuticleGirls',
    'どかぽか工務店（校内工事中☆）': 'DokaPokaKoumuten',
    'エターナルハァトエイジ': 'EternalHeartAge',
    'エターナルレディエイト': 'EternalLadiate',
    'エターナル・レディエイト': 'EternalLadiate',
    'ファシネ・プレサージュ': 'FascinerPresage',
    'ふるさと応援アイドル部': 'FurusatoOuenIdolBu',
    'はみだし者の研究魚': 'HamidashimononoKenkyuugyo',
    'はぴ☆☆☆ふら': 'HappiFura',
    'カワスウィーティなボクはぁと': 'KawaSweetieNaBokuHeart',
    'きらきらモデルfrom NSC': 'KiraKiraModelfromNSC',
    'きらきらモデル from NSC': 'KiraKiraModelfromNSC',
    '着せ替え人形と仕立て屋さん': 'KisekaeNingyoandShitateyaSan',
    'これでもくらえ☆': 'KoredemoKurae',
    'これでもくらえ☆with アナスタシア': 'KoredemoKuraeWithAnastasia',
    '愛の使徒～ラヴ・エンジェルズ': 'LoveAngels',
    '魔女の館/Dark Magic': 'MajonoYakata-DarkMagic',
    '☆マリナル応援団☆': 'MarinalOuendan',
    'ムーランルージュ': 'MoulinRouge',
    'OTONA・ウェディング': 'OTONAWedding',
    'オンリーワン・コレクション': 'OnlyOneCollection',
    'オトメなオトナのナツモヨウ☆': 'OtomenaOtonanoNatsumoyou',
    'おうちのじかん': 'OuchinoJikan',
    'ピンキーバウンス': 'PinkyBounce',
    '女王の同級生（花嫁）': 'QueensClassmate_Bride',
    'Ready? After!': 'ReadyAfter',
    '新春なでし娘': 'ShinshunNadeshiko',
    '正月短し遊べよ乙女☆': 'ShougatsuMijikashiAsobeyoOtome',
    'スウィート☆オペレーション': 'SweetOperation',
    'スウィーティー☆ミルキーウェイ': 'SweetieMilkeyWay',
    '戦う乙女たち': 'TatakauOtometachi',
    'トレジャートライアングル': 'TreasureTriangle',
    'バレンタイン振り返り会': 'ValentineFurikaeriKai',
    '志希を応援！ワンダーカラーズ': 'WonderColors',
    '花恋創作隊': 'KarenSousakutai',
    # フォルダなし（リンク不可）
    'ハートオブワールド': None,
    'エリカPとしゅがーはぁと': None,
}

EVENT_URL_MAP = {
    '第3回プロダクション対抗トークバトルショー': 'Mobamas/Event/Event_ProductionTalkBattle3rd.html',
    '第5回 ドリームLIVEフェスティバル 新春SP': 'Mobamas/Event/Event_DreamLiveFestival5thNewYear.html',
    'アイドルプロデュース The 6th Anniversary': 'Mobamas/Event/Event_IdolProduce6thAnniversary.html',
    '目指せきらきらモデル アイドルチャレンジ': 'Mobamas/Event/Event_KirakiraModelChallenge.html',
    '長野エリアボス': 'Mobamas/NaganoArea/NaganoAreaBoss.html',
    'デレステメモリアルコミュ5': 'Mobamas/MemorialCommu.html',
}

TYPE_ORDER = ['App', 'Battle', 'Draw', 'Lose', 'Win']
TYPE_LABEL = {'App': 'アプリ', 'Battle': 'バトル', 'Draw': '引き分け', 'Lose': '敗北', 'Win': '勝利'}


# ============================================================
# ユーティリティ
# ============================================================

def parse_filename(fname):
    """ファイル名からプレフィックスとタイプを抽出する。
    Returns (prefix_key, type_str) or None if not recognized.
    """
    stem = Path(fname).stem  # 拡張子なし
    # パターンB: YYYYMMDD_NType or YYYYMMDDType
    m = re.match(r'^(\d{8}_\d+)([A-Za-z]+)$', stem)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r'^(\d{8})([A-Za-z]+)$', stem)
    if m:
        return m.group(1), m.group(2)
    # パターンA: TypeOnly
    for t in TYPE_ORDER:
        if stem == t:
            return 'none', t
    return None


def format_date_key(key):
    """グループキーを表示用文字列に変換"""
    if key == 'none':
        return None
    m = re.match(r'^(\d{4})(\d{2})(\d{2})_(\d+)$', key)
    if m:
        return f"{m.group(1)}.{m.group(2)}.{m.group(3)} ({m.group(4)})"
    m = re.match(r'^(\d{4})(\d{2})(\d{2})$', key)
    if m:
        return f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
    return key


def get_earliest_date(folder_path):
    """フォルダ内ファイルの最古の日付プレフィックスを YYYY.MM.DD で返す。なければ '－'"""
    dates = set()
    for f in os.listdir(folder_path):
        parsed = parse_filename(f)
        if parsed and parsed[0] not in ('none', None):
            key = parsed[0]
            # YYYYMMDD or YYYYMMDD_N → 先頭8桁
            dates.add(key[:8])
    if not dates:
        return '－'
    earliest = sorted(dates)[0]
    return f"{earliest[:4]}.{earliest[4:6]}.{earliest[6:8]}"


def collect_images(folder_path):
    """フォルダ内画像を日付グループでまとめた dict を返す。
    {group_key: {type_str: filename}}
    """
    groups = {}
    for fname in os.listdir(folder_path):
        ext = Path(fname).suffix.lower()
        if ext not in ('.png', '.jpg', '.jpeg'):
            continue
        parsed = parse_filename(fname)
        if parsed is None:
            continue
        key, typ = parsed
        if typ not in TYPE_ORDER:
            continue
        if key not in groups:
            groups[key] = {}
        groups[key][typ] = fname

    # キー昇順ソート（'none' は先頭）
    def sort_key(k):
        if k == 'none':
            return '00000000'
        return k[:8] + (k[9:] if '_' in k else '')

    sorted_groups = dict(sorted(groups.items(), key=lambda x: sort_key(x[0])))
    return sorted_groups


# ============================================================
# 作業1: ユニット詳細HTMLページの生成
# ============================================================

def generate_unit_detail_html(folder_name, ja_name, groups):
    """ユニット詳細HTMLを生成して返す"""
    # 画像セクション生成
    sections_html = []
    for key, types_dict in groups.items():
        date_display = format_date_key(key)
        figs = []
        for typ in TYPE_ORDER:
            if typ not in types_dict:
                continue
            fname = types_dict[typ]
            label = TYPE_LABEL[typ]
            figs.append(
                f'            <figure class="unit-img-fig">\n'
                f'                <img src="Unit/{folder_name}/{fname}" alt="{ja_name} {label}">\n'
                f'                <figcaption>{label}</figcaption>\n'
                f'            </figure>'
            )
        if not figs:
            continue

        section_lines = ['    <section class="unit-img-group">']
        if date_display:
            section_lines.append(f'        <h2 class="box-title">初出日：{date_display}</h2>')
        section_lines.append('        <div class="unit-img-row">')
        for fig in figs:
            section_lines.append(fig)
        section_lines.append('        </div>')
        section_lines.append('    </section>')
        sections_html.append('\n'.join(section_lines))

    sections_str = '\n\n'.join(sections_html)

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <base href="/SugarHeartDB/">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ja_name}｜SugarHeartDB</title>
    <meta name="description" content="アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）が所属するユニット「{ja_name}」のページです。">
    <meta name="author" content="なごみ（@nagomi_IMCG）">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{ja_name}｜SugarHeartDB">
    <meta property="og:description" content="アイドルマスターシンデレラガールズの佐藤心（しゅがーはぁと）が所属するユニット「{ja_name}」のページです。">
    <meta property="og:site_name" content="SugarHeartDB">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="SugarHeartDB">
    <link rel="icon" type="image/png" sizes="32x32" href="Favicon/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="Favicon/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="Favicon/apple-touch-icon.png">
    <link rel="stylesheet" href="style.css">
</head>
<body>
<script src="components/header.js"></script>

<section class="page-hero">
    <div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <a href="Mobamas/Unit/UnitList.html">ユニット一覧</a> · <strong>{ja_name}</strong></div>
    <h1>{ja_name} <span class="sub">/ {folder_name}</span></h1>
</section>

<div class="box-area" style="max-width:1180px; margin:0 auto 24px; padding:0 28px;">

{sections_str}

</div>
</body>
</html>
'''
    return html


def task1_generate_unit_pages():
    """作業1: 各ユニットフォルダにHTMLを生成"""
    generated = []
    for folder_name, ja_name in FOLDER_TO_JA.items():
        folder_path = UNIT_DIR / folder_name
        if not folder_path.exists():
            print(f"  [WARN] フォルダが存在しません: {folder_path}")
            continue
        groups = collect_images(folder_path)
        html = generate_unit_detail_html(folder_name, ja_name, groups)
        out_path = folder_path / f'{folder_name}.html'
        out_path.write_text(html, encoding='utf-8')
        generated.append(str(out_path))
        print(f"  [OK] {out_path.name} を生成 ({len(groups)} グループ)")
    print(f"\n作業1完了: {len(generated)} ファイルを生成")
    return generated


# ============================================================
# 作業2: UnitList.html の更新
# ============================================================

def build_unit_card(folder_name, ja_name):
    """ユニットカードのHTMLを生成"""
    folder_path = UNIT_DIR / folder_name
    debut = get_earliest_date(folder_path) if folder_path.exists() else '－'
    return (
        f'        <article class="unit-card" data-size="-">\n'
        f'            <div class="unit-cover">\n'
        f'                <div class="meta">\n'
        f'                    <span class="unit-badge size">-人</span>\n'
        f'                    <span class="unit-badge year">-</span>\n'
        f'                    <span class="unit-badge theme">-</span>\n'
        f'                </div>\n'
        f'                <h3 class="unit-name">{ja_name}</h3>\n'
        f'                <div class="unit-en">{folder_name}</div>\n'
        f'            </div>\n'
        f'            <div class="unit-members">\n'
        f'                <div class="label">MEMBERS</div>\n'
        f'                <div class="member-row">\n'
        f'                    <div class="unit-member shin">\n'
        f'                        <div class="av">心</div>\n'
        f'                        <div class="nm">佐藤心</div>\n'
        f'                    </div>\n'
        f'                </div>\n'
        f'            </div>\n'
        f'            <div class="unit-info">\n'
        f'                <div class="row"><span class="k">DEBUT</span><span class="v">{debut}</span></div>\n'
        f'            </div>\n'
        f'            <div class="unit-foot">\n'
        f'                <div class="stats"></div>\n'
        f'                <a class="detail-btn" href="Unit/{folder_name}/{folder_name}.html">詳細 →</a>\n'
        f'            </div>\n'
        f'        </article>'
    )


def task2_update_unit_list():
    """作業2: UnitList.html のサンプルカードを実際のカードに置き換え"""
    unit_list_path = BASE_DIR / 'Mobamas' / 'Unit' / 'UnitList.html'
    content = unit_list_path.read_text(encoding='utf-8')

    # サンプルカード2つ（コメント含む）を削除し、実際のカードに差し替える
    # unit-grid の中身を全て置き換える
    cards = []
    for folder_name, ja_name in FOLDER_TO_JA.items():
        cards.append(build_unit_card(folder_name, ja_name))

    cards_html = '\n\n'.join(cards)

    # <!-- ユニットグリッド --> ... </div> の中の内容を置き換え
    # unit-grid div の中身を丸ごと置き換える
    new_grid_inner = f'''
        <!--
        ===========================================================
        自動生成されたユニットカード（generate_unit_pages.py）
        ===========================================================
        -->

{cards_html}

        <!-- TODO: ここに追加のユニットカードを貼り付けてください -->

    '''

    # unit-grid の内容を置き換え（開始タグから最初の </div>\n</div> まで）
    # まず既存の unit-grid の中身を特定して置換
    pattern = re.compile(
        r'(<div class="unit-grid" id="unit-grid">).*?(    </div>\n</div>)',
        re.DOTALL
    )

    def replacer(m):
        return m.group(1) + '\n' + new_grid_inner + m.group(2)

    new_content = pattern.sub(replacer, content)

    if new_content == content:
        print("  [WARN] UnitList.html の置換パターンがマッチしませんでした。手動確認が必要です。")
        # fallback: unit-grid 内のコメントブロックとサンプルカードを除去して挿入
    else:
        unit_list_path.write_text(new_content, encoding='utf-8')
        print(f"  [OK] UnitList.html を更新 ({len(FOLDER_TO_JA)} ユニット)")


# ============================================================
# 作業3: カード詳細HTMLの関連ページ再構築
# ============================================================

def build_card_name_to_path():
    """Mobamas配下のカード詳細HTMLから {card_name: relative_path} を構築"""
    result = {}
    # サブフォルダのみ対象（直下のHTMLは除く）
    card_html_files = []
    # 非カードフォルダを除外
    NON_CARD_DIRS = {'Unit', 'Event', 'NaganoArea', 'SeasonalEvents'}
    for entry in MOBAMAS_DIR.iterdir():
        if entry.is_dir() and entry.name not in NON_CARD_DIRS:
            for html_file in entry.glob('*.html'):
                card_html_files.append(html_file)

    for html_file in card_html_files:
        content = html_file.read_text(encoding='utf-8')
        m = re.search(r'<h1>(.*?)</h1>', content, re.DOTALL)
        if m:
            raw = m.group(1)
            # <span class="v2-date">...</span> を除去
            card_name = re.sub(r'<span[^>]*>.*?</span>', '', raw, flags=re.DOTALL).strip()
            # Mobamas/ からの相対パス（拡張子なし）
            rel = html_file.relative_to(BASE_DIR)
            path_no_ext = str(rel.with_suffix(''))
            result[card_name] = path_no_ext
    return result


def resolve_related_href(item, card_map):
    """関連ページ文字列からhrefを解決する"""
    item = item.strip()
    if not item:
        return None

    # ユニット判定
    UNIT_SUFFIX = '（ユニット）'  # 6文字
    if item.endswith(UNIT_SUFFIX):
        unit_name = item[:-len(UNIT_SUFFIX)]
        folder = NAME_TO_FOLDER.get(unit_name)
        if folder:
            return f'Unit/{folder}/{folder}.html'
        else:
            return '#'

    # デレステ系
    if '(デレステ)' in item or 'デレステ' in item:
        return '#'

    # 既知イベントURL
    for event_name, url in EVENT_URL_MAP.items():
        if item == event_name:
            return url

    # カード名マッチ
    if item in card_map:
        return card_map[item] + '.html'

    # その他 → #
    return '#'


def rebuild_related_links(html_content, related_items, card_map):
    """v2-related-links の中身を再構築"""
    links = []
    for item in related_items:
        if not item.strip():
            continue
        href = resolve_related_href(item, card_map)
        if href is None:
            continue
        display_name = item
        # ユニット表記の場合、表示名から「（ユニット）」を除去
        UNIT_SUFFIX = '（ユニット）'
        if display_name.endswith(UNIT_SUFFIX):
            display_name = display_name[:-len(UNIT_SUFFIX)]
        links.append(f'                <a href="{href}">{display_name}</a>')

    if not links:
        new_inner = ''
    else:
        new_inner = '\n' + '\n'.join(links) + '\n            '

    # v2-related-links の中身を置き換え
    pattern = re.compile(
        r'(<div class="v2-related-links">)(.*?)(</div>)',
        re.DOTALL
    )

    def replacer(m):
        return m.group(1) + new_inner + m.group(3)

    new_content = pattern.sub(replacer, html_content, count=1)
    return new_content


def task3_rebuild_related_links():
    """作業3: CSVに基づいてカード詳細HTMLの関連ページを再構築"""
    # カード名→パスのマッピングを構築
    card_map = build_card_name_to_path()
    print(f"  カードマップ: {len(card_map)} 件")

    # CSVを読み込む
    csv_path = BASE_DIR / 'data' / 'mobamas.csv'
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    updated = 0
    skipped = 0
    for row in rows:
        card_name = row['カード名'].strip()
        # 関連ページ列を収集
        related_items = []
        for i in range(1, 21):
            val = row.get(f'関連ページ{i}', '').strip()
            if val:
                related_items.append(val)

        # HTMLファイルを特定
        if card_name not in card_map:
            print(f"  [SKIP] カードHTMLが見つかりません: {card_name}")
            skipped += 1
            continue

        html_rel_path = card_map[card_name]
        html_path = BASE_DIR / (html_rel_path + '.html')
        if not html_path.exists():
            print(f"  [SKIP] ファイルが存在しません: {html_path}")
            skipped += 1
            continue

        content = html_path.read_text(encoding='utf-8')

        # v2-related-links が存在するか確認
        if 'v2-related-links' not in content:
            print(f"  [SKIP] v2-related-links が見つかりません: {html_path.name}")
            skipped += 1
            continue

        new_content = rebuild_related_links(content, related_items, card_map)

        if new_content != content:
            html_path.write_text(new_content, encoding='utf-8')
            updated += 1
            print(f"  [OK] {html_path.name} を更新 ({len(related_items)} 件の関連ページ)")
        else:
            print(f"  [NOCHANGE] {html_path.name} は変更なし")

    print(f"\n作業3完了: {updated} ファイルを更新、{skipped} スキップ")


# ============================================================
# 実行
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("作業1: ユニット詳細HTMLページの生成")
    print("=" * 60)
    task1_generate_unit_pages()

    print()
    print("=" * 60)
    print("作業2: UnitList.html の更新")
    print("=" * 60)
    task2_update_unit_list()

    print()
    print("=" * 60)
    print("作業3: カード詳細HTMLの関連ページ再構築")
    print("=" * 60)
    task3_rebuild_related_links()

    print()
    print("全作業完了！")
