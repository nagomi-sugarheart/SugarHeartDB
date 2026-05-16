#!/usr/bin/env python3
"""
Fix 1: Wrap sidebar contents in .v2-sidebar-sticky inner div
Fix 2: Change breadcrumb to HOME · カード一覧 · カード詳細
"""
import re
import glob

# --- Fix 1: sidebar inner wrapper ---
SIDEBAR_PATTERN = re.compile(
    r'(<aside class="v2-sidebar">)\s*(.*?)\s*(</aside>)',
    re.DOTALL
)

def wrap_sidebar(html):
    def replacer(m):
        open_tag = m.group(1)
        inner = m.group(2).strip()
        close_tag = m.group(3)
        return (
            open_tag + '\n'
            '        <div class="v2-sidebar-sticky">\n'
            '        ' + inner + '\n'
            '        </div>\n'
            '    ' + close_tag
        )
    return SIDEBAR_PATTERN.sub(replacer, html, count=1)

# --- Fix 2: breadcrumb ---
BREADCRUMB_MOBAMAS = re.compile(
    r'<div class="v2-breadcrumb"><a href="/SugarHeartDB/">HOME</a> · '
    r'<a href="Mobamas/index\.html">MOBAMAS</a> · <strong>.*?</strong></div>'
)
BREADCRUMB_DERESUTE = re.compile(
    r'<div class="v2-breadcrumb"><a href="/SugarHeartDB/">HOME</a> · '
    r'<a href="Deresute/index\.html">DERESUTE</a> · <strong>.*?</strong></div>'
)

BREADCRUMB_NEW_MOBAMAS = (
    '<div class="v2-breadcrumb">'
    '<a href="/SugarHeartDB/">HOME</a> · '
    '<a href="Mobamas/CardList.html">カード一覧</a> · '
    '<strong>カード詳細</strong>'
    '</div>'
)
BREADCRUMB_NEW_DERESUTE = (
    '<div class="v2-breadcrumb">'
    '<a href="/SugarHeartDB/">HOME</a> · '
    '<a href="Deresute/CardList.html">カード一覧</a> · '
    '<strong>カード詳細</strong>'
    '</div>'
)

def process(path, is_deresute):
    with open(path, encoding='utf-8') as f:
        html = f.read()

    changed = False

    # Fix 1: sidebar inner wrapper
    if 'v2-sidebar-sticky' not in html and 'v2-sidebar' in html:
        new_html = wrap_sidebar(html)
        if new_html != html:
            html = new_html
            changed = True

    # Fix 2: breadcrumb
    if is_deresute:
        new_html = BREADCRUMB_DERESUTE.sub(BREADCRUMB_NEW_DERESUTE, html)
    else:
        new_html = BREADCRUMB_MOBAMAS.sub(BREADCRUMB_NEW_MOBAMAS, html)
    if new_html != html:
        html = new_html
        changed = True

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  OK: {path}')
    else:
        print(f'  SKIP: {path}')
    return changed

mobamas = glob.glob('Mobamas/**/*.html', recursive=True)
deresute = glob.glob('Deresute/**/*.html', recursive=True)

count = 0
for path in sorted(mobamas):
    if process(path, False): count += 1
for path in sorted(deresute):
    if process(path, True): count += 1

print(f'\nDone: {count} files updated')
