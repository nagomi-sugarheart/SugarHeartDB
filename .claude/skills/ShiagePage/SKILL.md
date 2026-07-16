# ShiagePage スキル：イベントコミュページの仕上げ（欠損画像の配備とタイムスタンプ補正）

CreatePageで作成済みのイベントコミュページに対し、撮り直した欠損画像（タイトルカード・shotなし行）を
配備し、章開始時刻をタイトル画像基準に補正する。あわせてGドライブのYouTube素材
（chapters.txt / subtitles_ja.srt）も同じ基準で補正する。

**参考実装**
- 命燃やして恋せよ乙女（コミット `a26f170`）: 基本形。`Deresute/Event/InochiMoyashiteKoiseyoOtome.html`
- Happy New Yeah！／Take me☆Take you（コミット `7649d87`）: 応用形。SRTへのエントリ挿入・番号振り直し、
  補間潰れ区間の開き直し、TOUCH写り込みshotの差し替え、エピグラフ型の代用カードを扱った
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
  **場所カード（CSVの center_text）が代用**されていることが多い（CreatePage手順の仕様）
  - 代用カードの中身はイベントで異なる。**場所カード**（「12月 某日・旅館」「収録中」等）のほか、
    **エピグラフ／ポエムカード**（Take me☆Take you の「依田芳乃という存在は、その姿以上に大きく見える――」等）
    のこともある。挿入テキストは必ず dialogues.csv の該当行 `center_text` の実文字列を使う
  - **旧タイトルが場所カードではなくセリフ画像の代用**のこともある（Happy New Yeah 第2話）。
    その画像が既に本文中の別行で使われていれば、先頭への場面カード挿入は**省略**する
- SRTは連続形式（前エントリの終了時刻 = 次エントリの開始時刻）。章タイトル字幕は `【タイトル N話】` 形式
  - **SRTに章タイトルや場所カードのエントリ自体が欠落している**ことがある（Happy New Yeah は
    第2話タイトルと「神社」カードが両方欠落）。その場合は実時刻でエントリを新規挿入し、
    **全エントリの通し番号を振り直す**（末尾までズレる）。パーサは番号ではなく時刻行を基準にすること
  - **連続形式が崩れて補間時刻に潰れている**区間がある（複数エントリが同一の短区間に詰められている）。
    タイトル字幕の直前だけでなく、その手前数エントリも画像の実時刻で開き直す必要がある
    （Happy New Yeah ED直前の卯月「あけまして」＋全員「おめでとう」）
- 既存shotに **TOUCH表示や次カットが写り込んでいる**ことがある（Take me☆Take you ED最終行）。
  撮り直し画像があれば、no-shot行でなくても**その既存shotの src を撮り直し分に差し替える**
- shotなし行とSRTのセリフは1:1で対応するとは限らない。**撮り漏れがあれば該当行はno-shotのまま残す**
  （枚数が合わない場合は必ずどの行が漏れたかを時刻から特定して報告する）
- **Twitter告知の書き起こし行は常にno-shotのまま**（取材元がTwitter動画でゲーム画面のshotが無い）。
  予告タブ等に含まれる。撮り漏れと混同しないこと

## 実行手順

### 1. 画像の分類とマッピング
1. ページの `no-shot` 行と各話 `data-start` を列挙、Gドライブの chapters.txt / subtitles_ja.srt を読む
2. 各欠損画像の時刻を、章時刻（タイトル）または SRT のセリフ表示区間（shot）に割り当てる
3. **全画像をReadで目視**し、以下を確認する:
   - タイトル画像: 話タイトルの文言が合っているか
   - shot画像: セリフがページの本文と一致するか。**小書き文字（ああ/あぁ）や記号後のスペース
     （☆ ありがと）・話者の抜け（合唱行の人数）の差異は誤記**。判別しづらければPILで該当部分を
     切り出し拡大して確認する。枚数が多い時は4枚組の縦連結シートを作ると目視が速い
   - **中間フレームや部分表示の混入に注意**（未完成のセリフ・改行途中）。表示しきったフレームを使う
4. 誤記が見つかったらページ本文とSRTを同じ内容で修正する。`data/search-index.json` はページ修正後に
   **手順7で再生成**すればよい（直接編集しなくてよい。手作業置換は文字化けの原因になる）
   - **目視・照合はSonnetサブエージェントに並行委任してよい**（画像シートのReadと本文突合は独立作業）

### 2. Cloudinaryアップロード
public_id の命名規則（`Deresute/Event/{イベント名}/commu/` 配下）:
- タイトルカード: `title_OP`, `title_1` 〜 `title_5`, `title_ED`
- セリフshot: **直前フレーム番号+英字**（例: 0089の次に入るなら `0089a`、連続挿入は `0243a/0243b/0243c`）

