# -*- coding: utf-8 -*-
"""第1回 アイドルプロデュース コミュ画像のCloudinaryアップロード

使い方: python upload_idolproduce1st_commu.py [kokoro|nana|ev]
- kokoro: G:\マイドライブ\アイプロはぁと → Deresute/Event/IdolProduce1st/commu/{NNNN}
  （45は演出一覧のスクショ＝セリフ撮り漏れのため除外）
- nana:   G:\マイドライブ\アイプロ菜々   → Deresute/Event/IdolProduce1st/commu_nana/{NNNN}
- ev:     予告/OP/EDコミュ。merged_idolproduce1st_ev_commu.json の使用フレームを
          Deresute/Event/IdolProduce1st/commu_ev/{NNNN} へ、ログ画像を .../log/{code} へ
- kokoro/nana はPNG(約4MB)をJPEG(q90)に変換してからアップロードする
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

TARGETS = {
    "kokoro": {
        "src": Path(r"G:\マイドライブ\アイプロはぁと"),
        "base": "Deresute/Event/IdolProduce1st/commu",
        "skip": {45},  # 演出一覧のスクショ（セリフの撮り漏れ箇所）
    },
    "nana": {
        "src": Path(r"G:\マイドライブ\アイプロ菜々"),
        "base": "Deresute/Event/IdolProduce1st/commu_nana",
        "skip": set(),
    },
}
mode = sys.argv[1] if len(sys.argv) > 1 else "kokoro"

REPO = Path(__file__).parent.parent
MAP_FILE = REPO / "_cloudinary_upload_map.json"

jobs = []
if mode == "ev":
    FRAMES_DIR = Path(r"C:\Users\sawas\Downloads\comm_frames\アイプロ_202607091906")
    LOG_DIR = Path(r"G:\マイドライブ\コミュ")
    BASE = "Deresute/Event/IdolProduce1st"
    data = json.loads((REPO / "scripts" / "merged_idolproduce1st_ev_commu.json").read_text(encoding="utf-8"))
    frames = set()
    for sec in data:
        if sec.get("title_frame"):
            frames.add(sec["title_frame"])
        for e in sec["entries"]:
            if e.get("frame"):
                frames.add(e["frame"])
    for f in sorted(frames):
        num = f.split("_")[0]
        jobs.append((FRAMES_DIR / f, f"{BASE}/commu_ev/{num}"))
    for code in ["Tr1", "Tr2", "OP", "ED"]:
        jobs.append((LOG_DIR / f"第1回 アイドルプロデュース_{code}_log.png", f"{BASE}/log/{code}"))
else:
    target = TARGETS[mode]
    tmpdir = Path(tempfile.mkdtemp(prefix="ip1st_"))
    for n in range(1, 146):
        if n in target["skip"]:
            continue
        src = target["src"] / f"{n}.png"
        if not src.exists():
            print(f"  missing: {src}")
            continue
        jpg = tmpdir / f"{n:04d}.jpg"
        Image.open(src).convert("RGB").save(jpg, "JPEG", quality=90)
        jobs.append((jpg, f"{target['base']}/{n:04d}"))

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
