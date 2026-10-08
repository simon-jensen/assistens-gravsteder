// Headless røgtest af siden: prikker, søgning, links, GPS-visning, mørk tilstand og rettetilstanden.
// Kræver Playwright med Chromium. Kør fra repo-roden:
//   node tests/side.test.mjs                 # starter selv en lokal server på en ledig port
//   UD=/tmp/skaerm node tests/side.test.mjs  # skriver også skærmbilleder (telefon, lys/mørk) til mappen
import { createRequire } from 'module';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import net from 'net';
const require = createRequire(import.meta.url);
let pw; try { pw = require('playwright'); } catch (e) { pw = createRequire('/opt/node-tools/node_modules/')('playwright'); }
const { chromium } = pw;
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const UD = process.env.UD ? path.resolve(process.env.UD) : null;
if (UD) fs.mkdirSync(UD, { recursive: true });

let fejl = 0;
const ok = (c, m) => { console.log((c ? '✓ ' : '✗ ') + m); if (!c) fejl++; };
const port = await new Promise(r => { const s = net.createServer(); s.listen(0, () => { const p = s.address().port; s.close(() => r(p)); }); });
const srv = spawn('python3', ['-m', 'http.server', String(port), '--bind', '127.0.0.1'], { cwd: ROOT, stdio: 'ignore' });
await new Promise(r => setTimeout(r, 800));
const URL0 = `http://127.0.0.1:${port}/`;
const browser = await chromium.launch();
try {
  // Telefon, lys tilstand
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true,
    locale: 'da-DK', geolocation: { latitude: 55.6903, longitude: 12.5505 }, permissions: ['geolocation'], serviceWorkers: 'block' });
  const page = await ctx.newPage();
  const errs = []; page.on('pageerror', e => errs.push(e.message)); page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto(URL0 + '#g=P1');
  await page.waitForSelector('.dot');
  ok(await page.locator('.dot').count() === 133, '133 prikker på kortet');
  ok(await page.locator('.row').count() === 133, '133 rækker i listen');
  ok(await page.locator('#card.open').count() === 1 && (await page.locator('#cName').innerText()).includes('H. C. Andersen'), '#g=P1 vælger H. C. Andersen');
  ok(await page.locator('.dot.sel').count() === 1, 'den valgte prik er fremhævet');
  if (UD) await page.screenshot({ path: path.join(UD, 'telefon_lys.png'), fullPage: false });
  await page.fill('#q', 'bohr'); await page.waitForTimeout(250);
  ok(await page.locator('.row').count() === 3, 'søgning "bohr" giver 3 rækker');
  ok((await page.locator('#count').textContent()).startsWith('3 af 133'), 'tælleren viser 3 af 133'); // textContent: panel-title har text-transform
  ok(await page.locator('.dot:not(.dim)').count() === 3 + 1 || await page.locator('.dot:not(.dim)').count() === 3, 'andre prikker dæmpes ved søgning');
  await page.fill('#q', ''); await page.waitForTimeout(250);
  await page.selectOption('#afd', 'R');
  ok(await page.locator('.row').count() === 6, 'afdeling R har 6 gravsteder');
  await page.selectOption('#afd', '');
  await page.click('.kat[data-k="komp"]');
  ok(await page.locator('.row').count() === 12, 'kategorien komponister/musikere har 12');
  ok((await page.evaluate(() => location.hash)).includes('kat=komp'), 'kategori i linket');
  await page.click('.kat[data-k="komp"]');
  // Tryk på en prik → kortet viser navnet
  await page.locator('.dot[data-id="U1"]').scrollIntoViewIfNeeded(); // Playwright ruller selv hen til elementet før et klik; mål først derefter
  const y0 = await page.evaluate(() => scrollY);
  await page.locator('.dot[data-id="U1"]').click({ force: true }); // U1 ligger frit; i afd. A overlapper trykfladerne (brug Forstør)
  ok((await page.locator('#cName').innerText()).includes('John Christensen'), 'tryk på prik U1 viser John Christensen');
  ok((await page.evaluate(() => location.hash)).includes('g=U1'), 'linket følger valget');
  ok(await page.evaluate(() => scrollY) === y0, 'siden ruller ikke væk fra kortet ved tryk på en prik (telefon)');
  // GPS
  await page.click('#hereBtn'); await page.waitForTimeout(600);
  ok(await page.locator('#youdot:not([hidden])').count() === 1, '"Hvor er jeg?" viser den blå prik');
  const t = await page.locator('#toast').innerText();
  ok(t.includes('Nærmest dig'), 'toast nævner nærmeste gravsted: ' + t);
  ok(await page.locator('#nearBtn:not([hidden])').count() === 1, 'knappen Nærmeste først vises');
  await page.click('#nearBtn'); await page.waitForTimeout(100);
  const first = await page.locator('.row .yr b').first().innerText();
  ok(/^\d+ m$/.test(first), 'listen viser afstand i meter: ' + first);
  ok(await page.locator('.afdhead').count() === 0, 'ingen afdelingsoverskrifter, når der sorteres efter afstand');
  await page.click('#nearBtn'); await page.click('#hereBtn');
  ok(await page.locator('#youdot[hidden]').count() === 1, 'GPS slukkes igen');
  // Zoom: knappen, to-finger-knib (syntetiske touch-events) og dobbelttryk; prikkerne beholder skærmstørrelsen
  await page.locator('#mapwrap').scrollIntoViewIfNeeded();
  const kOf = async () => parseFloat(((await page.locator('#mapinner').evaluate(el => el.style.transform)).match(/scale\(([\d.]+)/) || [])[1] || '1'); // browseren normaliserer "scale(1.0000)" til "scale(1)"
  const dotW0 = (await page.locator('.dot[data-id="U1"]').boundingBox()).width;
  await page.click('#zoomBtn'); await page.waitForTimeout(350);
  ok(Math.abs(await kOf() - 2.5) < 0.01, 'Forstør giver 2,5×');
  ok(await page.evaluate(() => document.getElementById('mapwrap').classList.contains('zoom')), 'zoom-tilstand sat');
  const dotW1 = (await page.locator('.dot[data-id="U1"]').boundingBox()).width;
  ok(Math.abs(dotW1 - dotW0) < 1.5, 'prikken beholder sin skærmstørrelse ved zoom (' + dotW0.toFixed(1) + ' → ' + dotW1.toFixed(1) + ' px)');
  await page.click('#zoomBtn'); await page.waitForTimeout(350);
  ok(Math.abs(await kOf() - 1) < 0.01, 'Forstør igen går tilbage til 1×');
  await page.evaluate(() => { const m = document.getElementById('mapwrap'), r = m.getBoundingClientRect();
    const mk = (id, x, y) => new Touch({ identifier: id, target: m, clientX: x, clientY: y, pageX: x, pageY: y });
    const ev = (type, ts, ch) => new TouchEvent(type, { touches: ts, changedTouches: ch || ts, targetTouches: ts, bubbles: true, cancelable: true });
    const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    m.dispatchEvent(ev('touchstart', [mk(1, cx - 20, cy), mk(2, cx + 20, cy)]));
    m.dispatchEvent(ev('touchmove', [mk(1, cx - 60, cy), mk(2, cx + 60, cy)]));
    m.dispatchEvent(ev('touchend', [], [mk(1, cx - 60, cy), mk(2, cx + 60, cy)])); });
  await page.waitForTimeout(100);
  ok(Math.abs(await kOf() - 3) < 0.01, 'to-finger-knib 40 → 120 px giver 3×');
  await page.evaluate(() => { const m = document.getElementById('mapwrap'), r = m.getBoundingClientRect();
    const mk = (id, x, y) => new Touch({ identifier: id, target: m, clientX: x, clientY: y, pageX: x, pageY: y });
    const ev = (type, ts, ch) => new TouchEvent(type, { touches: ts, changedTouches: ch || ts, targetTouches: ts, bubbles: true, cancelable: true });
    const cx = r.left + 40, cy = r.top + 40;
    for (let i = 0; i < 2; i++) { m.dispatchEvent(ev('touchstart', [mk(9, cx, cy)])); m.dispatchEvent(ev('touchend', [], [mk(9, cx, cy)])); } });
  await page.waitForTimeout(350);
  ok(Math.abs(await kOf() - 5) < 0.01, 'dobbelttryk ved 3× giver 5×');
  if (UD) await page.screenshot({ path: path.join(UD, 'telefon_zoom.png') });
  await page.evaluate(() => document.getElementById('zoomBtn').click()); await page.waitForTimeout(350);
  ok(await page.locator('#card.open').count() === 1, 'kortet med det valgte gravsted er stadig åbent');
  // Rute: fra positionen (inde, ved afd. J) til H. C. Andersen (P1); udefra (Nørrebrogade) gennem en låge
  await page.goto(URL0 + '#g=P1'); await page.waitForSelector('.dot'); // nulstiller zoom og GPS
  await page.click('#cRute'); await page.waitForTimeout(1500);
  const rt = await page.locator('#rutetekst').textContent();
  ok(/\d+ m · ca\. \d+ min/.test(rt), 'ruten viser afstand og gangtid: ' + rt);
  const rm = +((rt.match(/(\d+) m/) || [])[1] || 0);
  ok(rm > 100 && rm < 900, 'afstanden fra J til P er plausibel (' + rm + ' m)');
  const npts = await page.locator('#rutelinje').evaluate(el => el.getAttribute('points').trim().split(/\s+/).length);
  ok(npts >= 5, 'rutelinjen følger stierne (' + npts + ' punkter)');
  ok((await page.locator('#rutestip').getAttribute('points')).trim().split(/\s+/).length === 2, 'den stiplede slutstrækning tegnes');
  ok((await page.locator('#cRute').textContent()).includes('Rute vises'), 'knappen på kortet viser, at ruten er aktiv');
  if (UD) await page.screenshot({ path: path.join(UD, 'telefon_rute.png') });
  await page.waitForTimeout(4200); // ruten regnes højst om hvert 4. sekund
  await ctx.setGeolocation({ latitude: 55.6918, longitude: 12.5530 }); await page.waitForTimeout(1200); // Nørrebrogade, uden for muren
  const rt2 = await page.locator('#rutetekst').textContent();
  ok(/gennem /.test(rt2), 'udefra går ruten gennem en låge: ' + rt2);
  await page.click('#ruteStop');
  ok(!(await page.evaluate(() => document.body.classList.contains('rute'))), 'Afslut rute slukker ruten');
  await ctx.setGeolocation({ latitude: 55.6903, longitude: 12.5505 }); await page.click('#hereBtn'); await page.waitForTimeout(300); // GPS fra igen
  // Rettetilstand: tryk på kortet flytter den valgte prik og gemmes lokalt
  await page.goto(URL0 + '#g=U1'); await page.waitForSelector('.dot'); // U1 valgt igen (ruteblokken valgte P1)
  await page.click('#retToggle');
  ok(await page.evaluate(() => document.body.classList.contains('ret')), 'rettetilstand tændt');
  await page.locator('#mapwrap').scrollIntoViewIfNeeded();
  const img = await page.locator('#mapimg').boundingBox();
  await page.mouse.click(img.x + img.width * 0.3, img.y + img.height * 0.3); // et tomt sted i afd. S
  const ret = await page.evaluate(() => JSON.parse(localStorage.getItem('assistens_grav_ret_v1') || '{}'));
  ok(ret.U1 && Math.abs(ret.U1.fx - 0.3) < 0.02 && Math.abs(ret.U1.fy - 0.3) < 0.02 && ret.U1.src === 'kort', 'rettelsen gemmes lokalt som src kort: ' + JSON.stringify(ret.U1));
  ok(await page.locator('.dot.flyttet').count() === 1, 'den flyttede prik markeres');
  await page.click('#retUndo');
  ok(await page.evaluate(() => Object.keys(JSON.parse(localStorage.getItem('assistens_grav_ret_v1') || '{}')).length) === 0, 'fortryd fjerner rettelsen');
  await page.click('#retToggle');
  if (UD) { await page.goto(URL0 + '#g=P1'); await page.waitForSelector('.dot'); }
  const vSw = fs.readFileSync(path.join(ROOT, 'sw.js'), 'utf8').match(/const VERSION\s*=\s*'([^']+)'/)[1];
  ok((await page.locator('#udgave').textContent()) === vSw, 'udgaven i sidefoden er sw.js VERSION (' + vSw + ')');
  ok(errs.length === 0, 'ingen JavaScript-fejl i konsollen' + (errs.length ? ': ' + errs.join(' | ') : ''));
  await ctx.close();
  // Telefon, mørk tilstand + skrivebord
  const ctx2 = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, colorScheme: 'dark', serviceWorkers: 'block' });
  const p2 = await ctx2.newPage(); await p2.goto(URL0 + '#g=E9'); await p2.waitForSelector('.dot');
  ok((await p2.locator('#mapimg').evaluate(i => i.currentSrc)).includes('kort-moerk'), 'mørk tilstand bruger det mørke kort');
  if (UD) await p2.screenshot({ path: path.join(UD, 'telefon_moerk.png') });
  await ctx2.close();
  const ctx3 = await browser.newContext({ viewport: { width: 1280, height: 900 }, serviceWorkers: 'block' });
  const p3 = await ctx3.newPage(); await p3.goto(URL0 + '#afd=A'); await p3.waitForSelector('.dot');
  ok(await p3.locator('.row').count() === 28, '#afd=A viser 28 rækker på skrivebordet');
  if (UD) await p3.screenshot({ path: path.join(UD, 'skrivebord.png') });
  await ctx3.close();
} finally {
  await browser.close(); srv.kill();
}
console.log(fejl ? `${fejl} fejl` : 'alt OK');
process.exit(fejl ? 1 : 0);
