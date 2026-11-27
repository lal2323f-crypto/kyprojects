import sys, re
sys.path.insert(0, '.')
from exams_new import EXAMS
from engine2 import compose, place
CIR='①②③④'
def dump(n, out):
    ex = EXAMS[n]; items, secs = compose(ex); place(items, 0)
    issues = []
    for it in items:
        if it['kind'] != 'w':
            ch = it['ch']
            if len(set(ch)) != 4: issues.append(f'≪{it["no"]}≫ 選択肢が重複/4つでない: {ch}')
            if ch[it['pos']] != it['a']: issues.append(f'≪{it["no"]}≫ 正解位置ずれ')
            if sum(1 for c in ch if c == it['a']) != 1: issues.append(f'≪{it["no"]}≫ 正解が複数')
    for s in secs:
        sec = s['sec']
        if sec['kind'] == 'lead':
            t = s['text']
            t = re.sub('\x00(\\d+)\x00', lambda m: '【' + items[int(m.group(1))]['a'] + '】', t)
            t = re.sub('\x01(.)\x02(.*?)\x03', r'\1)〈\2〉', t)
            out.write(f'\n### 模擬{n} 大設問{secs.index(s)+1}（文章・答え入り）\n{t}\n')
            for j in s['bl']:
                it = items[j]; out.write(f'  ≪{it["no"]}≫ 正:{it["a"]} 誤:{"/".join(it["w"])}\n')
        else:
            out.write(f'\n### 模擬{n} 大設問{secs.index(s)+1}\n')
        for j in s['subs']:
            it = items[j]
            if it['kind'] == 'w': out.write(f'  ≪{it["no"]}≫[記述] {it["q"]} → {it["a"]}\n')
            else: out.write(f'  ≪{it["no"]}≫ {it["q"]} 正:{it["a"]} 誤:{" / ".join(c for c in it["ch"] if c != it["a"])}\n')
    return issues
with open(sys.argv[1], 'w') as f:
    for n in range(1, 7):
        iss = dump(n, f)
        print(n, iss)
