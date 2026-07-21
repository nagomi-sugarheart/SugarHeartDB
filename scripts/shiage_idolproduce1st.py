"""
IdolProduce1st ShiagePage: Cloudinaryアップロード + HTML更新
"""
import json, re, os, ssl, urllib3, sys

# ── Cloudinary SDK セットアップ ──
d = open(r'C:/Users/sawas/.claude.json', encoding='utf-8').read()
os.environ['CLOUDINARY_URL'] = re.search(r'cloudinary://[0-9]+:[^"\']+@dnmzdghoi', d).group(0)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary, cloudinary.uploader as up
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

SRC = r'C:\Users\sawas\OneDrive\Pictures\欠損部分'
EV = 'IdolProduce1st'
BASE_PID = f'Deresute/Event/{EV}/commu_ev'

# ── アップロードマッピング ──
uploads = [
    # (ローカルファイル名, Cloudinary public_id)
    # 予告 serifs
    ('第1回アイプロ_00.02.06.png', f'{BASE_PID}/0003a'),
    ('第1回アイプロ_00.03.10.png', f'{BASE_PID}/0006a'),
    # OP title card
    ('第1回アイプロ_00.03.34.png', f'{BASE_PID}/title_op'),
    # OP serifs
    ('第1回アイプロ_00.03.41.png', f'{BASE_PID}/0008a'),
    ('第1回アイプロ_00.03.47.png', f'{BASE_PID}/0008b'),
    ('第1回アイプロ_00.03.50.png', f'{BASE_PID}/0008c'),
    ('第1回アイプロ_00.05.27.png', f'{BASE_PID}/0019a'),
    ('第1回アイプロ_00.06.00.png', f'{BASE_PID}/0023a'),
    ('第1回アイプロ_00.06.35.png', f'{BASE_PID}/0029a'),
    ('第1回アイプロ_00.06.48.png', f'{BASE_PID}/0031a'),
    ('第1回アイプロ_00.07.04.png', f'{BASE_PID}/0032a'),
    # ED serifs
    ('第1回アイプロ_00.09.07.png', f'{BASE_PID}/0046a'),
    ('第1回アイプロ_00.09.12.png', f'{BASE_PID}/0046b'),
    ('第1回アイプロ_00.09.21.png', f'{BASE_PID}/0046c'),
    ('第1回アイプロ_00.09.28.png', f'{BASE_PID}/0046d'),
    ('第1回アイプロ_00.09.33.png', f'{BASE_PID}/0046e'),
    ('第1回アイプロ_00.09.41.png', f'{BASE_PID}/0046f'),
    ('第1回アイプロ_00.09.50.png', f'{BASE_PID}/0047a'),
    ('第1回アイプロ_00.10.02.png', f'{BASE_PID}/0048a'),
    ('第1回アイプロ_00.10.04.png', f'{BASE_PID}/0048b'),
]

print(f'アップロード開始: {len(uploads)} 件')
results = []
for filename, pid in uploads:
    path = os.path.join(SRC, filename)
    result = up.upload(path, public_id=pid, overwrite=True)
    print(f'  OK: {filename} -> {pid}')
    results.append((filename, pid, result['secure_url']))

# ── _cloudinary_upload_map.json への追記 ──
map_path = r'C:\Users\sawas\Desktop\SugarHeartDB\_cloudinary_upload_map.json'
with open(map_path, encoding='utf-8') as f:
    upload_map = json.load(f)

for filename, pid, url in results:
    key = filename  # ローカルファイル名をキーに
    # public_id のみ保存（既存フォーマットに合わせる）
    local_rel = f'欠損部分/{filename}'
    upload_map[local_rel] = pid

with open(map_path, 'w', encoding='utf-8') as f:
    json.dump(upload_map, f, indent=1, ensure_ascii=False)
print('upload_map 更新完了')

# ── HTML更新 ──
html_path = r'C:\Users\sawas\Desktop\SugarHeartDB\Deresute\Event\IdolProduce1st.html'
with open(html_path, encoding='utf-8') as f:
    html = f.read()

CDN = 'https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto'

def img_tag(pid, alt):
    return f'<img src="{CDN}/{pid}" alt="{alt}" loading="lazy">'

def shot_div(pid, alt):
    return f'<div class="ev-shot">{img_tag(pid, alt)}</div>'

def dialog_row_with_shot(pid, alt, text_inner):
    return f'<div class="ev-dialog-row">{shot_div(pid, alt)}<div class="ev-text">{text_inner}</div></div>'

changes = 0

# 1. OP タイトルカード差し替え: commu_ev/0008 -> commu_ev/title_op
old_title = f'src="{CDN}/{BASE_PID}/0008" alt="ドキドキ☆温泉ロケ！ タイトルカード"'
new_title = f'src="{CDN}/{BASE_PID}/title_op" alt="ドキドキ☆温泉ロケ！ タイトルカード"'
assert html.count(old_title) == 1, f'タイトルカード置換エラー: {html.count(old_title)} 件'
html = html.replace(old_title, new_title, 1)
changes += 1
print('OP タイトルカード差し替え完了')

