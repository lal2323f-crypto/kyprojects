# 図・表（スライドの表は数値をそのまま写す）
def table(title, unit, rows, mark=None, hide=None, cap=''):
    """rows=[(国名, 数値)], hide={行番号: '記号'} で国名を記号に置き換える"""
    hide = hide or {}
    tr = ''.join(f'<tr><td>{hide.get(i, n)}</td><td class="r">{v}</td></tr>' for i, (n, v) in enumerate(rows))
    return f'<div><div class="figcap"><b>{title}</b></div><table class="dt"><tr><th>国名</th><th>{unit}</th></tr>{tr}</table><div class="figcap">{cap}</div></div>'

def row(*parts, cap=''):
    return f'<div class="figrow">{"".join(parts)}</div>' + (f'<div class="figcap" style="text-align:center">{cap}</div>' if cap else '')

def img(path, w, cap=''):
    return f'<div class="fig"><img src="{path}" style="width:{w}mm"><div class="figcap">{cap}</div></div>'

CASSAVA = [('ナイジェリア', '5,919'), ('コンゴ民主', '4,005'), ('タイ', '3,108'), ('ガーナ', '2,245'), ('ブラジル', '1,750')]
CACAO = [('コートジボワール', '2,180'), ('ガーナ', '812'), ('インドネシア', '784'), ('ナイジェリア', '350'), ('エクアドル', '284'), ('カメルーン', '280')]
COFFEE = [('ブラジル', '3,009'), ('ベトナム', '1,684'), ('コロンビア', '885'), ('インドネシア', '761'), ('エチオピア', '483'), ('ホンジュラス', '476')]
TEA = [('中国', '2,777'), ('インド', '1,390'), ('ケニア', '459'), ('スリランカ', '300'), ('ベトナム', '269'), ('トルコ', '261')]
COPPER = [('チリ', '583'), ('ペルー', '244'), ('中国', '159'), ('コンゴ民主共和国', '123'), ('アメリカ', '122'), ('オーストラリア', '92'), ('ザンビア', '85'), ('メキシコ', '75'), ('ロシア', '75'), ('インドネシア', '65')]
GOLD = [('中国', '401'), ('オーストラリア', '315'), ('ロシア', '311'), ('アメリカ', '226'), ('カナダ', '183'), ('ペルー', '143'), ('インドネシア', '135'), ('ガーナ', '127'), ('メキシコ', '117'), ('南アフリカ共和国', '117')]
DIAMOND = [('ロシア', '4,320'), ('ボツワナ', '2,441'), ('カナダ', '2,319'), ('コンゴ民主共和国', '1,513'), ('オーストラリア', '1,408'), ('南アフリカ共和国', '991'), ('アンゴラ', '841'), ('ジンバブエ', '326'), ('ナミビア', '240'), ('レソト', '129')]

def climograph(title, temps, prec, w=230, h=200):
    """雨温図（模式図）。気温 -20〜40℃、降水量 0〜600mm"""
    L, R, T, B = 34, w - 36, 22, h - 24
    def ty(t): return B - (t + 20) / 60 * (B - T)
    def py(p): return B - p / 600 * (B - T)
    bw = (R - L) / 12
    s = [f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg" font-family="IPAGothic" font-size="9">']
    s.append(f'<text x="{w/2}" y="12" text-anchor="middle" font-size="10" font-weight="bold">{title}</text>')
    for t in range(-20, 41, 10):
        y = ty(t); s.append(f'<line x1="{L}" y1="{y}" x2="{R}" y2="{y}" stroke="#bbb" stroke-width="0.6"/>')
        s.append(f'<text x="{L-3}" y="{y+3}" text-anchor="end">{t}</text>')
        s.append(f'<text x="{R+3}" y="{y+3}">{(t+20)*10}</text>')
    for i, p in enumerate(prec):
        x = L + i * bw + 1.5; s.append(f'<rect x="{x}" y="{py(p)}" width="{bw-3}" height="{B-py(p)}" fill="#7aa7c7" stroke="#336" stroke-width="0.5"/>')
    pts = ' '.join(f'{L+(i+0.5)*bw},{ty(t)}' for i, t in enumerate(temps))
    s.append(f'<polyline points="{pts}" fill="none" stroke="#c00" stroke-width="2"/>')
    s.append(f'<rect x="{L}" y="{T}" width="{R-L}" height="{B-T}" fill="none" stroke="#000"/>')
    for i, m in ((0, 1), (6, 7), (11, 12)):
        s.append(f'<text x="{L+(i+0.5)*bw}" y="{B+11}" text-anchor="middle">{m}月</text>')
    s.append(f'<text x="{L-28}" y="{T-6}">気温(℃)</text><text x="{R-6}" y="{T-6}">降水量(mm)</text></svg>')
    return ''.join(s)

CS_N = ([12, 12, 14, 16, 19, 23, 25, 26, 24, 20, 16, 13], [90, 80, 60, 50, 30, 10, 3, 5, 30, 60, 90, 110])
CS_S = ([22, 22, 21, 18, 16, 14, 13, 14, 15, 17, 19, 21], [15, 15, 20, 40, 70, 90, 85, 70, 40, 30, 15, 15])
AF = ([26, 26, 27, 27, 26, 25, 24, 24, 25, 26, 26, 26], [250, 240, 330, 340, 240, 60, 40, 60, 160, 370, 380, 250])
AW = ([25, 28, 31, 32, 31, 28, 26, 26, 27, 28, 27, 25], [0, 0, 3, 15, 60, 140, 220, 270, 180, 60, 5, 0])
BW = ([14, 15, 18, 22, 25, 27, 28, 28, 26, 24, 19, 15], [5, 4, 3, 1, 0, 0, 0, 0, 0, 1, 3, 5])
DFB = ([-3, -3, 0, 5, 11, 16, 18, 17, 12, 7, 3, -1], [39, 27, 26, 30, 30, 45, 72, 66, 55, 50, 53, 46])
ET = ([-12, -12, -10, -6, 0, 4, 7, 6, 2, -3, -8, -11], [40, 35, 30, 25, 25, 35, 45, 50, 45, 45, 40, 40])
