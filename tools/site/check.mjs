// Browser checks for the built site, driven by tools/site_check.py.
//   NODE_PATH=$(npm root -g) node tools/site/check.mjs <config.json>
// The config names the base URL, three entry pages, the search query and the
// headword it must find first, the pages to use for the preview and the
// translator's-view checks, the screenshot directory, and the results file.
// Results are written as JSON; progress goes to stderr.  Uses the globally
// installed playwright package (CommonJS require, which honours NODE_PATH).
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const results = [];
let fatal = null;

function record(viewport, page, check, ok, detail) {
  results.push({ viewport, page, check, ok: !!ok, detail: detail ? String(detail) : '' });
  console.error(`${ok ? 'pass' : 'FAIL'}  ${viewport.padEnd(8)} ${page.padEnd(28)} ${check}${detail ? '  (' + detail + ')' : ''}`);
}

function loadPlaywright() {
  const errors = [];
  for (const name of ['playwright', 'playwright-core']) {
    try { return require(name); } catch (e) { errors.push(`${name}: ${e.message.split('\n')[0]}`); }
  }
  throw new Error('cannot require playwright (' + errors.join('; ') + '); is NODE_PATH set to `npm root -g`?');
}

async function launch(pw) {
  const opts = { headless: true, args: ['--no-sandbox'] };
  try {
    return await pw.chromium.launch(opts);
  } catch (e) {
    if (cfg.executable_path) {
      console.error('default launch failed (' + e.message.split('\n')[0] + '); retrying with ' + cfg.executable_path);
      return await pw.chromium.launch({ ...opts, executablePath: cfg.executable_path });
    }
    throw e;
  }
}

function shot(page, name) {
  const file = path.join(cfg.shots_dir, name + '.png');
  return page.screenshot({ path: file, fullPage: false }).catch(() => {});
}

async function openPage(context, viewport, rel) {
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + (e.message || e)));
  page.on('console', (m) => { if (m.type() === 'error') { errors.push('console: ' + m.text()); } });
  page.on('requestfailed', (r) => errors.push('request failed: ' + r.url()));
  await page.goto(cfg.base_url + rel, { waitUntil: 'load' });
  await page.waitForTimeout(150);
  return { page, errors };
}

async function basicChecks(context, viewport, rel, label) {
  const { page, errors } = await openPage(context, viewport, rel);
  const metrics = await page.evaluate(() => ({
    scrollWidth: document.scrollingElement.scrollWidth,
    innerWidth: window.innerWidth,
    hasViewportMeta: !!document.querySelector('meta[name="viewport"]'),
    hasDisclosure: /written by language models/.test(document.body.textContent),
    hasSearch: !!document.querySelector('form.search input'),
    hasToggle: !!document.querySelector('.translator-toggle'),
  }));
  record(viewport, rel, 'no JavaScript errors', errors.length === 0, errors.slice(0, 3).join(' | '));
  record(viewport, rel, 'no horizontal overflow', metrics.scrollWidth <= metrics.innerWidth, `scrollWidth ${metrics.scrollWidth} <= innerWidth ${metrics.innerWidth}`);
  record(viewport, rel, 'viewport meta, disclosure, search box, toggle', metrics.hasViewportMeta && metrics.hasDisclosure && metrics.hasSearch && metrics.hasToggle, JSON.stringify(metrics).slice(0, 160));
  await shot(page, `${viewport}-${label}`);
  return { page, errors };
}

async function searchCheck(context, viewport) {
  const rel = 'index.html';
  const { page, errors } = await openPage(context, viewport, rel);
  const q = cfg.search.query;
  const input = page.locator('#home-search');
  await input.click();
  await input.fill(q);
  let first = null;
  let detail = '';
  try {
    await page.locator('form.home-search .search-results li a').first().waitFor({ state: 'visible', timeout: 8000 });
    first = await page.locator('form.home-search .search-results li a').first().getAttribute('data-hw');
    detail = `"${q}" -> first result "${first}", expected "${cfg.search.expect}"`;
  } catch (e) {
    detail = `no results for "${q}": ${e.message.split('\n')[0]}`;
  }
  record(viewport, rel, 'search for an inflected form finds its headword first', first === cfg.search.expect, detail);
  await shot(page, `${viewport}-search`);
  if (first === cfg.search.expect) {
    await input.press('Enter');
    let ok = false;
    try {
      await page.waitForURL((u) => /\/w\/[^/]+\.html/.test(u.href), { timeout: 8000 });
      ok = page.url().endsWith('/w/' + cfg.search.expect_page + '.html');
    } catch (e) { /* stays false */ }
    record(viewport, rel, 'Enter opens the first result', ok, page.url());
  }
  record(viewport, rel, 'no JavaScript errors during search', errors.length === 0, errors.slice(0, 3).join(' | '));
}