# 2. data-start 209 -> 213 (OP)
old_start = 'data-start="209">▶ この話からYouTubeで再生</button>'
new_start = 'data-start="213">▶ この話からYouTubeで再生</button>'
assert html.count(old_start) == 1, f'data-start 置換エラー: {html.count(old_start)} 件'
html = html.replace(old_start, new_start, 1)
changes += 1
print('OP data-start 209→213 更新完了')

# 3. no-shot 行に shot を付与
# 各行: (no-shot行のテキスト内容の一部, public_id, alt)
noshot_mappings = [
    # 予告1 line 196: 菜々「……じゃなくって」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="菜々">菜々</span><div class="line">……じゃなくって、取材するのは……山奥？',
        f'{BASE_PID}/0003a', '菜々のセリフ'
    ),
    # 予告2 line 200: 心「『しゅがみん』には」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="心">心</span><div class="line">『しゅがみん』にはちょーっと体を張ったお仕事が多いワケ。',
        f'{BASE_PID}/0006a', '心のセリフ'
    ),
    # OP line 223: ナレーション「こうして」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">こうして、デレ湖のスッティーは',
        f'{BASE_PID}/0008a', 'ナレーション'
    ),
    # OP line 224: ナレーション「スペシャル番組 スタッフ探検」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">スペシャル番組 スタッフ探検シリーズ',
        f'{BASE_PID}/0008b', 'ナレーション'
    ),
    # OP line 225: ナレーション「～完～」 (first OP one)
    # 注意: ED にも同じ「～完～」行がある。OP は dss-lines の中で先に出る
    # OP line 236: 心「プロデューサー！おっはスウィーティー」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="心">心</span><div class="line">プロデューサー！おっはスウィーティー♪今ね、ちょうど次のお仕事の話してたとこ。',
        f'{BASE_PID}/0019a', '心のセリフ'
    ),
    # OP line 240: 菜々「それもまた素敵ですよね！」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="菜々">菜々</span><div class="line">それもまた素敵ですよね！ナナとはぁとちゃんとプロデューサーさんで温泉……えへへ……♪',
        f'{BASE_PID}/0023a', '菜々のセリフ'
    ),
    # OP line 247: 菜々「あ、あうう……腕が……」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="菜々">菜々</span><div class="line">あ、あうう……腕が……ぶるぶる……っ！',
        f'{BASE_PID}/0029a', '菜々のセリフ'
    ),
    # OP line 250: 心「うぅ……ちくしょー……！」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="心">心</span><div class="line">うぅ……ちくしょー……！',
        f'{BASE_PID}/0031a', '心のセリフ'
    ),
    # OP line 252: ナレーション「スペシャル番組 しゅがしゅが☆み～ん探検シリーズ 山奥」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">スペシャル番組 しゅがしゅが☆み～ん探検シリーズ 山奥にある幻の秘境温泉を、探せ！！',
        f'{BASE_PID}/0032a', 'ナレーション'
    ),
    # ED line 993: 菜々「聞いたんです！」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="菜々">菜々</span><div class="line">聞いたんです！ 供物は17歳の娘が望ましい',
        f'{BASE_PID}/0046a', '菜々のセリフ'
    ),
    # ED line 994: 菜々「だからここでナナが……」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="菜々">菜々</span><div class="line">だからここでナナが……ナナが本当のことを言えば……！',
        f'{BASE_PID}/0046b', '菜々のセリフ'
    ),
    # ED line 995: 心「本当のこと！？」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="心">心</span><div class="line">本当のこと！？ んなもん知るか！',
        f'{BASE_PID}/0046c', '心のセリフ'
    ),
    # ED line 996: 心「パイセンが永遠の17歳」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="心">心</span><div class="line">パイセンが永遠の17歳であろうとなかろうと、みんなで脱出するんだよ！',
        f'{BASE_PID}/0046d', '心のセリフ'
    ),
    # ED line 997: 菜々「はぁとちゃん……！ あっ、上！」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="菜々">菜々</span><div class="line">はぁとちゃん……！ あっ、上！ 上を見てください！',
        f'{BASE_PID}/0046e', '菜々のセリフ'
    ),
    # ED line 998: 心「いねぇと思ったら」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="心">心</span><div class="line">いねぇと思ったら、助け呼んできてくれたとかマジかよ、プロデューサー……！',
        f'{BASE_PID}/0046f', '心のセリフ'
    ),
    # ED line 1000: 菜々「はいっ！ しゅがしゅが～？」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="菜々">菜々</span><div class="line">はいっ！ しゅがしゅが～？',
        f'{BASE_PID}/0047a', '菜々のセリフ'
    ),
    # ED line 1002: ナレーション「謎の村に閉じ込められた」
    (
        'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">スペシャル番組 しゅがしゅが☆み～ん探検シリーズ 謎の村に閉じ込められたふたり',
        f'{BASE_PID}/0048a', 'ナレーション'
    ),
]

