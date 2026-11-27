# 本物（2学期中間）の問題用紙に寄せたレイアウト
import re, html, random
from engine import isnum, numval, strip_tags
E = html.escape
CIR = '①②③④'
KANA = 'あいうえおかきくけこ'

def compose(exam):
    """sections: kind='q'（各問）/'lead'（文章＋空欄＋下線）/'map'（図＋各問）"""
    items = []; secs = []
    for si, sec in enumerate(exam['sections']):
        s = dict(sec=sec, bl=[], subs=[], text='')
        if sec['kind'] == 'lead':
            paras = []; letter = 0; linked = []
            for para in sec['paras']:
                ptxt = []
                for sen in para:
                    t = sen['t']
                    def brep(m):
                        p = m.group(1).split('|')
                        items.append(dict(kind='blank', a=p[0], w=p[1:4], src=p[4] if len(p) > 4 else '', ex=p[5] if len(p) > 5 else '', sec=si))
                        s['bl'].append(len(items) - 1)
                        return '\x00%d\x00' % (len(items) - 1)
                    t = re.sub(r'\[\[(.+?)\]\]', brep, t)
                    if '<<' in t:
                        L = 'ABCDEFGHIJKLMN'[letter]; letter += 1
                        t = re.sub(r'<<(.+?)>>', lambda m: f'\x01{L}\x02{m.group(1)}\x03', t)
                        for q in sen.get('subs', []):
                            linked.append((L, q))
                    ptxt.append(t)
                paras.append(''.join(ptxt))
            s['text'] = '\n'.join(paras)
            groups = []
            for L, q in linked:
                if groups and groups[-1][0] == f'{L})＿について、': groups[-1][1].append(q)
                else: groups.append((f'{L})＿について、', [q]))
            for q in sec.get('extra', []):
                groups.append((q.get('h', ''), [q]))
            s['groups'] = groups
        else:
            s['groups'] = [(q.get('h', ''), [q]) for q in sec['subs']]
        for h, qs in s['groups']:
            for q in qs:
                q = dict(q); q.setdefault('kind', 'mc'); q['sec'] = si
                items.append(q); s['subs'].append(len(items) - 1)
        secs.append(s)
    # 記号の番号：マークは出てくる順、記述はあ〜
    n = 0; wn = 0
    for s in secs:
        order = s['bl'] + s['subs']
        for j in order:
            it = items[j]
            if it['kind'] == 'w': it['no'] = KANA[wn]; wn += 1
            else: n += 1; it['no'] = str(n)
    return items, secs

def place(items, seed):
    rnd = random.Random(seed)
    mcs = [it for it in items if it['kind'] != 'w']
    seq = []
    while len(seq) < len(mcs):
        b = [0, 1, 2, 3]; rnd.shuffle(b); seq += b
    for it, p in zip(mcs, seq):
        if it.get('fixed') is not None:
            ch = list(it['choices']); it['pos'] = it['fixed']
        elif all(isnum(x) for x in [it['a']] + it['w']):
            ch = sorted([it['a']] + it['w'], key=numval); it['pos'] = ch.index(it['a'])
        else:
            ch = list(it['w']); ch.insert(p, it['a']); it['pos'] = p
        it['ch'] = ch
        it['pt'] = 2 if it.get('p2') else 1
    for it in items:
        if it['kind'] == 'w': it['pt'] = 2
    # 合計100点になるよう2点の問題数を調整（記述10点＋マーク90点）
    nm = len(mcs); need = 90 - nm
    two = [it for it in mcs if it['pt'] == 2]
    if len(two) > need:
        for it in two[need:]: it['pt'] = 1
    elif len(two) < need:
        cand = [it for it in mcs if it['pt'] == 1 and it['kind'] == 'mc']
        for it in cand[::-1][:need - len(two)]: it['pt'] = 2

def nb(no): return f'≪&nbsp;{no}&nbsp;≫'

def choices_html(it):
    ch = it['ch']; short = sum(len(c) for c in ch) <= 34 and max(len(c) for c in ch) <= 10
    if short:
        return '<div class="chl">' + ''.join(f'<span class="c">{CIR[k]}{E(c)}</span>' for k, c in enumerate(ch)) + '</div>'
    return '<div class="chv">' + ''.join(f'<div>{CIR[k]}{E(c)}</div>' for k, c in enumerate(ch)) + '</div>'

def abox(it):
    return f'<div class="abox"><span class="al">{nb(it["no"])}</span><span class="aw"></span></div>'

