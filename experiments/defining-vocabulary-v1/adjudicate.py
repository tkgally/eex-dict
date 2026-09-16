#!/usr/bin/env python3
"""Settle the defining vocabulary from proposals.tsv (wiki/decisions/defining-vocabulary.md).

Core = every lemma proposed by at least two of the three models. Single-vote
lemmas were read one by one by the founding session and accepted only when
general enough to serve in definitions (ACCEPT_SINGLES below; everything else
proposed once is left for the band passes). GAPS adds function words, light
verbs, and defining metalanguage the session found missing. British spellings
are replaced by the American headword (AMERICAN). Writes:

  schema/defining-vocabulary.txt   one lemma per line, sorted
  band1-rows.tsv                   queue rows (headword, pos, band, source, note) for every lemma and its parts of speech

    python3 experiments/defining-vocabulary-v1/adjudicate.py
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

ACCEPT_SINGLES = set("""
ok
active actual automatic available average bent blunt bold brief brown central chemical commercial connected convenient cooked crowded curious curly current delicious digital disappointed dishonest distant divorced drunk economic effective elderly electric electronic emotional exact expert familiar financial fine following foolish formal former frequent frozen full-time gold helpful hidden impatient individual indoor industrial informal interested international living logical loyal magic mechanical medical messy modest national nearby negative obvious occasional odd online orange outdoor paid painful part-time perfect permanent pink pleasant positive powerful proper pure purple quick reasonable recent satisfied secret sensible sensitive separate silent silver skilled slim slippery specific spicy spiritual spoken strict suitable surprised temporary terrible tough typical unfair unlikely used useless visible wealthy wonderful worn worried written
abroad absolutely ahead basically briefly closely commonly correctly downstairs effectively else eventually extremely fairly forever fortunately greatly highly honestly largely merely necessarily perfectly personally possibly properly regularly safely seldom similarly specially strangely terribly thus totally truly unfortunately upstairs widely wrongly
mid- multi- self-
an several these those whatever
thanks congratulations
dare ought
accent acid activity address adjective advantage aim alarm alphabet angle apartment ash attempt author bacteria bark basis battery battle beach beard bee bench berry bicycle birthday bit blade blame blanket block bomb breath broom bucket bug cabinet cable candy capital card career cartoon cat cattle cave ceiling cell chain chapter claim client climate club code colleague college color computer concert conclusion conflict container contest contract cotton council course cow crack creature cry cupboard custom deal debate delay demand democracy department description desert design destruction detail development device dictionary difficulty disability disadvantage disappointment discovery disgust display dog download drill drum economy effort electricity email enjoyment entrance equality equipment escape exchange exit fabric faith fan fashion fence festival figure file finance flame flavor flight flood fog folder fool fridge frost frown fuel gain garage gear gender germ glue governor grammar greeting grief guide hay hearing herb highway hole holiday honey hotel image improvement income industry influence intelligence internet issue item jail jewel joint judgment jungle jury keyboard knee knock laboratory lane laugh laundry lawyer layer leisure lever lid lightning link lip lot machine mass mayor measurement menu mouse movement movie murder museum nest network noun nut offer officer opportunity organ owner pair paragraph parking passion password pattern pause payment personality pest pet pharmacy photograph pilot pipe pity platform plug plural poison pool possibility potato priest print printer prisoner profession program progress promise pronoun pronunciation protest pulse radio rail range reader recipe record recovery relief rent report representative republic restaurant retirement rug ruin sauce scar scene schedule scissors scratch search seller server shake sheet shell sidewalk silk similarity singular smile snack snake socket sofa software sort soul spark speaker speech spice spirit spread standard statement stem step straw stress strike stroke structure stuff suggestion supper surgery survival suspicion switch tap task technology teenager telephone tense term texture theater theft thief threat throat thunder tissue tool topic tower training trap trick trouble truck tunnel twin twist underwear uniform university upload user vein verb victim video village virus washing machine waterfall wealth web website widow winner wisdom witness writer
absorb adopt advertise apologize bind borrow bury calculate celebrate collect communicate compete conclude consist count crush decay delete deliver depend develop disappear disappoint discuss dislike dissolve divide encourage entertain expand express fasten float govern hide hug improve inform install kick kiss leak lend multiply obey occur praise pronounce quit reduce refer reflect remind require rob satisfy sew shut slice smash spill stick stir strengthen strip subtract suffer suggest survive suspect swell threaten tire translate unlock wait weaken wonder
bring about bring back calm down carry out clear up come on come out come up with consist of cut down figure out get away get in get off get on get out get over go away go over go through hand over hang up lead to leave out listen to look out look up move in move out pass away pass on put back put off put together put up result in run away set off shut up speed up split up stand for start over take apart take away take back take place think about think of turn down turn into turn over turn up wash up
anybody anyone anything everybody everyone everything hers herself himself itself mine myself nobody nothing ours ourselves somebody theirs themselves yours yourself
-dom -ed -ic -ify -ing -like -ward -wise -y
en- semi-
including plus minus such as
for example in fact
""".split("\n"))
ACCEPT_SINGLES = {w.strip() for line in ACCEPT_SINGLES for w in [line] if w.strip()}
# multi-word items are listed one per line above only when they contain spaces; rebuild from the block:
_BLOCK = __doc__  # noqa: F841 (kept for readers)


def parse_accept(text: str) -> set[str]:
    out = set()
    multi = ["washing machine", "such as", "for example", "in fact", "bring about", "bring back", "calm down", "carry out",
             "clear up", "come on", "come out", "come up with", "consist of", "cut down", "figure out", "get away", "get in",
             "get off", "get on", "get out", "get over", "go away", "go over", "go through", "hand over", "hang up", "lead to",
             "leave out", "listen to", "look out", "look up", "move in", "move out", "pass away", "pass on", "put back",
             "put off", "put together", "put up", "result in", "run away", "set off", "shut up", "speed up", "split up",
             "stand for", "start over", "take apart", "take away", "take back", "take place", "think about", "think of",
             "turn down", "turn into", "turn over", "turn up", "wash up"]
    for m in multi:
        if m in text:
            out.add(m)
            text = text.replace(m, " ")
    out |= {w for w in text.split() if w}
    return out


AMERICAN = {"centre": "center", "cheque": "check", "humour": "humor", "neighbour": "neighbor",
            "neighbourhood": "neighborhood", "theatre": "theater", "grey": "gray", "colour": "color",
            "favourite": "favorite", "programme": "program", "metre": "meter", "litre": "liter",
            "travelling": "traveling", "behaviour": "behavior", "flavour": "flavor", "honour": "honor", "labour": "labor", "organise": "organize", "realise": "realize", "recognise": "recognize"}

GAPS = {  # lemma -> pos, added after checking the core for function words, light verbs, and defining metalanguage
    "a": "det", "an": "det", "the": "det", "this": "det", "that": "det", "these": "det", "those": "det",
    "i": "pron", "you": "pron", "he": "pron", "she": "pron", "it": "pron", "we": "pron", "they": "pron",
    "me": "pron", "him": "pron", "her": "pron", "us": "pron", "them": "pron", "one": "pron",
    "my": "det", "your": "det", "his": "det", "its": "det", "our": "det", "their": "det",
    "who": "pron", "whom": "pron", "whose": "det", "what": "pron", "which": "pron", "when": "adv", "where": "adv",
    "why": "adv", "how": "adv", "whether": "conj", "if": "conj", "because": "conj", "although": "conj", "though": "conj",
    "but": "conj", "and": "conj", "or": "conj", "so": "conj", "than": "conj", "as": "conj", "while": "conj",
    "unless": "conj", "until": "conj", "since": "conj", "once": "conj", "nor": "conj", "yet": "conj",
    "be": "v", "have": "v", "do": "v", "get": "v", "make": "v", "take": "v", "give": "v", "put": "v", "go": "v",
    "come": "v", "keep": "v", "let": "v", "seem": "v", "become": "v", "use": "v", "cause": "v", "mean": "v",
    "can": "modal", "could": "modal", "may": "modal", "might": "modal", "must": "modal", "shall": "modal",
    "should": "modal", "will": "modal", "would": "modal", "ought": "modal", "need": "v", "dare": "modal", "used to": "modal",
    "not": "adv", "no": "det", "yes": "interj", "very": "adv", "too": "adv", "also": "adv", "only": "adv", "just": "adv",
    "even": "adv", "still": "adv", "already": "adv", "ever": "adv", "never": "adv", "always": "adv", "often": "adv",
    "sometimes": "adv", "usually": "adv", "especially": "adv", "particularly": "adv", "mainly": "adv", "generally": "adv",
    "someone": "pron", "something": "pron", "somewhere": "adv", "anywhere": "adv", "nowhere": "adv", "everywhere": "adv",
    "thing": "n", "kind": "n", "type": "n", "way": "n", "part": "n", "person": "n", "people": "n", "place": "n",
    "time": "n", "amount": "n", "number": "n", "group": "n", "form": "n", "state": "n", "quality": "n", "fact": "n",
    "particular": "adj", "certain": "adj", "similar": "adj", "opposite": "adj", "same": "adj", "different": "adj",
    "relate": "v", "involve": "v", "connect": "v", "describe": "v", "refer": "v", "express": "v", "show": "v",
    "able": "adj", "possible": "adj", "likely": "adj", "necessary": "adj", "usual": "adj", "general": "adj",
    "in": "prep", "on": "prep", "at": "prep", "to": "prep", "of": "prep", "for": "prep", "with": "prep", "by": "prep",
    "from": "prep", "about": "prep", "into": "prep", "through": "prep", "between": "prep", "among": "prep",
    "without": "prep", "within": "prep", "during": "prep", "before": "prep", "after": "prep", "against": "prep",
    "toward": "prep", "across": "prep", "along": "prep", "around": "prep", "over": "prep", "under": "prep",
    "above": "prep", "below": "prep", "near": "prep", "off": "prep", "out": "adv", "up": "adv", "down": "adv",
    "instead": "adv", "rather": "adv", "quite": "adv", "almost": "adv", "enough": "adv", "either": "det", "neither": "det",
    "each": "det", "every": "det", "all": "det", "both": "det", "any": "det", "some": "det", "much": "det", "many": "det",
    "few": "det", "little": "det", "other": "det", "another": "det", "such": "det", "own": "adj", "else": "adv",
}


def main() -> int:
    rows = list(csv.DictReader((HERE / "proposals.tsv").open(encoding="utf-8"), delimiter="\t"))
    maxv: dict[str, int] = defaultdict(int)
    poses: dict[str, dict[str, int]] = defaultdict(dict)
    for r in rows:
        w = AMERICAN.get(r["word"], r["word"])
        maxv[w] = max(maxv[w], int(r["votes"]))
        poses[w][r["pos"]] = max(poses[w].get(r["pos"], 0), int(r["votes"]))
    accept = parse_accept(" ".join(ACCEPT_SINGLES))
    core = {w for w, v in maxv.items() if v >= 2}
    singles_in = {w for w, v in maxv.items() if v == 1 and w in accept}
    unknown_accepts = accept - set(maxv)
    dv = core | singles_in
    gaps_added = {w for w in GAPS if w not in dv}
    dv |= gaps_added
    for w, p in GAPS.items():
        poses[w].setdefault(p, 0)
    # British forms never survive as headwords; abbreviations are headwords (band 1) but not defining words
    dv = {AMERICAN.get(w, w) for w in dv}
    abbr_only = {w for w in dv if poses.get(w) and set(poses[w]) == {"abbr"}}
    dv -= abbr_only
    out = ROOT / "schema" / "defining-vocabulary.txt"
    lines = ["# The defining vocabulary of the TKG English Learner's Dictionary: one lemma per line.",
             "# Built from three models' judgment and settled by the founding session on 2026-09-16;",
             "# method and counts in wiki/decisions/defining-vocabulary.md. No external list was consulted.",
             "# Closed: additions and removals are logged decisions."]
    lines += sorted(dv)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    # queue rows: every lemma with each part of speech that had at least two votes, else its best single
    qrows = []
    for w in sorted(dv | abbr_only):
        pv = poses.get(w, {})
        if not pv:
            continue
        chosen = [p for p, v in pv.items() if v >= 2] or [max(pv, key=pv.get)]
        for p in sorted(chosen):
            src = "defining"
            note = f"votes {pv[p]}" if pv[p] else "gap fill"
            qrows.append([w, p, "1", src, note])
    with (HERE / "band1-rows.tsv").open("w", encoding="utf-8") as f:
        f.write("headword\tpos\tband\tsource\tnote\n")
        for r in qrows:
            f.write("\t".join(r) + "\n")
    print(f"core (2+ votes): {len(core)}; accepted singles: {len(singles_in)} of {sum(1 for v in maxv.values() if v == 1)}; "
          f"gaps added: {len(gaps_added)} ({', '.join(sorted(gaps_added))}); abbreviations kept for the queue only: {len(abbr_only)}; defining vocabulary: {len(dv)} lemmas; "
          f"band-1 queue rows: {len(qrows)}")
    if unknown_accepts:
        print("accepted words not in proposals (check spelling):", sorted(unknown_accepts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
