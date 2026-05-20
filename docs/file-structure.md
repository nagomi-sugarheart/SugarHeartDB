# ファイル構成・命名規則

## ディレクトリ構成

```
/
├── index.html                  # トップページ
├── style.css                   # 全ページ共通のスタイル（CSSはこの1ファイルに集約）
├── SugarHeartHistory.html      # しゅがーはぁとの年表ページ
├── updates.html                # 更新情報一覧ページ
├── CLAUDE.md                   # Claude Code向けプロジェクト指示
├── components/
│   └── header.js               # 共通ヘッダー（ナビ・ハンバーガーJS）★ナビ更新はここだけ
├── data/
│   └── updates.json            # 更新情報データ（index.html・updates.htmlが読み込む）
├── docs/                       # 仕様書ドキュメント
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

## 命名規則

- ディレクトリ名はUpperCamelCase英語（例：`Mobamas/`, `Deresute/`, `Popmas/`, `General/`）
- ファイル名はディレクトリ名の繰り返しを省く（例：`Mobamas/CardList.html`、`Deresute/EventList.html`）
- カード詳細ページ：`[カード名ディレクトリ]/[カード名].html`（例：`Mobamas/AngelHeart/AngelHeart.html`）
- ページ種別をまたぐ場合はプレフィックスで区別（例：`Event_HappyNewYeah.html`, `SeasonalEvents_Birthday.html`）

## 注意事項

- xlsxファイルはGitの管理対象外（.gitignoreで除外済み）
- 今後もHTMLファイルは増やしていく予定
