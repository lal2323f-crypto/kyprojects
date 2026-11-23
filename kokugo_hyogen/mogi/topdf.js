const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  const names = ['①', '②', '③', '④', '⑤', '⑥'];
  const opt = {
    format: 'A4', landscape: true, printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="font-size:8px;width:100%;text-align:center"><span class="pageNumber"></span></div>',
    margin: { top: '12mm', bottom: '12mm', left: '12mm', right: '12mm' }
  };
  for (let m = 1; m <= 6; m++) {
    await p.goto('file://' + process.cwd() + `/v${m}_q.html`);
    await p.pdf({ ...opt, path: `_q${m}.pdf` });
    await p.goto('file://' + process.cwd() + `/v${m}_k.html`);
    await p.pdf({ ...opt, path: `_k${m}.pdf` });
    execFileSync('pdfunite', [`_q${m}.pdf`, `_k${m}.pdf`, `【国語表現】模擬問題${names[m - 1]}.pdf`]);
  }
  await b.close();
})();
