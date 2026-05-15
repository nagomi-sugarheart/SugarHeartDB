# SugarHeartDB - プロジェクト概要

## 開発ルール 
- 基本的な開発は「dev」ブランチで実施される。ユーザーが修正を加えた旨の報告をした場合は、必ず自身の作業BranchにGitで最新のdevブランチを Fetch & Pull して、変更内容を把握した上で次の作業に取り掛かること。
 - 作業用のブランチは最大で1日1つとする。必ず `claude-YYYYMMDD` という命名規則に従うこと。同セッション内であれば日をまたいでもブランチを作り直す必要はない。すでに同日のブランチが存在する場合は、新規作成せずに既存のブランチを使い回すこと。
- 【重要】devからのPull時にコンフリクト（競合）などのGitエラーが発生した場合は、絶対に自力で解決しようとせず、作業を止めて「コンフリクトが発生しました」とユーザーにすぐ報告すること。
-  コミットメッセージは日本語で、変更の意図を簡潔に書くこと。
- gitへのpush時にエラーが発生した場合は一度エラーが出た時点で動きを止め、絶対に自力で解決しようとせずユーザーへ報告すること。

## サイト概要

アイドルマスターシンデレラガールズのキャラクター「佐藤心（しゅがーはぁと）」に関する情報をまとめたファンサイト。
管理者：なごみ（@nagomi_IMCG）

## 技術スタック

- **言語：** HTML + CSS + JavaScript（最小限）
- **ホスティング：** Netlify（GitHub連携による自動デプロイ）
- **リポジトリ：** https://github.com/nagomi-sugarheart/SugarHeartDB
- **本番URL：** https://sugarheart-db.netlify.app/
- **フォント：** Yusei Magic（Google Fonts）
- **JavaScript：** ページ固有のJS（画像切り替えなど）は各HTMLファイルの `<script>` タグに直書き。共通ヘッダーのみ `components/header.js` に集約

## ファイル構成

```
/
├── index.html                  # トップページ
├── style.css                   # 全ページ共通のスタイル（CSSはこの1ファイルに集約）
├── SugarHeartHistory.html      # しゅがーはぁとの年表ページ
├── updates.html                # 更新情報一覧ページ
├── CLAUDE.md                   # このファイル
├── components/
│   └── header.js               # 共通ヘッダー（ナビ・ハンバーガーJS）★ナビ更新はここだけ
├── data/
│   └── updates.json            # 更新情報データ（index.html・updates.htmlが読み込む）
├── Favicon/                    # ファビコン画像
├── Mobamas/                    # モバマス関連
│   ├── CardList.html           # カード一覧
│   ├── NaganoAreaBossLines.html
│   ├── EventList.html
│   ├── ... （その他コンテンツページ）
│   └── [カード名]/
│       ├── [カード名].html
│       ├── [カード名]Icon.jpg
│       └── [カード名].jpg
├── Deresute/                   # デレステ関連
│   ├── CardList.html
│   ├── EventList.html
│   ├── ... （その他コンテンツページ）
│   └── [カード名]/
│       ├── [カード名].html
│       └── [カード名].jpg
├── Popmas/                     # ポプマス関連
│   └── ... （コンテンツページ）
└── General/                    # その他（総選挙・歌唱曲・ライブ等）
    └── ... （コンテンツページ）
```

### ファイル命名規則

- ディレクトリ名はUpperCamelCase英語（例：`Mobamas/`, `Deresute/`, `Popmas/`, `General/`）
- ファイル名はディレクトリ名の繰り返しを省く（例：`Mobamas/CardList.html`、`Deresute/EventList.html`）
 - カード詳細ページ：`[カード名ディレクトリ]/[カード名].html`（例：`Mobamas/AngelHeart/AngelHeart.html`）
- ページ種別をまたぐ場合はプレフィックスで区別（例：`Event_HappyNewYeah.html`, `SeasonalEvents_Birthday.html`）

※今後もHTMLファイルは増やしていく予定

## デザイン仕様

### カラーパレット

| 用途 | カラーコード |
|---|---|
| メインカラー（ピンク） | `#fd89b9` |
| サブカラー（黄色） | `#FAD766` |
| 本文テキスト | `#5D4037` |
| 背景色 | `#F9F9F5`（オフホワイト） |
| 白テキスト | `#fff2f2` |

### デザイン方針

- トップページとサブページで統一感のあるデザインにする
- スマートフォン対応（レスポンシブデザイン）必須
- CSSは `style.css` の1ファイルに全て記載し、増やさない
- 新しいスタイルを追加するときは `style.css` に追記する
- `*, *::before, *::after { box-sizing: border-box }` がグローバルに適用済み（width:100% + padding の組み合わせで使用可）

## サイト共通ヘッダー

**ナビを更新するときは `components/header.js` の `HEADER_HTML` 変数だけ編集すればよい。HTMLファイルは触らなくてよい。**

全HTMLページの `<body>` 直後に以下の1行を入れるだけでヘッダーが挿入される。

