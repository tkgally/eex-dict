#!/usr/bin/env python3
"""build_sets.py -- build the eight test sets for decision-models-v1 from the
dictionary's own reviewed entries and adjudication log (no external data).

Writes sets/<task>.jsonl, one item per line:
  {"id", "task", "state", "gold", "kind", "screen"}
gold is True/False for yes-no (noul) tasks and an option key for choice tasks;
"kind" names the item's stratum (positive, or the kind of negative); "screen"
marks the ten easy items per task used in the screening phase.

Deterministic: seed 20261010.
"""
from __future__ import annotations
import glob, json, random, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(ROOT / "tools"))
from pronounce_check import agree  # noqa: E402  N2 normalization: a corruption must differ at phoneme level
OUT = Path(__file__).resolve().parent / "sets"
rng = random.Random(20261010)

E = [json.load(open(f)) for f in sorted(glob.glob(str(ROOT / "entries/*/*.json")))]
BY = {e["slug"]: e for e in E}
POSNAME = {"n": "noun", "v": "verb", "adj": "adjective", "adv": "adverb", "prep": "preposition",
           "pron": "pronoun", "det": "determiner", "conj": "conjunction", "modal": "modal verb",
           "aux": "auxiliary verb", "phrv": "phrasal verb", "interj": "interjection",
           "inf": "infinitive marker", "num": "number", "prefix": "prefix", "suffix": "suffix", "abbr": "abbreviation"}


def strip_marks(t):
    return re.sub(r"\*\*?|__", "", t or "")


def first_def(e):
    return strip_marks(e["senses"][0]["definition"])


def write(task, items):
    OUT.mkdir(exist_ok=True)
    with open(OUT / f"{task}.jsonl", "w") as f:
        for i, it in enumerate(items):
            it = {"id": f"{task}-{i:03d}", "task": task, **it}
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    c = collections.Counter(it["kind"] for it in items)
    print(f"{task}: {len(items)} items {dict(c)}; screen {sum(it['screen'] for it in items)}")


def mark_screen(items, kinds, n=10):
    """Mark n items for screening, balanced over the given (easy) kinds."""
    pools = {k: [it for it in items if it["kind"] == k] for k in kinds}
    per = n // len(kinds)
    for k in kinds:
        for it in pools[k][:per]:
            it["screen"] = True
    for it in items:
        it.setdefault("screen", False)


# ---------------------------------------------------------------- T1 pronunciation
VOWELS = ["aɪ", "aʊ", "eɪ", "oʊ", "ɔɪ", "ɑ", "æ", "ʌ", "ɛ", "ɪ", "i", "u", "ʊ", "ɔ", "ə", "ɝ", "ɚ", "e", "o", "a"]
VSWAP = {"æ": ["ɑ", "eɪ"], "ɑ": ["æ", "oʊ"], "ɪ": ["i", "aɪ"], "i": ["ɪ", "aɪ"], "ɛ": ["i", "eɪ"],
         "eɪ": ["æ", "i"], "ʌ": ["oʊ", "u"], "oʊ": ["ɑ", "aʊ"], "u": ["ʌ", "oʊ"], "ʊ": ["u", "ʌ"],
         "aɪ": ["i", "eɪ"], "aʊ": ["oʊ", "ɔ"], "ɔ": ["oʊ", "aʊ"], "ɝ": ["ɑr", "ɛr"]}
CSWAP = {"s": "z", "z": "s", "t": "d", "d": "t", "p": "b", "b": "p", "k": "g", "g": "k", "f": "v",
         "v": "f", "θ": "ð", "ð": "θ", "ʃ": "ʒ"}


def tokens(ipa):
    out, i = [], 0
    while i < len(ipa):
        two = ipa[i:i + 2]
        if two in ("aɪ", "aʊ", "eɪ", "oʊ", "ɔɪ", "tʃ", "dʒ"):
            out.append(two); i += 2
        else:
            out.append(ipa[i]); i += 1
    return out


def is_v(t):
    return t in VOWELS


