# -*- coding: utf-8 -*-
"""シンデレラガールズ劇場 一覧ページを生成する。
Cloudinaryにある CinGeki(無印)/CinGekiWide(わいど☆) の全話をブロックとして静的に描画し、
無印/わいど☆/アニメ の絞込み（URLハッシュ対応）を付ける。CASTは佐藤心＋空2枠。"""
import html
from pathlib import Path

CDN = "https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/CinGeki/"
SHIN = "https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/data/iconimg/satoshin_icon01"

mujirushi = [246, 329, 391, 447, 521, 527, 604, 671, 750, 841, 843, 931, 1001, 1008,
             1040, 1083, 1218, 1311, 1323, 1400, 1470, 1476, 1498, 1595, 1622]
wide = [5, 11, 27, 30, 57, 66, 94, 142, 157, 160, 175, 197, 219, 223, 225, 266, 274,
        297, 357, 371, 376, 380, 486, 541, 578, 607, 631, 662, 663, 665, 668, 669, 682, 728]

rel_mu = {
    246: ("Mobamas/SatoShin/SatoShin.html", "佐藤心"),
    329: ("Mobamas/TBSweetie/TBSweetie.html", "[T.B.ｽｳｨｰﾃｨｰ]佐藤心"),
    391: ("Mobamas/HeartModel/HeartModel.html", "[ﾊｰﾄ･ﾓﾃﾞﾙ]佐藤心"),
    447: ("Mobamas/AngelHeart/AngelHeart.html", "[えんじぇるはぁと]佐藤心"),
    521: ("Mobamas/HeartNoYomeiri/HeartNoYomeiri.html", "[はぁとの嫁入り]佐藤心"),
    604: ("Mobamas/SweetieRoyal/SweetieRoyal.html", "[ｽｳｨｰﾃｨｰ･ﾛﾜｲﾔﾙ]佐藤心"),
    671: ("Mobamas/WorkingSweetie/WorkingSweetie.html", "[ﾜｰｷﾝｸﾞ･ｽｳｨｰﾃｨｰ]佐藤心"),
    750: ("Mobamas/TokonatsuParadise/TokonatsuParadise.html", "[常夏ﾊﾟﾗﾀﾞｲｽ]佐藤心"),
    843: ("Mobamas/ChikuttoSweetie/ChikuttoSweetie.html", "[ﾁｸｯとｽｳｨｰﾃｨｰ]佐藤心"),
    1008: ("Mobamas/6thAnniversary/6thAnniversary.html", "[6thｱﾆﾊﾞｰｻﾘｰ]佐藤心"),
    1083: ("Mobamas/FallingHeart/FallingHeart.html", "[ふぉーりんはぁと]佐藤心"),
    1218: ("Mobamas/ShinshunHeartful/ShinshunHeartful.html", "[新春はぁとふる]佐藤心"),
    1311: ("Mobamas/NatsuiroHeart/NatsuiroHeart.html", "[夏色はぁと]佐藤心"),
    1400: ("Mobamas/SweetieNewYear/SweetieNewYear.html", "[ｽｳｨｰﾃｨｰ･ﾆｭｰｲﾔｰ]佐藤心"),
    1476: ("Mobamas/MerryChristmasHeart/MerryChristmasHeart.html", "[ﾒﾘｸﾘ☆ﾊｰﾄ]佐藤心"),
    1595: ("Mobamas/StylishHeart/StylishHeart.html", "[ｽﾀｲﾘｯｼｭ･はぁと]佐藤心"),
}
rel_wi = {
    30: ("Deresute/DekobokoSpeedStar/DekobokoSpeedStar.html", "[凸凹スピードスター]佐藤心"),
    57: ("Deresute/OrderMadeHeart/OrderMadeHeart.html", "[オーダーメイド・はぁと]佐藤心"),
    219: ("Deresute/BrilliantHeart/BrilliantHeart.html", "[ブリリアント・はぁと]佐藤心"),
    297: ("Deresute/GoJustGo/GoJustGo.html", "[Go Just Go！]佐藤心"),
    371: ("Deresute/OdoruFLAGSHIP/OdoruFlagship.html", "[躍るFLAGSHIP]佐藤心"),
    376: ("Deresute/HeartfulSweeteen/HeartfulSweeteen.html", "[はぁとふるsweeteen☆]佐藤心"),
    486: ("Deresute/CoCoNatsuNatsuNatsuHoliday/CoCoNatsuNatsuNatsuHoliday.html", "[CoCo夏夏夏Holiday]佐藤心"),
    541: ("Deresute/KoisuruSweetieSummer/KoisuruSweetieSummer.html", "[恋するスウィーティーサマー]佐藤心"),
    578: ("Deresute/DancingDead/DancingDead.html", "[ダンシング・デッド]佐藤心"),
    669: ("Deresute/AisareQueenHeart/AisareQueenHeart.html", "[愛されクイーン・はぁと]佐藤心"),
}
TYPE_LABEL = {'mujirushi': '無印', 'wide': 'わいど☆'}
IMG_PREFIX = {'mujirushi': 'CinGeki', 'wide': 'CinGekiWide'}


def esc(s):
    return html.escape(str(s), quote=True)


def block(ep, typ, rel):
    img = CDN + IMG_PREFIX[typ] + str(ep)
    tl = TYPE_LABEL[typ]
    lines = [
        f'            <article class="gekijo-block" data-type="{typ}" data-ep="{ep}">',
        f'                <div class="gekijo-thumb"><img class="lightbox-trigger" src="{img}" alt="シンデレラガールズ劇場{tl} 第{ep}話" loading="lazy"></div>',
        f'                <div class="gekijo-meta">',
        f'                    <div class="gekijo-head"><span class="gekijo-ep">第{ep}話</span><span class="gekijo-type type-{typ}">{tl}</span></div>',
        f'                    <div class="gekijo-cast">',
        f'                        <div class="idol shin"><img src="{SHIN}" alt="佐藤心" loading="lazy"><span class="nm">佐藤心</span></div>',
        f'                        <div class="idol idol-empty" title="共演アイドル（編集で追加）"></div>',
        f'                        <div class="idol idol-empty" title="共演アイドル（編集で追加）"></div>',
        f'                    </div>',
    ]
    if rel:
        lines.append(f'                    <div class="gekijo-rel"><a href="{rel[0]}">関連: {esc(rel[1])} →</a></div>')
    lines.append('                </div>')
    lines.append('            </article>')
    return "\n".join(lines)


def main():
    blocks = [block(ep, 'mujirushi', rel_mu.get(ep)) for ep in mujirushi]
    blocks += [block(ep, 'wide', rel_wi.get(ep)) for ep in wide]
    blocks_html = "\n".join(blocks)
    total = len(mujirushi) + len(wide)

    tpl = Path(__file__).parent / "gekijo_template.html"
    page = tpl.read_text(encoding="utf-8")
    page = page.replace("{{TOTAL}}", str(total)).replace("{{BLOCKS}}", blocks_html)
    out = Path(__file__).parent.parent / "CinderellaGirlsGekijou" / "CinderellaGirlsGekijou.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print("written", len(page), "chars; blocks:", total)


if __name__ == "__main__":
    main()
