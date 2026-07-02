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

### カード詳細ページ（例：Deresute/HeartToHeart/HeartToHeart.html）

Deresute/Mobamas 計77ページすべて、以下の v2 系クラス構成・共通コンポーネント方式で統一されている（旧クラス `.detail-container` 等は現在未使用。`docs/design.md` の「カード詳細ページ（v2系・現行）」を参照）。

- 全体は `.v2-detail-layout`（サイドバー＋メイン `.v2-detail-main` の構成）
- **左サイドバー（カード一覧）は `components/sidebar.js` が注入する**（PCのみ表示、スマホは非表示）
  - `.v2-detail-layout` の直下に `<script src="components/sidebar.js"></script>` を置くだけでよい
  - カードの追加・変更は `sidebar.js` 内の `CARDS` 配列を編集するだけでよい（HTML側は触らない）
  - アイコンURLは `href`（例：`Deresute/HeartToHeart/HeartToHeart.html`）の末尾 `.html` を `Icon` に置換してCloudinary public_idを自動導出する（例：`.../HeartToHeart/HeartToHeartIcon`）
  - 現在アクティブなカードの判定はURL（`location.pathname`）から自動で行われる
- メインエリア（`.v2-detail-main`）：
  - `.v2-title-block` … カード名＋実装日
  - `.v2-card-nav` … 前後カードへのナビゲーション（ページ上部・下部の2箇所）
  - `.v2-card-hero` … カード画像（`.v2-main-img-area`）＋カード情報（`.v2-meta-panel`）
  - `.v2-dialogue-block` … セリフエリア（テキストタブ／画像タブ切り替え、`.v2-accord` アコーディオン形式）
  - シンデレラガールズ劇場（`.v2-theater` 系）
  - `.v2-gallery` … 関連ギャラリー（横スクロール）
  - `.v2-related` … 関連ページリンク
- カード画像は `#v2-card-main-img` の `data-images` 属性（`|` 区切りのCloudinary URL）に列挙するだけでよい。`components/common.js` が `DOMContentLoaded` 時に自動検出して `initV2Cycler` を初期化する（ページ側でのインライン初期化スクリプトは不要・廃止済み）

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
