# -*- coding: utf-8 -*-
"""熱情エナモラル イベントコミュのCSV×JSONマージスクリプト

- dialogues.csv: スクショのフレーム・タイムスタンプ・センターテキストを保持
- *_log.json:    完全なセリフテキスト・タイトル・要約を保持

両者を突合し、タブ生成用のマージ済みJSON (merged_netsujou_commu.json) と
突合レポート (merge_netsujou_report.txt) を出力する。

【本イベント固有の事情】
- 歌唱メンバー 依田芳乃・村上巴・佐藤心・夢見りあむ・久川凪 の楽曲『熱情エナモラル』
  タイアップの恋愛即興ドラマ『焦がれる5人』。全8セクション（予告・OP・第1〜5話・ED）。
- 映像に英語タイトルカードは無く、各話タイトルは「エピソード・ワン『…』」等の
  セリフで示される。各話先頭は場所カード（プロデューサー室・事務所のカフェテラス・
  南国？ビーチ等）か先頭セリフを title_frame に使う。
- 第3話のログ（熱情エナモラル_3_log）は当初、誤って第4話（エピソード・フォー
  『寄せては返す女たち』）の複製が保存されていたが、ユーザーから正しい第3話ログ
  （エピソード・スリー『乱れたい女たち』。瀬戸内到着〜企画台本の乱丁発覚〜あべこべの
  役の練習）の提供を受け、G:\マイドライブ\コミュ の 熱情エナモラル_3_log.json/.png を
  正しい内容に差し替えた。よって第3話も他話と同様にログ付きで突合する。
- 複数話者が同時に発話する行は、CSVで話者名がセンターテキスト側に入ることがある
  （例 no185「[凪・芳乃・りあむ] 瀬戸内海一。」）。これを話者付きの line として扱う。
"""
import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CSV_PATH = Path(r"C:\Users\sawas\Downloads\comm_frames\熱情エナモラル_202606282127\dialogues.csv")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
JSON_PREFIX = "熱情エナモラル"
OUT_DIR = Path(__file__).parent
OUT_JSON = OUT_DIR / "merged_netsujou_commu.json"
OUT_REPORT = OUT_DIR / "merge_netsujou_report.txt"

# 場所・時制を示すセンターテキスト（話者なしのシーン表示）
LOCATIONS = {
    "プロデューサー室", "事務所のカフェテラス", "高級レストラン",
    "南国？ビーチ", "南国？リゾート内部", "ホテルへの送迎バス",
}

# センターテキストのみでPのセリフとして扱うもの（Pの中央表示セリフ）
P_CENTER_LINES = set()

SPEAKER_NORMALIZE = {
    "プロデューサー": "P",
    "なごみP": "P",
    "なこみP": "P",
    "なごみＰ": "P",
    "なこみＰ": "P",
    "Ｐ": "P",
    "依田芳乃": "芳乃",
    "村上巴": "巴",
    "佐藤心": "心",
    "夢見りあむ": "りあむ",
    "久川凪": "凪",
}

# 出演キャラ（掛け合いのセンター話者判定・自己名ナレーション誤判定除外に使う）
KNOWN_SPEAKERS = {"芳乃", "巴", "心", "りあむ", "凪", "P"}


def norm_speaker(s):
    return SPEAKER_NORMALIZE.get(s.strip(), s.strip())


def norm_text(s):
    """比較用の正規化"""
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
    ("はあと", "はぁと"),
    ("はあーと", "はぁーと"),
    # 第2話ログの52行目はP「魔女の大鍋…」と巴・心・りあむ「鮭のおかゆ…」の
    # 2行が誤って結合されている。前半のP分を除去し、CSV側のP行（no177）と
    # 巴・心・りあむ行（no178）が正しく別々に出力されるようにする。
    ("腐女の大鍋のようなものが、ぐつぐつ煮え立っている……これは何だろう……？鮭", "鮭"),
    # 第5話 心の笑い声。JSONの濁点付与（ふ→ぶ）とCSVの小書き誤り（っ→つ）を揃え、
    # 同一行として統合されるようにする（重複防止）。
    ("ぶっ……。ぶっぶっぶっぶっ", "ふっ……。ふっふっふっふっ"),
    ("ふつ……。 ふっふっ", "ふっ……。 ふっふっ"),
]


def apply_char_fixes(s):
    for a, b in DISPLAY_FIXES:
        s = s.replace(a, b)
    return s


def fix_display(s):
    s = re.sub(r"\s+", " ", s).strip()
    for a, b in DISPLAY_FIXES:
        s = s.replace(a, b)
    if s.startswith("(") and s.endswith(")"):
        s = "（" + s[1:-1] + "）"
    return s


