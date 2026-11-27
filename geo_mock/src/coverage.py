import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from topics import T
D = os.path.join(os.path.dirname(__file__), '..')
def load(n):
    return json.load(open(os.path.join(D, f'.items{n}.json')))
def hit(items):
    txt = ' '.join(i['a'] + ' ' + i['q'] for i in items)
    ans = {i['a'] for i in items}
    def m(w):
        return (w[1:] in ans) if w.startswith('=') else (w in txt)
    return {k for k, (g, lab, kws) in enumerate(T) if any(m(w) for w in kws)}
if __name__ == '__main__':
    ns = [int(x) for x in sys.argv[1:]]
    cum = set()
    for n in ns:
        h = hit(load(n)); cum |= h
        print(f'模擬{n}: 単独 {len(h)}/{len(T)} ({len(h)*100//len(T)}%)  累計 {len(cum)}/{len(T)} ({len(cum)*100//len(T)}%)')
    print('未出題:'); [print('  ', T[k][0], T[k][1]) for k in range(len(T)) if k not in cum]
