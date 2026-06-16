#!/usr/bin/env python3
"""Upload all Deresute/OtherIdol images to Cloudinary and update the map."""
import os, json, ssl, time
import urllib3
from pathlib import Path
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
TARGET_DIR = BASE_DIR / "Deresute" / "OtherIdol"
MAP_FILE = BASE_DIR / "_cloudinary_upload_map.json"

existing = json.load(open(MAP_FILE, encoding="utf-8")) if MAP_FILE.exists() else {}

files = sorted(TARGET_DIR.glob("*"))
files = [f for f in files if f.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}]
print(f"Found {len(files)} files in OtherIdol")

new_results = {}
for i, p in enumerate(files, 1):
    rel = str(p.relative_to(BASE_DIR)).replace("\\", "/")
    if rel in existing and existing[rel] is not None:
        print(f"[{i}/{len(files)}] SKIP (already uploaded): {rel}")
        continue
    public_id = "Deresute/OtherIdol/" + p.stem
    cdn_url = f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload/f_auto,q_auto/{public_id}"
    try:
        cloudinary.uploader.upload(str(p), public_id=public_id, overwrite=True, resource_type="image")
        new_results[rel] = cdn_url
        print(f"[{i}/{len(files)}] OK: {rel}")
    except Exception as e:
        print(f"[{i}/{len(files)}] ERROR: {rel} -> {e}")
        time.sleep(2)
        try:
            cloudinary.uploader.upload(str(p), public_id=public_id, overwrite=True, resource_type="image")
            new_results[rel] = cdn_url
            print(f"[{i}/{len(files)}] RETRY OK: {rel}")
        except Exception as e2:
            new_results[rel] = None
            print(f"[{i}/{len(files)}] FAILED: {rel} -> {e2}")

existing.update(new_results)
with open(MAP_FILE, "w", encoding="utf-8") as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)

ok = sum(1 for v in new_results.values() if v)
fail = sum(1 for v in new_results.values() if not v)
print(f"\nDone. New uploads: {ok} OK, {fail} failed. Map updated.")
