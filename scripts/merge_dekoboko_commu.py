# -*- coding: utf-8 -*-
"""凸凹スピードスター イベントコミュのCSV×JSONマージスクリプト

- dialogues.csv: スクショのフレーム・タイムスタンプ・センターテキストを保持
- *_log.json:    完全なセリフテキスト・タイトル・要約を保持

両者を突合し、タブ生成用のマージ済みJSON (merged_commu.json) と
突合レポート (merge_report.txt) を出力する。
"""
import csv
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CSV_PATH = Path(r"C:\Users\sawas\Downloads\comm_frames\凸凹スピードスター_202606220104\dialogues.csv")
JSON_DIR = Path(r"G:\マイドライブ\コミュ")
OUT_DIR = Path(__file__).parent
OUT_JSON = OUT_DIR / "merged_commu.json"
OUT_REPORT = OUT_DIR / "merge_report.txt"

LOCATIONS = {"心の部屋", "事務所", "街中", "レッスンルーム", "休憩中", "イベント終了後"}

# センターテキストのみでPのセリフとして扱うもの
P_CENTER_LINES = {"それは、ふたりが書くんだ"}

SPEAKER_NORMALIZE = {
    "プロデューサー": "P",
    "なごみP": "P",
    "なこみP": "P",
    "???": "？？？",
    "マッドエスパ－・ユッコ": "マッドエスパー・ユッコ",
    "マッドドクター・アラキー": "マッドドクター・アラーキー",
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
    # 途中フレームでOCR揺れがある場合: JSON側の先頭部分と比較
    if len(nb) > len(na) >= 4:
        pr = SequenceMatcher(None, na, nb[: len(na) + 2]).ratio()
        if pr >= 0.75:
            r = max(r, pr)
    return r


# 表示テキストの正規化（OCR起因の誤りと表記ゆれの修正）
DISPLAY_FIXES = [
    ("マッドエスパ－", "マッドエスパー"),
    ("アラキー", "アラーキー"),
    ("こく普通", "ごく普通"),
    ("はあと", "はぁと"),
    ("〜", "～"),
    # ログ画像との照合で確認したOCR誤りの修正（文脈付きで安全に置換）
    ("いや、確かにプロデューサーさんから貰った資料には", "いえ、確かにプロデューサーさんから貰った資料には"),
    ("きちんと言いってあった", "きちんと書いてあった"),
    ("いっぱいいろし", "いっぱいいるし"),
    ("トップアイドルってやつー", "トップアイドルってやーつ"),
    ("ミミミミッソ！", "ミミミミンッ！"),
    ("スウィティー☆メタモルフォーゼ", "スウィーティー☆メタモルフォーゼ"),
    ("あまおーいラブ", "あまぁ～いラブ"),
    ("ぶっとばすそう☆", "ぶっとばすぞ☆"),
    ("しゅかしゅが", "しゅがしゅが"),
]


def fix_display(s):
    s = re.sub(r"\s+", " ", s).strip()
    for a, b in DISPLAY_FIXES:
        s = s.replace(a, b)
    # 半角括弧→全角（心の声）
    s = re.sub(r"^\(", "（", s)
    s = re.sub(r"\)$", "）", s)
    return s


def load_json_lines(code):
    p = JSON_DIR / f"凸凹スピードスター_{code}_log.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    lines = []
    for c in d["conversation"]:
        sp, dg = c["speaker"].strip(), c["dialogue"].strip()
        if sp.startswith("（") and not dg:
            # ナレーション行（OCRがspeaker欄に格納）
            lines.append({"speaker": "ナレーション", "text": sp})
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
        # 地の文（企画書を渡した…… 等）
        return ("stage", "", dg)
    if sp and dg and ct and not any(ch in ct for ch in "!！?？"):
        # OCRが話者名をcenter_textに入れたケース（瑞樹・比奈・裕子 等）
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


def main():
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # 行番号(no)ベースでセクション分割
    def rows_between(a, b):
        return [r for r in rows if a <= int(r["no"]) <= b]

    # 再生開始秒: CSVの時刻は「表示されきった時刻」のため、
    # 各話の開始は直前セリフの時刻（＝タイトルカードの表示開始）とする。
    # 予告はTwitter予告（動画冒頭）から再生する。
    sections = [
        # (タブID, タブ名, JSONコード(複数可), CSV行範囲, 再生開始秒)
        ("trailer", "予告", ["Tr1", "Tr2"], (1, 9), 0),
        ("op", "OP", ["OP"], (10, 62), 109),
        ("ep1", "第1話", ["1"], (63, 115), 631),
        ("ep2", "第2話", ["2"], (116, 158), 1063),
        ("ep3", "第3話", ["3"], (159, 212), 1437),
        ("ep4", "第4話", ["4"], (213, 276), 1991),
        ("ep5", "第5話", ["5"], (277, 328), 2533),
        ("ed", "ED", ["ED"], (329, 369), 3172),
    ]

    report = []
    result = []
    for tab_id, tab_name, codes, (a, b), start_s in sections:
        sec_rows = rows_between(a, b)
        if tab_id == "trailer":
            # 予告タブ: Twitter告知(行1) + 予告1(行2-5) + 予告2(行6-9)
            entries = []
            r1 = rows[0]
            entries.append({"type": "sub", "speaker": "", "text": "Twitter告知",
                            "frame": r1["frame_file"], "t": float(r1["timestamp_s"])})
            entries.append({"type": "stage", "speaker": "", "text": r1["center_text"].strip(),
                            "frame": r1["frame_file"], "t": float(r1["timestamp_s"])})
            for code, (ra, rb) in [("Tr1", (2, 5)), ("Tr2", (6, 9))]:
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
            title, summary = d["title"], d["summary"]
            if tab_id == "op":
                # ログの本文（会話）は正しいOP内容だが、title/summary欄は第4話
                # （恐怖！闇の魔法少女たち）のメタデータのままなので上書きする。
                # タイトル・要約はゲーム内スキップダイアログの公式表示に一致させた。
                title = "結成！ふたりは魔法少女"
                summary = ("――自分たちは、あとどれだけ夢を追いかけていられるのだろう。"
                           "そんな危機感を抱き始めていた菜々と心に、ひとつの仕事が舞い込んできた。"
                           "ふたりで1から組み上げるステージ企画と聞いた菜々は、ずっと夢見ていた"
                           "「あること」を提案する。凸凹道を往くふたりの夢のステージ、ここに開幕！")
            result.append({"id": tab_id, "tab": tab_name,
                           "title": title, "summary": summary,
                           "start_s": start_s, "title_frame": header_row["frame_file"],
                           "log": [code], "entries": entries})

    # 表示テキストの最終正規化
    for sec in result:
        sec["title"] = fix_display(sec["title"])
        sec["summary"] = fix_display(sec["summary"])
        for e in sec["entries"]:
            e["text"] = fix_display(e["text"])

    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_REPORT.write_text("\n".join(report), encoding="utf-8")

    # サマリ表示
    for sec in result:
        n_shot = sum(1 for e in sec["entries"] if e.get("frame"))
        n_noshot = sum(1 for e in sec["entries"] if e["type"] == "line" and not e.get("frame"))
        n_csvonly = sum(1 for e in sec["entries"] if e.get("csv_only"))
        print(f"{sec['tab']}: 全{len(sec['entries'])}行 shot付{n_shot} shotなし{n_noshot} CSVのみ{n_csvonly} | {sec['title']}")
    print(f"\nレポート行数: {len(report)} -> {OUT_REPORT}")


if __name__ == "__main__":
    main()
