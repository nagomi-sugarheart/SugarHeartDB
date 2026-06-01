$basePath = 'C:\Users\sawas\Desktop\SugarHeartDB'

$dirMap = @{
    '佐藤心' = 'SatoShin'
    '佐藤心+' = 'SatoShin+'
    '[ハート・モデル]佐藤心' = 'HeartModel'
    '[ハート・モデル]佐藤心+' = 'HeartModel+'
    '[はぁとトゥハート]佐藤心' = 'HeartToHeart'
    '[はぁとトゥハート]佐藤心+' = 'HeartToHeart+'
    '[はぁとの嫁入り]佐藤心' = 'HeartNoYomeiri'
    '[はぁとの嫁入り]佐藤心+' = 'HeartNoYomeiri+'
    '[ブリリアント・はぁと]佐藤心' = 'BrilliantHeart'
    '[ブリリアント・はぁと]佐藤心+' = 'BrilliantHeart+'
    '[Happy New Yeah！]佐藤心' = 'HappyNewYeah'
    '[Happy New Yeah！]佐藤心+' = 'HappyNewYeah+'
    '[凸凹スピードスター]佐藤心' = 'DekobokoSpeedStar'
    '[凸凹スピードスター]佐藤心+' = 'DekobokoSpeedStar+'
    '[オーダーメイド・はぁと]佐藤心' = 'OrderMadeHeart'
    '[オーダーメイド・はぁと]佐藤心+' = 'OrderMadeHeart+'
    '[ラグジュアリィ・はぁと]佐藤心' = 'LuxuryHeart'
    '[ラグジュアリィ・はぁと]佐藤心+' = 'LuxuryHeart+'
    '[Go Just Go！]佐藤心' = 'GoJustGo'
    '[Go Just Go！]佐藤心+' = 'GoJustGo+'
    '[躍るFLAGSHIP]佐藤心' = 'OdoruFLAGSHIP'
    '[躍るFLAGSHIP]佐藤心+' = 'OdoruFLAGSHIP+'
    '[はぁとふるsweeteen☆]佐藤心' = 'HeartfulSweeteen'
    '[はぁとふるsweeteen☆]佐藤心+' = 'HeartfulSweeteen+'
    '[CoCo夏夏夏Holiday]佐藤心' = 'CoCoNatsuNatsuNatsuHoliday'
    '[CoCo夏夏夏Holiday]佐藤心+' = 'CoCoNatsuNatsuNatsuHoliday+'
    '[恋するスウィーティーサマー]佐藤心' = 'KoisuruSweetieSummer'
    '[恋するスウィーティーサマー]佐藤心+' = 'KoisuruSweetieSummer+'
    '[ダンシング・デッド]佐藤心' = 'DancingDead'
    '[ダンシング・デッド]佐藤心+' = 'DancingDead+'
    '[愛されクイーン・はぁと]佐藤心' = 'AisareQueenHeart'
    '[愛されクイーン・はぁと]佐藤心+' = 'AisareQueenHeart+'
    '[ド根性⭐︎レポーター]佐藤心' = 'DokonjyoReporter'
    '[ド根性⭐︎レポーター]佐藤心+' = 'DokonjyoReporter+'
    '[真夏の⭐︎はぁとミーツハート]佐藤心' = 'ManatsuNoHeartMeetsHeart'
    '[真夏の⭐︎はぁとミーツハート]佐藤心+' = 'ManatsuNoHeartMeetsHeart+'
    '[この世でただひとりのはぁと]佐藤心' = 'KonoyoDeTadaHitoriNoHeart'
    '[この世でただひとりのはぁと]佐藤心+' = 'KonoyoDeTadaHitoriNoHeart+'
}

$mobamasMap = @{
    '佐藤心' = 'Mobamas/SatoShin/SatoShin.html'
    '佐藤心+' = 'Mobamas/SatoShin+/SatoShin+.html'
    '[ハート・モデル]佐藤心' = 'Mobamas/HeartModel/HeartModel.html'
    '[ハート・モデル]佐藤心+' = 'Mobamas/HeartModel+/HeartModel+.html'
    '[はぁとの嫁入り]佐藤心' = 'Mobamas/HeartNoYomeiri/HeartNoYomeiri.html'
    '[はぁとの嫁入り]佐藤心+' = 'Mobamas/HeartNoYomeiri+/HeartNoYomeiri+.html'
    '[ブリリアント・はぁと]佐藤心' = 'Mobamas/BrilliantHeart/BrilliantHeart.html'
    '[ブリリアント・はぁと]佐藤心+' = 'Mobamas/BrilliantHeart+/BrilliantHeart+.html'
}

