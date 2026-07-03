# CreatePage スキル：イベントコミュページの作成（shot付・タブ形式）

動画から抽出したスクショ＋dialogues.csvと、コミュログ画像＋JSONを突合して、
イベント詳細ページにshot付・タブ形式のイベントコミュを組み込む。

**参考実装（テンプレート）: 凸凹スピードスター**
- 突合: `scripts/merge_dekoboko_commu.py` → `scripts/merged_commu.json`
- アップロード: `scripts/upload_dekoboko_commu.py`
- HTML生成: `scripts/generate_dekoboko_commu_html.py`
- 完成ページ: `Deresute/Event/DekobokoSpeedStar.html`

## ユーザーが毎回指定するもの
1. **スクショフォルダ**（例 `C:\Users\sawas\Downloads\comm_frames\{イベント名}_{日時}`）
   - `NNNN_dialogue_{秒}s.jpg`（動画フレーム）と `dialogues.csv` が入っている
2. **ログフォルダ**（例 `G:\マイドライブ\コミュ`）
   - 話ごとの `{イベント名}_{code}_log.json` と `{イベント名}_{code}_log.png`（code: Tr1/Tr2/OP/1〜5/ED）
3. **YouTubeのURL**（埋め込み・再生ボタン用）
4. 対象のイベントページ（`Deresute/Event/*.html`。なければどこに作るかユーザーに確認）

## データの性質（重要な前提知識）
- **dialogues.csv** 列: `no,timestamp_s,frame_file,speaker,dialogue,center_text`（BOM付きUTF-8）
  - `timestamp_s` は**セリフが表示されきった時刻**。セリフの開始時刻は直前行の時刻とみなす
  - `center_text` に場所（事務所など）・話タイトルカード・Pの中央表示セリフが入る
  - フレームOCRのため**テキスト品質は高い**。ただし途中フレーム（タイピング途中）の部分テキストが混ざる
  - OCRが複数話者名を `center_text` に入れることがある（例: 瑞樹・比奈・裕子）
- **ログJSON** キー: `event_name, title, episode, episode_code, summary, conversation[{speaker,dialogue}]`
  - （）で囲まれた心の声など、CSVにない行を保持
  - ログ画像OCRのため**濁点落ち・小書き文字誤りが多い**（が→か、ず→す、ぁ→あ 等）
  - **メタデータ誤記に注意**: 凸凹ではOPのtitle/summaryが4話の複製だった。CSVのタイトルカード（center_text）と必ず照合する
  - ナレーション行がspeaker欄に入っていることがある（speakerが「（」で始まりdialogueが空）
  - Pのセリフはログにほぼ含まれない（CSVのみ）。Pの短い中央表示（「うなずく」等）はTOUCH表示済みフレーム＝完全表示

## 実行手順

### 1. データ調査
- CSVの `center_text` のみの行を全て列挙し、話の境界（行番号範囲）・場所ラベル・P中央セリフを分類する
- 全JSONの title/summary/episode_code をCSVのタイトルカードと照合し、誤記があれば正しい値を確定する
  （要約が復元できない場合はWeb検索をSonnetサブエージェントに依頼。見つからなければ暫定要約＋「※暫定」注記）

### 2. 突合スクリプトの作成・実行
`scripts/merge_dekoboko_commu.py` をコピーしてイベント用に調整する。調整箇所:
- CSV/JSONパス、場所ラベル集合 `LOCATIONS`、P中央セリフ `P_CENTER_LINES`
- セクション表（タブID・CSV行範囲・再生開始秒）※開始秒は手順5で補正
- `SPEAKER_NORMALIZE`（プロデューサー/なごみP→P、OCR揺れの話者名）
- `DISPLAY_FIXES`（イベント固有のOCR修正。初回は空でよい）

突合ロジックの要点（テンプレートに実装済み）:
- 完全表示のセリフは**CSVテキストを優先**（JSONより高品質）。JSONはshotなし行と途中フレームの補完に使う
- 記号（……。）のみのセリフ同士は同一とみなす／途中フレームはJSON行の前方部分と比較して救済
- 同一セリフの途中→完全フレームはshotを後のフレームに差し替え、重複行は除去

### 3. 品質検証（Sonnetサブエージェントを並行活用）
- merge_report の「JSON未マッチ」「低類似」行を確認。P台詞はフレーム画像をReadで目視確認
- shotなし行（JSONのみ由来）に不自然な語があれば、**ログ画像との照合をSonnetサブエージェントに委任**
  （PILで縦長ログ画像を1500px程度にスライス→該当位置をReadで目視→正しい表記を報告させる）
- 確定した誤りを `DISPLAY_FIXES` に文脈付き置換で追加して再実行
- 完成データからランダムに数行選び、フレーム画像と話者・テキストの一致を抜き取り確認

### 4. Cloudinaryアップロード
`scripts/upload_dekoboko_commu.py` をコピーして調整し、バックグラウンド実行する。
- 認証: `CLOUDINARY_URL` を `~/.claude.json` 内の `cloudinary-url` から取得して環境変数に設定
- public_id: `Deresute/Event/{イベント名}/commu/{NNNN}`（使用フレームのみ）と `.../log/{code}`
- **10MB超のログPNGはPILでJPEG(quality=88)に圧縮して再アップロード**
- 完了後 `_cloudinary_upload_map.json` に追記されることを確認

### 5. 再生開始秒の算出
各話の開始秒 = **直前セリフの完了時刻**（タイトルカード表示開始）。
- タイトルカードの直前行の `timestamp_s` を床関数で秒に。直前行のtが無い場合は前後から均等補間
- 予告タブは動画冒頭（0）から
- この値をセクション表の `start_s` に反映して再実行

### 6. HTML生成・組み込み
`scripts/generate_dekoboko_commu_html.py` をコピーして調整し、断片を生成してイベントページに組み込む。
- タブ: `.v2-dialogue-tabs` + `v2SwitchTab()`（common.js既存）。2枚目以降のパネルは `style="display:none"`
- 行: `.ev-dialog-row` + `.ev-shot` + `.ev-text > .ud-dialogue`（コピーボタン・話者バッジ・ライトボックス自動対応）
- 各タブ先頭: タイトルカード画像・話タイトル・要約・「▶ この話からYouTubeで再生」ボタン（`data-start`属性）
- 各タブ末尾: `<details class="dss-log">` でコミュログ画像
- **CSSの `.dss-*` は style.css に定義済み**（凸凹で追加）。新規追加不要
- 動画セクション: `<iframe id="dss-player">` を設置。ページ末尾に再生ボタン用の小さなIIFEスクリプトと `#sh-lightbox` div、`components/idol-badge.js` の読み込みを追加（DekobokoSpeedStar.htmlを参照）

### 7. 検索インデックス再生成
```bash
python _generate_search_index.py
```
対象ページのエントリが追加されたことを確認する（/add-copy スキル参照）。

### 8. 動作検証
- Desktopフォルダを `python -m http.server` で配信すると `<base href="/SugarHeartDB/">` がそのまま解決できる:
  `http://localhost:{port}/SugarHeartDB/Deresute/Event/{ページ}.html` をPlaywrightで開く
- タブ切替・再生ボタンのiframe src変化（`?start=秒&autoplay=1`）・画像のbroken有無・コンソールエラーを確認
- **検証後にサーバー停止・スクショ等の一時ファイル削除**（画像をリポジトリにコミットしない）

### 9. コミット
CLAUDE.local.md の方針に従いローカルコミットのみ（push・PR不要）。
突合スクリプト・merged_commu.json もコミットする（再生成・CreateYoutubeスキルで使用）。
