/* TKG English Learner's Dictionary: the site's only script.  No framework, no
   dependency, works offline.  Written into docs/site.js by tools/build_site.py
   from tools/site/site.js.

   Jobs: the translator's-view toggle (state in localStorage), the search box
   (loads search-index.json on the first keystroke, understands inflected
   forms), previews on linked words (hover on desktop, tap on touch, one small
   JSON payload per headword under p/), and the random page. */
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

  /* Rank: exact headword, exact form, headword prefix, form prefix, substring. */
  function search(ix, query, limit) {
    var q = norm(query);
    if (!q) { return []; }
    var seen = {};
    var tiers = [[], [], [], [], []];
    function push(tier, i, via) {
      if (seen[i] !== undefined) { return; }
      seen[i] = tier;
      tiers[tier].push({ w: ix.words[i], via: via });
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

  /* ---- the search box ------------------------------------------------ */

  function setupSearch(form) {
    var input = form.querySelector('.search-input');
    var list = form.querySelector('.search-results');
    if (!input || !list) { return; }
    var current = [];
    var active = -1;
    var pending = 0;

    function render(results, query) {
      current = results;
      active = -1;
      if (!query) { list.hidden = true; list.innerHTML = ''; return; }
      if (!results.length) {
        list.innerHTML = '<li class="none">No entry matches “' + escapeHtml(query) + '” yet.</li>';
        list.hidden = false;
        return;
      }
      var html = '';
      loadIndex().then(function (ix) {
        for (var i = 0; i < results.length; i++) {
          var w = results[i].w;
          html += '<li><a href="' + escapeHtml(wordHref(w)) + '" data-hw="' + escapeHtml(w.w) + '">' +
            '<span class="hw">' + escapeHtml(w.w) + '</span>' +
            '<span class="pos">' + escapeHtml(posOf(ix, w)) + '</span>' +
            (results[i].via && results[i].via !== w.k ? '<span class="via">(' + escapeHtml(results[i].via) + ')</span>' : '') +
            (w.g ? '<span class="gloss">' + escapeHtml(w.g) + '</span>' : '') +
            '</a></li>';
        }
        list.innerHTML = html;
        list.hidden = false;
      });
    }

    function run() {
      var query = input.value;
      var ticket = ++pending;
      if (!norm(query)) { render([], ''); return; }
      loadIndex().then(function (ix) {
        if (ticket !== pending) { return; }
        render(search(ix, query, 30), query);
      }).catch(function (err) {
        list.innerHTML = '<li class="none">Search is unavailable: ' + escapeHtml(err.message || err) + '</li>';
        list.hidden = false;
      });
    }

    function openFirst() {
      var target = active >= 0 && current[active] ? current[active] : current[0];
      if (target) { window.location.href = wordHref(target.w); return; }
      loadIndex().then(function (ix) {
        var results = search(ix, input.value, 1);
        if (results.length) { window.location.href = wordHref(results[0].w); }
      });
    }

    function highlight() {
      var items = list.querySelectorAll('li');
      for (var i = 0; i < items.length; i++) {
        if (i === active) { items[i].classList.add('active'); } else { items[i].classList.remove('active'); }
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
  }

  var forms = document.querySelectorAll('form.search');
  for (var f = 0; f < forms.length; f++) { setupSearch(forms[f]); }

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
