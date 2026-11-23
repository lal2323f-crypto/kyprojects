import html as H, itertools, json, sys
from data_kanji import kanji_for
import data_note as N
import data_s5 as S5
import data_s6 as S6

KANA = "アイウエオカキクケコ"
MARU = "①②③④⑤⑥⑦⑧⑨⑩"


class Mock:
    def __init__(self, m):
        self.m = m
        self.parts = []
        self.key = []        # (label, ans, pts, kanten, expl, src)
        self.leak = []       # (label, [answers], text)
        self.letters = []    # 記号の正解（分布確認用）
        self._seq4 = itertools.cycle([1, 3, 0, 2, 2, 0, 3, 1, 0, 2, 1, 3, 3, 1, 2, 0])
        self._seq2 = itertools.cycle([1, 0, 0, 1, 1, 0, 1, 0])
        self._seq5 = itertools.cycle([3, 0, 4, 1, 2, 4, 2, 0, 1, 3])
        self._seq3 = itertools.cycle([2, 1, 0, 1, 2, 0])

    def pos(self, n):
        if n == 2:
            return next(self._seq2)
        if n == 5:
            return next(self._seq5)
        if n == 3:
            return next(self._seq3)
        return next(self._seq4) % n

    def choice(self, correct, wrongs, n=None):
        n = n or (len(wrongs) + 1)
        p = self.pos(n)
        opts = list(wrongs)
        opts.insert(p, correct)
        self.letters.append(KANA[p])
        return opts, KANA[p]

    def add(self, s):
        self.parts.append(s)

    def k(self, label, ans, pts, kanten, expl, src, check=None, text=""):
        self.key.append((label, ans, pts, kanten, expl, src))
        if check:
            self.leak.append((label, check, text))


def box(w=2.6, h=1.9):
    return f'<span class="ab" style="width:{w}em;height:{h}em"></span>'


def wbox(w=100):
    return f'<div class="wb" style="width:{w}%"></div>'


def opts_html(opts):
    return '<span class="opts">' + "　".join(f"{KANA[i]}　{o}" for i, o in enumerate(opts)) + "</span>"


def sec_head(no, text, pts, kanten):
    tag = "知識・技能" if kanten == "知" else "思考・判断・表現"
    return f'<div class="sec"><span class="secno">{no}</span><span class="sectxt">{text}</span><span class="tag">{tag}</span><span class="secpt">（{pts}点）</span></div>'


def kn(n):
    d = "〇一二三四五六七八九"
    t, o = divmod(n, 10)
    return (("" if t == 1 else d[t]) + "十" if t else "") + (d[o] if o else "")


def marks(s):
    out, pos = s, 0
    for L in "アイウエ":
        i = out.find(L, pos)
        if i < 0:
            break
        rep = f'<span class="mk">{L}</span>'
        out = out[:i] + rep + out[i+1:]
        pos = i + len(rep)
    return out


def ul_kata(sent, kata):
    return sent.replace(kata, f"<u>{kata}</u>", 1)


# ---------------------------------------------------------------- 大問1
def sec1(M):
    ks = kanji_for(M.m)
    M.add(sec_head(1, "次の――線部のカタカナを漢字に直しなさい。（送り仮名が必要なものは送り仮名も書くこと）", len(ks), "知"))
    M.add('<div class="grid3">')
    for i, (s, kata, ans, kai, no) in enumerate(ks, 1):
        ans_disp = ans + ("（甚だしい）" if ans == "甚" else "")
        M.add(f'<div class="kq"><span class="no">({i})</span>{ul_kata(s, kata)}<br>{box(6.5, 2.0)}</div>')
        M.k(f"1({i})", ans_disp, 1, "知", f"{kata}＝{ans}", f"漢字ボックス第{kai}回 書き{no}", [ans], s)
    M.add("</div>")


# ---------------------------------------------------------------- 大問2
def sec2(M):
    m = M.m
    M.add(sec_head(2, "同音異義語・異字同訓・間違えやすい漢字について、後の問いに答えなさい。", 14, "知"))
    M.add('<div class="q">問1　次の文の（　）に入る正しいほうを選び、記号で答えなさい。</div>')
    for i, (a, b, c, w, src) in enumerate(N.S2_CHOICE[m], 1):
        opts, L = M.choice(c, [w])
        M.add(f'<div class="item"><span class="no">({i})</span>{a}{KANA[0]}　{opts[0]}　・　{KANA[1]}　{opts[1]}{b}　{box()}</div>')
        M.k(f"2 問1({i})", f"{L}（{c}）", 1, "知", f"「{w}」ではなく「{c}」。", src, [c], a + b)
    M.add('<div class="q">問2　次の――線部のカタカナを漢字に直しなさい。（送り仮名が必要なものは送り仮名も書くこと）</div><div class="grid2">')
    for i, (s, kata, ans, src) in enumerate(N.S2_WRITE[m], 1):
        tail = s.split(kata, 1)[1]
        full = ans
        # 送り仮名
        okuri = {"熱": "熱い", "指": "指す", "刺": "刺す", "応": "応える", "収": "収める", "就": "就く"}
        if ans in okuri:
            # 傍線はカタカナ＋送り仮名まで
            kana_tail = okuri[ans][len(ans):]
            s2 = s.replace(kata + kana_tail, f"<u>{kata}{kana_tail}</u>", 1)
            full = okuri[ans]
        else:
            s2 = ul_kata(s, kata)
        M.add(f'<div class="kq"><span class="no">({i})</span>{s2}<br>{box(6.5, 2.0)}</div>')
        M.k(f"2 問2({i})", full, 1, "知", "", src, [ans], s)
    M.add("</div>")
    M.add('<div class="q">問3　次の文の中から間違っている漢字を一字抜き出し、正しい漢字に直しなさい。（完答）</div>')
    for i, (s, x, o, src) in enumerate(N.S2_FIX[m], 1):
        M.add(f'<div class="item"><span class="no">({i})</span>{s}　誤{box()}→正{box()}</div>')
        M.k(f"2 問3({i})", f"{x}→{o}", 2, "知", "誤りの字と正しい字の両方が合って2点。", src, [o], s)


