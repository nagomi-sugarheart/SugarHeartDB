# -*- coding: utf-8 -*-
"""熱情エナモラル コミュ画像のCloudinaryアップロード

- merged_netsujou_commu.json で使用されているフレームのみアップロード
- ログ画像（Tr1/Tr2/OP/1〜5/ED）をアップロード（10MB超はJPEGに圧縮）
  ※ 第3話ログは当初EDではなく第4話の複製が保存されていたが、ユーザーから
    正しい第3話ログ（乱れたい女たち）の提供を受け差し替え済みのため通常どおり。
- 完了後 _cloudinary_upload_map.json に追記
CLOUDINARY_URL は未設定なら ~/.claude.json から自動取得する。
"""
import json
import os
import ssl
import sys
import time
import tempfile
from pathlib import Path

if not os.environ.get("CLOUDINARY_URL"):
    cj = Path(os.path.expanduser("~")) / ".claude.json"
    conf = json.loads(cj.read_text(encoding="utf-8"))
    os.environ["CLOUDINARY_URL"] = conf["mcpServers"]["cloudinary"]["headers"]["cloudinary-url"]

import urllib3
import cloudinary
import cloudinary.uploader as up
from PIL import Image

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

cloudinary.config(secure=True)
assert cloudinary.config().cloud_name == "dnmzdghoi", "CLOUDINARY_URL 未設定"

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
FRAMES_DIR = Path(r"C:\Users\sawas\Downloads\comm_frames\熱情エナモラル_202606282127")
LOG_DIR = Path(r"G:\マイドライブ\コミュ")
LOG_PREFIX = "熱情エナモラル"
MERGED = REPO / "scripts" / "merged_netsujou_commu.json"
MAP_FILE = REPO / "_cloudinary_upload_map.json"
BASE = "Deresute/Event/NetsujouEnamorar"
LOG_CODES = ["Tr1", "Tr2", "OP", "1", "2", "3", "4", "5", "ED"]
MAX_BYTES = 10 * 1024 * 1024

data = json.loads(MERGED.read_text(encoding="utf-8"))


def resolve_log(code):
    for ext in (".png", ".PNG"):
        p = LOG_DIR / f"{LOG_PREFIX}_{code}_log{ext}"
        if p.exists():
            return p
    return LOG_DIR / f"{LOG_PREFIX}_{code}_log.png"


frames = set()
for sec in data:
    if sec.get("title_frame"):
        frames.add(sec["title_frame"])
    for e in sec["entries"]:
        if e.get("frame"):
            frames.add(e["frame"])

jobs = []
for f in sorted(frames):
    num = f.split("_")[0]
    jobs.append((FRAMES_DIR / f, f"{BASE}/commu/{num}"))
for code in LOG_CODES:
    jobs.append((resolve_log(code), f"{BASE}/log/{code}"))

print(f"アップロード対象: {len(jobs)} 件")


def prepared_path(path):
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
