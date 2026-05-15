#!/usr/bin/env python3
"""
Batch cleanup script for SugarHeartDB card detail HTML pages.

For each file found by: grep -rl '<div class="sub-title">' --include="*.html"

1. Remove old Google Fonts preconnect/stylesheet link lines from <head>
2. Move any <script> block between </head> and <body> to just before </body>
"""

import subprocess
import re
import sys

def find_target_files():
    result = subprocess.run(
        ['grep', '-rl', '<div class="sub-title">', '/home/user/SugarHeartDB', '--include=*.html'],
        capture_output=True, text=True
    )
    files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
    return files


def remove_font_links(content):
    """Remove the three Google Fonts link lines from <head>."""
    # Match each of the three lines with flexible whitespace, including optional trailing whitespace
    patterns = [
        r'[ \t]*<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*\n',
        r'[ \t]*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*\n',
        r'[ \t]*<link href="https://fonts\.googleapis\.com/css2\?family=Yusei\+Magic&display=swap" rel="stylesheet">\s*\n',
    ]
    changed = False
    for pat in patterns:
        new_content, count = re.subn(pat, '', content)
        if count > 0:
            changed = True
            content = new_content
    return content, changed


def move_script_before_body(content):
    """
    If there is a <script>...</script> block between </head> and <body>,
    move it to just before </body>.
    Returns (new_content, changed).
    """
    # Pattern: </head> then optional whitespace/newlines then <script>...</script> then optional whitespace/newlines then <body>
    pattern = re.compile(
        r'(</head>)\s*(<script>.*?</script>)\s*(<body>)',
        re.DOTALL | re.IGNORECASE
    )

    match = pattern.search(content)
    if not match:
        return content, False

    head_close = match.group(1)
    script_block = match.group(2)
    body_open = match.group(3)

    # Remove the script from between </head> and <body>
    new_content = pattern.sub(head_close + '\n' + body_open, content, count=1)

    # Insert the script just before </body>
    # Find the last </body> in the file
    body_close_pattern = re.compile(r'</body>', re.IGNORECASE)
    matches = list(body_close_pattern.finditer(new_content))
    if not matches:
        # No </body> found, just append before end
        new_content = new_content + '\n' + script_block + '\n'
    else:
        last_body_close = matches[-1]
        insert_pos = last_body_close.start()
        new_content = (
            new_content[:insert_pos]
            + script_block + '\n'
            + new_content[insert_pos:]
        )

    return new_content, True


def process_file(filepath):
    """Process a single file. Returns a dict describing what was done."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    # Skip files already using page-hero (already V2)
    if 'page-hero' in original:
        return {'file': filepath, 'skipped': 'already V2 (page-hero)', 'changed': False}

    content = original
    font_removed = False
    script_moved = False

    # Step 1: Remove font links (only if present)
    if 'fonts.googleapis.com' in content:
        content, font_removed = remove_font_links(content)

    # Step 2: Move script block if it's between </head> and <body>
    content, script_moved = move_script_before_body(content)

    changed = font_removed or script_moved

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return {
        'file': filepath,
        'skipped': None,
        'changed': changed,
        'font_removed': font_removed,
        'script_moved': script_moved,
    }


def main():
    files = find_target_files()
    print(f"Found {len(files)} target files.\n")

    results = []
    for filepath in files:
        result = process_file(filepath)
        results.append(result)

    # Summary
    skipped = [r for r in results if r['skipped']]
    changed = [r for r in results if r.get('changed')]
    unchanged = [r for r in results if not r.get('changed') and not r['skipped']]
    font_removed_count = sum(1 for r in results if r.get('font_removed'))
    script_moved_count = sum(1 for r in results if r.get('script_moved'))

    print("=== RESULTS ===")
    print(f"Total files processed : {len(files)}")
    print(f"Files changed         : {len(changed)}")
    print(f"  - Font links removed: {font_removed_count}")
    print(f"  - Script block moved: {script_moved_count}")
    print(f"Files skipped (V2)    : {len(skipped)}")
    print(f"Files unchanged       : {len(unchanged)}")

    if skipped:
        print("\nSkipped files:")
        for r in skipped:
            print(f"  [SKIP] {r['file']}  ({r['skipped']})")

    if unchanged:
        print("\nUnchanged files (no font links, no misplaced script):")
        for r in unchanged:
            print(f"  [--]   {r['file']}")

    if changed:
        print("\nChanged files:")
        for r in changed:
            tags = []
            if r.get('font_removed'):
                tags.append('font-removed')
            if r.get('script_moved'):
                tags.append('script-moved')
            print(f"  [OK]   {r['file']}  ({', '.join(tags)})")

    print("\nDone.")


if __name__ == '__main__':
    main()
