# 本番の過去問に近い形（問題用紙・解答用紙・解答解説の3つ）を作る
import re
import math
import html as H
import build as B

KANJI_NUM = "〇一二三四五六"
FONT = '<link rel="stylesheet" href="fonts/400.css"><link rel="stylesheet" href="fonts/700.css">'
SERIF = '"Noto Serif JP", "IPAMincho", serif'


def kanji_digits(n):
    return "".join(KANJI_NUM[int(c)] if c.isdigit() else c for c in str(n))


# ------------------------------------------------------------------ 問題用紙
QCSS = B.VCSS + f"""
body {{ font-family: {SERIF}; font-size: 11pt; line-height: 1.85; }}
.head {{ font-weight: bold; font-size: 12pt; margin-inline-end: 0; }}
.head .r {{ margin-inline-start: 2em; }}
.head .nm {{ font-weight: normal; margin-inline-start: 2em; }}
.notes2 {{ font-size: 10pt; margin: 0 6px 0 14px; }}
.sec {{ border: none; margin-block-start: 0; margin-inline: 10px 0; padding: 0; }}
.secno {{ background: none; color: #000; font-weight: bold; inline-size: auto; block-size: auto; }}
.sectxt {{ font-weight: bold; }}
.pt {{ font-weight: bold; }}
.q {{ font-weight: normal; }}
.grid3, .grid2, .nogrid {{ display: block; margin-inline-start: 1.2em; }}
.kq {{ display: inline-block; inline-size: 47%; margin-inline-end: 2%; margin-block-end: 0; vertical-align: top; }}
"""


def sec_head_exam(no, text, pts, kanten):
    tag = "【知技】" if kanten == "知" else "【思判表】"
    return f'<div class="sec"><span class="secno">{no}　</span><span class="sectxt">{text}</span><span class="pt">{tag}（{pts}）</span></div>'


BOXLBL = r'(?:　?→　?)?(?:誤|正|主張|具体例|理由|[❶❷❸❹❺❻❼アイウエ①②③④⑤ａｂｃＡＢＣ]|\([a-d]\))?<span class="ab"[^>]*></span>(?:→)?'


def strip_boxes(h):
    h = re.sub(BOXLBL, "", h)
    h = re.sub(r'<div class="wb"[^>]*></div>', "", h)
    h = re.sub(r"(<br>)+(</div>)", r"\2", h)
    return h


def exam_header(m):
    return (f'<div class="head">国語表現（ビジネス）　第三学年　模擬テスト{kanji_digits(m)}（四十五分）'
            f'<span class="nm">組　　番　名前</span></div>'
            '<div class="notes2">※注意事項<br>・問題をよく読み、指示のない限りできるだけ漢字で書くこと。<br>'
            '・解答はすべて解答用紙に書くこと。誤字等に注意し、空欄を作らない努力をすること。<br>'
            '・字数制限には句読点や記号を含むので注意すること。<br>'
            '・漢字を書く際は楷書体で一画ずつはなして書くこと。<br>'
            '・（完答）とある問題は、すべて合って得点とする。</div>')


def problem_html(m):
    orig = B.sec_head
    B.sec_head = sec_head_exam
    import mock6
    mock6.sec_head = sec_head_exam
    try:
        M, doc, tot, chi = B.build(m)
    finally:
        B.sec_head = orig
        mock6.sec_head = orig
    body = doc.split("<body>")[1].split("</body>")[0]
    prob = body.split('<div class="keyh">')[0]
    prob = re.sub(r'<div class="cover">.*?</div>\s*<div class="notes">.*?</div>', "", prob, flags=re.S)
    # 大問1 の漢字は《　》で示す（本番と同じ）
    i = prob.find('<span class="secno">1　</span>')
    j = prob.find('<span class="secno">2　</span>')
    s1 = prob[i:j].replace("次の――線部のカタカナを", "次の《　》のカタカナを")
    s1 = re.sub(r"<u>(.*?)</u>", r"《\1》", s1)
    prob = prob[:i] + s1 + prob[j:]
    prob = strip_boxes(prob)
    title = f"【国語表現】模擬問題{B.MARU[m-1]}　問題"
    q = (f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>{title}</title>{FONT}<style>{QCSS}</style></head>'
         f'<body>{exam_header(m)}{B._tcy(prob)}</body></html>')
    return M, q, tot, chi