# ---------------------------------------------------------------- 大問3
def sec3(M):
    m = M.m
    M.add(sec_head(3, "四字熟語・慣用句について、後の問いに答えなさい。", 12, "知"))
    yoji = N.S3_YOJI[m] if m != 5 else N.S3_YOJI[m][:3] + [N.S3_YOJI[m][3]]
    M.add('<div class="q">問1　次の文中の□に当てはまる漢字一字を書き、四字熟語を完成させなさい。</div>')
    yy = yoji if m != 5 else yoji[:3]
    for i, (s, a, src) in enumerate(yy, 1):
        M.add(f'<div class="item"><span class="no">({i})</span>{s}　{box()}</div>')
        M.k(f"3 問1({i})", a, 1, "知", "", src, [a], s)
    M.add('<div class="q">問2　次の文中の□に、体の一部を表す漢字一字を書き入れなさい。</div>')
    for i, (s, a, src) in enumerate(N.S3_BODY[m], 1):
        M.add(f'<div class="item"><span class="no">({i})</span>{s}　{box()}</div>')
        M.k(f"3 問2({i})", a, 1, "知", "", src, [a], s)
    M.add('<div class="q">問3　慣用句として正しいほうを選び、記号で答えなさい。</div>')
    for i, (a, b, c, w, src) in enumerate(N.S3_KANYO[m], 1):
        opts, L = M.choice(c, [w])
        M.add(f'<div class="item"><span class="no">({i})</span>{a}{KANA[0]}　{opts[0]}　・　{KANA[1]}　{opts[1]}{b}　{box()}</div>')
        M.k(f"3 問3({i})", f"{L}（{c}）", 1, "知", f"×「{w}」", src, [c], a + b)
    if m != 5:
        M.add('<div class="q">問4　次の文の――線部が正しければ○を、間違っていれば正しく書き直しなさい。</div>')
        for i, (s, u, a, src) in enumerate(N.S3_OX[m], 1):
            M.add(f'<div class="item"><span class="no">({i})</span>{s.replace(u, "<u>"+u+"</u>", 1)}　{box(7)}</div>')
            ex = "正しい慣用句なので○。" if a == "○" else f"正しくは「{a}」。"
            M.k(f"3 問4({i})", a, 2, "知", ex, src, [a] if a != "○" else None, s)
    else:
        # ⑤：四字熟語をもう1問 + □に言葉
        s, a, src = yoji[3]
        M.add('<div class="q">問4　次の文中の□に当てはまる言葉を書きなさい。</div>')
        items = [(s, a, src)] + N.S3_BLANK5
        # 四字熟語1問(1点)は問4の(1)として扱う → 合計 3+2+4+3=12
        for i, (s, a, src) in enumerate(items, 1):
            M.add(f'<div class="item"><span class="no">({i})</span>{s}　{box(5)}</div>')
            M.k(f"3 問4({i})", a, 1, "知", "", src, [a], s)


# ---------------------------------------------------------------- 大問4
def sec4(M):
    m = M.m
    M.add(sec_head(4, "敬語について、後の問いに答えなさい。", 13, "知"))
    M.add(f'<div class="q">問1　次の文の――線部の敬語の種類を、後のア〜ウから選び、記号で答えなさい。<br>{opts_html(["尊敬語", "謙譲語", "丁寧語"])}</div>')
    for i, n in enumerate(N.K1[m], 1):
        s, a, src = N.K1_POOL[n]
        L = KANA[["尊敬語", "謙譲語", "丁寧語"].index(a)]
        M.letters.append(L)
        M.add(f'<div class="item"><span class="no">({i})</span>{s}　{box()}</div>')
        M.k(f"4 問1({i})", f"{L}（{a}）", 1, "知", "", src)
    M.add('<div class="q">問2　次の問いに答えなさい。</div>')
    for i, it in enumerate(N.K2[m], 1):
        if it[0] == "fix":
            _, s, c, ws, src = it
            opts, L = M.choice(c, ws)
            M.add(f'<div class="item"><span class="no">({i})</span>――線部を最も適切な敬語表現に改めたものを選び、記号で答えなさい。<br>{s}<br>{opts_html(opts)}　{box()}</div>')
            M.k(f"4 問2({i})", f"{L}（{c}）", 2, "知", "過剰敬語（〜られる）や、尊敬語と謙譲語の取り違えに注意。", src, [c], s + "".join(ws))
        else:
            _, _, oks, bad, src = it
            opts, L = M.choice(bad, oks, 5)
            lines = "".join(f'<div class="opt">{KANA[j]}　{o}</div>' for j, o in enumerate(opts))
            M.add(f'<div class="item"><span class="no">({i})</span>次のア〜オから、敬語の使い方が間違っているものを一つ選び、記号で答えなさい。　{box()}{lines}</div>')
            M.k(f"4 問2({i})", f"{L}", 2, "知", f"誤り：「{bad}」", src, None, "".join(oks) + bad)
    M.add('<div class="q">問3　次の文の――線部を、（　）内の指示に従って適切な敬語表現に改めなさい。</div>')
    for i, (s, ins, a, alt, src) in enumerate(N.K3[m], 1):
        M.add(f'<div class="item"><span class="no">({i})</span>{s}（{ins}）<br>{box(len(a)*1.2+1.5)}</div>')
        M.k(f"4 問3({i})", a + (f"（{alt}も可）" if alt else ""), 2, "知", f"{kn(len(a))}字。" + ("「参りました」は自分の動作を聞き手に丁寧に言う形で、「先生」への敬意にはならない。" if a == "伺いました" else ""), src, [a], s)


