# -*- coding: utf-8 -*-
"""EVERLASTING & EVERAFTER（デレステ）のCSV×JSONマージスクリプト

2イベントを1ページに掲載:
- EVERLASTING (動画 vzls2sQRzd8): 第5話 / 第10話（ログ名EDだが実10話）
- EVERAFTER  (動画 e2mzlpSA5ek): OP / 楽曲MV / 1話 / 5話 / ED
  ※動画はOP・楽曲MV・1話まで。5話・EDはログのみ（no-shot）。楽曲MVは映像のみ（頭出しタブ）。

各セクションにCSV行範囲を明示指定。log-only/mv セクションはCSV突合しない。
"""
import csv, json, re, sys
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

FRAMES = Path(r"C:\Users\sawas\Downloads\comm_frames")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
OUT_DIR = Path(__file__).parent
OUT_JSON = OUT_DIR / "merged_ee_commu.json"
OUT_REPORT = OUT_DIR / "merge_ee_report.txt"

# セクション: (id, tab, title, 話ラベル, json_code, csv行リスト or None, title_frame行 or None, start秒, kind)
#   kind: commu(shot突合) / logonly(ログのみ) / mv(映像のみ)
EVENTS = [
    {
        "id": "everlasting", "name": "EVERLASTING", "video": "vzls2sQRzd8",
        "csv": "EVERLASTING_202607172138",
        "sections": [
            ("el5", "第5話", "Actors & Models", "第5話", "5",
             list(range(0, 23)), 0, 0, "commu"),
            ("el10", "第10話", "Glowing Memories", "第10話", "10",
             list(range(23, 55)), 23, 254, "commu"),
        ],
    },
    {
        "id": "everafter", "name": "EVERAFTER", "video": "e2mzlpSA5ek",
        "csv": "EVERAFTER_202607172137",
        "sections": [
            ("eaop", "OP", "Cinderella's Story", "OP", "OP",
             list(range(0, 19)), 0, 0, "commu"),
            ("eamv", "楽曲MV", "EVERAFTER（楽曲MV）", "楽曲MV", None,
             None, None, 231, "mv"),
            ("ea1", "1話", "An Invite to the Ball", "第1話", "1",
             list(range(25, 86)), 25, 408, "commu"),
            ("ea5", "5話", "Please ! Cinderella", "第5話", "5",
             None, None, None, "logonly"),
            ("eaed", "ED", "Cast a spell on you", "エンディング", "ED",
             None, None, None, "logonly"),
        ],
    },
]

SPEAKER_NORMALIZE = {
    "プロデューサー": "P", "なごみP": "P", "なこみP": "P",
    "なし": "ナレーション", "不明": "ナレーション",
}


def norm_speaker(s):
    return SPEAKER_NORMALIZE.get(s.strip(), s.strip())


def norm_text(s):
    s = re.sub(r"\s+", "", s or "")
    for ch in "…‥・！？♪☆★♡―ー『』「」（）()、。,.":
        s = s.replace(ch, "")
    return s


def is_ellipsis_only(s):
    return bool(s) and not norm_text(s) and bool(re.fullmatch(r"[…‥.。、\s]+", s))


def sim(a, b):
    if is_ellipsis_only(a) and is_ellipsis_only(b):
        return 1.0
    na, nb = norm_text(a), norm_text(b)
    if not na or not nb:
        return 0.0
    r = SequenceMatcher(None, na, nb).ratio()
    if nb.startswith(na) or na.startswith(nb):
        r = max(r, 0.9)
    if len(nb) > len(na) >= 4:
        pr = SequenceMatcher(None, na, nb[: len(na) + 2]).ratio()
        if pr >= 0.75:
            r = max(r, pr)
    return r


DISPLAY_FIXES = [("〜", "～"), ("はあと", "はぁと"), ("しゅかー", "しゅがー")]


