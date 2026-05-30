# ページ構成仕様

## サイト概要

アイドルマスターシンデレラガールズのキャラクター「佐藤心（しゅがーはぁと）」に関する情報をまとめたファンサイト。
管理者：なごみ（@nagomi_IMCG）

## 各ページの構成方針

### トップページ（index.html）

- メインタイトル（背景画像＋キャッチコピー）
- 更新情報ボックス（`data/updates.json` から読み込み）
- タブ切り替え（モバマス／デレステ／ポプマス／その他）で各ページへのリンク
  - 未実装ページのリンクは `href="#"` にする（CSSで自動グレーアウト）
- プロフィールボックス
- 情報提供フォームへのリンク

### カード一覧ページ（例：Mobamas/CardList.html）

- テーブル形式でカードを一覧表示
- 列：カード画像（アイコン）／レア度／カード名
- カード名・アイコン画像をクリックすると詳細ページへ遷移

### カード詳細ページ（例：Mobamas/AngelHeart/AngelHeart.html）

- 左サイドバー：カード一覧（PCのみ表示、スマホは非表示）
- メインエリア：
  - カード名＋実装日
  - 前後カードへのナビゲーション
  - カード画像（タップで次の画像に切り替わる）
  - セリフエリア（テキストタブ／画像タブ切り替え、アコーディオン形式）
  - シンデレラガールズ劇場（PC常時展開・モバイルはアコーディオン）
  - 関連ギャラリー（横スクロール）
  - 関連ページリンク
- `v2CardImages` 配列（`<script>` タグ内）で画像パスを管理し、`initV2Cycler` で初期化する（`components/common.js` 参照）

## 新規ページ作成時のテンプレート

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <base href="/SugarHeartDB/">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ページタイトル｜SugarHeartDB</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
<script src="components/header.js"></script>

<section class="page-hero">
  <div class="breadcrumb"><a href="/SugarHeartDB/">HOME</a> · <strong>ページ名</strong></div>
  <h1>ページ名 <span class="sub">/ PAGE SUBTITLE</span></h1>
</section>

<div class="page">
  <!-- ここにコンテンツ -->
</div>

<script src="components/common.js"></script>
</body>
</html>
```

※`<base href="/SugarHeartDB/">` により、全パスはサイトルートからの絶対パスとして記述できる（`href="style.css"` 等）。

## 今後追加予定のページ（スケルトン作成済み）

- モバマス：ぷちでれら、イベント詳細、ユニット、季節イベント詳細、各種コミュ
- デレステ：各コミュ詳細、各イベント詳細、衣装詳細、ゲスト参加詳細
- ポプマス：イラスト、ホームセリフ、親愛度セリフ、イベントセリフ
- その他：各詳細コンテンツ
- 共通：シンデレラシアター、他アイドル呼称
