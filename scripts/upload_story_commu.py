# -*- coding: utf-8 -*-
"""ストーリーコミュ3種の使用フレーム＋ログ画像をCloudinaryにアップロードし、
_cloudinary_upload_map.json を更新する。"""
import json, re, os, ssl, urllib3, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding="utf-8")
d=open(os.path.expanduser(r"~/.claude.json"),encoding="utf-8").read()
os.environ["CLOUDINARY_URL"]=re.search(r"cloudinary://[0-9]+:[^\"']+@dnmzdghoi",d).group(0)
ssl._create_default_https_context=ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary, cloudinary.uploader as up
from PIL import Image
cloudinary.CERT_KWARGS={"cert_reqs":"CERT_NONE"}; up._http=urllib3.PoolManager(cert_reqs="CERT_NONE")

REPO=Path(__file__).parent.parent
FR=Path(r"C:\Users\sawas\Downloads\comm_frames")
JD=Path(r"G:\マイドライブ\コミュ")

COMMUS=[
    dict(key="sweetie", folder=FR/"Story_WhatIsSweetie_202606250744",
         cdn="Deresute/StoryCommu/WhatIsSweetie", logpng=JD/"What is Sweetie？_OP_log.png"),
    dict(key="arisu", folder=FR/"ありすストーリーコミュ_202607142202",
         cdn="Deresute/GuestCommu/OtherIdolStory/arisu", logpng=JD/"ありすストーリーコミュ_log.png"),
    dict(key="miyu", folder=FR/"美優さんストーリーコミュ_202607142217",
         cdn="Deresute/GuestCommu/OtherIdolStory/miyu", logpng=JD/"美優ストーリーコミュ_log.png"),
]

def fid(frame): return frame.split("_")[0]

def main():
    results={}
    for cfg in COMMUS:
        sec=json.loads((REPO/"scripts"/f"merged_{cfg['key']}_commu.json").read_text(encoding="utf-8"))
        frames={sec["title_frame"]}
        for e in sec["entries"]:
            if e.get("frame"): frames.add(e["frame"])
        jobs=[]
        for fr in sorted(frames):
            local=cfg["folder"]/fr
            pid=f"{cfg['cdn']}/commu/{fid(fr)}"
            jobs.append((str(local),pid))
        print(f"{cfg['key']}: {len(jobs)}フレーム アップロード開始")
        def work(job):
            local,pid=job
            up.upload(local, public_id=pid, overwrite=True, resource_type="image")
            return pid
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs={ex.submit(work,j):j for j in jobs}
            for f in as_completed(futs):
                pid=f.result(); results[pid]=f"https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/{pid}"
        # ログPNG（10MB超はJPEG圧縮）
        logpid=f"{cfg['cdn']}/log/OP"
        src=cfg["logpng"]
        if src.stat().st_size > 10*1024*1024:
            im=Image.open(src).convert("RGB")
            tmp=REPO/"scripts"/f"_log_{cfg['key']}.jpg"
            im.save(tmp,quality=85)
            up.upload(str(tmp), public_id=logpid, overwrite=True, resource_type="image")
            tmp.unlink()
        else:
            up.upload(str(src), public_id=logpid, overwrite=True, resource_type="image")
        results[logpid]=f"https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/{logpid}"
        print(f"{cfg['key']}: 完了（ログ含む）")
    # マップ更新（indent=1）
    p=REPO/"_cloudinary_upload_map.json"
    m=json.loads(p.read_text(encoding="utf-8"))
    m.update(results)
    p.write_text(json.dumps(m,ensure_ascii=False,indent=1),encoding="utf-8")
    print(f"合計 {len(results)} 件をマップに追記")

if __name__=="__main__":
    main()
