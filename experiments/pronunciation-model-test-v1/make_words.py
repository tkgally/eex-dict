#!/usr/bin/env python3
"""Build words.tsv for the pronunciation model test from the strata fixed in design.md.

    python3 experiments/pronunciation-model-test-v1/make_words.py

Reads schema/defining-vocabulary.txt (with parts of speech from
experiments/defining-vocabulary-v1/proposals.tsv) and
experiments/defining-vocabulary-v1/bands.tsv. The rare, heteronym, and loanword
strata are the fixed lists below, written from the session's own knowledge; no
external list was consulted.
"""
from __future__ import annotations

import csv
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 20260916
BRITISH = {"tyre", "colour", "centre", "theatre", "cheque", "grey", "harbour", "neighbour", "neighbourhood", "flavour",
           "humour", "behaviour", "programme", "metre", "litre", "favourite", "jewellery", "pyjamas", "mum", "storey"}

RARE = """abstruse adj|sesquipedalian adj|obfuscate v|perspicacious adj|ubiquitous adj|ephemeral adj|
quixotic adj|sycophant n|obsequious adj|recalcitrant adj|truculent adj|pusillanimous adj|
vicissitude n|pulchritude n|somnambulist n|lachrymose adj|verisimilitude n|anathema n|
antediluvian adj|apotheosis n|cacophony n|chicanery n|denouement n|disingenuous adj|
egregious adj|epitome n|hegemony n|hyperbole n|idiosyncrasy n|ignominious adj|
inchoate adj|insouciant adj|juxtapose v|lugubrious adj|magnanimous adj|mellifluous adj|
mendacious adj|nefarious adj|obstreperous adj|onomatopoeia n|ostentatious adj|paradigm n|
parsimonious adj|pejorative adj|penultimate adj|perfunctory adj|plethora n|prevaricate v|
prescient adj|propitious adj|querulous adj|quintessential adj|recondite adj|redoubtable adj|
sanguine adj|scintillating adj|serendipity n|soporific adj|surreptitious adj|taciturn adj|
tenebrous adj|trepidation n|ubiquity n|unctuous adj|vacillate v|vociferous adj|
zealot n|abrogate v|acquiesce v|beleaguered adj|blandishment n|cognizant adj|
conflagration n|debilitate v|deleterious adj|desultory adj|diaphanous adj|effervescent adj|
enervate v|equanimity n|exacerbate v|facetious adj|garrulous adj|halcyon adj|
iconoclast n|impecunious adj|inexorable adj|intransigent adj|irascible adj|laconic adj|
loquacious adj|misanthrope n|nonchalant adj|obdurate adj|peremptory adj|phlegmatic adj|
pontificate v|sagacious adj|supercilious adj|tantamount adj"""

HETERONYMS = """record n|record v|lead n|lead v|minute n|minute adj|read v|wind n|wind v|
tear n|tear v|bow n|bow v|live v|live adj|close v|close adj|present n|present v|
object n|object v|permit n|permit v|produce n|produce v|project n|project v|
content n|content adj|contest n|contest v|desert n|desert v|conduct n|conduct v|
refuse n|refuse v|rebel n|rebel v|subject n|subject v|suspect n|suspect v|
wound n|use n|use v|house n|house v|excuse n|excuse v|separate v|separate adj|
moderate v|moderate adj|estimate n|estimate v|graduate n|graduate v|invalid n|invalid adj|
polish n|bass n|dove n|row n|sow v|does v|axes n|buffet n|resume v|entrance n|entrance v|
console n|console v|convict n|convict v|digest n|digest v|escort n|escort v|insult n|insult v|
perfect adj|perfect v|progress n|progress v|address n|address v|attribute n|attribute v|
increase n|increase v|import n|import v|export n|export v|insert n|insert v|
rebel n|survey n|survey v|upset adj|upset v|combine n|combine v|compound n|compound v"""

