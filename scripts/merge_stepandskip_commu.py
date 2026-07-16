# -*- coding: utf-8 -*-
"""ステップ＆スキップ ゲストコミュのCSV×JSONマージスクリプト

- dialogues.csv: スクショのフレーム・タイムスタンプ・センターテキストを保持
- *_log.json:    完全なセリフテキスト・タイトル・要約を保持

両者を突合し、タブ生成用のマージ済みJSON (merged_stepandskip_commu.json) と
突合レポート (merge_stepandskip_report.txt) を出力する。

【本コミュ固有の事情】
- 佐藤心はゲスト参加（主役はワンステップス＝乃々・ほたる・裕美）。予告・報酬・楽曲MVは無い。
- OP/2話/3話/EDには英語タイトルカードが映像にある（center_text）。1話/4話/5話には無いため、
  各話先頭のフレーム（場所カードまたは先頭セリフ）を title_frame に使う。
"""
import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CSV_PATH = Path(r"C:\Users\sawas\Downloads\comm_frames\ステップ＆スキップ_202607162248\dialogues.csv")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
JSON_PREFIX = "ステップ＆スキップ"
OUT_DIR = Path(__file__).parent
OUT_JSON = OUT_DIR / "merged_stepandskip_commu.json"
OUT_REPORT = OUT_DIR / "merge_stepandskip_report.txt"


def ws(s):
    return re.sub(r"\s+", "", s or "")


# 場所・時制を示すセンターテキスト（話者なしのシーン表示）。空白除去で比較する。
LOCATIONS = {ws(x) for x in {
    "数分後", "翌日", "事務所", "河川敷", "街中", "LIVE会場", "舞台裏", "MV撮影、本番",
}}

# センターテキストのみでPのセリフとして扱うもの（Pの中央表示セリフ）。空白除去で比較する。
P_CENTER_LINES = {ws(x) for x in {
    "今日は、頑張った3人へのご褒美だよ",
    "乃々、ホルモン焼けてるよ",
    "ミニLIVEもやるよ",
    "大丈夫みたいだよ",
    "今日は、よろしくお願いします",
    "それは……",
    "今回は、焼肉は無しだよ",
    "じゃあ、頑張ったご褒美に…",
}}

SPEAKER_NORMALIZE = {
    "プロデューサー": "P",
    "なごみP": "P",
    "なこみP": "P",
    "なごみＰ": "P",
    "なこみＰ": "P",
    "Ｐ": "P",
    "佐藤心": "心",
    "森久保乃々": "乃々",
    "白菊ほたる": "ほたる",
    "関裕美": "裕美",
    "三船美優": "美優",
}

# 出演キャラ（掛け合いのセンター話者判定・自己名ナレーション誤判定除外に使う）
KNOWN_SPEAKERS = {"乃々", "ほたる", "裕美", "心", "美優", "P"}


def norm_speaker(s):
    return SPEAKER_NORMALIZE.get(s.strip(), s.strip())


def norm_text(s):
    s = re.sub(r"\s+", "", s)
    s = s.replace("…", "").replace("‥", "").replace("・", "")
    s = s.replace("！", "!").replace("？", "?").replace("♪", "").replace("☆", "")
    s = s.replace("★", "").replace("♡", "")
    s = s.replace("―", "").replace("ー", "")
    s = s.replace("『", "").replace("』", "").replace("「", "").replace("」", "")
    s = s.replace("（", "").replace("）", "").replace("(", "").replace(")", "")
    s = s.replace("、", "").replace("。", "").replace(",", "").replace(".", "")
    return s


def is_ellipsis_only(s):
    return bool(s) and not norm_text(s) and bool(re.fullmatch(r"[…‥.。、・\s]+", s))


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


# 表示テキストの正規化（OCR起因の誤りと表記ゆれの修正）
DISPLAY_FIXES = [
    ("〜", "～"),
    # 心の一人称「はぁと」のOCR欠落（フレーム目視で確認）
    ("人生経験豊富なあとお姉さん", "人生経験豊富なはぁとお姉さん"),
    ("はぁたちにも何か", "はぁとたちにも何か"),
]


def fix_display(s):
    s = re.sub(r"[ \t]+", " ", s).strip()
    for a, b in DISPLAY_FIXES:
        s = s.replace(a, b)
    if s.startswith("(") and s.endswith(")"):
        s = "（" + s[1:-1] + "）"
    return s


def load_json_lines(code):
    p = JSON_DIR / f"{JSON_PREFIX}_{code}_log.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    lines = []
    for c in d["conversation"]:
        sp, dg = c["speaker"].strip(), c["dialogue"].strip()
        if sp == dg:
            continue
        if sp in ("（テキストなし）", "（なし）", "ナレーション", "（地の文）", "（ナレーション）"):
            lines.append({"speaker": "ナレーション", "text": dg or sp})
        elif sp.startswith("（") and not dg:
            lines.append({"speaker": "ナレーション", "text": sp})
        elif dg.startswith(sp) and len(sp) <= 4 and sp not in KNOWN_SPEAKERS:
            lines.append({"speaker": "ナレーション", "text": dg})
        else:
            lines.append({"speaker": norm_speaker(sp), "text": dg})
    return d, lines


