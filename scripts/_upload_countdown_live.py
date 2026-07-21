"""
オールスターカウントダウンLIVE 2021/2022/2024
- Cloudinaryへ画像アップロード（スクショ40枚＋ログ2枚＋2024ランキング2枚）
"""
import csv, os, re, ssl, time, urllib3

d = open(r'C:/Users/sawas/.claude.json', encoding='utf-8').read()
os.environ['CLOUDINARY_URL'] = re.search(r'cloudinary://[0-9]+:[^"\']+@dnmzdghoi', d).group(0)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary
import cloudinary.uploader as up
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

CLD_FOLDER = 'Deresute/Other/CountdownLive'
SRC_DIR    = r'C:\Users\sawas\Downloads\comm_frames\オールスターカウントダウンLIVE_202607212156'

# 1. スクリーンショット 40枚
csv_path = os.path.join(SRC_DIR, 'dialogues.csv')
with open(csv_path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

print(f"=== スクリーンショット アップロード ({len(rows)}枚) ===")
errors = []
for row in rows:
    no        = row['no'].zfill(4)
    frame_file = row['frame_file']
    src_path  = os.path.join(SRC_DIR, frame_file)
    public_id = f'{CLD_FOLDER}/{no}'

    if not os.path.exists(src_path):
        print(f"  SKIP (not found): {frame_file}")
        errors.append(f"NOT FOUND: {frame_file}")
        continue

    print(f"  {no} {frame_file} ...", end=' ', flush=True)
    try:
        r = up.upload(src_path, public_id=public_id, overwrite=True)
        print("OK")
    except Exception as e:
        print(f"ERROR: {e}")
        errors.append(f"ERROR: {no} -> {e}")
    time.sleep(0.3)

# 2. ログ画像・ランキング画像
extra = [
    (r'G:\マイドライブ\コミュ\オールスターカウントダウンLIVE2021_Tr1_log.png',  f'{CLD_FOLDER}/log/2021_Tr1'),
    (r'G:\マイドライブ\コミュ\オールスターカウントダウンLIVE 2022_OP_log.png',   f'{CLD_FOLDER}/log/2022_OP'),
    (r'G:\マイドライブ\コミュ\Sレアスカウト.PNG',                               f'{CLD_FOLDER}/2024_srare'),
    (r'G:\マイドライブ\コミュ\fesスカウト.PNG',                                 f'{CLD_FOLDER}/2024_fes'),
]

print(f"\n=== 追加画像アップロード ===")
for src, pid in extra:
    name = os.path.basename(src)
    print(f"  {name} ...", end=' ', flush=True)
    try:
        r = up.upload(src, public_id=pid, overwrite=True)
        print("OK")
    except Exception as e:
        print(f"ERROR: {e}")
        errors.append(f"ERROR: {name} -> {e}")
    time.sleep(0.3)

print(f"\n完了!")
if errors:
    print(f"エラー ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