def load_json_lines(code):
    if code is None:
        return None, []
    p = JSON_DIR / f"{JSON_PREFIX}_{code}_log.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    lines = []
    for c in d["conversation"]:
        sp, dg = c["speaker"].strip(), apply_char_fixes(c["dialogue"].strip())
        # OCRが本文頭にプロデューサー名を取り込んだケースの補正
        mp = re.match(r"^(なこみP|なごみP|プロデューサー|Ｐ)\s+(\S.*)$", dg)
        if mp:
            sp, dg = "P", mp.group(2)
        if sp == dg:
            continue
        if sp in ("（テキストなし）", "（なし）", "ナレーション", "（地の文）", "（ナレーション）",
                  "（テロップ）", "（台詞なし）", "（台詞なし)"):
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
    return bool(parts) and all(t in KNOWN_SPEAKERS for t in parts)


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
    if sp and not dg and ct:
        return ("line", norm_speaker(sp), ct)
    # 話者がセンターテキスト側に入った複数人同時発話（例 [凪・芳乃・りあむ] 瀬戸内海一。）
    if not sp and dg and ct and all_known(ct):
        return ("line", norm_speaker(ct), dg)
    if not sp and dg:
        m = re.match(r"^([^\s　]+?)[\s　]+([・…‥\.。]{3,})$", dg)
        if m and all_known(m.group(1)):
            return ("line", m.group(1), "……")
        return ("stage", "", dg)
    if (sp and dg and ct and ct != dg and len(ct) <= 16
            and not any(ch in ct for ch in "!！?？。、")
            and all_known(ct)):
        return ("line", norm_speaker(ct), dg)
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
                out.append({"type": "line", "speaker": "P",
                            "text": text, "frame": frame, "t": t})
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
            for k in range(j, min(j + 30, len(json_lines))):
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
            if json_lines:
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


# セクション定義（title_ov / sum_ov は code が None の話で使用）
SECTIONS = [
    # (id, tab, jsonコード, CSV行範囲, 再生開始秒, ログコード列, タイトル上書き, 要約上書き)
    ("op", "OP", "OP", (9, 63), 255, ["OP"], None, None),
    ("ep1", "第1話", "1", (64, 117), 1046, ["1"], None, None),
    ("ep2", "第2話", "2", (118, 184), 1797, ["2"], None, None),
    ("ep3", "第3話", "3", (185, 240), 2424, ["3"], None, None),
    # 再生開始秒はCreateYoutubeのチャプター（第3話末尾no239の完了時刻＝ビーチ
    # カード表示開始）に合わせて3024とする（no240は空フレームのため除外）。
    ("ep4", "第4話", "4", (241, 313), 3024, ["4"], None, None),
    ("ep5", "第5話", "5", (314, 395), 3722, ["5"], None, None),
    ("ed", "ED", "ED", (397, 465), 4433, ["ED"], None, None),
]


def main():
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    def rows_between(a, b):
        return [r for r in rows if a <= int(r["no"]) <= b]

    report = []
    result = []

    # --- 予告タブ（予告1: Tr1 / 予告2: Tr2）---
    # no1: 開催告知バナー, no2: 予告1カード, no3-4: 芳乃(Tr1)
    #                      no5: 予告2カード, no6-8: 凪(Tr2)
    entries = []
    banner = rows_between(1, 1)[0]
    entries.append({"type": "header", "speaker": "", "text": banner["center_text"].strip(),
                    "frame": banner["frame_file"], "t": float(banner["timestamp_s"])})
    for code, card_no, (ra, rb) in [("Tr1", 2, (3, 4)), ("Tr2", 5, (6, 8))]:
        d, jl = load_json_lines(code)
        card = rows_between(card_no, card_no)[0]
        entries.append({"type": "sub", "speaker": "", "text": card["center_text"].strip().replace("\n", " "),
                        "frame": card["frame_file"], "t": float(card["timestamp_s"])})
        entries += merge_section(rows_between(ra, rb), jl, report, code)
    result.append({"id": "trailer", "tab": "予告", "title": "予告",
                   "summary": "", "start_s": 0,
                   "title_frame": rows_between(2, 2)[0]["frame_file"], "log": ["Tr1", "Tr2"],
                   "entries": entries})

    # --- OP〜ED ---
    for tab_id, tab_name, code, (a, b), start_s, logs, title_ov, sum_ov in SECTIONS:
        d, jl = load_json_lines(code)
        sec_rows = rows_between(a, b)
        first_typ, _, _ = classify_csv_row(sec_rows[0])
        if first_typ in ("scene", "header"):
            title_frame = sec_rows[0]["frame_file"]
            entries = merge_section(sec_rows[1:], jl, report, code or tab_id)
        else:
            title_frame = sec_rows[0]["frame_file"]
            entries = merge_section(sec_rows, jl, report, code or tab_id)
        title = title_ov if title_ov is not None else d["title"]
        summary = sum_ov if sum_ov is not None else d["summary"]
        result.append({"id": tab_id, "tab": tab_name,
                       "title": title, "summary": summary,
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
        print(f"{sec['tab']}: 全{len(sec['entries'])}行 shot付{n_shot} shotなし{n_noshot} CSVのみ{n_csvonly} | {sec['title'][:30]}")
    print(f"\nレポート行数: {len(report)} -> {OUT_REPORT}")


if __name__ == "__main__":
    main()
