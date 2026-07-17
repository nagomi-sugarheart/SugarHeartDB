# -*- coding: utf-8 -*-
"""メモリアルコミュ（デレステ）のCSV×JSONマージスクリプト

1本の動画（YouTube 7bvsgbdut3Q）に全5話が収録されており、5話は選択肢で
「良い知らせ」「悪い知らせ」の2分岐に分かれる（動画には両分岐が順に収録）。

- dialogues.csv : 単一CSV。全話のフレーム・タイムスタンプ・OCRテキスト
- メモリアルコミュ_{code}_log.json : 話ごとの完全セリフ（1,2,3,4,5,5_B）

セクションごとにCSVの行範囲を明示指定して突合する。5話は共通冒頭(139-143)を
両分岐で共有し、良=144-177、悪=178-205 を各分岐固有部分とする。
"""
import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CSV_PATH = Path(r"C:\Users\sawas\Downloads\comm_frames\エピソードコミュ_202607172141\dialogues.csv")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
OUT_DIR = Path(__file__).parent
OUT_JSON = OUT_DIR / "merged_memorial_commu.json"
OUT_REPORT = OUT_DIR / "merge_memorial_report.txt"

# (id, タブ名, JSON code, 話タイトル, 要約, CSV行インデックスのリスト, タイトルカードframe行, 動画開始秒)
SECTIONS = [
    ("1", "第1話", "1", "第1話",
     "ドラマ撮影の現場でスカウトされ、アイドルを目指す",
     list(range(0, 30)), 0, 0),
    ("2", "第2話", "2", "第2話",
     "レッスン初日。全力で挑む心とプロデューサー",
     list(range(30, 58)), 30, 155),
    ("3", "第3話", "3", "第3話",
     "宣材写真とプロフィールの撮影",
     list(range(58, 90)), 58, 388),
    ("4", "第4話", "4", "第4話",
     "初めての仕事はドラマのモブ役。崖っぷちからの再挑戦",
     list(range(90, 139)), 90, 571),
    ("5a", "第5話「良い知らせ」", "5", "第5話 ―― 良い知らせ",
     "観覧車デートと、新しい仕事の知らせ",
     list(range(139, 178)), 139, 908),
    ("5b", "第5話「悪い知らせ」", "5_B", "第5話 ―― 悪い知らせ",
     "出番全カットの悪い知らせ。それでも前を向く心",
     list(range(139, 144)) + list(range(178, 206)), 139, 1173),
]

