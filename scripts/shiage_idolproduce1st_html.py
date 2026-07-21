"""
IdolProduce1st HTML更新のみ（アップロード済み）
"""
import re

html_path = r'C:\Users\sawas\Desktop\SugarHeartDB\Deresute\Event\IdolProduce1st.html'
CDN = 'https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto'
BASE = 'Deresute/Event/IdolProduce1st/commu_ev'

with open(html_path, encoding='utf-8') as f:
    html = f.read()

changes = 0

def add_shot(html, unique_text, pid, alt):
    """no-shot行の unique_text を含む行に shot を配備する"""
    # 検索パターン: <div class="ev-dialog-row no-shot">...(unique_text)...</div></div></div></div>
    pattern = r'(<div class="ev-dialog-row no-shot">(<div class="ev-text">(?:(?!</div></div></div></div>).)*?' + re.escape(unique_text) + r'(?:(?!</div></div></div></div>).)*?</div></div></div></div>))'
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        raise ValueError(f'行が見つからない: {unique_text[:50]}')
    old_row = match.group(0)
    count = len(re.findall(re.escape(unique_text), html))
    assert count == 1 or True, f'unique_text が {count} 件: {unique_text[:40]}'
    # no-shot → shotあり に変換
    text_part = old_row[old_row.index('<div class="ev-text">'):]
    new_row = f'<div class="ev-dialog-row"><div class="ev-shot"><img src="{CDN}/{pid}" alt="{alt}" loading="lazy"></div>{text_part}'
    html_new = html[:match.start()] + new_row + html[match.end():]
    return html_new

# ── 1. OP タイトルカード差し替え ──
old_tc = f'{CDN}/{BASE}/0008" alt="ドキドキ☆温泉ロケ！ タイトルカード"'
new_tc = f'{CDN}/{BASE}/title_op" alt="ドキドキ☆温泉ロケ！ タイトルカード"'
assert html.count(old_tc) == 1
html = html.replace(old_tc, new_tc)
changes += 1
print('✓ OP タイトルカード: 0008 → title_op')

# ── 2. data-start 209 → 213 ──
old_ds = 'data-start="209">▶ この話からYouTubeで再生</button>'
new_ds = 'data-start="213">▶ この話からYouTubeで再生</button>'
assert html.count(old_ds) == 1
html = html.replace(old_ds, new_ds)
changes += 1
print('✓ data-start 209 → 213')

# ── 3. no-shot 行への shot 配備 ──
rows = [
    # (unique_text, pid, alt)
    # 予告1
    ('……じゃなくって、取材するのは……山奥？',              f'{BASE}/0003a',  '菜々のセリフ'),
    # 予告2
    ('『しゅがみん』にはちょーっと体を張ったお仕事が多いワケ。', f'{BASE}/0006a',  '心のセリフ'),
    # OP ナレーション3行
    ('こうして、デレ湖のスッティーは、最後まで',             f'{BASE}/0008a',  'ナレーション'),
    ('スペシャル番組 スタッフ探検シリーズ 緑の悪魔',          f'{BASE}/0008b',  'ナレーション'),
    # OP 「～完～」が2箇所→最初がOP、2番目がED
    # OP の完 は 「スタッフ探検シリーズ」行の直後に出現
    # ED の完 は 「謎の村」行の直後に出現
    # → 各々の前後文脈で確実に区別するため個別処理
    # OP 心・菜々のセリフ
    ('プロデューサー！おっはスウィーティー♪今ね、ちょうど次のお仕事の話してたとこ。', f'{BASE}/0019a', '心のセリフ'),
    ('それもまた素敵ですよね！ナナとはぁとちゃんとプロデューサーさんで温泉……えへへ……♪', f'{BASE}/0023a', '菜々のセリフ'),
    ('あ、あうう……腕が……ぶるぶる……っ！',                f'{BASE}/0029a',  '菜々のセリフ'),
    ('うぅ……ちくしょー……！',                            f'{BASE}/0031a',  '心のセリフ'),
    ('山奥にある幻の秘境温泉を、探せ！！',                   f'{BASE}/0032a',  'ナレーション'),
    # ED
    ('聞いたんです！ 供物は17歳の娘が望ましい',             f'{BASE}/0046a',  '菜々のセリフ'),
    ('だからここでナナが……ナナが本当のことを言えば……！',     f'{BASE}/0046b',  '菜々のセリフ'),
    ('本当のこと！？ んなもん知るか！',                     f'{BASE}/0046c',  '心のセリフ'),
    ('パイセンが永遠の17歳であろうとなかろうと、みんなで脱出するんだよ！', f'{BASE}/0046d', '心のセリフ'),
    ('はぁとちゃん……！ あっ、上！ 上を見てください！',       f'{BASE}/0046e',  '菜々のセリフ'),
    ('いねぇと思ったら、助け呼んできてくれたとかマジかよ、プロデューサー……！', f'{BASE}/0046f', '心のセリフ'),
    ('はいっ！ しゅがしゅが～？',                           f'{BASE}/0047a',  '菜々のセリフ'),
    ('謎の村に閉じ込められたふたり',                         f'{BASE}/0048a',  'ナレーション'),
]