async function previewCheck(context, viewport, mobile) {
  const rel = 'w/' + cfg.preview_page + '.html';
  const { page, errors } = await openPage(context, viewport, rel);
  const link = page.locator('a.w:visible').first();
  const count = await page.locator('a.w:visible').count();
  if (!count) {
    record(viewport, rel, 'a linked word opens a preview', false, 'no visible a.w link on the page');
    return;
  }
  const hw = await link.getAttribute('data-hw');
  const before = page.url();
  if (mobile) { await link.tap(); } else { await link.hover(); }
  let ok = false;
  let detail = '';
  try {
    await page.locator('.preview').waitFor({ state: 'visible', timeout: 8000 });
    await page.locator('.preview .preview-hw').first().waitFor({ state: 'visible', timeout: 8000 });
    const text = (await page.locator('.preview').innerText()).replace(/\s+/g, ' ').trim();
    ok = text.length > 0 && text.toLowerCase().includes(String(hw).toLowerCase());
    detail = `${mobile ? 'tap' : 'hover'} on "${hw}": ${text.slice(0, 90)}`;
  } catch (e) {
    detail = `${mobile ? 'tap' : 'hover'} on "${hw}": ${e.message.split('\n')[0]}`;
  }
  record(viewport, rel, `a linked word opens a preview on ${mobile ? 'tap' : 'hover'}`, ok, detail);
  await shot(page, `${viewport}-preview`);
  if (mobile) {
    record(viewport, rel, 'the first tap does not follow the link', page.url() === before, page.url());
    await link.tap();
    let followed = false;
    try {
      await page.waitForURL((u) => u.href !== before, { timeout: 8000 });
      followed = true;
    } catch (e) { /* stays false */ }
    record(viewport, rel, 'the second tap follows the link', followed, page.url());
  }
  record(viewport, rel, 'no JavaScript errors during preview', errors.length === 0, errors.slice(0, 3).join(' | '));
}

async function translatorCheck(context, viewport) {
  const rel = 'w/' + cfg.translator_page + '.html';
  const { page, errors } = await openPage(context, viewport, rel);
  const block = page.locator('.translator').first();
  const total = await page.locator('.translator').count();
  if (!total) {
    record(viewport, rel, "translator's view reveals a hidden block", false, 'no .translator block on the page');
    return;
  }
  const hiddenBefore = !(await block.isVisible());
  await openMenu(page);
  await page.locator('.translator-toggle').first().click();
  let shown = false;
  try { await block.waitFor({ state: 'visible', timeout: 5000 }); shown = true; } catch (e) { /* stays false */ }
  record(viewport, rel, "translator's view reveals a hidden .translator block", hiddenBefore && shown, `hidden before: ${hiddenBefore}, visible after: ${shown}`);
  await shot(page, `${viewport}-translator`);
  await page.reload({ waitUntil: 'load' });
  const remembered = await page.locator('.translator').first().isVisible();
  record(viewport, rel, 'the toggle state survives a reload (localStorage)', remembered, `visible after reload: ${remembered}`);
  await openMenu(page);
  await page.locator('.translator-toggle').first().click();
  const hiddenAgain = !(await page.locator('.translator').first().isVisible());
  record(viewport, rel, 'toggling again hides the block', hiddenAgain, '');
  record(viewport, rel, 'no JavaScript errors during toggle', errors.length === 0, errors.slice(0, 3).join(' | '));
}

async function openMenu(page) {
  const button = page.locator('.menu-button');
  if (await button.count() && await button.first().isVisible()) {
    if ((await button.first().getAttribute('aria-expanded')) !== 'true') { await button.first().click(); }
  }
}

async function menuCheck(context, viewport, mobile) {
  const rel = 'index.html';
  const { page, errors } = await openPage(context, viewport, rel);
  const button = page.locator('.menu-button');
  const visible = await button.isVisible();
  if (mobile) {
    const navHidden = !(await page.locator('.site-nav a[href$="browse/index.html"]').first().isVisible());
    await button.click();
    const shown = await page.locator('.site-nav a[href$="browse/index.html"]').first().isVisible();
    const toggle = await page.locator('.translator-toggle').first().isVisible();
    record(viewport, rel, 'the menu button opens the menu with the translator toggle', visible && navHidden && shown && toggle,
      `button ${visible}, hidden before ${navHidden}, shown after ${shown}, toggle ${toggle}`);
    await shot(page, `${viewport}-menu`);
  } else {
    const navShown = await page.locator('.site-nav a[href$="browse/index.html"]').first().isVisible();
    record(viewport, rel, 'the menu is shown inline on a wide screen', !visible && navShown, `button ${visible}, nav ${navShown}`);
  }
  const homeBoxes = await page.locator('form.search').count();
  record(viewport, rel, 'the home page has one search box', homeBoxes === 1, `${homeBoxes} search forms`);
  record(viewport, rel, 'no JavaScript errors with the menu', errors.length === 0, errors.slice(0, 3).join(' | '));
}