def render(exam, items, secs):
    H = []
    mk = [i for i in items if i['kind'] != 'w']; wk = [i for i in items if i['kind'] == 'w']
    H.append(f'''<section class="cover"><div class="crow"><div class="cyear">2026年度</div><div class="cdate">2026年12月1日(火) 1校時<br><span class="ctan">担当：岩佐、小田嶋、二見</span></div></div>
<h1>3学年地理総合　2学期期末テスト<br><span class="msub">模擬問題{exam['no']}</span></h1>
<div class="cnote">注意事項</div><div class="cbul">
<p>◆設問中の{nb(1)}〜{nb(len(mk))}、および{nb('あ')}〜{nb(KANA[len(wk)-1])}は解答欄の番号を指す。この模擬問題では、各問の右下の解答欄（四角）に直接答えを書き込むこと。</p>
<p>◆解答は明瞭に記入すること。<u>採点者が解読不可と判断した場合は得点とならない。</u></p>
<p>◆印刷不鮮明、ページの不足等が確認できた際は、速やかに挙手し、監督の先生に申し出ること。</p>
<p>◆テスト当日に欠席者がいた場合、問題冊子は回収となるので、必ずクラス・出席番号・氏名を記入すること。</p></div>
<div class="cname">＿＿組　＿＿番　氏名＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿</div>
</section>''')
    for si, s in enumerate(secs):
        sec = s['sec']
        bl = [items[j] for j in s['bl']]; sb = [items[j] for j in s['subs']]
        mcs = [i for i in sb if i['kind'] != 'w']; ws = [i for i in sb if i['kind'] == 'w']
        if sec['kind'] == 'lead':
            ins = f'次の文章は{sec["title"]}について述べたものである。空欄{nb(bl[0]["no"])}〜{nb(bl[-1]["no"])}の適語を選びなさい。'
            tail = []
            if mcs: tail.append(f'{nb(mcs[0]["no"])}〜{nb(mcs[-1]["no"])}')
            if ws: tail.append(f'{nb(ws[0]["no"])}' + (f'〜{nb(ws[-1]["no"])}' if len(ws) > 1 else ''))
            if tail: ins += 'また' + 'および'.join(tail) + 'に答えなさい。'
        elif sec['kind'] == 'map':
            ins = f'{sec["title"]}を見て、{nb(mcs[0]["no"])}〜{nb(mcs[-1]["no"])}' + (f'および{nb(ws[0]["no"])}' if ws else '') + 'に答えなさい。'
        else:
            ins = f'{sec["title"]}について、次の各問に答えなさい。'
        H.append(f'<section class="q{" brk" if si in (1, 2, 3, 5) else ""}"><h2>大設問{si+1}　{ins}</h2>')
        if sec.get('fig_before'): H.append(sec['fig_before'])
        if sec['kind'] == 'lead':
            t = E(s['text'])
            t = re.sub('\x00(\\d+)\x00', lambda m: f'<b>{nb(items[int(m.group(1))]["no"])}</b>', t)
            t = re.sub('\x01(.)\x02(.*?)\x03', r'<u>\1)\2</u>', t)
            H.append('<div class="lead">' + ''.join(f'<p>{p}</p>' for p in t.split('\n')) + '</div>')
            if sec.get('fig'): H.append(sec['fig'])
            for it in bl:
                H.append(f'<div class="bq"><div class="qbody"><span class="qn">{nb(it["no"])}：</span>{choices_html(it)}</div>{abox(it)}</div>')
        elif sec.get('fig'):
            H.append(sec['fig'])
        qn = 0
        k = 0
        for h, qs in s['groups']:
            qn += 1
            for q in qs:
                it = sb[k]; k += 1
                qt = E(it['q']).replace('\n', '<br>')
                first = (q is qs[0])
                if h:
                    head = (f'<div><span class="qh">問{qn}</span> {E(h)}</div>' if first else '')
                    lab = f'<div class="qq">{nb(it["no"])}：{qt}</div>'
                else:
                    head = ''
                    lab = f'<div class="qi"><span class="qh">問{qn}</span>　{nb(it["no"])}：{qt}</div>'
                if it['kind'] == 'w':
                    H.append(f'<div class="sq sqw">{head}{lab}' + (it.get('fig') or '') + f'<div class="wbox">{nb(it["no"])}<span class="wl">{E(it.get("hint",""))}</span></div></div>')
                else:
                    H.append(f'<div class="sq">{head}<div class="qrow"><div class="qbody">{lab}' + (it.get('fig') or '') + choices_html(it) + f'</div>{abox(it)}</div></div>')
        H.append('</section>')
    rows = []
    for it in items:
        a = it['a'] if it['kind'] == 'w' else f'{CIR[it["pos"]]} {it["a"]}'
        rows.append(f'<tr><td class="c">大設問{it["sec"]+1}<br>{nb(it["no"])}</td><td class="ans">{E(a)}</td><td class="c">{it["pt"]}</td><td>{E(it.get("ex",""))}</td><td class="src">{E(it.get("src",""))}</td></tr>')
    H.append(f'<section class="key"><h2 class="kh">模擬問題{exam["no"]}　解答・解説（100点）</h2><table class="kt"><colgroup><col style="width:12%"><col style="width:23%"><col style="width:4%"><col style="width:38%"><col style="width:23%"></colgroup><thead><tr><th>問</th><th>正解</th><th>点</th><th>解説</th><th>出どころ</th></tr></thead><tbody>{"".join(rows)}</tbody></table></section>')
    return '\n'.join(H), sum(i['pt'] for i in items)

