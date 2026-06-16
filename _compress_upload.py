#!/usr/bin/env python3
"""Compress oversized PNGs to JPEG and upload to Cloudinary."""
import os, json, ssl, time
import urllib3
from pathlib import Path
from PIL import Image
import cloudinary, cloudinary.uploader

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}
import cloudinary.uploader as _up
_up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

CLOUD_NAME = "dnmzdghoi"
cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=os.environ["CLOUDINARY_APIKEY"],
    api_secret=os.environ["CLOUDINARY_APISECRETKEY"],
    secure=True,
)

BASE_DIR = Path("C:/Users/sawas/Desktop/SugarHeartDB")
MAP_FILE = BASE_DIR / "_cloudinary_upload_map.json"
existing = json.load(open(MAP_FILE, encoding="utf-8"))

# Files that failed due to size
failed = [k for k, v in existing.items() if v is None and "OtherIdol" in k]
print(f"Re-uploading {len(failed)} failed files with compression:")

for rel_str in failed:
    p = BASE_DIR / rel_str.replace("/", "\\")
    public_id = "Deresute/OtherIdol/" + p.stem
    cdn_url = f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload/f_auto,q_auto/{public_id}"

    # Compress to JPEG in temp file
    tmp = Path("C:/Users/sawas/Desktop/SugarHeartDB/_tmp_compress.jpg")
    img = Image.open(p)
    img = img.convert("RGB")
    img.save(tmp, "JPEG", quality=85)
    print(f"  Compressed {p.name}: {p.stat().st_size//1024}KB -> {tmp.stat().st_size//1024}KB")

    try:
        cloudinary.uploader.upload(str(tmp), public_id=public_id, overwrite=True, resource_type="image")
        existing[rel_str] = cdn_url
        print(f"  OK: {rel_str}")
    except Exception as e:
        print(f"  FAILED: {rel_str} -> {e}")

if tmp.exists():
    tmp.unlink()

with open(MAP_FILE, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
print("Done. Map updated.")