async function resultsOf(page, selector) {
  await page.locator(selector + ' .search-results li').first().waitFor({ state: 'visible', timeout: 8000 });
  return page.locator(selector + ' .search-results li a').evaluateAll((as) => as.map((a) => ({
    hw: a.getAttribute('data-hw'), href: a.getAttribute('href'), kind: a.getAttribute('data-kind') })));
}

async function phraseSearchCheck(context, viewport) {
  if (!cfg.phrase) { record(viewport, 'index.html', 'phrase search', false, 'no phrase with two words to search'); return; }
  const { page, errors } = await openPage(context, viewport, 'index.html');
  const input = page.locator('#home-search');
  await input.click();
  await input.fill(cfg.phrase.query);
  let found = false; let detail = '';
  try {
    const res = await resultsOf(page, 'form.home-search');
    found = res.some((r) => r.kind === 'phrase' && r.href.endsWith('#' + encodeURIComponent(cfg.phrase.anchor)));
    detail = `"${cfg.phrase.query}" -> ${res.slice(0, 4).map((r) => r.hw).join(', ')}`;
  } catch (e) { detail = e.message.split('\n')[0]; }
  record(viewport, 'index.html', 'a phrase is found by its words, fillers left out', found, detail);
  await shot(page, `${viewport}-phrase-search`);
  record(viewport, 'index.html', 'no JavaScript errors during phrase search', errors.length === 0, errors.slice(0, 3).join(' | '));
}

async function didYouMeanCheck(context, viewport) {
  if (!cfg.misspelling) { return; }
  const { page } = await openPage(context, viewport, 'index.html');
  const input = page.locator('#home-search');
  await input.click();
  await input.fill(cfg.misspelling.query);
  let ok = false; let detail = '';
  try {
    const res = await resultsOf(page, 'form.home-search');
    const head = await page.locator('form.home-search .search-results li.suggest').count();
    ok = head > 0 && res.some((r) => r.kind === 'suggestion' && r.hw === cfg.misspelling.expect);
    detail = `"${cfg.misspelling.query}" -> ${res.slice(0, 3).map((r) => r.hw).join(', ')}`;
  } catch (e) { detail = e.message.split('\n')[0]; }
  record(viewport, 'index.html', '"Did you mean" offers the headword for a misspelling', ok, detail);
}

async function queryParamCheck(context, viewport) {
  const q = cfg.search.query;
  const { page } = await openPage(context, viewport, 'index.html?q=' + encodeURIComponent(q));
  let ok = false; let detail = '';
  try {
    const res = await resultsOf(page, 'form.home-search');
    const value = await page.locator('#home-search').inputValue();
    ok = value === q && res.length > 0 && res[0].hw === cfg.search.expect;
    detail = `box "${value}", first "${res[0] && res[0].hw}"`;
  } catch (e) { detail = e.message.split('\n')[0]; }
  record(viewport, 'index.html?q=', '?q= fills in and runs the search', ok, detail);
}

async function notFoundCheck(context, viewport) {
  const rel = 'w/' + encodeURIComponent(cfg.search.expect_page) + 'xx.html';
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + (e.message || e)));
  const resp = await page.goto(cfg.base_url + rel, { waitUntil: 'load' });
  let ok = false; let detail = '';
  try {
    const res = await resultsOf(page, 'form.not-found-search');
    const value = await page.locator('#nf-search').inputValue();
    const styled = await page.evaluate(() => getComputedStyle(document.querySelector('.site-header')).borderBottomStyle === 'solid');
    ok = resp.status() === 404 && value.length > 0 && res.length > 0 && styled;
    detail = `status ${resp.status()}, box "${value}", ${res.length} results, styled ${styled}`;
  } catch (e) { detail = e.message.split('\n')[0]; }
  record(viewport, rel, 'the 404 page searches for the name in the address', ok && errors.length === 0, detail + (errors.length ? ' ' + errors[0] : ''));
  await shot(page, `${viewport}-404`);
}

async function senseMenuCheck(context, viewport) {
  if (!cfg.menu_page) { record(viewport, 'w/', 'sense menu', false, 'no entry page with a sense menu'); return; }
  const rel = 'w/' + cfg.menu_page + '.html';
  const { page } = await openPage(context, viewport, rel);
  const links = page.locator('.sense-menu a');
  const n = await links.count();
  let ok = false; let detail = `${n} menu links`;
  if (n >= 5) {
    const href = await links.nth(n - 1).getAttribute('href');
    await links.nth(n - 1).click();
    await page.waitForTimeout(200);
    const target = await page.evaluate((h) => { const el = document.getElementById(h.slice(1)); if (!el) { return null; }
      const r = el.getBoundingClientRect(); return { top: r.top, hash: location.hash }; }, href);
    ok = !!target && target.hash === href && target.top < 400;
    detail += `, last -> ${href}, ${JSON.stringify(target)}`;
  }
  record(viewport, rel, 'the sense menu lists five senses or more and jumps to one', ok, detail);
  await shot(page, `${viewport}-sense-menu`);
}

