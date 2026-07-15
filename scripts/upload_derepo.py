# -*- coding: utf-8 -*-
"""でれぽ: 指定画像のアバター・添付写真・元スクショをCloudinaryにアップロードし、
_cloudinary_upload_map.json を更新する。

public_id:
  アバター  Deresute/Derepo/{N}/av{i}
  写真      Deresute/Derepo/{N}/photo{i}
  元スクショ Deresute/Derepo/src/{N}
usage: python upload_derepo.py 0 1 2   （番号省略時は derepo_text/*.json 全て）
"""
import sys, json, os, ssl, re, urllib3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, str(Path(__file__).parent))
from derepo_crop import process, IMGDIR
from derepo_detect import src_path

d = open(os.path.expanduser(r"~/.claude.json"), encoding="utf-8").read()
os.environ["CLOUDINARY_URL"] = re.search(r"cloudinary://[0-9]+:[^\"']+@dnmzdghoi", d).group(0)
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary, cloudinary.uploader as up
from PIL import Image
cloudinary.CERT_KWARGS = {"cert_reqs": "CERT_NONE"}; up._http = urllib3.PoolManager(cert_reqs="CERT_NONE")

REPO = Path(__file__).parent.parent
TEXT = REPO / "scripts" / "derepo_text"
TMP = REPO / "scripts" / "derepo_tmp"; TMP.mkdir(exist_ok=True)

def url(pid): return f"https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/{pid}"

def targets():
    if len(sys.argv) > 1:
        return [int(x) for x in sys.argv[1:]]
    return sorted(int(p.stem) for p in TEXT.glob("*.json"))

def main():
    results = {}
    jobs = []          # (local_path, public_id)
    for n in targets():
        posts = process(n)                       # crop -> derepo_img/{n}_{i}_av.png (+photo)
        for p in posts:
            i = p["i"]
            jobs.append((IMGDIR / f"{n}_{i}_av.png", f"Deresute/Derepo/{n}/av{i}"))
            if p["photo"]:
                jobs.append((IMGDIR / f"{n}_{i}_photo.png", f"Deresute/Derepo/{n}/photo{i}"))
        # 元スクショ（10MB超はJPEG圧縮）
        src = src_path(n)
        if src.stat().st_size > 10 * 1024 * 1024:
            im = Image.open(src).convert("RGB"); tmp = TMP / f"src{n}.jpg"; im.save(tmp, quality=85)
            jobs.append((tmp, f"Deresute/Derepo/src/{n}"))
        else:
            jobs.append((src, f"Deresute/Derepo/src/{n}"))
    print(f"アップロード {len(jobs)} 件")
    def work(job):
        local, pid = job
        up.upload(str(local), public_id=pid, overwrite=True, resource_type="image")
        return pid
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(work, j): j for j in jobs}
        for f in as_completed(futs):
            pid = f.result(); results[pid] = url(pid)
    mp = REPO / "_cloudinary_upload_map.json"
    m = json.loads(mp.read_text(encoding="utf-8")); m.update(results)
    mp.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"完了。マップに {len(results)} 件追記")

if __name__ == "__main__":
    main()
