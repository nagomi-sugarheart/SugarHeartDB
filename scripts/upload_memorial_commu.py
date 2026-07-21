# -*- coding: utf-8 -*-
"""メモリアルコミュのフレーム＆ログをCloudinaryへアップロード。

- 使用フレームのみ: Deresute/Memorial/commu/{NNNN}
- ログ画像(6本):   Deresute/Memorial/log/{code}   (5_B -> 5B)
"""
import json, re, os, ssl, sys, glob
from pathlib import Path
import urllib3

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
FRAMES_DIR = Path(r"C:\Users\sawas\Downloads\comm_frames\エピソードコミュ_202607172141")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
MERGED = REPO / "scripts" / "merged_memorial_commu.json"
BASE = "Deresute/Memorial"

# 認証
d = open(os.path.expanduser(r"C:/Users/sawas/.claude.json"), encoding="utf-8").read()
os.environ["CLOUDINARY_URL"] = re.search(r"cloudinary://[0-9]+:[^\"']+@dnmzdghoi", d).group(0)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary, cloudinary.uploader as up
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

data = json.loads(MERGED.read_text(encoding="utf-8"))

# 使用フレーム番号を収集
used = set()
for sec in data:
    if sec.get("title_frame"):
        used.add(sec["title_frame"])
    for e in sec["entries"]:
        if e.get("frame"):
            used.add(e["frame"])

# 番号 -> ファイルパス
num2file = {}
for f in glob.glob(str(FRAMES_DIR / "*.jpg")):
    m = re.match(r"(\d+)", Path(f).name)
    if m:
        num2file[m.group(1)] = f

ok = fail = 0
missing = []
for num in sorted(used):
    fp = num2file.get(num)
    if not fp:
        missing.append(num); continue
    try:
        up.upload(fp, public_id=f"{BASE}/commu/{num}", overwrite=True)
        ok += 1
    except Exception as ex:
        fail += 1
        print(f"FRAME NG {num}: {ex}")
print(f"frames: ok={ok} fail={fail} missing={missing}")

# ログ画像
from PIL import Image
import io as _io
logok = 0
for code in ["1", "2", "3", "4", "5", "5_B"]:
    png = JSON_DIR / f"メモリアルコミュ_{code}_log.png"
    pid = f"{BASE}/log/{code.replace('_','')}"
    if not png.exists():
        print(f"LOG missing {png}"); continue
    try:
        if png.stat().st_size > 10 * 1024 * 1024:
            im = Image.open(png).convert("RGB")
            buf = _io.BytesIO(); im.save(buf, "JPEG", quality=88); buf.seek(0)
            up.upload(buf, public_id=pid, overwrite=True)
        else:
            up.upload(str(png), public_id=pid, overwrite=True)
        logok += 1
    except Exception as ex:
        print(f"LOG NG {code}: {ex}")
print(f"logs: ok={logok}")
print("DONE")
