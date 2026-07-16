# -*- coding: utf-8 -*-
"""でれぽ書き起こしJSONの検証: 名前がCSVに存在するか / star!=0 / 投稿数を検出と照合"""
import sys, os, json, csv, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))

def load_names():
    names = set()
    with io.open(os.path.join(ROOT, 'data', 'cgss_idols.csv'), encoding='utf-8-sig') as f:
        for row in csv.reader(f):
            if row and row[0] and row[0] != 'アイドル名':
                names.add(row[0].strip())
    return names

def main(nums):
    names = load_names()
    try:
        from derepo_detect import detect_icons_n, src_path
        from PIL import Image
        have_detect = True
    except Exception as e:
        have_detect = False
        print('detect unavailable:', e)
    for n in nums:
        p = os.path.join(ROOT, 'scripts', 'derepo_text', '%d.json' % n)
        if not os.path.exists(p):
            print('[%d] MISSING json' % n); continue
        with io.open(p, encoding='utf-8') as f:
            data = json.load(f)
        posts = data.get('posts', [])
        issues = []
        for i, po in enumerate(posts):
            nm = po.get('name', '')
            if nm not in names:
                issues.append('post%d name不明:%s' % (i, nm))
            if po.get('star', 0) == 0 and po.get('text', '') != '':
                issues.append('post%d star=0' % i)
            if not po.get('md') or not po.get('time'):
                issues.append('post%d md/time欠落' % i)
        det = ''
        if have_detect:
            try:
                img = Image.open(src_path(n)).convert('RGB')
                tops = detect_icons_n(img, len(posts))
                if len(tops) != len(posts):
                    det = ' [検出%d != json%d]' % (len(tops), len(posts))
            except Exception as e:
                det = ' [detect err:%s]' % e
        status = 'OK' if not issues else 'NG'
        print('[%d] %s posts=%d%s %s' % (n, status, len(posts), det, '; '.join(issues)))

if __name__ == '__main__':
    nums = [int(x) for x in sys.argv[1:]]
    main(nums)
