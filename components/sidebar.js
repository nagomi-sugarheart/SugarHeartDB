/* ============================================================
   SugarHeartDB カード詳細 共通サイドバー（カード一覧）コンポーネント
   カードを追加・変更するときはこのファイルの CARDS だけ編集すればOK
   - href は <base href="/SugarHeartDB/"> からの相対パス
   - アイコンは href の「.html → Icon」置換で Cloudinary public_id を自動導出
   ============================================================ */
(function () {
    var CLOUDINARY = 'https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/';

    var CARDS = [
        { href: 'Mobamas/SatoShin/SatoShin.html', name: '佐藤心' },
        { href: 'Mobamas/SatoShin+/SatoShin+.html', name: '佐藤心+' },
        { href: 'Mobamas/TBSweetie/TBSweetie.html', name: '[T.B.ｽｳｨｰﾃｨｰ]佐藤心' },
        { href: 'Mobamas/TBSweetie+/TBSweetie+.html', name: '[T.B.ｽｳｨｰﾃｨｰ]佐藤心+' },
        { href: 'Mobamas/NextStarIC+/NextStarIC+.html', name: '[ﾈｸｽﾄｽﾀｰI.C]佐藤心+' },
        { href: 'Mobamas/HeartModel/HeartModel.html', name: '[ﾊｰﾄ･ﾓﾃﾞﾙ]佐藤心' },
        { href: 'Mobamas/HeartModel+/HeartModel+.html', name: '[ﾊｰﾄ･ﾓﾃﾞﾙ]佐藤心+' },
        { href: 'Mobamas/HeartModel/HeartModelS.html', name: '[ﾊｰﾄ･ﾓﾃﾞﾙ･S]佐藤心' },
        { href: 'Mobamas/HeartModel+/HeartModelS+.html', name: '[ﾊｰﾄ･ﾓﾃﾞﾙ･S]佐藤心+' },
        { href: 'Mobamas/AngelHeart/AngelHeart.html', name: '[えんじぇるはぁと]佐藤心' },
        { href: 'Mobamas/AngelHeart+/AngelHeart+.html', name: '[えんじぇるはぁと]佐藤心+' },
        { href: 'Mobamas/HeartNoYomeiri/HeartNoYomeiri.html', name: '[はぁとの嫁入り]佐藤心' },
        { href: 'Mobamas/HeartNoYomeiri+/HeartNoYomeiri+.html', name: '[はぁとの嫁入り]佐藤心+' },
        { href: 'Mobamas/SweetieRoyal/SweetieRoyal.html', name: '[ｽｳｨｰﾃｨｰ･ﾛﾜｲﾔﾙ]佐藤心' },
        { href: 'Mobamas/SweetieRoyal+/SweetieRoyal+.html', name: '[ｽｳｨｰﾃｨｰ･ﾛﾜｲﾔﾙ]佐藤心+' },
        { href: 'Mobamas/WorkingSweetie/WorkingSweetie.html', name: '[ﾜｰｷﾝｸﾞ･ｽｳｨｰﾃｨｰ]佐藤心' },
        { href: 'Mobamas/WorkingSweetie+/WorkingSweetie+.html', name: '[ﾜｰｷﾝｸﾞ･ｽｳｨｰﾃｨｰ]佐藤心+' },
        { href: 'Mobamas/TokonatsuParadise/TokonatsuParadise.html', name: '[常夏ﾊﾟﾗﾀﾞｲｽ]佐藤心' },
        { href: 'Mobamas/TokonatsuParadise+/TokonatsuParadise+.html', name: '[常夏ﾊﾟﾗﾀﾞｲｽ]佐藤心+' },
        { href: 'Mobamas/ChikuttoSweetie/ChikuttoSweetie.html', name: '[ﾁｸｯとｽｳｨｰﾃｨｰ]佐藤心' },
        { href: 'Mobamas/ChikuttoSweetie+/ChikuttoSweetie+.html', name: '[ﾁｸｯとｽｳｨｰﾃｨｰ]佐藤心+' },
        { href: 'Mobamas/6thAnniversary/6thAnniversary.html', name: '[6thｱﾆﾊﾞｰｻﾘｰ]佐藤心' },
        { href: 'Mobamas/6thAnniversary+/6thAnniversary+.html', name: '[6thｱﾆﾊﾞｰｻﾘｰ]佐藤心+' },
        { href: 'Mobamas/6thAnniversary/6thAnniversaryS.html', name: '[6thｱﾆﾊﾞｰｻﾘｰ･S]佐藤心' },
        { href: 'Mobamas/6thAnniversary+/6thAnniversaryS+.html', name: '[6thｱﾆﾊﾞｰｻﾘｰ･S]佐藤心+' },
        { href: 'Mobamas/FallingHeart/FallingHeart.html', name: '[ふぉーりんはぁと]佐藤心' },
        { href: 'Mobamas/FallingHeart+/FallingHeart+.html', name: '[ふぉーりんはぁと]佐藤心+' },
        { href: 'Mobamas/ShinshunHeartful/ShinshunHeartful.html', name: '[新春はぁとふる]佐藤心' },
        { href: 'Mobamas/ShinshunHeartful+/ShinshunHeartful+.html', name: '[新春はぁとふる]佐藤心+' },
        { href: 'Mobamas/NatsuiroHeart/NatsuiroHeart.html', name: '[夏色はぁと]佐藤心' },
        { href: 'Mobamas/NatsuiroHeart+/NatsuiroHeart+.html', name: '[夏色はぁと]佐藤心+' },
        { href: 'Mobamas/SweetieNewYear/SweetieNewYear.html', name: '[ｽｳｨｰﾃｨｰ･ﾆｭｰｲﾔｰ]佐藤心' },
        { href: 'Mobamas/SweetieNewYear+/SweetieNewYear+.html', name: '[ｽｳｨｰﾃｨｰ･ﾆｭｰｲﾔｰ]佐藤心+' },
        { href: 'Mobamas/MerryChristmasHeart/MerryChristmasHeart.html', name: '[ﾒﾘｸﾘ☆ﾊｰﾄ]佐藤心' },
        { href: 'Mobamas/MerryChristmasHeart+/MerryChristmasHeart+.html', name: '[ﾒﾘｸﾘ☆ﾊｰﾄ]佐藤心+' },
        { href: 'Mobamas/BrilliantHeart/BrilliantHeart.html', name: '[ﾌﾞﾘﾘｱﾝﾄ･はぁと]佐藤心' },
        { href: 'Mobamas/BrilliantHeart+/BrilliantHeart+.html', name: '[ﾌﾞﾘﾘｱﾝﾄ･はぁと]佐藤心+' },
        { href: 'Mobamas/StylishHeart/StylishHeart.html', name: '[ｽﾀｲﾘｯｼｭ･はぁと]佐藤心' },
        { href: 'Mobamas/StylishHeart+/StylishHeart+.html', name: '[ｽﾀｲﾘｯｼｭ･はぁと]佐藤心+' },
        { href: 'Deresute/SatoShin/SatoShin.html', name: '佐藤心' },
        { href: 'Deresute/SatoShin+/SatoShin+.html', name: '佐藤心+' },
        { href: 'Deresute/HeartModel/HeartModel.html', name: '[ハート・モデル]佐藤心' },
        { href: 'Deresute/HeartModel+/HeartModel+.html', name: '[ハート・モデル]佐藤心+' },
        { href: 'Deresute/HeartToHeart/HeartToHeart.html', name: '[はぁとトゥハート]佐藤心' },
        { href: 'Deresute/HeartToHeart+/HeartToHeart+.html', name: '[はぁとトゥハート]佐藤心+' },
        { href: 'Deresute/HeartNoYomeiri/HeartNoYomeiri.html', name: '[はぁとの嫁入り]佐藤心' },
        { href: 'Deresute/HeartNoYomeiri+/HeartNoYomeiri+.html', name: '[はぁとの嫁入り]佐藤心+' },
        { href: 'Deresute/BrilliantHeart/BrilliantHeart.html', name: '[ブリリアント・はぁと]佐藤心' },
        { href: 'Deresute/BrilliantHeart+/BrilliantHeart+.html', name: '[ブリリアント・はぁと]佐藤心+' },
        { href: 'Deresute/HappyNewYeah/HappyNewYeah.html', name: '[Happy New Yeah！]佐藤心' },
        { href: 'Deresute/HappyNewYeah+/HappyNewYeah+.html', name: '[Happy New Yeah！]佐藤心+' },
        { href: 'Deresute/DekobokoSpeedStar/DekobokoSpeedStar.html', name: '[凸凹スピードスター]佐藤心' },
        { href: 'Deresute/DekobokoSpeedStar+/DekobokoSpeedStar+.html', name: '[凸凹スピードスター]佐藤心+' },
        { href: 'Deresute/OrderMadeHeart/OrderMadeHeart.html', name: '[オーダーメイド・はぁと]佐藤心' },
        { href: 'Deresute/OrderMadeHeart+/OrderMadeHeart+.html', name: '[オーダーメイド・はぁと]佐藤心+' },
        { href: 'Deresute/LuxuryHeart/LuxuryHeart.html', name: '[ラグジュアリィ・はぁと]佐藤心' },
        { href: 'Deresute/LuxuryHeart+/LuxuryHeart+.html', name: '[ラグジュアリィ・はぁと]佐藤心+' },
        { href: 'Deresute/GoJustGo/GoJustGo.html', name: '[Go Just Go！]佐藤心' },
        { href: 'Deresute/GoJustGo+/GoJustGo+.html', name: '[Go Just Go！]佐藤心+' },
        { href: 'Deresute/OdoruFlagship/OdoruFlagship.html', name: '[躍るFLAGSHIP]佐藤心' },
        { href: 'Deresute/OdoruFlagship+/OdoruFlagship+.html', name: '[躍るFLAGSHIP]佐藤心+' },
        { href: 'Deresute/HeartfulSweeteen/HeartfulSweeteen.html', name: '[はぁとふるsweeteen☆]佐藤心' },
        { href: 'Deresute/HeartfulSweeteen+/HeartfulSweeteen+.html', name: '[はぁとふるsweeteen☆]佐藤心+' },
        { href: 'Deresute/CoCoNatsuNatsuNatsuHoliday/CoCoNatsuNatsuNatsuHoliday.html', name: '[CoCo夏夏夏Holiday]佐藤心' },
        { href: 'Deresute/CoCoNatsuNatsuNatsuHoliday+/CoCoNatsuNatsuNatsuHoliday+.html', name: '[CoCo夏夏夏Holiday]佐藤心+' },
        { href: 'Deresute/KoisuruSweetieSummer/KoisuruSweetieSummer.html', name: '[恋するスウィーティーサマー]佐藤心' },
        { href: 'Deresute/KoisuruSweetieSummer+/KoisuruSweetieSummer+.html', name: '[恋するスウィーティーサマー]佐藤心+' },
        { href: 'Deresute/DancingDead/DancingDead.html', name: '[ダンシング・デッド]佐藤心' },
        { href: 'Deresute/DancingDead+/DancingDead+.html', name: '[ダンシング・デッド]佐藤心+' },
        { href: 'Deresute/AisareQueenHeart/AisareQueenHeart.html', name: '[愛されクイーン・はぁと]佐藤心' },
        { href: 'Deresute/AisareQueenHeart+/AisareQueenHeart+.html', name: '[愛されクイーン・はぁと]佐藤心+' },
        { href: 'Deresute/DokonjyoReporter/DokonjyoReporter.html', name: '[ド根性⭐︎レポーター]佐藤心' },
        { href: 'Deresute/DokonjyoReporter+/DokonjyoReporter+.html', name: '[ド根性⭐︎レポーター]佐藤心+' },
        { href: 'Deresute/ManatsuNoHeartMeetsHeart/ManatsuNoHeartMeetsHeart.html', name: '[真夏の⭐︎はぁとミーツハート]佐藤心' },
        { href: 'Deresute/ManatsuNoHeartMeetsHeart+/ManatsuNoHeartMeetsHeart+.html', name: '[真夏の⭐︎はぁとミーツハート]佐藤心+' },
        { href: 'Deresute/KonoyoDeTadaHitoriNoHeart/KonoyoDeTadaHitoriNoHeart.html', name: '[この世でただひとりのはぁと]佐藤心' },
        { href: 'Deresute/KonoyoDeTadaHitoriNoHeart+/KonoyoDeTadaHitoriNoHeart+.html', name: '[この世でただひとりのはぁと]佐藤心+' }
    ];

    var current = decodeURIComponent(location.pathname);
    var html = '<aside class="v2-sidebar"><div class="v2-sidebar-sticky">' +
        '<h3>カード一覧 <span class="sb-count">' + CARDS.length + '</span></h3>' +
        '<div class="sb-list">';
    CARDS.forEach(function (c) {
        var active = current.slice(-(c.href.length + 1)) === '/' + c.href;
        var icon = CLOUDINARY + c.href.replace(/\.html$/, '') + 'Icon';
        html += '<a class="sb-item' + (active ? ' active' : '') + '" href="' + c.href + '">' +
            '<img class="sb-icon" src="' + icon + '" alt="" loading="lazy">' +
            '<div class="nm">' + c.name + '</div>' +
            '</a>';
    });
    html += '</div></div></aside>';

    // このscriptタグの直前に同期注入（header.jsと同方式）
    document.currentScript.insertAdjacentHTML('beforebegin', html);

    // 現在のカードが見える位置までサイドバー内スクロール（ページ本体は動かさない）
    document.addEventListener('DOMContentLoaded', function () {
        var box = document.querySelector('.v2-sidebar-sticky');
        var act = box && box.querySelector('.sb-item.active');
        if (box && act) box.scrollTop = Math.max(0, act.offsetTop - box.clientHeight / 2);
    });
})();
