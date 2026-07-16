# -*- coding: utf-8 -*-
"""営業コミュ画像のCloudinaryアップロード

- merged_eigyo_commu.json で使用されているフレームのみアップロード
- 各営業のログPNG（{タイトル}_OP_log.png）もアップロード（10MB超はJPEG圧縮）
- public_id: Deresute/Eigyo/{pid}/commu/{num} ・ Deresute/Eigyo/{pid}/log
- 完了後 _cloudinary_upload_map.json に追記

環境変数 CLOUDINARY_URL が必要（cloudinary://<api_key>:<api_secret>@dnmzdghoi）。
"""
import json
import os
import ssl
import sys
import time
import tempfile
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
FRAMES_ROOT = Path(r"C:\Users\sawas\Downloads\comm_frames")
LOG_DIR = Path(r"G:\マイドライブ\コミュ")
MERGED = REPO / "scripts" / "merged_eigyo_commu.json"
MAP_FILE = REPO / "_cloudinary_upload_map.json"
BASE = "Deresute/Eigyo"
MAX_BYTES = 10 * 1024 * 1024

data = json.loads(MERGED.read_text(encoding="utf-8"))

jobs = []  # (ローカルパス, public_id)
for sec in data:
    pid = sec["pid"]
    frames_dir = FRAMES_ROOT / sec["folder"]
    frames = {sec["title_frame"]}
    for e in sec["entries"]:
        if e.get("frame"):
            frames.add(e["frame"])
    for f in sorted(frames):
        num = f.split("_")[0]
        jobs.append((frames_dir / f, f"{BASE}/{pid}/commu/{num}"))
    # ログPNG（プレフィックス＝タイトル）
    jobs.append((LOG_DIR / f"{sec['title']}_OP_log.png", f"{BASE}/{pid}/log"))

print(f"アップロード対象: {len(jobs)} 件")


def prepared_path(path):
    """10MB超はJPEG(quality=88)に圧縮した一時ファイルを返す"""
    if path.stat().st_size <= MAX_BYTES:
        return str(path), None
    img = Image.open(path).convert("RGB")
    tmp = Path(tempfile.gettempdir()) / (path.stem + "_c.jpg")
    img.save(tmp, "JPEG", quality=88, optimize=True)
    print(f"  圧縮: {path.name} {path.stat().st_size} -> {tmp.stat().st_size}")
    return str(tmp), tmp


uploaded = {}
failed = []
for i, (path, public_id) in enumerate(jobs, 1):
    if not path.exists():
        failed.append((str(path), "file not found"))
        continue
    send_path, tmp = prepared_path(path)
    for attempt in range(3):
        try:
            res = up.upload(send_path, public_id=public_id, overwrite=True, resource_type="image")
            uploaded[public_id] = res["secure_url"]
            break
        except Exception as e:
            if attempt == 2:
                failed.append((public_id, str(e)))
            else:
                time.sleep(2)
    if tmp:
        try:
            os.remove(tmp)
        except OSError:
            pass
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
