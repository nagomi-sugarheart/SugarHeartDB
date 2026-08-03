#!/usr/bin/env python3
"""
_generate_search_index.py
data/search-index.json を生成するスクリプト。

対象:
  - data/mobamas.csv  → type: "card"
  - data/udetail.csv  → type: "unit"
  - Mobamas/**/*.html, Deresute/**/*.html
      → コミュ台詞は type: "story"
      → カード詳細セリフ（形式E）は type: "card"

使い方:
  python _generate_search_index.py
"""

import csv
import json
import os
import re
import glob
from html.parser import HTMLParser

# このスクリプトは scripts/ 配下にあるため、リポジトリ直下を親ディレクトリとして参照する
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'search-index.json')


# ─────────────────────────────────────────────
# 1. アイドルマスターデータ読み込み
# ─────────────────────────────────────────────

def load_idols():
    """cgss_idols.csv を読んで {短縮名: フルネーム} のマップを返す。"""
    idol_map = {}  # short_name -> full_name
    path = os.path.join(BASE_DIR, 'data', 'cgss_idols.csv')
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            short = row['名前'].strip()
            full  = row['アイドル名'].strip()
            if short:
                idol_map[short] = full
    return idol_map


# 劇中の役名などでカタカナ表記される話者と、対応するアイドルの短縮名。
# 表記が違うだけで同一人物なので、検索・バッジ表示は漢字表記に揃える。
# （ナターリア・キャシー・ライラ等、本来カタカナ名のアイドルはここには入れない）
KANA_SPEAKER_ALIASES = {
    'シン':   '心',     'エリカ': '瑛梨華', 'キヨラ': '清良',   'コハル': '小春',
    'サチコ': '幸子',   'シキ':   '志希',   'シノ':   '志乃',   'セイラ': '聖來',
    'トモエ': '巴',     'ハヤテ': '颯',     'ホナミ': '保奈美', 'マユ':   'まゆ',
    'マリナ': '麻理菜', 'ミカ':   '美嘉',   'ミユ':   '美優',   'ムツミ': 'むつみ',
    'ヨーコ': '洋子',   'リナ':   '里奈',   'カナデ': '奏',
}


def normalize_speaker(speaker, member_shorts=None):
    """カタカナ表記の話者名を漢字表記（cgss_idols.csv の「名前」）に揃える。

    member_shorts を渡した場合、変換先がそのユニットのメンバーであるときだけ
    変換する（同じ読みの別アイドルへ誤変換するのを防ぐ）。"""
    alias = KANA_SPEAKER_ALIASES.get(speaker)
    if not alias:
        return speaker
    if member_shorts and alias not in member_shorts:
        return speaker
    return alias


def extract_idol_short(card_name, idol_map):
    """カード名（例: [ﾊｰﾄ･ﾓﾃﾞﾙ]佐藤心+）からアイドル短縮名を返す。"""
    # [prefix] を除去して末尾の + を取り除く
    plain = re.sub(r'^\[.*?\]', '', card_name).rstrip('+').strip()
    for short, full in idol_map.items():
        if full == plain or short == plain:
            return short
    return ''


# ─────────────────────────────────────────────
# 2. UnitList.html からユニット名 → URL のマップを構築
# ─────────────────────────────────────────────

class UnitListParser(HTMLParser):
    """UnitList.html を解析してユニット名とURLのマッピングを作成する。"""

    def __init__(self):
        super().__init__()
        self.unit_url_map = {}   # unit_ja_name -> relative_url
        self._current_unit_ja = None
        self._in_article = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'article' and 'unit-card' in attrs_dict.get('class', ''):
            self._in_article = True
            self._current_unit_ja = attrs_dict.get('data-name-ja', '')
        if self._in_article and tag == 'a':
            cls = attrs_dict.get('class', '')
            href = attrs_dict.get('href', '')
            if 'detail-btn' in cls and href:
                if self._current_unit_ja:
                    self.unit_url_map[self._current_unit_ja] = href

    def handle_endtag(self, tag):
        if tag == 'article':
            self._in_article = False
            self._current_unit_ja = None


