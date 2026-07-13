# -*- coding: utf-8 -*-
"""シンデレラヒストリー「永遠に輝きを放つ乙女たち☆」コミュ画像のCloudinaryアップロード

merged_cindehist_eien_commu.json の使用フレームを
Mobamas/CinderellaHistory/EienNiKagayaki/{NNNN} へアップロードする。
完了後 _cloudinary_upload_map.json に追記。環境変数 CLOUDINARY_URL が必要。
"""
import json
import os
import ssl
import sys
import time
from pathlib import Path

import urllib3
import cloudinary
import cloudinary.uploader as up

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

cloudinary.config(secure=True)  # CLOUDINARY_URL から読み込み
assert cloudinary.config().cloud_name == "dnmzdghoi", "CLOUDINARY_URL 未設定"

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
MAP_FILE = REPO / "_cloudinary_upload_map.json"
FRAMES_DIR = Path(r"C:\Users\sawas\Downloads\comm_frames\永遠に輝きを放つ乙女たち☆_202607041009")

data = json.loads((REPO / "scripts" / "merged_cindehist_eien_commu.json").read_text(encoding="utf-8"))
BASE = data["cloudinary_base"]

jobs = []
for e in data["entries"]:
    if e.get("frame"):
        num = e["frame"].split("_")[0]
        jobs.append((FRAMES_DIR / e["frame"], f"{BASE}/{num}"))

print(f"アップロード対象: {len(jobs)} 件")

uploaded = {}
failed = []
for i, (path, public_id) in enumerate(jobs, 1):
    if not path.exists():
        failed.append((public_id, "file not found"))
        continue
    for attempt in range(3):
        try:
            res = up.upload(
                str(path),
                public_id=public_id,
                overwrite=True,
                resource_type="image",
            )
            uploaded[public_id] = res["secure_url"]
            break
        except Exception as e:
            if attempt == 2:
                failed.append((public_id, str(e)))
            else:
                time.sleep(2)
    if i % 25 == 0 or i == len(jobs):
        print(f"  {i}/{len(jobs)} 完了")

try:
    m = json.loads(MAP_FILE.read_text(encoding="utf-8"))
except Exception:
    m = {}
for pid in uploaded:
    m[pid] = f"https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/{pid}"
MAP_FILE.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")

print(f"成功: {len(uploaded)} / 失敗: {len(failed)}")
for pid, err in failed:
    print(f"  FAILED {pid}: {err[:100]}")
