# imgup スキル：GitHub画像 → Cloudinary 移行

GitHubリポジトリに追加された画像をCloudinaryにアップロードし、HTMLのパスを置換して画像ファイルをリポジトリから削除する。

## 実行手順

### 1. 対象画像の特定

リポジトリ内の画像ファイル（jpg/jpeg/png/gif/webp/svg）を検索する。
`_cloudinary_upload_map.json` に**まだ登録されていない**ものを新規対象とする。

```bash
python3 -c "
import json
from pathlib import Path

BASE_DIR = Path('/home/user/SugarHeartDB')
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'}
map_file = BASE_DIR / '_cloudinary_upload_map.json'
existing = set(json.load(open(map_file)).keys()) if map_file.exists() else set()

new_images = []
for p in sorted(BASE_DIR.rglob('*')):
    if p.suffix.lower() in IMAGE_EXTS and '.git' not in p.parts:
        rel = str(p.relative_to(BASE_DIR))
        if rel not in existing:
            new_images.append(rel)

print(f'新規画像: {len(new_images)}枚')
for r in new_images:
    print(r)
"
```

新規画像が0枚なら作業終了。

### 2. GitHubにプッシュされているか確認

対象画像が `dev` ブランチ（または指定ブランチ）にプッシュ済みか確認する。
プッシュ済みでない場合はユーザーに確認を求める。

コミットSHAを取得：
```bash
git rev-parse origin/dev
```

### 3. Cloudinaryへアップロード（MCP経由・並行処理）

画像が多い場合（20枚超）は8バッチに分割して並行Agentで処理する。
少数の場合は直接MCPツールで処理する。

**GitHub raw URL形式：**
```
https://raw.githubusercontent.com/nagomi-sugarheart/SugarHeartDB/{COMMIT_SHA}/{rel_path}
```

**MCPツール呼び出し：**
- ツール: `mcp__5178af08-9f66-45b3-af43-2099a58d67d0__upload-asset`
- パラメータ: `file`=GitHub raw URL, `public_id`=拡張子なしのrelパス, `overwrite`=true

**Cloudinary URL生成ルール：**
- SVG以外: `https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/{public_id}`
- SVG: `https://res.cloudinary.com/dnmzdghoi/image/upload/{public_id}.svg`

並行Agentへの指示テンプレート（各バッチ用）：
```
/tmp/batch_N.json を読んで、各画像をCloudinaryにアップロードし、
結果を /tmp/result_batch_N.json に {"rel_path": "cdn_url"} 形式で書き出せ。
```

### 4. `_cloudinary_upload_map.json` の更新

```python
import json
from pathlib import Path

map_file = Path('/home/user/SugarHeartDB/_cloudinary_upload_map.json')
existing = json.load(open(map_file)) if map_file.exists() else {}

# バッチ結果をマージ
for i in range(num_batches):
    with open(f'/tmp/result_batch_{i}.json') as f:
        existing.update(json.load(f))

with open(map_file, 'w') as f:
    json.dump(existing, f, indent=2, ensure_ascii=False)
```

### 5. HTMLのパス置換

HTMLファイル内のGitHub上の画像パス（相対パスまたはGitHub raw URL）をCloudinary URLに置換する。

置換対象のパターン（`src=`, `href=`, `url()`, `content=` 属性）：
- 相対パス: `../CinGeki/foo.jpg`, `./CinGeki/foo.jpg`, `CinGeki/foo.jpg`
- GitHub raw URL: `https://raw.githubusercontent.com/.../foo.jpg`

```python
import re, os, json
from pathlib import Path

BASE_DIR = Path('/home/user/SugarHeartDB')
upload_map = json.load(open(BASE_DIR / '_cloudinary_upload_map.json'))
# 新規追加分のみ対象にする場合は new_map を渡す

html_files = [f for f in BASE_DIR.rglob('*.html') if '.git' not in f.parts]
replaced_count = 0

for html_path in html_files:
    content = open(html_path, encoding='utf-8').read()
    original = content
    html_dir = html_path.parent

    for rel_str, cdn_url in upload_map.items():
        if not cdn_url:
            continue
        img_path = BASE_DIR / rel_str
        rel_from_html = os.path.relpath(img_path, html_dir).replace('\\', '/')
        rel_from_base = rel_str.replace('\\', '/')

        for old_path in set([rel_from_html, './' + rel_from_html, rel_from_base, './' + rel_from_base]):
            escaped = re.escape(old_path)
            for pat, rep in [
                (r'(src=["\'])' + escaped + r'(["\'])', r'\g<1>' + cdn_url + r'\2'),
                (r'(href=["\'])' + escaped + r'(["\'])', r'\g<1>' + cdn_url + r'\2'),
                (r'(url\(["\']?)' + escaped + r'(["\']?\))', r'\g<1>' + cdn_url + r'\2'),
                (r'(content=["\'])' + escaped + r'(["\'])', r'\g<1>' + cdn_url + r'\2'),
            ]:
                content = re.sub(pat, rep, content)

    if content != original:
        open(html_path, 'w', encoding='utf-8').write(content)
        replaced_count += 1

print(f'{replaced_count}件のHTMLを更新')
```

### 6. リポジトリから画像ファイルを削除

```bash
# upload_mapに登録済みの画像ファイルのみ削除
python3 -c "
import json, os
from pathlib import Path
BASE_DIR = Path('/home/user/SugarHeartDB')
m = json.load(open(BASE_DIR / '_cloudinary_upload_map.json'))
for rel in m:
    p = BASE_DIR / rel
    if p.exists():
        p.unlink()
        print(f'削除: {rel}')
"
```

### 7. コミット・プッシュ・PR作成

```bash
git add -A
git commit -m "feat: migrate new images to Cloudinary and update HTML paths"
git push -u origin <current-branch>
```

PRが存在しない場合は作成する。

## 注意事項

- アップロードに失敗した画像（結果が`null`）は削除しない
- `_cloudinary_upload_map.json` と `scripts/cloudinary_migrate.py` はリポジトリに残す
- 画像ファイルはコミットしない（`.gitignore`への追加を検討）
- 作業ブランチは `claude/kind-feynman-MxwRC`（または指示されたブランチ）で行う
