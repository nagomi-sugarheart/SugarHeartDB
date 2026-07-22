# SEO / sitemap 運用メモ

SugarHeartDB をGoogle検索に載せる（インデックスさせる）ための仕組みと運用ルール。

## 公開URL
- サイトURL: `https://nagomi-sugarheart.github.io/SugarHeartDB/`
- sitemap: `https://nagomi-sugarheart.github.io/SugarHeartDB/sitemap.xml`

## ファイル構成
| ファイル | 役割 |
| --- | --- |
| `sitemap.xml` | サイト内全ページのURL一覧。検索エンジンにページの存在を伝える。**自動生成物なので手書き編集しない。** |
| `generate_sitemap.py` | HTMLを走査して `sitemap.xml` を生成するスクリプト。 |
| `robots.txt` | クローラ向けの許可設定と sitemap の場所を記載。 |

## sitemap.xml の更新ルール（重要）
ページを **追加・削除・URL変更** したら、必ず再生成してコミットする。

```bash
python generate_sitemap.py
```

- `<meta name="robots" content="noindex">` を含むページは自動的に除外される。
- `lastmod` は各ファイルのGit最終コミット日を使う。
- `index.html` は末尾スラッシュのディレクトリURLに正規化される。

## Google にインデックスさせる手順（サイト管理者が一度だけ行う作業）
GitHub Pages への公開だけでは検索結果に出るまで時間がかかる。以下で登録・確認する。

1. **Google Search Console に登録**
   - https://search.google.com/search-console/ にGoogleアカウントでログインする。
   - プロパティタイプは「URLプレフィックス」を選び、`https://nagomi-sugarheart.github.io/SugarHeartDB/` を入力する。

2. **所有権の確認（verification）**
   - 「HTMLタグ」方式が簡単。表示される `<meta name="google-site-verification" content="xxxx">` を
     `index.html` の `<head>` 内にコピーして追記し、コミット・公開してから「確認」を押す。
   - ※GitHub Pagesのプロジェクトサイトのため、HTMLファイルアップロード方式やドメイン確認は使いにくい。metaタグ方式を推奨。

3. **sitemap を送信**
   - Search Console 左メニュー「サイトマップ」で `sitemap.xml` を送信する
     （入力欄には `sitemap.xml` と入れればよい）。

4. **インデックス状況の確認**
   - 「URL検査」で主要ページのインデックス状況を確認できる。
   - 反映には数日〜数週間かかることがある。

## 補足：robots.txt の注意点
- 本リポジトリはプロジェクトページ（`/SugarHeartDB/` 配下）のため、`robots.txt` は
  `https://nagomi-sugarheart.github.io/SugarHeartDB/robots.txt` に配置される。
- Googleが参照するのはホスト直下の `https://nagomi-sugarheart.github.io/robots.txt` であり、
  これは別リポジトリ（ユーザーページ）の管轄。よって本リポジトリの `robots.txt` はクロール制御としては
  効かない場合がある。**インデックスの主導線は Search Console への sitemap 送信**である点に注意。
- sitemap.xml 自体は上記URLで正しく配信され、Search Console から直接送信できるため問題ない。

## 各ページのSEO要素（既存の実装）
- `index.html` には `title` / `meta description` / `meta keywords` / OGP / Twitter Card / canonical が設定済み。
- 新規ページ作成時も、最低限 `title` と `meta description`、`link rel="canonical"` を設定することが望ましい。