# ---------------------------------------------------------------- 大問5
def sec5(M):
    m = M.m
    plan = S5.PLAN[m]
    M.add(sec_head(5, "文法と正しい表現について、後の問いに答えなさい。", 24, "思"))
    M.add('<div class="q">問1　次の文の（　）に入る最も適当な語を選び、記号で答えなさい。</div>')
    for i, code in enumerate(plan["q1"], 1):
        if code.startswith("H"):
            words, c, src, ex = S5.H[code]
            ws = [w for w in words if w != c]
            opts, L = M.choice(c, ws, 5)
            M.add(f'<div class="item"><span class="no">({i})</span>次の中で、一つだけ品詞の異なるものを選びなさい。<br>{opts_html(opts)}　{box()}</div>')
            M.k(f"5 問1({i})", f"{L}（{c}）", 1, "思", ex, src)
        else:
            a, b, c, ws, src, ex = S5.Q1[code]
            opts, L = M.choice(c, ws)
            M.add(f'<div class="item"><span class="no">({i})</span>{a}　　{b}<br>{opts_html(opts)}　{box()}</div>')
            M.k(f"5 問1({i})", f"{L}（{c}）", 1, "思", ex, src)
    M.add('<div class="q">問2　次の問いに答えなさい。</div>')
    for i, code in enumerate(plan["q2"], 1):
        if code in S5.COMMA:
            s, c1, a1, c2, a2, src = S5.COMMA[code]
            M.add(f'<div class="item"><span class="no">({i})</span>次の文に読点を一つ打つとき、最も適当な位置をア〜エから選びなさい。（①②完答）<br>{marks(s)}<br>①{c1}　{box()}　②{c2}　{box()}</div>')
            M.k(f"5 問2({i})", f"①{a1}　②{a2}", 2, "思", "読点は、意味の切れ目（どこにかかるか）を示す。", src)
        else:
            w, s, a, src, ex = S5.P[code]
            if w.startswith("（"):
                q = "次の文を二つの文に分けて書き換えるとき、一文目の終わりとして最も適当な位置をア〜エから選びなさい。"
            else:
                q = f"「{w}」という語を次の文に加えるとき、最も適当な位置をア〜エから選びなさい。"
            M.add(f'<div class="item"><span class="no">({i})</span>{q}<br>{marks(s)}　{box()}</div>')
            M.k(f"5 問2({i})", a, 2, "思", ex, src)
    if plan["q3"] == "CUKE":
        M.add(f'<div class="q">問3　次の文章の①〜⑤の文には、それぞれ一か所ずつ表現の誤りがある。その誤りの種類を後のア〜エから選び、記号で答えなさい。（同じ記号を何度使ってもよい）</div>')
        M.add('<div class="passage">' + "".join(f"{MARU[j]}{t}" for j, t in enumerate(S5.CUKE)) + "</div>")
        M.add(f'<div class="item">{opts_html(S5.CUKE_OPTS)}</div><div class="item">' + "　".join(f"{MARU[j]}{box()}" for j in range(5)) + "</div>")
        for j, (a, ex) in enumerate(S5.CUKE_ANS):
            L = KANA[S5.CUKE_OPTS.index(a)]
            M.k(f"5 問3{MARU[j]}", f"{L}（{a}）", 1, "思", ex, "ステ26 3")
    else:
        M.add(f'<div class="q">問3　次の文の――線部には表現の誤りがある。その誤りの種類を後のア〜オから選び、記号で答えなさい。<br>{opts_html(S5.E_OPTS)}</div>')
        for i, code in enumerate(plan["q3"], 1):
            s, a, src, ex = S5.E[code]
            L = KANA[S5.E_OPTS.index(a)]
            M.add(f'<div class="item"><span class="no">({i})</span>{s}　{box()}</div>')
            M.k(f"5 問3({i})", f"{L}（{a}）", 1, "思", ex, src)
    M.add('<div class="q">問4　次の文の――線部を、（　）内の指示に従って書き直しなさい。</div>')
    for i, code in enumerate(plan["q4"], 1):
        s, ins, a, alt, src = S5.W[code]
        M.add(f'<div class="item"><span class="no">({i})</span>{s}（{ins}）<br>{box(13)}</div>')
        M.k(f"5 問4({i})", a + (f"（{alt}も可）" if alt else ""), 2, "思", "", src, [a], s)
    M.add('<div class="q">問5　次の問いに答えなさい。</div>')
    for i, code in enumerate(plan["q5"], 1):
        if code == "TALK":
            t = S5.TALK
            txt = "<br>".join(t["text"])
            M.add(f'<div class="item"><span class="no">({i})</span>次の会話の〔　〕に、（　）内の字数の指示に従って適切な語句を補いなさい。（完答）<div class="passage">{txt}</div>' + "　".join(f"{MARU[j]}{box(4.5)}" for j in range(5)) + "</div>")
            M.k(f"5 問5({i})", "　".join(f"{MARU[j]}{a}" for j, a in enumerate(t["ans"])), 3, "思", "①推定②理由③打ち消しの推量④仮定⑤願望", t["src"])
        elif code == "SPLIT":
            t = S5.SPLIT
            M.add(f'<div class="item"><span class="no">({i})</span>次の文は一文が長すぎる。わかりやすくなるように三文に分けて全文を書き直しなさい。（完答）<div class="passage">{t["text"]}</div>{wbox()}{wbox()}</div>')
            M.k(f"5 問5({i})", t["ans"], 3, "思", "「〜があった。」「それは〜ことだ。」と、主語と述語がまとまるところで分ける。", t["src"])
        else:
            s, ins, a, src = S5.R[code]
            M.add(f'<div class="item"><span class="no">({i})</span>次の文を、後の指示に従って書き換えなさい。<div class="passage">{s}</div>〈指示〉{ins}{wbox()}</div>')
            M.k(f"5 問5({i})", a, 3, "思", "", src)


# ---------------------------------------------------------------- 大問6（10分ドリル）
def passage(paras):
    return '<div class="passage">' + "".join(f"<p>{p}</p>" for p in paras) + "</div>"


def mc_item(M, label, q, c, ws, pts, src, ex="", n=None):
    opts, L = M.choice(c, ws, n)
    lines = "".join(f'<div class="opt">{KANA[j]}　{o}</div>' for j, o in enumerate(opts))
    M.add(f'<div class="item">{q}　{box()}{lines}</div>')
    M.k(label, L, pts, "思", ex or f"正解：{c}", src)


def table10(nums=True):
    return ('<table class="dt"><tr><th></th><th>携帯できる数</th><th>連続して〔❶〕ができる時間</th><th>読書中にどのあたりを読んでいるかの把握</th></tr>'
            '<tr><td>〔❷〕</td><td>〔❸〕</td><td>半永久的</td><td>感覚的にわかる</td></tr>'
            '<tr><td>〔❹〕</td><td>多い</td><td>〔❺〕</td><td>〔❻〕</td></tr></table>')


