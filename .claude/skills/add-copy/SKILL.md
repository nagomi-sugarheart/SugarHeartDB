# コピーボタン・検索インデックスの追加

新しいHTMLセリフ形式（新クラスのセリフ要素）を追加したページに対して、
「セリフコピーボタン」と「グローバル検索インデックス」の両方を対応させる手順です。

---

## このスキルを使うタイミング

- 新しいHTMLクラス構造のセリフ（例：`.ev-dialog-row .ev-text`）を追加したとき
- 既存の形式A〜Cに該当しない新形式のセリフ要素が追加されたとき
- `docs/search-feature.md` に「対応形式を追加してほしい」と言われたとき

---

## 前提知識：現在の対応形式

| 形式 | セレクター | 使用場所 |
|------|-----------|---------|
| 形式A | `.script-row:not(.stage-direction) .line` | モバマス通常ストーリー |
| 形式B | `.dialog .body .text` | KirakiraModelChallenge等のシーン台詞 |
| 形式C | `.ud-dialogue .line` | ユニット詳細ページ |
| 形式D | `.ev-dialog-row .ev-text` | イベント中セリフ・他アイドル言及 |

新形式を追加する場合は、以下の **形式E以降** として追加していく。

---

## 実行手順

### 1. 追加するセリフ要素のセレクターを確認する

対象HTMLを開き、セリフテキストが入っている要素のクラス名を確認する。
- セリフ本文が入る最内要素（例：`<div class="ev-text">テキスト</div>`）
- その外側の行コンテナ（例：`<div class="ev-dialog-row">`）
- スピーカー情報がどこに書かれているか（例：親アコーディオンの `span[data-who]`）

---

### 2. `components/idol-badge.js` にコピーボタン注入を追加する

`initCopyButtons()` 関数の末尾に1行追加する。

```js
// 形式X: .新コンテナ .新テキスト要素（追加する形式の説明）
document.querySelectorAll('.新コンテナ .新テキスト要素').forEach(injectCopyBtn);
```

**例（形式Dを追加したとき）:**
```js
function initCopyButtons() {
  document.querySelectorAll('.script-row:not(.stage-direction) .line').forEach(injectCopyBtn);
  document.querySelectorAll('.dialog .body .text').forEach(injectCopyBtn);
  document.querySelectorAll('.ud-dialogue .line').forEach(injectCopyBtn);
  // 形式D: .ev-dialog-row .ev-text（イベント中セリフ・他アイドル言及）← 追加
  document.querySelectorAll('.ev-dialog-row .ev-text').forEach(injectCopyBtn);
}
```

`getLineText()` はそのまま使える（`.speaker` / `.who` スパンを除外してテキストのみ取得する共通実装）。

---

### 3. `_generate_search_index.py` の `DialogueParser` に形式を追加する

#### 3-1. `__init__` に状態変数を追加

```python
# 形式X: .新コンテナ
self._新形式_depth = -1    # -1 = 対象外
self._新形式_who   = ''
self._in_新テキスト = False
self._新テキスト_depth = 0
self._新テキスト_text  = ''
```

**スピーカー情報の取得方法によって状態変数は変わる。**
- セリフ行ごとに `data-who` がある場合 → 行の属性から直接読む
- 親コンテナ（アコーディオン等）の `span[data-who]` から読む場合 → コンテナ入場時に取得し、子要素すべてに使い回す（形式Dのパターン）

#### 3-2. `handle_starttag` に検出ロジックを追加

**パターン①：親コンテナからスピーカーを引き継ぐ場合（形式Dのパターン）**

```python
# 形式X: 親コンテナ（例 .v2-accord）の入場を検出
if tag == 'div' and self._has_class(attrs_dict, '親コンテナクラス'):
    self._新形式_depth = len(self._stack)
    self._新形式_who   = ''

# 親コンテナ内の最初の speaker[data-who] からアイドル名を取得
if (self._新形式_depth >= 0
        and not self._新形式_who
        and tag == 'span' and self._has_class(attrs_dict, 'speaker')):
    who = attrs_dict.get('data-who', '')
    if who and who not in ('P', 'ナレーション'):
        self._新形式_who = who

# テキスト要素の入場
if (self._新形式_depth >= 0
        and tag == 'div' and self._has_class(attrs_dict, 'テキストクラス')):
    self._in_新テキスト    = True
    self._新テキスト_depth = len(self._stack)
    self._新テキスト_text  = ''
```

