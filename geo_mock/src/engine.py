# 模擬問題の生成エンジン（問題データ → HTML → PDF、ヒント漏れチェック、カバー率）
import re, html, random, json, sys, os
E = html.escape
CIR = '①②③④'

def parse_blanks(lead):
    """[[正解|誤1|誤2|誤3|出どころ|解説]] を取り出す"""
    out = []
    def rep(m):
        parts = m.group(1).split('|')
        out.append(dict(kind='blank', a=parts[0], w=parts[1:4], src=parts[4] if len(parts) > 4 else '',
                        ex=parts[5] if len(parts) > 5 else ''))
        return '\x00%d\x00' % (len(out) - 1)
    t = re.sub(r'\[\[(.+?)\]\]', rep, lead, flags=re.S)
    return t, out

def isnum(s):
    return re.fullmatch(r'[0-9０-９.,]+(%|％|か国|m|ｍ|度|倍|円|年|位|時間|億人)?', s.strip()) is not None

def numval(s):
    return float(re.sub(r'[^0-9.]', '', s.translate(str.maketrans('０１２３４５６７８９', '0123456789'))) or 0)

def build(exam, seed):
    items = []      # 採点する全項目（順番どおり）
    secs = []
    for si, sec in enumerate(exam['sections']):
        t, blanks = parse_blanks(sec['lead'])
        bl_ids = []
        for b in blanks:
            b['sec'] = si; items.append(b); bl_ids.append(len(items) - 1)
        sub_ids = []
        for q in sec.get('subs', []):
            q = dict(q); q.setdefault('kind', 'mc'); q['sec'] = si
            items.append(q); sub_ids.append(len(items) - 1)
        secs.append(dict(sec=sec, text=t, bl=bl_ids, subs=sub_ids))
    # 番号
    n = 0; wn = 0; KANA = 'あいうえおかきくけこ'
    for it in items:
        if it['kind'] == 'w':
            it['no'] = KANA[wn]; wn += 1
        else:
            n += 1; it['no'] = str(n)
    # 正解の位置を散らす
    mcs = [it for it in items if it['kind'] != 'w']
    rnd = random.Random(seed)
    seq = []
    while len(seq) < len(mcs):
        blk = [0, 1, 2, 3]; rnd.shuffle(blk); seq += blk
    for it, p in zip(mcs, seq):
        if it.get('fixed') is not None:
            ch = list(it['choices']); it['pos'] = it['fixed']
        elif all(isnum(x) for x in [it['a']] + it['w']):
            ch = sorted([it['a']] + it['w'], key=numval); it['pos'] = ch.index(it['a'])
        else:
            ch = list(it['w']); ch.insert(p, it['a']); it['pos'] = p
        it['ch'] = ch
        it['pt'] = it.get('pt', 1 if it['kind'] == 'blank' else 2)
    for it in items:
        if it['kind'] == 'w': it['pt'] = 2
    return items, secs

def ul(t):
    return re.sub(r'<<([A-Z]):(.+?)>>', r'<span class="ul">\2</span><span class="ull">\1)</span>', t)

