/**
 * SugarHeartDB 共通スクリプト
 * タブ切り替え・アコーディオン・ライトボックス・画像サイクラーを一元管理
 */

/* ============================================================
   タブ切り替え
   - .tab-group 内でスコープして動作（グループをまたがない）
   - .tab-group の入れ子にも対応（自分のグループ直属のタブのみ切り替える）
   - 呼び出し: onclick="switchTab(this,'タブID')"
============================================================ */
function switchTab(btn, tab) {
    var g = btn.closest('.tab-group');
    g.querySelectorAll('.tab-item').forEach(function (b) {
        if (b.closest('.tab-group') === g) b.classList.remove('active');
    });
    g.querySelectorAll('.tab-panel').forEach(function (c) {
        if (c.closest('.tab-group') === g) c.classList.remove('active');
    });
    btn.classList.add('active');
    g.querySelector('.tab-panel[data-tab="' + tab + '"]').classList.add('active');
}

/* ============================================================
   v2 ダイアログタブ切り替え
   - v2 カード詳細ページのセリフタブで使用
   - 呼び出し: onclick="v2SwitchTab(インデックス, this)"
============================================================ */
function v2SwitchTab(idx, btn) {
    var tabs = btn.parentElement.querySelectorAll('.v2-dialogue-tab');
    var contents = btn.closest('.v2-dialogue-block').querySelectorAll('.v2-dialogue-content');
    tabs.forEach(function (t) { t.classList.remove('active'); });
    contents.forEach(function (c) { c.style.display = 'none'; });
    btn.classList.add('active');
    contents[idx].style.display = '';
}

/* ============================================================
   イベント一覧 並び替え
   - .event-table 内の article.event-row を日付順に並び替える
   - data-date があれば日付で、無ければ初期の並び順を基準にする
   - 呼び出し: onclick="toggleSort(this)"
============================================================ */
function toggleSort(btn) {
    var table = document.querySelector('.event-table');
    if (!btn || !table) return;
    var rows = Array.from(table.querySelectorAll('article.event-row'));
    rows.forEach(function (r, i) {
        if (!r.dataset.sortKey) {
            r.dataset.sortKey = r.dataset.date || ('idx-' + String(i).padStart(4, '0'));
        }
    });
    var newOrder = btn.dataset.order === 'asc' ? 'desc' : 'asc';
    rows.sort(function (a, b) {
        return newOrder === 'asc'
            ? a.dataset.sortKey.localeCompare(b.dataset.sortKey)
            : b.dataset.sortKey.localeCompare(a.dataset.sortKey);
    });
    rows.forEach(function (r) { table.appendChild(r); });
    btn.dataset.order = newOrder;
    btn.textContent = newOrder === 'asc' ? '新しい順 ▼' : '古い順 ▲';
}

/* ============================================================
   イベント一覧 検索・並び替え（拡張版）
   - .event-table 内の article.event-row を対象にする
   - 検索: data-name（無ければ行テキスト）に対する部分一致（大文字小文字/全半角無視）
   - 並び替え: key='date'（日付） / 'name'（イベント名）。同じボタン再クリックで昇順/降順トグル
   - 呼び出し: oninput="filterEventList(this.value)" / onclick="sortEventList(this,'date')"
============================================================ */
function filterEventList(q) {
    var table = document.querySelector('.event-table');
    if (!table) return;
    q = (q || '').trim().toLowerCase();
    var rows = table.querySelectorAll('article.event-row');
    var shown = 0;
    rows.forEach(function (r) {
        var hay = (r.dataset.name || r.textContent || '').toLowerCase();
        var hit = !q || hay.indexOf(q) !== -1;
        r.style.display = hit ? '' : 'none';
        if (hit) shown++;
    });
    var empty = document.getElementById('event-empty');
    if (empty) empty.style.display = shown ? 'none' : '';
    var cnt = document.getElementById('event-count');
    if (cnt) cnt.textContent = shown;
}

