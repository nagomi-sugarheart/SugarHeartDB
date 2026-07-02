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
| `.hero` / `.hero-text` / `.hero-visual` | トップページ（index.html）のメインタイトルエリア |
| `.page-hero` | サブページのタイトルエリア・ヒーローセクション（パンくず＋h1＋概要）。**サブページの標準はこれ** |
| `.sec-head` | セクション見出し（各ページ内の中項目タイトル） |
| `.box-area` | 情報をまとめるボックス（ボーダー：ピンク） |
| `.box-title` | ボックスの見出し |
| `.box-item` | ボックス内の各行 |
| `.table-area` | カード一覧テーブル |
| `.sh-container` / `.sh-container.tight` | 一覧ページなどの外枠コンテナ（`max-width` + 左右パディングを統一）。`.tight` は下部パディングを詰める |
| `.disabled` | 未実装リンクのグレーアウト（pointer-events: none） |

> `.main-title` / `.sub-title` は旧世代のクラス名で、`style.css` に定義は残っているが現在どのページからも使われていない（死んだCSS）。新規ページでは使わないこと。トップページのタイトル部は `.hero` 系、サブページは `.page-hero` を使う。

### タブ切り替え（共通・JSベース）

**新規ページのタブ切り替えはこのJSベース方式を標準とする。** 複数のタブグループを同一ページに置いても干渉しない。

| クラス名 | 用途 |
|---|---|
| `.tab-group` | タブ全体のラッパー（スコープ境界） |
| `.tab-list` | タブボタンを並べるナビ行 |
| `.tab-item` | タブボタン（`active` クラスで選択中を示す） |
| `.tab-panel` | タブに対応するコンテンツパネル（`data-tab="..."` で紐付け、`active` クラスで表示） |

```html
<div class="tab-group">
  <div class="tab-list">
    <button class="tab-item active" onclick="switchTab(this,'tab-1')">タブ1</button>
    <button class="tab-item" onclick="switchTab(this,'tab-2')">タブ2</button>
  </div>
  <div class="tab-panel active" data-tab="tab-1">…</div>
  <div class="tab-panel" data-tab="tab-2">…</div>
</div>
```

`switchTab` 関数は `components/common.js` に定義されている。

なお `.tab-wrapper`（radioベースのタブ）はトップページ（index.html）の `.games`（ゲーム別タブ、CSS-only radio方式）以外では使われていない旧世代のクラスで、`style.css` に定義のみ残っている。**新規ページでは使わず、上記のJSベース方式を使うこと。**

### カード詳細ページ（v2系・現行）

Deresute/Mobamas の各カード詳細ページ（計77ページ）はすべて以下のv2系クラスで構成されている。

| クラス名 | 用途 |
|---|---|
| `.v2-detail-layout` | カード詳細ページ全体のレイアウト（サイドバー＋メイン） |
| `.v2-sidebar` | 左サイドバー（カード一覧）。`components/sidebar.js` が生成・注入する |
| `.v2-detail-main` | メインコンテンツ全体のラッパー |
| `.v2-title-block` | カード名＋実装日のタイトルブロック |
| `.v2-breadcrumb` | パンくずリスト |
| `.v2-card-nav` | 前後カードへのナビゲーション（上下2箇所に設置） |
| `.v2-card-hero` | カード画像＋メタ情報パネルのセクション |
| `.v2-meta-panel` | カード情報（レアリティ・ステータス・スキル等）のパネル |
| `.v2-dialogue-block` | セリフエリア全体（テキストタブ／画像タブ切り替え） |
| `.v2-accord` / `.v2-accord-head` / `.v2-accord-body` | セリフ種別ごとのアコーディオン（開閉はcommon.jsが処理） |
| `.v2-theater` 系 | シンデレラガールズ劇場セクション |
| `.v2-gallery` | 関連ギャラリー（横スクロール） |
| `.v2-related` | 関連ページリンク |

