# -*- coding: utf-8 -*-
"""
shiage_final.py
全6イベントのShiagePage処理スクリプト
"""
import re, json, os, ssl, urllib3

# ── Cloudinary セットアップ ──
def setup_cloudinary():
    d = open(r'C:/Users/sawas/.claude.json', encoding='utf-8').read()
    os.environ['CLOUDINARY_URL'] = re.search(r'cloudinary://[0-9]+:[^"\']+@dnmzdghoi', d).group(0)
    ssl._create_default_https_context = ssl._create_unverified_context
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    import cloudinary, cloudinary.uploader as up
    cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
    up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")
    return cloudinary, up

CDN = 'https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto'
IMG_DIR = r'C:\Users\sawas\OneDrive\Pictures\欠損部分'
REPO = r'C:\Users\sawas\Desktop\SugarHeartDB'
MAP_PATH = os.path.join(REPO, '_cloudinary_upload_map.json')

def load_upload_map():
    with open(MAP_PATH, encoding='utf-8') as f:
        return json.load(f)

def save_upload_map(m):
    with open(MAP_PATH, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(m, f, indent=1, ensure_ascii=False)
    print('upload_map 保存完了')

def upload(up, local_path, public_id, overwrite=True):
    result = up.upload(local_path, public_id=public_id, overwrite=overwrite)
    return result['secure_url']

def secs_to_ts(s):
    """秒 → chapters.txt 形式 (m:ss or h:mm:ss)"""
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    if h > 0:
        return f'{h}:{m:02d}:{sec:02d}'
    return f'{m}:{sec:02d}'

def secs_to_srt(s):
    """秒 → SRT タイムスタンプ (HH:MM:SS,mmm)"""
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f'{h:02d}:{m:02d}:{sec:02d},000'

def time_str_to_secs(t):
    """HH.MM.SS → 秒"""
    parts = t.split('.')
    if len(parts) == 3:
        h, m, sec = int(parts[0]), int(parts[1]), int(parts[2])
        return h * 3600 + m * 60 + sec
    elif len(parts) == 2:
        m, sec = int(parts[0]), int(parts[1])
        return m * 60 + sec
    return 0

# ────────────────────────────────────────────────
# GoJustGo
# ────────────────────────────────────────────────

def process_gojustgo(up, upload_map):
    print('\n=== Go Just Go！ ===')
    ev = 'GoJustGo'
    html_path = os.path.join(REPO, f'Deresute/Event/{ev}.html')
    CDN_BASE = f'Deresute/Event/{ev}/commu'

    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    uploads = [
        # (filename, frame_pid, alt, is_noshot_fill)
        ('Go Just Go！_00.53.40.png', '0387b', '一同のセリフ', True),
        ('Go Just Go！_00.57.25.png', '0424a', '唯のセリフ', False),
        ('Go Just Go！_00.57.30.png', '0424b', '志希のセリフ', False),
        ('Go Just Go！_00.57.35.png', '0424c', 'Pのセリフ', False),
    ]

    new_entries = {}
    for fname, pid, alt, is_noshot in uploads:
        local = os.path.join(IMG_DIR, fname)
        public_id = f'{CDN_BASE}/{pid}'
        url = upload(up, local, public_id, overwrite=True)
        new_entries[fname] = {'public_id': public_id, 'url': url}
        upload_map[fname] = public_id
        print(f'  ✓ {fname} → {pid}')

    # no-shot 行 (line 723: 一同「いってきます」) への shot 配備
    NOSHOT_KEY = 'いってきまーす♪'
    pattern = r'(<div class="ev-dialog-row no-shot">(<div class="ev-text">(?:(?!</div></div></div></div>).)*?' + re.escape(NOSHOT_KEY) + r'(?:(?!</div></div></div></div>).)*?</div></div></div></div>))'
    m = re.search(pattern, html, re.DOTALL)
    if m:
        old_row = m.group(0)
        text_part = old_row[old_row.index('<div class="ev-text">'):]
        pid_url = f'{CDN}/{CDN_BASE}/0387b'
        new_row = f'<div class="ev-dialog-row"><div class="ev-shot"><img src="{pid_url}" alt="一同のセリフ" loading="lazy"></div>{text_part}'
        html = html[:m.start()] + new_row + html[m.end():]
        print(f'  ✓ 0387b: 一同「いってきまーす♪」')
    else:
        print(f'  ✗ 一同「いってきまーす♪」 が見つからない')

    with open(html_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print(f'  GoJustGo.html 書き出し完了')

    # 検証
    remaining = html.count('class="ev-dialog-row no-shot"') - html.count('class="ev-dialog-row no-shot no-frame"')
    print(f'  残 no-shot (撮り漏れ): {remaining} 行')

# ────────────────────────────────────────────────
# 汎用: HTMLから no-shot 行を抽出 (tab別)
# ────────────────────────────────────────────────

def extract_noshot_rows(html, tab_prefix):
    """
    Returns: {tab_name: [{'pid': str, 'speaker': str, 'unique_text': str}]}
    pid は preceding_frame + letter で採番
    """
    import re as re2
    result = {}
    tabs_order = ['trailer', 'op', 'ep1', 'ep2', 'ep3', 'ep4', 'ep5', 'ed']

    for i, tab_name in enumerate(tabs_order):
        tab_id = f'{tab_prefix}-{tab_name}'
        tab_start = html.find(f'data-tab="{tab_id}"')
        if tab_start == -1:
            result[tab_name] = []
            continue
        if i + 1 < len(tabs_order):
            next_tab_id = f'{tab_prefix}-{tabs_order[i+1]}'
            tab_end = html.find(f'data-tab="{next_tab_id}"', tab_start + 1)
            if tab_end == -1:
                tab_end = len(html)
        else:
            tab_end = len(html)

        tab_html = html[tab_start:tab_end]
        events = []

        # commu フレーム画像の位置
        for m in re2.finditer(r'<img src="[^"]*/commu/([0-9][0-9a-z]*)"', tab_html):
            events.append((m.start(), 'frame', m.group(1)))

        # no-shot 行 (no-frame 除く)
        # no-shot no-frame は class="ev-dialog-row no-shot no-frame" (no-shot の後にスペース+no-frame)
        # no-shot のみ (クォートの前 or スペースのない終わり) で確実にマッチ
        noshot_re = re2.compile(
            r'<div class="ev-dialog-row no-shot">.*?</div></div></div></div>',
            re2.DOTALL
        )
        for m in noshot_re.finditer(tab_html):
            row_html = m.group(0)
            speaker_m = re2.search(r'data-who="([^"]+)"', row_html)
            line_m = re2.search(r'<div class="line">(.*?)</div>', row_html, re2.DOTALL)
            speaker = speaker_m.group(1) if speaker_m else ''
            line = line_m.group(1).strip() if line_m else ''
            events.append((m.start(), 'noshot', (speaker, line)))

        events.sort(key=lambda x: x[0])

        rows = []
        last_frame_base = 'UNKNOWN'
        frame_suffix_counter = {}
        # 既にHTMLで使われているpidを追跡
        used_pids = set(re2.findall(r'commu/([0-9][0-9a-z]*)"', tab_html))

        for pos, etype, data in events:
            if etype == 'frame':
                # ベースフレーム番号 (数字部分のみ)
                m2 = re2.match(r'([0-9]+)', data)
                last_frame_base = m2.group(1) if m2 else data
            elif etype == 'noshot':
                speaker, line = data
                base = last_frame_base
                count = frame_suffix_counter.get(base, 0)
                # 既存のpidと衝突しない文字を探す
                while True:
                    letter = chr(ord('a') + count)
                    candidate = f'{base}{letter}'
                    if candidate not in used_pids:
                        break
                    count += 1
                frame_suffix_counter[base] = count + 1
                used_pids.add(candidate)
                # unique_text: セリフの先頭40文字
                unique_text = line[:40]
                rows.append({
                    'pid': candidate,
                    'speaker': speaker,
                    'unique_text': unique_text,
                    'full_line': line,
                })

        result[tab_name] = rows

    return result

# ────────────────────────────────────────────────
# 汎用: タイトルカード差し替え
# ────────────────────────────────────────────────

def replace_title_card(html, tab_prefix, tab_name, old_frame, new_pid, cdn_base):
    """tab内のdss-title-card imgのsrcを差し替え"""
    tab_id = f'{tab_prefix}-{tab_name}'
    # old_frame は末尾フレーム番号 (例: '0009')
    old_src = f'{CDN}/{cdn_base}/{old_frame}"'
    new_src = f'{CDN}/{cdn_base}/{new_pid}"'
    count = html.count(old_src)
    if count == 0:
        print(f'  ✗ {tab_name} title-card: {old_frame} が見つからない')
        return html
    if count > 1:
        print(f'  ⚠ {tab_name} title-card: {old_frame} が {count} 箇所 (1つだけ置換)')
    html = html.replace(old_src, new_src, 1)
    print(f'  ✓ title-card [{tab_name}]: {old_frame} → {new_pid}')
    return html

def replace_data_start(html, tab_prefix, tab_name, old_val, new_val):
    """tab内のdata-startを更新"""
    tab_id = f'{tab_prefix}-{tab_name}'
    tab_start = html.find(f'data-tab="{tab_id}"')
    if tab_start == -1:
        return html
    # このタブの最初のdata-start="old_val"を探す
    needle = f'data-start="{old_val}">'
    idx = html.find(needle, tab_start)
    if idx == -1:
        print(f'  ✗ data-start {old_val} [{tab_name}] が見つからない')
        return html
    html = html[:idx] + f'data-start="{new_val}">' + html[idx+len(needle):]
    print(f'  ✓ data-start [{tab_name}]: {old_val} → {new_val}')
    return html

# ────────────────────────────────────────────────
# 汎用: no-shot行への shot 配備
# ────────────────────────────────────────────────

def add_shot(html, unique_text, pid_url, alt):
    """no-shot行の unique_text を含む行に shot を配備"""
    pattern = (r'(<div class="ev-dialog-row no-shot">(<div class="ev-text">(?:(?!</div></div></div></div>).)*?'
               + re.escape(unique_text)
               + r'(?:(?!</div></div></div></div>).)*?</div></div></div></div>))')
    m = re.search(pattern, html, re.DOTALL)
    if not m:
        raise ValueError(f'行が見つからない: {unique_text[:50]}')
    old_row = m.group(0)
    text_part = old_row[old_row.index('<div class="ev-text">'):]
    new_row = f'<div class="ev-dialog-row"><div class="ev-shot"><img src="{pid_url}" alt="{alt}" loading="lazy"></div>{text_part}'
    return html[:m.start()] + new_row + html[m.end():]

# ────────────────────────────────────────────────
# chapters.txt 更新
# ────────────────────────────────────────────────

def update_chapters_txt(chapters_path, tab_names, new_secs_map):
    """
    new_secs_map: {tab_name: new_seconds}
    tab_names: chapters.txt の行と対応するタブ名リスト (Twitter予告/予告1/予告2/OP/1話...EDの順)
    """
    if not os.path.exists(chapters_path):
        print(f'  chapters.txt が見つからない: {chapters_path}')
        return

    with open(chapters_path, encoding='utf-8') as f:
        lines = f.readlines()

    # chapters.txt の各行: "M:SS 説明" or "H:MM:SS 説明"
    # tab_names との対応: 最初の行がTwitter予告(skip), 次が予告1, 予告2, OP, 1話...
    # OP = tab_names[0]..? 実際の対応は event ごとに異なる

    # 対応表: line_index → tab_name
    # chapters.txt の行数: 10 (Twitter/予告1/予告2/OP/1話/2話/3話/4話/5話/ED)
    tab_line_map = {
        'op': 3, 'ep1': 4, 'ep2': 5, 'ep3': 6, 'ep4': 7, 'ep5': 8, 'ed': 9,
        'trailer': 1,  # 予告1 に相当
    }

    changed = False
    for tab_name, new_s in new_secs_map.items():
        line_idx = tab_line_map.get(tab_name)
        if line_idx is None or line_idx >= len(lines):
            continue
        line = lines[line_idx]
        parts = line.split(' ', 1)
        if len(parts) < 2:
            continue
        old_ts, label = parts[0], parts[1]
        new_ts = secs_to_ts(new_s)
        if old_ts == new_ts:
            print(f'  章時刻 [{tab_name}]: {old_ts} (変更なし)')
            continue
        lines[line_idx] = f'{new_ts} {label}'
        print(f'  ✓ 章時刻 [{tab_name}]: {old_ts} → {new_ts}')
        changed = True

    if changed:
        with open(chapters_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f'  chapters.txt 保存完了')

# ────────────────────────────────────────────────
# SRT 更新
# ────────────────────────────────────────────────

def parse_srt(path):
    """SRTを [{'start': str, 'end': str, 'text': str}] のリストとして返す"""
    with open(path, encoding='utf-8-sig', newline='') as f:
        content = f.read()
    blocks = []
    # ブロック分割: 空行で区切る
    raw_blocks = re.split(r'\r?\n\r?\n', content.strip())
    for block in raw_blocks:
        lines_b = block.strip().splitlines()
        if len(lines_b) < 2:
            continue
        # 1行目: 番号 (スキップ)
        # 2行目: タイムスタンプ
        ts_line = None
        text_lines = []
        for line in lines_b:
            if re.match(r'^\d+$', line.strip()):
                continue
            if re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', line):
                ts_line = line
            elif ts_line is not None:
                text_lines.append(line)
        if ts_line:
            start, end = ts_line.split(' --> ')
            blocks.append({'start': start.strip(), 'end': end.strip(), 'text': '\n'.join(text_lines)})
    return blocks

def srt_ts_to_ms(ts):
    """HH:MM:SS,mmm → ミリ秒"""
    h, m, rest = ts.split(':')
    s, ms = rest.split(',')
    return int(h)*3600000 + int(m)*60000 + int(s)*1000 + int(ms)

def ms_to_srt_ts(ms):
    """ミリ秒 → HH:MM:SS,mmm"""
    h = ms // 3600000
    ms %= 3600000
    m = ms // 60000
    ms %= 60000
    s = ms // 1000
    ms %= 1000
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

def write_srt(path, blocks):
    """SRT ブロックリストをファイルに書き出す (CRLF)"""
    lines = []
    for i, b in enumerate(blocks, 1):
        lines.append(str(i))
        lines.append(f'{b["start"]} --> {b["end"]}')
        lines.append(b['text'])
        lines.append('')
    with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('\n'.join(lines))

def update_srt(srt_path, tab_chapter_secs):
    """
    tab_chapter_secs: {tab_name: new_chapter_seconds}
    各タブの章タイトル字幕 (【タイトル...】 形式) の開始時刻を更新
    """
    if not os.path.exists(srt_path):
        print(f'  SRT が見つからない: {srt_path}')
        return

    blocks = parse_srt(srt_path)
    changed = False

    tab_label_map = {
        'op':  'OP',
        'ep1': '第1話',
        'ep2': '第2話',
        'ep3': '第3話',
        'ep4': '第4話',
        'ep5': '第5話',
        'ed':  'ED',
    }

    for tab_name, new_s in sorted(tab_chapter_secs.items()):
        label = tab_label_map.get(tab_name)
        if label is None:
            continue
        new_ms = new_s * 1000

        # 章タイトル字幕を探す
        found = False
        for idx, b in enumerate(blocks):
            if label in b['text'] and '【' in b['text']:
                old_start_ms = srt_ts_to_ms(b['start'])
                if abs(old_start_ms - new_ms) < 10:  # 既に正しい
                    print(f'  SRT [{tab_name}]: {b["start"]} (変更なし)')
                    found = True
                    break
                # 前のブロックの end を new_ms に揃える
                if idx > 0:
                    old_end = blocks[idx-1]['end']
                    blocks[idx-1]['end'] = ms_to_srt_ts(new_ms)
                    print(f'  ✓ SRT 前ブロック end: {old_end} → {ms_to_srt_ts(new_ms)}')
                old_start = b['start']
                b['start'] = ms_to_srt_ts(new_ms)
                print(f'  ✓ SRT 【{label}】 start: {old_start} → {b["start"]}')
                changed = True
                found = True
                break
        if not found:
            print(f'  ⚠ SRT 【{label}】 が見つからない')

    if changed:
        write_srt(srt_path, blocks)
        print(f'  SRT 保存完了')

# ────────────────────────────────────────────────
# イベント設定
# ────────────────────────────────────────────────

# 各イベントの設定
# title_cards: {tab_name: (image_filename_time, old_placeholder_frame, new_pid_suffix)}
# image_filename_time: ファイル名の HH.MM.SS 部分
# old_placeholder_frame: HTML内の現在のtitle-card imgのフレーム番号
# new_pid_suffix: Cloudinary に登録する pid (title_op など)
# chapter_tab_order: chapters.txt のどの行(0-indexed)がどのタブか

EVENT_CONFIGS = {
    'OdoruFlagship': {
        'prefix': 'odf',
        'img_prefix': '躍るFLAGSHIP',
        'html': 'Deresute/Event/OdoruFlagship.html',
        'cdn_base': 'Deresute/Event/OdoruFlagship/commu',
        'chapters_path': '',
        'srt_path': '',
        'title_cards': {
            # tab_name: (img_time_str, old_frame, new_pid, img_secs)
            'op':  ('00.02.03', '0009', 'title_op',  123),
            'ep1': ('00.10.17', '0062', 'title_1',   617),
            'ep2': ('00.18.47', '0104', 'title_2',  1127),
            'ep3': ('00.28.19', '0158', 'title_3',  1699),
            'ep4': ('00.37.36', '0211', 'title_4',  2256),
        },
        # serifs_by_tab: {tab_name: [img_time_str, ...]} (タイトルカード除く)
        'serifs_by_tab': {
            'trailer': ['00.00.50', '00.01.36'],
            'op':      ['00.02.08', '00.07.55', '00.09.07'],
            'ep1':     ['00.10.52', '00.11.39', '00.12.24', '00.15.07', '00.16.31', '00.18.15', '00.18.34'],
            'ep2':     ['00.21.23', '00.21.56', '00.22.02', '00.22.15', '00.22.22', '00.22.38',
                        '00.22.49', '00.23.06', '00.23.18', '00.23.35', '00.23.46', '00.23.51',
                        '00.24.00', '00.27.26', '00.27.39'],
            'ep3':     ['00.35.06', '00.35.40', '00.36.25', '00.37.08', '00.37.17', '00.37.22',
                        '00.37.28', '00.37.31'],
            'ep4':     ['00.42.41', '00.42.53', '00.43.47', '00.44.44', '00.45.40', '00.46.10',
                        '00.46.48', '00.47.12'],
            'ep5':     ['00.48.03', '00.48.30', '00.49.33'],
            'ed':      ['00.57.18', '00.59.23'],
        },
    },
    'CoCoNatsuHoliday': {
        'prefix': 'csh',
        'img_prefix': 'CoCo夏夏夏Holiday',
        'html': 'Deresute/Event/CoCoNatsuHoliday.html',
        'cdn_base': 'Deresute/Event/CoCoNatsuHoliday/commu',
        'chapters_path': r'G:\マイドライブ\コミュ\YouTube_CoCo夏夏夏 Holiday\chapters.txt',
        'srt_path': r'G:\マイドライブ\コミュ\YouTube_CoCo夏夏夏 Holiday\subtitles_ja.srt',
        'title_cards': {
            'op':  ('00.02.10', '0009', 'title_op',  130),
            'ep1': ('00.10.50', '0067', 'title_1',   650),
            'ep2': ('00.18.12', '0118', 'title_2',  1092),
            'ep3': ('00.25.36', '0178', 'title_3',  1536),
            'ep4': ('00.34.05', '0213', 'title_4',  2045),
            'ep5': ('00.41.48', '0262', 'title_5',  2508),
            'ed':  ('00.48.00', '0302', 'title_ed', 2880),
        },
        'serifs_by_tab': {
            'trailer': ['00.00.58'],
            'op':      ['00.02.19', '00.02.31', '00.03.03', '00.05.42', '00.06.28',
                        '00.06.39', '00.07.14'],
            'ep1':     ['00.11.11'],
            'ep2':     ['00.19.46', '00.20.42'],
            'ep3':     ['00.25.43', '00.26.21', '00.26.52', '00.27.33', '00.28.41',
                        '00.28.56', '00.29.01', '00.29.16', '00.29.24', '00.29.37',
                        '00.30.07', '00.30.27', '00.30.32', '00.30.34', '00.30.57',
                        '00.31.14', '00.31.20', '00.32.34', '00.33.41'],
            'ep4':     ['00.35.55', '00.36.02', '00.36.33', '00.36.38', '00.36.54',
                        '00.39.03', '00.39.10', '00.39.37'],
            'ep5':     ['00.46.01'],
            'ed':      ['00.51.14', '00.51.40', '00.51.45'],
        },
    },
    'DancingDead': {
        'prefix': 'dd',
        'img_prefix': 'ダンシング・デッド',
        'html': 'Deresute/Event/DancingDead.html',
        'cdn_base': 'Deresute/Event/DancingDead/commu',
        'chapters_path': '',
        'srt_path': '',
        'title_cards': {
            'op':  ('00.02.41', '0009', 'title_op',  161),
            'ep5': ('00.48.32', '0294', 'title_5',  2912),
        },
        'serifs_by_tab': {
            'trailer': ['00.01.27', '00.02.11'],
            'op':      ['00.03.04', '00.04.51', '00.08.01', '00.08.11', '00.08.16',
                        '00.08.31', '00.08.53'],
            'ep1':     ['00.13.47', '00.14.03', '00.14.57', '00.15.29', '00.15.50', '00.17.44'],
            'ep2':     ['00.21.22', '00.24.11', '00.24.26', '00.25.09', '00.26.02',
                        '00.27.44', '00.30.28'],
            'ep3':     ['00.32.58', '00.33.52', '00.35.12', '00.35.17', '00.35.33',
                        '00.35.57', '00.36.30', '00.37.15', '00.39.40', '00.40.08'],
            'ep4':     ['00.41.27', '00.44.28', '00.45.06', '00.48.01', '00.48.27'],
            'ep5':     ['00.53.08', '00.53.16', '00.54.55', '00.56.28', '00.59.17'],
            'ed':      ['01.01.05', '01.01.28', '01.01.45', '01.02.33'],
        },
    },
    'NextChapter': {
        'prefix': 'nc',
        'img_prefix': 'Next Chapter',
        'html': 'Deresute/Event/NextChapter.html',
        'cdn_base': 'Deresute/Event/NextChapter/commu',
        'chapters_path': r'G:\マイドライブ\コミュ\YouTube_Next Chapter\chapters.txt',
        'srt_path': r'G:\マイドライブ\コミュ\YouTube_Next Chapter\subtitles_ja.srt',
        'title_cards': {
            'op':  ('00.03.42', '0011', 'title_op',  222),
            'ep1': ('00.14.08', '0070', 'title_1',   848),
            'ep2': ('00.23.25', '0128', 'title_2',  1405),
            'ep3': ('00.33.33', '0174', 'title_3',  2013),
            'ep4': ('00.42.35', '0187', 'title_4',  2555),
            'ep5': ('00.52.41', '0246', 'title_5',  3161),
            'ed':  ('01.05.17', '0294', 'title_ed', 3917),
        },
        'serifs_by_tab': {
            'trailer': ['00.01.50'],
            'op':      ['00.05.41', '00.08.42', '00.09.03', '00.09.59'],
            'ep1':     ['00.14.11'],
            'ep2':     ['00.23.27', '00.23.40', '00.23.53', '00.24.12', '00.24.20',
                        '00.24.38', '00.27.26', '00.31.24', '00.32.47'],
            'ep3':     ['00.33.36', '00.33.47', '00.33.56', '00.34.06', '00.34.12',
                        '00.34.18', '00.34.35', '00.34.41', '00.34.45', '00.34.58',
                        '00.35.10', '00.35.14', '00.35.23', '00.35.30', '00.35.35',
                        '00.35.45', '00.35.51', '00.36.01', '00.36.08', '00.36.13',
                        '00.36.25', '00.36.40', '00.36.52', '00.37.07', '00.37.14',
                        '00.37.35', '00.37.48', '00.37.59', '00.38.13', '00.38.25',
                        '00.38.33', '00.38.51', '00.38.54', '00.39.05', '00.39.17',
                        '00.39.36', '00.40.05'],
            'ep4':     ['00.44.01', '00.44.25', '00.44.33', '00.47.48', '00.48.03',
                        '00.48.33', '00.49.41'],
            'ep5':     ['00.53.24', '00.53.33', '01.00.49', '01.01.03', '01.01.57',
                        '01.02.07', '01.02.18', '01.02.34', '01.03.02', '01.03.24',
                        '01.03.41', '01.04.00', '01.04.47'],
            'ed':      ['01.07.35', '01.07.40', '01.09.01', '01.11.41'],
        },
    },
    'NetsujouEnamorar': {
        'prefix': 'ne',
        'img_prefix': '熱情エナモラル',
        'html': 'Deresute/Event/NetsujouEnamorar.html',
        'cdn_base': 'Deresute/Event/NetsujouEnamorar/commu',
        'chapters_path': '',
        'srt_path': '',
        'title_cards': {
            'op':  ('00.04.21', '0009', 'title_op',  261),
            'ep2': ('00.30.02', '0118', 'title_2',  1802),
            'ep3': ('00.40.28', '0185', 'title_3',  2428),
            'ep4': ('00.50.27', '0241', 'title_4',  3027),
            'ep5': ('01.02.08', '0314', 'title_5',  3728),
        },
        'serifs_by_tab': {
            'trailer': ['00.01.56'],
            'op':      ['00.09.59', '00.16.41', '00.16.55'],
            'ep1':     ['00.19.05', '00.19.52', '00.20.42', '00.23.00', '00.23.15',
                        '00.23.34', '00.23.39', '00.24.05', '00.24.19', '00.24.25',
                        '00.26.34', '00.27.11', '00.29.27', '00.29.34'],
            'ep2':     ['00.30.10', '00.34.22'],
            'ep3':     ['00.40.45', '00.43.04', '00.43.14', '00.45.41', '00.45.55',
                        '00.46.37', '00.47.14'],
            'ep4':     ['00.50.34', '00.52.46', '00.54.39', '00.58.11', '00.58.30',
                        '00.59.04'],
            'ep5':     ['01.02.15', '01.02.22', '01.02.33', '01.05.06', '01.05.32'],
            'ed':      [],
        },
    },
}

# ────────────────────────────────────────────────
# イベント処理メイン
# ────────────────────────────────────────────────

def process_event(ev_name, config, up, upload_map, dry_run=False):
    print(f'\n=== {ev_name} ===')

    prefix = config['prefix']
    img_prefix = config['img_prefix']
    html_path = os.path.join(REPO, config['html'])
    cdn_base = config['cdn_base']

    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    # ── 1. no-shot 行を HTML から抽出 ──
    noshot_by_tab = extract_noshot_rows(html, prefix)
    total_noshot = sum(len(v) for v in noshot_by_tab.values())
    print(f'  no-shot 行 (合計): {total_noshot}')

    # ── 2. タイトルカードと serif の対応確認 ──
    serifs_by_tab = config['serifs_by_tab']
    title_cards = config['title_cards']

    # serif マッピング
    assignments = {}  # tab_name → [(row_dict, img_time_str)]
    missing_rows = {}  # tab_name → [row_dict]
    extra_imgs = {}  # tab_name → [img_time_str]

    for tab_name, rows in noshot_by_tab.items():
        serifs = serifs_by_tab.get(tab_name, [])
        assigned = []
        for i, row in enumerate(rows):
            if i < len(serifs):
                assigned.append((row, serifs[i]))
            else:
                missing_rows.setdefault(tab_name, []).append(row)
        assignments[tab_name] = assigned
        if len(serifs) > len(rows):
            extra_imgs[tab_name] = serifs[len(rows):]

    # 集計表示
    for tab_name in ['trailer', 'op', 'ep1', 'ep2', 'ep3', 'ep4', 'ep5', 'ed']:
        rows = noshot_by_tab.get(tab_name, [])
        serifs = serifs_by_tab.get(tab_name, [])
        filled = len(assignments.get(tab_name, []))
        missing = len(missing_rows.get(tab_name, []))
        extra = len(extra_imgs.get(tab_name, []))
        tc = '✓' if tab_name in title_cards else '-'
        print(f'  [{tc}] {tab_name}: rows={len(rows)}, serifs={len(serifs)}, fill={filled}, miss={missing}, extra={extra}')

    if dry_run:
        print('  [dry_run] ここで停止')
        return

    # ── 3. タイトルカードのアップロードと HTML 更新 ──
    for tab_name, (img_time, old_frame, new_pid, img_secs) in title_cards.items():
        fname = f'{img_prefix}_{img_time}.png'
        local = os.path.join(IMG_DIR, fname)
        public_id = f'{cdn_base}/{new_pid}'
        url = upload(up, local, public_id, overwrite=True)
        upload_map[fname] = public_id
        print(f'  ✓ upload title [{tab_name}]: {fname} → {new_pid}')

        # HTML: title-card 差し替え
        html = replace_title_card(html, prefix, tab_name, old_frame, new_pid, cdn_base)

        # data-start 更新: new_chapter_secs = img_secs - 1
        new_ds = img_secs - 1
        # 現在の data-start を探す
        tab_id = f'{prefix}-{tab_name}'
        tab_start = html.find(f'data-tab="{tab_id}"')
        if tab_start != -1:
            m = re.search(r'data-start="(\d+)"', html[tab_start:tab_start+2000])
            if m:
                old_ds = int(m.group(1))
                html = replace_data_start(html, prefix, tab_name, old_ds, new_ds)

    # ── 4. serif のアップロードと no-shot 行配備 ──
    changes = 0
    for tab_name, assigned in assignments.items():
        for row, img_time in assigned:
            fname = f'{img_prefix}_{img_time}.png'
            local = os.path.join(IMG_DIR, fname)
            public_id = f'{cdn_base}/{row["pid"]}'
            pid_url = f'{CDN}/{public_id}'
            alt = f'{row["speaker"]}のセリフ'

            # アップロード
            url = upload(up, local, public_id, overwrite=True)
            upload_map[fname] = public_id

            # HTML 更新
            try:
                html = add_shot(html, row['unique_text'], pid_url, alt)
                changes += 1
                print(f'  ✓ {row["pid"]}: {row["unique_text"][:30]}')
            except ValueError as e:
                print(f'  ✗ {row["pid"]}: {e}')

    # ── 5. HTML 書き出し ──
    with open(html_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print(f'  HTML 書き出し完了 ({changes} 行配備)')

    # 残 no-shot 集計
    remaining = html.count('class="ev-dialog-row no-shot"') - html.count('class="ev-dialog-row no-shot no-frame"')
    total_miss = sum(len(v) for v in missing_rows.values())
    print(f'  残 no-shot: {remaining} (撮り漏れ: {total_miss})')
    for tab_name, rows in missing_rows.items():
        for row in rows:
            print(f'    撮り漏れ [{tab_name}]: {row["unique_text"][:40]}')

    # ── 6. chapters.txt 更新 ──
    chapters_path = config.get('chapters_path', '')
    if chapters_path:
        new_secs_map = {tab_name: img_secs - 1 for tab_name, (_, _, _, img_secs) in title_cards.items()}
        update_chapters_txt(chapters_path, None, new_secs_map)

    # ── 7. SRT 更新 ──
    srt_path = config.get('srt_path', '')
    if srt_path:
        srt_secs_map = {tab_name: img_secs - 1 for tab_name, (_, _, _, img_secs) in title_cards.items()}
        update_srt(srt_path, srt_secs_map)


# ────────────────────────────────────────────────
# main
# ────────────────────────────────────────────────

if __name__ == '__main__':
    import sys
    dry_run = '--dry' in sys.argv

    cloudinary, up = setup_cloudinary()
    upload_map = load_upload_map()

    # GoJustGo
    process_gojustgo(up, upload_map)

    # 5イベント
    for ev_name, config in EVENT_CONFIGS.items():
        process_event(ev_name, config, up, upload_map, dry_run=dry_run)

    # upload_map 保存
    save_upload_map(upload_map)

    print('\n=== 全処理完了 ===')