def render(exam, items, secs):
    total = sum(i['pt'] for i in items)
    nmc = sum(1 for i in items if i['kind'] != 'w'); nw = sum(1 for i in items if i['kind'] == 'w')
    H = []
    # 表紙
    H.append(f'''<section class="cover"><div class="ctop">2026年度　2学期期末考査（模擬）</div>
<h1>地理総合　模擬問題{exam['no']}</h1><div class="cmeta">3年　（　　）組（　　）番　氏名（　　　　　　　　　　）</div>
<div class="cbox"><b>注意事項</b><ol>
<li>この問題用紙に直接答えを書き込む形式です（解答用紙はありません）。</li>
<li>マーク問題は ≪1≫〜≪{nmc}≫、記述問題は ≪あ≫〜≪{'あいうえおかきくけこ'[nw-1]}≫ です。</li>
<li>マーク問題は①〜④から最も適当なものを一つ選びなさい。</li>
<li>文中の空欄〔　〕は1点、下線部・図表などの小問は2点、記述は各2点（思考・判断・表現）です。</li>
<li>試験時間50分。100点満点。</li></ol></div>
<table class="ctab"><tr><th>設問</th>{''.join(f'<td>{i+1}</td>' for i in range(len(secs)))}<th>計</th></tr>
<tr><th>内容</th>{''.join(f'<td class="sm">{E(s["sec"]["short"])}</td>' for s in secs)}<td></td></tr>
<tr><th>配点</th>{''.join('<td>%d</td>' % sum(items[j]['pt'] for j in s['bl'] + s['subs']) for s in secs)}<td>{total}</td></tr></table>
<p class="cnote">{E(exam.get('note',''))}</p></section>''')
    # 本文
    for si, s in enumerate(secs):
        sec = s['sec']
        pts = sum(items[j]['pt'] for j in s['bl'] + s['subs'])
        H.append(f'<section class="q"><h2>設問{si+1}　{E(sec["title"])}（{pts}点）</h2>')
        txt = E(s['text']).replace('\n', '<br>')
        txt = re.sub(r'&lt;&lt;([A-Z]):(.+?)&gt;&gt;', r'<span class="ul">\2</span><span class="ull">\1)</span>', txt)
        def brep(m):
            it = items[s['bl'][int(m.group(1))]]
            return f'〔<b class="no">≪{it["no"]}≫</b>〕'
        txt = re.sub('\x00(\\d+)\x00', brep, txt)
        if sec.get('fig_before'): H.append(sec['fig_before'])
        H.append(f'<div class="lead">{txt}</div>')
        if s['bl']:
            H.append('<table class="chs">' + ''.join(
                f'<tr><td class="cn">≪{items[j]["no"]}≫</td>' + ''.join(f'<td>{CIR[k]} {E(c)}</td>' for k, c in enumerate(items[j]['ch'])) + '</tr>'
                for j in s['bl']) + '</table>')
        if sec.get('fig'): H.append(sec['fig'])
        for qi, j in enumerate(s['subs']):
            it = items[j]
            q = E(it['q']).replace('\n', '<br>')
            q = q.replace('[[FIG]]', '')
            H.append(f'<div class="sq"><span class="qh">問{qi+1}</span> {q}')
            if it.get('fig'): H.append(it['fig'])
            if it['kind'] == 'w':
                H.append(f'<div class="wbox">≪{it["no"]}≫<span class="wl">{E(it.get("hint",""))}</span></div></div>')
            else:
                H.append(f'<div class="ch">≪{it["no"]}≫ ' + ''.join(f'<span class="c">{CIR[k]} {E(c)}</span>' for k, c in enumerate(it['ch'])) + '</div></div>')
        H.append('</section>')
    # 解答・解説
    rows = []
    for it in items:
        if it['kind'] == 'w':
            a = it['a']
        else:
            a = f'{CIR[it["pos"]]} {it["a"]}'
        secno = it['sec'] + 1
        rows.append(f'<tr><td class="c">設問{secno}<br>≪{it["no"]}≫</td><td class="ans">{E(a)}</td><td class="c">{it["pt"]}</td><td>{E(it.get("ex",""))}</td><td class="src">{E(it.get("src",""))}</td></tr>')
    H.append(f'<section class="key"><h2>模擬問題{exam["no"]}　解答・解説</h2><table class="kt"><colgroup><col style="width:11%"><col style="width:24%"><col style="width:4%"><col style="width:38%"><col style="width:23%"></colgroup><thead><tr><th>問</th><th>正解</th><th>点</th><th>解説</th><th>出どころ</th></tr></thead><tbody>{"".join(rows)}</tbody></table></section>')
    return '\n'.join(H), total

