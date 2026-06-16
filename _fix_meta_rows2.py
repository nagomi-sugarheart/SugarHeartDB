import re
from pathlib import Path

BASE_DIR = Path('C:/Users/sawas/Desktop/SugarHeartDB')

# After the first pass, orphaned old rows remain after the new </div>.
# Pattern: match the orphaned rows between </div> (new grid end) and </div>\n            </div>
# Specifically, remove lines that are old v2-meta-row divs with the old key labels.

OLD_ROW_PATTERN = re.compile(
    r'\n\s*<div class="v2-meta-row"><span class="v2-meta-k">(?:最大Lv|コスト|最大攻\（初期攻\）|最大守\（初期守\）|特技\（効果\）)</span>.*?</div>',
    re.DOTALL
)

# Also need to remove the extra orphaned </div> that was the old grid closing tag.
# It appears as a line with just spaces + </div> right after the last orphaned row.
# We'll remove this extra </div> that immediately follows the last old row removal.
# To do this safely, we look for the pattern:
#   </div>
#     </div>        ← this is the extra one (v2-meta-panel closing was already there)
# Actually, the structure after first pass is:
#   </div>    ← new grid closing
#   <old rows>
# </div>      ← was old grid closing, now orphaned
#             </div>  ← v2-meta-panel closing

ORPHAN_CLOSING = re.compile(
    r'(\n\s*</div>)(\n\s*</div>)(\n\s*</div>)',
    # We want to remove the middle </div> that's the orphaned grid closing
)

html_files = list((BASE_DIR / 'Mobamas').rglob('*.html'))
fixed = []

for p in sorted(html_files):
    content = p.read_text(encoding='utf-8')
    if 'v2-meta-grid' not in content:
        continue

    # Check if there are still orphaned rows
    if not re.search(r'<div class="v2-meta-row"><span class="v2-meta-k">最大Lv</span>', content):
        continue

    original = content

    # Remove orphaned old rows
    content = OLD_ROW_PATTERN.sub('', content)

    # Now there should be an extra </div> left (old grid closing).
    # It appears after the new grid's </div> and before the v2-meta-panel's </div>.
    # Pattern: the sequence is now:
    #   "                </div>\n            </div>\n            </div>"
    # We want to remove the middle </div>.
    # The new grid's closing </div> has 16 spaces, the orphaned one has 16 spaces,
    # and v2-meta-panel's </div> has 12 spaces.
    content = re.sub(
        r'(                </div>)\n(                </div>)\n(            </div>)',
        r'\1\n\3',
        content
    )

    if content != original:
        p.write_text(content, encoding='utf-8')
        rel = str(p.relative_to(BASE_DIR))
        fixed.append(rel)
        print('Fixed:', rel)

print('---')
print('Total fixed:', len(fixed))
