# -*- coding: utf-8 -*-
"""
SongList追加ジャケット画像のCloudinaryアップロード
- ソロリミックスCDジャケット7枚（ローカル）
- メインジャケット3枚（ダンスダンスダンス / もしもカワイイ / シンデレラNo.1）
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

BASE_DIR = Path(r'C:\Users\sawas\Desktop\SugarHeartDB')
JK_DIR = Path(r'C:\Users\sawas\OneDrive\Pictures\ジャケット')

# (ローカルファイル名, Cloudinary public_id)
UPLOADS = [
    # メインジャケット（下4曲のうち画像あり3曲）
    ('ダンスダンスダンス.jpg',          'Deresute/SongList/jacket/dance_dance_dance'),
    ('もしも「カワイイ」が世界からなくなっても.jpg', 'Deresute/SongList/jacket/moshimo_kawaii'),
    ('シンデレラNo.1.jpg',             'Deresute/SongList/jacket/cinderella_no1'),
    # ソロリミックスCDジャケット
    ('「THE IDOLM@STER CINDERELLA GIRLS SS3A Live Sound Booth♪」会場オリジナルCD.jpg',
     'Deresute/SongList/jacket/inochi_solo_remix'),
    ('THE IDOLM@STER CINDERELLA GIRLS 10th ANNIVERSARY M@GICAL WONDERLAND TOUR!!! Celebration Land オリジナルCD.jpg',
     'Deresute/SongList/jacket/takeme_solo_remix'),
    ('「THE IDOLM@STER CINDERELLA GIRLS 7thLIVE TOUR Special 3chord♪ Glowing Rock!」会場オリジナルCD.jpg',
     'Deresute/SongList/jacket/happynewyeah_solo_remix'),
    ('THE IDOLM@STER CINDERELLA GIRLS 6thLIVE MERRY-GO-ROUNDOME!!! オリジナルCD MASTER SEASONS SUMMER!　SOLO REMIX.jpg',
     'Deresute/SongList/jacket/coco_solo_remix'),
    ('THE IDOLM@STER CINDERELLA GIRLS　Live Broadcast 24magic ～シンデレラたちの24時間生放送！～　オリジナルCD.jpg',
     'Deresute/SongList/jacket/dekoboko_solo_remix'),
    ("THE IDOLM@STER CINDERELLA GIRLS STARLIGHT STAGE 10th ANNIVERSARY TOUR Let's AMUSEMENT!!!OKINAWA.jpg",
     'Deresute/SongList/jacket/odoru_solo_remix'),
    ("THE IDOLM@STER CINDERELLA GIRLS STARLIGHT STAGE 10th ANNIVERSARY TOUR Let's AMUSEMENT!!!TOKYO.jpg",
     'Deresute/SongList/jacket/nextchapter_solo_remix'),
]

# アップロードマップ読み込み
MAP_PATH = BASE_DIR / '_cloudinary_upload_map.json'
upload_map = json.load(open(MAP_PATH, encoding='utf-8'))

results = {}
for fname, public_id in UPLOADS:
    fpath = JK_DIR / fname
    if not fpath.exists():
        print(f'[SKIP] ファイルなし: {fpath}')
        continue
    print(f'Uploading {fname} -> {public_id} ...', flush=True)
    try:
        r = up.upload(str(fpath), public_id=public_id, overwrite=True, resource_type='image')
        url = r['secure_url']
        results[public_id] = url
        upload_map[public_id] = url
        print(f'  OK: {url}')
    except Exception as e:
        print(f'  ERROR: {e}')

# マップ更新
json.dump(upload_map, open(MAP_PATH, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
print(f'\nDone. {len(results)}/{len(UPLOADS)} uploaded.')
print(json.dumps(results, ensure_ascii=False, indent=2))
