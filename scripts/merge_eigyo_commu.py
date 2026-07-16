# -*- coding: utf-8 -*-
"""営業コミュ（デレステ）のCSV×JSONマージスクリプト

各営業コミュは1話完結（ログの episode_code は "OP" だが実態は1話のみ）。
- dialogues.csv : スクショのフレーム・タイムスタンプ・OCRテキストを保持
- *_OP_log.json  : 完全なセリフテキスト・タイトル・要約を保持（正データ）

両者を順序を保ちながら突合し、タブ生成用の merged_eigyo_commu.json と
突合レポート merge_eigyo_report.txt を出力する。

CSVの1行目は各営業の「エリア/地名カード」（center_text=地名, speaker空）で、
これをタイトルカード画像＆地名として扱い、本文からは除外する。
"""
import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

FRAMES_ROOT = Path(r"C:\Users\sawas\Downloads\comm_frames")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
OUT_DIR = Path(__file__).parent
OUT_JSON = OUT_DIR / "merged_eigyo_commu.json"
OUT_REPORT = OUT_DIR / "merge_eigyo_report.txt"

# (id, タブ名/タイトル, フォルダ名, JSONプレフィックス, エリア, 実装日, YouTube ID, Cloudinary用ID)
EIGYO = [
    ("akushu", "しゅがみんと握手！", "しゅがみんと握手！_202607152311",
     "しゅがみんと握手！", "北東", "2018/12/28", "GCLrn08az68", "ShugaminToAkushu"),
    ("kibou", "希望を歌う少女・異世界編", "希望を歌う少女・異世界編_202607152311",
     "希望を歌う少女・異世界編", "中央", "2019/04/12", "0PXHNCxi8cM", "KibouWoUtauShoujo"),
    ("nangoku", "キラキラ☆南国のふたり", "キラキラ☆南国のふたり_202607162038",
     "キラキラ☆南国のふたり", "南", "2019/05/08", "pv96Lqwxoxc", "KirakiraNangoku"),
    ("fukkura", "外はしっかり、中はふっくら", "外はしっかり、中はふっくら_202607162037",
     "外はしっかり、中はふっくら", "首都", "2019/10/11", "hF_2Y902JSA", "SotowaShikkari"),
    ("gaisen", "しゅがみんの凱旋LIVE！", "しゅがみんの凱旋LIVE！_202607152119",
     "しゅがみんの凱旋LIVE！", "中央", "2020/02/10", "GWtXivnVGm4", "ShugaminGaisenLive"),
    ("oshinobi", "しゅがみんとお忍び！", "しゅがみんとお忍び！_202607152119",
     "しゅがみんとお忍び！", "南", "2024/10/28", "rODmqNVocLA", "ShugaminToOshinobi"),
]

# 主要な出演キャラ（無言ビート救済・地の文誤判定回避用）
KNOWN_SPEAKERS = {"心", "菜々", "P", "ファン", "はぁと", "一同", "唯"}

SPEAKER_NORMALIZE = {
    "プロデューサー": "P",
    "なごみP": "P",
    "不明": "ナレーション",
}


def norm_speaker(s):
    return SPEAKER_NORMALIZE.get(s.strip(), s.strip())


def norm_text(s):
    s = re.sub(r"\s+", "", s)
    for ch in "…‥・！？♪☆★♡―ー『』「」（）()、。,.":
        s = s.replace(ch, "")
    s = s.replace("！", "!").replace("？", "?")
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
]


def fix_display(s):
    s = re.sub(r"\s+", " ", s).strip()
    for a, b in DISPLAY_FIXES:
        s = s.replace(a, b)
    if s.startswith("(") and s.endswith(")"):
        s = "（" + s[1:-1] + "）"
    return s


def load_json_lines(prefix):
    p = JSON_DIR / f"{prefix}_OP_log.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    lines = []
    for c in d["conversation"]:
        sp, dg = c["speaker"].strip(), c["dialogue"].strip()
        if sp == dg:
            # ナレーション（speaker欄に本文が重複）→ 地の文として1行に
            lines.append({"speaker": "ナレーション", "text": dg})
            continue
        sp = norm_speaker(sp)
        if sp == "ナレーション":
            lines.append({"speaker": "ナレーション", "text": dg})
        else:
            lines.append({"speaker": sp, "text": dg})
    return d, lines


def classify_csv_row(r):
    sp = r["speaker"].strip()
    dg = r["dialogue"].strip()
    ct = r["center_text"].strip()
    if not sp and not dg and not ct:
        return ("empty", None, None)
    if not sp and ct and not dg:
        # center_textのみ = 地名/シーンカード。短く句読点なしなら scene 扱い
        return ("scene", "", ct)
    if not sp and dg:
        return ("stage", "", dg)
    return ("line", norm_speaker(sp), dg)


def merge_section(csv_rows, json_lines, report, sec):
    """CSV行とJSON行を順序を保ちながら突合。テキストはJSON(正データ)を優先採用。"""
    out = []
    j = 0
    last_idx = None
    last_json = None

    for r in csv_rows:
        typ, sp, text = classify_csv_row(r)
        frame = r["frame_file"]
        t = float(r["timestamp_s"])
        if typ == "empty":
            continue
        if typ == "scene":
            out.append({"type": "scene", "speaker": "", "text": text, "frame": frame, "t": t})
            continue
        if typ == "stage":
            # 地の文: JSONのナレーション行にマッチすればそちらを採用
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

        # --- line 行 ---
        # 直前マッチ行の続きフレーム（途中→完全表示）か？
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

    # 残ったJSON行
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

    for sid, title, folder, prefix, area, date, yt, pid in EIGYO:
        csv_path = FRAMES_ROOT / folder / "dialogues.csv"
        with open(csv_path, encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        d, jl = load_json_lines(prefix)

        # 1行目 = エリア/地名カード
        title_frame = rows[0]["frame_file"]
        area_label = rows[0]["center_text"].strip()
        entries = merge_section(rows[1:], jl, report, sid)

        entries = dedup_adjacent(entries, report, sid)
        for e in entries:
            e["text"] = fix_display(e["text"])

        result.append({
            "id": sid, "tab": title, "title": title,
            "area": area, "date": date, "youtube": yt, "pid": pid,
            "area_label": area_label,
            "summary": fix_display(d.get("summary", "")),
            "title_frame": title_frame,
            "folder": folder,
            "entries": entries,
        })

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_REPORT.write_text("\n".join(report), encoding="utf-8")

    for sec in result:
        n_shot = sum(1 for e in sec["entries"] if e.get("frame"))
        n_noshot = sum(1 for e in sec["entries"] if not e.get("frame"))
        n_csv = sum(1 for e in sec["entries"] if e.get("csv_only"))
        print(f"{sec['id']:9s} 全{len(sec['entries']):3d}行 shot付{n_shot:3d} shotなし{n_noshot:3d} CSVのみ{n_csv} | {sec['tab']}")
    print(f"\nレポート {len(report)}行 -> {OUT_REPORT.name}")


if __name__ == "__main__":
    main()
