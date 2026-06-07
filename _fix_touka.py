import re
from pathlib import Path

BASE_DIR = Path('C:/Users/sawas/Desktop/SugarHeartDB')
html_files = list((BASE_DIR / 'Mobamas').rglob('*.html'))

CDN = 'https://res.cloudinary.com/dnmzdghoi/image/upload/f_auto,q_auto/'

fixed = []
for p in sorted(html_files):
    content = p.read_text(encoding='utf-8')
    if 'v2CardImages' not in content:
        continue

    original = content

    # Remove CDN URL entries ending in "Touka" from v2CardImages
    pattern_touka = r",\s*'" + re.escape(CDN) + r"[^']*Touka'"
    content = re.sub(pattern_touka, '', content)

    # Remove broken local paths (non-CDN single-quoted paths ending in image ext)
    pattern_local = r",\s*'Mobamas/[^']+\.(jpg|png|gif|webp)'"
    def keep_if_cdn(m):
        return m.group(0) if CDN in m.group(0) else ''
    content = re.sub(pattern_local, keep_if_cdn, content)

    if content != original:
        p.write_text(content, encoding='utf-8')
        rel = str(p.relative_to(BASE_DIR))
        fixed.append(rel)
        print('Fixed:', rel)

print('---')
print('Total fixed:', len(fixed))