def sec6_1(M):
    M.add('<div class="q">［Ａ］次の文章を読んで、後の問いに答えなさい。</div>' + passage(S6.D10_1))
    opts = ["電子書籍", "読書", "紙の本", "旅行", "バッテリーが切れるまで", "少ない", "携帯", "感覚的にわからない"]
    ans = {"❶": "読書", "❷": "紙の本", "❸": "少ない", "❹": "電子書籍", "❺": "バッテリーが切れるまで", "❻": "感覚的にわからない"}
    M.add(f'<div class="item">問1　文章をもとに作成した次の表を完成させるために、空欄❶〜❻に入る言葉を選択肢から選び、記号で答えなさい。{table10()}{opts_html(opts)}<br>' + "　".join(f"{k}{box()}" for k in ans) + "</div>")
    for k, v in ans.items():
        L = KANA[opts.index(v)]
        M.letters.append(L)
        M.k(f"6 問1{k}", f"{L}（{v}）", 1, "思", "", "ドリル10 1")
    M.add(f'<div class="item">問2　文章中で、電子書籍の利点として挙げられていることを、六字で抜き出しなさい。　{box(8)}</div>')
    M.k("6 問2", "かさばらない", 2, "思", "「電子書籍の利点として、かさばらないという点がある」", "ドリル10 1（本文）")
    mc_item(M, "6 問3", "問3　文章中の「一方」と同じ働きをする言葉として最も適当なものを選び、記号で答えなさい。", "これに対して", ["だから", "たとえば", "つまり"], 2, "ドリル10 POINT", "対比を表す接続語。")
    mc_item(M, "6 問4", "問4　筆者が最も言いたいことは何か。最も適当なものを選び、記号で答えなさい。",
            "電子書籍と紙の本にはどちらにもよい面があり、目的に合わせて使えば双方の利点を生かせる。",
            ["電子書籍は紙の本よりも便利なので、紙の本はいずれなくなる。", "紙の本は半永久的に読めるので、電子書籍よりすぐれている。", "電子書籍はバッテリー切れの心配があるので、使い方に注意が必要だ。"], 2, "ドリル10 1（最終段落）")
    M.add('<div class="q">［Ｂ］次の文章を読んで、後の問いに答えなさい。</div>' + passage(S6.D10_2))
    M.add('<div class="item">問5　次の図中の空欄Ａに入る言葉を、文章中から四字で抜き出しなさい。'
          '<div class="fig">語学習得のため／その国の文化を知るため　の手段<br>インターネット　⇔（対比）⇔　〔　Ａ　〕</div>' + box(6.5) + "</div>")
    M.k("6 問5", "海外留学", 2, "思", "インターネットと対比されているのは「海外留学」。", "ドリル10 2(1)")
    opts = ["成長に役立つこと", "Ａはお金がかかること", "外国語を学び、外国文化を知ることができること", "Ａには貴重な体験があること"]
    M.add(f'<div class="item">問6　次の文章中の空欄❶❷に入る言葉を選び、記号で答えなさい。<div class="fig">問5の「インターネット」とＡとの共通点は〔❶〕である。一方で相違点は〔❷〕である。</div>' + "".join(f'<div class="opt">{KANA[j]}　{o}</div>' for j, o in enumerate(opts)) + f'❶{box()}　❷{box()}</div>')
    M.letters += ["ウ", "エ"]
    M.k("6 問6❶", "ウ", 1, "思", "どちらも外国語を学び、文化を知る手段。", "ドリル10 2(2)")
    M.k("6 問6❷", "エ", 1, "思", "現地でしか出あえない「貴重な体験」は海外留学にしかない。", "ドリル10 2(2)")
    M.add('<div class="item">問7　次のア〜エについて、［Ｂ］の文章の内容に合うものには○、合わないものには×を書きなさい。'
          '<div class="opt">ア　インターネットを使っても、外国に住む人から外国語を学ぶことはできない。</div>'
          '<div class="opt">イ　海外留学をする目的は、人によってさまざまである。</div>'
          '<div class="opt">ウ　その国の文化は、インターネットで調べれば十分に体験できる。</div>'
          '<div class="opt">エ　現地でしか出あえない瞬間は、貴重な体験となる。</div>'
          + "　".join(f"{k}{box()}" for k in "アイウエ") + "</div>")
    for k, v, ex in [("ア", "×", "リアルタイムで学ぶことができると書かれている。"), ("イ", "○", "「その目的もさまざまである」"), ("ウ", "×", "検索して出てくるものではない、と書かれている。"), ("エ", "○", "「それらは貴重な体験となるだろう」")]:
        M.k(f"6 問7{k}", v, 1, "思", ex, "ドリル10 2（本文）")
    mc_item(M, "6 問8", "問8　［Ｂ］の文章中の――線部「それら」が指す内容として最も適当なものを選び、記号で答えなさい。",
            "海外へ行き、現地の言葉でコミュニケーションをとったり文化を感じたりする、その場所でしか出あえない瞬間",
            ["インターネットで検索して出てくる、世界のあらゆる情報", "実際に外国に住む人からリアルタイムで学ぶ外国語", "長期休暇を利用して海外留学をする大学生の目的"], 2, "ドリル10 2（最終段落）", "直前の三文の内容を指す。")


