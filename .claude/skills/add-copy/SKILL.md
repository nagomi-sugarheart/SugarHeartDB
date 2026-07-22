# コピーボタン・検索インデックスの追加

新しい HTML ページのセリフに対して、**コピーボタン**と**グローバル検索への登録**を行う。
新規ページが完成したタイミングで実行する。

---

## 実行手順

### 1. 新ページのセリフ要素を確認する

対象ページを開き、セリフテキストが入っている要素のクラス名を確認する。

```bash
grep -n "class=" 対象ページ.html | grep -E "line|text|dialogue|dialog"
```

---

### 2. コピーボタンの対応確認・追加

`components/idol-badge.js` の `initCopyButtons()` に登録されているセレクターと照合する。

```bash
grep -A 10 "function initCopyButtons" components/idol-badge.js
```

**現在登録済みのセレクター（形式A〜D）:**

| 形式 | セレクター |
|------|-----------|
| 形式A | `.script-row:not(.stage-direction) .line` |
| 形式B | `.dialog .body .text` |
| 形式C | `.ud-dialogue .line` |
| 形式D | `.ev-dialog-row .ev-text` |

- **新ページのセリフが既存セレクターに一致する場合** → そのまま手順 3 へ（コピーボタンは自動で動く）
- **一致しない場合** → `initCopyButtons()` の末尾に1行追加する：

  ```js
  document.querySelectorAll('.新コンテナ .新テキスト要素').forEach(injectCopyBtn);
  ```

  さらに `scripts/_generate_search_index.py` の `DialogueParser` と `docs/search-feature.md` にも同セレクターを追記する（詳細は `docs/search-feature.md` を参照）。

---

### 3. 検索インデックスを再生成する

```bash
python scripts/_generate_search_index.py
```

スクリプトは `Mobamas/**/*.html` と `Deresute/**/*.html` を自動スキャンするため、
新ページがそれらディレクトリ内にあれば自動でピックアップされる。

---

### 4. 追加されたことを確認する

```python
import json
with open('data/search-index.json') as f:
    data = json.load(f)

# 対象ページのエントリを確認（ページ名の一部で絞り込む）
target = [e for e in data if '対象ページ名' in e.get('url', '')]
print(f'エントリ数: {len(target)}')
for e in target[:5]:
    print(f'  idol={e["idol"]:4} text={e["text"][:50]}')
```

エントリが 0 件の場合は、セリフ要素のセレクターが未登録（手順2で形式追加が必要）。

---

### 5. コミットする

```bash
git add data/search-index.json
# セレクターを新規追加した場合は以下も追加
# git add components/idol-badge.js scripts/_generate_search_index.py docs/search-feature.md
git commit -m "search-index: 〇〇ページのセリフをインデックスに追加"
```
