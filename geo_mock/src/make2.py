import sys, os, json, importlib
sys.path.insert(0, os.path.dirname(__file__))
from engine2 import compose, place, render, CSS, leak, KANA
from engine import doc
import engine
engine.CSS = CSS
from exams_new import EXAMS
OUT = os.path.join(os.path.dirname(__file__), '..')
def run(n):
    ex = EXAMS[n]
    best = None
    for seed in range(300):
        items, secs = compose(ex); place(items, seed)
        b = [0]*4
        for i in items:
            if i['kind'] != 'w': b[i['pos']] += 1
        sc = max(b) - min(b)
        if best is None or sc < best[0]: best = (sc, seed)
    items, secs = compose(ex); place(items, best[1])
    body, total = render(ex, items, secs)
    open(os.path.join(OUT, f'mock{n}.html'), 'w').write(doc(f'地理総合 模擬問題{ex["no"]}', body))
    nm = sum(1 for i in items if i['kind'] != 'w'); p2 = sum(1 for i in items if i.get('pt') == 2 and i['kind'] != 'w'); nw = sum(1 for i in items if i['kind'] == 'w')
    bal = [0]*4
    for i in items:
        if i['kind'] != 'w': bal[i['pos']] += 1
    per = [sum(1 for i in items if i['sec'] == s and i['kind'] != 'w') for s in range(len(secs))]
    print(f'exam{n}: total={total} marks={nm} 2pt={p2} 記述={nw} sec={per} bal={bal}')
    for x in leak(items, secs): print('  LEAK', x)
    json.dump([dict(no=i['no'], a=i['a'], q=i.get('q', ''), src=i.get('src', ''), sec=i['sec']) for i in items], open(os.path.join(OUT, f'.items{n}.json'), 'w'), ensure_ascii=False)
for a in sys.argv[1:]: run(int(a))