def sec6_2(M):
    M.add('<div class="q">［Ａ］次の文章を読んで、後の問いに答えなさい。</div>' + passage(["(a)<u>明日の天気予報は雨だ</u>。〔　　　〕、(b)<u>マラソン大会は中止だろう</u>。"]))
    M.add(f'<div class="item">問1　下線部(a)・(b)を、主張と具体例に分け、記号で答えなさい。（完答）　主張{box()}　具体例{box()}</div>')
    M.k("6 問1", "主張(b)　具体例(a)", 2, "思", "「〜だろう」は筆者の考え（主張）、「天気予報は雨だ」は事実。", "ドリル13 1(1)")
    mc_item(M, "6 問2", "問2　文章中の〔　〕に入る言葉を選び、記号で答えなさい。", "だから", ["たとえば", "なぜなら", "または"], 1, "ドリル13 1(2)")
    mc_item(M, "6 問3", "問3　文章中の〔　〕に「けれども」が入るのは、どのような状況のときか。最も適当なものを選び、記号で答えなさい。",
            "明日のマラソン大会は、雨でも決行する予定だった。", ["明日のマラソン大会は、雨の場合には中止する予定だった。", "明日は晴れているときだけ、マラソン大会を開催する予定だった。"], 2, "ドリル13 1(3)", "雨でも決行なのに中止になる、という逆接の関係になる。")
    M.add('<div class="q">［Ｂ］次の文章を読んで、後の問いに答えなさい。</div>' + passage(S6.D13_2))
    M.add(f'<div class="item">問4　筆者の主張が書かれている文はどれか。(a)〜(d)の記号で答えなさい。　{box()}</div>')
    M.k("6 問4", "(d)", 2, "思", "「〜が求められているのである」と筆者の考えを述べている。", "ドリル13 2(1)")
    mc_item(M, "6 問5", "問5　(c)の文の「しかし」と同じ働きをする言葉を選び、記号で答えなさい。", "けれども", ["だから", "たとえば", "つまり"], 2, "ドリル13 POINT", "逆接。")
    mc_item(M, "6 問6", "問6　筆者の考えに合うものとして最も適当なものを選び、記号で答えなさい。",
            "あふれる情報の中から、必要な情報を主体的に判断し、選択し、活用する力が必要だ。",
            ["インターネットの情報はすべて正しいので、積極的に活用すべきだ。", "テレビや本よりも、インターネットの情報のほうが信頼できる。", "うその情報が掲載されているので、インターネットは使わないほうがよい。"], 2, "ドリル13 2")
    M.add('<div class="q">［Ｃ］次の文章(1)〜(3)には、主張と理由が示されている。その理由を支える具体例として適切なものを選び、記号で答えなさい。</div>')
    for i, (t, c, ws, src) in enumerate(S6.D14_1, 1):
        opts, L = M.choice(c, ws, 3)
        lines = "".join(f'<div class="opt">{KANA[j]}　{o}</div>' for j, o in enumerate(opts))
        M.add(f'<div class="item">問7({i})　{t}　{box()}{lines}</div>')
        M.k(f"6 問7({i})", L, 2, "思", f"正解：{c}", src)
    s1 = "女性専用車両を廃止することには反対だ"
    M.add(f'<div class="item">問8　［Ｃ］(1)の文章で、筆者の主張が書かれている部分を、文中から{kn(len(s1))}字で抜き出しなさい。{box(len(s1)*1.05+1)}</div>')
    M.k("6 問8", s1, 2, "思", f"{kn(len(s1))}字。「なぜなら」の前が主張。", "ドリル14 1(1)・POINT")
    M.add('<div class="item">問9　次のア〜ウの文を、「主張→なぜなら＋理由→たとえば＋具体例」の順になるように並べ替え、記号で答えなさい。（完答）'
          '<div class="opt">ア　たとえば、去年の夏休みも宿題が終わらず、最後の日に徹夜で取り組んだ。</div>'
          '<div class="opt">イ　なぜなら、宿題が終わらないと夏休みの最後の日に困ることになるからだ。</div>'
          '<div class="opt">ウ　夏休みの宿題は計画的に進めるべきだ。</div>'
          f'{box()}→{box()}→{box()}</div>')
    M.k("6 問9", "ウ→イ→ア", 3, "思", "主張（〜べきだ）→理由（なぜなら〜からだ）→具体例（たとえば）。", "ドリル14 POINT")


def fig14():
    return ('<div class="fig tree"><table><tr><td colspan="2" class="top">〔❶〕</td><td class="gap"></td><td colspan="2" class="top">〔❸〕</td></tr>'
            '<tr><td>〔❷〕</td><td>彫刻家</td><td class="gap"></td><td>ペンタブレット</td><td>〔❹〕</td></tr></table></div>')


def sec6_3(M):
    M.add('<div class="q">［Ａ］次の文章を読んで、後の問いに答えなさい。</div>' + passage([S6.D14_2]))
    opts = ["情報教育", "芸術家", "パソコン", "芸術教育", "画家", "情報機器"]
    ans = {"❶": "芸術家", "❷": "画家", "❸": "情報機器", "❹": "パソコン"}
    M.add(f'<div class="item">問1　文章をもとに作成した次の図を完成させるために、空欄❶〜❹に入る言葉を選び、記号で答えなさい。（上の語が、下の語をまとめたもの）{fig14()}{opts_html(opts)}<br>' + "　".join(f"{k}{box()}" for k in ans) + "</div>")
    for k, v in ans.items():
        L = KANA[opts.index(v)]
        M.letters.append(L)
        M.k(f"6 問1{k}", f"{L}（{v}）", 1, "思", "", "ドリル14 2(1)")
    M.add('<div class="item">問2　下線部(a)〜(d)を、主張・理由・具体例に分けなさい。（主張なら「主張」、理由なら「理由」、具体例なら「具体例」と書くこと）<br>' + "　".join(f"({x}){box(4.5)}" for x in "abcd") + "</div>")
    for x, v in zip("abcd", ["具体例", "具体例", "理由", "主張"]):
        M.k(f"6 問2({x})", v, 1, "思", "「このように」で具体例をまとめたものが理由、「したがって」の後が主張。", "ドリル14 2(2)")
    mc_item(M, "6 問3", "問3　文章中の「したがって」と同じ働きをする言葉を選び、記号で答えなさい。", "だから", ["しかし", "たとえば", "または"], 2, "ドリル14 2", "順接。")
    M.add('<div class="q">［Ｂ］次の文章を読んで、後の問いに答えなさい。</div>' + passage(S6.D16))
    M.add(f'<div class="item">問4　①②の段落のうち、筆者の主張が書かれた段落と、理由が書かれた段落を、それぞれ番号で答えなさい。（完答）　主張{box()}　理由{box()}</div>')
    M.k("6 問4", "主張①　理由②", 2, "思", "①「〜を勧めたい」が主張、②「〜知ることができる」が理由。", "ドリル16 (1)")
    M.add(f'<div class="item">問5　理由を支える具体例が書かれた段落は、③④のうちどちらか。番号で答えなさい。　{box()}</div>')
    M.k("6 問5", "④", 2, "思", "④は「その周辺を見ることで…より広く深く知ることができる」と、②の理由とつながる。", "ドリル16 (2)")
    mc_item(M, "6 問6", "問6　問5で選ばれなかった段落は、どのような役割をしているか。最も適当なものを選び、記号で答えなさい。",
            "筆者の主張には直接つながらない具体例を述べている。", ["筆者の主張とはまったく関係のない別の意見を述べている。", "具体例はなく筆者の別の意見だけを述べている。"], 2, "ドリル16 (3)")
    mc_item(M, "6 問7", "問7　⑤の段落を評価した文として最も適当なものを選び、記号で答えなさい。",
            "筆者の主張に近い意見と具体例が書いてある。", ["筆者の主張を繰り返しており、それを強調している。", "筆者の主張とはまったく関係のない具体例が書いてある。"], 2, "ドリル16 (4)")
    mc_item(M, "6 問8", "問8　④の段落の「辞書からのお誘い」とは何か。最も適当なものを選び、記号で答えなさい。",
            "調べた単語の周辺に、反対の意味の語や使い方の異なる語が記されていること。",
            ["辞書の前や後に、おもしろい付録がついていること。", "辞書に書かれていることを、すべて頭に入れること。", "わからない単語の意味や用法を、すぐに調べられること。"], 2, "ドリル16 ④")
    mc_item(M, "6 問9", "問9　［Ａ］の文章の筆者の主張として最も適当なものを選び、記号で答えなさい。",
            "これからの芸術教育においては、情報教育が必要である。",
            ["若い画家は、ペンタブレットを使いこなせるようになるべきだ。", "彫刻家は、作品をインターネット上で発信してはいけない。", "芸術家は、情報機器を使わずに芸術活動をするべきだ。"], 2, "ドリル14 2(d)")


