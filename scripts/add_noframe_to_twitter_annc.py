"""予告タブ内の Twitter告知 セクションの no-shot 行に no-frame クラスを追加する"""
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
    in_twitter = False
    modified_lines = []
    changes = []

    for i, line in enumerate(lines, 1):
        # 予告タブパネル開始
        if re.search(r'data-tab="[^"]*-trailer"', line) and 'tab-panel' in line:
            in_trailer = True
            in_twitter = False
        # 次のタブパネル開始 → 予告タブ終了
        elif 'tab-panel' in line and re.search(r'data-tab="[^"]*"', line) and '-trailer"' not in line:
            in_trailer = False
            in_twitter = False

        if in_trailer:
            # Twitter告知 セクション開始
            if 'ev-label">Twitter告知</span>' in line:
                in_twitter = True
            # 次の ev-condition （別セクション）→ Twitter告知 終了
            elif 'ev-condition' in line and 'Twitter告知' not in line and in_twitter:
                in_twitter = False

        # Twitter告知 セクション内の no-shot 行に no-frame を追加
        if in_twitter and 'class="ev-dialog-row no-shot"' in line:
            new_line = line.replace('class="ev-dialog-row no-shot"', 'class="ev-dialog-row no-shot no-frame"', 1)
            modified_lines.append(new_line)
            changes.append(f'  Line {i}')
        else:
            modified_lines.append(line)

    if changes:
        print(f'{filename}: {len(changes)} 行変更')
        for c in changes:
            print(c)
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.writelines(modified_lines)
        total_changes += len(changes)
    else:
        print(f'{filename}: 変更なし')

print(f'\n合計: {total_changes} 行に no-frame を追加')
