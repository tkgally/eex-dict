#!/usr/bin/env python3
"""Copy ten reviewed entries into inputs/ with known defects planted (the answer key is planted.json).
The real entries in entries/ are not touched."""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def load(slug):
    p = subprocess.run([sys.executable, str(ROOT / "tools/entry_path.py"), slug], capture_output=True, text=True, cwd=ROOT).stdout.strip()
    return json.loads((ROOT / p).read_text())

def rep(s, old, new):
    assert old in s, (old, s[:200])
    return s.replace(old, new, 1)

KEY = []
def plant(slug, field, family, desc, fn):
    KEY.append({"id": f"{slug}#{sum(1 for k in KEY if k['slug']==slug)+1}", "slug": slug, "field": field, "family": family, "defect": desc})
    fn()

E = {}
for s in "local-adj home-adv although-conj few-det must-modal iron-n fabric-n turn-off-phrv behind-prep compare-v".split():
    E[s] = load(s)

def ex(slug, i, old, new):
    for x in E[slug]["senses"][i]["examples"]:
        if x["text"] == old:
            x["text"] = new; return
    raise AssertionError((slug, old))

e = E["local-adj"]
plant("local-adj", "senses[0].examples", "example-grammar", "subject-verb agreement error 'Our children goes'",
      lambda: ex("local-adj", 0, "Our children go to the local school.", "Our children goes to the local school."))
plant("local-adj", "senses[1].examples", "example-policy", "checkable real-world fact (date, statistic) in an example",
      lambda: ex("local-adj", 1, "Local elections are held next spring.", "Local elections were held on May 5, 2022, and only 31 percent of voters took part."))
plant("local-adj", "senses[2].definition", "definition-meaning", "definition reversed: 'the whole body' instead of one part",
      lambda: e["senses"][2].update(definition="affecting the whole body, not only one part"))

e = E["home-adv"]
plant("home-adv", "pronunciation.american", "pronunciation", "wrong American IPA /hum/",
      lambda: e["pronunciation"]["american"].update(ipa="hum"))
plant("home-adv", "learner_errors", "learner-error", "the 'correct' form is wrong: 'went back to the home'",
      lambda: e["learner_errors"][1].update(correct="She went back to the home."))
plant("home-adv", "senses[0].definition", "definition-style", "padding 'used to describe the act of' in a content-word definition",
      lambda: e["senses"][0].update(definition="used to describe the act of going to or being at the place where you live"))

e = E["although-conj"]
plant("although-conj", "synonym_discrimination", "synonym-discrimination", "register reversed: says although is more common in speech, though more formal",
      lambda: e["synonym_discrimination"].update(note=rep(e["synonym_discrimination"]["note"], "**though** is more common in speech, and **although** is a little more formal", "**although** is more common in speech, and **though** is a little more formal")))
plant("although-conj", "senses[0].examples", "example-grammar", "'Although ..., but ...' error inside an example",
      lambda: ex("although-conj", 0, "Although she was tired, she stayed up to help.", "Although she was tired, but she stayed up to help."))
plant("although-conj", "etymology", "etymology", "false etymology from Latin alter through French",
      lambda: e.update(etymology="From the Latin word *alter*, meaning other, which came into English through French."))

e = E["few-det"]
plant("few-det", "senses[0].definition", "definition-meaning", "says uncountable noun / not much instead of plural noun / not many",
      lambda: e["senses"][0].update(definition="used before an uncountable noun to mean not much, less than expected or wanted"))
plant("few-det", "senses[1].examples", "example-grammar", "'a few money'",
      lambda: ex("few-det", 1, "Could I borrow a few dollars?", "Could I borrow a few money?"))
plant("few-det", "usage_note", "usage-note", "comparative/superlative given as less/least",
      lambda: e.update(usage_note=rep(e["usage_note"], "The comparative of **few** is **fewer**, and the superlative is **fewest**: *fewer people*, *the fewest mistakes*", "The comparative of **few** is **less**, and the superlative is **least**: *less people*, *the least mistakes*")))

e = E["must-modal"]
plant("must-modal", "senses[0].grammar", "grammar-code", "pattern 'verb + to-infinitive' for must",
      lambda: e["senses"][0]["grammar"].update(patterns=["verb + to-infinitive"]))