# ------------------------------------------------------------------ 解答用紙
ACSS = f"""
@page {{ size: A4 landscape; margin: 0; }}
html, body {{ margin: 0; }}
body {{ font-family: {SERIF}; color: #000; }}
.sheet {{ position: relative; width: 297mm; height: 210mm; box-sizing: border-box; padding: 10mm 10mm 8mm; }}
.wrap {{ display: flex; flex-direction: row-reverse; align-items: flex-start; gap: 3mm; transform-origin: top right; }}
.title {{ writing-mode: vertical-rl; font-size: 12pt; font-weight: bold; letter-spacing: .05em; height: 150mm; }}
.title .d {{ font-weight: normal; font-size: 10pt; margin-inline-start: 1em; }}
.name {{ writing-mode: vertical-rl; border: 1.4px solid #000; width: 9mm; height: 150mm; font-size: 10pt; padding: 2mm 0; box-sizing: border-box; }}
.name span {{ margin-block-end: 0; }}
.dai {{ display: flex; flex-direction: column; align-items: stretch; }}
.dai > .dh {{ border: 1.4px solid #000; border-bottom: none; text-align: center; font-size: 8pt; line-height: 1.5; }}
.mons {{ display: flex; flex-direction: row-reverse; border: 1.4px solid #000; }}
.mon {{ display: flex; flex-direction: column; border-left: 1px solid #000; }}
.mon:last-child {{ border-left: none; }}
.mh {{ font-size: 7pt; text-align: center; border-bottom: 1px solid #000; line-height: 1.5; white-space: nowrap; }}
.cols {{ display: flex; flex-direction: row-reverse; }}
.col {{ display: flex; flex-direction: column; border-left: 1px solid #000; }}
.col:last-child {{ border-left: none; }}
.cell {{ border-bottom: 1px solid #000; display: flex; flex-direction: column; }}
.cell:last-child {{ border-bottom: none; }}
.lbl {{ font-size: 6.5pt; text-align: center; border-bottom: .6px solid #000; line-height: 1.35; white-space: nowrap; overflow: hidden; }}
.area {{ flex: none; }}
.part {{ display: flex; flex-direction: column; }}
.part + .part {{ border-top: .6px dashed #000; }}
.pl {{ font-size: 6pt; text-align: center; line-height: 1.3; }}
.score {{ margin-top: 3mm; border: 1.4px solid #000; display: flex; flex-direction: column; }}
.score div {{ height: 7mm; border-bottom: 1px solid #000; position: relative; }}
.score div:last-child {{ border-bottom: none; }}
.score .sh {{ background: repeating-linear-gradient(45deg, #ccc 0 2px, #fff 2px 5px); }}
.score .mx {{ position: absolute; right: 1px; bottom: 0; font-size: 6pt; }}
.total {{ position: absolute; right: 10mm; bottom: 8mm; border: 1.4px solid #000; display: grid; grid-template-columns: 14mm 14mm 30mm; font-size: 8pt; }}
.total div {{ border-left: 1px solid #000; border-bottom: 1px solid #000; height: 7mm; display: flex; align-items: center; justify-content: flex-end; padding-right: 2px; }}
.total .k {{ justify-content: center; }}
.total .big {{ grid-row: span 2; font-size: 10pt; align-items: flex-end; }}
"""

CW = 8.5      # 1列の幅(mm)
CH = 5.0      # 1字あたりの高さ(mm)
MAXH = 132.0  # 1列の最大の高さ(mm)
LBLH = 3.6


def parse_label(l):
    """'2 問1(3)' -> ('2', '問1', '(3)')  /  '1(3)' -> ('1', '', '(3)')"""
    if " " in l:
        d, rest = l.split(" ", 1)
        mo = re.match(r"(問\d+(?:-\d+)?)(.*)", rest)
        if mo:
            return d, mo.group(1), mo.group(2) or ""
        return d, rest, ""
    mo = re.match(r"(\d+)(.*)", l)
    return mo.group(1), "", mo.group(2)


def clean_ans(a):
    a = re.sub(r"（[^）]*も可[^）]*）", "", a)
    a = re.sub(r"^[アイウエオカキク]（.*）$", lambda x: x.group(0)[0], a)
    return a


PART_RE = re.compile(r"^(①|②|③|④|⑤|主張|具体例|Ａ|Ｂ|Ｃ)(.+)$")


def parts_of(ans):
    a = clean_ans(ans)
    if "→" in a and len(a) <= 4:
        x, o = a.split("→")
        return [("誤", 1), ("正", 1)]
    if "　" in a:
        ps = []
        for piece in a.split("　"):
            mo = PART_RE.match(piece)
            if not mo:
                return [("", len(a))]
            ps.append((mo.group(1), len(re.sub(r"（.*?）", "", mo.group(2)))))
        return ps
    if a.startswith("（私の）"):
        a = "私の姉"
    if "→" in a:  # 並べ替え（ウ→イ→ア）
        return [("", len(a.replace("→", "")))]
    return [("", len(a))]


def cell_html(label, ans):
    ps = parts_of(ans)
    total_chars = sum(max(n, 1) for _, n in ps)
    long = total_chars > 22
    if long:
        ncols = math.ceil((total_chars + 2) / 24)
        w = CW * ncols
        h = MAXH - LBLH
        inner = f'<div class="area" style="height:{h:.1f}mm;width:{w:.1f}mm"></div>'
        return inner, w, h + LBLH, label
    w = CW
    parts = []
    hsum = 0
    for pl, n in ps:
        h = max(2, n + 1) * CH * (0.85 if n <= 1 else 1)
        h = max(h, 9.0)
        hsum += h + (2.6 if pl else 0)
        parts.append(f'<div class="part">{f"<div class=pl>{pl}</div>" if pl else ""}<div class="area" style="height:{h:.1f}mm"></div></div>')
    return "".join(parts), w, hsum + LBLH, label


