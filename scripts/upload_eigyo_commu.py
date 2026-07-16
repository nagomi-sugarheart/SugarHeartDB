# -*- coding: utf-8 -*-
"""営業コミュ画像のCloudinaryアップロード

- merged_eigyo_commu.json で使用されているフレームのみアップロード
- 各営業のログPNG（{タイトル}_OP_log.png）もアップロード（10MB超はJPEG圧縮）
- public_id: Deresute/Eigyo/{pid}/commu/{num} ・ Deresute/Eigyo/{pid}/log
- 完了後 _cloudinary_upload_map.json に追記

認証情報はリポジトリ直下の .env（CLOUDINARY_APIKEY / CLOUDINARY_APISECRETKEY）から
自動読み込みする。環境変数に設定済みならそちらを優先。
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

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent


def load_dotenv(path):
    """.env を素朴にパースして os.environ に取り込む（未設定のキーのみ）"""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv(REPO / ".env")

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

cloudinary.config(
    cloud_name="dnmzdghoi",
    api_key=os.environ["CLOUDINARY_APIKEY"],
    api_secret=os.environ["CLOUDINARY_APISECRETKEY"],
    secure=True,
    api_proxy=None,
)
assert cloudinary.config().cloud_name == "dnmzdghoi", "Cloudinary 認証情報が読み込めません"
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
