# -*- coding: utf-8 -*-
"""ストーリーコミュ（単話）のCSV×JSONマージ

対象: What is Sweetie？ / 橘ありす（Be honest with yourself）/ 三船美優（Step forward to the future）
各コミュは1話構成。中央表示のピンク吹き出しはPのセリフ、場所/時刻カードはシーン、
speaker空のdialogueはナレーション。突合ロジックは merge_inochi_commu.py を単話用に簡略化。

出力: merged_{key}_commu.json / merge_{key}_report.txt
"""
import csv, json, re, sys
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT_DIR = Path(__file__).parent
FR = Path(r"C:\Users\sawas\Downloads\comm_frames")
JD = Path(r"G:\マイドライブ\コミュ")

# 各コミュの設定
#   scene_nos: 場所/時刻カード（center_textのみ）の no
#   pline_nos: Pの中央表示セリフ（ピンク吹き出し）の no
#   stage_nos: ナレーション（speaker空のdialogue）の no
COMMUS = [
    dict(key="sweetie", csv=FR/"Story_WhatIsSweetie_202606250744"/"dialogues.csv",
         json=JD/"What is Sweetie？_OP_log.json",
         scene_nos={1,21,50,57,80,91,131,150,162},
         pline_nos={119,121,168}, stage_nos=set(),
         known={"心","菜々","比奈","美玲","柚","P"}),
    dict(key="arisu", csv=FR/"ありすストーリーコミュ_202607142202"/"dialogues.csv",
         json=JD/"ありすストーリーコミュ_OP_log.json",
         scene_nos={1,13,17,33,41,62,74,85,131,149},
         pline_nos={70,77,136,138,140}, stage_nos={148},
         known={"ありす","薫","仁奈","夕美","心","ありすの母","P"}),
    dict(key="miyu", csv=FR/"美優さんストーリーコミュ_202607142217"/"dialogues.csv",
         json=JD/"美優ストーリーコミュ_OP_log.json",
         scene_nos={1,7,34,48},
         pline_nos={49,135,143,147,161,170,172}, stage_nos={108},
         known={"美優","仁奈","晴","亜季","心","美優の母","スタッフ","P"}),
]

SPEAKER_NORMALIZE = {"プロデューサー":"P","なごみP":"P","なこみP":"P","なごみ":"P","なこみ":"P"}
DISPLAY_FIXES = [("〜","～"),("はあと","はぁと"),("しゃがーはぁと","しゅがーはぁと"),("スキップ LIVE","LIVE")]


def norm_speaker(s): return SPEAKER_NORMALIZE.get(s.strip(), s.strip())

def norm_text(s):
    s = re.sub(r"\s+","",s)
    for a in "…‥・":
        s = s.replace(a,"")
    s = (s.replace("！","!").replace("？","?").replace("♪","").replace("☆","")
           .replace("―","").replace("ー","").replace("『","").replace("』","")
           .replace("「","").replace("」","").replace("（","").replace("）","")
           .replace("(","").replace(")","").replace("、","").replace("。","")
           .replace(",","").replace(".",""))
    return s

def is_ellipsis_only(s):
    return bool(s) and not norm_text(s) and bool(re.fullmatch(r"[…‥.。、\s]+", s))

def sim(a,b):
    if is_ellipsis_only(a) and is_ellipsis_only(b): return 1.0
    na,nb = norm_text(a),norm_text(b)
    if not na or not nb: return 0.0
    r = SequenceMatcher(None,na,nb).ratio()
    if min(len(na),len(nb)) >= 4 and (nb.startswith(na) or na.startswith(nb)): r = max(r,0.9)
    if len(nb) > len(na) >= 4:
        pr = SequenceMatcher(None,na,nb[:len(na)+2]).ratio()
        if pr >= 0.75: r = max(r,pr)
    return r

def fix_display(s):
    s = re.sub(r"\s+"," ",s).strip()
    for a,b in DISPLAY_FIXES: s = s.replace(a,b)
    if s.startswith("(") and s.endswith(")"): s = "（"+s[1:-1]+"）"
    return s

def load_json_lines(path, known):
    d = json.loads(path.read_text(encoding="utf-8"))
    lines = []
    for c in d["conversation"]:
        sp,dg = c["speaker"].strip(), c["dialogue"].strip()
        if sp == dg: continue
        if sp.startswith("（") and not dg:
            lines.append({"speaker":"ナレーション","text":sp}); continue
        # 話者欄に本文が丸ごと入ったOCRグリッチ（既知話者でない長文）→ 本文が空ならスキップ
        if len(sp) > 6 and sp not in known and dg:
            lines.append({"speaker":"","text":dg}); continue
        if len(sp) > 6 and sp not in known and not dg:
            continue
        lines.append({"speaker":norm_speaker(sp),"text":dg})
    return d, lines