def all_known(names):
    parts = [t for t in re.split(r"[・&]", names) if t]
    return parts and all(norm_speaker(t) in KNOWN_SPEAKERS for t in parts)


def classify_csv_row(r):
    sp, dg, ct = r["speaker"].strip(), r["dialogue"].strip(), r["center_text"].strip()
    if not sp and not dg and not ct:
        return ("empty", None, None)
    if not sp and ct and not dg:
        key = ws(ct)
        if key in LOCATIONS:
            return ("scene", "", ct.replace("\n", " ").strip())
        if key in P_CENTER_LINES:
            return ("line", "P", ct.replace("\n", " ").strip())
        # 「話者名 セリフ」形式の掛け合いセンター（例: ほたる・乃々・裕美 ステップ！）
        m = re.match(r"^([^\s　]+)[\s　]+(.+)$", ct.replace("\n", " ").strip())
        if m and all_known(m.group(1)) and norm_text(m.group(2)):
            return ("line", norm_speaker(m.group(1)), m.group(2).strip())
        return ("header", "", ct.replace("\n", " ").strip())
    if sp and not dg and ct:
        return ("line", norm_speaker(sp), ct)
    if not sp and dg:
        m = re.match(r"^([^\s　]+?)[\s　]+([・…‥\.。]{3,})$", dg)
        if m and all_known(m.group(1)):
            return ("line", m.group(1), "……")
        return ("stage", "", dg)
    if (sp and dg and ct and ct != dg and len(ct) <= 12
            and not any(ch in ct for ch in "!！?？。、")
            and all_known(ct)):
        return ("line", norm_speaker(ct), dg)
    return ("line", norm_speaker(sp), dg)


def merge_section(csv_rows, json_lines, report, sec_name):
    out = []
    j = 0
    last_matched_idx = None
    last_matched_json = None

    for r in csv_rows:
        typ, sp, text = classify_csv_row(r)
        frame = r["frame_file"]
        t = float(r["timestamp_s"])
        if typ == "empty":
            continue
        if typ in ("scene", "stage"):
            out.append({"type": typ, "speaker": "", "text": text, "frame": frame, "t": t})
            continue
        if typ == "header":
            report.append(f"[{sec_name}] ヘッダ扱い: no{r['no']} {text}")
            out.append({"type": "header", "speaker": "", "text": text, "frame": frame, "t": t})
            continue

        if sp == "P":
            best_k, best_s = -1, 0.0
            for k in range(j, min(j + 8, len(json_lines))):
                if json_lines[k]["speaker"] != "P":
                    continue
                s = sim(text, json_lines[k]["text"])
                if s > best_s:
                    best_k, best_s = k, s
            if best_s >= 0.7:
                for k in range(j, best_k):
                    out.append({"type": "line", "speaker": json_lines[k]["speaker"],
                                "text": json_lines[k]["text"], "frame": None, "t": None})
                    report.append(f"[{sec_name}] shotなし(JSONのみ): {json_lines[k]['speaker']}: {json_lines[k]['text'][:30]}")
                out.append({"type": "line", "speaker": "P", "text": text, "frame": frame, "t": t})
                last_matched_idx = len(out) - 1
                last_matched_json = json_lines[best_k]["text"]
                j = best_k + 1
            else:
                out.append({"type": "line", "speaker": "P", "text": text,
                            "frame": frame, "t": t, "csv_only": True})
                report.append(f"[{sec_name}] Pセリフ(CSVのみ): no{r['no']} {text[:40]}")
                last_matched_idx = None
                last_matched_json = None
            continue

        if last_matched_json is not None:
            s_prev = sim(text, last_matched_json)
            s_next = sim(text, json_lines[j]["text"]) if j < len(json_lines) else 0.0
            if s_prev >= 0.85 and s_prev > s_next:
                out[last_matched_idx]["frame"] = frame
                out[last_matched_idx]["t"] = t
                continue

        best_k, best_s = -1, 0.0
        for k in range(j, min(j + 6, len(json_lines))):
            s = sim(text, json_lines[k]["text"])
            if s > best_s:
                best_k, best_s = k, s
        if best_s < 0.55:
            fb_k, fb_s = -1, 0.0
            for k in range(j, min(j + 25, len(json_lines))):
                s = sim(text, json_lines[k]["text"])
                if s > fb_s:
                    fb_k, fb_s = k, s
            if fb_s >= 0.72:
                best_k, best_s = fb_k, fb_s
        if best_s >= 0.55:
            if out and out[-1].get("csv_only") and sim(out[-1]["text"], json_lines[best_k]["text"]) >= 0.6:
                report.append(f"[{sec_name}] 途中フレーム除去: 「{out[-1]['text'][:20]}」")
                out.pop()
            for k in range(j, best_k):
                out.append({"type": "line", "speaker": json_lines[k]["speaker"],
                            "text": json_lines[k]["text"], "frame": None, "t": None})
                report.append(f"[{sec_name}] shotなし(JSONのみ): {json_lines[k]['speaker']}: {json_lines[k]['text'][:30]}")
            jl = json_lines[best_k]
            use_csv = len(norm_text(text)) >= len(norm_text(jl["text"])) - 2
            out.append({"type": "line", "speaker": jl["speaker"] or norm_speaker(sp),
                        "text": text if use_csv else jl["text"], "frame": frame, "t": t})
            if best_s < 0.75:
                report.append(f"[{sec_name}] 低類似({best_s:.2f}): no{r['no']} CSV「{text[:25]}」/ JSON「{jl['text'][:25]}」")
            last_matched_idx = len(out) - 1
            last_matched_json = jl["text"]
            j = best_k + 1
        else:
            out.append({"type": "line", "speaker": norm_speaker(sp), "text": text,
                        "frame": frame, "t": t, "csv_only": True})
            report.append(f"[{sec_name}] JSON未マッチ(CSVのみ採用): no{r['no']} {sp}: {text[:40]}")

    for k in range(j, len(json_lines)):
        jl = json_lines[k]
        if any(o["type"] in ("line", "stage") and sim(jl["text"], o["text"]) >= 0.85
               for o in out[-4:]):
            report.append(f"[{sec_name}] 末尾重複除外: {jl['speaker']}: {jl['text'][:20]}")
            continue
        out.append({"type": "line", "speaker": jl["speaker"],
                    "text": jl["text"], "frame": None, "t": None})
        report.append(f"[{sec_name}] shotなし(JSON末尾): {jl['speaker']}: {jl['text'][:30]}")
    return out