LOAN = """croissant n|genre n|entrepreneur n|karaoke n|tsunami n|jalapeno n|faux pas n|deja vu n|
rendezvous n|bourgeois adj|chic adj|cliche n|debut n|facade n|niche n|cache n|quiche n|
ballet n|buffet v|gourmet n|coup n|corps n|pizza n|sushi n|kimono n|karate n|feng shui n|
yoga n|guru n|avatar n|safari n|samurai n|machiavellian adj|sandwich n|boycott v|
pasteurize v|quixotic adj|platonic adj|herculean adj|draconian adj|cardigan n|diesel n|
watt n|volt n|guillotine n|saxophone n|braille n|mesmerize v|galvanize v|silhouette n|
leotard n|nicotine n|shrapnel n|bikini n|denim n|marathon n|paparazzi n|lingerie n|
espresso n|schadenfreude n"""


def parse_fixed(text: str, n: int, seen: set) -> list[tuple[str, str]]:
    items = []
    for chunk in text.replace("\n", "").split("|"):
        chunk = chunk.strip()
        if not chunk:
            continue
        w, pos = chunk.rsplit(" ", 1)
        key = (w, pos)
        if key in seen:
            continue
        seen.add(key)
        items.append(key)
    if len(items) < n:
        print(f"warning: fixed list has {len(items)} items, wanted {n}", file=sys.stderr)
    return items[:n]


def main() -> int:
    rng = random.Random(SEED)
    dv = [w.strip() for w in (ROOT / "schema/defining-vocabulary.txt").read_text(encoding="utf-8").splitlines()
          if w.strip() and not w.startswith("#")]
    pos_of: dict[str, list[str]] = defaultdict(list)
    best_pos: dict[str, tuple[int, str]] = {}
    with (ROOT / "experiments/defining-vocabulary-v1/proposals.tsv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            if int(row["votes"]) >= 2:
                pos_of[row["word"]].append(row["pos"])
            v = int(row["votes"])
            if v > best_pos.get(row["word"], (0, ""))[0]:
                best_pos[row["word"]] = (v, row["pos"])
    dv_items = []
    for w in dv:
        if len(w) < 2 or w.startswith("-") or w.endswith("-") or " " in w:
            continue
        poses = pos_of.get(w) or ["n"]
        dv_items.append((w, sorted(poses, key=lambda p: ["n", "v", "adj", "adv"].index(p) if p in ("n", "v", "adj", "adv") else 9)[0]))
    # stratify by pos in proportion
    by_pos: dict[str, list] = defaultdict(list)
    for w, p in dv_items:
        by_pos[p].append((w, p))
    total = len(dv_items)
    defining = []
    for p, items in sorted(by_pos.items()):
        k = round(200 * len(items) / total)
        rng.shuffle(items)
        defining.extend(items[:k])
    defining = defining[:200]
    while len(defining) < 200:
        cand = rng.choice(dv_items)
        if cand not in defining:
            defining.append(cand)
    # the stratification above used "n" for single-vote lemmas (a slip in the first run of this
    # script, kept so the sample stays the same); relabel each sampled word with its best-voted part of speech
    defining = [(w, best_pos.get(w, (0, p))[1]) for w, p in defining]
    seen = set(defining)
    mid_pool = []
    with (ROOT / "experiments/defining-vocabulary-v1/bands.tsv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            key = (row["word"], row["pos"])
            if row["word"] in BRITISH:
                continue
            if row["band_median"] in ("2", "3") and key not in seen and " " not in row["word"] and row["word"] not in dv:
                mid_pool.append(key)
    rng.shuffle(mid_pool)
    mid = mid_pool[:100]
    seen |= set(mid)
    rare = parse_fixed(RARE, 100, seen)
    het = parse_fixed(HETERONYMS, 50, set())  # heteronyms may repeat a word with another pos on purpose
    seen |= set(het)
    loan = parse_fixed(LOAN, 50, seen)
    rows = [(w, p, "defining") for w, p in defining] + [(w, p, "mid") for w, p in mid] + \
           [(w, p, "rare") for w, p in rare] + [(w, p, "heteronym") for w, p in het] + [(w, p, "loan") for w, p in loan]
    with (HERE / "words.tsv").open("w", encoding="utf-8") as f:
        f.write("word\tpos\tstratum\n")
        for w, p, s in rows:
            f.write(f"{w}\t{p}\t{s}\n")
    print({s: sum(1 for r in rows if r[2] == s) for s in ("defining", "mid", "rare", "heteronym", "loan")}, "total", len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
