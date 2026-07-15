/* ============================================================
   SugarHeartDB 共通ヘッダーコンポーネント
   更新するときはこのファイルだけ編集すればOK
   ============================================================ */
(function () {
    var HEADER_HTML = '<header class="site-header" id="site-header">\n\
    <nav class="header-nav">\n\
        <a href="/SugarHeartDB/" class="header-logo">SugarHeartDB</a>\n\
        <ul class="nav-menu">\n\
            <li class="nav-item">\n\
                <a href="Mobamas/index.html" class="nav-link">モバマス</a>\n\
                <div class="mega-menu">\n\
                    <div class="mega-inner">\n\
                        <div class="mega-col">\n\
                            <h4>カード・コミュ</h4>\n\
                            <ul>\n\
                                <li><a href="CardList.html#mobamas">カード一覧</a></li>\n\
                                <li><a href="Mobamas/NaganoArea/NaganoAreaBoss.html">長野エリアボスセリフ</a></li>\n\
                                <li><a href="Mobamas/PuchiDerella.html">ぷちでれら</a></li>\n\
                            </ul>\n\
                        </div>\n\
                        <div class="mega-col">\n\
                            <h4>イベント・ユニット</h4>\n\
                            <ul>\n\
                                <li><a href="Mobamas/Event/EventList.html">イベント一覧</a></li>\n\
                                <li><a href="Unit/UnitList.html?game=mobamas">ユニット一覧</a></li>\n\
                                <li><a href="Mobamas/SeasonalEvents/SeasonalEvents.html">季節イベント一覧</a></li>\n\
                            </ul>\n\
                        </div>\n\
                        <div class="mega-col">\n\
                            <h4>その他</h4>\n\
                            <ul>\n\
                                <li><a href="Mobamas/OtherCommu.html">その他コミュ・セリフ</a></li>\n\
                                <li><a href="Mobamas/OtherGameCenter.html">その他（ゲームセンター等）</a></li>\n\
                            </ul>\n\
                        </div>\n\
                    </div>\n\
                </div>\n\
            </li>\n\
            <li class="nav-item">\n\
                <a href="Deresute/index.html" class="nav-link">デレステ</a>\n\
                <div class="mega-menu">\n\
                    <div class="mega-inner">\n\
                        <div class="mega-col">\n\
                            <h4>カード・コミュ</h4>\n\
                            <ul>\n\
                                <li><a href="CardList.html#deresute">カード一覧</a></li>\n\
                                <li><a href="Deresute/Common/CommonCommu.html">共通コミュ・ボイス</a></li>\n\
                                <li><a href="Deresute/Event/EventList.html">メインイベント</a></li>\n\
                                <li><a href="Deresute/GuestCommu/GuestCommu.html">ゲスト参加コミュ＆映り込みカード</a></li>\n\
                            </ul>\n\
                        </div>\n\
                        <div class="mega-col">\n\
                            <h4>その他</h4>\n\
                            <ul>\n\
                                <li><a href="Deresute/CostumeList.html">衣装一覧</a></li>\n\
                                <li><a href="Deresute/CinderellaTheater/CinderellaTheater.html">シンデレラシアター</a></li>\n\
                                <li><a href="Deresute/Other/Other.html">その他</a></li>\n\
                            </ul>\n\
                        </div>\n\
                    </div>\n\
                </div>\n\
            </li>\n\
            <li class="nav-item">\n\
                <a href="#" class="nav-link">ポプマス</a>\n\
                <div class="mega-menu">\n\
                    <div class="mega-inner">\n\
                        <div class="mega-col">\n\
                            <h4>コンテンツ</h4>\n\
                            <ul>\n\
                                <li><a href="Popmas/Popmas.html">ポプマスまとめ</a></li>\n\
                            </ul>\n\
                        </div>\n\
                    </div>\n\
                </div>\n\
            </li>\n\
            <li class="nav-item">\n\
                <a href="#" class="nav-link">その他</a>\n\
                <div class="mega-menu">\n\
                    <div class="mega-inner">\n\
                        <div class="mega-col">\n\
                            <h4>コンテンツ</h4>\n\
                            <ul>\n\
                                <li><a href="General/SongList.html">歌唱曲</a></li>\n\
                                <li><a href="General/LiveList.html">ライブ</a></li>\n\
                                <li><a href="General/AnimeManga.html">アニメ・漫画</a></li>\n\
                                <li><a href="General/CollabList.html">コラボ</a></li>\n\
                                <li><a href="General/GeneralElection.html">総選挙</a></li>\n\
                                <li><a class="disabled">他アイドル呼称</a></li>\n\
                                <li><a href="General/References.html">参考・情報提供</a></li>\n\
                            </ul>\n\
                        </div>\n\
                    </div>\n\
                </div>\n\
            </li>\n\
        </ul>\n\
        <button class="sh-search-btn" id="sh-search-open-btn" aria-label="検索を開く"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></button>\n\
        <button class="hamburger" id="hamburger" aria-label="メニューを開く">\n\
            <span></span>\n\
            <span></span>\n\
            <span></span>\n\
        </button>\n\
    </nav>\n\
</header>\n\
<div class="mobile-menu-overlay" id="mobile-overlay"></div>\n\
<div class="mobile-menu" id="mobile-menu">\n\
        <ul class="mobile-nav">\n\
            <li class="mobile-item">\n\
                <div class="mobile-item-header">\n\
                    <span>モバマス</span>\n\
                    <button class="accordion-toggle" aria-label="展開">＋</button>\n\
                </div>\n\
                <ul class="mobile-submenu">\n\
                    <li><a href="CardList.html#mobamas">カード一覧</a></li>\n\
                    <li><a href="Mobamas/NaganoArea/NaganoAreaBoss.html">長野エリアボスセリフ</a></li>\n\
                    <li><a href="Mobamas/PuchiDerella.html">ぷちでれら</a></li>\n\
                    <li><a href="Mobamas/Event/EventList.html">イベント一覧</a></li>\n\
                    <li><a href="Unit/UnitList.html?game=mobamas">ユニット一覧</a></li>\n\
                    <li><a href="Mobamas/SeasonalEvents/SeasonalEvents.html">季節イベント一覧</a></li>\n\
                    <li><a href="Mobamas/OtherCommu.html">その他コミュ・セリフ</a></li>\n\
                    <li><a href="Mobamas/OtherGameCenter.html">その他（ゲームセンター等）</a></li>\n\
                </ul>\n\
            </li>\n\
            <li class="mobile-item">\n\
                <div class="mobile-item-header">\n\
                    <span>デレステ</span>\n\
                    <button class="accordion-toggle" aria-label="展開">＋</button>\n\
                </div>\n\
                <ul class="mobile-submenu">\n\
                    <li><a href="CardList.html#deresute">カード一覧</a></li>\n\
                    <li><a href="Deresute/Common/CommonCommu.html">共通コミュ・ボイス</a></li>\n\
                    <li><a href="Deresute/Event/EventList.html">メインイベント</a></li>\n\
                    <li><a href="Deresute/GuestCommu/GuestCommu.html">ゲスト参加コミュ＆映り込みカード</a></li>\n\
                    <li><a href="Deresute/CostumeList.html">衣装一覧</a></li>\n\
                    <li><a href="Deresute/CinderellaTheater/CinderellaTheater.html">シンデレラシアター</a></li>\n\
                    <li><a href="Deresute/Other/Other.html">その他</a></li>\n\
                </ul>\n\
            </li>\n\
            <li class="mobile-item">\n\
                <div class="mobile-item-header">\n\
                    <span>ポプマス</span>\n\
                    <button class="accordion-toggle" aria-label="展開">＋</button>\n\
                </div>\n\
                <ul class="mobile-submenu">\n\
                    <li><a href="Popmas/Popmas.html">ポプマスまとめ</a></li>\n\
                </ul>\n\
            </li>\n\
            <li class="mobile-item">\n\
                <div class="mobile-item-header">\n\
                    <span>その他</span>\n\
                    <button class="accordion-toggle" aria-label="展開">＋</button>\n\
                </div>\n\
                <ul class="mobile-submenu">\n\
                    <li><a href="General/SongList.html">歌唱曲</a></li>\n\
                    <li><a href="General/LiveList.html">ライブ</a></li>\n\
                    <li><a href="General/AnimeManga.html">アニメ・漫画</a></li>\n\
                    <li><a href="General/CollabList.html">コラボ</a></li>\n\
                    <li><a href="General/GeneralElection.html">総選挙</a></li>\n\
                    <li><a class="disabled">他アイドル呼称</a></li>\n\
                    <li><a href="General/References.html">参考・情報提供</a></li>\n\
                </ul>\n\
            </li>\n\
        </ul>\n\
    </div>\n\
</div>';

    // Zen Maru Gothic フォントを全ページで有効化
    (function() {
        if (!document.querySelector('link[href*="Zen+Maru+Gothic"]')) {
            var fl = document.createElement('link');
            fl.rel = 'stylesheet';
            fl.href = 'https://fonts.googleapis.com/css2?family=Yusei+Magic&family=Zen+Maru+Gothic:wght@400;500;700;900&display=swap';
            document.head.appendChild(fl);
        }
    })();

    // ヘッダーをこのscriptタグの直前に同期注入（フラッシュなし）
    var me = document.currentScript;
    me.insertAdjacentHTML('beforebegin', HEADER_HTML);

    // 注入後すぐにイベント設定（DOMContentLoaded不要：要素は既にDOM上にある）
    var header   = document.getElementById('site-header');
    var hamburger = document.getElementById('hamburger');
    var mobileMenu = document.getElementById('mobile-menu');
    var overlay  = document.getElementById('mobile-overlay');
    var lastScrollY = 0;

    window.addEventListener('scroll', function () {
        var y = window.scrollY;
        if (y <= 0) {
            header.classList.remove('header-hidden');
        } else if (y > lastScrollY + 4) {
            header.classList.add('header-hidden');
            closeMenu();
        } else if (y < lastScrollY - 4) {
            header.classList.remove('header-hidden');
        }
        lastScrollY = y;
    }, { passive: true });

    function openMenu() {
        hamburger.classList.add('active');
        mobileMenu.classList.add('active');
        overlay.classList.add('active');
        document.body.classList.add('menu-open');
        hamburger.setAttribute('aria-label', 'メニューを閉じる');
    }

    function closeMenu() {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
        overlay.classList.remove('active');
        document.body.classList.remove('menu-open');
        hamburger.setAttribute('aria-label', 'メニューを開く');
    }

    hamburger.addEventListener('click', function () {
        if (mobileMenu.classList.contains('active')) {
            closeMenu();
        } else {
            openMenu();
        }
    });

    overlay.addEventListener('click', closeMenu);

    document.querySelectorAll('.accordion-toggle').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var submenu = btn.closest('.mobile-item').querySelector('.mobile-submenu');
            var isOpen = btn.classList.contains('open');
            document.querySelectorAll('.accordion-toggle.open').forEach(function (b) {
                b.classList.remove('open');
                b.closest('.mobile-item').querySelector('.mobile-submenu').classList.remove('open');
            });
            if (!isOpen) {
                btn.classList.add('open');
                submenu.classList.add('open');
            }
        });
    });

    // ─────────────────────────────────────────────
    // グローバル検索機能
    // ─────────────────────────────────────────────

    // 検索オーバーレイ HTML
    // ─────────────────────────────────────────────
    // サイト共通フッター
    // ─────────────────────────────────────────────
    var FOOTER_HTML = [
        '<footer class="sh-site-footer">',
        '  <div class="sh-site-footer-inner">',
        '    <a class="sh-footer-x-btn" id="sh-footer-x-btn" href="#" target="_blank" rel="noopener noreferrer">',
        '      <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.742l7.727-8.834L1.254 2.25H8.08l4.262 5.633 5.902-5.633Zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
        '      Xでシェア',
        '    </a>',
        '    <div class="sh-footer-disclaimer">',
        '      <p>このサイトはアイドルマスター シンデレラガールズの非公式ファンサイトです。<br>バンダイナムコエンターテインメント株式会社および各関連企業・団体とは一切関係ありません。</p>',
        '      <p class="sh-footer-copyright">THE IDOLM@STER™ &amp; ©Bandai Namco Entertainment Inc.</p>',
        '    </div>',
        '  </div>',
        '</footer>'
    ].join('\n');

    var SEARCH_OVERLAY_HTML = [
        '<div class="sh-search-overlay" id="sh-search-overlay" aria-hidden="true">',
        '  <div class="sh-search-box">',
        '    <span class="sh-search-icon"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></span>',
        '    <input type="text" class="sh-search-input" id="sh-search-input"',
        '      placeholder="キーワードを入力..." autocomplete="off">',
        '    <select class="sh-search-idol-select" id="sh-search-idol">',
        '      <option value="">すべてのアイドル</option>',
        '    </select>',
        '    <button class="sh-search-close" id="sh-search-close" aria-label="検索を閉じる">✕</button>',
        '  </div>',
        '  <div class="sh-search-type-bar">',
        '    <button class="sh-search-type-btn active" data-type="">すべて</button>',
        '    <button class="sh-search-type-btn" data-type="card">カード</button>',
        '    <button class="sh-search-type-btn" data-type="unit">ユニット</button>',
        '    <button class="sh-search-type-btn" data-type="story">ストーリー</button>',
        '  </div>',
        '  <div class="sh-search-results" id="sh-search-results">',
        '    <div class="sh-search-hint">キーワードを入力するか、アイドルを選択してください</div>',
        '  </div>',
        '</div>'
    ].join('\n');

    var _searchIndex = null;
    var _searchLoading = false;
    var _searchTypeFilter = ''; // '' = すべて, 'card' | 'unit' | 'story'

    function escHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function normalize(str) {
        try { return str.normalize('NFKC').toLowerCase(); }
        catch (e) { return str.toLowerCase(); }
    }

    function populateIdolSelect(csvText) {
        var select = document.getElementById('sh-search-idol');
        if (!select) return;
        var lines = csvText.replace(/^﻿/, '').trim().split('\n');
        for (var i = 1; i < lines.length; i++) {
            var cols = lines[i].split(',');
            var short = cols[1] ? cols[1].trim() : '';
            if (short) {
                var opt = document.createElement('option');
                opt.value = short;
                opt.textContent = short;
                select.appendChild(opt);
            }
        }
    }

    function loadSearchData(callback) {
        if (_searchIndex) { callback(); return; }
        if (_searchLoading) return;
        _searchLoading = true;

        var resultEl = document.getElementById('sh-search-results');
        if (resultEl) resultEl.innerHTML = '<div class="sh-search-hint">読み込み中…</div>';

        var idxDone = false, idolDone = false;
        var idx = null, idolCsv = null;

        function tryFinish() {
            if (!idxDone || !idolDone) return;
            if (idx) _searchIndex = idx;
            if (idolCsv) populateIdolSelect(idolCsv);
            _searchLoading = false;
            callback();
        }

        fetch('data/search-index.json').then(function(r) {
            return r.ok ? r.json() : null;
        }).then(function(data) {
            idx = data;
            idxDone = true;
            tryFinish();
        }).catch(function() {
            idxDone = true;
            tryFinish();
        });

        fetch('data/cgss_idols.csv').then(function(r) {
            return r.ok ? r.text() : null;
        }).then(function(text) {
            idolCsv = text;
            idolDone = true;
            tryFinish();
        }).catch(function() {
            idolDone = true;
            tryFinish();
        });
    }

    function runSearch() {
        var input  = document.getElementById('sh-search-input');
        var idol   = document.getElementById('sh-search-idol');
        var q      = input ? input.value : '';
        var idolVal= idol  ? idol.value   : '';

        if (!q.trim() && !idolVal) {
            var r = document.getElementById('sh-search-results');
            if (r) r.innerHTML = '<div class="sh-search-hint">キーワードを入力するか、アイドルを選択してください</div>';
            return;
        }

        if (!_searchIndex) {
            loadSearchData(runSearch);
            return;
        }

        var qn = normalize(q.trim());
        var results = (_searchIndex || []).filter(function(entry) {
            // タイプフィルター
            if (_searchTypeFilter && entry.type !== _searchTypeFilter) return false;
            // アイドルフィルター
            if (idolVal) {
                var parts = (entry.idol || '').split(' ');
                if (parts.indexOf(idolVal) === -1) return false;
            }
            // キーワード検索
            if (qn) {
                var searchable = normalize(
                    (entry.title   || '') + ' ' +
                    (entry.text    || '') + ' ' +
                    (entry.idol    || '') + ' ' +
                    (entry.context || '')
                );
                if (searchable.indexOf(qn) === -1) return false;
            }
            return true;
        }).slice(0, 120);

        renderSearchResults(results);
    }

    function renderSearchResults(results) {
        var container = document.getElementById('sh-search-results');
        if (!container) return;

        if (!results || results.length === 0) {
            container.innerHTML = '<div class="sh-search-hint">見つかりませんでした</div>';
            return;
        }

        var TYPE_LABELS = { card: 'CARD', unit: 'UNIT', story: 'STORY' };
        var showGroups = !_searchTypeFilter; // タイプ絞り込み中はグループ見出し非表示
        var groups = { card: [], unit: [], story: [] };
        results.forEach(function(r) {
            if (groups[r.type]) groups[r.type].push(r);
        });

        var html = '';
        ['card', 'unit', 'story'].forEach(function(type) {
            var list = groups[type];
            if (!list || list.length === 0) return;
            if (showGroups) {
                html += '<div class="sh-search-group"><span class="sh-search-group-label">' +
                        TYPE_LABELS[type] + '</span></div>';
            }
            list.forEach(function(item) {
                var excerpt = item.text.length > 60 ? item.text.slice(0, 60) + '…' : item.text;
                html += '<a class="sh-search-item" href="' + escHtml(item.url) + '">' +
                        '<span class="sh-search-item-title">' + escHtml(item.title) + '</span>' +
                        '<span class="sh-search-item-text">「' + escHtml(excerpt) + '」</span>' +
                        '</a>';
            });
        });
        container.innerHTML = html;
    }

    function openSearch() {
        var overlay = document.getElementById('sh-search-overlay');
        if (!overlay) return;
        overlay.classList.add('active');
        overlay.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        var input = document.getElementById('sh-search-input');
        if (input) {
            input.focus();
            // データを先読み
            if (!_searchIndex && !_searchLoading) {
                loadSearchData(function() {
                    runSearch();
                });
            }
        }
    }

    function closeSearch() {
        var overlay = document.getElementById('sh-search-overlay');
        if (!overlay) return;
        overlay.classList.remove('active');
        overlay.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    // オーバーレイ・フッターを body に挿入 + イベント設定
    document.addEventListener('DOMContentLoaded', function () {
        document.body.insertAdjacentHTML('beforeend', SEARCH_OVERLAY_HTML);

        // フッター注入
        document.body.insertAdjacentHTML('beforeend', FOOTER_HTML);
        var xBtn = document.getElementById('sh-footer-x-btn');
        if (xBtn) {
            var shareUrl  = encodeURIComponent(window.location.href);
            var shareText = encodeURIComponent(document.title + ' | SugarHeartDB');
            xBtn.href = 'https://twitter.com/intent/tweet?url=' + shareUrl + '&text=' + shareText;
        }

        var openBtn  = document.getElementById('sh-search-open-btn');
        var closeBtn = document.getElementById('sh-search-close');
        var overlay  = document.getElementById('sh-search-overlay');
        var input    = document.getElementById('sh-search-input');
        var idolSel  = document.getElementById('sh-search-idol');

        if (openBtn)  openBtn.addEventListener('click',  openSearch);
        if (closeBtn) closeBtn.addEventListener('click', closeSearch);

        // オーバーレイ背景クリックで閉じる
        if (overlay) {
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) closeSearch();
            });
        }

        // ESCキーで閉じる
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeSearch();
        });

        // 入力時に検索実行
        var searchTimer;
        if (input) {
            input.addEventListener('input', function() {
                clearTimeout(searchTimer);
                searchTimer = setTimeout(runSearch, 220);
            });
        }
        if (idolSel) {
            idolSel.addEventListener('change', function() {
                runSearch();
            });
        }

        // タイプフィルターボタン
        document.querySelectorAll('.sh-search-type-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.sh-search-type-btn').forEach(function(b) {
                    b.classList.remove('active');
                });
                btn.classList.add('active');
                _searchTypeFilter = btn.dataset.type || '';
                runSearch();
            });
        });
    });

})();
