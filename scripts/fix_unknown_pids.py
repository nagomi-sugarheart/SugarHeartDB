# -*- coding: utf-8 -*-
"""
fix_unknown_pids.py
extract_noshot_rows の lightbox-trigger 未検出バグにより
commu/UNKNOWNx で配備されてしまった行を正しいピッドに修正する。
"""
import re, json, os, sys, ssl, urllib3

CDN = 'https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto'
IMG_DIR = r'C:\Users\sawas\OneDrive\Pictures\欠損部分'
REPO    = r'C:\Users\sawas\Desktop\SugarHeartDB'
MAP_PATH = os.path.join(REPO, '_cloudinary_upload_map.json')

def setup_cloudinary():
    d = open(r'C:/Users/sawas/.claude.json', encoding='utf-8').read()
    os.environ['CLOUDINARY_URL'] = re.search(r'cloudinary://[0-9]+:[^"\']+@dnmzdghoi', d).group(0)
    ssl._create_default_https_context = ssl._create_unverified_context
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    import cloudinary, cloudinary.uploader as up
    cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
    up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")
    return cloudinary, up

def suffix_letter(count):
    if count < 26:
        return chr(ord('a') + count)
    first = (count // 26) - 1
    second = count % 26
    return chr(ord('a') + first) + chr(ord('a') + second)

# ── EVENT_CONFIGS (shiage_final.py と同じ) ──
EVENT_CONFIGS = {
    'OdoruFlagship': {
        'prefix': 'odf', 'img_prefix': '躍るFLAGSHIP',
        'html': 'Deresute/Event/OdoruFlagship.html',
        'cdn_base': 'Deresute/Event/OdoruFlagship/commu',
        'title_cards': {
            'op':  ('00.02.03', '0009', 'title_op',  123),
            'ep1': ('00.10.17', '0062', 'title_1',   617),
            'ep2': ('00.18.47', '0104', 'title_2',  1127),
            'ep3': ('00.28.19', '0158', 'title_3',  1699),
            'ep4': ('00.37.36', '0211', 'title_4',  2256),
        },
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
        'prefix': 'csh', 'img_prefix': 'CoCo夏夏夏Holiday',
        'html': 'Deresute/Event/CoCoNatsuHoliday.html',
        'cdn_base': 'Deresute/Event/CoCoNatsuHoliday/commu',
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
    'NextChapter': {
        'prefix': 'nc', 'img_prefix': 'Next Chapter',
        'html': 'Deresute/Event/NextChapter.html',
        'cdn_base': 'Deresute/Event/NextChapter/commu',
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
        'prefix': 'ne', 'img_prefix': '熱情エナモラル',
        'html': 'Deresute/Event/NetsujouEnamorar.html',
        'cdn_base': 'Deresute/Event/NetsujouEnamorar/commu',
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

TABS_ORDER = ['trailer', 'op', 'ep1', 'ep2', 'ep3', 'ep4', 'ep5', 'ed']

# UNKNOWN行パターン（どんなsuffix文字でも対応）
UNKNOWN_ROW_PAT = re.compile(
    r'<div class="ev-dialog-row"><div class="ev-shot">'
    r'<img\b[^>]*?src="[^"]*/commu/(UNKNOWN[^"]*)"[^>]*>'
    r'</div>((?:(?!</div></div></div></div>).)*?</div></div></div></div>)',
    re.DOTALL
)

# 通常フレーム（数字始まり、lightbox-trigger なし）
REGULAR_FRAME_PAT = re.compile(
    r'<img\b(?![^>]*class="lightbox-trigger")[^>]*?src="[^"]*/commu/([0-9][0-9a-z]*)"'
)
# lightbox-trigger フレーム（タイトルカード等）
LBT_FRAME_PAT = re.compile(
    r'<img\b[^>]*class="lightbox-trigger"[^>]*?src="[^"]*/commu/([0-9][0-9a-z]*)"'
)

def get_tab_bounds(html, prefix, i):
    tab_id = f'{prefix}-{TABS_ORDER[i]}'
    start = html.find(f'data-tab="{tab_id}"')
    if start == -1:
        return -1, -1
    end = len(html)
    for j in range(i + 1, len(TABS_ORDER)):
        nxt = f'{prefix}-{TABS_ORDER[j]}'
        pos = html.find(f'data-tab="{nxt}"', start + 1)
        if pos != -1:
            end = pos
            break
    return start, end

def fix_event(ev_name, config, up_func, upload_map, dry_run=False):
    html_path = os.path.join(REPO, config['html'])
    cdn_base  = config['cdn_base']
    prefix    = config['prefix']
    img_prefix = config['img_prefix']
    title_cards   = config['title_cards']
    serifs_by_tab = config['serifs_by_tab']

    with open(html_path, encoding='utf-8') as f:
        html = f.read()

    if 'UNKNOWN' not in html:
        print(f'  {ev_name}: UNKNOWN なし')
        return

    print(f'\n=== {ev_name} ===')
    total_fixed = 0

    for i, tab_name in enumerate(TABS_ORDER):
        t_start, t_end = get_tab_bounds(html, prefix, i)
        if t_start == -1:
            continue
        tab_html = html[t_start:t_end]

        if 'UNKNOWN' not in tab_html:
            continue

        # ── UNKNOWN行を収集 ──
        unk_rows = []
        for m in UNKNOWN_ROW_PAT.finditer(tab_html):
            old_pid = m.group(1)
            row_html = m.group(0)
            dlg = re.search(r'<div class="line">(.*?)</div>', row_html, re.DOTALL)
            spk = re.search(r'data-who="([^"]+)"', row_html)
            dialogue = dlg.group(1).strip() if dlg else ''
            speaker  = spk.group(1) if spk else ''
            unk_rows.append({
                'old_pid':     old_pid,
                'unique_text': dialogue[:40],
                'speaker':     speaker,
                'tab_pos':     m.start(),
            })

        if not unk_rows:
            continue

        print(f'  [{tab_name}] UNKNOWN: {len(unk_rows)}件')

        # ── 初期ベース（タイトルカードの元フレーム番号）──
        initial_base = title_cards.get(tab_name, ('', 'UNKNOWN', '', 0))[1]

        # ── タブ内の全フレーム（通常 + lightbox-trigger）を位置順に収集 ──
        all_frames = []
        for m in REGULAR_FRAME_PAT.finditer(tab_html):
            nm = re.match(r'([0-9]+)', m.group(1))
            all_frames.append((m.start(), nm.group(1) if nm else m.group(1)))
        for m in LBT_FRAME_PAT.finditer(tab_html):
            nm = re.match(r'([0-9]+)', m.group(1))
            if nm:
                all_frames.append((m.start(), nm.group(1)))
        all_frames.sort()

        # ── 既存の正規pid（衝突回避用）──
        tab_used_pids = set(re.findall(r'commu/([0-9][0-9a-z]*)"', tab_html))

        suffix_counter = {}  # base → count

        corrections = []
        for row in unk_rows:
            # この行の直前にある最後のフレーム番号を探す
            last_base = initial_base
            for fpos, fbase in all_frames:
                if fpos < row['tab_pos']:
                    last_base = fbase
                else:
                    break

            base = last_base if last_base and last_base != 'UNKNOWN' else initial_base

            count = suffix_counter.get(base, 0)
            while True:
                letter    = suffix_letter(count)
                candidate = f'{base}{letter}'
                if candidate not in tab_used_pids:
                    break
                count += 1
            suffix_counter[base] = count + 1
            tab_used_pids.add(candidate)

            corrections.append({
                'old_pid':     row['old_pid'],
                'new_pid':     candidate,
                'unique_text': row['unique_text'],
                'speaker':     row['speaker'],
            })

        # ── 画像ファイルを対応付け（先頭N件がUNKNOW行、残りは既に正規pid）──
        serifs = serifs_by_tab.get(tab_name, [])
        for j, corr in enumerate(corrections):
            corr['image_file'] = f'{img_prefix}_{serifs[j]}.png' if j < len(serifs) else None

        # ── 表示 ──
        for corr in corrections:
            tag = '⚠ no-image' if not corr['image_file'] else ''
            print(f'    {corr["old_pid"]:16s} → {corr["new_pid"]:10s}'
                  f'  [{corr["speaker"][:8]}] {corr["unique_text"][:22]}  {tag}')

        if dry_run:
            continue

        # ── アップロード＋HTML更新 ──
        for corr in corrections:
            if not corr['image_file']:
                continue
            local = os.path.join(IMG_DIR, corr['image_file'])
            if not os.path.exists(local):
                print(f'    ✗ 画像なし: {corr["image_file"]}')
                continue

            # Cloudinary アップロード
            new_full_pid = f'{cdn_base}/{corr["new_pid"]}'
            result = up_func(local, public_id=new_full_pid, overwrite=True)
            upload_map[corr['image_file']] = new_full_pid
            print(f'    ✓ upload → {corr["new_pid"]}')

            # HTML中の該当行を更新（unique_text で特定）
            old_url = f'{CDN}/{cdn_base}/{corr["old_pid"]}'
            new_url = f'{CDN}/{cdn_base}/{corr["new_pid"]}'

            # old_url + unique_text を含む行を1件だけ置換
            escaped_old = re.escape(old_url)
            escaped_txt = re.escape(corr['unique_text'][:20])
            pat = (r'(<div class="ev-dialog-row"><div class="ev-shot">'
                   r'<img\b[^>]*?src=")' + escaped_old +
                   r'("[^>]*></div>(?:(?!</div></div></div></div>).)*?' +
                   escaped_txt +
                   r'(?:(?!</div></div></div></div>).)*?</div></div></div></div>)')
            m = re.search(pat, html, re.DOTALL)
            if m:
                html = html[:m.start()] + m.group(0).replace(old_url, new_url, 1) + html[m.end():]
                print(f'    ✓ HTML: {corr["unique_text"][:22]}')
                total_fixed += 1
            else:
                print(f'    ✗ HTML未更新: {corr["unique_text"][:22]}')

    if not dry_run:
        with open(html_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        print(f'  {ev_name}.html 保存 ({total_fixed}件更新)')

if __name__ == '__main__':
    dry_run = '--dry' in sys.argv

    if not dry_run:
        cloudinary, up = setup_cloudinary()
        up_func = up.upload
        with open(MAP_PATH, encoding='utf-8') as f:
            upload_map = json.load(f)
    else:
        up_func = None
        upload_map = {}
        print('[DRY RUN] アップロードなし\n')

    for ev_name, config in EVENT_CONFIGS.items():
        fix_event(ev_name, config, up_func, upload_map, dry_run=dry_run)

    if not dry_run:
        with open(MAP_PATH, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(upload_map, f, indent=1, ensure_ascii=False)
        print('\nupload_map 保存完了')

    print('\n=== 完了 ===')