$eventMap = @{
    'Happy New Yeah!' = 'Deresute/Event/Event_HappyNewYeah.html'
    '凸凹スピードスター' = 'Deresute/Event/Event_DekobokoSpeedStar.html'
    'Go Just Go!' = 'Deresute/Event/Event_GoJustGo.html'
    '躍るFLAGSHIP' = 'Deresute/Event/Event_OdoruFLAGSHIP.html'
    'CoCo夏夏夏Holiday' = 'Deresute/Event/Event_CoCoNatsuHoliday.html'
    '恋するいこいの乙女' = 'Deresute/Event/Event_KoisuruIkoiOtome.html'
    'Dancing Dead' = 'Deresute/Event/Event_DancingDead.html'
    '向日葵のきらめき' = 'Deresute/Event/Event_SunFlower.html'
    'Take Me☆Take You' = 'Deresute/Event/Event_TakeMeTakeYou.html'
    'ネクストチャプター' = 'Deresute/Event/Event_NextChapter.html'
}

$specialMap = @{
    'メモリアルコミュ' = 'Deresute/MemorialCommu.html'
    'ビジネスコミュ' = 'Deresute/Common/BusinessCommu.html'
    'ストーリーコミュ' = 'Deresute/Common/StoryCommu.html'
    'コモンボイス' = 'Deresute/Common/CommonVoice.html'
}

function Get-RelatedUrl([string]$name) {
    if ([string]::IsNullOrWhiteSpace($name)) { return $null }
    if ($name -like '【公式】*') { return '#' }
    if ($name -like '*（ユニット）') { return '#' }
    if ($name -match '（(デレステ)?イベント）$') {
        $evtName = $name -replace '（(デレステ)?イベント）$', ''
        if ($script:eventMap.ContainsKey($evtName)) { return $script:eventMap[$evtName] }
        return '#'
    }
    if ($name -like '*（モバマス）') {
        $cardName = $name -replace '（モバマス）$', ''
        if ($script:mobamasMap.ContainsKey($cardName)) { return $script:mobamasMap[$cardName] }
        return '#'
    }
    if ($script:specialMap.ContainsKey($name)) { return $script:specialMap[$name] }
    if ($script:dirMap.ContainsKey($name)) {
        $d = $script:dirMap[$name]
        return "Deresute/$d/$d.html"
    }
    return '#'
}

function Escape-Html([string]$s) {
    return $s -replace '&','&amp;' -replace '<','&lt;' -replace '>','&gt;'
}

function Build-MetaGrid($card) {
    $r = $card.'カード性能_レアリティ'
    $lv = $card.'カード性能_最大Lv'
    $attr = $card.'カード性能_属性'
    $ml = $card.'カード性能_最大Life'; $il = $card.'カード性能_初期Life'
    $mv = $card.'カード性能_最大Vocal'; $iv = $card.'カード性能_初期Vocal'
    $md = $card.'カード性能_最大Dance'; $id = $card.'カード性能_初期Dance'
    $mvi = $card.'カード性能_最大Visual'; $ivi = $card.'カード性能_初期Visual'
    $cn = $card.'カード性能_センタースキル名'; $ce = $card.'カード性能_センタースキル効果'
    $sn = $card.'カード性能_特技名'; $ss = $card.'カード性能_特技スキル名'; $se = $card.'カード性能_特技スキル効果'
    $i = '                    '
    @(
        "$i<div class=`"v2-meta-row`"><span class=`"v2-meta-k`">レアリティ</span><span class=`"v2-meta-v`">$r</span></div>"
        "$i<div class=`"v2-meta-row`"><span class=`"v2-meta-k`">最大Lv</span><span class=`"v2-meta-v`">$lv</span></div>"
        "$i<div class=`"v2-meta-row`"><span class=`"v2-meta-k`">属性</span><span class=`"v2-meta-v`">$attr</span></div>"
        "$i<div class=`"v2-meta-row`"><span class=`"v2-meta-k`">最大Life（初期）</span><span class=`"v2-meta-v`">$ml（$il）</span></div>"
        "$i<div class=`"v2-meta-row`"><span class=`"v2-meta-k`">最大Vocal（初期）</span><span class=`"v2-meta-v`">$mv（$iv）</span></div>"
        "$i<div class=`"v2-meta-row`"><span class=`"v2-meta-k`">最大Dance（初期）</span><span class=`"v2-meta-v`">$md（$id）</span></div>"
        "$i<div class=`"v2-meta-row`"><span class=`"v2-meta-k`">最大Visual（初期）</span><span class=`"v2-meta-v`">$mvi（$ivi）</span></div>"
        "$i<div class=`"v2-meta-row`"><span class=`"v2-meta-k`">センタースキル</span><span class=`"v2-meta-v`">$cn（$ce）</span></div>"
        "$i<div class=`"v2-meta-row`"><span class=`"v2-meta-k`">特技</span><span class=`"v2-meta-v`">$sn／$ss（$se）</span></div>"
    ) -join "`n"
}