def dedup_adjacent(entries, report, sec_name):
    out = []
    for e in entries:
        raw_sim = SequenceMatcher(None, e["text"], out[-1]["text"]).ratio() if out else 0.0
        if (out and e["type"] == "line" and out[-1]["type"] == "line"
                and e["speaker"] == out[-1]["speaker"] and e["speaker"]
                and (sim(e["text"], out[-1]["text"]) >= 0.85 or raw_sim >= 0.8)):
            prev = out[-1]
            keep = e if (e.get("frame") and not prev.get("frame")) else prev
            drop = prev if keep is e else e
            report.append(f"[{sec_name}] 重複統合: 「{drop['text'][:20]}」")
            out[-1] = keep
            continue
        out.append(e)
    return out


def main():
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    def rows_between(a, b):
        return [r for r in rows if a <= int(r["no"]) <= b]

    sections = [
        # (タブID, タブ名, JSONコード, CSV行範囲, 再生開始秒, ログ画像コード列)
        ("op",  "OP",   "OP", (1, 62),    0,    ["OP"]),
        ("ep1", "第1話", "1",  (63, 116),  494,  ["1"]),
        ("ep2", "第2話", "2",  (117, 165), 1023, ["2"]),
        ("ep3", "第3話", "3",  (166, 238), 1463, ["3"]),
        ("ep4", "第4話", "4",  (239, 288), 2122, ["4"]),
        ("ep5", "第5話", "5",  (289, 328), 2703, ["5"]),
        ("ed",  "ED",   "ED", (329, 389), 3459, ["ED"]),
    ]

    report = []
    result = []

    for tab_id, tab_name, code, (a, b), start_s, logs in sections:
        d, jl = load_json_lines(code)
        sec_rows = rows_between(a, b)
        first_typ, _, _ = classify_csv_row(sec_rows[0])
        if first_typ in ("scene", "header"):
            title_frame = sec_rows[0]["frame_file"]
            entries = merge_section(sec_rows[1:], jl, report, code)
        else:
            title_frame = sec_rows[0]["frame_file"]
            entries = merge_section(sec_rows, jl, report, code)
        result.append({"id": tab_id, "tab": tab_name,
                       "title": d["title"], "summary": d["summary"],
                       "start_s": start_s, "title_frame": title_frame,
                       "log": logs, "entries": entries})

    for sec in result:
        sec["title"] = fix_display(sec["title"])
        sec["summary"] = fix_display(sec["summary"])
        for e in sec["entries"]:
            e["text"] = fix_display(e["text"])

    for sec in result:
        sec["entries"] = dedup_adjacent(sec["entries"], report, sec["id"])

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_REPORT.write_text("\n".join(report), encoding="utf-8")

    for sec in result:
        n_shot = sum(1 for e in sec["entries"] if e.get("frame"))
        n_noshot = sum(1 for e in sec["entries"] if e["type"] == "line" and not e.get("frame"))
        n_csvonly = sum(1 for e in sec["entries"] if e.get("csv_only"))
        print(f"{sec['tab']}: 全{len(sec['entries'])}行 shot付{n_shot} shotなし{n_noshot} CSVのみ{n_csvonly} | {sec['title']}")
    print(f"\nレポート行数: {len(report)} -> {OUT_REPORT}")


if __name__ == "__main__":
    main()
