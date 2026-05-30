# 開発時の注意事項

## CSS

- CSSは `style.css` のみに記載。HTMLファイルに `<style>` タグを書かない
- 新しいスタイルを追加するときは `style.css` に追記する

## JavaScript

- **共通関数は `components/common.js` に定義されている**。全ページで `<script src="[相対パス]/components/common.js"></script>` を読み込む
  - 定義されている関数: `switchTab`（タブ切り替え）、`v2SwitchTab`（v2対話タブ）、`initV2Cycler`（カード画像サイクル）
  - DOMContentLoaded 自動初期化: `.lv-accord` アコーディオン、`.v2-accord-head` アコーディオン、`.ep-block .ep-head` アコーディオン、ライトボックス
- ページ固有のJS（`v2CardImages` 配列・fetchなど）は各HTMLファイルの `<script>` タグに直書き
- **ナビ変更は `components/header.js` の `HEADER_HTML` だけ編集する**。HTMLファイルは触らない

## 新規HTMLページ作成チェックリスト

1. `<head>` に `style.css` を相対パスでリンク
2. `<body>` 直後に `<script src="[相対パス]/components/header.js"></script>` を入れる
3. `</body>` 直前に `<script src="[相対パス]/components/common.js"></script>` を入れる
4. `index.html` など既存ページから新ページへのリンクを追加する（孤立させない）
5. スマホ対応（`@media screen and (max-width: 900px)`）を確認する

## パス指定

- 画像・CSS・JSの読み込みや別ページへのリンクは**相対パス**を使用すること
- 絶対パス（`/` から始まるパス）は禁止

## デプロイ

- コミットしたらGitHub Pagesに自動デプロイされる
- `xlsxファイル` は `.gitignore` で管理対象外に設定済み

## フォント

- Yusei Magic（Google Fonts）を使用
