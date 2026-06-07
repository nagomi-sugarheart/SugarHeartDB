import re
from pathlib import Path

BASE_DIR = Path('C:/Users/sawas/Desktop/SugarHeartDB')

def get_val(content, key):
    m = re.search(
        r'<div class="v2-meta-row[^"]*">\s*<span class="v2-meta-k">'
        + re.escape(key)
        + r'</span>(?:<span class="v2-meta-sep">[^<]*</span>)?(?:<span class="v2-meta-k">[^<]*</span>)?<span class="v2-meta-v">([^<]*)</span>',
        content
    )
    if m:
        return m.group(1)
    # Also handle combined rows with sep
    m2 = re.search(
        r'<span class="v2-meta-k">' + re.escape(key) + r'</span><span class="v2-meta-v">([^<]*)</span>',
        content
    )
    return m2.group(1) if m2 else ''

def build_new_grid(rarity, lv, cost, atk, defe, skill):
    return (
        '<div class="v2-meta-grid">\n'
        f'                    <div class="v2-meta-row v2-meta-wide"><span class="v2-meta-k">レアリティ</span><span class="v2-meta-v">{rarity}</span></div>\n'
        f'                    <div class="v2-meta-row"><span class="v2-meta-k">最大Lv</span><span class="v2-meta-v">{lv}</span></div>\n'
        f'                    <div class="v2-meta-row"><span class="v2-meta-k">コスト</span><span class="v2-meta-v">{cost}</span></div>\n'
        f'                    <div class="v2-meta-row"><span class="v2-meta-k">攻</span><span class="v2-meta-v">{atk}</span></div>\n'
        f'                    <div class="v2-meta-row"><span class="v2-meta-k">守</span><span class="v2-meta-v">{defe}</span></div>\n'
        f'                    <div class="v2-meta-row v2-meta-wide"><span class="v2-meta-k">特技</span><span class="v2-meta-v">{skill}</span></div>\n'
        '                </div>'
    )

GRID_PATTERN = re.compile(r'<div class="v2-meta-grid">.*?</div>\s*</div>', re.DOTALL)

html_files = list((BASE_DIR / 'Mobamas').rglob('*.html'))
fixed = []

for p in sorted(html_files):
    content = p.read_text(encoding='utf-8')
    if 'v2-meta-grid' not in content:
        continue

    rarity = get_val(content, 'レアリティ')
    lv     = get_val(content, '最大Lv')
    cost   = get_val(content, 'コスト')
    atk    = get_val(content, '攻')
    defe   = get_val(content, '守')
    skill  = get_val(content, '特技')

    new_grid = build_new_grid(rarity, lv, cost, atk, defe, skill)
    new_content = GRID_PATTERN.sub(new_grid, content, count=1)

    if new_content != content:
        p.write_text(new_content, encoding='utf-8')
        rel = str(p.relative_to(BASE_DIR))
        fixed.append(rel)
        print('Fixed:', rel)

print('---')
print('Total fixed:', len(fixed))