def stress_shift(ipa):
    """Move the main stress to another full-vowel syllable. With syllable dots the
    mark goes at the start of the new syllable; without them, before the onset consonant."""
    if "." in ipa:
        syl = ipa.replace("ˈ", ".ˈ").replace("..", ".").strip(".").split(".")
        cur = next((i for i, x in enumerate(syl) if x.startswith("ˈ")), None)
        if cur is None:
            return None
        plain = [x.lstrip("ˈˌ") for x in syl]
        others = [i for i, x in enumerate(plain) if i != cur and any(is_v(t) and t not in ("ə", "ɚ") for t in tokens(x))]
        if not others:
            return None
        n = rng.choice(others)
        return ".".join(("ˈ" + x) if i == n else x for i, x in enumerate(plain))
    t = [x for x in tokens(ipa) if x not in ("ˈ", "ˌ")]
    nuclei = [i for i, x in enumerate(t) if is_v(x)]
    if len(nuclei) < 2 or "ˈ" not in ipa:
        return None
    k = len([x for x in tokens(ipa.split("ˈ")[0]) if x != "ˌ"])
    stressed_nuc = next((n for n in nuclei if n >= k), None)
    others = [n for n in nuclei if n != stressed_nuc and t[n] not in ("ə", "ɚ")]
    if not others:
        return None
    n = rng.choice(others)
    ins = n - 1 if n - 1 >= 0 and not is_v(t[n - 1]) else n
    t.insert(ins, "ˈ")
    return "".join(t)


def vowel_swap(ipa):
    toks = tokens(ipa)
    idx = [i for i, x in enumerate(toks) if x in VSWAP]
    if not idx:
        return None
    # prefer the stressed vowel
    stressed = [i for i in idx if "ˈ" in toks[:i]] or idx
    i = stressed[0]
    toks[i] = rng.choice(VSWAP[toks[i]])
    return "".join(toks)


def cons_swap(ipa):
    toks = tokens(ipa)
    idx = [i for i, x in enumerate(toks) if x in CSWAP]
    if not idx:
        return None
    i = rng.choice(idx)
    toks[i] = CSWAP[toks[i]]
    return "".join(toks)


def build_pron():
    pool = [e for e in E if "cmudict:agree" in (e["pronunciation"]["american"].get("checked_by") or "")
            and " " not in e["headword"] and e["pos"] in ("n", "v", "adj", "adv")]
    rng.shuffle(pool)
    seen, items = set(), []
    plan = ["positive"] * 80 + ["stress-shift"] * 27 + ["vowel-swap"] * 27 + ["consonant-voicing"] * 26
    rng.shuffle(plan)
    pi = 0
    for kind in plan:
        while True:
            e = pool[pi]; pi += 1
            if e["headword"] in seen:
                continue
            ipa = e["pronunciation"]["american"]["ipa"]
            alt = {"positive": lambda x: x, "stress-shift": stress_shift, "vowel-swap": vowel_swap,
                   "consonant-voicing": cons_swap}[kind](ipa)
            if alt and (kind == "positive" or not agree(alt, ipa, "american")):
                break
        seen.add(e["headword"])
        items.append({"state": {"word": e["headword"], "part_of_speech": POSNAME[e["pos"]],
                                "ipa_general_american": f"/{alt}/"},
                      "gold": kind == "positive", "kind": kind, "true_ipa": f"/{ipa}/"})
    mark_screen(items, ["positive", "stress-shift", "vowel-swap"])
    return items


# ---------------------------------------------------------------- T2 definitions
def related_slugs(e):
    out = [x["slug"] for x in e.get("see_also") or []]
    for s in e["senses"]:
        out += [x["slug"] for x in s["synonyms"] + s["compare"]]
    return [s for s in out if s in BY and BY[s]["headword"] != e["headword"]]


def build_defs():
    pool = [e for e in E if e["pos"] in ("n", "v", "adj", "adv") and " " not in e["headword"]]
    rng.shuffle(pool)
    with_rel = [e for e in pool if related_slugs(e)]
    items, used = [], set()
    for e in pool[:80]:
        s = rng.choice(e["senses"])
        items.append({"state": {"word": e["headword"], "part_of_speech": POSNAME[e["pos"]],
                                "definition": strip_marks(s["definition"])}, "gold": True, "kind": "positive"})
        used.add(e["slug"])
    rest = [e for e in pool if e["slug"] not in used]
    for e in rest[:40]:
        other = rng.choice([x for x in pool if x["pos"] == e["pos"] and x["headword"] != e["headword"]])
        items.append({"state": {"word": e["headword"], "part_of_speech": POSNAME[e["pos"]],
                                "definition": first_def(other)}, "gold": False, "kind": "random-other-word",
                      "source": other["slug"]})
    hard = [e for e in with_rel if e["slug"] not in used][:40]
    for e in hard:
        r = BY[rng.choice(related_slugs(e))]
        items.append({"state": {"word": e["headword"], "part_of_speech": POSNAME[e["pos"]],
                                "definition": first_def(r)}, "gold": False, "kind": "related-word",
                      "source": r["slug"]})
    rng.shuffle(items)
    mark_screen(items, ["positive", "random-other-word"])
    return items


