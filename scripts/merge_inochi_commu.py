# -*- coding: utf-8 -*-
"""命燃やして恋せよ乙女 イベントコミュのCSV×JSONマージスクリプト

- dialogues.csv: スクショのフレーム・タイムスタンプ・センターテキストを保持
- *_log.json:    完全なセリフテキスト・タイトル・要約を保持

両者を突合し、タブ生成用のマージ済みJSON (merged_inochi_commu.json) と
突合レポート (merge_inochi_report.txt) を出力する。
"""
import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CSV_PATH = Path(r"C:\Users\sawas\Downloads\comm_frames\命燃やして恋せよ乙女_202606220001\dialogues.csv")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
JSON_PREFIX = "命燃やして恋せよ乙女"
OUT_DIR = Path(__file__).parent
OUT_JSON = OUT_DIR / "merged_inochi_commu.json"
OUT_REPORT = OUT_DIR / "merge_inochi_report.txt"

# 場所・シーンを示すセンターテキスト（タイトルカード扱い）
LOCATIONS = {
    "12月 某日・旅館", "合宿所", "レッスン後", "居酒屋", "海沿いの道",
    "TV局 廊下", "TV局 控え室", "宴会場", "乾杯", "数時間後",
}

# センターテキストのみでPのセリフとして扱うもの（今回は無し）
P_CENTER_LINES = set()

SPEAKER_NORMALIZE = {
    "プロデューサー": "P",
    "なごみP": "P",
    "なこみP": "P",
}

# 出演キャラ（自己名で始まるセリフをナレーション誤判定しないための除外集合）
KNOWN_SPEAKERS = {"楓", "早苗", "心", "美優", "菜々", "店主", "P"}


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
    # 途中フレームでOCR揺れがある場合: JSON側の先頭部分と比較
    if len(nb) > len(na) >= 4:
        pr = SequenceMatcher(None, na, nb[: len(na) + 2]).ratio()
        if pr >= 0.75:
            r = max(r, pr)
    return r


# 表示テキストの正規化（OCR起因の誤りと表記ゆれの修正）
DISPLAY_FIXES = [
    ("〜", "～"),
    ("はあと", "はぁと"),
]


def fix_display(s):
    s = re.sub(r"\s+", " ", s).strip()
    for a, b in DISPLAY_FIXES:
        s = s.replace(a, b)
    # 半角括弧→全角（行全体が心の声のときのみ。タイトルの「(17)」等は変換しない）
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
            # ナレーション（OCRがspeaker欄にも本文を格納）。CSVのセンターテキストに
            # 同じ地の文が入っているため、重複を避けてスキップする。
            continue
        if sp.startswith("（") and not dg:
            # ナレーション行（OCRがspeaker欄に格納）
            lines.append({"speaker": "ナレーション", "text": sp})
        elif dg.startswith(sp) and len(sp) <= 4 and sp not in KNOWN_SPEAKERS:
            # 地の文が話者欄に分断混入したケース（例: speaker「宴会」/ dialogue「宴会は長時間に及んだ」）
            lines.append({"speaker": "ナレーション", "text": dg})
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
        return ("header", "", ct)  # 話タイトルカード・地の文の中央表示等
    if not sp and dg:
        # 地の文
        return ("stage", "", dg)
    if (sp and dg and ct and ct != dg and len(ct) <= 12
            and not any(ch in ct for ch in "!！?？。、")):
        # OCRが話者名をcenter_textに入れたケース（複数名の掛け合い等）
        return ("line", norm_speaker(ct), dg)
    return ("line", norm_speaker(sp), dg)