def fig15():
    return ('<div class="fig"><div class="c">〔❶〕</div><div class="row">'
            '<div class="bx">〔❷〕<br>〔❹〕 ⇔ 〔❺〕<br>（〔❼〕）</div>'
            '<div class="bx">〔❸〕<br>〔❻〕 ⇔ 死ぬことができない<br>（〔❼〕）</div></div>'
            '<div class="c">〔❼〕……〔❶〕を浮き彫りにする手段</div></div>')


def sec6_4(M):
    M.add('<div class="q">次の文章を読んで、後の問いに答えなさい。</div>' + passage(S6.D15))
    opts = ["経済成長", "パラドックス", "環境問題", "長生きできる", "現代社会の問題", "環境汚染", "医療問題"]
    ans = {"❶": "現代社会の問題", "❷": "環境問題", "❸": "医療問題", "❹": "経済成長", "❺": "環境汚染", "❻": "長生きできる", "❼": "パラドックス"}
    M.add(f'<div class="item">問1　次の図は文章を図式化したものである。空欄❶〜❼に入る言葉を選び、記号で答えなさい。{fig15()}{opts_html(opts)}<br>' + "　".join(f"{k}{box()}" for k in ans) + "</div>")
    for k, v in ans.items():
        L = KANA[opts.index(v)]
        M.letters.append(L)
        M.k(f"6 問1{k}", f"{L}（{v}）", 1, "思", "", "ドリル15 (2)")
    copts = ["このように", "しかし", "したがって", "たとえば"]
    M.add(f'<div class="item">問2　文章中の空欄ａ〜ｃに入る言葉を選び、記号で答えなさい。（選択肢は一回ずつしか使えない）<br>{opts_html(copts)}<br>ａ{box()}　ｂ{box()}　ｃ{box()}</div>')
    for k, v in zip("ａｂｃ", ["たとえば", "このように", "したがって"]):
        L = KANA[copts.index(v)]
        M.letters.append(L)
        M.k(f"6 問2{k}", f"{L}（{v}）", 1, "思", "ａは具体例の始まり、ｂは具体例のまとめ、ｃは結論（主張）を導く。", "ドリル15 (3)")
    pdx = "一般に正しいと考えられていることに反する主張や事態"
    M.add(f'<div class="item">問3　「パラドックス」とはどのようなことか。文章中から{kn(len(pdx))}字で抜き出しなさい。<br>{box(len(pdx)*1.0+1)}</div>')
    M.k("6 問3", pdx, 2, "思", f"①段落。{kn(len(pdx))}字。", "ドリル15 ①")
    mc_item(M, "6 問4", "問4　「貧しき者は幸いである」「急がば回れ」は、文章中で何として挙げられているか。最も適当なものを選び、記号で答えなさい。",
            "パラドックスの例", ["環境問題の例", "医療問題の例", "現代社会の問題の特徴"], 2, "ドリル15 ①")
    M.add(f'<div class="item">問5　③段落で、医療技術が発達したことで生まれた事態を、文中から九字で抜き出しなさい。（かぎかっこは含めない）　{box(10)}</div>')
    M.k("6 問5", "死ぬことができない", 2, "思", "「長生きできる」と反対のことが同時に起きている。", "ドリル15 ③")
    M.add('<div class="item">問6　次のア〜エについて、文章の内容に合うものには○、合わないものには×を書きなさい。'
          '<div class="opt">ア　日本は工業化に成功し、経済大国へと成長した。</div>'
          '<div class="opt">イ　環境汚染は、工業化が失敗したことによって生じた。</div>'
          '<div class="opt">ウ　現代社会の問題は、反対のことが同時に起きているという特徴をもつ。</div>'
          '<div class="opt">エ　パラドックスの視点で見ると、社会の問題点はわかりにくくなる。</div>'
          + "　".join(f"{k}{box()}" for k in "アイウエ") + "</div>")
    for k, v, ex in [("ア", "○", "②段落。"), ("イ", "×", "工業化は「みごとに成功」した一方で生じた。"), ("ウ", "○", "④段落。"), ("エ", "×", "問題点を「浮き彫りにする」と述べている。")]:
        M.k(f"6 問6{k}", v, 1, "思", ex, "ドリル15")
    mc_item(M, "6 問7", "問7　④段落で、筆者は現代社会の問題の特徴を何だと述べているか。最も適当なものを選び、記号で答えなさい。",
            "反対のことが同時に起きていること", ["工業化と経済成長が進んだこと", "医療技術が高度に発達したこと", "問題の数が少なくなったこと"], 2, "ドリル15 ④")