def classify(r, cfg):
    no = int(r["no"]); sp,dg,ct = r["speaker"].strip(),r["dialogue"].strip(),r["center_text"].strip()
    if not sp and not dg and not ct: return ("empty","",None)
    if no in cfg["scene_nos"]: return ("scene","",re.sub(r"\s+"," ",ct or dg))
    if no in cfg["pline_nos"]: return ("line","P",re.sub(r"\s+"," ",ct or dg))
    if no in cfg["stage_nos"]:
        txt=re.sub(r"\s+"," ",ct or dg)
        if "スキップ" in txt or "コミュでのLIVE" in txt: txt="LIVE"  # LIVEスキップ画面
        return ("stage","",txt)
    if not sp and ct and not dg: return ("scene","",re.sub(r"\s+"," ",ct))  # 未分類の場所カード
    if not sp and dg: return ("stage","",dg)
    if (sp and dg and ct and ct != dg and len(ct) <= 12 and not any(c in ct for c in "!！?？。、")):
        return ("line",norm_speaker(ct),dg)
    return ("line",norm_speaker(sp),dg)

def dup_index(out, text, speaker, win=12, thr=0.85):
    """直近win件に同一話者の高類似セリフがあればそのout内indexを返す（無ければNone）。
    話者が異なる同一テキスト（心→全員の掛け合い等）は重複とみなさない。
    OCR揺れの途中フレームを拾うため類似度は対称に評価する。"""
    nt=norm_text(text)
    if len(nt) < 4: return None  # 短い相槌は誤除去を避ける
    for idx in range(len(out)-1, max(-1, len(out)-win-1), -1):
        e=out[idx]
        if (e["type"]=="line" and e["speaker"]==speaker and len(norm_text(e["text"])) >= 4
                and max(sim(text,e["text"]), sim(e["text"],text)) >= thr):
            return idx
    return None

def build_csv_only(csv_rows, report, cfg):
    """CSVを一次情報として本文を構築する。

    CSVはJSONより行数が多く（欠損セリフはほぼ無い）、OCR品質も高く、時系列順で並ぶ。
    そのためJSON突合は行わず、CSVから直接構築する。JSON突合は録画リプレイ由来の
    重複・順序乱れを招くため用いない（JSONはタイトル/要約のみ利用）。処理:
      - 途中フレーム（前のセリフが次のセリフの前方一致・同話者・近接時刻）を完全版に統合
      - 録画リプレイ由来の重複（近接ウィンドウ内の高類似セリフ・完全一致シーン）を除去
    """
    out=[]
    for r in csv_rows:
        typ,sp,text = classify(r,cfg); frame=r["frame_file"]; t=float(r["timestamp_s"])
        if typ=="empty": continue
        if not norm_text(text) and not is_ellipsis_only(text): continue  # 本文空フレーム
        if typ=="scene":
            if any(e["type"]=="scene" and norm_text(e["text"])==norm_text(text) for e in out[-10:]):
                report.append(f"重複シーン除去: no{r['no']} {text}"); continue
            out.append({"type":"scene","speaker":"","text":text,"frame":frame,"t":t}); continue
        if typ=="stage":
            out.append({"type":"stage","speaker":"","text":text,"frame":frame,"t":t}); continue
        # リプレイ重複・途中フレーム: 同話者の近接高類似があれば長い方（完全版）を残す
        di=dup_index(out, text, sp)
        if di is not None:
            if len(norm_text(text)) > len(norm_text(out[di]["text"])):
                report.append(f"完全版に差し替え: no{r['no']} 「{out[di]['text'][:15]}」→「{text[:15]}」")
                out[di]={"type":"line","speaker":sp,"text":text,"frame":frame,"t":t}
            else:
                report.append(f"重複セリフ除去: no{r['no']} {sp}: {text[:30]}")
            continue
        out.append({"type":"line","speaker":sp,"text":text,"frame":frame,"t":t})
    return out

def main():
    for cfg in COMMUS:
        rows=list(csv.DictReader(open(cfg["csv"],encoding="utf-8-sig")))
        d,_=load_json_lines(cfg["json"],cfg["known"])  # title/summaryのみ利用
        report=[]
        first_typ,_,_=classify(rows[0],cfg)
        title_frame=rows[0]["frame_file"]
        body=build_csv_only(rows[1:] if first_typ=="scene" else rows, report, cfg)
        sec={"key":cfg["key"],"title":fix_display(d["title"]),"summary":fix_display(d["summary"]),
             "title_frame":title_frame,"entries":[dict(e,text=fix_display(e["text"])) for e in body]}
        (OUT_DIR/f"merged_{cfg['key']}_commu.json").write_text(json.dumps(sec,ensure_ascii=False,indent=1),encoding="utf-8")
        (OUT_DIR/f"merge_{cfg['key']}_report.txt").write_text("\n".join(report),encoding="utf-8")
        n_shot=sum(1 for e in sec["entries"] if e.get("frame"))
        n_no=sum(1 for e in sec["entries"] if e["type"]=="line" and not e.get("frame"))
        print(f"{cfg['key']}: 全{len(sec['entries'])}行 shot付{n_shot} shotなし{n_no} | {sec['title']} | report {len(report)}行")

if __name__=="__main__":
    main()
