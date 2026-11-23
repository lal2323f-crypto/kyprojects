# 12回分（書き込み式6＋解答用紙付き6）の自動チェック
import json, re, html, sys
import build as B, exam as E
KANA = "アイウエオカキクケコ"
def text(h):
    h = re.sub(r"<(div|br|p|tr)[^>]*>", "\n", h); h = re.sub(r"<[^>]+>", "", h)
    return html.unescape(h)
kd = "〇一二三四五六七八九"
def kn(n):
    t, o = divmod(n, 10); return ((("" if t == 1 else kd[t]) + "十") if t else "") + (kd[o] if o else "")
issues = []
for m in range(1, 7):
    key = json.load(open(f"key{m}.json"))
    wq = open(f"v{m}_q.html").read().split("<body>")[1]
    eq = open(f"e{m}_q.html").read().split("<body>")[1]
    sheet = open(f"e{m}_a.html").read()
    for name, src in (("書込", wq), ("用紙付", eq)):
        t = text(src)
        # 1 記号の答えと選択肢
        for l, a, p, k, e, s in key:
            mo = re.match(r"^([アイウエオカキク])（(.+?)）$", a)
            if mo and f"{mo.group(1)}　{mo.group(2)}" not in t:
                issues.append((m, name, l, "記号と選択肢が合わない", a))
        # 2 字数指定
        for mo in re.finditer(r"([〇一二三四五六七八九十]+)字で", t):
            pass
    # 3 配点
    tot = sum(r[2] for r in key); chi = sum(r[2] for r in key if r[3] == "知")
    if tot != 100: issues.append((m, "", "", "合計が100でない", tot))
    # 大問ごとの配点 = 見出し
    secpts = {}
    for l, a, p, k, e, s in key:
        d = l.split()[0] if " " in l else re.match(r"\d+", l).group(0)
        secpts[d] = secpts.get(d, 0) + p
    for d, p in secpts.items():
        if f'<span class="secno"><span class="tcy">{d}</span>　</span>' in eq:
            seg = eq.split(f'<span class="secno"><span class="tcy">{d}</span>　</span>')[1][:700]
            mo = re.search(r"（(\d+)）", re.sub("<[^>]+>", "", seg))
            if not mo or int(mo.group(1)) != p: issues.append((m, "用紙付", d, "大問の配点表示が違う", (mo and mo.group(1), p)))
        seg = wq.split(f'<span class="secno"><span class="tcy">{d}</span>')[1][:700]
        mo = re.search(r"（(\d+)点）", re.sub("<[^>]+>", "", seg))
        if not mo or int(mo.group(1)) != p: issues.append((m, "書込", d, "大問の配点表示が違う", (mo and mo.group(1), p)))
    if f"／{chi}" not in wq or f"／{tot-chi}" not in wq: issues.append((m, "書込", "表紙", "観点の点数が違う", chi))
    if f"<div>{chi}</div>" not in sheet or f"<div>{tot-chi}</div>" not in sheet: issues.append((m, "用紙付", "解答用紙", "観点の点数が違う", chi))
    # 4 字数指定と答えの字数（解答解説の「〇字」と照合）
    for l, a, p, k, e, s in key:
        mo = re.match(r"^([〇一二三四五六七八九十]+)字", e)
        if mo:
            ans = re.sub(r"（.*?も可）", "", a)
            if kn(len(ans)) != mo.group(1): issues.append((m, "", l, "字数が合わない", (ans, mo.group(1))))
    # 5 2つの形で問題文が同じか（記号の□や表紙を除いて比べる）
    def norm(h):
        h = re.sub(r'<div class="cover">.*?</div>\s*<div class="notes">.*?</div>', "", h, flags=re.S)
        h = re.sub(r'<div class="head">.*?</div><div class="notes2">.*?</div>', "", h, flags=re.S)
        h = E.strip_boxes(h)
        h = re.sub(r'<div class="sec">.*?</div>', "", h)
        h = h.replace("《", "").replace("》", "")
        t = text(h)
        return re.sub(r"\s+", "", t)
    a1, a2 = norm(wq), norm(eq)
    if a1 != a2:
        import difflib
        sm = difflib.SequenceMatcher(None, a1, a2)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal": issues.append((m, "比較", "", "2つの形で問題文が違う", (a1[i1-10:i2+10], a2[j1-10:j2+10])))
    # 6 解答用紙のますの数 = 解答の数
    cells = sheet.count('class="cell"')
    if cells != len(key): issues.append((m, "用紙付", "解答用紙", "ますの数が解答の数と違う", (cells, len(key))))
    # 7 解答用紙の大問ごとの点数欄
    for d, p in secpts.items():
        if f'<span class=mx>{p}</span>' not in sheet: issues.append((m, "用紙付", d, "点数欄の点が違う", p))
print(len(issues))
for x in issues: print(x)