def sec6_5(M):
    M.add('<div class="q">［Ａ］次の文章を読んで、後の問いに答えなさい。</div>' + passage(["(a)<u>明日の天気予報は雨だ</u>。〔　　　〕、(b)<u>マラソン大会は中止だろう</u>。"]))
    M.add(f'<div class="item">問1　(1)下線部(a)・(b)を主張と具体例に分けなさい。（完答）　主張{box()}　具体例{box()}<br>(2)〔　〕に入る言葉を次から選び、記号で答えなさい。<br>' + opts_html(["なぜなら", "たとえば", "または", "だから"]) + f"　{box()}</div>")
    M.letters.append("エ")
    M.k("6 問1(1)", "主張(b)　具体例(a)", 2, "思", "", "ドリル13 1(1)")
    M.k("6 問1(2)", "エ（だから）", 1, "思", "具体例（事実）→だから→主張。", "ドリル13 1(2)")
    t, c, ws, src = S6.D14_1[2]
    opts, L = M.choice(c, ws, 3)
    lines = "".join(f'<div class="opt">{KANA[j]}　{o}</div>' for j, o in enumerate(opts))
    M.add(f'<div class="q">［Ｂ］次の文章の理由を支える具体例として適切なものを選び、記号で答えなさい。</div><div class="item">問2　{t}　{box()}{lines}</div>')
    M.k("6 問2", L, 2, "思", f"正解：{c}", src)
    M.add('<div class="q">［Ｃ］次の文章を読んで、後の問いに答えなさい。</div>' + passage(S6.D16))
    roles = ["主張", "理由", "具体例", "主張に直接つながらない具体例", "主張に近い意見と具体例"]
    M.add(f'<div class="item">問3　①〜⑤の段落の役割として適切なものを選び、記号で答えなさい。（同じ記号を二度使ってもよい）<br>{opts_html(roles)}<br>' + "　".join(f"{MARU[j]}{box()}" for j in range(5)) + "</div>")
    for j, v in enumerate(["主張", "理由", "主張に直接つながらない具体例", "具体例", "主張に近い意見と具体例"]):
        L = KANA[roles.index(v)]
        M.letters.append(L)
    # 8点：①②完答2点、③④⑤各2点
    M.k("6 問3①②", "①ア　②イ（完答）", 2, "思", "①「〜を勧めたい」が主張、②がその理由。", "ドリル16 (1)")
    M.k("6 問3③", "エ", 2, "思", "単語の意味や用法を調べるだけでは「もったいない」という例で、主張に直接はつながらない。", "ドリル16 (3)")
    M.k("6 問3④", "ウ", 2, "思", "「その周辺を見ることで…より広く深く知ることができる」と②の理由を支える。", "ドリル16 (2)")
    M.k("6 問3⑤", "オ", 2, "思", "辞書を本として読むという、主張に近い意見と付録の例。", "ドリル16 (4)")
    M.add('<div class="q">［Ｄ］次の文章を読んで、後の問いに答えなさい。</div>' + passage(S6.D10_1))
    kt = "バッテリーが切れたらそこで読書が終わってしまうこと"
    M.add(f'<div class="item">問4　(1)筆者が挙げている電子書籍の欠点を、文中から{kn(len(kt))}字で抜き出しなさい。<br>{box(len(kt)*1.0+1)}<br>(2)目的に合った使い方をすると、どうなると筆者は述べているか。文中から九字で抜き出しなさい。{box(10)}</div>')
    M.k("6 問4(1)", kt, 2, "思", f"{kn(len(kt))}字。", "ドリル10 1（本文）")
    M.k("6 問4(2)", "双方の利点を生かす", 2, "思", "「目的に合った使い方をすれば、双方の利点を生かすことができるのだ」。", "ドリル10 1（最終段落）")
    M.add('<div class="q">［Ｅ］次の文章を読んで、後の問いに答えなさい。</div>' + passage(S6.D13_2))
    M.add(f'<div class="item">問5　筆者の主張が書かれている文はどれか。(a)〜(d)の記号で答えなさい。　{box()}</div>')
    M.k("6 問5", "(d)", 2, "思", "「〜が求められているのである」と筆者の考えを述べている。", "ドリル13 2(1)")


SEC6 = {1: sec6_1, 2: sec6_2, 3: sec6_3, 4: sec6_4, 5: sec6_5}

CSS = """
@page { size: A4; }
body { font-family: "IPAGothic", sans-serif; font-size: 10.5pt; line-height: 1.75; color:#111; }
.cover { border: 2px solid #222; padding: 6px 10px; margin-bottom: 6px; }
.cover h1 { font-size: 17pt; margin: 0; text-align:center; letter-spacing: .1em; }
.cover .sub { text-align:center; font-size: 10pt; }
table.info { border-collapse: collapse; width:100%; margin-top:6px; }
table.info td, table.info th { border:1px solid #222; padding:3px 6px; text-align:center; font-size:10pt; }
.notes { border:1px solid #555; padding: 4px 10px; font-size: 9.5pt; margin: 6px 0 10px; }
.sec { margin: 14px 0 4px; border-bottom: 2px solid #222; padding-bottom: 2px; page-break-after: avoid; }
.secno { display:inline-block; background:#222; color:#fff; width: 1.6em; text-align:center; margin-right:6px; font-weight:bold; }
.sectxt { font-weight: bold; }
.tag { white-space: nowrap; font-size: 8.5pt; border:1px solid #444; border-radius: 3px; padding: 0 4px; margin-left: 6px; }
.secpt { float:right; font-weight:bold; white-space: nowrap; }
.mk { display:inline-block; border:1px solid #222; font-size:8pt; line-height:1.2; padding:0 2px; margin:0 2px; vertical-align: super; }
.q { margin: 8px 0 3px; font-weight: bold; page-break-after: avoid; }
.item { margin: 3px 0 7px 1.2em; page-break-inside: avoid; }
.no { margin-right: .4em; }
.ab { display:inline-block; border:1.3px solid #222; vertical-align: middle; margin: 2px 3px; background:#fff; }
.wb { border:1.3px solid #222; height: 2.2em; margin: 4px 0; }
.opts { display:inline-block; margin-left: .5em; }
.opt { margin-left: 1.2em; }
.grid3 { display:grid; grid-template-columns: 1fr 1fr 1fr; gap: 2px 12px; }
.grid2 { display:grid; grid-template-columns: 1fr 1fr; gap: 2px 12px; margin-left:1.2em; }
.kq { page-break-inside: avoid; margin-bottom: 4px; }
.passage { border:1px solid #444; padding: 6px 10px; margin: 4px 0 6px; line-height: 1.9; page-break-inside: avoid; }
.passage p { margin: 0; text-indent: 1em; }
.fig { border:1px dashed #444; padding:6px 10px; margin:6px 0; text-align:center; page-break-inside: avoid; }
.fig .row { display:flex; gap: 14px; justify-content:center; margin: 6px 0; }
.fig .bx { border:1px solid #444; padding:4px 12px; }
.fig.tree table { margin: 0 auto; border-collapse: collapse; }
.fig.tree td { border:1px solid #444; padding:3px 14px; }
.fig.tree td.top { border-bottom: 2px solid #444; }
.fig.tree td.gap { border:none; width: 30px; }
table.dt { border-collapse: collapse; margin: 6px auto; font-size: 9.5pt; }
table.dt td, table.dt th { border:1px solid #444; padding:3px 8px; text-align:center; }
.keyh { page-break-before: always; font-size: 15pt; border-bottom: 3px double #222; margin-bottom: 6px; }
table.key { border-collapse: collapse; width:100%; font-size: 9pt; }
table.key { table-layout: fixed; }
table.key th, table.key td { border:1px solid #666; padding: 2px 5px; vertical-align: top; }
table.key th { background:#eee; }
table.key td.c { text-align:center; white-space: nowrap; }
.end { text-align:center; margin-top: 10px; }
"""


