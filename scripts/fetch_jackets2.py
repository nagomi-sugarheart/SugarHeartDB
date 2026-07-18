# -*- coding: utf-8 -*-
"""
各曲のgamerch個別ページから2枚目（CDジャケット）URLを取得する。
Playwright経由でブラウザから fetch() を使う（同一オリジン制限回避）。
"""
import asyncio, base64, json, sys
from pathlib import Path

BASE = Path(__file__).parent.parent

async def fetch_jackets(page, url, song_title):
    """指定gamerchページで wiki/3825/entry/ な画像のdata-srcを全部デコード"""
    await page.goto(url)
    await page.wait_for_load_state('networkidle')

    result = await page.evaluate("""() => {
        const imgs = document.querySelectorAll('img[data-src]');
        const keys = [];
        for (const img of imgs) {
            const ds = img.getAttribute('data-src');
            if (!ds || ds.includes('.svg')) continue;
            try {
                // base64 → JSON → key
                const b64part = ds.split('/').pop();
                const decoded = JSON.parse(atob(b64part));
                if (decoded.key && decoded.key.includes('wiki/3825/entry/')) {
                    const url = 'https://cdn.gamerch.com/contents/' + decoded.key;
                    if (!keys.includes(url)) keys.push(url);
                }
            } catch(e) {}
        }
        return keys;
    }""")
    print(f"[{song_title}] => {result}")
    return result


async def main():
    from playwright.async_api import async_playwright

    pages_info = [
        ('命燃やして恋せよ乙女',   'https://gamerch.com/imascg-slstage-wiki/517463'),
        ('Happy New Yeah!',        'https://gamerch.com/imascg-slstage-wiki/518093'),
        ('CoCo夏夏夏 Holiday',     'https://gamerch.com/imascg-slstage-wiki/521061'),
        ('凸凹スピードスター',       'https://gamerch.com/imascg-slstage-wiki/518447'),
        ('躍るFLAGSHIP',           'https://gamerch.com/imascg-slstage-wiki/520451'),
        ('Go Just Go!',            'https://gamerch.com/imascg-slstage-wiki/520032'),
        ('ダンシング・デッド',       'https://gamerch.com/imascg-slstage-wiki/521567'),
        ('世界はそれを愛と呼ぶんだぜ', 'https://gamerch.com/imascg-slstage-wiki/811768'),
        ('Next Chapter',           'https://gamerch.com/imascg-slstage-wiki/777123'),
    ]

    results = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        for title, url in pages_info:
            jackets = await fetch_jackets(page, url, title)
            results[title] = jackets
        await browser.close()

    # 認めてくれなくたっていいよ → 熱情エナモラルと同じ
    results['認めてくれなくたっていいよ'] = ['https://cdn.gamerch.com/contents/wiki/3825/entry/JfHHPBS6.jpg']

    out_path = BASE / 'scripts' / 'songlist_data' / 'jacket2_urls.json'
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print(f"\nSaved to {out_path}")

asyncio.run(main())
