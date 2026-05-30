/**
 * SugarHeartDB 共通スクリプト
 * タブ切り替え・アコーディオン・ライトボックス・画像サイクラーを一元管理
 */

/* ============================================================
   タブ切り替え
   - .tab-group 内でスコープして動作（グループをまたがない）
   - 呼び出し: onclick="switchTab(this,'タブID')"
============================================================ */
function switchTab(btn, tab) {
    var g = btn.closest('.tab-group');
    g.querySelectorAll('.tab-item').forEach(function (b) { b.classList.remove('active'); });
    g.querySelectorAll('.tab-panel').forEach(function (c) { c.classList.remove('active'); });
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
    img.style.cursor = images.length > 1 ? 'pointer' : 'default';
    if (images.length <= 1) return;
    var idx = 0;
    img.addEventListener('click', function () {
        idx = (idx + 1) % images.length;
        img.style.opacity = '0.5';
        setTimeout(function () {
            img.src = images[idx];
            img.style.opacity = '1';
            if (counter) counter.textContent = idx + 1;
        }, 150);
    });
}

/* ============================================================
   DOMContentLoaded 自動初期化
============================================================ */
(function () {
    document.addEventListener('DOMContentLoaded', function () {

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

        /* ep-block アコーディオン (PuchiDerela) */
        document.querySelectorAll('.ep-block .ep-head').forEach(function (h) {
            h.style.cursor = 'pointer';
            h.addEventListener('click', function () {
                h.parentElement.classList.toggle('open');
            });
        });

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