SPEAKER_NORMALIZE = {
    "プロデューサー": "P",
    "なごみP": "P",
    "なこみP": "P",
    "なし": "ナレーション",
    "不明": "ナレーション",
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


DISPLAY_FIXES = [
    ("〜", "～"),
    ("はあと", "はぁと"),
    ("しゅかー", "しゅがー"),
    ("しゅか", "しゅが"),
]


def fix_display(s):
    s = re.sub(r"\s+", " ", s or "").strip()
    for a, b in DISPLAY_FIXES:
        s = s.replace(a, b)
    if s.startswith("(") and s.endswith(")"):
        s = "（" + s[1:-1] + "）"
    return s


def load_json_lines(code):
    p = JSON_DIR / f"メモリアルコミュ_{code}_log.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    lines = []
    for c in d["conversation"]:
        sp, dg = c["speaker"].strip(), c["dialogue"].strip()
        if sp == dg:
            lines.append({"speaker": "ナレーション", "text": dg})
            continue
        sp = norm_speaker(sp)
        if sp == "ナレーション":
            lines.append({"speaker": "ナレーション", "text": dg})
        else:
            lines.append({"speaker": sp, "text": dg})
    return d, lines


def frame_num(frame_file):
    m = re.match(r"(\d+)", frame_file or "")
    return m.group(1) if m else None


def classify_csv_row(r):
    sp = r["speaker"].strip()
    dg = r["dialogue"].strip()
    ct = r["center_text"].strip()
    if not sp and not dg and not ct:
        return ("empty", None, None)
    if not sp and ct and not dg:
        return ("scene", "", ct)
    if not sp and dg:
        return ("stage", "", dg)
    return ("line", norm_speaker(sp), dg)


def merge_section(csv_rows, json_lines, report, sec):
    out = []
    j = 0
    last_idx = None
    last_json = None

    for r in csv_rows:
        typ, sp, text = classify_csv_row(r)
        frame = frame_num(r["frame_file"])
        t = float(r["timestamp_s"])
        if typ == "empty":
            continue
        if typ == "scene":
            out.append({"type": "scene", "speaker": "", "text": text, "frame": frame, "t": t})
            continue
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
                    report.append(f"[{sec}] shotなし(JSONのみ): {json_lines[k]['speaker']}: {json_lines[k]['text'][:30]}")
                out.append({"type": "stage", "speaker": "", "text": json_lines[best_k]["text"],
                            "frame": frame, "t": t})
                last_idx, last_json = len(out) - 1, json_lines[best_k]["text"]
                j = best_k + 1
            else:
                out.append({"type": "stage", "speaker": "", "text": text, "frame": frame, "t": t})
                last_idx, last_json = None, None
            continue

        # line 行
        if last_json is not None:
            s_prev = sim(text, last_json)
            s_next = sim(text, json_lines[j]["text"]) if j < len(json_lines) else 0.0
            if s_prev >= 0.85 and s_prev > s_next:
                out[last_idx]["frame"] = frame
                out[last_idx]["t"] = t
                continue

        best_k, best_s = -1, 0.0
        for k in range(j, min(j + 12, len(json_lines))):
            s = sim(text, json_lines[k]["text"])
            if s > best_s:
                best_k, best_s = k, s
        if best_s >= 0.5:
            for k in range(j, best_k):
                out.append({"type": "line", "speaker": json_lines[k]["speaker"],
                            "text": json_lines[k]["text"], "frame": None, "t": None})
                report.append(f"[{sec}] shotなし(JSONのみ): {json_lines[k]['speaker']}: {json_lines[k]['text'][:30]}")
            jl = json_lines[best_k]
            out.append({"type": ("stage" if jl["speaker"] == "ナレーション" else "line"),
                        "speaker": "" if jl["speaker"] == "ナレーション" else jl["speaker"],
                        "text": jl["text"], "frame": frame, "t": t})
            if best_s < 0.7:
                report.append(f"[{sec}] 低類似({best_s:.2f}): CSV「{text[:25]}」/ JSON「{jl['text'][:25]}」")
            last_idx, last_json = len(out) - 1, jl["text"]
            j = best_k + 1
        else:
            out.append({"type": "line", "speaker": norm_speaker(sp), "text": text,
                        "frame": frame, "t": t, "csv_only": True})
            report.append(f"[{sec}] JSON未マッチ(CSV採用): {sp}: {text[:40]}")
            last_idx, last_json = None, None

    for k in range(j, len(json_lines)):
        jl = json_lines[k]
        if any(o["type"] in ("line", "stage") and sim(jl["text"], o["text"]) >= 0.85
               for o in out[-4:]):
            report.append(f"[{sec}] 末尾重複除外: {jl['speaker']}: {jl['text'][:20]}")
            continue
        out.append({"type": ("stage" if jl["speaker"] == "ナレーション" else "line"),
                    "speaker": "" if jl["speaker"] == "ナレーション" else jl["speaker"],
                    "text": jl["text"], "frame": None, "t": None})
        report.append(f"[{sec}] shotなし(JSON末尾): {jl['speaker']}: {jl['text'][:30]}")
    return out


def dedup_adjacent(entries, report, sec):
    out = []
    for e in entries:
        if (out and e["type"] == out[-1]["type"] and e["type"] in ("line", "stage")
                and e.get("speaker") == out[-1].get("speaker")
                and sim(e["text"], out[-1]["text"]) >= 0.85):
            prev = out[-1]
            keep = e if (e.get("frame") and not prev.get("frame")) else prev
            report.append(f"[{sec}] 重複統合: 「{e['text'][:20]}」")
            out[-1] = keep
            continue
        out.append(e)
    return out


def main():
    report = []
    result = []
    all_rows = list(csv.DictReader(open(CSV_PATH, encoding="utf-8-sig")))

    for sid, tab, code, title, summary, row_idx, tf_row, start_s in SECTIONS:
        rows = [all_rows[i] for i in row_idx]
        d, jl = load_json_lines(code)
        title_frame = frame_num(all_rows[tf_row]["frame_file"])
        entries = merge_section(rows, jl, report, sid)
        entries = dedup_adjacent(entries, report, sid)
        for e in entries:
            e["text"] = fix_display(e["text"])
        result.append({
            "id": sid, "tab": tab, "code": code, "title": title,
            "summary": summary, "title_frame": title_frame,
            "start_s": start_s, "entries": entries,
        })

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_REPORT.write_text("\n".join(report), encoding="utf-8")

    for sec in result:
        n_shot = sum(1 for e in sec["entries"] if e.get("frame"))
        n_noshot = sum(1 for e in sec["entries"] if not e.get("frame"))
        n_csv = sum(1 for e in sec["entries"] if e.get("csv_only"))
        print(f"{sec['id']:4s} 全{len(sec['entries']):3d}行 shot付{n_shot:3d} shotなし{n_noshot:3d} CSVのみ{n_csv:2d} | {sec['tab']}")
    print(f"\nレポート {len(report)}行 -> {OUT_REPORT.name}")


if __name__ == "__main__":
    main()
