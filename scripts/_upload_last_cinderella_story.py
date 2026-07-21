"""
ラストシンデレラストーリー 第3話
- Cloudinaryへ画像アップロード
- HTMLの ev-dialog-row 行を生成して out_html に保存
"""
import csv, html as H, json, os, re, ssl, time, urllib3

d = open(r'C:/Users/sawas/.claude.json', encoding='utf-8').read()
os.environ['CLOUDINARY_URL'] = re.search(r'cloudinary://[0-9]+:[^"\']+@dnmzdghoi', d).group(0)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary
import cloudinary.uploader as up
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

SRC_DIR   = r'C:\Users\sawas\Downloads\comm_frames\RPReplay_Final1680150053_202607212229'
CLD_FOLDER = 'Mobamas/LastCinderellaStory'
CLD_BASE   = 'https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto'
OUT_HTML   = r'C:\Users\sawas\Desktop\SugarHeartDB\scripts\_last_cinderella_story_rows.html'

csv_path = os.path.join(SRC_DIR, 'dialogues.csv')
with open(csv_path, encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

print(f"=== アップロード開始 ({len(rows)}枚) ===")
results, errors = {}, []

for row in rows:
    no         = row['no'].zfill(4)
    frame_file = row['frame_file']
    src_path   = os.path.join(SRC_DIR, frame_file)
    public_id  = f'{CLD_FOLDER}/{no}'

    if not os.path.exists(src_path):
        print(f"  SKIP (not found): {frame_file}")
        errors.append(f"NOT FOUND: {frame_file}")
        continue

    print(f"  {no} {frame_file} ...", end=' ', flush=True)
    try:
        r = up.upload(src_path, public_id=public_id, overwrite=True)
        results[public_id] = r['secure_url']
        print("OK")
    except Exception as e:
        print(f"ERROR: {e}")
        errors.append(f"ERROR: {no} -> {e}")
    time.sleep(0.3)

print(f"\nアップロード完了: {len(results)} / {len(rows)}")
if errors:
    print(f"エラー ({len(errors)}):")
    for e in errors:
        print(f"  {e}")

# HTML行生成
lines = []
for row in rows:
    no          = row['no'].zfill(4)
    speaker     = row['speaker']
    dialogue    = row['dialogue']
    center_text = row['center_text']
    img_url     = f'{CLD_BASE}/{CLD_FOLDER}/{no}'

    if center_text:
        alt        = H.escape(center_text)
        text_block = f'<div class="dss-stage-text">{H.escape(center_text)}</div>'
    else:
        alt        = H.escape(f'{speaker}のセリフ')
        text_block = (
            f'<div class="ud-dialogue">'
            f'<span class="speaker" data-who="{H.escape(speaker)}">{H.escape(speaker)}</span>'
            f'<div class="line">{H.escape(dialogue)}</div>'
            f'</div>'
        )

    lines.append(
        f'                <div class="ev-dialog-row">'
        f'<div class="ev-shot"><img src="{img_url}" alt="{alt}" loading="lazy"></div>'
        f'<div class="ev-text">{text_block}</div>'
        f'</div>'
    )

html_rows = '\n'.join(lines)
with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html_rows)
print(f"\nHTML行生成: {len(lines)}行 → {OUT_HTML}")
