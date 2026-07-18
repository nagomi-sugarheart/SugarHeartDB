# -*- coding: utf-8 -*-
"""
2枚目ジャケット・Next Chapterジャケットのアップロードと全JSONデータ更新
"""
import json, re, os, ssl, urllib3
from pathlib import Path

# --- Cloudinary 認証 ---
d = open(r'C:/Users/sawas/.claude.json', encoding='utf-8').read()
os.environ['CLOUDINARY_URL'] = re.search(r'cloudinary://[0-9]+:[^"\']+@dnmzdghoi', d).group(0)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary
import cloudinary.uploader as up
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

BASE = Path(__file__).parent.parent
DD = BASE / 'scripts' / 'songlist_data'

# ========== Step 1: 2枚目ジャケット + Next Chapterジャケットをアップロード ==========
JACKET2_UPLOADS = [
    # Next Chapterメインジャケット
    ('nextchapter',          'https://cdn.gamerch.com/contents/wiki/3825/entry/hcq301UE.png'),
    # 2枚目ジャケット（各曲CDジャケット）
    ('inochi_jacket2',       'https://cdn.gamerch.com/contents/wiki/3825/entry/1500536752.jpg'),
    ('happynewyeah_jacket2', 'https://cdn.gamerch.com/contents/wiki/3825/entry/jq9mrs8h.jpg'),
    ('coconatsu_jacket2',    'https://cdn.gamerch.com/contents/wiki/3825/entry/GqoLnXlY.jpg'),
    ('dekoboko_jacket2',     'https://cdn.gamerch.com/contents/wiki/3825/entry/jueasmgh.jpg'),
    ('flagship_jacket2',     'https://cdn.gamerch.com/contents/wiki/3825/entry/kmcbtg15.jpg'),
    ('gojustgo_jacket2',     'https://cdn.gamerch.com/contents/wiki/3825/entry/ker7zxg9.jpg'),
    ('dancingdead_jacket2',  'https://cdn.gamerch.com/contents/wiki/3825/entry/D0YFjL8A.jpg'),
    ('sekaiwa_jacket2',      'https://cdn.gamerch.com/contents/wiki/3825/entry/ynvuclHu.jpg'),
    ('nextchapter_jacket2',  'https://cdn.gamerch.com/contents/wiki/3825/entry/Kmch60MJ.jpg'),
    # 認めてくれなくたっていいよ → 熱情エナモラルのジャケット(mitomete_jacket2)を
    # Cloudinaryにupload（enamorarのURLから再アップ）
    ('mitomete_jacket2',     'https://cdn.gamerch.com/contents/wiki/3825/entry/JfHHPBS6.jpg'),
]

MAP_PATH = BASE / '_cloudinary_upload_map.json'
upload_map = json.load(open(MAP_PATH, encoding='utf-8'))

uploaded = {}
for slug, src_url in JACKET2_UPLOADS:
    pid = f'Deresute/SongList/jacket/{slug}'
    print(f'Uploading {slug} ...', flush=True)
    try:
        r = up.upload(src_url, public_id=pid, overwrite=True, resource_type='image')
        uploaded[pid] = r['secure_url']
        upload_map[pid] = r['secure_url']
        print(f'  OK')
    except Exception as e:
        print(f'  ERROR: {e}')

json.dump(upload_map, open(MAP_PATH, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print(f'Uploaded {len(uploaded)}/{len(JACKET2_UPLOADS)} jackets.\n')

# ========== Step 2: gamerch_data.json に Next Chapter を追加 ==========
gj = json.load(open(DD / 'gamerch_data.json', encoding='utf-8'))
if 'Next Chapter' not in gj:
    gj['Next Chapter'] = {
        "type": "全タイプ",
        "time": "2:06",
        "bpm": "108",
        "release": "2023/06/29",
        "levels": {
            "DEBUT": "6",
            "REGULAR": "12",
            "PRO": "16",
            "MASTER": "24",
            "MASTER+": "28"
        },
        "jacket": "https://cdn.gamerch.com/contents/wiki/3825/entry/hcq301UE.png"
    }
    json.dump(gj, open(DD / 'gamerch_data.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('gamerch_data.json: Next Chapter 追加')
else:
    print('gamerch_data.json: Next Chapter already exists')

# ========== Step 3: gamerch_jackets.json に Next Chapter を追加 ==========
jk = json.load(open(DD / 'gamerch_jackets.json', encoding='utf-8'))
if 'Next Chapter' not in jk:
    jk['Next Chapter'] = 'https://cdn.gamerch.com/contents/wiki/3825/entry/hcq301UE.png'
    json.dump(jk, open(DD / 'gamerch_jackets.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('gamerch_jackets.json: Next Chapter 追加')

# ========== Step 4: lives_data.json に Next Chapter を追加 ==========
lives = json.load(open(DD / 'lives_data.json', encoding='utf-8'))
if 'Next Chapter' not in lives:
    lives['Next Chapter'] = [
        {
            "date": "2023-09-10",
            "tag": "",
            "event": "THE IDOLM@STER CINDERELLA GIRLS Shout out Live!!! DAY2",
            "venue": "愛知・愛知県国際展示場 ホールA",
            "performers": "森下来奈、市ノ瀬加那、藍原ことみ"
        },
        {
            "date": "2025-09-06",
            "tag": "",
            "event": "THE IDOLM@STER CINDERELLA GIRLS 10th MEMORIAL LIVE STARLIGHT STAGE DAY1",
            "venue": "神奈川・Kアリーナ横浜",
            "performers": "森下来奈、東山奈央、原田彩楓 ／ Next Chapter (Medley Size)"
        },
        {
            "date": "2025-11-30",
            "tag": "xR",
            "event": "CINDERELLA GIRLS fes. Once Upon a St@rs DAY2 第4公演 Ever Starlight",
            "venue": "千葉・幕張メッセ 国際展示場ホール9-10",
            "performers": "佐藤心、鷺沢文香"
        }
    ]
    json.dump(lives, open(DD / 'lives_data.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('lives_data.json: Next Chapter 追加')

# ========== Step 5: song_data.json に Next Chapter を追加 ==========
sd = json.load(open(DD / 'song_data.json', encoding='utf-8'))
if 'Next Chapter' not in sd:
    sd['Next Chapter'] = {
        "head": "(選挙SfC)GroupB BEST5",
        "credits": {
            "作詞": "大森祥子",
            "作曲": "設楽哲也",
            "編曲": "設楽哲也",
            "GAME初出": "スターライトステージ(2023/06/29)",
            "CD初出": "THE IDOLM@STER CINDERELLA MASTER Dreamy Anniversary & Next Chapter（2023/10/25）"
        },
        "lives": [],
        "media": [
            "THE IDOLM@STER CINDERELLA MASTER Dreamy Anniversary & Next Chapter／2023/10/25"
        ],
        "fulltext": ""
    }
    json.dump(sd, open(DD / 'song_data.json', 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('song_data.json: Next Chapter 追加')

print('\n=== All done ===')