function Make-PLines([string[]]$lines) {
    ($lines | Where-Object { $_.Trim() -ne '' } | ForEach-Object {
        "                        <p>$(Escape-Html $_)</p>"
    }) -join "`n"
}

function Build-DialogueContent($card) {
    $nl = "`n"
    $lines = [System.Collections.Generic.List[string]]::new()

    # アイドルセリフ
    $idol = Escape-Html $card.'アイドルセリフ'
    $lines.Add('                <div class="v2-accord open">')
    $lines.Add('                    <div class="v2-accord-head"><span class="v2-accord-lbl">アイドルセリフ</span><span class="v2-accord-arrow">▾</span></div>')
    $lines.Add('                    <div class="v2-accord-body">')
    $lines.Add("                        <p>$idol</p>")
    $lines.Add('                    </div>')
    $lines.Add('                </div>')

    # ホームセリフ
    $homeLines = @()
    for ($n = 1; $n -le 12; $n++) {
        $v = $card."ホーム$n"
        if ($v) { $homeLines += "                        <p>$(Escape-Html $v)</p>" }
    }
    $lines.Add('                <div class="v2-accord open">')
    $lines.Add('                    <div class="v2-accord-head"><span class="v2-accord-lbl">ホームセリフ</span><span class="v2-accord-arrow">▾</span></div>')
    $lines.Add('                    <div class="v2-accord-body">')
    foreach ($hl in $homeLines) { $lines.Add($hl) }
    $lines.Add('                    </div>')
    $lines.Add('                </div>')

    # LIVEセリフ
    $lines.Add('                <div class="v2-accord">')
    $lines.Add('                    <div class="v2-accord-head"><span class="v2-accord-lbl">LIVEセリフ</span><span class="v2-accord-arrow">▾</span></div>')
    $lines.Add('                    <div class="v2-accord-body">')
    $lines.Add('                        <div class="accord-sub">LIVE開始</div>')
    $lines.Add("                        <p>$(Escape-Html $card.'LIVE開始')</p>")
    $lines.Add('                        <div class="accord-sub">LIVE特技</div>')
    for ($n = 1; $n -le 3; $n++) {
        $v = $card."LIVE特技$n"; if ($v) { $lines.Add("                        <p>$(Escape-Html $v)</p>") }
    }
    $lines.Add('                        <div class="accord-sub">LIVEクリア</div>')
    for ($n = 1; $n -le 2; $n++) {
        $v = $card."LIVEクリア$n"; if ($v) { $lines.Add("                        <p>$(Escape-Html $v)</p>") }
    }
    $lines.Add('                    </div>')
    $lines.Add('                </div>')

    # ルームセリフ
    $roomLines = @()
    for ($n = 1; $n -le 12; $n++) {
        $v = $card."ルーム$n"
        if ($v) { $roomLines += "                        <p>$(Escape-Html $v)</p>" }
    }
    $lines.Add('                <div class="v2-accord">')
    $lines.Add('                    <div class="v2-accord-head"><span class="v2-accord-lbl">ルームセリフ</span><span class="v2-accord-arrow">▾</span></div>')
    $lines.Add('                    <div class="v2-accord-body">')
    foreach ($rl in $roomLines) { $lines.Add($rl) }
    $lines.Add('                    </div>')
    $lines.Add('                </div>')

    # 親愛度セリフ
    $lines.Add('                <div class="v2-accord">')
    $lines.Add('                    <div class="v2-accord-head"><span class="v2-accord-lbl">親愛度セリフ</span><span class="v2-accord-arrow">▾</span></div>')
    $lines.Add('                    <div class="v2-accord-body">')
    $lines.Add('                        <div class="accord-sub">親愛度半分</div>')
    $affHalf = ($card.'親愛度半分' -replace "`r","").Split("`n") | Where-Object { $_.Trim() -ne '' }
    foreach ($al in $affHalf) { $lines.Add("                        <p>$(Escape-Html $al)</p>") }
    $lines.Add('                        <div class="accord-sub">親愛度MAX</div>')
    $affMax = ($card.'親愛度MAX' -replace "`r","").Split("`n") | Where-Object { $_.Trim() -ne '' }
    foreach ($al in $affMax) { $lines.Add("                        <p>$(Escape-Html $al)</p>") }
    $lines.Add('                    </div>')
    $lines.Add('                </div>')

    # 特訓コミュ
    $trainText = ($card.'特訓コミュ' -replace "`r","").Split("`n") | Where-Object { $_.Trim() -ne '' }
    $lines.Add('                <div class="v2-accord">')
    $lines.Add('                    <div class="v2-accord-head"><span class="v2-accord-lbl">特訓コミュ</span><span class="v2-accord-arrow">▾</span></div>')
    $lines.Add('                    <div class="v2-accord-body">')
    foreach ($tl in $trainText) { $lines.Add("                        <p>$(Escape-Html $tl)</p>") }
    $lines.Add('                    </div>')
    $lines.Add('                </div>')

    return $lines -join "`n"
}

