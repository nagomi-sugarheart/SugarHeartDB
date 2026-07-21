"""予告タブ内のすべての ev-dialog-row（shot付き）を no-shot に変換する"""
import re
import os

event_dir = r'C:\Users\sawas\Desktop\SugarHeartDB\Deresute\Event'
files = sorted([f for f in os.listdir(event_dir) if f.endswith('.html') and f != 'EventList.html'])

total_changes = 0

for filename in files:
    filepath = os.path.join(event_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_trailer = False
    modified_lines = []
    changes = []

    for i, line in enumerate(lines, 1):
        # 予告タブパネル開始
        if re.search(r'data-tab="[^"]*-trailer"', line) and 'tab-panel' in line:
            in_trailer = True
        # 次のタブパネル開始（予告以外）→ 終了
        elif 'tab-panel' in line and re.search(r'data-tab="[^"]*"', line) and '-trailer"' not in line:
            in_trailer = False

        if in_trailer and 'class="ev-dialog-row"' in line and 'ev-shot' in line:
            # no-shot クラスを追加し、ev-shot div を除去
            new_line = line.replace('"ev-dialog-row"', '"ev-dialog-row no-shot"', 1)
            new_line = re.sub(r'<div class="ev-shot">.*?</div>', '', new_line)
            modified_lines.append(new_line)
            changes.append(f'  Line {i}')
        else:
            modified_lines.append(line)

    if changes:
        print(f'{filename}: {len(changes)} 行変換')
        for c in changes:
            print(c)
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.writelines(modified_lines)
        total_changes += len(changes)
    else:
        print(f'{filename}: 変更なし')

print(f'\n合計: {total_changes} 行変換')