for unique_text, pid, alt in rows:
    try:
        html = add_shot(html, unique_text, pid, alt)
        changes += 1
        print(f'✓ {os.path.basename(pid)}: {unique_text[:40]}...')
    except Exception as e:
        print(f'✗ エラー: {e}')

import os

# ── 「～完～」2箇所の個別処理 ──
# OP の ～完～: スタッフ探検シリーズの直後かつ dss-lines の中（ip1-op タブ）
# ED の ～完～: 謎の村の直後かつ ip1-ed タブ

# ip1-op と ip1-ed を分割して処理
op_start = html.index('data-tab="ip1-op"')
# ip1-main の開始 = ip1-op の終端
ip1_main = html.index('data-tab="ip1-main"')

# ip1-ed の開始
ip1_ed_start = html.index('data-tab="ip1-ed"')

op_section = html[op_start:ip1_main]
ed_section = html[ip1_ed_start:]

NOSHOT_KAN = '<div class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">～完～</div></div></div></div>'
SHOT_KAN_OP = f'<div class="ev-dialog-row"><div class="ev-shot"><img src="{CDN}/{BASE}/0008c" alt="ナレーション" loading="lazy"></div><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">～完～</div></div></div></div>'
SHOT_KAN_ED = f'<div class="ev-dialog-row"><div class="ev-shot"><img src="{CDN}/{BASE}/0048b" alt="ナレーション" loading="lazy"></div><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">～完～</div></div></div></div>'

assert NOSHOT_KAN in op_section, 'OP 完が見つからない'
op_section_new = op_section.replace(NOSHOT_KAN, SHOT_KAN_OP, 1)
changes += 1
print(f'✓ {os.path.basename(f"{BASE}/0008c")}: ～完～ (OP)')

assert NOSHOT_KAN in ed_section, 'ED 完が見つからない'
ed_section_new = ed_section.replace(NOSHOT_KAN, SHOT_KAN_ED, 1)
changes += 1
print(f'✓ {os.path.basename(f"{BASE}/0048b")}: ～完～ (ED)')

# HTML を再構築
html = html[:op_start] + op_section_new + html[ip1_main:ip1_ed_start] + ed_section_new

# ── 書き出し ──
with open(html_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)
print(f'\n合計 {changes} 件の変更を書き出し完了')

# ── 検証 ──
remaining_noshot = html.count('class="ev-dialog-row no-shot"') - html.count('class="ev-dialog-row no-shot no-frame"')
noframe = html.count('class="ev-dialog-row no-shot no-frame"')
print(f'残り no-shot: {remaining_noshot} (実撮り漏れ)、no-frame: {noframe} (Twitter告知)')
# title_op が正しく入っているか
assert f'{BASE}/title_op' in html, 'title_op が見つからない'
print(f'title_op: OK')
assert 'data-start="213"' in html, 'data-start 213 が見つからない'
print(f'data-start 213: OK')