def merge_section(csv_rows, json_lines, report, sec_name):
    """CSV行とJSON行を順序を保ちながら突合する"""
    out = []
    j = 0
    last_matched_idx = None  # out内の直近マッチ行
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
        # Pのセリフは基本ログに無い（選択肢）が、EDのなこみP等ログに登場する場合がある。
        # ログのP話者行に高類似でマッチすれば突合してshotを付け（重複を防ぐ）、
        # 無ければCSVのまま出力する（近い語を含むアイドルのセリフへの誤マージを防ぐため
        # マッチ対象はP話者のJSON行に限定する）。
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
                jl = json_lines[best_k]
                use_csv = len(norm_text(text)) >= len(norm_text(jl["text"])) - 2
                out.append({"type": "line", "speaker": "P",
                            "text": text if use_csv else jl["text"], "frame": frame, "t": t})
                last_matched_idx = len(out) - 1
                last_matched_json = jl["text"]
                j = best_k + 1
            else:
                out.append({"type": "line", "speaker": "P", "text": text,
                            "frame": frame, "t": t, "csv_only": True})
                report.append(f"[{sec_name}] Pセリフ(CSVのみ): no{r['no']} {text[:40]}")
                last_matched_idx = None
                last_matched_json = None
            continue

        # 直前にマッチしたJSON行の続きフレームか？（途中→完全表示）
        if last_matched_json is not None:
            s_prev = sim(text, last_matched_json)
            s_next = sim(text, json_lines[j]["text"]) if j < len(json_lines) else 0.0
            if s_prev >= 0.85 and s_prev > s_next:
                # 同じセリフのより完全なフレーム → shotを差し替え
                out[last_matched_idx]["frame"] = frame
                out[last_matched_idx]["t"] = t
                continue

        # 次の数行から最良マッチを探す
        best_k, best_s = -1, 0.0
        for k in range(j, min(j + 6, len(json_lines))):
            s = sim(text, json_lines[k]["text"])
            if s > best_s:
                best_k, best_s = k, s
        if best_s >= 0.55:
            # 直前のCSVのみ行が同セリフの途中フレームなら除去
            if out and out[-1].get("csv_only") and sim(out[-1]["text"], json_lines[best_k]["text"]) >= 0.6:
                report.append(f"[{sec_name}] 途中フレーム除去: 「{out[-1]['text'][:20]}」")
                out.pop()
            # 飛ばされたJSON行（CSVに無い＝shotなし）を先に出力
            for k in range(j, best_k):
                out.append({"type": "line", "speaker": json_lines[k]["speaker"],
                            "text": json_lines[k]["text"], "frame": None, "t": None})
                report.append(f"[{sec_name}] shotなし(JSONのみ): {json_lines[k]['speaker']}: {json_lines[k]['text'][:30]}")
            jl = json_lines[best_k]
            # CSV側が完全表示ならCSVテキストを優先（フレームOCRの方が高品質）
            use_csv = len(norm_text(text)) >= len(norm_text(jl["text"])) - 2
            out.append({"type": "line", "speaker": jl["speaker"] or norm_speaker(sp),
                        "text": text if use_csv else jl["text"], "frame": frame, "t": t})
            if best_s < 0.75:
                report.append(f"[{sec_name}] 低類似({best_s:.2f}): no{r['no']} CSV「{text[:25]}」/ JSON「{jl['text'][:25]}」")
            last_matched_idx = len(out) - 1
            last_matched_json = jl["text"]
            j = best_k + 1
        else:
            # JSONに存在しない行（Pのセリフ等）→ CSVのまま出力
            out.append({"type": "line", "speaker": norm_speaker(sp), "text": text,
                        "frame": frame, "t": t, "csv_only": True})
            report.append(f"[{sec_name}] JSON未マッチ(CSVのみ採用): no{r['no']} {sp}: {text[:40]}")

    # 残ったJSON行
    for k in range(j, len(json_lines)):
        out.append({"type": "line", "speaker": json_lines[k]["speaker"],
                    "text": json_lines[k]["text"], "frame": None, "t": None})
        report.append(f"[{sec_name}] shotなし(JSON末尾): {json_lines[k]['speaker']}: {json_lines[k]['text'][:30]}")
    return out


def dedup_adjacent(entries, report, sec_name):
    """隣接する同一話者・高類似の重複行を統合（短い相槌のOCR揺れ二重化を解消）。
    shot付きの行を優先して残す。"""
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

    # 再生開始秒: CSVの時刻は「表示されきった時刻」のため、各話の開始は
    # 直前セリフの時刻（＝先頭カードの表示開始）とする。予告は動画冒頭から。
    sections = [
        # (タブID, タブ名, JSONコード, CSV行範囲, 再生開始秒)
        ("op", "OP", "OP", (8, 80), 83),
        ("ep1", "第1話", "1", (81, 122), 645),
        ("ep2", "第2話", "2", (123, 167), 1060),  # ep1末尾のshotなし行を挟むためカード表示は約1060（YouTubeチャプターと一致）
        ("ep3", "第3話", "3", (168, 209), 1358),  # 空フレームでなく実セリフ末尾no166基準（YouTubeチャプターと一致）
        ("ep4", "第4話", "4", (210, 247), 1744),
        ("ep5", "第5話", "5", (248, 286), 2060),
        ("ed", "ED", "ED", (287, 338), 2423),
    ]

    report = []
    result = []

    # --- 予告タブ（予告1: Tr1 / 予告2: Tr2）---
    # no1: 予告1カード, no2-3: 楓(Tr1) / no4: 予告2カード, no5-7: 早苗(Tr2)
    entries = []
    for code, card_no, (ra, rb) in [("Tr1", 1, (2, 3)), ("Tr2", 4, (5, 7))]:
        d, jl = load_json_lines(code)
        card = rows_between(card_no, card_no)[0]
        entries.append({"type": "sub", "speaker": "", "text": d["episode"],
                        "frame": card["frame_file"], "t": float(card["timestamp_s"])})
        entries += merge_section(rows_between(ra, rb), jl, report, code)
    result.append({"id": "trailer", "tab": "予告", "title": "予告",
                   "summary": "", "start_s": 0,
                   "title_frame": rows_between(1, 1)[0]["frame_file"], "log": ["Tr1", "Tr2"],
                   "entries": entries})

    # --- OP〜ED ---
    for tab_id, tab_name, code, (a, b), start_s in sections:
        d, jl = load_json_lines(code)
        sec_rows = rows_between(a, b)
        first_typ, _, _ = classify_csv_row(sec_rows[0])
        if first_typ in ("scene", "header"):
            # 先頭が場所カード → タイトルカード画像に使い、本文からは除外
            title_frame = sec_rows[0]["frame_file"]
            entries = merge_section(sec_rows[1:], jl, report, code)
        else:
            # 先頭がセリフ → 先頭フレームを見出し画像に使いつつ本文にも残す
            title_frame = sec_rows[0]["frame_file"]
            entries = merge_section(sec_rows, jl, report, code)
        result.append({"id": tab_id, "tab": tab_name,
                       "title": d["title"], "summary": d["summary"],
                       "start_s": start_s, "title_frame": title_frame,
                       "log": [code], "entries": entries})

    # 表示テキストの正規化（波ダッシュ等を揃えてから重複統合する）
    for sec in result:
        sec["title"] = fix_display(sec["title"])
        sec["summary"] = fix_display(sec["summary"])
        for e in sec["entries"]:
            e["text"] = fix_display(e["text"])

    # 隣接重複の統合
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
