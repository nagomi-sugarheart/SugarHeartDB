"""
季節イベント画像アップロード
- 誕生日 2021(シーン4) / 2022(シーン1-3)
- バレンタイン 2022(シーン1-2)
- ホワイトデー 2022(シーン1-3)
- Anniversary 7th-11th アイドルプロデュース
"""
import os, re, ssl, time, urllib3

d = open(r'C:/Users/sawas/.claude.json', encoding='utf-8').read()
os.environ['CLOUDINARY_URL'] = re.search(r'cloudinary://[0-9]+:[^"\']+@dnmzdghoi', d).group(0)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary
import cloudinary.uploader as up
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

uploads = [
    # 誕生日
    (r'G:\マイドライブ\季節イベント\2021誕生日\IMG_8258.PNG',         'Mobamas/SeasonalEvents/Birthday/2021_4'),
    (r'G:\マイドライブ\季節イベント\2022誕生日\IMG_4849.jpg',         'Mobamas/SeasonalEvents/Birthday/2022_1'),
    (r'G:\マイドライブ\季節イベント\2022誕生日\IMG_4850.jpg',         'Mobamas/SeasonalEvents/Birthday/2022_2'),
    (r'G:\マイドライブ\季節イベント\2022誕生日\IMG_4851.jpg',         'Mobamas/SeasonalEvents/Birthday/2022_3'),
    # バレンタイン
    (r'C:\Users\sawas\OneDrive\Pictures\画像\2022バレンタイン1.png',   'Mobamas/SeasonalEvents/Valentine/2022_1'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\2022バレンタイン2.png',   'Mobamas/SeasonalEvents/Valentine/2022_2'),
    # ホワイトデー
    (r'C:\Users\sawas\OneDrive\Pictures\画像\2022ホワイトデー1.png',   'Mobamas/SeasonalEvents/WhiteDay/2022_1'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\2022ホワイトデー2.png',   'Mobamas/SeasonalEvents/WhiteDay/2022_2'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\2022ホワイトデー3.png',   'Mobamas/SeasonalEvents/WhiteDay/2022_3'),
    # Anniversary アイドルプロデュース
    (r'C:\Users\sawas\OneDrive\Pictures\画像\7thアイプロ_エンカ.png',      'Mobamas/SeasonalEvents/Anniversary/7th_enka'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\7thアイプロ_ノーマル.png',    'Mobamas/SeasonalEvents/Anniversary/7th_normal'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\7thアイプロ_グッド.png',      'Mobamas/SeasonalEvents/Anniversary/7th_good'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\7thアイプロ_パーフェクト.png','Mobamas/SeasonalEvents/Anniversary/7th_perfect'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\8thアイプロ.png',             'Mobamas/SeasonalEvents/Anniversary/8th'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\9thアイプロ.png',             'Mobamas/SeasonalEvents/Anniversary/9th'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\10thアイプロ.png',            'Mobamas/SeasonalEvents/Anniversary/10th'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\11thアイプロ_1.png',          'Mobamas/SeasonalEvents/Anniversary/11th_1'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\11thアイプロ_2.png',          'Mobamas/SeasonalEvents/Anniversary/11th_2'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\11thアイプロ_3.png',          'Mobamas/SeasonalEvents/Anniversary/11th_3'),
    (r'C:\Users\sawas\OneDrive\Pictures\画像\11thアイプロ_4.png',          'Mobamas/SeasonalEvents/Anniversary/11th_4'),
]

print(f"=== アップロード開始 ({len(uploads)}件) ===")
errors = []
for src, pid in uploads:
    name = os.path.basename(src)
    print(f"  {name} ...", end=' ', flush=True)
    if not os.path.exists(src):
        print("SKIP (not found)")
        errors.append(f"NOT FOUND: {src}")
        continue
    try:
        up.upload(src, public_id=pid, overwrite=True)
        print("OK")
    except Exception as e:
        print(f"ERROR: {e}")
        errors.append(f"ERROR: {name} -> {e}")
    time.sleep(0.3)

print(f"\n完了!")
if errors:
    print(f"エラー ({len(errors)}):")
    for e in errors: print(f"  {e}")
