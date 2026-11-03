// 以 Playwright 檢查各頁在手機寬度是否橫向溢出。用法：node tools/audit_mobile.js [寬度,...]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const widths = (process.argv[2] || '320,375').split(',').map(Number);
function walk(d, out = []) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    if (e.name === '.git' || e.name === 'node_modules') continue;
    const p = path.join(d, e.name);
    e.isDirectory() ? walk(p, out) : p.endsWith('.html') && out.push(p);
  }
  return out;
}
(async () => {
  const b = await chromium.launch();
  let bad = 0;
  for (const w of widths) {
    const ctx = await b.newContext({ viewport: { width: w, height: 800 } });
    const pg = await ctx.newPage();
    for (const f of walk(root)) {
      await pg.goto('file://' + f, { waitUntil: 'domcontentloaded' });
      const r = await pg.evaluate(() => {
        const de = document.documentElement, over = de.scrollWidth - de.clientWidth;
        let who = '';
        if (over > 1) for (const el of document.body.querySelectorAll('*')) {
          const r = el.getBoundingClientRect();
          if (r.right > de.clientWidth + 1 && getComputedStyle(el).position !== 'fixed') { who = el.tagName + '.' + el.className; break; }
        }
        return { over, who };
      });
      if (r.over > 1) { bad++; console.log(`${w}px  +${r.over}  ${path.relative(root, f)}  ${r.who}`); }
    }
    await ctx.close();
  }
  await b.close();
  console.log('橫向溢出頁面數：' + bad);
})();
