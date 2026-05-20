# デザイン仕様

## カラーパレット

| 用途 | カラーコード |
|---|---|
| メインカラー（ピンク） | `#fd89b9` |
| サブカラー（黄色） | `#FAD766` |
| 本文テキスト | `#5D4037` |
| 背景色 | `#F9F9F5`（オフホワイト） |
| 白テキスト | `#fff2f2` |

## デザイン方針

- トップページとサブページで統一感のあるデザインにする
- スマートフォン対応（レスポンシブデザイン）必須
- CSSは `style.css` の1ファイルに全て記載し、増やさない
- 新しいスタイルを追加するときは `style.css` に追記する
- `*, *::before, *::after { box-sizing: border-box }` がグローバルに適用済み（width:100% + padding の組み合わせで使用可）
- スマホ対応ブレークポイント: `@media screen and (max-width: 900px)`

## 主要なCSSクラス

### ヘッダー関連

| クラス名 | 用途 |
|---|---|
| `.site-header` | 全ページ共通の固定ヘッダー |
| `.header-nav` | ヘッダー内のナビバー（max-width: 1100px） |
| `.header-logo` | ヘッダーのサイト名リンク |
| `.nav-menu` | PC用ナビメニュー（ul） |
| `.nav-item` | ナビメニューの各項目（メガメニュー付き） |
| `.nav-link` | ナビメニューのリンク（hover でアンダーライン） |
| `.mega-menu` | メガメニューパネル（PC hover で表示） |
| `.mega-inner` | メガメニューの内側コンテナ |
| `.mega-col` | メガメニューのカラム |
| `.hamburger` | モバイル用ハンバーガーボタン |
| `.mobile-menu` | モバイル用ドロワーメニュー |
| `.mobile-menu-overlay` | モバイルメニュー開時の背景オーバーレイ |
| `.mobile-item` | モバイルメニューの各カテゴリー行 |
| `.mobile-item-header` | モバイルメニューのカテゴリーヘッダー行 |
| `.accordion-toggle` | モバイルメニューのアコーディオン開閉ボタン |
| `.mobile-submenu` | モバイルメニューのサブリスト |

### ページ共通

| クラス名 | 用途 |
|---|---|
| `.main-title` | トップページのメインタイトルエリア（背景画像あり） |
| `.sub-title` | サブページのタイトルエリア（グラデーション背景） |
| `.box-area` | 情報をまとめるボックス（ボーダー：ピンク） |
| `.box-title` | ボックスの見出し |
| `.box-item` | ボックス内の各行 |
| `.table-area` | カード一覧テーブル |
| `.tab-wrapper` | タブ切り替えUI（トップページ用） |
| `.disabled` | 未実装リンクのグレーアウト（pointer-events: none） |

### カード詳細ページ

| クラス名 | 用途 |
|---|---|
| `.detail-container` | カード詳細ページのレイアウト（サイドバー＋メイン） |
| `.sidebar-cardlist` | 詳細ページの左サイドバー（カード一覧） |
| `.accordion-item` | セリフエリアのアコーディオン（折りたたみ）UI |
| `.card-navigation` | 前後のカードへのナビゲーション |
| `.dialogue-area` | カードのセリフ表示エリア |
| `.theater-checkbox` / `.theater-accordion-label` / `.theater-accordion-content` | シンデレラガールズ劇場セクションのアコーディオン（PCは常時展開、モバイルは閉じた状態） |

### ボスセリフページ

| クラス名 | 用途 |
|---|---|
| `.boss-split` | ボスセリフページの左右分割レイアウト（PC: flex / mobile: block） |
| `.boss-table-wrap` | ボスセリフ表のラッパー（左カラム） |
| `.boss-img-pc` | ボスセリフ画像エリア（PCのみ表示、右カラム） |
| `.boss-img-mobile` | ボスセリフ画像アコーディオン（モバイルのみ表示） |
