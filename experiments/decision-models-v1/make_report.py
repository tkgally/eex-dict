#!/usr/bin/env python3
"""make_report.py -- build report.html (one static page, inline SVG charts) from
screen-metrics.json, full-metrics.json and pilot/judgments.json."""
from __future__ import annotations
import html, json, math
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = json.load(open(HERE / "screen-metrics.json"))
F = json.load(open(HERE / "full-metrics.json"))
J = json.load(open(HERE / "pilot/judgments.json"))
esc = html.escape

TASKS = ["pron", "defs", "exsense", "exok", "xref", "link", "triage", "count"]
TNAME = {"pron": "Pronunciation", "defs": "Definition fit", "exsense": "Example → sense", "exok": "Example quality",
         "xref": "See-also link", "link": "Link target", "triage": "Reviewer triage", "count": "Countability"}
LANG = ["defs", "exsense", "exok", "xref", "link"]

# display name, maker, $ per million input tokens, context (k tokens)
DM = {
    "perplexity__pplx-decider-v1.1-27b": ("Decider V1.1 27B", "Perplexity", 0.020, 262),
    "microsoft__microsoft-decision-1": ("Decision-1", "Microsoft", 0.042, 33),
    "cloudflare__clef": ("Clef", "Cloudflare", 0.24, 66),
    "inception__mercury-decide": ("Mercury Decide", "Inception", 0.020, 66),
    "typesafe__jev-1.13": ("Jev 1.13", "TypeSafe", 0.042, 64),
    "liquid__d1": ("D1", "Liquid", 0.040, 66),
    "openai__gpt-6-luna-decisions": ("GPT-6 Luna Decisions", "OpenAI", 0.10, 1050),
    "upstage__solar-decide": ("Solar Decide", "Upstage", 0.05, 524),
    "cloudflare__clef-omni": ("Clef Omni", "Cloudflare", 0.15, 66),
    "nace-ai__drex-v1.5": ("Drex v1.5", "Nace.AI", 0.040, 131),
    "cloudflare__clef-flash": ("Clef Flash", "Cloudflare", 0.038, 66),
    "respan__span-01": ("Span-01", "Respan", 0.020, None),
    "respan__span-01-lite": ("Span-01 Lite", "Respan", 0.0, None),
    "togethercomputer__tev1-4b-experimental": ("TEV1 4B (experimental)", "Together", 0.042, 33),
    "jaredpalmer__kev-4b": ("Kev 4B", "Jared Palmer", 0.042, 8),
    "upstage__solar-decide-flash": ("Solar Decide Flash", "Upstage", 0.05, 524),
}
LLM = {
    "openai__gpt-5.6-terra": ("GPT-5.6 Terra", "OpenAI", "reviewer-a today; 2.00 / 12.00"),
    "stepfun__step-5-preview": ("Step 5 Preview", "StepFun", "chat model with built-in reasoning; 1.00 / 2.70"),
    "anthropic__claude-haiku-5.5": ("Claude Haiku 5.5", "Anthropic", "small chat model; 0.10 / 0.50"),
    "openai__gpt-6-luna": ("GPT-6 Luna (chat)", "OpenAI", "same model as Luna Decisions, as a chat model; 0.10 / 0.50"),
}
ENS = "ensemble__top3"
PANEL = "panel__pronunciation-3"
NAMES = {**{k: v[0] for k, v in DM.items()}, **{k: v[0] for k, v in LLM.items()},
         ENS: "Top-3 average", PANEL: "Pronunciation panel (3 LLMs)"}


def acc(src, m, t):
    r = (src.get(m) or {}).get(t)
    return r.get("acc") if r and "acc" in r else None


def bin_of(v):
    if v is None:
        return "na"
    edges = [0.6, 0.7, 0.8, 0.9, 0.95]
    return "s" + str(1 + sum(v >= e for e in edges))


def fmt(v, d=2):
    return "—" if v is None else f"{v:.{d}f}".lstrip("0") if v < 1 else "1.00"


def eng_score(m):
    vals = [acc(S, m, t) for t in ["defs", "exsense", "exok", "xref", "link", "count"]]
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else 0


