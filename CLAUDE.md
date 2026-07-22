# プロジェクト概要
このプロジェクトは、GitHub Pagesで公開する静的Webサイトの開発リポジトリです。

## 技術スタック
- Frontend: HTML5, CSS3, Vanilla JavaScript（フレームワークなし）
- Hosting: GitHub Pages
- 画像ホスティング: Cloudinary（Cloud name: `dnmzdghoi`）

## 画像管理
- **すべての画像はCloudinaryで管理する。** リポジトリに画像ファイル（jpg/png/gif/webp/svg等）を追加しないこと。
- 新しい画像は `scripts/cloudinary_migrate.py` を使ってアップロードするか、Cloudinary Consoleから直接アップロードすること。
- 画像のURLは `https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/{public_id}` の形式を使用する。
- フォルダ構成は従来のリポジトリ構成（`CinGeki/`, `Deresute/`, `Mobamas/`, `Popmas/`, `Unit/`, `data/` 等）をCloudinaryのpublic_idとして維持している。
- アップロード済み画像の一覧は `_cloudinary_upload_map.json` を参照すること。

## プロジェクト全体のコーディングルール
- **【重要】リンクとパスの指定:** 画像以外のCSS・JSの読み込みや別ページへのリンクは、必ず**相対パス**を使用すること。（絶対パス `/` から始めるのは禁止）
- **画像パスについて:** 画像はCloudinaryのURLを使用するため、相対パスではなくCloudinaryのURLを直接指定すること。
- HTMLはセマンティックなタグ（`<header>`, `<main>`, `<article>` など）を適切に使用して構造化すること。
- モバイルファーストなレスポンシブデザインを心がけること。
- JavaScriptはモダンな構文（ES6以降）を使用し、グローバル変数の汚染を避けること。

## Claude Codeへの指示
- **回答言語:** ユーザーへの返答・質問・報告はすべて**日本語**で行うこと。
- **孤立ページの防止:** 新しいHTMLファイルを作成した場合は、必ず既存のページ（`index.html`など）からアクセスできるようにリンクを追加してください。どこのディレクトリに入れるべきかわからなかった場合はユーザーに質問をし、勝手な場所に配備しないでください。
- **【重要】sitemap.xmlの更新:** HTMLページを**追加・削除・URL変更**した場合は、必ず `python scripts/generate_sitemap.py` を実行して `sitemap.xml` を再生成し、コミットに含めること。sitemap.xml はサイト内の全ページを走査して自動生成されるため、手書きで編集しないこと（検索エンジンにページを認識させるための重要ファイル）。
- **【重要】一時作業スクリプトの管理:** アップロード・生成・移行などの**使い捨て（単発）スクリプトは、必ず `scripts/tmp/` の中に作成すること**（このフォルダは `.gitignore` で追跡対象外＝コミットされない）。そして**作業が終わったら削除し、フォルダを空に戻すこと**。リポジトリ直下や `scripts/` 直下に一時スクリプトを放置・コミットしないこと。恒久的に使うツール（`scripts/generate_sitemap.py`・`scripts/cloudinary_migrate.py`・`scripts/_generate_search_index.py`・各テンプレート）だけを `scripts/` 直下に置く。
- **仕様の確認:** 各機能の細かい要件は docs/ フォルダ内の仕様書を確認してください。
