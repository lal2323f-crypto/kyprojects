import sys, importlib, json, subprocess, os
sys.path.insert(0, os.path.dirname(__file__))
from engine import *
OUT = os.path.join(os.path.dirname(__file__), '..')
def run(n, seed):
    m = importlib.import_module(f'exam{n}')
    items, secs = build(m.EXAM, seed)
    body, total = render(m.EXAM, items, secs)
    p = os.path.join(OUT, f'mock{n}.html')
    open(p, 'w').write(doc(f'地理総合 模擬問題{m.EXAM["no"]}', body))
    probs = leak_check(m.EXAM, items, secs)
    nb = sum(1 for i in items if i['kind'] == 'blank'); ns = sum(1 for i in items if i['kind'] == 'mc'); nw = sum(1 for i in items if i['kind'] == 'w')
    print(f'exam{n}: total={total} blanks={nb} subs={ns} 記述={nw} balance={balance(items)}')
    for x in probs: print('  LEAK', x)
    json.dump([dict(no=i['no'], a=i['a'], q=i.get('q', ''), src=i.get('src', ''), sec=i['sec']) for i in items], open(os.path.join(OUT, f'.items{n}.json'), 'w'), ensure_ascii=False)
    return p
if __name__ == '__main__':
    for n in sys.argv[1:]: run(int(n), 100 + int(n))