# ---------------------------------------------------------------- T3 example -> sense
def build_exsense():
    pool = [e for e in E if 3 <= len(e["senses"]) <= 6]
    rng.shuffle(pool)
    items = []
    for e in pool[:150]:
        k = rng.randrange(len(e["senses"]))
        ex = rng.choice(e["senses"][k]["examples"])["text"]
        crit = {f"sense_{i+1}": (f"({s['signpost']}) " if s.get("signpost") else "") + strip_marks(s["definition"])
                for i, s in enumerate(e["senses"])}
        items.append({"state": {"word": e["headword"], "part_of_speech": POSNAME[e["pos"]],
                                "example_sentence": strip_marks(ex)},
                      "criteria": crit, "gold": f"sense_{k+1}", "kind": f"{len(e['senses'])}-senses"})
    for it in items[:10]:
        it["screen"] = True
    for it in items:
        it.setdefault("screen", False)
    return items


# ---------------------------------------------------------------- T4 example acceptability
def word_re(w):
    return re.compile(r"\b" + re.escape(w) + r"\b", re.I)


def build_exok():
    pool = [e for e in E if " " not in e["headword"] and e["pos"] in ("n", "v", "adj")]
    rng.shuffle(pool)
    items, pi = [], 0

    def take():
        nonlocal pi
        e = pool[pi % len(pool)]; pi += 1
        s = rng.choice(e["senses"])
        return e, s, strip_marks(rng.choice(s["examples"])["text"])

    def st(e, s, text):
        return {"word": e["headword"], "part_of_speech": POSNAME[e["pos"]],
                "sense_definition": strip_marks(s["definition"]), "example_sentence": text}

    for _ in range(80):
        e, s, ex = take()
        items.append({"state": st(e, s, ex), "gold": True, "kind": "positive"})
    # wrong verb form
    n = 0
    while n < 27:
        e, s, ex = take()
        if e["pos"] != "v":
            continue
        forms = e["inflections"]["forms"]
        allf = [e["headword"]] + [v for v in forms.values() if isinstance(v, str)]
        hit = [f for f in sorted(set(allf), key=len, reverse=True) if word_re(f).search(ex)]
        if not hit:
            continue
        h = hit[0]
        cands = [f for f in set(allf) if f.lower() != h.lower()]
        if not cands:
            continue
        bad = word_re(h).sub(rng.choice(cands), ex, count=1)
        items.append({"state": st(e, s, bad), "gold": False, "kind": "wrong-verb-form", "original": ex}); n += 1
    # adjacent word swap
    n = 0
    while n < 27:
        e, s, ex = take()
        w = ex.rstrip(".?!").split()
        if len(w) < 5:
            continue
        i = rng.randrange(1, len(w) - 1)
        if w[i].lower() == w[i + 1].lower():
            continue
        w[i], w[i + 1] = w[i + 1], w[i]
        bad = " ".join(w) + ex[-1]
        items.append({"state": st(e, s, bad), "gold": False, "kind": "word-order", "original": ex}); n += 1
    # headword misused: replaced by another word of the same part of speech
    n = 0
    while n < 26:
        e, s, ex = take()
        if not word_re(e["headword"]).search(ex) or e["pos"] == "v":
            continue
        other = rng.choice([x for x in pool if x["pos"] == e["pos"] and x["headword"] != e["headword"]])
        bad = word_re(e["headword"]).sub(other["headword"], ex, count=1)
        # the state still names the headword and sense: the example no longer illustrates it
        items.append({"state": st(e, s, bad), "gold": False, "kind": "wrong-word", "original": ex}); n += 1
    rng.shuffle(items)
    mark_screen(items, ["positive", "word-order"])
    return items


# ---------------------------------------------------------------- T5 cross-reference relevance
def build_xref():
    pairs = [(e, BY[x["slug"]]) for e in E for x in (e.get("see_also") or []) if x["slug"] in BY]
    rng.shuffle(pairs)
    targets = [b for _, b in pairs]
    items, seen = [], set()
    for a, b in pairs:
        if a["slug"] in seen:
            continue
        seen.add(a["slug"])
        items.append((a, b, True, "positive"))
        if len(items) >= 75:
            break
    rest = [a for a, _ in pairs if a["slug"] not in seen]
    rng.shuffle(rest)
    for a in rest:
        if a["slug"] in seen:
            continue
        seen.add(a["slug"])
        rel = set(related_slugs(a)) | {x["slug"] for x in a.get("word_family") or []}
        b = rng.choice([t for t in targets if t["slug"] not in rel and t["headword"] != a["headword"]])
        items.append((a, b, False, "other-entry-link-target"))
        if len(items) >= 150:
            break
    out = [{"state": {"entry_word": a["headword"], "entry_part_of_speech": POSNAME[a["pos"]],
                      "entry_meaning": first_def(a), "linked_word": b["headword"],
                      "linked_part_of_speech": POSNAME[b["pos"]], "linked_meaning": first_def(b)},
            "gold": g, "kind": k} for a, b, g, k in items]
    rng.shuffle(out)
    mark_screen(out, ["positive", "other-entry-link-target"])
    return out