CSS = '''@page{size:A4;margin:14mm 13mm}
body{font-family:"IPAGothic",sans-serif;font-size:10.3pt;line-height:1.62;color:#111}
.cover{page-break-after:always;text-align:center;padding-top:30mm}
.ctop{font-size:12pt}.cover h1{font-size:24pt;margin:8mm 0}
.cmeta{font-size:12pt;margin-bottom:10mm}
.cbox{border:1.5px solid #000;text-align:left;padding:4mm 6mm;margin:0 10mm 8mm}
.cbox ol{margin:2mm 0 0 5mm;padding:0}
.ctab{border-collapse:collapse;margin:0 auto}.ctab td,.ctab th{border:1px solid #000;padding:2mm 3mm;min-width:12mm}
.ctab .sm{font-size:8.5pt}.cnote{font-size:9pt;color:#333;margin-top:8mm}
h2{font-size:11.5pt;border-top:2px solid #000;border-bottom:1px solid #000;padding:1.2mm 0;margin:5mm 0 2mm;page-break-after:avoid}
.lead{border:1px solid #555;padding:2.5mm 3.5mm;margin:2mm 0}
.no{font-weight:bold}
.ul{text-decoration:underline}.ull{font-size:8.5pt;vertical-align:super;margin-left:1px}
.chs{border-collapse:collapse;width:100%;font-size:9.8pt;margin:1.5mm 0 3mm}
.chs td{padding:0.6mm 2mm;border-bottom:1px dotted #aaa}.chs .cn{width:13mm;font-weight:bold}
.sq{margin:2.2mm 0 2.6mm;page-break-inside:avoid}.qh{font-weight:bold}
.ch{margin:1mm 0 0 6mm}.ch .c{display:inline-block;margin-right:7mm}
.wbox{border:1px solid #000;height:11mm;margin:1.5mm 0 0 6mm;width:85%;padding:1mm 2mm;font-weight:bold}
.wl{font-weight:normal;font-size:9pt;color:#444;margin-left:4mm}
.fig{text-align:center;margin:2mm 0;page-break-inside:avoid}.fig img{max-width:100%}
.figcap{font-size:9pt}
table.dt{border-collapse:collapse;margin:1mm auto;font-size:9.5pt}
table.dt td,table.dt th{border:1px solid #000;padding:0.6mm 3mm}table.dt th{background:#eee}
table.dt td.r{text-align:right}
.figrow{display:flex;gap:4mm;justify-content:center;align-items:flex-start;page-break-inside:avoid;margin:2mm 0}
.key{page-break-before:always}
.kt{border-collapse:collapse;width:100%;font-size:8.8pt;table-layout:fixed}.kt td,.kt th{border:1px solid #777;padding:1mm 1.5mm;vertical-align:top}
.kt th{background:#e6e6e6}.kt .c{text-align:center;white-space:nowrap}.kt .ans{font-weight:bold}.kt .src{font-size:8.2pt}
tr{page-break-inside:avoid}'''

def doc(title, body):
    return f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>{E(title)}</title><style>{CSS}</style></head><body>{body}</body></html>'

def strip_tags(s):
    return re.sub(r'<[^>]+>', ' ', s)

def leak_check(exam, items, secs):
    """正解の語が、同じ回のほかの場所（問題文・選択肢・図表）に出ていないか"""
    probs = []
    for i, it in enumerate(items):
        if it.get('nocheck'): continue
        if isnum(it['a']): continue
        keys = it.get('keys') or [re.sub(r'[（(].*?[）)]', '', it['a']).strip()]
        others = []
        for s in secs:
            sec = s['sec']
            # 本文（自分以外の空欄はその選択肢、自分の空欄は空）
            t = s['text']
            t = re.sub('\x00\\d+\x00', ' ', t)
            others.append(('本文' + str(secs.index(s) + 1), strip_tags(t)))
            for k in ('fig', 'fig_before'):
                if sec.get(k): others.append(('図表' + str(secs.index(s) + 1), strip_tags(sec[k])))
        for j, o in enumerate(items):
            if j == i: continue
            if o['kind'] != 'w':
                others.append((f'≪{o["no"]}≫の選択肢', ' / '.join(o['ch'])))
            if o.get('q'): others.append((f'≪{o["no"]}≫の問題文', o['q']))
            if o.get('fig'): others.append((f'≪{o["no"]}≫の図', strip_tags(o['fig'])))
        if it.get('q'): pass
        for k in keys:
            if len(k) < 2: continue
            for where, txt in others:
                if k in txt:
                    probs.append(f'≪{it["no"]}≫ 正解「{k}」が {where} に出ている')
    return probs

def balance(items):
    c = [0, 0, 0, 0]
    for it in items:
        if it['kind'] != 'w': c[it['pos']] += 1
    return c
