# SugarHeartDB - プロジェクト概要

## サイト概要

アイドルマスターシンデレラガールズのキャラクター「佐藤心（しゅがーはぁと）」に関する情報をまとめたファンサイト。
管理者：なごみ（@nagomi_IMCG）

## 技術スタック

- **言語：** HTML + CSS + JavaScript（最小限）
- **ホスティング：** Netlify（GitHub連携による自動デプロイ）
- **リポジトリ：** https://github.com/nagomi-sugarheart/SugarHeartDB
- **本番URL：** https://sugarheart-db.netlify.app/
- **フォント：** Yusei Magic（Google Fonts）
- **JavaScript：** 各HTMLファイルの `<script>` タグに直書き（外部JSファイルは使わない）

## ファイル構成

```
/
├── index.html                  # トップページ
├── style.css                   # 全ページ共通のスタイル（CSSはこの1ファイルに集約）
├── SugarHeartHistory.html      # しゅがーはぁとの年表ページ
├── CLAUDE.md                   # このファイル
├── data/                       # データフォルダ（将来利用予定）
├── デレステ/                    # デレステ関連
│   ├── Deresute_CardList.html  # デレステカード一覧
│   └── [カード名]/
│       ├── Deresute_[カード名].html
│       ├── [カード名]アイコン.jpg
│       └── [カード名].jpg
├── モバマス/                    # モバマス関連
│   ├── Mobamas_CardList.html   # モバマスカード一覧
│   └── [カード名]/
│       ├── Mobamas_[カード名].html
│       ├── [カード名]アイコン.jpg
│       └── [カード名].jpg
└── ファビコン/                  # ファビコン画像
```

### HTMLファイル一覧

| ファイル名 | 役割 |
|---|---|
| index.html | トップページ（プロフィール・更新情報・各ページへのリンク） |
| SugarHeartHistory.html | しゅがーはぁとの年表ページ |
| モバマス/Mobamas_CardList.html | モバマスのカード一覧ページ |
| デレステ/Deresute_CardList.html | デレステのカード一覧ページ |
| モバマス/[カード名]/Mobamas_[カード名].html | モバマス カード詳細ページ |
| デレステ/[カード名]/Deresute_[カード名].html | デレステ カード詳細ページ |

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

全HTMLページの `<body>` 直後に以下の構造を挿入する。

```html
<header class="site-header" id="site-header">
    <nav class="header-nav">
        <a href="/" class="header-logo">SugarHeartDB</a>
        <ul class="nav-menu">
            <!-- PC用メガメニュー付きナビ -->
            <li class="nav-item"> ... </li>
        </ul>
        <button class="hamburger" id="hamburger" aria-label="メニューを開く">
            <span></span><span></span><span></span>
        </button>
    </nav>
    <div class="mobile-menu-overlay" id="mobile-overlay"></div>
    <div class="mobile-menu" id="mobile-menu">
        <!-- モバイル用ドロワーメニュー -->
    </div>
</header>
```

各ページの `</body>` 直前に以下のスクリプトを挿入する（スマートヘッダー・ハンバーガー・アコーディオン制御）。

```html
<script>
(function () {
    var header = document.getElementById('site-header');
    var hamburger = document.getElementById('hamburger');
    var mobileMenu = document.getElementById('mobile-menu');
    var overlay = document.getElementById('mobile-overlay');
    var lastScrollY = 0;
    // スマートヘッダー・ハンバーガー・アコーディオンのイベント処理
    // ... (index.html のスクリプトを参照)
})();
</script>
```

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

## 今後追加予定のページ

- モバマス：長野エリアボスセリフ、ぷちでれら、イベント、ユニット、季節イベント、その他コミュ
- デレステ：メモリアルコミュ、ストーリーコミュ、共通衣装、参加イベント、その他コミュ、シンデレラシアター
- ポプマス：イラスト、ホームセリフ、親愛度セリフ、イベントセリフ
- その他：歌唱曲、ライブ、アニメ・漫画、コラボ、総選挙、他アイドル呼称

## 開発時の注意事項

- CSSは `style.css` のみに記載。HTMLファイルに `<style>` タグを書かない
- JSは各HTMLファイル末尾の `<script>` タグに直書き。外部JSファイルは作らない
- 画像パスはルートからの絶対パスで記載（例：`/モバマス/佐藤心/佐藤心アイコン.jpg`）
- 新しいHTMLページを作る際は必ず `style.css` をリンクし、共通ヘッダーを挿入する
- スマホ対応（`@media screen and (max-width: 900px)`）を忘れない
- xlsxファイルはGitの管理対象外（.gitignoreで除外済み）
- コミットしたら自動でNetlifyにデプロイされる
- `body` には `padding-top: 64px` が設定済み（固定ヘッダー分）
- モバイルメニューのオーバーレイには必ず `pointer-events: none`（閉時）/ `pointer-events: auto`（開時）を設定すること（ないと画面操作が効かなくなる）
