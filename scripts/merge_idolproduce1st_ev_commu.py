# -*- coding: utf-8 -*-
"""第1回 アイドルプロデュース 予告/OP/EDコミュのCSV×JSONマージスクリプト

- dialogues.csv: スクショのフレーム・タイムスタンプ・センターテキストを保持
- *_log.json:    完全なセリフテキスト・タイトル・要約を保持

両者を突合し、タブ生成用のマージ済みJSON (merged_idolproduce1st_ev_commu.json) と
突合レポート (merge_idolproduce1st_ev_report.txt) を出力する。

CSVの行33（セリフ視聴確認）は心の絆Lv達成セリフ視聴部分のため対象外
（ログに含まれず、ページの絆Lvタブに収録済み）。
"""
import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CSV_PATH = Path(r"C:\Users\sawas\Downloads\comm_frames\アイプロ_202607091906\dialogues.csv")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
JSON_PREFIX = "第1回 アイドルプロデュース"
OUT_DIR = Path(__file__).parent
OUT_JSON = OUT_DIR / "merged_idolproduce1st_ev_commu.json"
OUT_REPORT = OUT_DIR / "merge_idolproduce1st_ev_report.txt"

LOCATIONS = {"事務所"}

# センターテキストのみでPのセリフとして扱うもの
P_CENTER_LINES = set()

SPEAKER_NORMALIZE = {
    "プロデューサー": "P",
    "なごみP": "P",
    "なこみP": "P",
}


def norm_speaker(s):
    return SPEAKER_NORMALIZE.get(s.strip(), s.strip())


def norm_text(s):
    """比較用の正規化"""
    s = re.sub(r"\s+", "", s)
    s = s.replace("…", "").replace("‥", "").replace("・", "")
    s = s.replace("！", "!").replace("？", "?").replace("♪", "").replace("☆", "")
    s = s.replace("―", "").replace("ー", "")
    s = s.replace("『", "").replace("』", "").replace("「", "").replace("」", "")
    s = s.replace("（", "").replace("）", "").replace("(", "").replace(")", "")
    s = s.replace("、", "").replace("。", "").replace(",", "").replace(".", "")
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
    # CSV側が途中フレーム（前方一致）の場合を救済
    if nb.startswith(na) or na.startswith(nb):
        r = max(r, 0.9)
    # CSV側がセリフ後半のみ表示のフレーム（後方一致）の場合を救済
    # （ログ側OCR揺れがあっても拾えるよう末尾部分との類似で判定）
    if len(nb) > len(na) >= 6:
        sr = SequenceMatcher(None, na, nb[-(len(na) + 2):]).ratio()
        if sr >= 0.75:
            r = max(r, sr)
    # 途中フレームでOCR揺れがある場合: JSON側の先頭部分と比較
    if len(nb) > len(na) >= 4:
        pr = SequenceMatcher(None, na, nb[: len(na) + 2]).ratio()
        if pr >= 0.75:
            r = max(r, pr)
    return r


# 表示テキストの正規化（OCR起因の誤りと表記ゆれの修正）
DISPLAY_FIXES = [
    ("〜", "～"),
    ("しゅかしゅが", "しゅがしゅが"),
    ("バイセン", "パイセン"),
    ("はあと", "はぁと"),
    ("............", "…………"),
    # ログ画像との照合で確認（JSONは括弧欠落・長音がOCR揺れ）
    ("しゅがしゅが☆みーんは夢と希望", "『しゅがしゅが☆み～ん』は夢と希望"),
]


def fix_display(s):
    s = re.sub(r"\s+", " ", s).strip()
    for a, b in DISPLAY_FIXES:
        s = s.replace(a, b)
    s = re.sub(r"^\(", "（", s)
    s = re.sub(r"\)$", "）", s)
    return s


# ゲーム内では2つのセリフボックスだがログJSONでは1行に結合されているもの
# （ログ画像と照合して確認済み）。{(code, 行index): 分割マーカー} — マーカーの直前で分割する
MERGED_LOG_SPLITS = {
    ("ED", 7): "だからここで",
    ("ED", 8): "パイセンが永遠の",
    ("ED", 10): "ラスト一発",
    ("ED", 13): "～完～",  # このログのみ全角チルダ表記
    ("ED", 16): "でもでも、",
}


def load_json_lines(code):
    p = JSON_DIR / f"{JSON_PREFIX}_{code}_log.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    lines = []
    for i, c in enumerate(d["conversation"]):
        sp, dg = c["speaker"].strip(), c["dialogue"].strip()
        dg = dg.replace("バイセン", "パイセン")  # ログOCRの頻出誤り（突合・分割前に正規化）
        if sp.startswith("（") and not dg:
            lines.append({"speaker": "ナレーション", "text": sp})
            continue
        marker = MERGED_LOG_SPLITS.get((code, i))
        if marker and marker in dg:
            pos = dg.index(marker)
            lines.append({"speaker": norm_speaker(sp), "text": dg[:pos].strip()})
            lines.append({"speaker": norm_speaker(sp), "text": dg[pos:].strip()})
        else:
            lines.append({"speaker": norm_speaker(sp), "text": dg})
    return d, lines