# OP の「～完～」を先に処理（OP行は ED行より先に出現）
# OP line 225: OP側の「～完～」 は 「スタッフ探検シリーズ」行の直後に出現
# ED line 1003: ED側の「～完～」 は 「謎の村」行の直後に出現

# 「～完～」は2か所ある。OP の方を先に置換、次に ED の方を置換
# pattern: OP 完 = 山奥行（0032a）の後
# ED 完 = 謎の村行（0048a）の後
# → ここでは両方 split 戦略で処理

# まず OP 完を置換（最初の出現）
op_kan_old = 'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">～完～</div>'
op_kan_shot = f'{shot_div(f"{BASE_PID}/0008c", "ナレーション")}'
op_kan_new = f'class="ev-dialog-row">{op_kan_shot}<div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">～完～</div>'

count_kan = html.count(op_kan_old)
assert count_kan == 2, f'「～完～」行が {count_kan} 件 (2 件期待)'
# 最初の出現を置換 (OP)
idx = html.index(op_kan_old)
html = html[:idx] + op_kan_new + html[idx + len(op_kan_old):]
changes += 1
print('OP 完 (0008c) 配備完了')

# ED 完を置換（2番目の出現）
ed_kan_shot = f'{shot_div(f"{BASE_PID}/0048b", "ナレーション")}'
ed_kan_new = f'class="ev-dialog-row">{ed_kan_shot}<div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="ナレーション">ナレーション</span><div class="line">～完～</div>'

count_kan2 = html.count(op_kan_old)
assert count_kan2 == 1, f'残り「～完～」行が {count_kan2} 件 (1 件期待)'
idx2 = html.index(op_kan_old)
html = html[:idx2] + ed_kan_new + html[idx2 + len(op_kan_old):]
changes += 1
print('ED 完 (0048b) 配備完了')

# 残りのマッピングを処理
for snippet, pid, alt in noshot_mappings:
    old = f'{snippet}'
    # 古い行全体を見つけて置換
    # 古い行パターン: class="ev-dialog-row no-shot"><div class="ev-text">...
    # 新しい行パターン: class="ev-dialog-row"><div class="ev-shot">...</div><div class="ev-text">...
    old_full = f'class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue">'
    # より具体的なsnippetで検索
    old_str = f'<div class="ev-dialog-row no-shot"><div class="ev-text"><div class="ud-dialogue"><span class="speaker" data-who="{alt.replace("のセリフ", "")}"'
    # snippetを使って検索
    if snippet not in html:
        print(f'  WARNING: snippet not found: {snippet[:60]}...')
        continue
    count = html.count(snippet)
    if count != 1:
        print(f'  WARNING: snippet count={count} (1 expected): {snippet[:60]}...')
        continue
    # 古い行の先頭「<div class="ev-dialog-row no-shot">」を見つける
    idx = html.index(snippet)
    # この snippet の直前に「<div」がある
    # 「<div class="ev-dialog-row no-shot">」の開始位置を探す
    start = html.rfind('<div class="ev-dialog-row no-shot">', 0, idx)
    assert start != -1, f'行開始が見つからない: {snippet[:40]}'
    # 行全体の終端「</div></div></div></div>」を探す
    end = html.find('</div></div></div></div>', idx)
    assert end != -1, f'行終端が見つからない: {snippet[:40]}'
    end += len('</div></div></div></div>')
    old_row = html[start:end]
    # 新しい行を構築
    # old_row = <div class="ev-dialog-row no-shot"><div class="ev-text">{inner}</div></div>
    # new_row = <div class="ev-dialog-row"><div class="ev-shot"><img ...></div><div class="ev-text">{inner}</div></div>
    assert 'class="ev-dialog-row no-shot">' in old_row, f'no-shot not in row: {old_row[:80]}'
    text_content = old_row[old_row.index('<div class="ev-text">'):]
    new_row = f'<div class="ev-dialog-row"><div class="ev-shot"><img src="{CDN}/{pid}" alt="{alt}" loading="lazy"></div>{text_content}'
    html = html[:start] + new_row + html[end:]
    changes += 1
    print(f'  配備: {os.path.basename(pid)} -> {snippet[:50]}...')

print(f'\n合計 {changes} 件の変更')

# ファイル書き出し
with open(html_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)
print('IdolProduce1st.html 書き出し完了')

# ── 残り no-shot 数の確認 ──
remaining = html.count('class="ev-dialog-row no-shot"')
print(f'残り no-shot 行数: {remaining} (Twitter告知の no-frame 行を除く実撮り漏れ)')
noframe = html.count('class="ev-dialog-row no-shot no-frame"')
print(f'  うち no-frame (Twitter告知等): {noframe}')
print(f'  実撮り漏れ: {remaining - noframe}')