def load_unit_url_map():
    """UnitList.html を解析してユニット名 → URL のマップを返す。"""
    path = os.path.join(BASE_DIR, 'Unit', 'UnitList.html')
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        html = f.read()
    parser = UnitListParser()
    parser.feed(html)
    return parser.unit_url_map


# ─────────────────────────────────────────────
# 3. mobamas.csv → カードエントリ生成
# ─────────────────────────────────────────────

# セリフが含まれる列のプレフィックス
DIALOGUE_PREFIXES = ('あいさつ_', 'お仕事_', '親愛度MAX_')


def load_existing_entries(types):
    """既存の search-index.json から指定タイプのエントリを取り出す。
    元データCSV（mobamas.csv / udetail.csv / ulist.csv）は「今後カード追加なし」の
    方針で削除済みのため、それらを入力とするカード・ユニットのエントリは
    再生成時に既存インデックスから引き継いで保持する。"""
    if not os.path.exists(OUTPUT_FILE):
        return []
    try:
        with open(OUTPUT_FILE, encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return []
    return [e for e in data if e.get('type') in types]


# mobamas.csv 由来のカードエントリのリンク先。引き継ぎ対象の判別に使う
CARD_CSV_URL = 'CardList.html'


def load_card_entries(idol_map):
    path = os.path.join(BASE_DIR, 'data', 'mobamas.csv')
    if not os.path.exists(path):
        # 元データCSVが無い場合は既存インデックスのカードエントリを維持する。
        # ただし type: "card" にはカード詳細ページから毎回生成されるものも
        # 含まれるため、CSV由来（リンク先が CardList.html）だけを引き継ぐ。
        # 全部引き継ぐと再生成のたびにページ由来分が二重に積まれてしまう。
        return [e for e in load_existing_entries({'card'})
                if e.get('url') == CARD_CSV_URL]
    entries = []
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        dialogue_cols = [k for k in fieldnames if any(k.startswith(p) for p in DIALOGUE_PREFIXES)]
        for row in reader:
            card_name = row['カード名'].strip()
            idol = extract_idol_short(card_name, idol_map)
            for col in dialogue_cols:
                text = row.get(col, '').strip()
                if text:
                    # 列名を「カテゴリ/種別」形式に変換（例: あいさつ_マイスタジオ1 → あいさつ）
                    context = col.split('_')[0] if '_' in col else col
                    entries.append({
                        'type':    'card',
                        'title':   card_name,
                        'text':    text,
                        'idol':    idol,
                        'context': context,
                        'url':     CARD_CSV_URL,
                    })
    return entries


# ─────────────────────────────────────────────
# 4. udetail.csv → ユニット台詞エントリ生成
# ─────────────────────────────────────────────

# 台詞の種別ラベル
SERIF_CONTEXTS = ['登場時セリフ', 'バトル時セリフ', '勝利時セリフ', '敗北時セリフ', '引き分け時セリフ']

# ユニットページの話者スパンを拾う正規表現
UNIT_LINE_RE = re.compile(
    r'<p class="line">(?:<span class="speaker"([^>]*)>([^<]*)</span>)?(.*?)</p>', re.S)
DATA_IDOL_RE = re.compile(r'data-idol="([^"]*)"')


def load_unit_speaker_map():
    """Unit/**/*.html から「セリフ本文 → 話者」のマップを作る。

    ユニットページは実際にサイトへ表示されている台詞そのものなので、
    話者の正となるデータとして扱う。カタカナの役名で表示している話者は
    data-idol に本人の名前を持つため、あればそちらを優先する。"""
    speaker_by_text = {}
    for path in sorted(glob.glob(os.path.join(BASE_DIR, 'Unit', '**', '*.html'), recursive=True)):
        if os.path.basename(path) == 'UnitList.html':
            continue
        try:
            with open(path, encoding='utf-8', errors='ignore') as f:
                html = f.read()
        except Exception:
            continue
        for m in UNIT_LINE_RE.finditer(html):
            attrs = m.group(1) or ''
            idol_attr = DATA_IDOL_RE.search(attrs)
            speaker = (idol_attr.group(1) if idol_attr else (m.group(2) or '')).strip()
            text = re.sub(r'<[^>]+>', '', m.group(3)).strip()
            if text and speaker:
                speaker_by_text[text] = speaker
    return speaker_by_text


def resync_unit_speakers(entries):
    """既存インデックスのユニットエントリの話者(idol)をユニットページと同期する。

    idol にはユニット全メンバーではなく「そのセリフを話したアイドル」を入れる。
    ページ側に該当セリフが無い場合は既存の値を保持する。"""
    speaker_by_text = load_unit_speaker_map()
    if not speaker_by_text:
        return entries
    for e in entries:
        speaker = speaker_by_text.get(e.get('text', '').strip())
        if speaker:
            e['idol'] = speaker
    return entries


def load_unit_entries(idol_map, unit_url_map):
    ulist_path = os.path.join(BASE_DIR, 'data', 'ulist.csv')
    udetail_path = os.path.join(BASE_DIR, 'data', 'udetail.csv')
    if not (os.path.exists(ulist_path) and os.path.exists(udetail_path)):
        # 元データCSVが無い場合は既存インデックスのユニットエントリを維持しつつ、
        # 話者だけはユニットページの内容と同期する
        return resync_unit_speakers(load_existing_entries({'unit'}))

    entries = []

    # ulist.csv からユニット名 → フルネームメンバーリスト のマップを作成
    unit_members_full = {}  # unit_name -> [full_name1, ...]
    with open(ulist_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            uname = row['ユニット名'].strip()
            members = []
            for i in range(1, 16):
                m = row.get(f'メンバー{i}', '').strip()
                if m:
                    members.append(m)
            unit_members_full[uname] = members

    # フルネーム → 短縮名のマップ（逆引き）
    full_to_short = {full: short for short, full in idol_map.items()}

    # udetail.csv を読んでエントリ生成
    with open(udetail_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            uname = row['ユニット名'].strip()
            # URLの取得（UnitList.htmlから取得したマップか、UnitList.htmlにない場合はUnitList.html）
            unit_ja_name = uname
            url = unit_url_map.get(unit_ja_name, 'Unit/UnitList.html')

            # メンバーの短縮名リスト（話者名の妥当性チェックに使う）
            member_shorts = []
            for full in unit_members_full.get(uname, []):
                short = full_to_short.get(full, '')
                if short:
                    member_shorts.append(short)

            # 各種セリフ
            for ctx in SERIF_CONTEXTS:
                for n in ['1', '2']:
                    speaker_col = f'{ctx}{n}話者'
                    text_col    = f'{ctx}{n}セリフ'
                    speaker = row.get(speaker_col, '').strip()
                    text    = row.get(text_col, '').strip()
                    if text:
                        # idol は「そのセリフを話したアイドル」。
                        # ユニット全メンバーを入れると話者での絞り込みが効かない。
                        entries.append({
                            'type':    'unit',
                            'title':   uname,
                            'text':    text,
                            'idol':    normalize_speaker(speaker, member_shorts),
                            'context': ctx,
                            'url':     url,
                        })
    return entries


# ─────────────────────────────────────────────
# 5. HTML → ストーリー台詞エントリ生成
# ─────────────────────────────────────────────

def speaker_of(attrs_dict):
    """話者名を取り出す。

    劇中の役名や愛称で表示している話者（例: data-who="ダークシュガー"）は
    data-idol に本人の名前を持たせているため、あればそちらを優先する。
    こうするとページの表示は役名のまま、検索の話者絞り込みだけ本人に紐づく。"""
    return (attrs_dict.get('data-idol') or attrs_dict.get('data-who') or '').strip()


class DialogueParser(HTMLParser):
    """
    HTML から会話行を抽出する。
    対応形式:
      A: .script-row[data-who] > .line
      B: .dialog .body > .line-head .speaker[data-who]  + .text
      C: .ud-dialogue .line（.speaker スパンはスキップ）
      E: .v2-dialogue-content .v2-accord-body p（デレステカード詳細セリフ）
      F: .ev-dialog-row .ev-text（v2-accord外、Popmasなど）
    """

    def __init__(self, card_idol='心'):
        super().__init__()
        self.entries = []       # [(idol, text)] ストーリー台詞（形式A/B/C/D/F）
        self.card_entries = []  # [(idol, text)] カード詳細セリフ（形式E）
        self.title = ''
        # 形式E（カード詳細セリフ）の話者。ページのカード名から判定して渡す
        self.card_idol = card_idol

        self._in_title = False

        # 形式A
        self._in_script_row = False
        self._script_row_who = ''
        self._in_line_a = False
        self._line_a_depth = 0

        # 形式B
        self._in_dialog_body = False
        self._dialog_who = ''
        self._in_text_b = False
        self._text_b_depth = 0

        # 形式C
        self._in_ud_line = False
        self._in_speaker_c = False
        self._ud_line_who = ''
        self._ud_text_parts = []
        self._ud_depth = 0

        # 形式D: .ev-dialog-row .ev-text（イベント中セリフ）
        self._v2_accord_depth = -1   # -1 = アコーディオン外
        self._v2_accord_who = ''
        self._in_ev_text_d = False
        self._ev_text_d_depth = 0
        self._ev_text_d_text = ''
        # ev-text 内の個別 speaker スパン（行ごとの話者）
        self._in_ev_text_speaker = False
        self._ev_text_line_who = ''

        # 形式E: .v2-dialogue-content .v2-accord-body p（デレステカード詳細セリフ）
        self._in_v2_dialogue = False
        self._v2_dialogue_depth = -1
        self._in_v2_accord_body_e = False
        self._v2_accord_body_e_depth = -1
        self._in_v2_p_e = False
        self._v2_p_e_depth = -1
        self._v2_p_e_text = ''

        # 形式F: .ev-dialog-row .ev-text（v2-accord外、Popmasなど）
        self._in_standalone_ev_row = False
        self._standalone_ev_row_depth = -1
        self._in_standalone_ev_text_f = False
        self._standalone_ev_text_f_depth = -1
        self._standalone_ev_text_f_text = ''
        self._standalone_ev_who = ''      # 行内 .speaker[data-who] の話者
        self._f_skip_depth = -1           # ラベル・話者名・注記をテキストから除外する領域

        self._stack = []  # タグスタックで深さ管理

    def _has_class(self, attrs_dict, cls):
        classes = attrs_dict.get('class', '').split()
        return cls in classes

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self._stack.append(tag)

        # <title>
        if tag == 'title':
            self._in_title = True
            return

        # 形式A: .script-row[data-who] （stage-direction 除外）
        if tag == 'div' and self._has_class(attrs_dict, 'script-row'):
            classes = attrs_dict.get('class', '').split()
            if 'stage-direction' not in classes and 'data-who' in attrs_dict:
                self._in_script_row = True
                self._script_row_who = speaker_of(attrs_dict)
        if self._in_script_row and tag == 'div' and self._has_class(attrs_dict, 'line'):
            self._in_line_a = True
            self._line_a_depth = len(self._stack)
            self._line_a_text = ''

        # 形式B: .dialog .body > speaker + text
        if tag == 'div' and self._has_class(attrs_dict, 'body'):
            self._in_dialog_body = True
            self._dialog_who = ''
        if self._in_dialog_body and tag == 'span' and self._has_class(attrs_dict, 'speaker'):
            who = speaker_of(attrs_dict)
            if who:
                self._dialog_who = who
        if self._in_dialog_body and tag == 'div' and self._has_class(attrs_dict, 'text'):
            self._in_text_b = True
            self._text_b_depth = len(self._stack)
            self._text_b_text = ''

        # 形式C: .ud-dialogue .line
        if tag == 'p' and self._has_class(attrs_dict, 'line'):
            self._in_ud_line = True
            self._ud_text_parts = []
            self._ud_depth = len(self._stack)
            self._ud_line_who = ''
        if self._in_ud_line and tag == 'span' and self._has_class(attrs_dict, 'speaker'):
            self._in_speaker_c = True

        # 形式E: .v2-dialogue-content .v2-accord-body p
        if tag == 'div' and self._has_class(attrs_dict, 'v2-dialogue-content'):
            self._in_v2_dialogue = True
            self._v2_dialogue_depth = len(self._stack)
        if self._in_v2_dialogue and tag == 'div' and self._has_class(attrs_dict, 'v2-accord-body'):
            self._in_v2_accord_body_e = True
            self._v2_accord_body_e_depth = len(self._stack)
        if self._in_v2_accord_body_e and tag == 'p':
            self._in_v2_p_e = True
            self._v2_p_e_depth = len(self._stack)
            self._v2_p_e_text = ''

        # 形式F: .ev-dialog-row .ev-text（v2-accord外）
        if (self._v2_accord_depth < 0
                and tag == 'div' and self._has_class(attrs_dict, 'ev-dialog-row')):
            self._in_standalone_ev_row = True
            self._standalone_ev_row_depth = len(self._stack)
        if (self._in_standalone_ev_row
                and tag == 'div' and self._has_class(attrs_dict, 'ev-text')):
            self._in_standalone_ev_text_f = True
            self._standalone_ev_text_f_depth = len(self._stack)
            self._standalone_ev_text_f_text = ''
            self._standalone_ev_who = ''
            self._f_skip_depth = -1
        # ev-text 内の speaker スパン（話者を取得し、名前はテキストから除外）・
        # ev-condition ラベル・dss-stage-text 注記はテキストに含めない
        if self._in_standalone_ev_text_f and self._f_skip_depth < 0:
            if tag == 'span' and self._has_class(attrs_dict, 'speaker'):
                who = speaker_of(attrs_dict)
                if who:
                    self._standalone_ev_who = who
                self._f_skip_depth = len(self._stack)
            elif tag == 'div' and (self._has_class(attrs_dict, 'ev-condition')
                                   or self._has_class(attrs_dict, 'dss-stage-text')):
                self._f_skip_depth = len(self._stack)

        # 形式D: .v2-accord > (head の speaker) + .ev-text
        if tag == 'div' and self._has_class(attrs_dict, 'v2-accord'):
            self._v2_accord_depth = len(self._stack)
            self._v2_accord_who = ''
        # アコーディオン内の最初の speaker[data-who] からアイドル名を取得
        if (self._v2_accord_depth >= 0
                and not self._v2_accord_who
                and tag == 'span' and self._has_class(attrs_dict, 'speaker')):
            who = speaker_of(attrs_dict)
            if who and who not in ('P', 'ナレーション'):
                self._v2_accord_who = who
        # .ev-text: アコーディオン内のセリフテキスト
        if (self._v2_accord_depth >= 0
                and tag == 'div' and self._has_class(attrs_dict, 'ev-text')):
            self._in_ev_text_d = True
            self._ev_text_d_depth = len(self._stack)
            self._ev_text_d_text = ''
            self._ev_text_line_who = ''  # 行ごとの話者リセット
        # ev-text 内の speaker スパン: 行ごとの話者特定（テキストは除外）
        if (self._in_ev_text_d
                and tag == 'span' and self._has_class(attrs_dict, 'speaker')):
            who = speaker_of(attrs_dict)
            if who and who not in ('P', 'ナレーション'):
                self._ev_text_line_who = who
                self._in_ev_text_speaker = True

    def handle_endtag(self, tag):
        depth = len(self._stack)

        # 形式A終了
        if self._in_line_a and depth < self._line_a_depth:
            text = getattr(self, '_line_a_text', '').strip()
            who  = self._script_row_who
            if text and who and who not in ('P', 'ナレーション', ''):
                self.entries.append((who, text))
            self._in_line_a = False
            self._script_row_who = ''
            self._in_script_row = False

        # 形式B終了
        if self._in_text_b and depth < self._text_b_depth:
            text = getattr(self, '_text_b_text', '').strip()
            who  = self._dialog_who
            if text and who and who not in ('P', 'ナレーション', ''):
                self.entries.append((who, text))
            self._in_text_b = False

        if tag == 'div' and self._in_dialog_body:
            # bodyが終わったらリセット（depth管理は省略、簡易実装）
            pass

        # 形式C終了
        if self._in_speaker_c and tag == 'span':
            self._in_speaker_c = False
        if self._in_ud_line and depth < self._ud_depth:
            text = ''.join(self._ud_text_parts).strip()
            who  = self._ud_line_who
            if text and who and who not in ('P', 'ナレーション', ''):
                self.entries.append((who, text))
            self._in_ud_line = False

        # 形式E終了: <p>
        # </p> を受け取った時点で確定させる。深さ比較だけだと </p> の時点では
        # まだスタックが同じ深さのため確定せず、同じアコーディオン内の最後の
        # 1行しかインデックスに載らなかった。
        if self._in_v2_p_e and (tag == 'p' or depth < self._v2_p_e_depth):
            text = self._v2_p_e_text.strip()
            if text and self.card_idol:
                # カード詳細のセリフなので、検索では「カード」として扱う
                self.card_entries.append((self.card_idol, text))
            self._in_v2_p_e = False
            self._v2_p_e_text = ''
        # 形式E終了: .v2-accord-body
        if self._in_v2_accord_body_e and depth < self._v2_accord_body_e_depth:
            self._in_v2_accord_body_e = False
        # 形式E終了: .v2-dialogue-content
        if self._in_v2_dialogue and depth < self._v2_dialogue_depth:
            self._in_v2_dialogue = False

        # 形式F: 除外領域（speaker / ev-condition / dss-stage-text）終了
        if self._f_skip_depth >= 0 and depth <= self._f_skip_depth:
            self._f_skip_depth = -1
        # 形式F終了: ev-text
        if self._in_standalone_ev_text_f and depth < self._standalone_ev_text_f_depth:
            text = self._standalone_ev_text_f_text.strip()
            who = self._standalone_ev_who or '心'
            if text and who not in ('P', 'ナレーション'):
                self.entries.append((who, text))
            self._in_standalone_ev_text_f = False
        # 形式F終了: ev-dialog-row
        if self._in_standalone_ev_row and depth < self._standalone_ev_row_depth:
            self._in_standalone_ev_row = False

        # 形式D: ev-text 内の speaker スパン終了
        if self._in_ev_text_speaker and tag == 'span':
            self._in_ev_text_speaker = False

        # 形式D終了
        if self._in_ev_text_d and depth < self._ev_text_d_depth:
            text = self._ev_text_d_text.strip()
            # 行ごとの話者があればそれを優先、なければアコーディオンヘッドの話者
            who  = self._ev_text_line_who if self._ev_text_line_who else self._v2_accord_who
            if text and who and who not in ('P', 'ナレーション', ''):
                self.entries.append((who, text))
            self._in_ev_text_d = False
        if tag == 'div' and self._v2_accord_depth >= 0 and depth < self._v2_accord_depth:
            self._v2_accord_depth = -1
            self._v2_accord_who = ''

        # <title>
        if tag == 'title':
            self._in_title = False

        if self._stack:
            self._stack.pop()

    def handle_data(self, data):
        if self._in_title:
            self.title += data

        if self._in_line_a:
            self._line_a_text = getattr(self, '_line_a_text', '') + data

        if self._in_text_b:
            self._text_b_text = getattr(self, '_text_b_text', '') + data

        if self._in_ud_line:
            if self._in_speaker_c:
                self._ud_line_who += data
            else:
                self._ud_text_parts.append(data)

        if self._in_ev_text_d and not self._in_ev_text_speaker:
            self._ev_text_d_text += data

        if self._in_v2_p_e:
            self._v2_p_e_text += data

        if self._in_standalone_ev_text_f and self._f_skip_depth < 0:
            self._standalone_ev_text_f_text += data


def html_to_url(html_path):
    """絶対パスをサイトルートからの相対URLに変換する。"""
    rel = os.path.relpath(html_path, BASE_DIR)
    return rel.replace(os.sep, '/')


def load_story_entries(idol_map):
    entries = []
    # スキャン対象
    patterns = [
        os.path.join(BASE_DIR, 'Mobamas', '**', '*.html'),
        os.path.join(BASE_DIR, 'Deresute', '**', '*.html'),
        os.path.join(BASE_DIR, 'Popmas', '*.html'),
    ]
    # スキップするファイル名パターン
    SKIP_FILES = {'index.html', 'EventList.html', 'CardList.html', 'CostumeList.html',
                  'OtherGameCenter.html', 'Derepo.html'}

    html_files = []
    for pattern in patterns:
        html_files.extend(glob.glob(pattern, recursive=True))

    for html_path in sorted(html_files):
        fname = os.path.basename(html_path)
        if fname in SKIP_FILES:
            continue

        try:
            with open(html_path, encoding='utf-8', errors='ignore') as f:
                html = f.read()
        except Exception:
            continue

        # カード詳細ページのセリフ（形式E）はページ内に話者名を持たないため、
        # カード名（例: "[ハート・モデル]佐藤心+"）からアイドルを判定して話者にする
        title_m = re.search(r'<title>([^<]*)</title>', html)
        raw_title = re.split(r'[｜|]', title_m.group(1))[0].strip() if title_m else ''
        card_idol = extract_idol_short(raw_title, idol_map)

        parser = DialogueParser(card_idol=card_idol)
        try:
            parser.feed(html)
        except Exception:
            continue

        # <title> の ｜ 以降を除去（例: "シンデレラヒストリー｜SugarHeartDB" → "シンデレラヒストリー"）
        page_title = re.split(r'[｜|]', parser.title)[0].strip()
        url = html_to_url(html_path)

        for who, text in parser.entries:
            # data-who に含まれる短縮名リストを取得
            idol_str = ' '.join(
                n.strip()
                for n in who.split('・')
                if n.strip()
            )
            entries.append({
                'type':    'story',
                'title':   page_title,
                'text':    text,
                'idol':    idol_str,
                'context': page_title,
                'url':     url,
            })

        # カード詳細ページのセリフは検索の「カード」タブに出す
        for who, text in parser.card_entries:
            entries.append({
                'type':    'card',
                'title':   page_title,
                'text':    text,
                'idol':    who,
                'context': page_title,
                'url':     url,
            })

    return entries


def load_derepo_entries(idol_map):
    """でれぽ書き起こし(scripts/derepo_text/*.json)から検索エントリを生成する。
    HTMLは解析せず、書き起こしJSONを直接読む（生成ページと二重計上しない）。"""
    full_to_short = {full: short for short, full in idol_map.items()}
    entries = []
    pat = os.path.join(BASE_DIR, 'scripts', 'derepo_text', '*.json')
    for path in sorted(glob.glob(pat), key=lambda p: int(os.path.splitext(os.path.basename(p))[0])):
        try:
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            continue
        for post in data.get('posts', []):
            name = post.get('name', '').strip()
            text = post.get('text', '').strip()
            if not text:
                continue
            entries.append({
                'type':    'story',
                'title':   'でれぽ',
                'text':    text,
                'idol':    full_to_short.get(name, name),
                'context': 'でれぽ',
                'url':     'Deresute/CinderellaTheater/Derepo.html',
            })
    return entries


# ─────────────────────────────────────────────
# メイン処理
# ─────────────────────────────────────────────

def main():
    print('アイドルデータ読み込み中...')
    idol_map     = load_idols()
    unit_url_map = load_unit_url_map()

    print('カードエントリ生成中...')
    card_entries = load_card_entries(idol_map)
    print(f'  → {len(card_entries)} エントリ')

    print('ユニットエントリ生成中...')
    unit_entries = load_unit_entries(idol_map, unit_url_map)
    print(f'  → {len(unit_entries)} エントリ')

    print('ストーリーエントリ生成中...')
    story_entries = load_story_entries(idol_map)
    print(f'  → {len(story_entries)} エントリ')

    print('でれぽエントリ生成中...')
    derepo_entries = load_derepo_entries(idol_map)
    print(f'  → {len(derepo_entries)} エントリ')

    all_entries = card_entries + unit_entries + story_entries + derepo_entries
    print(f'合計: {len(all_entries)} エントリ')

    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, separators=(',', ':'))

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f'出力完了: {OUTPUT_FILE} ({size_kb:.1f} KB)')


if __name__ == '__main__':
    main()
