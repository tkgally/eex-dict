/* TKG English Learner's Dictionary: the site's only script.  No framework, no
   dependency, works offline.  Written into docs/site.js by tools/build_site.py
   from tools/site/site.js.

   Jobs: the menu button on phones, the translator's-view toggle (state in
   localStorage), the search box (loads search-index.json on the first
   keystroke, understands inflected forms; loads phrase-index.json when the
   query has a space; suggests near spellings; ?q= in the address runs a
   search; the 404 page searches for the name in the address), previews on
   linked words (hover on desktop, tap on touch, one small JSON payload per
   headword under p/), and the random page. */
(function () {
  'use strict';

  var root = document.documentElement;
  var base = root.getAttribute('data-base') || '';
  var STORAGE_KEY = 'eex-translator';

  function closest(el, selector) {
    while (el && el.nodeType === 1) {
      if (el.matches(selector)) { return el; }
      el = el.parentNode;
    }
    return null;
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  /* ---- translator's view ------------------------------------------- */

  function readPref() {
    try { return localStorage.getItem(STORAGE_KEY) === '1'; } catch (e) { return false; }
  }

  function applyPref(on) {
    if (on) { root.classList.add('translator-on'); } else { root.classList.remove('translator-on'); }
    var buttons = document.querySelectorAll('.translator-toggle');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].setAttribute('aria-pressed', on ? 'true' : 'false');
    }
  }

  applyPref(readPref());

  document.addEventListener('click', function (e) {
    var b = closest(e.target, '.translator-toggle');
    if (!b) { return; }
    var on = !root.classList.contains('translator-on');
    try { localStorage.setItem(STORAGE_KEY, on ? '1' : '0'); } catch (err) { /* private mode: state lasts for the page only */ }
    applyPref(on);
  });

  /* ---- the menu (phones) ---------------------------------------------- */

  var menuButton = document.querySelector('.menu-button');
  var menu = document.getElementById('site-menu');
  function setMenu(open) {
    if (!menuButton || !menu) { return; }
    if (open) { menu.classList.add('open'); } else { menu.classList.remove('open'); }
    menuButton.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  if (menuButton && menu) {
    menuButton.addEventListener('click', function () { setMenu(!menu.classList.contains('open')); });
    document.addEventListener('click', function (e) {
      if (!closest(e.target, '.site-menu') && !closest(e.target, '.menu-button')) { setMenu(false); }
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { setMenu(false); } });
  }

  /* ---- the compact index --------------------------------------------- */

  var indexPromise = null;

  function loadIndex() {
    if (!indexPromise) {
      indexPromise = fetch(base + 'search-index.json', { cache: 'force-cache' })
        .then(function (r) { if (!r.ok) { throw new Error('search index: HTTP ' + r.status); } return r.json(); })
        .then(prepare);
    }
    return indexPromise;
  }

  function norm(s) {
    return String(s || '').toLowerCase().replace(/’/g, "'").replace(/\s+/g, ' ').trim();
  }

  function prepare(data) {
    var words = data.words || [];
    var forms = {};
    for (var i = 0; i < words.length; i++) {
      var w = words[i];
      w.p = w.p || w.w;
      w.f = w.f || [];
      w.k = norm(w.w);
      addForm(forms, w.k, i);
      for (var j = 0; j < w.f.length; j++) { addForm(forms, norm(w.f[j]), i); }
    }
    var keys = Object.keys(forms);
    keys.sort();
    return { words: words, forms: forms, keys: keys, pos: data.pos || {} };
  }

  function addForm(forms, key, i) {
    if (!key) { return; }
    if (!forms[key]) { forms[key] = []; }
    if (forms[key].indexOf(i) < 0) { forms[key].push(i); }
  }

  function posOf(ix, word) {
    var labels = [];
    var slugs = word.s || [];
    for (var i = 0; i < slugs.length; i++) {
      var parts = slugs[i].split('-');
      var code = parts[parts.length - 1];
      if (/^\d+$/.test(code) && parts.length > 2) { code = parts[parts.length - 2]; }
      var label = ix.pos[code] || code;
      if (labels.indexOf(label) < 0) { labels.push(label); }
    }
    return labels.join(', ');
  }

  /* ---- phrases (ruling D1): loaded only when a query has a space ------- */

  var phrasePromise = null;
  var STOP = { 'a': 1, 'an': 1, 'the': 1, 'to': 1, 'of': 1, 'and': 1, 'or': 1, 'it': 1, 'be': 1, 'is': 1, 'are': 1 };

  function loadPhrases() {
    if (!phrasePromise) {
      phrasePromise = fetch(base + 'phrase-index.json', { cache: 'force-cache' })
        .then(function (r) { if (!r.ok) { throw new Error('phrase index: HTTP ' + r.status); } return r.json(); })
        .then(preparePhrases)
        .catch(function () { return { phrases: [], fillers: {} }; });
    }
    return phrasePromise;
  }

  function tokens(s, fillers) {
    var out = [];
    var parts = norm(s).replace(/[^a-z0-9' -]+/g, ' ').split(' ');
    for (var i = 0; i < parts.length; i++) {
      if (parts[i] && !fillers[parts[i]]) { out.push(parts[i]); }
    }
    return out;
  }

  function stem(w) {
    w = w.replace(/'s$/, '');
    if (w.length > 4) { w = w.replace(/(ing|ed|es|s)$/, ''); }
    return w;
  }

  function preparePhrases(data) {
    var fillers = {};
    var list = data.fillers || [];
    for (var i = 0; i < list.length; i++) { fillers[list[i]] = 1; }
    var phrases = [];
    var rows = data.phrases || [];
    for (i = 0; i < rows.length; i++) {
      var r = rows[i];
      var toks = tokens(r[0], fillers);
      var content = [];
      for (var j = 0; j < toks.length; j++) { if (!STOP[toks[j]]) { content.push(stem(toks[j])); } }
      phrases.push({ t: r[0], p: r[1], a: r[2], e: r[3], g: r[4], k: toks.join(' '), c: content });
    }
    return { phrases: phrases, fillers: fillers };
  }

  /* Prefix: the phrase, fillers removed, starts with the query, fillers removed.
     Contains: the query has every content word of a phrase of two content words or more. */
  function searchPhrases(px, query, limit) {
    var qt = tokens(query, px.fillers);
    var qk = qt.join(' ');
    if (qk.length < 3) { return { prefix: [], contains: [] }; }
    var qs = {};
    for (var i = 0; i < qt.length; i++) { qs[stem(qt[i])] = 1; }
    var prefix = [];
    var contains = [];
    for (i = 0; i < px.phrases.length; i++) {
      var ph = px.phrases[i];
      if (ph.k.slice(0, qk.length) === qk) { if (prefix.length < limit) { prefix.push(ph); } continue; }
      if (ph.c.length >= 2 && contains.length < limit) {
        var all = true;
        for (var j = 0; j < ph.c.length; j++) { if (!qs[ph.c[j]]) { all = false; break; } }
        if (all) { contains.push(ph); }
      }
    }
    return { prefix: prefix, contains: contains };
  }

  /* ---- "Did you mean": spelling distance over headwords and forms ------ */

  function distance(a, b, max) {
    /* optimal string alignment (Damerau-Levenshtein with adjacent transpositions); gives up past max */
    var la = a.length, lb = b.length;
    if (Math.abs(la - lb) > max) { return max + 1; }
    var prev2 = null, prev = [], cur, i, j;
    for (j = 0; j <= lb; j++) { prev[j] = j; }
    for (i = 1; i <= la; i++) {
      cur = [i];
      var rowMin = i;
      for (j = 1; j <= lb; j++) {
        var cost = a.charAt(i - 1) === b.charAt(j - 1) ? 0 : 1;
        var v = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost);
        if (prev2 && i > 1 && j > 1 && a.charAt(i - 1) === b.charAt(j - 2) && a.charAt(i - 2) === b.charAt(j - 1)) {
          v = Math.min(v, prev2[j - 2] + 1);
        }
        cur[j] = v;
        if (v < rowMin) { rowMin = v; }
      }
      if (rowMin > max) { return max + 1; }
      prev2 = prev;
      prev = cur;
    }
    return prev[lb];
  }

  function suggestions(ix, query, limit) {
    var q = norm(query);
    if (q.length < 3) { return []; }
    var max = q.length <= 4 ? 1 : 2;
    var best = {};
    var keys = ix.keys;
    for (var i = 0; i < keys.length; i++) {
      var d = distance(q, keys[i], max);
      if (d > max) { continue; }
      var idx = ix.forms[keys[i]];
      for (var j = 0; j < idx.length; j++) {
        var w = ix.words[idx[j]];
        var score = d * 10 + (w.k === keys[i] ? 0 : 1) + Math.min(Math.abs(keys[i].length - q.length), 5);
        if (best[idx[j]] === undefined || score < best[idx[j]].score) { best[idx[j]] = { w: w, score: score, via: w.k === keys[i] ? null : keys[i] }; }
      }
    }
    var out = [];
    for (var k in best) { if (Object.prototype.hasOwnProperty.call(best, k)) { out.push(best[k]); } }
    out.sort(function (a, b) { return a.score - b.score || (a.w.k < b.w.k ? -1 : 1); });
    return out.slice(0, limit);
  }

  /* Rank: exact headword, exact form, headword prefix, form prefix, substring. */
  function search(ix, query, limit) {
    var q = norm(query);
    if (!q) { return []; }
    var seen = {};
    var tiers = [[], [], [], [], []];
    function push(tier, i, via) {
      if (seen[i] !== undefined) { return; }
      seen[i] = tier;
      tiers[tier].push({ w: ix.words[i], via: via, tier: tier });
    }
    var exact = ix.forms[q] || [];
    var i, j;
    for (i = 0; i < exact.length; i++) {
      if (ix.words[exact[i]].k === q) { push(0, exact[i], null); }
    }
    for (i = 0; i < exact.length; i++) { push(1, exact[i], q); }
    var keys = ix.keys;
    for (i = 0; i < keys.length; i++) {
      var k = keys[i];
      if (k.length > q.length && k.slice(0, q.length) === q) {
        var idx = ix.forms[k];
        for (j = 0; j < idx.length; j++) {
          push(ix.words[idx[j]].k === k ? 2 : 3, idx[j], ix.words[idx[j]].k === k ? null : k);
        }
      }
    }
    if (q.length >= 2) {
      for (i = 0; i < ix.words.length; i++) {
        if (ix.words[i].k.indexOf(q) > 0) { push(4, i, null); }
      }
    }
    var out = [];
    for (i = 0; i < tiers.length; i++) {
      tiers[i].sort(function (a, b) {
        if (a.w.k.length !== b.w.k.length) { return a.w.k.length - b.w.k.length; }
        return a.w.k < b.w.k ? -1 : (a.w.k > b.w.k ? 1 : 0);
      });
      for (j = 0; j < tiers[i].length && out.length < limit; j++) { out.push(tiers[i][j]); }
      if (out.length >= limit) { break; }
    }
    return out;
  }

  function wordHref(word) {
    return base + 'w/' + encodeURIComponent(word.p) + '.html';
  }

  function phraseHref(ph) {
    return base + 'w/' + encodeURIComponent(ph.p) + '.html#' + encodeURIComponent(ph.a);
  }

  /* Words and phrases in one list: exact words, phrases that start with the query, word prefixes,
     phrases that contain the query's content words, substrings; near spellings when nothing matches. */
  function combined(ix, px, query, limit) {
    var words = search(ix, query, limit);
    var items = [];
    function addWords(lo, hi) {
      for (var i = 0; i < words.length; i++) {
        if (words[i].tier >= lo && words[i].tier <= hi) {
          items.push({ kind: 'word', href: wordHref(words[i].w), hw: words[i].w.w, pos: posOf(ix, words[i].w),
                       via: words[i].via && words[i].via !== words[i].w.k ? words[i].via : null, g: words[i].w.g });
        }
      }
    }
    function addPhrases(list) {
      for (var i = 0; i < list.length; i++) {
        items.push({ kind: 'phrase', href: phraseHref(list[i]), hw: list[i].t, pos: 'phrase', via: 'in ' + list[i].e, g: list[i].g });
      }
    }
    var ph = px ? searchPhrases(px, query, limit) : { prefix: [], contains: [] };
    addWords(0, 1);
    addPhrases(ph.prefix);
    addWords(2, 3);
    addPhrases(ph.contains);
    var strong = items.length;
    addWords(4, 4);
    if (!strong) {
      var sugg = suggestions(ix, query, 3);
      if (sugg.length) {
        var lead = [{ kind: 'suggest-head' }];
        for (var i = 0; i < sugg.length; i++) {
          lead.push({ kind: 'suggestion', href: wordHref(sugg[i].w), hw: sugg[i].w.w, pos: posOf(ix, sugg[i].w), via: sugg[i].via, g: sugg[i].w.g });
        }
        items = lead.concat(items);
      }
    }
    return items.slice(0, limit + 1);
  }

  /* ---- the search box ------------------------------------------------ */

  function setupSearch(form) {
    var input = form.querySelector('.search-input');
    var list = form.querySelector('.search-results');
    if (!input || !list) { return; }
    var current = [];
    var active = -1;
    var pending = 0;

    function render(results, query) {
      current = [];
      for (var c = 0; c < results.length; c++) { if (results[c].href) { current.push(results[c]); } }
      active = -1;
      if (!query) { list.hidden = true; list.innerHTML = ''; return; }
      if (!results.length) {
        list.innerHTML = '<li class="none">No entry matches “' + escapeHtml(query) + '” yet.</li>';
        list.hidden = false;
        return;
      }
      var html = '';
      for (var i = 0; i < results.length; i++) {
        var r = results[i];
        if (r.kind === 'suggest-head') { html += '<li class="suggest">Did you mean:</li>'; continue; }
        html += '<li class="' + r.kind + '-result' + (r.kind === 'suggestion' ? ' suggestion' : '') + '"><a href="' + escapeHtml(r.href) +
          '" data-hw="' + escapeHtml(r.hw) + '" data-kind="' + r.kind + '">' +
          '<span class="hw">' + escapeHtml(r.hw) + '</span>' +
          '<span class="pos">' + escapeHtml(r.pos || '') + '</span>' +
          (r.via ? '<span class="via">(' + escapeHtml(r.via) + ')</span>' : '') +
          (r.g ? '<span class="gloss">' + escapeHtml(r.g) + '</span>' : '') +
          '</a></li>';
      }
      list.innerHTML = html;
      list.hidden = false;
    }

    function run() {
      var query = input.value;
      var ticket = ++pending;
      if (!norm(query)) { render([], ''); return; }
      var wantPhrases = norm(query).indexOf(' ') > 0;
      Promise.all([loadIndex(), wantPhrases ? loadPhrases() : Promise.resolve(null)]).then(function (got) {
        if (ticket !== pending) { return; }
        render(combined(got[0], got[1], query, 30), query);
      }).catch(function (err) {
        list.innerHTML = '<li class="none">Search is unavailable: ' + escapeHtml(err.message || err) + '</li>';
        list.hidden = false;
      });
    }

    function openFirst() {
      var target = active >= 0 && current[active] ? current[active] : current[0];
      if (target) { window.location.href = target.href; return; }
      var query = input.value;
      if (!norm(query)) { return; }
      var wantPhrases = norm(query).indexOf(' ') > 0;
      Promise.all([loadIndex(), wantPhrases ? loadPhrases() : Promise.resolve(null)]).then(function (got) {
        var results = combined(got[0], got[1], query, 2);
        for (var i = 0; i < results.length; i++) {
          if (results[i].href) { window.location.href = results[i].href; return; }
        }
      });
    }

    function highlight() {
      var items = list.querySelectorAll('li a');
      for (var i = 0; i < items.length; i++) {
        var li = items[i].parentNode;
        if (i === active) { li.classList.add('active'); } else { li.classList.remove('active'); }
      }
    }

    input.addEventListener('input', run);
    input.addEventListener('focus', function () { if (input.value && current.length) { list.hidden = false; } });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); openFirst(); }
      else if (e.key === 'Escape') { list.hidden = true; input.blur(); }
      else if (e.key === 'ArrowDown' && current.length) { e.preventDefault(); active = Math.min(active + 1, current.length - 1); highlight(); }
      else if (e.key === 'ArrowUp' && current.length) { e.preventDefault(); active = Math.max(active - 1, 0); highlight(); }
    });
    form.addEventListener('submit', function (e) { e.preventDefault(); openFirst(); });
    document.addEventListener('click', function (e) {
      if (!closest(e.target, '.search')) { list.hidden = true; }
    });
    return { input: input, run: run };
  }

  var forms = document.querySelectorAll('form.search');
  var boxes = [];
  for (var f = 0; f < forms.length; f++) { var box = setupSearch(forms[f]); if (box) { boxes.push(box); } }

  /* ?q= in the address fills in and runs the search (the main box: the home page's, else the header's);
     the 404 page searches for the name in the address. */
  function initialQuery() {
    var q = null;
    try { q = new URLSearchParams(window.location.search).get('q'); } catch (e) { q = null; }
    if (q) { return q; }
    if (document.body.getAttribute('data-page') === '404') {
      var m = /([^\/]+?)(?:\.html?)?\/?$/.exec(window.location.pathname);
      if (m) {
        var name = m[1];
        try { name = decodeURIComponent(name); } catch (e) { /* keep it raw */ }
        return name.replace(/[-_+]+/g, ' ').trim();
      }
    }
    return null;
  }
  var q0 = initialQuery();
  if (q0 && boxes.length) {
    var mainBox = boxes[boxes.length - 1];
    var home = document.querySelector('form.home-search .search-input');
    for (var b = 0; b < boxes.length; b++) { if (boxes[b].input === home) { mainBox = boxes[b]; } }
    mainBox.input.value = q0;
    mainBox.run();
    try { mainBox.input.focus({ preventScroll: true }); } catch (e) { mainBox.input.focus(); }
  }

  /* ---- previews on linked words -------------------------------------- */

  var preview = null;
  var previewFor = null;
  var showTimer = null;
  var hideTimer = null;
  var payloads = {};
  var lastTouch = { el: null, at: 0 };

  function hoverCapable() {
    return !!(window.matchMedia && window.matchMedia('(hover: hover)').matches);
  }

  function pageOf(a) {
    var m = /(?:^|\/)w\/([^\/#?]+)\.html/.exec(a.getAttribute('href') || '');
    return m ? decodeURIComponent(m[1]) : null;
  }

  function fetchPayload(page) {
    if (!payloads[page]) {
      payloads[page] = fetch(base + 'p/' + encodeURIComponent(page) + '.json')
        .then(function (r) { return r.ok ? r.json() : null; })
        .catch(function () { return null; });
    }
    return payloads[page];
  }

  function ensurePreview() {
    if (!preview) {
      preview = document.createElement('div');
      preview.className = 'preview';
      preview.setAttribute('role', 'tooltip');
      preview.hidden = true;
      preview.addEventListener('mouseenter', cancelHide);
      preview.addEventListener('mouseleave', scheduleHide);
      document.body.appendChild(preview);
    }
    return preview;
  }

  function renderPayload(d, a) {
    var html = '';
    var entries = d.e || [];
    for (var i = 0; i < entries.length; i++) {
      var en = entries[i];
      html += '<p><span class="preview-hw">' + escapeHtml(d.w) + '</span>' +
        (en.hn > 1 ? '<sup>' + en.hn + '</sup>' : '') +
        '<span class="preview-pos">' + escapeHtml(en.pos || '') + '</span> ' +
        escapeHtml(en.d || '') + '</p>';
    }
    if (!entries.length) { html = '<p>' + escapeHtml(d.w || '') + '</p>'; }
    html += '<a class="preview-more" href="' + escapeHtml(a.getAttribute('href')) + '">Open the entry →</a>';
    return html;
  }

  function place(el, a) {
    var r = a.getBoundingClientRect();
    var docWidth = document.documentElement.clientWidth;
    var top = r.bottom + window.pageYOffset + 4;
    var left = r.left + window.pageXOffset;
    var width = el.offsetWidth;
    if (left + width > window.pageXOffset + docWidth - 8) {
      left = Math.max(window.pageXOffset + 8, window.pageXOffset + docWidth - width - 8);
    }
    el.style.top = top + 'px';
    el.style.left = left + 'px';
  }

  function show(a) {
    var page = pageOf(a);
    if (!page) { return; }
    var el = ensurePreview();
    previewFor = a;
    el.innerHTML = '<p class="muted">Loading…</p>';
    el.hidden = false;
    place(el, a);
    fetchPayload(page).then(function (d) {
      if (previewFor !== a) { return; }
      el.innerHTML = d ? renderPayload(d, a) : '<p>No preview for this word.</p>';
      place(el, a);
    });
  }

  function hide() {
    if (preview) { preview.hidden = true; }
    previewFor = null;
  }

  function cancelHide() { if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; } }
  function scheduleHide() { cancelHide(); hideTimer = setTimeout(hide, 250); }

  document.addEventListener('mouseover', function (e) {
    if (!hoverCapable()) { return; }
    var a = closest(e.target, 'a.w');
    if (!a) { return; }
    cancelHide();
    if (showTimer) { clearTimeout(showTimer); }
    showTimer = setTimeout(function () { show(a); }, 120);
  });

  document.addEventListener('mouseout', function (e) {
    if (!hoverCapable()) { return; }
    var a = closest(e.target, 'a.w');
    if (!a) { return; }
    if (showTimer) { clearTimeout(showTimer); showTimer = null; }
    scheduleHide();
  });

  document.addEventListener('touchstart', function (e) {
    var a = closest(e.target, 'a.w');
    lastTouch = { el: a, at: Date.now() };
  }, { passive: true });

  document.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'touch') { return; }
    var a = closest(e.target, 'a.w');
    lastTouch = { el: a, at: Date.now() };
  }, { passive: true });

  document.addEventListener('click', function (e) {
    var a = closest(e.target, 'a.w');
    if (!a) {
      if (!closest(e.target, '.preview')) { hide(); }
      return;
    }
    var byTouch = (lastTouch.el === a && Date.now() - lastTouch.at < 1500) || !hoverCapable();
    if (!byTouch) { return; }
    if (previewFor !== a || !preview || preview.hidden) {
      e.preventDefault();   /* first tap: the preview; the second tap follows the link */
      show(a);
    }
  });

  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { hide(); } });
  window.addEventListener('scroll', function () { if (preview && !preview.hidden && previewFor) { place(preview, previewFor); } }, { passive: true });

  /* ---- the random page ----------------------------------------------- */

  if (document.body.getAttribute('data-page') === 'random') {
    loadIndex().then(function (ix) {
      if (!ix.words.length) { return; }
      var word = ix.words[Math.floor(Math.random() * ix.words.length)];
      window.location.replace(wordHref(word));
    }).catch(function () { /* the page's own links remain */ });
  }
})();