CSS = '''@page{size:A4;margin:15mm 15mm 16mm}
body{font-family:"IPAGothic",sans-serif;font-size:10.4pt;line-height:1.75;color:#111}
.cover{page-break-after:always;padding:6mm 6mm 0}
.crow{display:flex;justify-content:space-between;align-items:flex-start}.cyear{font-size:22pt}
.cdate{text-align:right;font-size:10.5pt;line-height:2}.ctan{font-size:10pt}
.cover h1{text-align:center;font-size:19pt;font-weight:normal;margin:8mm 0 12mm;line-height:1.5}.msub{font-size:13pt}
.cnote{font-size:11pt;margin-bottom:3mm}.cbul p{font-size:11.5pt;line-height:2.1;margin:0 0 3mm 4mm}
.cname{margin:36mm 0 0 18mm;font-size:12pt}.cmeta{font-size:8.5pt;color:#555;margin-top:14mm}
h2{font-size:10.6pt;font-weight:bold;margin:6mm 0 2mm;page-break-after:avoid;break-inside:avoid}.brk{page-break-before:always}.brk h2{margin-top:0}
.lead p{text-indent:1em;margin:0 0 1.5mm}
.bq{display:flex;align-items:flex-end;margin:0.8mm 0 0.8mm 4mm;page-break-inside:avoid;border-bottom:1px dotted #ccc;padding-bottom:0.6mm}.bq .qbody{display:flex;flex:1}.bq .qbody .chl,.bq .qbody .chv{flex:1}.bq .qn{white-space:nowrap;min-width:15mm}
.qrow{display:flex;align-items:flex-end}.qrow .qbody{flex:1}
.abox{display:flex;align-items:center;margin-left:3mm;flex:none}.abox .al{font-size:8pt;margin-right:1mm;white-space:nowrap}.abox .aw{display:inline-block;width:12mm;height:8mm;border:1.2px solid #000}
.chl{display:flex;flex-wrap:nowrap}.chl .c{flex:1 1 0;min-width:0;padding-right:2mm}
.chv{margin-left:4mm}.chv div{margin:0.3mm 0}
.sq{margin:2.2mm 0 2.8mm}.qrow{page-break-inside:avoid}.sqw{page-break-inside:avoid}.qh{font-weight:normal}.qq{margin-left:4mm}.qi{text-indent:-12mm;padding-left:12mm}
.sq .chl,.sq .chv{margin-left:14mm}
.wbox{border:1px solid #000;height:10mm;margin:1.5mm 0 0 14mm;width:80%;padding:0.5mm 2mm}
.wl{font-size:9pt;color:#444;margin-left:4mm}
.fig{text-align:center;margin:2mm 0;page-break-inside:avoid}.fig img{max-width:100%}.figcap{font-size:9pt}
table.dt{border-collapse:collapse;margin:1mm auto;font-size:9.5pt}table.dt td,table.dt th{border:1px solid #000;padding:0.5mm 3mm}
table.dt th{background:#eee}table.dt td.r{text-align:right}
.figrow{display:flex;gap:4mm;justify-content:center;align-items:flex-start;page-break-inside:avoid;margin:2mm 0}
.key{page-break-before:always}.kh{font-size:12pt}
.kt{border-collapse:collapse;width:100%;font-size:8.6pt;table-layout:fixed;line-height:1.45}.kt td,.kt th{border:1px solid #777;padding:1mm 1.5mm;vertical-align:top}
.kt th{background:#e6e6e6}.kt .c{text-align:center}.kt .ans{font-weight:bold}.kt .src{font-size:8pt}tr{page-break-inside:avoid}'''

def leak(items, secs):
    probs = []
    texts = []
    for s in secs:
        sec = s['sec']
        t = re.sub('\x00\\d+\x00', ' ', s.get('text', ''))
        texts.append(('本文' + str(secs.index(s) + 1), strip_tags(t)))
        for k in ('fig', 'fig_before'):
            if sec.get(k): texts.append(('図表' + str(secs.index(s) + 1), strip_tags(sec[k])))
    for i, it in enumerate(items):
        if it.get('nocheck') or isnum(it['a']): continue
        keys = it.get('keys') or [re.sub(r'[（(].*?[）)]', '', it['a']).strip()]
        others = list(texts)
        for j, o in enumerate(items):
            if j == i: continue
            if o['kind'] != 'w': others.append((f'≪{o["no"]}≫の選択肢', ' / '.join(o['ch'])))
            if o.get('q'): others.append((f'≪{o["no"]}≫の問題文', o['q']))
            if o.get('fig'): others.append((f'≪{o["no"]}≫の図', strip_tags(o['fig'])))
        for k in keys:
            if len(k) < 2: continue
            for w, t in others:
                if k in t: probs.append(f'≪{it["no"]}≫「{k}」→{w}')
    return probs
