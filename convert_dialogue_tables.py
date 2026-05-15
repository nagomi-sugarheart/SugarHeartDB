#!/usr/bin/env python3
"""
Batch-convert card detail HTML pages from old table-based dialogue
to new V2 script-row format.

Only converts tables that have:
  <thead><tr><th>名前</th><th>セリフ</th></tr></thead>
"""

import os
import re
import sys

# The thead signature that identifies dialogue tables
DIALOGUE_THEAD = '<thead><tr><th>名前</th><th>セリフ</th></tr></thead>'

# Pattern for a full dialogue table block (table-area with the dialogue thead)
# Matches the entire <table class="table-area">...</table> block
TABLE_PATTERN = re.compile(
    r'<table class="table-area">\s*'         # opening tag
    r'(?:<colgroup>.*?</colgroup>\s*)?'      # optional colgroup
    r'<thead><tr><th>名前</th><th>セリフ</th></tr></thead>\s*'  # thead (exact match)
    r'<tbody>(.*?)</tbody>\s*'               # tbody content (captured)
    r'</table>',
    re.DOTALL
)

# Pattern for a single <tr> row within tbody
# Captures: first td content (may be empty), second td content (may contain HTML)
TR_PATTERN = re.compile(
    r'<tr><td>(.*?)</td><td>(.*?)</td></tr>',
    re.DOTALL
)


def convert_table_to_script_block(tbody_content: str, indent: str) -> str:
    """Convert tbody rows to script-block div format."""
    rows = TR_PATTERN.findall(tbody_content)
    lines = [f'{indent}<div class="script-block">']
    for who, line in rows:
        who = who.strip()
        if who == '':
            # Stage direction row
            lines.append(
                f'{indent}    <div class="script-row stage-direction">'
                f'<span class="who"></span>'
                f'<div class="line">{line}</div>'
                f'</div>'
            )
        else:
            # Speaker row
            lines.append(
                f'{indent}    <div class="script-row" data-who="{who}">'
                f'<span class="who">{who}</span>'
                f'<div class="line">{line}</div>'
                f'</div>'
            )
    lines.append(f'{indent}</div>')
    return '\n'.join(lines)


def convert_file(filepath: str) -> bool:
    """
    Convert dialogue tables in a single HTML file.
    Returns True if the file was modified, False otherwise.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Quick check: does this file contain any dialogue tables?
    if DIALOGUE_THEAD not in content:
        return False

    def replacer(match: re.Match) -> str:
        full_match = match.group(0)
        tbody_content = match.group(1)

        # Determine indentation from the original table tag position
        # Find the position of the match start in the content
        start = match.start()
        # Walk back from start to find the start of the line
        line_start = content.rfind('\n', 0, start) + 1
        prefix = content[line_start:start]
        # Extract only the whitespace (indent) part
        indent = ''
        for ch in prefix:
            if ch in (' ', '\t'):
                indent += ch
            else:
                break

        return convert_table_to_script_block(tbody_content, indent)

    new_content, count = TABLE_PATTERN.subn(replacer, content)

    if count == 0:
        # Pattern found the thead but regex didn't match full table — shouldn't happen
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True


def find_card_detail_pages(base_dirs: list) -> list:
    """
    Find all card detail HTML pages.
    Excludes known non-card-detail files.
    """
    # Files at the top level of a game subdirectory (CardList.html etc.) are excluded.
    # Card detail pages are always inside a subdirectory: GameDir/CardName/CardName.html
    # We also include files like CinderellaHistory.html, PuchiDerela.html that are
    # directly inside Mobamas/ but have dialogue tables — include all .html files.
    exclude_names = {
        'CardList.html',
        'EventList.html',
        'CostumeList.html',
        'UnitList.html',
    }

    results = []
    for base_dir in base_dirs:
        for dirpath, dirnames, filenames in os.walk(base_dir):
            for fname in filenames:
                if not fname.endswith('.html'):
                    continue
                if fname in exclude_names:
                    continue
                results.append(os.path.join(dirpath, fname))

    return sorted(results)


def main():
    base_dirs = [
        '/home/user/SugarHeartDB/Mobamas',
        '/home/user/SugarHeartDB/Deresute',
    ]

    pages = find_card_detail_pages(base_dirs)
    print(f'Found {len(pages)} candidate HTML pages.')

    modified = []
    skipped = []

    for page in pages:
        changed = convert_file(page)
        if changed:
            modified.append(page)
            print(f'  CONVERTED: {page}')
        else:
            skipped.append(page)

    print()
    print(f'=== Summary ===')
    print(f'Total pages scanned : {len(pages)}')
    print(f'Files modified      : {len(modified)}')
    print(f'Files unchanged     : {len(skipped)}')

    if modified:
        print()
        print('Modified files:')
        for p in modified:
            print(f'  {p}')


if __name__ == '__main__':
    main()
