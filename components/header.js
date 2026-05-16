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
                                <li><a href="Mobamas/PuchiDerela.html">ぷちでれら</a></li>\n\
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
                                <li><a class="disabled">シンデレラシアター</a></li>\n\
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
                                <li><a href="Popmas/BasicInfo.html">基本情報</a></li>\n\
                                <li><a href="Popmas/FinalEventLines.html">ファイナルイベントセリフ</a></li>\n\
                                <li><a href="Popmas/Other.html">その他</a></li>\n\
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
                    <li><a href="Mobamas/PuchiDerela.html">ぷちでれら</a></li>\n\
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
                    <li><a class="disabled">シンデレラシアター</a></li>\n\
                    <li><a href="Deresute/Other/Other.html">その他</a></li>\n\
                </ul>\n\
            </li>\n\
            <li class="mobile-item">\n\
                <div class="mobile-item-header">\n\
                    <span>ポプマス</span>\n\
                    <button class="accordion-toggle" aria-label="展開">＋</button>\n\
                </div>\n\
                <ul class="mobile-submenu">\n\
                    <li><a href="Popmas/BasicInfo.html">基本情報</a></li>\n\
                    <li><a href="Popmas/FinalEventLines.html">ファイナルイベントセリフ</a></li>\n\
                    <li><a href="Popmas/Other.html">その他</a></li>\n\
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
})();