アップロード方法（**推奨: cloudinary Python SDK 直接**）:
MCPの `upload-asset` は `file://` のローカルパスを読めない（ENOENT）。環境変数にAPIキーも無い。
だが `~/.claude.json` 内に `cloudinary://{key}:{secret}@dnmzdghoi` 形式のURLがあるので、これを
`CLOUDINARY_URL` に設定すればSDKで直接アップロードできる（**枚数が多くても署名不要・日本語パスもOK**）:
```python
import json,re,os,ssl,urllib3
d=open(r'C:/Users/sawas/.claude.json',encoding='utf-8').read()
os.environ['CLOUDINARY_URL']=re.search(r'cloudinary://[0-9]+:[^"\']+@dnmzdghoi',d).group(0)
ssl._create_default_https_context=ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import cloudinary, cloudinary.uploader as up
cloudinary.CERT_KWARGS={"cert_reqs":"CERT_NONE"}; up._http=urllib3.PoolManager(cert_reqs="CERT_NONE")
up.upload('C:/Users/sawas/Pictures/欠損部分/xxx.png', public_id='Deresute/Event/{ev}/commu/{pid}', overwrite=True)
```
- フォールバック（認証URLが見つからない時）: `mcp__cloudinary__sign-upload` で全ファイル分の署名を
  一括取得し、curlでPOST（`file=@`＋api_key/signature/timestamp/colors/overwrite/public_id を全て渡す。
  日本語パスは失敗しやすいので `/c/temp_upload/` 等ASCIIパスにコピーしてから実行し完了後削除）
- `_cloudinary_upload_map.json` に追記する際は **`json.dump(..., indent=1, ensure_ascii=False)`**
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
   - public_id割当は、その行の**直前に本文で使われているフレーム番号+英字**を自動採番すると衝突しない
     （no-shot行をスクリプトで走査し、直前の `commu/NNNN` を記憶して `NNNNa/NNNNb...` を振る）
   - 本文置換はスクリプトで一括処理し、各誤記修正は `assert count==1` を付けて取りこぼし・多重置換を防ぐ
4. **写り込みshotの差し替え**（該当あれば）: no-shot行でない既存shotでも、TOUCH表示や次カットが
   写り込んでいれば src を撮り直し分（例 `0360a`）に差し替える
5. **再生開始秒の補正**: 各話 `data-start` = **タイトル画像ファイル名の時刻 − 1秒**（chapters.txtと同値にする）

### 4. Gドライブ素材の補正
1. **chapters.txt**: 各章時刻 = タイトル画像時刻 − 1秒（予告1/予告2は変更なし）
2. **subtitles_ja.srt**（ブロック単位でパースして再構築するのが安全）:
   - パーサは各ブロックを `[start, end, text]` に分解する（**番号行ではなく時刻行を基準に**。
     番号は挿入で振り直すため）。書き出し時に通し番号を1から振り直す
   - 章タイトル字幕（`【… N話】`）の開始時刻を補正値に直し、**直前エントリの終了時刻も連動**させる
     （SRTは連続形式のため。タイトル字幕の終了時刻は変更しない）
   - **エントリ自体が欠落している場合は実時刻で新規挿入**（例: 章タイトル・場所カード）。
     挿入位置は前後セリフの時刻の間に収め、番号振り直しで整合させる
   - **補間で潰れた区間**（複数ブロックが同一短区間に詰まっている）は、タイトル直前だけでなく
     手前数エントリも画像の実時刻で開き直す
   - 手順1で見つけた誤記も修正（`assert count==1` で確認）
   - ユーザーから指示があれば**最後に全タイムスタンプを一括シフト**（例: +1秒。各ブロックの
     start/end に加算）。シフト後は章タイトル字幕の開始がタイトル表示しきり時刻に一致するのが正
   - ファイルは **UTF-8（BOMなし）・CRLF**。`newline=''` で読み書きして改行を保持する

### 5. 検索インデックス再生成
`python _generate_search_index.py` を実行する（本文の誤記修正を反映）。
`data/search-index.json` を手で編集しないこと（文字化けの原因）。差分は該当行のみになるのが正。

### 6. 検証
- HTML: `no-shot` の残数（=撮り漏れ数。Twitter告知行を除いた実撮り漏れを把握）、新public_idの
  出現回数、`data-start` 値、`dss-stage-text` 行数を grep で確認
- CDN: 新URLを `curl -s -o /dev/null -w "%{http_code}"` で数枚スポットチェック（200であること）
- SRT: 章タイトル字幕の開始・終了、挿入エントリ、先頭/末尾のシフト結果を目視確認

### 7. コミット
CLAUDE.local.md の方針に従いローカルコミットのみ（push・PR不要）。
対象: イベントページHTML・`_cloudinary_upload_map.json`・`data/search-index.json`
（Gドライブのファイルはgit管理外）。**複数イベントを一度に処理した場合もイベントごとに何をしたかを
コミットメッセージに整理**し、撮り漏れ・写り込み差し替え・SRTへのエントリ挿入があれば明記する。
一時ファイル（画像シート・ASCIIコピー・`_tmp_*`）は削除してからコミットする。
