# -*- coding: utf-8 -*-
"""EVERLASTING & EVERAFTER のフレーム＆ログをCloudinaryへアップロード。

public_id:
  Deresute/GuestCommu/EverlastingEverafter/{Everlasting|Everafter}/commu/{NNNN}
  Deresute/GuestCommu/EverlastingEverafter/{Everlasting|Everafter}/log/{code}
"""
import json, re, os, ssl, sys, glob, io as _io
from pathlib import Path
import urllib3

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).parent.parent
FRAMES = Path(r"C:\Users\sawas\Downloads\comm_frames")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
MERGED = REPO / "scripts" / "merged_ee_commu.json"
BASE = "Deresute/GuestCommu/EverlastingEverafter"

EVENT_INFO = {
    "everlasting": {"pid": "Everlasting", "csv": "EVERLASTING_202607172138",
                    "prefix": "EVERLASTING", "logs": ["5", "10"]},
    "everafter":  {"pid": "Everafter", "csv": "EVERAFTER_202607172137",
                   "prefix": "EVERAFTER", "logs": ["OP", "1", "5", "ED"]},
}

d = open(os.path.expanduser(r"C:/Users/sawas/.claude.json"), encoding="utf-8").read()
os.environ["CLOUDINARY_URL"] = re.search(r"cloudinary://[0-9]+:[^\"']+@dnmzdghoi", d).group(0)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary, cloudinary.uploader as up
from PIL import Image
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

data = json.loads(MERGED.read_text(encoding="utf-8"))
new_map = {}
totok = totfail = 0

for ev in data:
    info = EVENT_INFO[ev["id"]]
    pidbase = f"{BASE}/{info['pid']}"
    # 番号 -> file
    num2file = {}
    for f in glob.glob(str(FRAMES / info["csv"] / "*.jpg")):
        m = re.match(r"(\d+)", Path(f).name)
        if m:
            num2file[m.group(1)] = f
    used = set()
    for s in ev["sections"]:
        if s.get("title_frame"):
            used.add(s["title_frame"])
        for e in s["entries"]:
            if e.get("frame"):
                used.add(e["frame"])
    for num in sorted(used):
        fp = num2file.get(num)
        if not fp:
            print(f"MISSING frame {ev['id']} {num}"); totfail += 1; continue
        pid = f"{pidbase}/commu/{num}"
        try:
            up.upload(fp, public_id=pid, overwrite=True); totok += 1
            new_map[pid] = f"https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/{pid}"
        except Exception as ex:
            print(f"NG frame {pid}: {ex}"); totfail += 1
    # logs
    for code in info["logs"]:
        png = JSON_DIR / f"{info['prefix']}_{code}_log.png"
        pid = f"{pidbase}/log/{code}"
        if not png.exists():
            print(f"LOG missing {png}"); continue
        try:
            if png.stat().st_size > 10 * 1024 * 1024:
                im = Image.open(png).convert("RGB")
                buf = _io.BytesIO(); im.save(buf, "JPEG", quality=88); buf.seek(0)
                up.upload(buf, public_id=pid, overwrite=True)
            else:
                up.upload(str(png), public_id=pid, overwrite=True)
            totok += 1
            new_map[pid] = f"https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/{pid}"
        except Exception as ex:
            print(f"NG log {pid}: {ex}")

print(f"ok={totok} fail={totfail}")

# _cloudinary_upload_map.json 追記
MAP = REPO / "_cloudinary_upload_map.json"
m = json.loads(MAP.read_text(encoding="utf-8"))
added = 0
for k, v in new_map.items():
    if k not in m:
        m[k] = v; added += 1
json.dump(m, open(MAP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"map追記: {added}")
print("DONE")