def sheet_html(M, m, tot, chi):
    # 大問 -> 問 -> [(小問ラベル, 答え)]
    dais = {}
    pts = {}
    kan = {}
    for l, a, p, k, e, s in M.key:
        d, mon, sub = parse_label(l)
        dais.setdefault(d, {}).setdefault(mon, []).append((sub, a))
        pts[d] = pts.get(d, 0) + p
        kan[d] = k
    blocks = []
    for d in sorted(dais, key=int):
        mons = []
        for mon, items in dais[d].items():
            cols, cur, curh = [], [], 0.0
            per = 6 if len(items) == 18 else 5  # 大問1の漢字は1列に5問（本番と同じ）
            for idx, (sub, a) in enumerate(items):
                lab = re.sub(r"[()（）]", "", sub) or "　"
                inner, w, h, _ = cell_html(lab, a)
                cell = f'<div class="cell" style="width:{w:.1f}mm"><div class="lbl">{H.escape(lab)}</div>{inner}</div>'
                if cur and ((d == "1" and mon == "" and idx % per == 0) or (not (d == "1" and mon == "") and curh + h > MAXH)):
                    cols.append(cur); cur, curh = [], 0.0
                cur.append(cell); curh += h
            if cur:
                cols.append(cur)
            colh = "".join(f'<div class="col">{"".join(c)}</div>' for c in cols)
            mh = f'<div class="mh">{mon}</div>' if mon else ""
            mons.append(f'<div class="mon">{mh}<div class="cols">{colh}</div></div>')
        sh_chi = "" if kan[d] == "知" else "sh"
        sh_shi = "sh" if kan[d] == "知" else ""
        score = (f'<div class="score"><div class="{sh_chi}">{"<span class=mx>"+str(pts[d])+"</span>" if kan[d]=="知" else ""}</div>'
                 f'<div class="{sh_shi}">{"<span class=mx>"+str(pts[d])+"</span>" if kan[d]!="知" else ""}</div></div>')
        blocks.append(f'<div class="dai"><div class="dh">{d}</div><div class="mons">{"".join(mons)}</div>{score}</div>')
    head = (f'<div class="title">国語表現（ビジネス）　第三学年　模擬テスト{kanji_digits(m)}　解答用紙'
            '</div>'
            '<div class="name"><span>三年</span>　　<span>組</span>　　　<span>番</span>　<span>氏名</span></div>')
    total = (f'<div class="total"><div class="k">知技</div><div>{chi}</div><div class="big">100</div>'
             f'<div class="k">思判表</div><div>{tot-chi}</div></div>')
    title = f"【国語表現】模擬問題{B.MARU[m-1]}　解答用紙"
    return (f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>{title}</title>{FONT}<style>{ACSS}</style></head>'
            f'<body><div class="sheet"><div class="wrap" id="wrap">{head}{"".join(blocks)}</div>{total}</div></body></html>')


# ------------------------------------------------------------------ 解答・解説
def key_html(M, m, tot, chi):
    rows = "".join(f'<tr><td class="c">{H.escape(l)}</td><td>{a}</td><td class="c">{p}</td><td class="c">{"知" if k=="知" else "思"}</td><td>{e}</td><td>{s}</td></tr>' for l, a, p, k, e, s in M.key)
    title = f"【国語表現】模擬問題{B.MARU[m-1]}"
    KCSS = B.CSS.replace("@page { size: A4; }", "@page { size: A4 landscape; }").replace(".keyh { page-break-before: always;", ".keyh {")
    KCSS += f"body {{ font-family: {SERIF}; }}"
    return (f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>{title} 解答・解説</title>{FONT}<style>{KCSS}</style></head><body>'
            f'<div class="keyh">{title}　解答・解説</div><div>配点合計 {tot}点（知識・技能 {chi}点／思考・判断・表現 {tot-chi}点）</div>'
            f'<table class="key"><colgroup><col style="width:10%"><col style="width:24%"><col style="width:4%"><col style="width:5%"><col style="width:35%"><col style="width:22%"></colgroup>'
            f'<tr><th>問</th><th>正解</th><th>点</th><th>観点</th><th>解説</th><th>出どころ</th></tr>{rows}</table></body></html>')


if __name__ == "__main__":
    for m in range(1, 7):
        M, q, tot, chi = problem_html(m)
        open(f"e{m}_q.html", "w").write(q)
        open(f"e{m}_a.html", "w").write(sheet_html(M, m, tot, chi))
        open(f"e{m}_k.html", "w").write(key_html(M, m, tot, chi))
        print(m, tot, chi)
