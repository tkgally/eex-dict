#!/usr/bin/env python3
"""Check the built site in a real browser at phone and desktop widths.

    python3 tools/site_check.py [--docs docs] [--port 8765] [--entries entries] [--no-browser]
    python3 tools/site_check.py --fixture      # build and check a scratch site from the test fixture

Serves the built docs/ from a local static server (http.server in a thread)
and drives Chromium through the globally installed Playwright package
(tools/site/check.mjs, run with NODE_PATH set to ``npm root -g``).  At 360x780
(touch) and 1280x900 it opens the home page and three entry pages and checks:
no JavaScript errors, no horizontal overflow, the viewport meta and the
disclosure on every page, that searching for an inflected form of an existing
entry (a verb's past tense from its inflections, ``ran`` when run-v exists)
returns that headword first and Enter opens it, that hovering (desktop) or
tapping (phone: first tap previews, second follows) a linked word opens a
preview, and that the translator's-view toggle reveals a hidden ``.translator``
block and remembers its state.  Screenshots go to .tmp/site-check/ (gitignored).
A few static checks run first without a browser.  Prints a pass/fail table and
exits 1 on any failure.  Standard library only on the Python side.

``--fixture`` copies tools/tests/fixtures/bank-n.json (marked reviewed) into a
temporary entries directory, builds a scratch site from it with
tools/build_site.py, and checks that instead: the way to exercise the whole
pipeline while no reviewed entry exists.  Nothing is written under entries/.
"""

import argparse
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from functools import partial
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

CHECK_SCRIPT = HERE / "site" / "check.mjs"
SHOTS_DIR = ROOT / ".tmp" / "site-check"
HREF_RE = re.compile(r'\b(?:href|src)="([^"]*)"')


class Row:
    def __init__(self, viewport, page, check, ok, detail=""):
        self.viewport, self.page, self.check, self.ok, self.detail = viewport, page, check, bool(ok), detail


# --------------------------------------------------------------------------
# Choosing what to test
# --------------------------------------------------------------------------

def html_pages(docs):
    return sorted(p for p in (docs / "w").glob("*.html")) if (docs / "w").is_dir() else []


def pick_pages(docs, want=3):
    """Three entry pages, preferring ones with linked words and a translator block."""
    scored = []
    for path in html_pages(docs):
        text = path.read_text(encoding="utf-8")
        if "http-equiv=\"refresh\"" in text:
            continue
        has_links = 'class="w"' in text
        has_translator = 'class="translator' in text
        scored.append((-(int(has_links) + int(has_translator)), path.stem, has_links, has_translator))
    scored.sort()
    pages = [s[1] for s in scored[:want]]
    preview = next((s[1] for s in scored if s[2]), pages[0] if pages else None)
    translator = next((s[1] for s in scored if s[3]), pages[0] if pages else None)
    return pages, preview, translator