**パターン②：セリフ行自体に `data-who` がある場合（形式Aに近いパターン）**

```python
if tag == 'div' and self._has_class(attrs_dict, '行クラス') \
        and 'data-who' in attrs_dict:
    self._新形式_who   = attrs_dict['data-who']
    self._in_新テキスト    = True
    self._新テキスト_depth = len(self._stack)
    self._新テキスト_text  = ''
```

#### 3-3. `handle_endtag` に終了ロジックを追加

```python
# テキスト要素の終了
if self._in_新テキスト and depth < self._新テキスト_depth:
    text = self._新テキスト_text.strip()
    who  = self._新形式_who
    if text and who and who not in ('P', 'ナレーション', ''):
        self.entries.append((who, text))
    self._in_新テキスト = False

# 親コンテナの終了（パターン①の場合のみ）
if tag == 'div' and self._新形式_depth >= 0 and depth < self._新形式_depth:
    self._新形式_depth = -1
    self._新形式_who   = ''
```

#### 3-4. `handle_data` にテキスト収集を追加

```python
if self._in_新テキスト:
    self._新テキスト_text += data
```

---

### 4. `docs/search-feature.md` を更新する

2か所を更新する。

**① セリフコピー機能 > 対象要素 の表に追記**

```markdown
| 形式X（新形式の説明）| `.新コンテナ .新テキスト要素` |
```

**② データソース一覧 > Mobamas/**/*.html の行を更新**

```markdown
| `Mobamas/**/*.html` | ストーリー台詞 `.script-row` / `.dialog .body` / `.ev-dialog-row .ev-text` / `.新コンテナ .新テキスト要素` （type: story） |
```

---

### 5. 検索インデックスを再生成する

```bash
python _generate_search_index.py
```

出力例:
```
合計: XXXX エントリ
出力完了: data/search-index.json (XXX KB)
```

---

### 6. 動作確認

以下のPythonコードで、新形式のセリフがインデックスに入っているか確認する。

```python
import json
with open('data/search-index.json') as f:
    data = json.load(f)

# 対象ページのエントリを抽出（URLに対象ページ名を含むもの）
target = [e for e in data if '対象ページ名' in e.get('url', '')]
print(f'対象ページのエントリ数: {len(target)}')

from collections import Counter
print('アイドル別:', dict(Counter(e['idol'] for e in target)))

# サンプル表示
for e in target[-5:]:
    print(f'  idol={e["idol"]:4} text={e["text"][:50]}')
```

期待結果：
- 追加したセリフがエントリとして含まれている
- `idol` フィールドが正しいアイドル短縮名になっている（空・`P`・`ナレーション` ではない）

---

### 7. コミット

変更対象ファイル：
- `components/idol-badge.js`
- `_generate_search_index.py`
- `data/search-index.json`
- `docs/search-feature.md`

```bash
git add components/idol-badge.js _generate_search_index.py data/search-index.json docs/search-feature.md
git commit -m "コピーボタン・検索インデックスを形式Xに対応"
```

---

## 注意事項

- `_generate_search_index.py` の `DialogueParser` は**逐次パーサー**なので、深さ（`len(self._stack)`）の管理を正確に行うこと。`handle_starttag` でスタックに push した後に `len(self._stack)` を記録し、`handle_endtag` では pop 前の `depth` と比較する。
- 既存の形式A〜D（特に形式B の `_in_dialog_body` フラグ）と **名前が衝突しないよう**、新形式の状態変数名を一意にすること。
- `data/search-index.json` は生成物だが **Git 管理対象**なので必ずコミットに含めること。
- コピーボタンの `getLineText()` は `.speaker` / `.who` クラスを除外する実装になっているため、セリフ行内にスピーカー名のスパンが混在している場合も本文のみが正しくコピーされる。