```html
<body>
<script src="/components/header.js"></script>
```

`header.js` は `document.currentScript.insertAdjacentHTML('beforebegin', HEADER_HTML)` でヘッダーを同期的にDOM注入し、ハンバーガー・スクロール・アコーディオンのイベントも自動設定する。

- **未実装ページへのリンク**は `<a class="disabled">` にする（CSS でグレーアウト・クリック不可）
- メガメニュー内・モバイルドロワー内・`.link-list` 内すべてで `href="#"` または `class="disabled"` を使う

## 主要なCSSクラス

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
| `.main-title` | トップページのメインタイトルエリア（背景画像あり） |
| `.sub-title` | サブページのタイトルエリア（グラデーション背景） |
| `.box-area` | 情報をまとめるボックス（ボーダー：ピンク） |
| `.box-title` | ボックスの見出し |
| `.box-item` | ボックス内の各行 |
| `.table-area` | カード一覧テーブル |
| `.tab-wrapper` | タブ切り替えUI（トップページ用） |
| `.detail-container` | カード詳細ページのレイアウト（サイドバー＋メイン） |
| `.sidebar-cardlist` | 詳細ページの左サイドバー（カード一覧） |
| `.accordion-item` | セリフエリアのアコーディオン（折りたたみ）UI |
| `.card-navigation` | 前後のカードへのナビゲーション |
| `.dialogue-area` | カードのセリフ表示エリア |
| `.theater-checkbox` / `.theater-accordion-label` / `.theater-accordion-content` | シンデレラガールズ劇場セクションのアコーディオン（PCは常時展開、モバイルは閉じた状態） |
| `.disabled` | 未実装リンクのグレーアウト（pointer-events: none） |
| `.boss-split` | ボスセリフページの左右分割レイアウト（PC: flex / mobile: block） |
| `.boss-table-wrap` | ボスセリフ表のラッパー（左カラム） |
| `.boss-img-pc` | ボスセリフ画像エリア（PCのみ表示、右カラム） |
| `.boss-img-mobile` | ボスセリフ画像アコーディオン（モバイルのみ表示） |

## ページ構成の方針

### トップページ（index.html）

- メインタイトル（背景画像＋キャッチコピー）
- 更新情報ボックス
- タブ切り替え（モバマス／デレステ／ポプマス／その他）で各ページへのリンク
  - 未実装ページのリンクは `href="#"` にする（CSSで自動グレーアウト）
- プロフィールボックス
- 情報提供フォームへのリンク

### カード一覧ページ（例：Mobamas_CardList.html）

- テーブル形式でカードを一覧表示
- 列：カード画像（アイコン）／レア度／カード名
- カード名・アイコン画像をクリックすると詳細ページへ遷移

### カード詳細ページ（例：Mobamas_佐藤心.html）

- 左サイドバー：カード一覧（PCのみ表示、スマホは非表示）
- メインエリア：
  - カード名＋実装日
  - 前後カードへのナビゲーション
  - カード画像（タップで次の画像に切り替わる）
  - セリフエリア（テキストタブ／画像タブ切り替え、アコーディオン形式）
  - シンデレラガールズ劇場（PC常時展開・モバイルはアコーディオン）
  - 関連ギャラリー（横スクロール）
  - 関連ページリンク
- `cardImages` 配列（`<script>` タグ内）で画像パスを管理し、タップで切り替え

## 今後追加予定のページ（コンテンツ未記入のスケルトンは作成済み）

- モバマス：ぷちでれら、イベント詳細、ユニット、季節イベント詳細、各種コミュ
- デレステ：各コミュ詳細、各イベント詳細、衣装詳細、ゲスト参加詳細
- ポプマス：イラスト、ホームセリフ、親愛度セリフ、イベントセリフ
- その他：各詳細コンテンツ
- 共通：シンデレラシアター、他アイドル呼称

## 開発時の注意事項

- CSSは `style.css` のみに記載。HTMLファイルに `<style>` タグを書かない
- **ナビ変更は `components/header.js` の `HEADER_HTML` だけ編集する**。HTMLファイルは触らない
- ページ固有のJS（`cardImages` 配列・fetchなど）は各HTMLファイルの `<script>` タグに直書き
- 新しいHTMLページを作る際は `<head>` に `style.css` をリンクし、`<body>` 直後に `<script src="/components/header.js"></script>` を入れる
- 画像パスはルートからの絶対パスで記載（例：`/Mobamas/AngelHeart/AngelHeartIcon.jpg`）
- スマホ対応（`@media screen and (max-width: 900px)`）を忘れない
- xlsxファイルはGitの管理対象外（.gitignoreで除外済み）
- コミットしたら自動でNetlifyにデプロイされる
- `body` には `padding-top: 64px` が設定済み（固定ヘッダー分）
- モバイルメニューのオーバーレイには必ず `pointer-events: none`（閉時）/ `pointer-events: auto`（開時）を設定すること（ないと画面操作が効かなくなる）
