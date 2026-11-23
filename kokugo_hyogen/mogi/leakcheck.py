import json, re
KANA="アイウエオカキクケコ"
for m in range(1,7):
    doc = open(f"mogi{m}.html").read()
    prob = doc.split('<div class="keyh">')[0]
    txt = re.sub(r"<[^>]+>", "", prob)
    items = {x[0]:x for x in json.load(open(f"leak{m}.json"))}
    keys = json.load(open(f"key{m}.json"))
    for l,a,p,k,e,s in keys:
        choice = a[:1] in KANA and a[1:2] in ("（","") 
        mm = re.search(r"（(.+?)）", a)
        cands = []
        if choice and mm: cands=[mm.group(1)]
        elif l in items: cands = items[l][1]
        own = re.sub(r"<[^>]+>","",items[l][2]) if l in items else ""
        for c in cands:
            if c in ("○",) or len(c)<2: continue
            n = txt.count(c) - own.count(c) - (1 if choice else 0)
            if n>0:
                idx=[mo.start() for mo in re.finditer(re.escape(c), txt)]
                print(f"mock{m} {l} 「{c}」+{n}:", [txt[max(0,i-12):i+len(c)+6] for i in idx])
