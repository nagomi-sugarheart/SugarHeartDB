# 開発時の注意事項

## CSS

- CSSは `style.css` のみに記載。HTMLファイルに `<style>` タグを書かない
- 新しいスタイルを追加するときは `style.css` に追記する

## JavaScript

- **共通関数は `components/common.js` に定義されている**。タブ・アコーディオン・サイクラー・DURATION・ソートを使うページで `<script src="[相対パス]/components/common.js"></script>` を読み込む（`</body>` 直前）
  - 定義されている関数: `switchTab`（タブ切り替え）、`v2SwitchTab`（v2対話タブ）、`initV2Cycler`（カード画像サイクル）、`toggleSort`（イベント一覧の並び替え）
  - DOMContentLoaded 自動初期化: `#v2-card-main-img` の `data-images` からv2カード画像サイクラーを自動起動、`#ud-duration` の `data-debut` からユニットDURATION（経過年月）を自動表示、`.lv-accord` アコーディオン、`.v2-accord-head` アコーディオン、`.ep-block .ep-head` アコーディオン、ライトボックス
  - これらの自動初期化により、各ページ側でのインライン初期化スクリプトは不要（廃止済み）
- カード詳細ページ（v2系）の左サイドバー「カード一覧」は `components/sidebar.js` が注入する。追加・変更は `sidebar.js` 内の `CARDS` 配列を編集するだけでよい
- ページ固有のJS（fetchなど）は各HTMLファイルの `<script>` タグに直書き
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
