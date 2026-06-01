#!/usr/bin/env python3
"""
Cloudinary migration script
1. Upload all images maintaining folder structure
2. Replace image paths in HTML files
3. Output list of uploaded files for deletion
"""
import os
import re
import json
import time
import ssl
import urllib3
from pathlib import Path
import cloudinary
import cloudinary.uploader

# Disable SSL verification for environments with self-signed certificates
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CLOUD_NAME = "dnmzdghoi"
API_KEY = os.environ["CLOUDINARY_APIKEY"]
API_SECRET = os.environ["CLOUDINARY_APISECRETKEY"]

cloudinary.config(
    cloud_name=CLOUD_NAME,
    api_key=API_KEY,
    api_secret=API_SECRET,
    secure=True,
    api_proxy=None,
)

BASE_DIR = Path(__file__).parent
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}

def find_images():
    images = []
    for p in BASE_DIR.rglob("*"):
        if p.suffix.lower() in IMAGE_EXTS and ".git" not in p.parts:
            images.append(p)
    return sorted(images)

def get_public_id(image_path: Path) -> str:
    rel = image_path.relative_to(BASE_DIR)
    # Remove extension for public_id
    parts = list(rel.parts)
    name_no_ext = rel.stem
    folder_parts = parts[:-1]
    if folder_parts:
        return "/".join(folder_parts) + "/" + name_no_ext
    return name_no_ext

def get_cloudinary_url(public_id: str, ext: str) -> str:
    # Use f_auto,q_auto for optimization; keep original format for SVG
    if ext.lower() == ".svg":
        return f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload/{public_id}.svg"
    return f"https://res.cloudinary.com/{CLOUD_NAME}/image/upload/f_auto,q_auto/{public_id}"

def upload_images(images):
    results = {}
    total = len(images)
    print(f"Uploading {total} images...")
    for i, img_path in enumerate(images, 1):
        rel = img_path.relative_to(BASE_DIR)
        public_id = get_public_id(img_path)
        ext = img_path.suffix.lower()

        # Determine folder
        parts = list(rel.parts)
        folder = "/".join(parts[:-1]) if len(parts) > 1 else ""

        try:
            resource_type = "image"
            upload_opts = {
                "public_id": public_id,
                "overwrite": True,
                "resource_type": resource_type,
            }
            if folder:
                upload_opts["folder"] = None  # public_id already includes folder

            result = cloudinary.uploader.upload(str(img_path), **upload_opts)
            cloudinary_url = get_cloudinary_url(public_id, ext)
            results[str(rel)] = cloudinary_url
            print(f"[{i}/{total}] OK: {rel}")
        except Exception as e:
            print(f"[{i}/{total}] ERROR: {rel} -> {e}")
            # Retry once after 2s
            time.sleep(2)
            try:
                result = cloudinary.uploader.upload(str(img_path), **upload_opts)
                cloudinary_url = get_cloudinary_url(public_id, ext)
                results[str(rel)] = cloudinary_url
                print(f"[{i}/{total}] RETRY OK: {rel}")
            except Exception as e2:
                print(f"[{i}/{total}] FAILED: {rel} -> {e2}")
                results[str(rel)] = None

    return results

def replace_html_paths(upload_map):
    """Replace image src/href paths in HTML files with Cloudinary URLs."""
    html_files = list(BASE_DIR.rglob("*.html"))
    html_files = [f for f in html_files if ".git" not in f.parts]
    print(f"\nReplacing paths in {len(html_files)} HTML files...")

    # Build a mapping from relative path patterns to Cloudinary URLs
    # We need to handle paths like: ./Popmas/icon.jpeg, Popmas/icon.jpeg, ../Popmas/icon.jpeg

    replaced_count = 0
    for html_path in html_files:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        html_dir = html_path.parent

        for rel_str, cdn_url in upload_map.items():
            if cdn_url is None:
                continue

            img_path = BASE_DIR / rel_str

            # Compute relative path from HTML file's directory to image
            try:
                rel_from_html = os.path.relpath(img_path, html_dir)
            except ValueError:
                continue

            # Normalize path separator for HTML (use forward slashes)
            rel_from_html_fwd = rel_from_html.replace("\\", "/")

            # Also compute path relative to BASE_DIR (for absolute-ish references)
            rel_from_base = rel_str.replace("\\", "/")

            # Replace various forms of the path
            for old_path in [rel_from_html_fwd, "./" + rel_from_html_fwd, rel_from_base, "./" + rel_from_base]:
                # Escape for regex
                escaped = re.escape(old_path)
                # Match in src="..." or href="..." or url(...)
                for pattern, repl in [
                    (f'(src=["\']){escaped}(["\'])', f'\\g<1>{cdn_url}\\2'),
                    (f'(href=["\']){escaped}(["\'])', f'\\g<1>{cdn_url}\\2'),
                    (f'(url\\(["\']?){escaped}(["\']?\\))', f'\\g<1>{cdn_url}\\2'),
                    (f'(content=["\']){escaped}(["\'])', f'\\g<1>{cdn_url}\\2'),
                ]:
                    content = re.sub(pattern, repl, content)

        if content != original:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)
            replaced_count += 1
            print(f"  Updated: {html_path.relative_to(BASE_DIR)}")

    print(f"Updated {replaced_count} HTML files.")

def main():
    images = find_images()
    print(f"Found {len(images)} images.\n")

    # Check for existing upload map
    map_file = BASE_DIR / "_cloudinary_upload_map.json"
    if map_file.exists():
        print("Found existing upload map, loading...")
        with open(map_file) as f:
            upload_map = json.load(f)
        # Re-upload only failed ones
        failed = [BASE_DIR / k for k, v in upload_map.items() if v is None]
        if failed:
            print(f"Retrying {len(failed)} failed uploads...")
            retry_map = upload_images(failed)
            upload_map.update(retry_map)
    else:
        upload_map = upload_images(images)
        with open(map_file, "w") as f:
            json.dump(upload_map, f, indent=2, ensure_ascii=False)
        print(f"\nUpload map saved to {map_file}")

    # Count results
    success = sum(1 for v in upload_map.values() if v is not None)
    failed = sum(1 for v in upload_map.values() if v is None)
    print(f"\nUpload results: {success} succeeded, {failed} failed")

    if failed > 0:
        print("Failed files:")
        for k, v in upload_map.items():
            if v is None:
                print(f"  {k}")

    # Replace HTML paths
    replace_html_paths(upload_map)

    print("\nDone! Review changes, then delete image files.")

if __name__ == "__main__":
    main()
