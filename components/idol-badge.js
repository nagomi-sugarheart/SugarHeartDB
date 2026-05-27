/**
 * idol-badge.js
 * data/cgss_idols.csv を読み込み、会話バッジにパーソナルカラーを適用する。
 * 対応形式: .script-row .who / .ud-dialogue .speaker / .dialog .body .speaker
 */
(function () {
  'use strict';

  const ATTR_COLORS = {
    'キュート':   '#ef2782',
    'クール':     '#006aff',
    'パッション': '#f49207',
  };
  const ATTR_ORDER = ['キュート', 'クール', 'パッション'];

  /** HEXカラーの輝度からテキスト色を決定（明るい背景→濃いテキスト） */
  function textColor(hex) {
    if (!hex || hex.length < 7) return '#fff';
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.75 ? '#222' : '#fff';
  }

  function applyStyle(el, bg, txt, shadow) {
    el.style.background = bg;
    el.style.color = txt;
    if (shadow) el.style.textShadow = '0 1px 2px rgba(0,0,0,0.55)';
    else el.style.textShadow = '';
  }

  /**
   * nameStr: 「心」「心・千鶴」「一同」などの文字列
   * idolMap: { shortName: { color, attribute } }
   */
  function applyBadge(el, nameStr, idolMap) {
    if (!nameStr || nameStr.trim() === '') return;

    const names = nameStr.split('・').map(n => n.trim()).filter(Boolean);

    if (names.length === 1) {
      const name = names[0];

      // 特殊: 一同・アイドル他 → 3属性カラー斜め分割
      if (name === '一同' || name === 'アイドル他') {
        applyStyle(el,
          `linear-gradient(100deg, ${ATTR_COLORS['キュート']} 33.33%, ${ATTR_COLORS['クール']} 33.33% 66.67%, ${ATTR_COLORS['パッション']} 66.67%)`,
          '#fff', true);
        return;
      }

      const idol = idolMap[name];
      if (!idol) return; // CSV未収録の場合はCSS fallbackに任せる
      applyStyle(el, idol.color, textColor(idol.color), false);

    } else if (names.length === 2) {
      // 2人同時: 100degの斜め分割
      const c1 = (idolMap[names[0]] || {}).color || '#aaa';
      const c2 = (idolMap[names[1]] || {}).color || '#aaa';
      applyStyle(el,
        `linear-gradient(100deg, ${c1} 50%, ${c2} 50%)`,
        '#fff', true);

    } else {
      // 3人以上: 属性カラーで1〜3色、キュート▶クール▶パッション優先
      const attrSet = new Set();
      for (const name of names) {
        if (idolMap[name]) attrSet.add(idolMap[name].attribute);
      }
      const attrs = ATTR_ORDER.filter(a => attrSet.has(a));
      let bg;
      if (attrs.length === 0) {
        bg = `linear-gradient(100deg, ${ATTR_COLORS['キュート']} 33.33%, ${ATTR_COLORS['クール']} 33.33% 66.67%, ${ATTR_COLORS['パッション']} 66.67%)`;
      } else if (attrs.length === 1) {
        bg = ATTR_COLORS[attrs[0]];
      } else if (attrs.length === 2) {
        bg = `linear-gradient(100deg, ${ATTR_COLORS[attrs[0]]} 50%, ${ATTR_COLORS[attrs[1]]} 50%)`;
      } else {
        bg = `linear-gradient(100deg, ${ATTR_COLORS['キュート']} 33.33%, ${ATTR_COLORS['クール']} 33.33% 66.67%, ${ATTR_COLORS['パッション']} 66.67%)`;
      }
      applyStyle(el, bg, '#fff', true);
    }
  }

  async function init() {
    let res;
    try {
      res = await fetch('data/cgss_idols.csv');
    } catch (e) {
      return; // ローカルファイルアクセス不可 or ネットワークエラー
    }
    if (!res.ok) return;

    const raw = await res.text();
    // BOM除去 + 行分割
    const lines = raw.replace(/^﻿/, '').trim().split('\n');

    // CSVパース: アイドル名,名前,属性,属性カラー,イメージカラー
    const idolMap = {};
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(',');
      if (cols.length < 5) continue;
      const shortName = cols[1].trim();
      const attribute = cols[2].trim();
      const color = cols[4].trim();
      if (shortName && color) {
        idolMap[shortName] = { color, attribute };
      }
    }

    // 1. .script-row .who（Mobamasページ）
    //    data-who はrow要素に付く。stage-directionはスキップ
    document.querySelectorAll('.script-row:not(.stage-direction)[data-who]').forEach(row => {
      const nameStr = row.dataset.who;
      if (!nameStr) return;
      const whoEl = row.querySelector('.who');
      if (whoEl) applyBadge(whoEl, nameStr, idolMap);
    });

    // 2. .ud-dialogue .speaker（Unitページ）
    //    data-who 属性があればそれを優先、なければ要素のテキストで照合
    document.querySelectorAll('.ud-dialogue .speaker').forEach(el => {
      const nameStr = el.dataset.who || el.textContent.trim();
      applyBadge(el, nameStr, idolMap);
    });

    // 3. .dialog .body .speaker（KirakiraModelChallenge等）
    //    CSSでも定義済みだが、JSで一元管理するためここでも適用
    document.querySelectorAll('.dialog .body .speaker[data-who]').forEach(el => {
      const nameStr = el.dataset.who;
      if (!nameStr || nameStr === 'P' || nameStr === 'ナレーション') return;
      applyBadge(el, nameStr, idolMap);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
