# サイト内グローバル検索 + セリフコピー機能

## 機能概要

| 機能 | 説明 |
|------|------|
| グローバル検索 | ヘッダーの🔍ボタンからオーバーレイを開き、全コンテンツをキーワード検索 |
| アイドル絞り込み | 検索オーバーレイ内のドロップダウンで特定アイドルに絞り込み |
| セリフコピー | 会話ページのセリフ行にカーソルを当てると表示されるボタンでテキストコピー |

---

## 検索インデックスの構造

検索データは `data/search-index.json` に格納されています。

### エントリ形式

```json
{
  "type": "card" | "unit" | "story",
  "title": "表示タイトル（カード名・ユニット名・ページ名）",
  "text": "検索対象テキスト（セリフ・台詞）",
  "idol": "アイドル短縮名（スペース区切り複数可）",
  "context": "補足情報（カテゴリ、イベント名など）",
  "url": "CardList.html"
}
```

### type 別の内容

| type | データソース | url |
|------|-------------|-----|
| `card` | `data/mobamas.csv` のセリフ列 | `CardList.html` |
| `unit` | `data/udetail.csv` の台詞列 | 各ユニット詳細ページ |
| `story` | `Mobamas/**/*.html` および `Deresute/**/*.html` の `.script-row` / `.dialog .body` 要素 | 各ストーリーページ |

---

## データソース一覧

| ファイル | 用途 |
|----------|------|
| `data/mobamas.csv` | カード名・セリフ（type: card） |
| `data/ulist.csv` | ユニット名・メンバー（unit の idol フィールド生成に使用） |
| `data/udetail.csv` | ユニット台詞（type: unit） |
| `Mobamas/**/*.html` | ストーリー台詞 `.script-row` / `.dialog .body` （type: story） |
| `Deresute/**/*.html` | ストーリー台詞 `.script-row` / `.dialog .body` （type: story） |
| `data/cgss_idols.csv` | アイドル選択ドロップダウンの選択肢生成（JS側でフェッチ） |

---

## インデックス更新手順

新しいページ・カード・ユニットを追加した後は、以下のコマンドを実行して `data/search-index.json` を再生成してください。

```bash
python _generate_search_index.py
```

### 実行後に更新されるファイル

- `data/search-index.json`（上書き生成）

### 更新が必要なタイミング

- `data/mobamas.csv` にカードを追加・変更した時
- `data/udetail.csv` にユニット台詞を追加・変更した時
- `Mobamas/` または `Deresute/` 以下にストーリーページを追加・変更した時

---

## アイドル選択ドロップダウン

- 検索オーバーレイ内の `<select>` 要素
- 初回オーバーレイ表示時に `data/cgss_idols.csv` をフェッチして選択肢を動的生成
- 先頭に「すべてのアイドル」オプション（デフォルト値、絞り込みなし）
- アイドルを選択すると、エントリの `idol` フィールド（スペース区切りの短縮名リスト）に対して AND 条件でフィルタリング

---

## セリフコピー機能

### 対象要素

| HTML形式 | 対象セレクター |
|---------|--------------|
| 形式A（モバマスストーリー）| `.script-row:not(.stage-direction) .line` |
| 形式B（KirakiraModelChallenge等）| `.dialog .body .text` |
| 形式C（ユニット詳細）| `.ud-dialogue .line` |

### 動作

1. 各セリフ要素にコピーボタン（⎘）を JS で自動挿入
2. ボタンはホバー時に表示（タッチデバイスでは常時表示）
3. クリックで `navigator.clipboard.writeText()` を実行
4. コピーするテキスト: セリフ本文のみ（`.speaker` / `.who` スパンのテキストは除外）
5. 1.5 秒間「✓」表示でフィードバック

### 制約

- `navigator.clipboard` は `https://` または `localhost` 環境でのみ動作（GitHub Pages は対象内）
- HTTP 環境（ローカルファイル）では動作しない

---

## 実装ファイル

| ファイル | 役割 |
|----------|------|
| `_generate_search_index.py` | `data/search-index.json` を生成するスクリプト |
| `data/search-index.json` | 生成物（Git 管理対象） |
| `components/header.js` | 検索ボタン（🔍）・オーバーレイ UI・検索ロジック |
| `components/idol-badge.js` | コピーボタン inject・クリップボード処理 |
| `style.css` | 検索オーバーレイ・コピーボタンの CSS |
| `docs/search-feature.md` | この仕様書 |