def load_index(docs):
    try:
        return json.loads((docs / "search-index.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"words": []}


def pick_search(docs, entries_dir):
    """``(query, expected headword, expected page)``: an inflected form that must find its headword."""
    words = load_index(docs).get("words") or []
    by_word = {w["w"]: w for w in words if isinstance(w, dict) and "w" in w}

    def page_of(w):
        return w.get("p") or w["w"]

    run = by_word.get("run")
    if run and "ran" in [f.lower() for f in run.get("f") or []]:
        return "ran", "run", page_of(run)
    if entries_dir and entries_dir.is_dir():
        for path in sorted(entries_dir.rglob("*.json")):
            try:
                d = eexlib.load_json(path)
            except (OSError, ValueError):
                continue
            if not isinstance(d, dict) or eexlib.is_redirect_stub(d):
                continue
            if (d.get("provenance") or {}).get("status") != "reviewed" or d.get("pos") not in ("v", "phrv"):
                continue
            past = ((d.get("inflections") or {}).get("forms") or {}).get("past_tense")
            hw = d.get("headword")
            if past and hw in by_word and past.lower() != hw.lower():
                return past, hw, page_of(by_word[hw])
    for w in words:
        for form in w.get("f") or []:
            if form.lower() != w["w"].lower():
                return form, w["w"], page_of(w)
    if words:
        return words[0]["w"], words[0]["w"], page_of(words[0])
    return None


# --------------------------------------------------------------------------
# Static checks (no browser)
# --------------------------------------------------------------------------

def static_checks(docs):
    rows = []
    pages = sorted(docs.rglob("*.html"))
    if not pages:
        return [Row("static", "docs", "built pages exist", False, "no .html under %s" % docs)]
    missing_meta, missing_disclosure, missing_search, absolute = [], [], [], []
    for path in pages:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(docs).as_posix()
        if 'name="viewport" content="width=device-width, initial-scale=1"' not in text:
            missing_meta.append(rel)
        if "no human has checked most entries" not in text:
            missing_disclosure.append(rel)
        if 'form class="search' not in text:
            missing_search.append(rel)
        for href in HREF_RE.findall(text):
            if href.startswith("/") or href.startswith("http"):
                if rel == "about.html" and href.startswith("http"):
                    continue
                absolute.append("%s: %s" % (rel, href))
    rows.append(Row("static", "%d pages" % len(pages), "viewport meta on every page", not missing_meta, ", ".join(missing_meta[:3])))
    rows.append(Row("static", "%d pages" % len(pages), "AI-authorship disclosure on every page", not missing_disclosure, ", ".join(missing_disclosure[:3])))
    rows.append(Row("static", "%d pages" % len(pages), "search box on every page", not missing_search, ", ".join(missing_search[:3])))
    rows.append(Row("static", "%d pages" % len(pages), "relative links only (absolute links only on about)", not absolute, "; ".join(absolute[:3])))
    for name in ("site.css", "site.js", "search-index.json", "index.html"):
        rows.append(Row("static", name, "exists", (docs / name).is_file()))
    return rows


# --------------------------------------------------------------------------
# The server and the browser
# --------------------------------------------------------------------------

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt, *args):  # noqa: D401 - silence the request log
        pass


def start_server(docs, port):
    handler = partial(QuietHandler, directory=str(docs))
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, server.server_address[1]


def npm_root(npm):
    try:
        out = subprocess.run([npm, "root", "-g"], capture_output=True, text=True, timeout=60)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return os.environ.get("NODE_PATH", "")


def chromium_executable(browsers_path):
    base = Path(browsers_path) if browsers_path else None
    if not base or not base.is_dir():
        return None
    candidates = sorted(base.glob("chromium-*/chrome-linux/chrome")) + sorted(base.glob("chromium_headless_shell-*/chrome-linux/headless_shell"))
    direct = base / "chromium"
    if direct.is_file() and os.access(direct, os.X_OK):
        candidates.insert(0, direct)
    for c in candidates:
        if c.is_file():
            return str(c)
    return None


def run_browser(docs, port, entries_dir, node, npm, timeout):
    rows = []
    pages, preview_page, translator_page = pick_pages(docs)
    search = pick_search(docs, entries_dir)
    if len(pages) < 1 or search is None:
        rows.append(Row("browser", "setup", "at least one entry page and a searchable headword", False,
                        "build the site from reviewed entries first (or pass --entries with a scratch copy to build_site.py)"))
        return rows, False
    if len(pages) < 3:
        rows.append(Row("browser", "setup", "three entry pages available", True,
                        "only %d headword page(s) built; checking those (not a site fault)" % len(pages)))
    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    for old in SHOTS_DIR.glob("*.png"):
        old.unlink()
    results_path = SHOTS_DIR / "results.json"
    if results_path.exists():
        results_path.unlink()
    config = {
        "base_url": "http://127.0.0.1:%d/" % port,
        "pages": [{"page": p} for p in pages],
        "search": {"query": search[0], "expect": search[1], "expect_page": search[2]},
        "preview_page": preview_page,
        "translator_page": translator_page,
        "shots_dir": str(SHOTS_DIR),
        "results_path": str(results_path),
        "executable_path": chromium_executable(os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or "/opt/pw-browsers"),
    }
    config_path = SHOTS_DIR / "config.json"
    config_path.write_text(json.dumps(config, indent=1), encoding="utf-8")
    env = dict(os.environ)
    env["NODE_PATH"] = npm_root(npm)
    env.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
    print("site_check: pages %s; search %r -> %r; NODE_PATH=%s" % (", ".join(pages), search[0], search[1], env["NODE_PATH"]))
    try:
        proc = subprocess.run([node, str(CHECK_SCRIPT), str(config_path)], env=env, timeout=timeout,
                              capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError) as exc:
        rows.append(Row("browser", "node", "Playwright run", False, str(exc)))
        return rows, False
    if proc.stderr.strip():
        print(proc.stderr.rstrip())
    data = None
    if results_path.exists():
        try:
            data = json.loads(results_path.read_text(encoding="utf-8"))
        except ValueError:
            data = None
    if not data:
        rows.append(Row("browser", "node", "Playwright run produced results", False, (proc.stdout + proc.stderr).strip()[-400:]))
        return rows, False
    for r in data.get("results") or []:
        rows.append(Row(r.get("viewport", "?"), r.get("page", "?"), r.get("check", "?"), r.get("ok"), r.get("detail", "")))
    if data.get("fatal"):
        rows.append(Row("browser", "node", "Playwright run completed", False, str(data["fatal"]).splitlines()[0][:300]))
    return rows, True


# --------------------------------------------------------------------------

def print_table(rows):
    width_page = max([len(r.page) for r in rows] + [4])
    width_check = max([len(r.check) for r in rows] + [5])
    print("%-6s %-8s %-*s %-*s detail" % ("result", "viewport", width_page, "page", width_check, "check"))
    for r in rows:
        print("%-6s %-8s %-*s %-*s %s" % ("pass" if r.ok else "FAIL", r.viewport, width_page, r.page, width_check, r.check, r.detail[:160]))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check the built site in a browser at phone and desktop widths.")
    parser.add_argument("--docs", default=str(ROOT / "docs"), help="the built site (default docs/)")
    parser.add_argument("--port", type=int, default=8765, help="local port for the static server (default 8765)")
    parser.add_argument("--entries", default=str(ROOT / "entries"), help="entries directory the site was built from (to pick a verb's past tense)")
    parser.add_argument("--node", default=shutil.which("node") or "node")
    parser.add_argument("--npm", default=shutil.which("npm") or "npm")
    parser.add_argument("--timeout", type=int, default=300, help="seconds allowed for the browser run")
    parser.add_argument("--no-browser", action="store_true", help="static checks only")
    parser.add_argument("--fixture", action="store_true", help="build and check a scratch site from the test fixture")
    args = parser.parse_args(argv)

    scratch = None
    if args.fixture:
        scratch = tempfile.mkdtemp(prefix="eex-site-check-")
        args.entries, args.docs = fixture_site(Path(scratch))
    try:
        return check(args)
    finally:
        if scratch:
            shutil.rmtree(scratch, ignore_errors=True)


def fixture_site(scratch):
    """Build a scratch site from the fixture entry (marked reviewed); returns (entries dir, docs dir)."""
    import build_site
    fixture = eexlib.load_json(HERE / "tests" / "fixtures" / "bank-n.json")
    fixture["provenance"]["status"] = "reviewed"
    entries = scratch / "entries"
    eexlib.save_json(entries / eexlib.shard(fixture["slug"]) / (fixture["slug"] + ".json"), fixture)
    # A companion entry for a word the fixture's examples use, so that links,
    # previews, and cross-references have a target.  Scratch data only.
    companion = json.loads(json.dumps(fixture))
    companion["id"] = companion["slug"] = "account-n"
    companion["headword"] = "account"
    companion["pronunciation"]["american"]["ipa"] = "ə.ˈkaʊnt"
    companion["pronunciation"]["british"]["ipa"] = "ə.ˈkaʊnt"
    companion["inflections"]["forms"] = {"plural": "accounts"}
    companion["core_idea"] = None
    companion["senses"] = [companion["senses"][0]]
    sense = companion["senses"][0]
    sense.update({"signpost": None, "definition": "an arrangement with a bank that lets you keep money there and take it out when you need it",
                  "explanation": None, "subsenses": [], "compare": [], "collocations": [], "synonyms": [], "antonyms": []})
    sense["labels"]["domain"] = ["finance"]
    sense["examples"] = [{"text": "Mari opened an account at the bank.", "note": None, "pattern": None},
                         {"text": "How much money is in your account?", "note": None, "pattern": None}]
    sense["adaptation"] = {"semantic": None, "grammar": None, "culture": None, "false_friends": None, "pronunciation": None}
    for key in ("phrases", "word_family", "learner_errors", "see_also"):
        companion[key] = []
    companion["synonym_discrimination"] = companion["etymology"] = companion["usage_note"] = None
    companion["adaptation"] = {"semantic": None, "grammar": "Countable: an account, two accounts.", "culture": None,
                               "false_friends": None, "pronunciation": None}
    eexlib.save_json(entries / eexlib.shard(companion["slug"]) / (companion["slug"] + ".json"), companion)
    docs = scratch / "docs"
    build_site.build(root=ROOT, entries_dir=entries, out=docs, quiet=True)
    print("site_check: scratch site from the fixture built in %s" % docs)
    return str(entries), str(docs)


def check(args):
    docs = Path(args.docs).resolve()
    if not (docs / "index.html").is_file():
        print("site_check: %s has no index.html; run python3 tools/build_site.py first" % docs)
        return 1
    rows = static_checks(docs)
    server = None
    if not args.no_browser:
        server, port = start_server(docs, args.port)
        try:
            browser_rows, _ran = run_browser(docs, port, Path(args.entries).resolve(), args.node, args.npm, args.timeout)
        finally:
            server.shutdown()
            server.server_close()
        rows.extend(browser_rows)
    print_table(rows)
    failed = sum(1 for r in rows if not r.ok)
    print("site_check: %d checks, %d failed%s" % (len(rows), failed, "" if args.no_browser else "; screenshots in %s" % SHOTS_DIR))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