def build(m):
    M = Mock(m)
    title = f"【国語表現】模擬問題{MARU[m-1]}"
    M.add(f'''<div class="cover"><h1>{title}</h1>
<div class="sub">3年　国語表現（ビジネス）　2学期期末テスト対策（授業内テスト 11月26日 想定）　45分・100点</div>
<table class="info"><tr><th>組</th><td style="width:12%"></td><th>番</th><td style="width:12%"></td><th>氏名</th><td style="width:40%"></td></tr></table>
<table class="info"><tr><th>観点</th><th>知識・技能</th><th>思考・判断・表現</th><th>合計</th></tr>
<tr><th>得点</th><td>　　　／{54 if m != 5 else 57}</td><td>　　　／{46 if m != 5 else 43}</td><td>　　　／100</td></tr></table></div>
<div class="notes">【注意事項】<br>1　解答は、すべてこの問題用紙の解答欄（□）に書き込むこと。<br>2　指示のない限り、できるだけ漢字で書くこと。<br>3　字数制限のある問題は、句読点や記号も一字と数える。<br>4　記号で答える問題は、記号をはっきり書くこと。（完答）とある問題は、すべて合って得点とする。</div>''')
    sec1(M); sec2(M); sec3(M); sec4(M); sec5(M)
    s6pts = 22 if m != 5 else 19
    M.add(sec_head(6, "次の文章を読んで、後の問いに答えなさい。", s6pts, "思"))
    SEC6[m](M)
    M.add('<div class="end">― 以上 ―</div>')
    # 解答
    rows = "".join(f'<tr><td class="c">{H.escape(l)}</td><td>{a}</td><td class="c">{p}</td><td class="c">{"知" if k=="知" else "思"}</td><td>{e}</td><td>{s}</td></tr>' for l, a, p, k, e, s in M.key)
    tot = sum(r[2] for r in M.key)
    chi = sum(r[2] for r in M.key if r[3] == "知")
    M.add(f'<div class="keyh">{title}　解答・解説</div><div>配点合計 {tot}点（知識・技能 {chi}点／思考・判断・表現 {tot-chi}点）</div>'
          f'<table class="key"><colgroup><col style="width:10%"><col style="width:24%"><col style="width:4%"><col style="width:5%"><col style="width:35%"><col style="width:22%"></colgroup><tr><th>問</th><th>正解</th><th>点</th><th>観点</th><th>解説</th><th>出どころ</th></tr>{rows}</table>')
    doc = f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>{title}</title><style>{CSS}</style></head><body>{"".join(M.parts)}</body></html>'
    return M, doc, tot, chi


if __name__ == "__main__":
    out = {}
    for m in range(1, 6):
        M, doc, tot, chi = build(m)
        open(f"mogi{m}.html", "w").write(doc)
        from collections import Counter
        out[m] = dict(total=tot, chi=chi, letters=dict(Counter(M.letters)))
        json.dump([list(x) for x in M.leak], open(f"leak{m}.json", "w"), ensure_ascii=False)
        json.dump([list(x) for x in M.key], open(f"key{m}.json", "w"), ensure_ascii=False)
    print(json.dumps(out, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- 縦書き・横向き版
import re as _re

VCSS = CSS.replace("@page { size: A4; }", "@page { size: A4 landscape; }") + """
html { writing-mode: vertical-rl; }
body { font-size: 10.5pt; line-height: 1.8; }
.ab { width:auto; height:auto; }
.wb { width:auto; height:auto; inline-size: 100%; block-size: 2.4em; margin: 0 4px; }
.item { margin: 0 6px 0 0; margin-inline-start: 1.2em; margin-block-end: 6px; }
.opts { margin-left: 0; margin-inline-start: .5em; }
.opt { margin-left: 0; margin-inline-start: 1.2em; }
.grid2 { margin-left: 0; margin-inline-start: 1.2em; }
.secpt { float: none; margin-inline-start: 1em; }
.sec { border-bottom: none; border-left: 2px solid #222; padding: 0 0 0 2px; margin: 0 0 0 4px; margin-block-start: 14px; }
.secno { width: auto; block-size: 1.6em; inline-size: auto; }
u { text-underline-position: right; }
.tcy { text-combine-upright: all; }
.cover table.info td[style] { width:auto !important; }
.cover table.info td { min-inline-size: 5em; block-size: 2.4em; }
table.info td, table.info th { padding: 6px 3px; }
table.dt td, table.dt th { padding: 8px 3px; }
.fig.tree td { padding: 14px 3px; }
.fig .row { flex-direction: row; }
.end { margin: 0 10px; }
"""


def _tcy(html):
    def fix_text(t):
        return _re.sub(r"\(?[0-9A-Za-z]{1,3}\)?", lambda mo: f'<span class="tcy">{mo.group(0)}</span>' if len(mo.group(0)) <= 4 else mo.group(0), t)
    parts = _re.split(r"(<[^>]+>)", html)
    return "".join(p if p.startswith("<") else fix_text(p) for p in parts)


def _vbox(html):
    # 解答欄：width/height を inline/block サイズに置き換える（縦書きで縦長の枠になる）
    return _re.sub(r'class="ab" style="width:([\d.]+)em;height:([\d.]+)em"',
                   lambda mo: f'class="ab" style="inline-size:{mo.group(1)}em;block-size:{mo.group(2)}em"', html)


def build_vertical(m):
    M, doc, tot, chi = build(m)
    body = doc.split("<body>")[1].split("</body>")[0]
    prob, key = body.split('<div class="keyh">')
    title = f"【国語表現】模擬問題{MARU[m-1]}"
    q = f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>{title}</title><style>{VCSS}</style></head><body>{_tcy(_vbox(prob))}</body></html>'
    KCSS = CSS.replace("@page { size: A4; }", "@page { size: A4 landscape; }").replace(".keyh { page-break-before: always;", ".keyh {")
    k = f'<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8"><title>{title} 解答</title><style>{KCSS}</style></head><body><div class="keyh">{key}</body></html>'
    return q, k


if __name__ == "__main__":
    for m in range(1, 6):
        q, k = build_vertical(m)
        open(f"v{m}_q.html", "w").write(q)
        open(f"v{m}_k.html", "w").write(k)
