#!/usr/bin/env python3
"""
_generate_search_index.py
data/search-index.json を生成するスクリプト。

対象:
  - data/mobamas.csv  → type: "card"
  - data/udetail.csv  → type: "unit"
  - Mobamas/**/*.html, Deresute/**/*.html → type: "story"

使い方:
  python _generate_search_index.py
"""

import csv
import json
import os
import re
import glob
from html.parser import HTMLParser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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


def load_card_entries(idol_map):
    entries = []
    path = os.path.join(BASE_DIR, 'data', 'mobamas.csv')
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
                        'url':     'CardList.html',
                    })
    return entries


# ─────────────────────────────────────────────
# 4. udetail.csv → ユニット台詞エントリ生成
# ─────────────────────────────────────────────

# 台詞の種別ラベル
SERIF_CONTEXTS = ['登場時セリフ', 'バトル時セリフ', '勝利時セリフ', '敗北時セリフ', '引き分け時セリフ']


def load_unit_entries(idol_map, unit_url_map):
    entries = []
    ulist_path = os.path.join(BASE_DIR, 'data', 'ulist.csv')
    udetail_path = os.path.join(BASE_DIR, 'data', 'udetail.csv')

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

            # メンバーの短縮名リスト
            member_shorts = []
            for full in unit_members_full.get(uname, []):
                short = full_to_short.get(full, '')
                if short:
                    member_shorts.append(short)
            idol_str = ' '.join(member_shorts)

            # 各種セリフ
            for ctx in SERIF_CONTEXTS:
                for n in ['1', '2']:
                    speaker_col = f'{ctx}{n}話者'
                    text_col    = f'{ctx}{n}セリフ'
                    speaker = row.get(speaker_col, '').strip()
                    text    = row.get(text_col, '').strip()
                    if text:
                        entries.append({
                            'type':    'unit',
                            'title':   uname,
                            'text':    text,
                            'idol':    idol_str,
                            'context': ctx,
                            'url':     url,
                        })
    return entries


# ─────────────────────────────────────────────
# 5. HTML → ストーリー台詞エントリ生成
# ─────────────────────────────────────────────

class DialogueParser(HTMLParser):
    """
    HTML から会話行を抽出する。
    対応形式:
      A: .script-row[data-who] > .line
      B: .dialog .body > .line-head .speaker[data-who]  + .text
      C: .ud-dialogue .line（.speaker スパンはスキップ）
    """

    def __init__(self):
        super().__init__()
        self.entries = []     # [(idol, text)]
        self.title = ''

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
                self._script_row_who = attrs_dict.get('data-who', '')
        if self._in_script_row and tag == 'div' and self._has_class(attrs_dict, 'line'):
            self._in_line_a = True
            self._line_a_depth = len(self._stack)
            self._line_a_text = ''

        # 形式B: .dialog .body > speaker + text
        if tag == 'div' and self._has_class(attrs_dict, 'body'):
            self._in_dialog_body = True
            self._dialog_who = ''
        if self._in_dialog_body and tag == 'span' and self._has_class(attrs_dict, 'speaker'):
            who = attrs_dict.get('data-who', '')
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
    ]
    # スキップするファイル名パターン
    SKIP_FILES = {'index.html', 'EventList.html', 'CardList.html', 'CostumeList.html',
                  'OtherGameCenter.html'}

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

        parser = DialogueParser()
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

    all_entries = card_entries + unit_entries + story_entries
    print(f'合計: {len(all_entries)} エントリ')

    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_entries, f, ensure_ascii=False, separators=(',', ':'))

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f'出力完了: {OUTPUT_FILE} ({size_kb:.1f} KB)')


if __name__ == '__main__':
    main()