async function missingXrefCheck(context, viewport) {
  if (!cfg.missing_page) { return; }
  const rel = 'w/' + cfg.missing_page + '.html';
  const { page } = await openPage(context, viewport, rel);
  const info = await page.evaluate(() => {
    const el = document.querySelector('.xref-missing');
    const cs = getComputedStyle(el);
    const link = getComputedStyle(document.querySelector('a') || document.body).color;
    return { tag: el.tagName, inLink: !!el.closest('a'), deco: cs.textDecorationLine, border: cs.borderBottomStyle,
             color: cs.color, body: getComputedStyle(document.body).color, title: el.getAttribute('title'),
             legend: /Grey words have no entry yet/.test(document.body.textContent) };
  });
  const ok = info.tag === 'SPAN' && !info.inLink && info.deco === 'none' && info.border === 'none' && info.color !== info.body &&
    !info.title && info.legend;
  record(viewport, rel, 'a cross-reference with no entry is grey, plain, untitled, with the legend', ok, JSON.stringify(info).slice(0, 160));
}

async function overflowScan(browser) {
  const context = await browser.newContext({ viewport: { width: 360, height: 780 }, isMobile: true, hasTouch: true });
  const page = await context.newPage();
  const bad = [];
  for (const rel of cfg.overflow_pages) {
    await page.goto(cfg.base_url + rel, { waitUntil: 'domcontentloaded' });
    const m = await page.evaluate(() => [document.scrollingElement.scrollWidth, document.documentElement.clientWidth]);
    if (m[0] > m[1]) { bad.push(`${rel} (${m[0]})`); }
  }
  record('phone', `${cfg.overflow_pages.length} pages`, 'no sideways scroll at 360 px on any entry or key page', bad.length === 0,
    bad.length ? `${bad.length}: ${bad.slice(0, 5).join(', ')}` : '');
  await context.close();
}

async function darkModeCheck(context, viewport) {
  const rel = 'w/' + cfg.pages[0].page + '.html';
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push('pageerror: ' + (e.message || e)));
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto(cfg.base_url + rel, { waitUntil: 'load' });
  const colors = await page.evaluate(() => {
    const cs = getComputedStyle(document.body);
    return { background: cs.backgroundColor, color: cs.color };
  });
  const dark = /rgb\((\d+), (\d+), (\d+)\)/.exec(colors.background);
  const isDark = dark && (Number(dark[1]) + Number(dark[2]) + Number(dark[3])) < 3 * 80;
  record(viewport, rel, 'dark mode renders with a dark background and no errors', isDark && errors.length === 0, JSON.stringify(colors));
  await shot(page, `${viewport}-dark`);
}

async function main() {
  fs.mkdirSync(cfg.shots_dir, { recursive: true });
  const pw = loadPlaywright();
  const browser = await launch(pw);
  try {
    const viewports = [
      { name: 'phone', width: 360, height: 780, mobile: true },
      { name: 'desktop', width: 1280, height: 900, mobile: false },
    ];
    for (const vp of viewports) {
      const context = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        isMobile: vp.mobile, hasTouch: vp.mobile, deviceScaleFactor: vp.mobile ? 2 : 1,
      });
      try {
        await basicChecks(context, vp.name, 'index.html', 'home');
        for (const p of cfg.pages) {
          await basicChecks(context, vp.name, 'w/' + p.page + '.html', 'entry-' + p.page);
        }
        await searchCheck(context, vp.name);
        await previewCheck(context, vp.name, vp.mobile);
        await translatorCheck(context, vp.name);
        await darkModeCheck(context, vp.name);
        await menuCheck(context, vp.name, vp.mobile);
        await phraseSearchCheck(context, vp.name);
        await didYouMeanCheck(context, vp.name);
        await queryParamCheck(context, vp.name);
        await notFoundCheck(context, vp.name);
        await senseMenuCheck(context, vp.name);
        await missingXrefCheck(context, vp.name);
      } finally {
        await context.close();
      }
    }
    await overflowScan(browser);
  } finally {
    await browser.close();
  }
}

main().catch((e) => {
  fatal = (e && e.stack) || String(e);
  console.error('site check crashed: ' + fatal);
}).finally(() => {
  fs.writeFileSync(cfg.results_path, JSON.stringify({ results, fatal }, null, 1));
  process.exit(fatal || results.some((r) => !r.ok) ? 1 : 0);
});