# ---------------------------------------------------------------- heatmaps
def heatmap(rows, cols, src, extra=None, groups=None):
    out = ['<div class="scroll"><table class="heat"><thead><tr><th class="mname">Model</th>']
    out += [f'<th>{esc(TNAME[c])}</th>' for c in cols]
    if extra:
        out += [f'<th>{esc(h)}</th>' for h, _ in extra]
    out.append("</tr></thead><tbody>")
    for i, m in enumerate(rows):
        if groups and i in groups:
            out.append(f'<tr class="grp"><td colspan="{1 + len(cols) + len(extra or [])}">{esc(groups[i])}</td></tr>')
        out.append(f'<tr><th class="mname" scope="row">{esc(NAMES.get(m, m))}</th>')
        for c in cols:
            v = acc(src, m, c)
            tip = f"{NAMES.get(m, m)} · {TNAME[c]}: " + ("not supported" if v is None else f"{v:.0%} correct")
            out.append(f'<td class="cell {bin_of(v)}" data-tip="{esc(tip)}" tabindex="0">{fmt(v)}</td>')
        for _, fn in extra or []:
            out.append(f"<td>{fn(m)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


screen_rows = sorted([m for m in DM], key=lambda m: -eng_score(m))
passed = [m for m in screen_rows if eng_score(m) >= 0.85]


def chip(m):
    ok = eng_score(m) >= 0.85
    return f'<span class="chip {"good" if ok else "bad"}">{"✓ pass" if ok else "✕ fail"}</span>'


screen_tbl = heatmap(screen_rows + ["openai__gpt-5.6-terra"], ["pron", "defs", "exsense", "exok", "xref", "link", "count"], S,
                     extra=[("Language score", lambda m: f'<span class="num">{eng_score(m):.2f}</span>'),
                            ("Screen", lambda m: chip(m) if m in DM else '<span class="chip ref">reference</span>')],
                     groups={len(screen_rows): "Reference: the current reviewer model"})

full_dm = sorted([m for m in passed], key=lambda m: -sum(acc(F, m, t) or 0 for t in LANG))
full_rows = full_dm + [ENS] + list(LLM) + [PANEL]
full_tbl = heatmap(full_rows, TASKS, F, groups={0: "Decision models (passed the screen)", len(full_dm): "Average of the three best-screened decision models",
                                                len(full_dm) + 1: "Chat LLMs asked the same questions", len(full_dm) + 5: "The production pronunciation check"})


# ---------------------------------------------------------------- strip plot per task
def strip():
    W, rowh, left, right, top = 760, 46, 150, 24, 34
    H = top + rowh * len(TASKS) + 30
    x0, x1 = 0.4, 1.0

    def X(v):
        return left + (v - x0) / (x1 - x0) * (W - left - right)
    g = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Accuracy per task: every decision model compared with chat LLMs">']
    for t in [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        g.append(f'<line x1="{X(t):.1f}" y1="{top-8}" x2="{X(t):.1f}" y2="{H-26}" class="grid"/>')
        g.append(f'<text x="{X(t):.1f}" y="{H-8}" class="tick" text-anchor="middle">{int(t*100)}%</text>')
    for i, t in enumerate(TASKS):
        y = top + i * rowh + rowh / 2
        g.append(f'<text x="{left-12}" y="{y+4:.1f}" class="rowlab" text-anchor="end">{esc(TNAME[t])}</text>')
        g.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W-right}" y2="{y:.1f}" class="lane"/>')
        dms = [(m, acc(F, m, t)) for m in full_dm if acc(F, m, t) is not None]
        best = max(dms, key=lambda x: x[1])
        for m, v in dms:
            cls = "dm best" if m == best[0] else "dm"
            r = 6 if m == best[0] else 4.5
            g.append(f'<circle cx="{X(max(v, x0)):.1f}" cy="{y:.1f}" r="{r}" class="{cls}" data-tip="{esc(NAMES[m])}: {v:.0%}" tabindex="0"/>')
        for m, shape in (("openai__gpt-5.6-terra", "diamond"), ("stepfun__step-5-preview", "tri")):
            v = acc(F, m, t)
            if v is None:
                continue
            cx = X(max(v, x0))
            if shape == "diamond":
                pts = f"{cx},{y-8} {cx+8},{y} {cx},{y+8} {cx-8},{y}"
            else:
                pts = f"{cx},{y-8} {cx+8},{y+7} {cx-8},{y+7}"
            g.append(f'<polygon points="{pts}" class="llm" data-tip="{esc(NAMES[m])}: {v:.0%}" tabindex="0"/>')
        if t == "pron":
            v = acc(F, PANEL, t)
            g.append(f'<rect x="{X(v)-6:.1f}" y="{y-6:.1f}" width="12" height="12" class="panel" data-tip="Production pronunciation panel: {v:.0%}" tabindex="0"/>')
        g.append(f'<text x="{X(max(best[1], x0)):.1f}" y="{y-12:.1f}" class="annot" text-anchor="middle">{esc(NAMES[best[0]])}</text>')
    g.append("</svg>")
    return "".join(g)


# ---------------------------------------------------------------- cost vs accuracy scatter
def scatter():
    W, H, left, right, top, bottom = 760, 380, 64, 24, 20, 52
    pts = []
    for m in full_dm + list(LLM):
        if any(acc(F, m, t) is None for t in LANG):
            continue
        a = sum(acc(F, m, t) for t in LANG) / len(LANG)
        costs = [F[m][t]["cost_per_item"] for t in LANG]
        c = sum(costs) / len(costs) * 1000
        pts.append((m, max(c, 0.001), a))
    lx0, lx1, y0, y1 = -3, 1, 0.82, 0.98

    def X(c):
        return left + (math.log10(c) - lx0) / (lx1 - lx0) * (W - left - right)

    def Y(a):
        return top + (y1 - a) / (y1 - y0) * (H - top - bottom)
    g = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Cost per thousand checks against average accuracy">']
    for e in range(lx0, lx1 + 1):
        x = X(10 ** e)
        g.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{H-bottom}" class="grid"/>')
        lab = {-3: "$0.001", -2: "$0.01", -1: "$0.10", 0: "$1", 1: "$10"}[e]
        g.append(f'<text x="{x:.1f}" y="{H-bottom+18}" class="tick" text-anchor="middle">{lab}</text>')
    for a in [0.82, 0.84, 0.86, 0.88, 0.90, 0.92, 0.94, 0.96, 0.98]:
        g.append(f'<line x1="{left}" y1="{Y(a):.1f}" x2="{W-right}" y2="{Y(a):.1f}" class="grid"/>')
        g.append(f'<text x="{left-8}" y="{Y(a)+4:.1f}" class="tick" text-anchor="end">{int(a*100)}%</text>')
    g.append(f'<text x="{(left+W-right)/2:.0f}" y="{H-10}" class="axis" text-anchor="middle">Cost per 1,000 checks (log scale)</text>')
    g.append(f'<text x="14" y="{(top+H-bottom)/2:.0f}" class="axis" text-anchor="middle" transform="rotate(-90 14 {(top+H-bottom)/2:.0f})">Mean accuracy, five language tasks</text>')
    label = {"perplexity__pplx-decider-v1.1-27b": (-10, 16, "end"), "microsoft__microsoft-decision-1": (8, 14, "start"),
             "typesafe__jev-1.13": (-10, -8, "end"), "openai__gpt-5.6-terra": (-10, -8, "end"),
             "stepfun__step-5-preview": (-10, -8, "end"), "anthropic__claude-haiku-5.5": (12, 16, "start"),
             "nace-ai__drex-v1.5": (8, 4, "start"), "upstage__solar-decide": (8, 4, "start"),
             "openai__gpt-6-luna": (10, -8, "start")}
    for m, c, a in pts:
        cls = "llm" if m in LLM else "dm"
        cx, cy = X(c), Y(a)
        tip = f"{NAMES[m]}: {a:.1%} mean accuracy, ${c:.3f} per 1,000 checks"
        if m in LLM:
            g.append(f'<polygon points="{cx},{cy-8} {cx+8},{cy} {cx},{cy+8} {cx-8},{cy}" class="llm" data-tip="{esc(tip)}" tabindex="0"/>')
        else:
            g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="6" class="dm" data-tip="{esc(tip)}" tabindex="0"/>')
        if m in label:
            dx, dy, anc = label[m]
            g.append(f'<text x="{cx+dx:.1f}" y="{cy+dy:.1f}" class="annot" text-anchor="{anc}">{esc(NAMES[m])}</text>')
    g.append("</svg>")
    return "".join(g), pts


# ---------------------------------------------------------------- automation bars (cross-validated)
def autobars():
    sel = ["inception__mercury-decide", "microsoft__microsoft-decision-1", "perplexity__pplx-decider-v1.1-27b",
           ENS, "openai__gpt-5.6-terra", "stepfun__step-5-preview"]
    tasks = ["exok", "defs", "xref"]
    W, left, right, rowh, top = 760, 190, 120, 24, 30
    blocks = []
    for t in tasks:
        H = top + rowh * len(sel) + 10
        g = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="Share of {TNAME[t]} items decided automatically">']
        g.append(f'<text x="0" y="16" class="rowlab strong">{esc(TNAME[t])}</text>')
        for k in (0, 0.25, 0.5, 0.75, 1.0):
            x = left + k * (W - left - right)
            g.append(f'<line x1="{x:.1f}" y1="{top-6}" x2="{x:.1f}" y2="{H-6}" class="grid"/>')
            g.append(f'<text x="{x:.1f}" y="{top-10}" class="tick" text-anchor="middle">{int(k*100)}%</text>')
        for i, m in enumerate(sel):
            cv = F[m][t]["cv"]
            y = top + i * rowh
            w = cv["auto_share"] * (W - left - right)
            err = cv["auto_error"] or 0
            cls = "llm" if m in LLM else "dm"
            g.append(f'<text x="{left-10}" y="{y+15}" class="rowlab" text-anchor="end">{esc(NAMES[m])}</text>')
            tip = f"{NAMES[m]}: {cv['auto_share']:.0%} decided automatically, {err:.0%} of those wrong"
            g.append(f'<rect x="{left}" y="{y+4}" width="{max(w, 1.5):.1f}" height="14" rx="2" class="{cls}" data-tip="{esc(tip)}" tabindex="0"/>')
            flag = " over" if err > 0.05 else ""
            g.append(f'<text x="{left + w + 8:.1f}" y="{y+15}" class="val{flag}">{cv["auto_share"]:.0%} · {err:.0%} wrong</text>')
        g.append("</svg>")
        blocks.append("".join(g))
    return "".join(blocks)


# ---------------------------------------------------------------- pilot bars
def pilotbars():
    rows = [("Example → sense (28 flags from 1,500 examples)", len(J["exsense"]["real"]), len(J["exsense"]["arguable"]), len(J["exsense"]["false"])),
            ("See-also links (100 flags from 1,468 links)", 0, len(J["xref"]["arguable"]), len(J["xref"]["legitimate"]))]
    W, left, right, top, rowh = 760, 0, 0, 8, 62
    H = top + rowh * len(rows)
    g = [f'<svg viewBox="0 0 {W} {H}" class="chart" role="img" aria-label="How many pilot flags were real problems">']
    for i, (lab, real, arg, fal) in enumerate(rows):
        y = top + i * rowh
        n = real + arg + fal
        g.append(f'<text x="0" y="{y+12}" class="rowlab">{esc(lab)}</text>')
        x = 0
        for v, cls, name in ((real, "p-real", "real problem"), (arg, "p-arg", "arguable"), (fal, "p-false", "no problem")):
            if not v:
                continue
            w = v / n * W
            g.append(f'<rect x="{x+1:.1f}" y="{y+20}" width="{max(w-2, 2):.1f}" height="22" rx="3" class="{cls}" data-tip="{v} {name}" tabindex="0"/>')
            if w > 70:
                g.append(f'<text x="{x+8:.1f}" y="{y+35}" class="inbar {cls}-t">{v} {name}</text>')
            x += w
    g.append("</svg>")
    return "".join(g)


sc_svg, sc_pts = scatter()


def costrow(m):
    rs = [F[m][t] for t in TASKS if F.get(m, {}).get(t) and "cost_per_item" in F[m][t]]
    c = sum(r["cost_per_item"] for r in rs) / len(rs) * 1000
    lat = sorted(r["lat_median"] for r in rs)[len(rs) // 2]
    return c, lat


cost_rows = []
for m in full_dm + list(LLM):
    c, lat = costrow(m)
    cost_rows.append((m, c, lat))
cost_rows.sort(key=lambda x: x[1])
cost_tbl = ['<div class="scroll"><table class="data"><thead><tr><th>Model</th><th>Kind</th><th class="r">$ per 1,000 checks</th><th class="r">Median seconds per check</th></tr></thead><tbody>']
for m, c, lat in cost_rows:
    kind = "chat LLM" if m in LLM else "decision"
    cost_tbl.append(f'<tr><td>{esc(NAMES[m])}</td><td>{kind}</td><td class="r num">{c:.4f}</td><td class="r num">{lat:.2f}</td></tr>')
cost_tbl.append(f'<tr><td>{esc(NAMES[PANEL])}</td><td>3 chat LLMs</td><td class="r num">0.70</td><td class="r num">about 1 (batched 50 words a call)</td></tr>')
cost_tbl.append("</tbody></table></div>")

# per-cycle savings table (12-entry build cycle; corpus averages)
terra_c = dict((m, c) for m, c, _ in cost_rows)["openai__gpt-5.6-terra"] / 1000
pplx_c = dict((m, c) for m, c, _ in cost_rows)["perplexity__pplx-decider-v1.1-27b"] / 1000
ms_c = dict((m, c) for m, c, _ in cost_rows)["microsoft__microsoft-decision-1"] / 1000
lat_t = dict((m, l) for m, _, l in cost_rows)["openai__gpt-5.6-terra"]
lat_d = dict((m, l) for m, _, l in cost_rows)["perplexity__pplx-decider-v1.1-27b"]
checks = [("Example → sense, every example of a 12-entry cycle", 107),
          ("Example quality, every example of a 12-entry cycle", 114),
          ("Link target, every ambiguous word on the whole site (one rebuild)", 31854)]
sav = ['<div class="scroll"><table class="data"><thead><tr><th>Check</th><th class="r">Calls</th><th class="r">With GPT-5.6 Terra</th><th class="r">With a decision model</th><th class="r">Wall time, Terra → decision (8 parallel)</th></tr></thead><tbody>']
for lab, n in checks:
    sav.append(f'<tr><td>{esc(lab)}</td><td class="r num">{n:,}</td><td class="r num">${n*terra_c:.2f}</td>'
               f'<td class="r num">${n*pplx_c:.4f}</td><td class="r num">{n*lat_t/8/60:.1f} → {n*lat_d/8/60:.1f} min</td></tr>')
sav.append("</tbody></table></div>")

ex_examples_real = J["exsense"]["real"]

STYLE = r"""
:root{
  /* Layout: one reading column (about 68ch) with charts and tables allowed to run to 820px; data as tables first, pictures second */
  --bg:#f5f7fa; --surface:#ffffff; --ink:#16202b; --ink-2:#465363; --ink-3:#6f7c8c; --rule:#d9e0e8;
  --accent:#1d5cb4; --dm:#2a78d6; --llm:#eb6834; --panel:#1baf7a;
  --good:#1f7a45; --good-bg:#e3f3e9; --warn:#8a5a00; --warn-bg:#fbf0d9; --bad:#a3302a; --bad-bg:#f8e3e1; --ref-bg:#e8edf3;
  --s1:#f1f5fb; --s2:#dce8f7; --s3:#b6cfee; --s4:#7eaae2; --s5:#3f7fd2; --s6:#1d58a6; --na:#eef0f3;
  --t-lo:#16202b; --t-hi:#ffffff;
  --p-real:#1d5cb4; --p-arg:#8fb3e6; --p-false:#cfd6df; --p-real-t:#ffffff; --p-arg-t:#10233d; --p-false-t:#2c3642;
  --f-display:"Newsreader", "Iowan Old Style", Georgia, serif;
  --f-body:"Public Sans", "Segoe UI", system-ui, sans-serif;
  --f-mono:"IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#11161d; --surface:#18202a; --ink:#e7ecf2; --ink-2:#b3bfcc; --ink-3:#8794a4; --rule:#2b3542;
  --accent:#7aa8ee; --dm:#3987e5; --llm:#d95926; --panel:#199e70;
  --good:#7fd3a0; --good-bg:#16352a; --warn:#f0c46b; --warn-bg:#3a2e12; --bad:#f19b93; --bad-bg:#3e1f1d; --ref-bg:#232d3a;
  --s1:#18222f; --s2:#1b2d45; --s3:#1f4170; --s4:#2a5c9e; --s5:#3f7fd2; --s6:#86b2f0; --na:#1d242d;
  --t-lo:#e7ecf2; --t-hi:#ffffff;
  --p-real:#3f7fd2; --p-arg:#2a4d7c; --p-false:#36404d; --p-real-t:#ffffff; --p-arg-t:#e7ecf2; --p-false-t:#d6dde6;
  color-scheme:dark }}
:root[data-theme="dark"]{
  --bg:#11161d; --surface:#18202a; --ink:#e7ecf2; --ink-2:#b3bfcc; --ink-3:#8794a4; --rule:#2b3542;
  --accent:#7aa8ee; --dm:#3987e5; --llm:#d95926; --panel:#199e70;
  --good:#7fd3a0; --good-bg:#16352a; --warn:#f0c46b; --warn-bg:#3a2e12; --bad:#f19b93; --bad-bg:#3e1f1d; --ref-bg:#232d3a;
  --s1:#18222f; --s2:#1b2d45; --s3:#1f4170; --s4:#2a5c9e; --s5:#3f7fd2; --s6:#86b2f0; --na:#1d242d;
  --t-lo:#e7ecf2; --t-hi:#ffffff;
  --p-real:#3f7fd2; --p-arg:#2a4d7c; --p-false:#36404d; --p-real-t:#ffffff; --p-arg-t:#e7ecf2; --p-false-t:#d6dde6;
  color-scheme:dark }
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:16px/1.6 var(--f-body);margin:0}
.wrap{max-width:880px;margin:0 auto;padding-inline:20px;padding-block:40px 80px}
.prose{max-width:68ch}
h1,h2,h3{font-family:var(--f-display);font-weight:600;text-wrap:balance;line-height:1.15;margin:0}
h1{font-size:clamp(2rem,5vw,2.9rem);letter-spacing:-.01em}
h2{font-size:1.65rem;margin-top:3.2rem;padding-top:1.2rem;border-top:1px solid var(--rule)}
h3{font-size:1.2rem;margin-top:1.8rem}
p{margin:.8rem 0}
.eyebrow{font:500 .78rem/1.2 var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3)}
.lede{font-size:1.15rem;color:var(--ink-2)}
.headword{font-family:var(--f-display);font-size:1.05rem;font-weight:600}
.pos{font:italic 400 .95rem var(--f-display);color:var(--ink-3);margin-left:.35em}
.num,td.num{font-family:var(--f-mono);font-variant-numeric:tabular-nums;font-size:.9rem}
.scroll{overflow-x:auto;margin:1rem 0;-webkit-overflow-scrolling:touch}
table{border-collapse:collapse;width:100%;font-size:.92rem}
table.data th,table.data td{padding:.45rem .6rem;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}
table.data thead th{font:600 .74rem/1.3 var(--f-mono);letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3)}
.r{text-align:right!important}
table.heat{min-width:640px}
table.heat td:last-child{padding-right:2px}
table.heat th,table.heat td{padding:0;text-align:center}
table.heat thead th{font:600 .7rem/1.25 var(--f-mono);letter-spacing:.03em;text-transform:uppercase;color:var(--ink-3);padding:.3rem .25rem;vertical-align:bottom}
table.heat th.mname{text-align:left;font:500 .88rem/1.3 var(--f-body);color:var(--ink);padding:.25rem .6rem .25rem 0;white-space:nowrap}
table.heat thead th.mname{font:600 .7rem/1.25 var(--f-mono);color:var(--ink-3)}
table.heat td{padding:.15rem .25rem}
.cell{font:500 .82rem/1 var(--f-mono);font-variant-numeric:tabular-nums;height:30px;min-width:44px;border-radius:3px;outline-offset:1px;border:2px solid var(--bg)}
.cell.s1{background:var(--s1);color:var(--t-lo)} .cell.s2{background:var(--s2);color:var(--t-lo)} .cell.s3{background:var(--s3);color:var(--t-lo)}
.cell.s4{background:var(--s4);color:var(--t-lo)} .cell.s5{background:var(--s5);color:var(--t-hi)} .cell.s6{background:var(--s6);color:var(--t-hi)}
:root[data-theme="dark"] .cell.s6{color:#0f1a29}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .cell.s6{color:#0f1a29}}
.cell.na{background:var(--na);color:var(--ink-3)}
tr.grp td{text-align:left!important;font:600 .72rem/1 var(--f-mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3);padding:1.1rem 0 .35rem!important}
.legend{display:flex;flex-wrap:wrap;gap:.4rem 1rem;align-items:center;font-size:.82rem;color:var(--ink-2);margin:.4rem 0 0}
.legend .sw{display:inline-block;width:14px;height:14px;border-radius:3px;vertical-align:-2px;margin-right:.35rem}
.chip{display:inline-block;font:600 .72rem/1 var(--f-mono);padding:.3rem .5rem;border-radius:999px;white-space:nowrap}
.chip.good{background:var(--good-bg);color:var(--good)} .chip.bad{background:var(--bad-bg);color:var(--bad)}
.chip.warn{background:var(--warn-bg);color:var(--warn)} .chip.ref{background:var(--ref-bg);color:var(--ink-2)}
.verdicts{display:grid;gap:0;border-top:1px solid var(--rule);margin-top:1.2rem}
.verdict{display:grid;grid-template-columns:minmax(0,13rem) minmax(0,1fr);gap:.4rem 1.2rem;padding:.8rem 0;border-bottom:1px solid var(--rule)}
.verdict > div{min-width:0}
.verdict p{margin:.2rem 0 0;color:var(--ink-2);font-size:.95rem}
@media (max-width:560px){.verdict{grid-template-columns:minmax(0,1fr)}}
.chart{width:100%;height:auto;display:block;margin:.6rem 0;overflow:visible}
.chart text{fill:var(--ink-2);font-family:var(--f-body)}
.chart .tick{font:11px var(--f-mono);fill:var(--ink-3)}
.chart .axis{font-size:12px;fill:var(--ink-3)}
.chart .rowlab{font-size:13px;fill:var(--ink)}
.chart .rowlab.strong{font:600 15px var(--f-display);fill:var(--ink)}
.chart .annot{font-size:11px;fill:var(--ink-2)}
.chart .val{font:11.5px var(--f-mono);fill:var(--ink-2)} .chart .val.over{fill:var(--bad)}
.chart .grid{stroke:var(--rule);stroke-width:1}
.chart .lane{stroke:var(--rule);stroke-width:1;stroke-dasharray:2 4}
.chart circle.dm{fill:var(--dm);fill-opacity:.45;stroke:var(--surface);stroke-width:1.5}
.chart circle.dm.best{fill-opacity:1}
.chart polygon.llm,.chart rect.llm{fill:var(--llm);stroke:var(--surface);stroke-width:1.5}
.chart rect.dm{fill:var(--dm)}
.chart rect.panel{fill:var(--panel);stroke:var(--surface);stroke-width:1.5}
.chart .p-real{fill:var(--p-real)} .chart .p-arg{fill:var(--p-arg)} .chart .p-false{fill:var(--p-false)}
.chart .inbar{font:600 12px var(--f-body)} .chart .p-real-t{fill:var(--p-real-t)} .chart .p-arg-t{fill:var(--p-arg-t)} .chart .p-false-t{fill:var(--p-false-t)}
[data-tip]{cursor:default} [data-tip]:focus{outline:2px solid var(--accent);outline-offset:2px}
.chart [data-tip]:hover{stroke:var(--ink);stroke-width:1.5}
#tip{position:fixed;z-index:10;pointer-events:none;background:var(--ink);color:var(--bg);font:500 .8rem/1.35 var(--f-body);padding:.35rem .55rem;border-radius:4px;max-width:280px}
.callout{background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:1rem 1.2rem;margin:1.2rem 0}
.callout h3{margin-top:0}
ul.tight{padding-left:1.2rem;margin:.6rem 0} ul.tight li{margin:.25rem 0}
code{font-family:var(--f-mono);font-size:.86em;background:var(--ref-bg);padding:.05rem .3rem;border-radius:3px}
.small{font-size:.86rem;color:var(--ink-3)}
blockquote{margin:.6rem 0;padding-left:1rem;border-left:3px solid var(--rule);color:var(--ink-2);font-family:var(--f-display);font-size:1.05rem}
a{color:var(--accent)}
@media (prefers-reduced-motion: no-preference){ .cell{transition:filter .15s} .cell:hover{filter:brightness(1.08)} }
"""

JS = r"""
(function(){var t=document.getElementById('tip');function show(e){var el=e.target.closest('[data-tip]');if(!el){t.hidden=true;return}
t.textContent=el.getAttribute('data-tip');t.hidden=false;var r=el.getBoundingClientRect();var x=(e.clientX||r.left+r.width/2)+12,y=(e.clientY||r.top)+12;
if(x+290>innerWidth)x=innerWidth-296;t.style.left=x+'px';t.style.top=y+'px'}
document.addEventListener('mousemove',show);document.addEventListener('focusin',show);document.addEventListener('mouseleave',function(){t.hidden=true});
document.addEventListener('focusout',function(){t.hidden=true})})();
"""


def verdict(task, chip_cls, chip_txt, body):
    return (f'<div class="verdict"><div><span class="headword">{esc(TNAME[task])}</span><br>'
            f'<span class="chip {chip_cls}">{chip_txt}</span></div><div><p>{body}</p></div></div>')


A = lambda m, t: acc(F, m, t)  # noqa: E731
best_dm = {t: max(((m, A(m, t)) for m in full_dm if A(m, t) is not None), key=lambda x: x[1]) for t in TASKS}
P = lambda v: f"{v*100:.0f}%"  # noqa: E731

verdicts = "".join([
    verdict("exsense", "good", "✓ worth a pilot",
            f"Best decision model {P(best_dm['exsense'][1])} ({esc(NAMES[best_dm['exsense'][0]])}), GPT-5.6 Terra {P(A('openai__gpt-5.6-terra','exsense'))}. "
            "On 1,500 real examples it flagged 28; 8 were genuine misfilings and 12 more were examples that fit two senses. A cheap advisory flag for reviewers, never an automatic fix."),
    verdict("exok", "warn", "◐ promising, untested on real data",
            f"Best {P(best_dm['exok'][1])} against Terra's {P(A('openai__gpt-5.6-terra','exok'))}; Mercury Decide could settle 89% of items on its own with 5% of those wrong. "
            "Only synthetic errors were tested, so a real-data pilot comes first."),
    verdict("link", "warn", "◐ possible, at build time",
            f"Jev 1.13 picks the right homograph entry {P(A('typesafe__jev-1.13','link'))} of the time against Terra's {P(A('openai__gpt-5.6-terra','link'))}. "
            "Cheap enough to run over every ambiguous word on the site, but links are built in CI, which has no key, so verdicts would have to be stored."),
    verdict("defs", "warn", "◐ no better than review",
            f"Decision models match Terra ({P(best_dm['defs'][1])} against {P(A('openai__gpt-5.6-terra','defs'))}), and both miss about half of the definitions swapped in from a related word. "
            f"Step 5 Preview, which reasons before answering, reached {P(A('stepfun__step-5-preview','defs'))}. Nothing here replaces the whole-entry review."),
    verdict("xref", "bad", "✕ not on real data",
            f"Up to {P(best_dm['xref'][1])} on the test, ahead of Terra. On the 1,468 real links, though, 100 were flagged and none was clearly wrong. "
            "The models cannot see why a link exists (an idiom, a confusable word, a non-first sense)."),
    verdict("count", "bad", "✕ too weak",
            f"Best {P(best_dm['count'][1])} against Terra {P(A('openai__gpt-5.6-terra','count'))} and Step 5 {P(A('stepfun__step-5-preview','count'))}. "
            "Every model struggles with nouns used both ways (<i>a coffee</i>, <i>some coffee</i>)."),
    verdict("pron", "bad", "✕ cannot read IPA",
            f"Best {P(best_dm['pron'][1])}. Decision models wave through most vowel and stress errors. The production panel, which transcribes and compares by script, scored {P(A(PANEL,'pron'))}."),
    verdict("triage", "bad", "✕ nobody can",
            f"Predicting the adjudicator's apply-or-reject call from the reviewer's note: decision models {P(min(A(m,'triage') for m in full_dm))}–{P(best_dm['triage'][1])}, "
            f"chat LLMs {P(A('openai__gpt-5.6-terra','triage'))}–{P(A('openai__gpt-6-luna','triage'))}. Coin-flip territory. Adjudication stays with the session."),
])

task_rows = [
    ("pron", "noul", "Is this IPA a correct General American pronunciation (sounds and stress)?", "160: 80 verified transcriptions; 80 with one scripted error (stress moved, vowel changed, consonant voicing flipped)", "Panel of three LLMs transcribes; a script compares (<code>pronounce_check.py</code>)"),
    ("defs", "noul", "Is this a real meaning of the word?", "160: 80 real definitions; 40 from a random word; 40 from a related word (a see-also or synonym target)", "Reviewers read every definition inside the whole-entry review"),
    ("exsense", "choice", "Which sense does this example illustrate?", "150 examples from entries with 3–6 senses", "Reviewers (no separate check)"),
    ("exok", "noul", "Is this a good learner's example: grammatical, natural, the word in the stated sense?", "160: 80 real examples; 80 with a wrong verb form, two words swapped, or the headword replaced", "Reviewers"),
    ("xref", "noul", "Would a see-also link from A to B help a learner?", "150: 75 real links; 75 targets borrowed from other entries' links", "Reviewers; <code>crossref.py</code> checks only that targets exist"),
    ("link", "choice", "Which entry does this word belong to here (e.g. <i>plan</i> noun or verb)?", "150 example sentences of headwords with two entries", "Site build guesses the part of speech (<code>link_words.py</code>)"),
    ("triage", "noul", "Is the reviewer's objection right, so the entry should change?", "200 past reviewer issues: 100 applied, 100 rejected by the adjudicator", "The session reads and decides every blocking issue"),
    ("count", "choice", "Countable, uncountable, both, singular only, or plural only?", "150 noun senses, 30 per class", "Drafter writes; reviewers check"),
]
task_tbl = ['<div class="scroll"><table class="data"><thead><tr><th>Task</th><th>Question type</th><th>Question asked</th><th>Test items (from reviewed entries)</th><th>Done today by</th></tr></thead><tbody>']
for t, ty, q, items, now in task_rows:
    task_tbl.append(f'<tr><td><span class="headword">{esc(TNAME[t])}</span></td><td><span class="pos">{ty}</span></td><td>{q}</td><td>{items}</td><td>{now}</td></tr>')
task_tbl.append("</tbody></table></div>")

model_tbl = ['<div class="scroll"><table class="data"><thead><tr><th>Model</th><th>Maker</th><th class="r">$ per M input tokens</th><th class="r">Context</th><th>Note</th></tr></thead><tbody>']
named = {"microsoft__microsoft-decision-1", "nace-ai__drex-v1.5", "cloudflare__clef-omni", "perplexity__pplx-decider-v1.1-27b", "openai__gpt-6-luna-decisions"}
for m in screen_rows:
    n, mk, pr, ctx = DM[m]
    note = []
    if m in named:
        note.append("on your list")
    if m.startswith("respan"):
        note.append("yes/no questions only")
    if m == "respan__span-01-lite":
        note.append("free")
    if m == "upstage__solar-decide":
        note.append("slow tail: p90 16 s")
    model_tbl.append(f'<tr><td>{esc(n)}</td><td>{esc(mk)}</td><td class="r num">{pr:.3f}</td><td class="r num">{(str(ctx)+"k") if ctx else "—"}</td><td>{esc(", ".join(note))}</td></tr>')
model_tbl.append("</tbody></table></div>")

real_list = "".join(f"<li>{esc(x.split(': ',1)[0])}: <i>{esc(x.split(': ',1)[1])}</i></li>" for x in ex_examples_real)

page = f"""<title>Decision Models Trial</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,600;1,6..72,400&family=Public+Sans:wght@400;500;600&display=swap">
<style>{STYLE}</style>
<div id="tip" hidden></div>
<main class="wrap">
<header class="prose">
<p class="eyebrow">TKG English Learner's Dictionary · experiment decision-models-v1 · 10 October 2026</p>
<h1>Can decision models check dictionary entries?</h1>
<p class="lede">I tested sixteen decision models on eight checking tasks drawn from the dictionary's 1,944 reviewed entries, then compared them with four chat LLMs, including the reviewer the project uses today. Two short real-data pilots followed.</p>
</header>

<section class="prose">
<h2>The short answer</h2>
<p>Decision models are fast and almost free: about <b>$0.004–0.06 per thousand checks</b>, against <b>$0.59</b> for GPT-5.6 Terra, and roughly three times faster per call. On narrow language questions the best of them match Terra: which sense an example belongs to, whether an example sentence is broken, which homograph a word is. They fail at anything that needs IPA or editorial judgment, and every model, chat LLMs included, failed at predicting how the adjudicator would rule on a reviewer's objection.</p>
<p>None of them can replace the current whole-entry review, so today's cost per entry would not fall. What they could add is new, narrow, advisory checks at almost no cost. The strongest candidate is an example-to-sense check: on real entries it found genuine misfilings that had survived review.</p>
</section>

<div class="verdicts">{verdicts}</div>

<section>
<h2 class="prose">What a decision model is</h2>
<div class="prose">
<p>A decision model reads a <i>state</i> (here, a small JSON record such as a word, a definition and an example) and answers typed questions: <b>noul</b> (yes or no, returned as a probability of yes), <b>choice</b> (one of several named options, with a probability for each) or <b>score</b> (a position on an ordered scale). It returns no text and no reasoning, and it bills input tokens only. OpenRouter serves these models through <code>POST /api/alpha/decisions</code>. The endpoint is marked alpha.</p>
<p>The models do not appear in OpenRouter's ordinary model list. Asking the list for <code>output_modalities=decisions</code> returned 19 listings, which reduce to 16 distinct models (the others are free variants and an alias). Five of the six models on your list are decision models. <b>Step 5 Preview is not</b>: it is StepFun's new general chat model, so I tested it as a chat LLM.</p>
</div>
{''.join(model_tbl)}
</section>

<section>
<h2 class="prose">Eight tasks</h2>
<p class="prose">Each test set comes from the dictionary's own reviewed entries and adjudication log, so every item has a known answer. No external data was used. Wrong items were made by script (a moved stress mark, two swapped words, a definition borrowed from another entry), so they are cleaner than a drafter's real mistakes; the two pilots in the last section test real entries.</p>
{''.join(task_tbl)}
</section>

<section>
<h2 class="prose">Stage 1: a quick screen</h2>
<p class="prose">Ten easy items per task (nine for pronunciation), every model. Before looking at the results I set the bar: a model passes if it averages at least 85% on the six language tasks. Pronunciation is shown but not counted, because reading IPA is a separate skill. Thirteen models passed. The whole screen cost $0.017 for all sixteen models; one GPT-5.6 Terra pass over the same items cost $0.040.</p>
{screen_tbl}
<div class="legend"><span><span class="sw" style="background:var(--s1)"></span>below 60%</span><span><span class="sw" style="background:var(--s3)"></span>70–80%</span><span><span class="sw" style="background:var(--s5)"></span>90–95%</span><span><span class="sw" style="background:var(--s6)"></span>95% and up</span><span>— = question type not supported</span></div>
</section>

<section>
<h2 class="prose">Stage 2: the full test</h2>
<p class="prose">There were 1,280 items across the eight tasks. The thirteen models that passed the screen answered all of them, and so did four chat LLMs, asked the same questions with the same wording and told to reply with a label and a probability. GPT-5.6 Terra ran without hidden reasoning, as it does in production. For pronunciation, the production panel transcribed each word itself and a script compared the transcriptions, as <code>pronounce_check.py</code> does. A cell shows the share of items answered correctly.</p>
{full_tbl}
<h3 class="prose">Best decision model against the chat LLMs, task by task</h3>
{strip()}
<div class="legend"><span><svg width="14" height="14" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="var(--dm)"/></svg>decision model (solid dot = best, named)</span><span><svg width="16" height="16" aria-hidden="true"><polygon points="8,1 15,8 8,15 1,8" fill="var(--llm)"/></svg>GPT-5.6 Terra</span><span><svg width="16" height="16" aria-hidden="true"><polygon points="8,1 15,14 1,14" fill="var(--llm)"/></svg>Step 5 Preview</span><span><svg width="14" height="14" aria-hidden="true"><rect x="1" y="1" width="12" height="12" fill="var(--panel)"/></svg>production pronunciation panel</span></div>
<div class="prose">
<p><b>Where they hold up.</b> On example-to-sense, example quality, see-also and link target, the best decision models are within one or two points of Terra, and on see-also they are ahead. Averaging the three best-screened models gains little over the best single one.</p>
<p><b>Where they fall down.</b> Pronunciation: most decision models accept nearly every transcription; ten of the thirteen catch fewer than a third of the vowel errors. Terra without reasoning does no better at <i>checking</i> IPA, which is why the production panel <i>transcribes</i> instead. Countability: the "countable or uncountable" class defeats everyone. Triage: the reviewer's note alone does not carry enough to predict the ruling.</p>
<p><b>Reasoning helps.</b> Step 5 Preview, the only chat model here that reasons before answering, was the best non-panel model on pronunciation (97%), definitions (94%) and countability (84%). It cost the most ($1.44 per thousand checks), its slowest calls took 25 seconds, and about one triage item in six produced no answer within 3,000 tokens.</p>
</div>
</section>

<section>
<h2 class="prose">Cost, speed and accuracy</h2>
{sc_svg}
<div class="legend"><span><svg width="14" height="14" aria-hidden="true"><circle cx="7" cy="7" r="5" fill="var(--dm)"/></svg>decision model</span><span><svg width="16" height="16" aria-hidden="true"><polygon points="8,1 15,8 8,15 1,8" fill="var(--llm)"/></svg>chat LLM</span><span class="small">Mean over definition fit, example → sense, example quality, see-also and link target. Respan models are left out (yes/no questions only).</span></div>
<p class="prose">The cheapest decision models sit about two orders of magnitude to the left of Terra at nearly the same height. The small chat models (Haiku 5.5, GPT-6 Luna) are also cheap and accurate on these five tasks, but they are roughly three times slower per call and have to be parsed: in the first pass Haiku returned empty replies on nearly half the items until its hidden reasoning was switched off, and Luna echoed whole option descriptions instead of labels.</p>
{''.join(cost_tbl)}
<p class="small prose">Billed <code>usage.cost</code> per item, averaged over the eight tasks; latency is the median single call from this container. Decision models bill input only, and most of that input is the question wording, which is sent with every item.</p>

<h3 class="prose">Could they decide on their own?</h3>
<p class="prose">A practical set-up is a two-threshold gate: accept when the probability of "fine" is high, flag when it is low, and send the middle band to an LLM. Thresholds were tuned on half the items and tested on the other half (2-fold cross-validation), aiming for at most 5% errors among the automatic decisions. Bars show the share settled automatically; red text means the error target was missed on unseen items.</p>
{autobars()}
<p class="prose">For example quality, Mercury Decide could settle about nine items in ten at the target error rate, more than Terra can, because Terra's probabilities are nearly all 0 or 1. For definitions, no model met the target on unseen items.</p>

<h3 class="prose">Savings, in this project's units</h3>
<p class="prose">These checks do not exist as separate steps today; the two reviewers cover them inside one whole-entry call, which costs about $0.065 per entry (ledger average). A decision-model check therefore saves no current spend. It makes a new check affordable. Corpus averages: 9.5 examples per entry, 93% of them in entries with two or more senses.</p>
{''.join(sav)}
<p class="small prose">Prices are the billed averages from this test (Decider V1.1 for the decision column). The site-wide link check would cost about 13 cents with a decision model; with Terra it would cost about ${31854*terra_c:.0f} per rebuild.</p>
</section>

<section>
<h2 class="prose">Real entries, unaltered</h2>
<p class="prose">Synthetic errors flatter a checker. So I ran the two strongest decision models (Decision-1 and Decider V1.1) over real entries, flagged items only where both disagreed with the dictionary, and read every flag myself.</p>
{pilotbars()}
<div class="legend"><span><span class="sw" style="background:var(--p-real)"></span>real problem</span><span><span class="sw" style="background:var(--p-arg)"></span>arguable (fits two senses; a weak link)</span><span><span class="sw" style="background:var(--p-false)"></span>no problem</span></div>
<div class="prose">
<p><b>Example → sense.</b> 28 of 1,500 examples flagged (1.9%). Eight are real: the example sits under a sense it does not show.</p>
<ul class="tight">{real_list}</ul>
<p>Twelve more are examples that read naturally under two senses (<i>a bag of apples</i>, <i>bring a pan of water to a boil</i>). That is worth a reviewer's glance in a learner's dictionary, where an example is supposed to settle the sense. Eight flags were simply wrong. Twenty useful flags in 1,500 examples, for about one cent, is a good return.</p>
<p><b>See-also links.</b> 100 of 1,468 links flagged (6.8%), and none is clearly wrong; at most three are weak (<i>friend → neighbor</i>, <i>game → toy</i>, <i>layer → level</i>). The rest are links the models could not understand from two definitions: idioms (<i>promise → moon</i>, <i>sleeve → heart</i>), confusables (<i>peace ↔ piece</i>, <i>fabric ↔ factory</i>), and links to a target's later sense (<i>block → street</i>, <i>degree → university</i>). The synthetic test had used obviously unrelated targets, so the 97% it reported doesn't hold on real links. As a lint, this check would be almost all noise.</p>
</div>
</section>

<section class="prose">
<h2>Trade-offs</h2>
<ul class="tight">
<li><b>Accuracy.</b> On narrow language questions the best decision models are 0–2 points below Terra and occasionally above it. On anything needing IPA, policy knowledge or editorial judgment they are far below, and even their high-confidence answers are often wrong.</li>
<li><b>No reasons.</b> A decision model gives a probability and nothing else. The pipeline's adjudication rule (read every issue, log apply/reject with a reason) needs a reason to check, so a decision-model flag can only route an item to a reader, never settle it.</li>
<li><b>Calibration varies.</b> Mercury, Decision-1 and D1 give graded probabilities that support thresholds. Luna Decisions and Jev often answer exactly 0 or 1, which leaves no middle band to escalate.</li>
<li><b>Fit with the house rules.</b> Flags are verdicts, not field text, so they stay on the right side of the ownership table. Under rule 10, a new check starts as a note in <code>wiki/notes/</code> and lands in a later run with a logged reason.</li>
<li><b>Maturity.</b> The endpoint is alpha, most models are under three weeks old, and one is labelled experimental. Pin dated versions (as with <code>typesafe/jev-1.13</code>) and expect slugs to change.</li>
</ul>

<h2>Suggested next steps (owner's call)</h2>
<ul class="tight">
<li>Pilot an <b>advisory example-to-sense flag</b> in review mode: two decision models, flag only when both disagree with the filing, write one line per flag into the review notes for the adjudicator. Cost per 12-entry cycle: well under one cent.</li>
<li>Run a <b>real-data pilot for example quality</b> before trusting the synthetic 95%.</li>
<li>If build-time links matter, test <b>stored link-target verdicts</b> (the CI build has no key).</li>
<li>Leave pronunciation, countability, see-also and triage as they are.</li>
</ul>

<h2>Method notes</h2>
<ul class="tight small">
<li>All runs on 2026-10-10, single pass, temperature 0 for chat models. Each task has 150–200 items, so a difference under about 4 points is within noise.</li>
<li>The question wording was identical for every model and not tuned per model. The screen used only 10 items per task, so a borderline model could have been excluded by chance; the three that failed (Kev 4B, TEV1 4B, Solar Decide Flash) were also the weakest overall.</li>
<li>The ensemble (Decider V1.1, Clef, Decision-1) was fixed from the screen before the full results were read.</li>
<li>Spend: $3.71 recorded in the ledger under <code>experiment:decision-models-v1</code>. Decision models (both screens, the full run and the pilots) were $0.32 of that. The four chat baselines were $3.28, of which Step 5 Preview's reasoning was $2.32. The pronunciation panel was $0.11.</li>
<li>Pilot judgments are the session's own reading of each flag, recorded in <code>pilot/judgments.json</code>.</li>
<li>Code, test sets and per-item verdicts: <code>experiments/decision-models-v1/</code> in the repository.</li>
</ul>
</section>
</main>
<script>{JS}</script>
"""
(HERE / "report.html").write_text(page)
print("wrote report.html", len(page))
