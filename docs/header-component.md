# 共通ヘッダーコンポーネント仕様

## 概要

**ナビを更新するときは `components/header.js` の `HEADER_HTML` 変数だけ編集すればよい。HTMLファイルは触らなくてよい。**

## 組み込み方法

全HTMLページの `<body>` 直後に以下の1行を入れるだけでヘッダーが挿入される。

```html
<body>
<script src="../components/header.js"></script>
```

※パスはページの階層に合わせて相対パスで記載すること。

## 動作仕様

`header.js` は `document.currentScript.insertAdjacentHTML('beforebegin', HEADER_HTML)` でヘッダーを同期的にDOM注入し、ハンバーガー・スクロール・アコーディオンのイベントも自動設定する。

## 未実装ページのリンク処理

- **未実装ページへのリンク**は `<a class="disabled">` にする（CSS でグレーアウト・クリック不可）
- メガメニュー内・モバイルドロワー内・`.link-list` 内すべてで `href="#"` または `class="disabled"` を使う

## モバイルメニューの注意事項

モバイルメニューのオーバーレイには必ず以下を設定すること（ないと画面操作が効かなくなる）：

- 閉時：`pointer-events: none`
- 開時：`pointer-events: auto`

## レイアウトへの影響

- `body` には `padding-top: 64px` が設定済み（固定ヘッダー分）