function sortEventList(btn, key) {
    var table = document.querySelector('.event-table');
    if (!btn || !table) return;
    var rows = Array.from(table.querySelectorAll('article.event-row'));
    rows.forEach(function (r, i) {
        if (!r.dataset.origIdx) r.dataset.origIdx = 'idx-' + String(i).padStart(4, '0');
    });
    // 同じキーの再クリックでトグル、別キーへ切り替えたら既定方向から
    var active = btn.dataset.sortKey === key;
    var order = active ? (btn.dataset.order === 'asc' ? 'desc' : 'asc')
                       : (key === 'name' ? 'asc' : 'desc');
    rows.sort(function (a, b) {
        var av, bv;
        if (key === 'name') {
            av = a.dataset.name || a.textContent;
            bv = b.dataset.name || b.textContent;
            var c = av.localeCompare(bv, 'ja');
            return order === 'asc' ? c : -c;
        }
        av = a.dataset.date || a.dataset.origIdx;
        bv = b.dataset.date || b.dataset.origIdx;
        return order === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
    });
    rows.forEach(function (r) { table.appendChild(r); });
    // ボタン状態を更新（同じ並び替えグループ内でトグル）
    var grp = btn.closest('.unit-sort-group') || document;
    grp.querySelectorAll('.unit-sort-btn').forEach(function (b) {
        b.classList.remove('active');
    });
    btn.classList.add('active');
    btn.dataset.sortKey = key;
    btn.dataset.order = order;
    var labels = {
        'date-desc': '新しい順 ▼', 'date-asc': '古い順 ▲',
        'name-asc': '名前順 あ→ん', 'name-desc': '名前順 ん→あ'
    };
    if (btn.dataset.baseLabel) {
        btn.textContent = labels[key + '-' + order] || btn.dataset.baseLabel;
    }
}

/* ============================================================
   画像サイクラー
   - 呼び出し: initV2Cycler(画像パス配列, img要素ID, カウンター要素ID)
   - カウンターIDが 'xxx-counter' なら 'xxx-total' を自動探索
============================================================ */
function initV2Cycler(images, imgId, counterId) {
    var img     = document.getElementById(imgId);
    var counter = document.getElementById(counterId);
    var total   = document.getElementById(counterId.replace(/-counter$/, '-total'));
    if (total) total.textContent = images.length;
    if (!img) return;

    function isVideo(url) { return url.indexOf('/video/upload/') !== -1; }

    // 動画URLが含まれる場合のみ <video> 要素を生成
    var vid = null;
    if (images.some(isVideo)) {
        vid = document.createElement('video');
        vid.autoplay = true;
        vid.loop = true;
        vid.muted = true;
        vid.setAttribute('playsinline', '');
        vid.setAttribute('disablePictureInPicture', '');
        vid.style.display = 'none';
        img.parentNode.insertBefore(vid, img.nextSibling);
    }

    var idx = 0;

    function showCurrent() {
        var url = images[idx];
        if (isVideo(url)) {
            img.style.display = 'none';
            if (vid) {
                vid.src = url;
                vid.style.display = '';
                vid.play().catch(function(){});
            }
        } else {
            if (vid) { vid.pause(); vid.src = ''; vid.style.display = 'none'; }
            img.src = url;
            img.style.display = '';
        }
        if (counter) counter.textContent = idx + 1;
    }

    img.style.cursor = images.length > 1 ? 'pointer' : 'default';
    if (vid) vid.style.cursor = images.length > 1 ? 'pointer' : 'default';
    if (images.length <= 1) return;

    function advance() {
        var cur = (vid && vid.style.display !== 'none') ? vid : img;
        cur.style.opacity = '0.5';
        idx = (idx + 1) % images.length;
        setTimeout(function () {
            showCurrent();
            img.style.opacity = '1';
            if (vid) vid.style.opacity = '1';
        }, 150);
    }

    img.addEventListener('click', advance);
    if (vid) vid.addEventListener('click', advance);
}