function Build-RelatedLinks($card) {
    $links = [System.Collections.Generic.List[string]]::new()
    for ($n = 1; $n -le 20; $n++) {
        $relPage = $card."関連ページ$n"
        if ([string]::IsNullOrWhiteSpace($relPage)) { break }
        $url = Get-RelatedUrl $relPage
        if ($null -ne $url) {
            $links.Add("                <a href=`"$url`">$(Escape-Html $relPage)</a>")
        }
    }
    return $links -join "`n"
}

# Replace the first occurrence of <div class="$className">...</div> (depth-tracked)
function Replace-FirstDivBlock([string]$html, [string]$className, [string]$newBlock) {
    $openTag = "<div class=`"$className`">"
    $startIdx = $html.IndexOf($openTag)
    if ($startIdx -lt 0) { return $html }

    $depth = 0
    $i = $startIdx
    $len = $html.Length

    while ($i -lt $len) {
        # Opening <div
        if (($i + 4) -lt $len -and $html[$i] -eq '<' -and $html[$i+1] -eq 'd' -and $html[$i+2] -eq 'i' -and $html[$i+3] -eq 'v' -and ($html[$i+4] -eq ' ' -or $html[$i+4] -eq '>')) {
            $depth++
        }
        # Closing </div>
        if (($i + 5) -lt $len -and $html[$i] -eq '<' -and $html[$i+1] -eq '/' -and $html[$i+2] -eq 'd' -and $html[$i+3] -eq 'i' -and $html[$i+4] -eq 'v' -and $html[$i+5] -eq '>') {
            $depth--
            if ($depth -eq 0) {
                $endIdx = $i + 6
                return $html.Substring(0, $startIdx) + $newBlock + $html.Substring($endIdx)
            }
        }
        $i++
    }
    return $html
}

# ---- Main ----
$cards = Import-Csv -Path "$basePath\data\deresute.csv" -Encoding UTF8

foreach ($card in $cards) {
    $cardName = $card.'カード名'
    if (-not $dirMap.ContainsKey($cardName)) {
        Write-Host "SKIP (no dir): $cardName"
        continue
    }
    $dir = $dirMap[$cardName]
    $htmlPath = "$basePath\Deresute\$dir\$dir.html"
    if (-not (Test-Path $htmlPath)) {
        Write-Host "MISSING: $htmlPath"
        continue
    }

    Write-Host "Updating: $dir"
    $html = [System.IO.File]::ReadAllText($htmlPath, [System.Text.Encoding]::UTF8)

    # 1. Fix date
    $date = $card.'実装日'
    $html = $html -replace '<span class="v2-date">[^<]*</span>', "<span class=`"v2-date`">$date</span>"

    # 2. Replace meta-grid
    $newMeta = Build-MetaGrid $card
    $newMetaBlock = "<div class=`"v2-meta-grid`">`n$newMeta`n                </div>"
    $html = Replace-FirstDivBlock -html $html -className 'v2-meta-grid' -newBlock $newMetaBlock

    # 3. Replace first dialogue-content (text tab)
    $newDialogue = Build-DialogueContent $card
    $newDialogueBlock = "<div class=`"v2-dialogue-content`">`n$newDialogue`n            </div>"
    $html = Replace-FirstDivBlock -html $html -className 'v2-dialogue-content' -newBlock $newDialogueBlock

    # 4. Replace related links
    $newRelated = Build-RelatedLinks $card
    $newRelatedBlock = "<div class=`"v2-related-links`">`n$newRelated`n            </div>"
    $html = Replace-FirstDivBlock -html $html -className 'v2-related-links' -newBlock $newRelatedBlock

    [System.IO.File]::WriteAllText($htmlPath, $html, [System.Text.Encoding]::UTF8)
}

Write-Host "Done!"
