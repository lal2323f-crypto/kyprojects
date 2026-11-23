// 問題用紙・解答用紙・解答解説 をそれぞれPDFにする
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1123, height: 794 } });
  const names = ['①', '②', '③', '④', '⑤', '⑥'];
  const foot = {
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center"><span class="pageNumber"></span></div>',
  };
  const opt = { format: 'A4', landscape: true, printBackground: true, margin: { top: '12mm', bottom: '12mm', left: '12mm', right: '12mm' } };
  const report = [];
  for (let m = 1; m <= 6; m++) {
    const n = names[m - 1];
    await p.goto('file://' + process.cwd() + `/e${m}_q.html`);
    await p.evaluate(() => document.fonts.ready);
    await p.pdf({ ...opt, ...foot, path: `out/【国語表現】模擬問題${n}_問題.pdf` });
    // 解答用紙：1ページに収まるよう縮小
    await p.goto('file://' + process.cwd() + `/e${m}_a.html`);
    await p.evaluate(() => document.fonts.ready);
    const sc = await p.evaluate(() => {
      const w = document.getElementById('wrap');
      let l = Infinity, r = -Infinity, t = Infinity, bt = -Infinity;
      for (const e of w.querySelectorAll('*')) {
        const x = e.getBoundingClientRect();
        if (!x.width) continue;
        l = Math.min(l, x.left); r = Math.max(r, x.right); t = Math.min(t, x.top); bt = Math.max(bt, x.bottom);
      }
      const W = r - l, Hh = bt - t;
      const availW = 1123 - 2 * 38, availH = 794 - 38 - 90;
      const s = Math.min(1, availW / W, availH / Hh);
      w.style.transform = `scale(${s})`;
      // 縮小後もはみ出していないか確認
      let l2 = Infinity;
      for (const e of w.querySelectorAll('*')) { const x = e.getBoundingClientRect(); if (x.width) l2 = Math.min(l2, x.left); }
      return [Math.round(W), Math.round(Hh), s, Math.round(l2)];
    });
    report.push(`${n} sheet ${sc.map(x => Math.round(x * 100) / 100).join(' ')}`);
    await p.pdf({ format: 'A4', landscape: true, printBackground: true, margin: { top: '0', bottom: '0', left: '0', right: '0' }, path: `out/【国語表現】模擬問題${n}_解答用紙.pdf`, pageRanges: '1' });
    await p.goto('file://' + process.cwd() + `/e${m}_k.html`);
    await p.evaluate(() => document.fonts.ready);
    await p.pdf({ ...opt, ...foot, path: `out/【国語表現】模擬問題${n}_解答解説.pdf` });
  }
  console.log(report.join('\n'));
  await b.close();
})();