plant("must-modal", "senses[1].examples", "example-unnatural", "obligation example placed under the 'almost certainly true' sense (examples_fit)",
      lambda: e["senses"][1]["examples"].append({"text": "You must hand in your homework by Friday.", "note": None, "pattern": "verb + bare infinitive"}))
plant("must-modal", "usage_note", "spelling-or-format", "abbreviation 'e.g.' in prose",
      lambda: e.update(usage_note=rep(e["usage_note"], "use **had to** for the past", "use **had to** for the past, e.g. *I had to leave early*")))

e = E["iron-n"]
plant("iron-n", "pronunciation.american", "pronunciation", "wrong American IPA ˈɪ.rɑn",
      lambda: e["pronunciation"]["american"].update(ipa="ˈɪ.rɑn"))
plant("iron-n", "senses[0].examples", "example-policy", "science fact (melting point) in an example",
      lambda: ex("iron-n", 0, "Iron rusts if you leave it out in the rain.", "Iron melts at 1,538 degrees Celsius."))
plant("iron-n", "phrases[1].definition", "phrase", "'strike while the iron is hot' defined as waiting until things are calm",
      lambda: e["phrases"][1].update(definition="wait until a situation becomes calm before you do something"))

e = E["fabric-n"]
plant("fabric-n", "senses[0].collocations", "collocation", "untypical collocation 'tall fabric'",
      lambda: e["senses"][0]["collocations"][0].update(items=["cotton fabric", "soft fabric", "tall fabric", "light fabric"]))
plant("fabric-n", "senses[0].adaptation", "adaptation", "adaptation note names specific languages",
      lambda: e["senses"][0]["adaptation"].update(false_friends="In Spanish and Portuguese, the word that looks like **fabric** means a factory."))
plant("fabric-n", "senses[0].definition", "definition-vocabulary", "hard defining words: interlacing filaments, warp and weft",
      lambda: e["senses"][0].update(definition="material made by interlacing filaments through warp and weft, used for making clothes, curtains, and other things"))

e = E["turn-off-phrv"]
plant("turn-off-phrv", "learner_errors", "learner-error", "incorrect and correct swapped for the pronoun-position error",
      lambda: e["learner_errors"][1].update(incorrect="Can you turn it off?", correct="Can you turn off it?"))
plant("turn-off-phrv", "senses[0].cross_references", "cross-reference", "antonym switch-on listed as a synonym",
      lambda: e["senses"][0]["synonyms"].append({"slug": "switch-on-phrv", "note": None}))
plant("turn-off-phrv", "senses[2].labels", "label", "register 'formal' on the informal 'make someone bored' sense",
      lambda: e["senses"][2]["labels"].update(register=["formal"]))

e = E["behind-prep"]
plant("behind-prep", "senses[0].examples", "example-unnatural", "unnatural wording 'located in the behind position of the store'",
      lambda: ex("behind-prep", 0, "There's a parking lot behind the store.", "There is a parking lot that is located in the behind position of the store."))
plant("behind-prep", "headword_and_pos", "sense-structure", "adverb use 'left his keys behind' as an example of the preposition",
      lambda: e["senses"][1]["examples"].append({"text": "He left his keys behind.", "note": None, "pattern": None}))
plant("behind-prep", "senses[2].definition", "spelling-or-format", "abbreviations sb/sth in a definition",
      lambda: e["senses"][2].update(definition="giving support or encouragement to sb or sth"))

e = E["compare-v"]
plant("compare-v", "senses[2].grammar", "grammar-code", "transitivity 'transitive' on the intransitive 'compare with' sense",
      lambda: e["senses"][2]["grammar"].update(transitivity="transitive"))
plant("compare-v", "usage_note", "usage-note", "false claim that only 'compare with' is correct for 'say similar'",
      lambda: e.update(usage_note=rep(e["usage_note"], "In the sense *say similar*, **compare to** is more usual: *she compared the city to a garden*.", "In the sense *say similar*, only **compare with** is correct; **compare to** is a mistake.")))
plant("compare-v", "senses[0].examples", "example-policy", "brand names in an example",
      lambda: ex("compare-v", 0, "We compared prices at three different stores.", "We compared prices at Walmart and Target."))

if __name__ == "__main__":
    for s, entry in E.items():
        entry["provenance"]["status"] = "draft"
        (HERE / "inputs" / f"{s}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n")
    (HERE / "planted.json").write_text(json.dumps(KEY, ensure_ascii=False, indent=1) + "\n")
    print(len(KEY), "defects planted in", len(E), "entries")