def classify_csv_row(r):
    sp, dg, ct = r["speaker"].strip(), r["dialogue"].strip(), r["center_text"].strip()
    if not sp and not dg and not ct:
        return ("empty", None, None)
    if not sp and ct and not dg:
        if ct in LOCATIONS:
            return ("scene", "", ct)
        if ct in P_CENTER_LINES:
            return ("line", "P", ct)
        return ("header", "", ct)  # 話タイトルカード等
    if not sp and dg:
        # 地の文（菜々たちが、楽しそう？に話している…… 等）
        return ("stage", "", dg)
    return ("line", norm_speaker(sp), dg)


def merge_section(csv_rows, json_lines, report, sec_name):
    """CSV行とJSON行を順序を保ちながら突合する"""
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

        # --- dialogue 行 ---
        # ゲーム内で選択・表示されるプロデューサーの短文はログに存在しないため突合しない
        # （「なごみP」名義のセリフはログに含まれるので通常どおり突合する）
        if r["speaker"].strip() == "プロデューサー":
            out.append({"type": "line", "speaker": "P", "text": text,
                        "frame": frame, "t": t, "csv_only": True})
            report.append(f"[{sec_name}] P行(CSVのみ採用): no{r['no']} {text[:40]}")
            continue

        # 直前にマッチしたJSON行の続きフレームか？（途中→完全表示）
        if last_matched_json is not None:
            s_prev = sim(text, last_matched_json)
            s_next = sim(text, json_lines[j]["text"]) if j < len(json_lines) else 0.0
            if s_prev >= 0.85 and s_prev > s_next:
                out[last_matched_idx]["frame"] = frame
                out[last_matched_idx]["t"] = t
                # より完全なCSVテキストなら差し替え（フレームOCRの方が高品質）
                if len(norm_text(text)) >= len(norm_text(out[last_matched_idx]["text"])) - 2:
                    out[last_matched_idx]["text"] = text
                continue

        # 次の数行から最良マッチを探す
        # （このイベントはEDでshotなし行が6行連続するため先読み窓は広めにとる）
        best_k, best_s = -1, 0.0
        for k in range(j, min(j + 10, len(json_lines))):
            s = sim(text, json_lines[k]["text"])
            if s > best_s:
                best_k, best_s = k, s
        if best_s >= 0.55:
            if out and out[-1].get("csv_only") and out[-1]["speaker"] != "P" \
                    and sim(out[-1]["text"], json_lines[best_k]["text"]) >= 0.6:
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
        out.append({"type": "line", "speaker": json_lines[k]["speaker"],
                    "text": json_lines[k]["text"], "frame": None, "t": None})
        report.append(f"[{sec_name}] shotなし(JSON末尾): {json_lines[k]['speaker']}: {json_lines[k]['text'][:30]}")
    return out


def main():
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    def rows_between(a, b):
        return [r for r in rows if a <= int(r["no"]) <= b]

    # 再生開始秒: 各話の開始 = 直前セリフの完了時刻（タイトルカード表示開始）。
    # 予告は動画冒頭（0）から。EDの直前は絆Lv達成セリフ視聴部分（対象外）のため、
    # EDタイトルカード完全表示(457.2)の少し手前から。
    sections = [
        # (タブID, タブ名, JSONコード(複数可), CSV行範囲, 再生開始秒)
        ("trailer", "予告", ["Tr1", "Tr2"], (1, 7), 0),
        ("op", "OP", ["OP"], (8, 32), 209),
        ("ed", "ED", ["ED"], (34, 83), 454),
    ]

    report = []
    result = []
    for tab_id, tab_name, codes, (a, b), start_s in sections:
        sec_rows = rows_between(a, b)
        if tab_id == "trailer":
            # 予告タブ: イベント告知(行1) + 予告1(行2-4) + 予告2(行5-7)
            entries = []
            r1 = rows[0]
            entries.append({"type": "sub", "speaker": "", "text": "イベント告知",
                            "frame": r1["frame_file"], "t": float(r1["timestamp_s"])})
            entries.append({"type": "stage", "speaker": "", "text": r1["center_text"].strip(),
                            "frame": r1["frame_file"], "t": float(r1["timestamp_s"])})
            for code, (ra, rb) in [("Tr1", (2, 4)), ("Tr2", (5, 7))]:
                d, jl = load_json_lines(code)
                sub_rows = rows_between(ra, rb)
                entries.append({"type": "sub", "speaker": "", "text": d["episode"],
                                "frame": sub_rows[0]["frame_file"], "t": float(sub_rows[0]["timestamp_s"])})
                entries += merge_section(sub_rows[1:], jl, report, code)
            result.append({"id": tab_id, "tab": tab_name, "title": "予告",
                           "summary": "", "start_s": start_s,
                           "title_frame": rows[1]["frame_file"], "log": ["Tr1", "Tr2"],
                           "entries": entries})
        else:
            code = codes[0]
            d, jl = load_json_lines(code)
            header_row = sec_rows[0]
            entries = merge_section(sec_rows[1:], jl, report, code)
            result.append({"id": tab_id, "tab": tab_name,
                           "title": d["title"], "summary": d["summary"],
                           "start_s": start_s, "title_frame": header_row["frame_file"],
                           "log": [code], "entries": entries})

    for sec in result:
        sec["title"] = fix_display(sec["title"])
        sec["summary"] = fix_display(sec["summary"])
        for e in sec["entries"]:
            e["text"] = fix_display(e["text"])

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