def fix_display(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    for a, b in DISPLAY_FIXES:
        s = s.replace(a, b)
    if s.startswith("(") and s.endswith(")"):
        s = "（" + s[1:-1] + "）"
    return s


def load_json_lines(prefix, code):
    p = JSON_DIR / f"{prefix}_{code}_log.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    lines = []
    for c in d["conversation"]:
        sp, dg = c["speaker"].strip(), c["dialogue"].strip()
        if sp == dg:
            lines.append({"speaker": "ナレーション", "text": dg}); continue
        sp = norm_speaker(sp)
        lines.append({"speaker": "ナレーション" if sp == "ナレーション" else sp, "text": dg})
    return d, lines


def frame_num(frame_file):
    m = re.match(r"(\d+)", frame_file or "")
    return m.group(1) if m else None


def classify(r):
    sp, dg, ct = r["speaker"].strip(), r["dialogue"].strip(), r["center_text"].strip()
    if not sp and not dg and not ct:
        return ("empty", None, None)
    if not sp and ct and not dg:
        return ("scene", "", ct)
    if not sp and dg:
        return ("stage", "", dg)
    return ("line", norm_speaker(sp), dg)


def merge_section(csv_rows, json_lines, report, sec):
    out, j, last_idx, last_json = [], 0, None, None
    for r in csv_rows:
        typ, sp, text = classify(r)
        frame = frame_num(r["frame_file"])
        t = float(r["timestamp_s"])
        if typ == "empty":
            continue
        if typ == "scene":
            out.append({"type": "scene", "speaker": "", "text": text, "frame": frame, "t": t}); continue
        if typ == "stage":
            best_k, best_s = -1, 0.0
            for k in range(j, min(j + 12, len(json_lines))):
                s = sim(text, json_lines[k]["text"])
                if s > best_s:
                    best_k, best_s = k, s
            if best_s >= 0.55:
                for k in range(j, best_k):
                    out.append({"type": "line", "speaker": json_lines[k]["speaker"],
                                "text": json_lines[k]["text"], "frame": None, "t": None})
                out.append({"type": "stage", "speaker": "", "text": json_lines[best_k]["text"], "frame": frame, "t": t})
                last_idx, last_json = len(out) - 1, json_lines[best_k]["text"]; j = best_k + 1
            else:
                out.append({"type": "stage", "speaker": "", "text": text, "frame": frame, "t": t})
                last_idx, last_json = None, None
            continue
        if last_json is not None:
            s_prev = sim(text, last_json)
            s_next = sim(text, json_lines[j]["text"]) if j < len(json_lines) else 0.0
            if s_prev >= 0.85 and s_prev > s_next:
                out[last_idx]["frame"] = frame; out[last_idx]["t"] = t; continue
        best_k, best_s = -1, 0.0
        for k in range(j, min(j + 12, len(json_lines))):
            s = sim(text, json_lines[k]["text"])
            if s > best_s:
                best_k, best_s = k, s
        if best_s >= 0.5:
            for k in range(j, best_k):
                out.append({"type": "line", "speaker": json_lines[k]["speaker"],
                            "text": json_lines[k]["text"], "frame": None, "t": None})
            jl = json_lines[best_k]
            out.append({"type": ("stage" if jl["speaker"] == "ナレーション" else "line"),
                        "speaker": "" if jl["speaker"] == "ナレーション" else jl["speaker"],
                        "text": jl["text"], "frame": frame, "t": t})
            if best_s < 0.7:
                report.append(f"[{sec}] 低類似({best_s:.2f}): CSV「{text[:22]}」/ JSON「{jl['text'][:22]}」")
            last_idx, last_json = len(out) - 1, jl["text"]; j = best_k + 1
        else:
            out.append({"type": "line", "speaker": norm_speaker(sp), "text": text, "frame": frame, "t": t, "csv_only": True})
            report.append(f"[{sec}] JSON未マッチ(CSV採用): {sp}: {text[:36]}")
            last_idx, last_json = None, None
    for k in range(j, len(json_lines)):
        jl = json_lines[k]
        if any(o["type"] in ("line", "stage") and sim(jl["text"], o["text"]) >= 0.85 for o in out[-4:]):
            continue
        out.append({"type": ("stage" if jl["speaker"] == "ナレーション" else "line"),
                    "speaker": "" if jl["speaker"] == "ナレーション" else jl["speaker"],
                    "text": jl["text"], "frame": None, "t": None})
    return out


def dedup(entries):
    out = []
    for e in entries:
        if (out and e["type"] == out[-1]["type"] and e["type"] in ("line", "stage")
                and e.get("speaker") == out[-1].get("speaker") and sim(e["text"], out[-1]["text"]) >= 0.85):
            prev = out[-1]
            out[-1] = e if (e.get("frame") and not prev.get("frame")) else prev
            continue
        out.append(e)
    return out


def main():
    report, result = [], []
    for ev in EVENTS:
        all_rows = list(csv.DictReader(open(FRAMES / ev["csv"] / "dialogues.csv", encoding="utf-8-sig")))
        secs = []
        for sid, tab, title, epl, code, ridx, tfr, start, kind in ev["sections"]:
            entry = {"id": sid, "tab": tab, "title": title, "eplabel": epl,
                     "code": code, "kind": kind, "start_s": start}
            if kind == "mv":
                entry["entries"] = []
                entry["title_frame"] = None
                entry["summary"] = ""
                secs.append(entry); continue
            d, jl = load_json_lines(ev["name"], code)
            entry["summary"] = fix_display(d.get("summary", ""))
            if kind == "logonly":
                ents = [{"type": ("stage" if x["speaker"] == "ナレーション" else "line"),
                         "speaker": "" if x["speaker"] == "ナレーション" else x["speaker"],
                         "text": x["text"], "frame": None, "t": None} for x in jl]
                entry["title_frame"] = None
            else:
                rows = [all_rows[i] for i in ridx]
                ents = merge_section(rows, jl, report, sid)
                ents = dedup(ents)
                entry["title_frame"] = frame_num(all_rows[tfr]["frame_file"])
            for e in ents:
                e["text"] = fix_display(e["text"])
            entry["entries"] = ents
            secs.append(entry)
        result.append({"id": ev["id"], "name": ev["name"], "video": ev["video"], "sections": secs})

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_REPORT.write_text("\n".join(report), encoding="utf-8")
    for ev in result:
        print(f"\n■ {ev['name']} ({ev['video']})")
        for s in ev["sections"]:
            n_shot = sum(1 for e in s["entries"] if e.get("frame"))
            n_no = sum(1 for e in s["entries"] if not e.get("frame"))
            print(f"  {s['id']:6s} {s['kind']:8s} 全{len(s['entries']):3d} shot{n_shot:3d} no-shot{n_no:3d} | {s['tab']} {s['title']}")
    print(f"\nレポート {len(report)}行 -> {OUT_REPORT.name}")


if __name__ == "__main__":
    main()
