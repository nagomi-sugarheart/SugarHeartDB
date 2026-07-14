# ShiagePage スキル：イベントコミュページの仕上げ（欠損画像の配備とタイムスタンプ補正）

CreatePageで作成済みのイベントコミュページに対し、撮り直した欠損画像（タイトルカード・shotなし行）を
配備し、章開始時刻をタイトル画像基準に補正する。あわせてGドライブのYouTube素材
（chapters.txt / subtitles_ja.srt）も同じ基準で補正する。

**参考実装: 命燃やして恋せよ乙女**（コミット `a26f170`）
- ページ: `Deresute/Event/InochiMoyashiteKoiseyoOtome.html`
- Gドライブ: `G:\マイドライブ\コミュ\YouTube_{イベント名}\`（chapters.txt / subtitles_ja.srt）

## ユーザーが毎回指定するもの
1. **対象のイベントページ**（`Deresute/Event/*.html`）
2. **欠損画像フォルダ**（例 `C:\Users\sawas\Pictures\欠損部分`）
   - ファイル名: `{イベント名}_HH.MM.SS.png`。**複数イベントの画像が混在している**ので対象イベント分のみ扱う
   - **ファイル名の時刻 = セリフが全部表示された時刻**（タイトル画像なら表示しきった時刻）
3. **GドライブのYouTube素材フォルダ**（例 `G:\マイドライブ\コミュ\YouTube_{イベント名}`）
4. 参考データ: `C:\Users\sawas\Downloads\comm_frames\{イベント名}_{日時}\dialogues.csv`（フレーム時刻の裏取り用）

## データの性質（重要な前提知識）
- 欠損画像は**2種類**が混在する。時刻で機械的に分類できる:
  - **話タイトルカード**（OP/1〜5話/ED）: chapters.txt の各章時刻の直後（+1〜5秒）にある画像
  - **shotなし行のセリフshot**: SRTで該当セリフの表示区間（start→end）末尾に一致する画像
- ページの既存タイトルカードは、動画にタイトルカードのフレームが無かったため
  **場所カード（CSVの center_text。例「12月 某日・旅館」）が代用**されていることが多い（CreatePage手順の仕様）
- SRTは連続形式（前エントリの終了時刻 = 次エントリの開始時刻）。章タイトル字幕は `【タイトル N話】` 形式
- shotなし行とSRTのセリフは1:1で対応するとは限らない。**撮り漏れがあれば該当行はno-shotのまま残す**
  （枚数が合わない場合は必ずどの行が漏れたかを時刻から特定して報告する）

## 実行手順

### 1. 画像の分類とマッピング
1. ページの `no-shot` 行と各話 `data-start` を列挙、Gドライブの chapters.txt / subtitles_ja.srt を読む
2. 各欠損画像の時刻を、章時刻（タイトル）または SRT のセリフ表示区間（shot）に割り当てる
3. **全画像をReadで目視**し、以下を確認する:
   - タイトル画像: 話タイトルの文言が合っているか
   - shot画像: セリフがページの本文と一致するか。**小書き文字（ああ/あぁ）や記号後のスペース
     （☆ ありがと）の差異は誤記**。判別しづらければPILで該当部分を切り出し拡大して確認する
4. 誤記が見つかったらページ本文・`data/search-index.json`・SRTの3か所を同じ内容で修正する

### 2. Cloudinaryアップロード
public_id の命名規則（`Deresute/Event/{イベント名}/commu/` 配下）:
- タイトルカード: `title_OP`, `title_1` 〜 `title_5`, `title_ED`
- セリフshot: **直前フレーム番号+英字**（例: 0089の次に入るなら `0089a`、連続挿入は `0243a/0243b/0243c`）

アップロード方法の注意（ハマりどころ）:
- ローカルにCLOUDINARY APIキーの環境変数は**無い**。MCPの `upload-asset` は `file://` の
  ローカルパスを読めない（ENOENT）。**`mcp__cloudinary__sign-upload` で全ファイル分の署名を
  一括取得し、curlでPOSTする**のが確実:
  ```
  curl https://api.cloudinary.com/v1_1/dnmzdghoi/image/upload \
    -F 'file=@"/c/temp_upload/xxx.png"' -F api_key=... -F signature=... \
    -F timestamp=... -F colors=0 -F overwrite=1 -F public_id=...
  ```
  （upload_params の全キーをそのままフォームフィールドにする。1つでも欠けると署名エラー）
- 日本語パスは失敗することがあるため、`/c/temp_upload/` 等ASCIIパスにコピーしてから実行し、完了後削除する
- `_cloudinary_upload_map.json` に25件追記する際は **`json.dump(..., indent=1, ensure_ascii=False)`**
  （元ファイルはindent=1。indent=2で書くと全行差分になる）

### 3. HTMLの更新
1. **タイトルカード差し替え**: `.dss-title-card img` の src を `commu/title_*` に変更（altは変更不要）
2. **旧タイトル画像を各話コミュの先頭へ**: 旧画像は場所カードなので、各話 `<div class="dss-lines">` の
   直後に場面テキスト行として挿入する（既存の「居酒屋」行と同じ形式）:
   ```html
   <div class="ev-dialog-row"><div class="ev-shot"><img src=".../commu/0008" alt="12月 某日・旅館" loading="lazy"></div><div class="ev-text"><div class="dss-stage-text">12月 某日・旅館</div></div></div>
   ```
   テキストは dialogues.csv の該当行の `center_text` を使う。
   **同じ画像がもとから本文中にある場合は挿入を省略**。予告タブのタイトルが正しいタイトル画像なら変更しない
3. **shotなし行に画像を配備**: `class="ev-dialog-row no-shot"` → `class="ev-dialog-row"` にし、
   `<div class="ev-shot"><img src=... alt="{話者}のセリフ" loading="lazy"></div>` を `ev-text` の前に挿入
4. **再生開始秒の補正**: 各話 `data-start` = **タイトル画像ファイル名の時刻 − 1秒**（chapters.txtと同値にする）

### 4. Gドライブ素材の補正
1. **chapters.txt**: 各章時刻 = タイトル画像時刻 − 1秒（予告1/予告2は変更なし）
2. **subtitles_ja.srt**:
   - 章タイトル字幕（`【… N話】`）の開始時刻を同じ値に修正し、**直前エントリの終了時刻も連動**させる
     （SRTは連続形式のため。タイトル字幕の終了時刻は変更しない）
   - 手順1で見つけた誤記も修正
   - ユーザーから指示があれば**最後に全タイムスタンプを一括シフト**（例: +1秒。正規表現で
     `HH:MM:SS,mmm` を全置換）。シフト後は章タイトル字幕の開始がタイトル表示しきり時刻に一致するのが正
   - ファイルは **UTF-8（BOMなし）・CRLF**。`newline=''` で読み書きして改行を保持する

### 5. 検証
- HTML: `no-shot` の残数（=撮り漏れ数）、新public_idの出現回数、`data-start` 値、
  `dss-stage-text` 行数を grep で確認
- CDN: 新URLを `curl -s -o /dev/null -w "%{http_code}"` で数枚スポットチェック（200であること）
- SRT: 章タイトル字幕の開始・終了、先頭/末尾エントリのシフト結果を目視確認

### 6. コミット
CLAUDE.local.md の方針に従いローカルコミットのみ（push・PR不要）。
対象: イベントページHTML・`_cloudinary_upload_map.json`・`data/search-index.json`
（Gドライブのファイルはgit管理外）。撮り漏れがあれば行とセリフをコミットメッセージと報告に明記する。