> **旧世代クラス（`.detail-container` / `.sidebar-cardlist` / `.card-navigation` / `.dialogue-area` / `.theater-checkbox` / `.theater-accordion-label` / `.theater-accordion-content`）は現在どのページからも使われていない。** `style.css` に定義のみ残っている死んだCSS。唯一 `.accordion-item`（セリフの折りたたみUI）だけが `Deresute/GuestCommu/GuestCommu.html` で使用中。新規のカード詳細ページは必ずv2系クラスと `components/sidebar.js` を使うこと。

### ボスセリフページ

| クラス名 | 用途 |
|---|---|
| `.split` | 左右分割レイアウト（PC: flex / mobile: block） |
| `.table-wrap` | テーブルのラッパー（左カラム） |
| `.img-pc` | 画像エリア（PCのみ表示、右カラム） |
| `.img-mobile` | 画像アコーディオン（モバイルのみ表示） |

### 汎用ユーティリティ（`style.css` 末尾「汎用ユーティリティ」以降）

インラインstyleの廃止に伴い追加された共通クラス群。

| クラス名 | 用途 |
|---|---|
| `.placeholder-text` | 「準備中」「読み込み中」「画像募集中」などのプレースホルダ文。インラインstyleは使わずこのクラスを使う |
| `.sh-container` / `.sh-container.tight` | 一覧ページの外枠コンテナ（`.sh-container` の説明は「ページ共通」表を参照） |
| `.sh-tag.sh-tag-sm` | 一覧の行内バッジ用の小さめタグ |
| `.sh-tag[data-tag="goods"]` | グッズ用タグの配色（ピンク背景） |
| `.stats-strip` | 一覧ページ上部の統計ストリップ（例：CollabList.html） |
| `.filter-chip .dot.collab` / `.dot.goods` / `.dot.campaign` | フィルターチップの種別ドット配色 |
| `.ref-list` / `.ref-item` / `.ref-note` / `.ref-section` | References（参考・情報提供）ページ用のリスト表示。旧 `References.html` 内の `<style>` ブロックは廃止し、この定義に統合した |

## コンポーネント構成

| ファイル | 役割 | 読み込み位置 |
|---|---|---|
| `components/header.js` | 全ページ共通ヘッダー・フッター・グローバル検索。`HEADER_HTML` 変数を編集するだけでナビが変わる | `<body>` 直後 |
| `components/common.js` | タブ切り替え（`switchTab`）、v2セリフタブ（`v2SwitchTab`）、画像サイクラー（`initV2Cycler`、`#v2-card-main-img` の `data-images` から自動初期化）、イベント一覧ソート（`toggleSort`）、ユニットDURATION自動計算（`#ud-duration` の `data-debut` から自動表示）、各種アコーディオン、ライトボックスを一元管理 | タブ・アコーディオン・サイクラー・DURATION・ソートを使うページの `</body>` 直前 |
| `components/sidebar.js` | カード詳細ページ（v2系）左サイドバー「カード一覧」。`CARDS` 配列を編集するだけで一覧が変わる。詳細は「カード詳細ページ（v2系・現行）」を参照 | `.v2-detail-layout` 内、サイドバーを出したい位置 |
| `components/idol-badge.js` | アイドル名バッジへのパーソナルカラー適用、セリフコピーボタンの自動挿入 | アイドル名バッジ表示のあるページの `</body>` 直前 |

### JS読み込み規約

- 全ページ共通: `components/header.js`（`<body>` 直後）
- タブ・アコーディオン・サイクラー・DURATION・ソートのいずれかを使うページ: `components/common.js`（`</body>` 直前）
- アイドル名バッジ表示のあるページ: `components/idol-badge.js`（`</body>` 直前）
- カード詳細ページ: `components/sidebar.js`（`.v2-detail-layout` 内のサイドバー位置）

### メタ情報の規約

- `og:image` ・ favicon は必ずCloudinary URL（`https://res.cloudinary.com/dnmzdghoi/...`）を使用する。`github.io` の旧URLやリポジトリ相対パスは禁止
- `twitter:title` は `og:title` と同じ、ページ固有のタイトルにする（サイト名の使い回し等は禁止）
