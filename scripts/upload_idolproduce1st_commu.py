# -*- coding: utf-8 -*-
"""第1回 アイドルプロデュース コミュ画像のCloudinaryアップロード

- G:\マイドライブ\アイプロはぁと の 1.png〜145.png（45は演出一覧のスクショのため除外）
- PNG(約4MB)をJPEG(q90)に変換してからアップロードする
- public_id: Deresute/Event/IdolProduce1st/commu/0001 〜 0145
- 完了後 _cloudinary_upload_map.json に追記
環境変数 CLOUDINARY_URL が必要。
"""
import json
import os
import ssl
import sys
import tempfile
import time
from pathlib import Path

import urllib3
import cloudinary
import cloudinary.uploader as up
from PIL import Image

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

cloudinary.config(secure=True)  # CLOUDINARY_URL から読み込み
assert cloudinary.config().cloud_name == "dnmzdghoi", "CLOUDINARY_URL 未設定"

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
SRC_DIR = Path(r"G:\マイドライブ\アイプロはぁと")
MAP_FILE = REPO / "_cloudinary_upload_map.json"
BASE = "Deresute/Event/IdolProduce1st"
SKIP = {45}  # 演出一覧のスクショ（セリフの撮り漏れ箇所）

tmpdir = Path(tempfile.mkdtemp(prefix="ip1st_"))
jobs = []
for n in range(1, 146):
    if n in SKIP:
        continue
    src = SRC_DIR / f"{n}.png"
    if not src.exists():
        print(f"  missing: {src}")
        continue
    jpg = tmpdir / f"{n:04d}.jpg"
    Image.open(src).convert("RGB").save(jpg, "JPEG", quality=90)
    jobs.append((jpg, f"{BASE}/commu/{n:04d}"))

print(f"アップロード対象: {len(jobs)} 件")

uploaded = {}
failed = []
for i, (path, public_id) in enumerate(jobs, 1):
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
