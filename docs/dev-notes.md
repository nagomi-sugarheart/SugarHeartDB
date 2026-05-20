# 開発時の注意事項

## CSS

- CSSは `style.css` のみに記載。HTMLファイルに `<style>` タグを書かない
- 新しいスタイルを追加するときは `style.css` に追記する

## JavaScript

- ページ固有のJS（`cardImages` 配列・fetchなど）は各HTMLファイルの `<script>` タグに直書き
- **ナビ変更は `components/header.js` の `HEADER_HTML` だけ編集する**。HTMLファイルは触らない

## 新規HTMLページ作成チェックリスト

1. `<head>` に `style.css` を相対パスでリンク
2. `<body>` 直後に `<script src="[相対パス]/components/header.js"></script>` を入れる
3. `index.html` など既存ページから新ページへのリンクを追加する（孤立させない）
4. スマホ対応（`@media screen and (max-width: 900px)`）を確認する

## パス指定

- 画像・CSS・JSの読み込みや別ページへのリンクは**相対パス**を使用すること
- 絶対パス（`/` から始まるパス）は禁止

## デプロイ

- コミットしたらGitHub Pagesに自動デプロイされる
- `xlsxファイル` は `.gitignore` で管理対象外に設定済み

## フォント

- Yusei Magic（Google Fonts）を使用