# ---------------------------------------------------------------- T6 link target (homograph / POS)
def build_link():
    groups = collections.defaultdict(list)
    for e in E:
        groups[e["headword"].lower()].append(e)
    groups = {h: g for h, g in groups.items() if len(g) >= 2}
    items = []
    cands = [(h, e) for h, g in groups.items() for e in g]
    rng.shuffle(cands)
    for h, e in cands:
        exs = [strip_marks(x["text"]) for s in e["senses"] for x in s["examples"]]
        # the headword itself (any case) must appear, so the item is about that occurrence
        exs = [x for x in exs if word_re(h).search(x)]
        if not exs:
            continue
        crit = {g["slug"]: f"{h} ({POSNAME[g['pos']]}): " + first_def(g) for g in groups[h]}
        items.append({"state": {"word": h, "sentence": rng.choice(exs)}, "criteria": crit,
                      "gold": e["slug"], "kind": f"{len(groups[h])}-entries"})
        if len(items) >= 150:
            break
    for it in items[:10]:
        it["screen"] = True
    for it in items:
        it.setdefault("screen", False)
    return items


# ---------------------------------------------------------------- T7 reviewer-issue triage
def build_triage():
    dec = {}
    for line in open(ROOT / "reviews/decisions.jsonl"):
        d = json.loads(line)
        if d["decision"] in ("apply", "reject"):
            dec[(d["run_id"], d["slug"], d["field"], d["role"])] = d
    rows = []
    cache = {}
    for (run, slug, field, role), d in dec.items():
        p = ROOT / "reviews" / run / f"{slug}.json"
        if not p.exists():
            continue
        if p not in cache:
            cache[p] = json.load(open(p))
        for rv in cache[p].get("reviewers", []):
            if rv["role"] != role:
                continue
            for v in rv.get("verdicts", []):
                if v["field"] == field and v["verdict"] != "ok" and v.get("reason"):
                    rows.append((d, v))
                    break
    seen, uniq = set(), []
    for d, v in rows:
        k = (d["slug"], d["field"], v["reason"])
        if k not in seen:
            seen.add(k); uniq.append((d, v))
    rng.shuffle(uniq)
    app = [r for r in uniq if r[0]["decision"] == "apply"][:100]
    rej = [r for r in uniq if r[0]["decision"] == "reject"][:100]
    items = []
    for d, v in app + rej:
        e = BY.get(d["slug"])
        items.append({"state": {"word": e["headword"] if e else d["slug"],
                                "part_of_speech": POSNAME.get(e["pos"], e["pos"]) if e else None,
                                "field": d["field"], "quoted_text": strip_marks(v.get("quote") or ""),
                                "reviewer_objection": strip_marks(v["reason"]),
                                "reviewer_severity": v.get("severity")},
                      "gold": d["decision"] == "apply", "kind": d["family"] or "other",
                      "role": d["role"]})
    rng.shuffle(items)
    for it in items:
        it["screen"] = False
    return items


# ---------------------------------------------------------------- T8 countability
def build_count():
    by = collections.defaultdict(list)
    for e in E:
        if e["pos"] != "n":
            continue
        for s in e["senses"]:
            c = (s.get("grammar") or {}).get("countability")
            if c:
                by[c].append((e, s))
    items = []
    for c, lst in sorted(by.items()):
        rng.shuffle(lst)
        for e, s in lst[:30]:
            exs = [strip_marks(x["text"]) for x in s["examples"][:3]]
            items.append({"state": {"noun": e["headword"], "sense_definition": strip_marks(s["definition"]),
                                    "example_sentences": exs},
                          "gold": c, "kind": c})
    rng.shuffle(items)
    mark_screen(items, ["countable", "uncountable", "plural only", "singular only", "countable or uncountable"])
    return items


if __name__ == "__main__":
    write("pron", build_pron())
    write("defs", build_defs())
    write("exsense", build_exsense())
    write("exok", build_exok())
    write("xref", build_xref())
    write("link", build_link())
    write("triage", build_triage())
    write("count", build_count())