/* ============================================================
   DOMContentLoaded 自動初期化
============================================================ */
(function () {
    document.addEventListener('DOMContentLoaded', function () {

        /* v2 カード画像サイクラー（#v2-card-main-img の data-images から自動初期化） */
        var cyclerImg = document.getElementById('v2-card-main-img');
        if (cyclerImg && cyclerImg.dataset.images) {
            initV2Cycler(cyclerImg.dataset.images.split('|'), 'v2-card-main-img', 'v2-img-counter');
        }

        /* ユニットページ DURATION（#ud-duration の data-debut から経過年月を表示） */
        var dur = document.getElementById('ud-duration');
        if (dur && dur.dataset.debut) {
            var debut = new Date(dur.dataset.debut);
            var now = new Date();
            var y = now.getFullYear() - debut.getFullYear();
            var m = now.getMonth() - debut.getMonth();
            if (m < 0) { y--; m += 12; }
            dur.textContent = y + 'YEAR ' + m + 'MONTH';
        }

        /* lv-accord アコーディオン */
        document.querySelectorAll('.lv-accord .lv-head').forEach(function (h) {
            h.style.cursor = 'pointer';
            h.addEventListener('click', function () {
                h.parentElement.classList.toggle('open');
            });
        });

        /* v2 アコーディオン */
        document.querySelectorAll('.v2-accord-head').forEach(function (h) {
            h.addEventListener('click', function () {
                h.parentElement.classList.toggle('open');
            });
        });

        /* URL ハッシュで v2-accord を自動展開してスクロール */
        if (location.hash) {
            try {
                var hashTarget = document.querySelector(location.hash);
                if (hashTarget && hashTarget.classList.contains('v2-accord')) {
                    hashTarget.classList.add('open');
                    setTimeout(function () {
                        hashTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 50);
                }
            } catch (e) {}
        }

        /* ep-block アコーディオン (PuchiDerella) */
        document.querySelectorAll('.ep-block .ep-head').forEach(function (h) {
            h.style.cursor = 'pointer';
            h.addEventListener('click', function () {
                h.parentElement.classList.toggle('open');
            });
        });

        /* イベント一覧 並び替えボタンの初期化＋既定並び替え適用 */
        var evDefaultBtn = document.querySelector('.unit-sort-group .unit-sort-btn[data-default]');
        if (evDefaultBtn && document.querySelector('.event-table')) {
            document.querySelectorAll('.unit-sort-group .unit-sort-btn').forEach(function (b) {
                b.dataset.baseLabel = b.textContent.trim();
            });
            sortEventList(evDefaultBtn, evDefaultBtn.dataset.sortKeyName || 'date');
        }

        /* ライトボックス（#sh-lightbox が存在するページのみ） */
        var lb = document.getElementById('sh-lightbox');
        if (!lb) return;
        var lbImg   = document.getElementById('sh-lightbox-img');
        var lbClose = document.getElementById('sh-lightbox-close');

        function openLb(src, alt) {
            if (!lbImg) return;
            lbImg.src = src;
            lbImg.alt = alt || '';
            lb.classList.add('open');
            document.body.style.overflow = 'hidden';
        }
        function closeLb() {
            lb.classList.remove('open');
            document.body.style.overflow = '';
        }

        document.querySelectorAll('.ev-shot img, .pm-gallery-img, .lightbox-trigger').forEach(function (img) {
            img.addEventListener('click', function (e) { e.stopPropagation(); openLb(img.src, img.alt); });
        });
        lb.addEventListener('click', closeLb);
        if (lbClose) lbClose.addEventListener('click', function (e) { e.stopPropagation(); closeLb(); });
        if (lbImg)   lbImg.addEventListener('click', function (e) { e.stopPropagation(); });
        document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeLb(); });
    });
})();
