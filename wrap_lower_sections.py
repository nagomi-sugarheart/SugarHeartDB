#!/usr/bin/env python3
"""Wrap v2-theater, v2-gallery, v2-related sections in v2-detail-lower layout."""
import re
import glob

PATTERN = re.compile(
    r'( *<section class="v2-theater">.*?</section>)'
    r'\s*'
    r'( *<section class="v2-gallery">.*?</section>)'
    r'\s*'
    r'( *<section class="v2-related">.*?</section>)',
    re.DOTALL
)

def replacement(m):
    theater = m.group(1)
    gallery = m.group(2)
    related = m.group(3)
    return (
        '        <div class="v2-detail-lower">\n'
        + theater + '\n'
        + '            <div class="v2-detail-lower-right">\n'
        + gallery + '\n'
        + related + '\n'
        + '            </div>\n'
        + '        </div>'
    )

files = glob.glob('Mobamas/**/*.html', recursive=True) + glob.glob('Deresute/**/*.html', recursive=True)
count = 0
for path in sorted(files):
    with open(path, encoding='utf-8') as f:
        html = f.read()
    if 'v2-detail-lower' in html:
        print(f'  SKIP already: {path}')
        continue
    if 'v2-theater' not in html:
        continue
    new_html = PATTERN.sub(replacement, html)
    if new_html == html:
        print(f'  WARN no match: {path}')
        continue
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f'  OK: {path}')
    count += 1

print(f'\nDone: {count} files updated')
