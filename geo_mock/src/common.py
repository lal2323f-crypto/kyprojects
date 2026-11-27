from figs import *
def mc(q, a, w, src='', ex='', **k):
    d = dict(kind='mc', q=q, a=a, w=list(w), src=src, ex=ex); d.update(k); return d
def fx(q, choices, pos, src='', ex='', **k):
    """選択肢の順番を固定する問題（記号・組合せ）"""
    d = dict(kind='mc', q=q, a=choices[pos], w=[c for i, c in enumerate(choices) if i != pos], choices=choices, fixed=pos, src=src, ex=ex, nocheck=True); d.update(k); return d
def wr(q, a, src='', ex='', hint='', **k):
    d = dict(kind='w', q=q, a=a, src=src, ex=ex, hint=hint); d.update(k); return d
EUROPE = img('img/europe_q.png', 125, '地図Ⅰ')
NORDIC = img('img/nordic_q_s.png', 120, '地図Ⅱ')
AFCLIM = img('img/africa_clim_q.png', 95, '図　アフリカの気候区分（凡例は省略）')
def afclim(n): return img('img/africa_clim_q.png', 95, f'図{n}　アフリカの気候区分（凡例は省略）')

EUROPE1 = img('img/europe_q.png', 125, '地図')
NORDIC1 = img('img/nordic_q_s.png', 120, '地図')
