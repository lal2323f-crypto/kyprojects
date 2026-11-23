const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  const names = ['①', '②', '③', '④', '⑤'];
  for (let m = 1; m <= 5; m++) {
    await p.goto('file://' + process.cwd() + `/mogi${m}.html`);
    await p.pdf({
      path: `【国語表現】模擬問題${names[m - 1]}.pdf`, format: 'A4', printBackground: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="font-size:8px;width:100%;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
      margin: { top: '12mm', bottom: '14mm', left: '13mm', right: '13mm' }
    });
  }
  await b.close();
})();
