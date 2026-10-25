#!/usr/bin/env python3
"""The harder planted set: ten more reviewed entries, two subtle defects each, appended to planted.json
with "set": "subtle" (plant.py's thirty are the "obvious" set). The real entries are not touched."""
import json
from plant import HERE, load, rep

KEY = [k for k in json.loads((HERE / "planted.json").read_text()) if k.get("set") != "subtle"]
for k in KEY:
    k["set"] = "obvious"
E = {s: load(s) for s in "pregnant-adj manager-n leak-v arrange-v also-adv since-conj ought-modal look-up-phrv during-prep record-v".split()}
n = {}

def plant(slug, field, family, desc, fn):
    n[slug] = n.get(slug, 0) + 1
    KEY.append({"id": f"{slug}#{n[slug]}", "slug": slug, "field": field, "family": family, "defect": desc, "set": "subtle"})
    fn()

def ex(slug, i, old, new):
    for x in E[slug]["senses"][i]["examples"]:
        if x["text"] == old:
            x["text"] = new; return
    raise AssertionError((slug, old))

def col(slug, i, typ, old, new):
    for c in E[slug]["senses"][i]["collocations"]:
        if c["type"] == typ and old in c["items"]:
            c["items"][c["items"].index(old)] = new; return
    raise AssertionError((slug, old))

e = E["pregnant-adj"]
plant("pregnant-adj", "senses[0].collocations", "collocation", "'strongly pregnant' for 'heavily pregnant'",
      lambda: col("pregnant-adj", 0, "adverb + adjective", "heavily pregnant", "strongly pregnant"))
plant("pregnant-adj", "pronunciation.british", "pronunciation", "unreduced second vowel ˈpreɡ.nænt",
      lambda: e["pronunciation"]["british"].update(ipa="ˈpreɡ.nænt"))
plant("manager-n", "senses[0].examples", "example-unnatural", "'promoted to a manager' (idiom is 'promoted to manager')",
      lambda: ex("manager-n", 0, "She was promoted to manager last year.", "She was promoted to a manager last year."))
plant("manager-n", "senses[0].collocations", "collocation", "'a high manager' for senior/top manager",
      lambda: col("manager-n", 0, "adjective + noun", "a senior manager", "a high manager"))
e = E["leak-v"]
plant("leak-v", "senses[2].definition", "definition-meaning", "'usually by mistake': leaking secrets is usually deliberate",
      lambda: e["senses"][2].update(definition="give secret information to newspapers or to the public, usually by mistake, or become known in this way"))
plant("leak-v", "senses[0].examples", "example-grammar", "impossible passive 'The roof was leaked by the rain'",
      lambda: e["senses"][0]["examples"].append({"text": "The roof was leaked by the rain.", "note": "passive", "pattern": "verb + object"}))
e = E["arrange-v"]
plant("arrange-v", "senses[0].examples", "example-grammar", "'arranged meeting her' (arrange takes a to-infinitive, not -ing)",
      lambda: ex("arrange-v", 0, "I've arranged to meet her at noon.", "I've arranged meeting her at noon."))
plant("arrange-v", "senses[1].grammar", "grammar-code", "pattern 'verb + -ing form' added to the 'put in order' sense",
      lambda: e["senses"][1]["grammar"]["patterns"].append("verb + -ing form"))
e = E["also-adv"]
plant("also-adv", "learner_errors", "learner-error", "note says also comes before be, contradicting its own correction",
      lambda: e["learner_errors"][1].update(note=rep(e["learner_errors"][1]["note"], "comes after **be** but before other main verbs", "comes before **be** and before other main verbs")))
plant("also-adv", "senses[0].examples", "example-grammar", "word order 'Kim wants also to come'",
      lambda: ex("also-adv", 0, "Kim also wants to come.", "Kim wants also to come."))
e = E["since-conj"]
plant("since-conj", "learner_errors", "learner-error", "correction is still wrong: 'I am living here since I was ten'",
      lambda: e["learner_errors"][0].update(correct="I am living here since I was ten."))
plant("since-conj", "senses[0].examples", "example-grammar", "'since I have last seen him' (since-clause takes the past simple)",
      lambda: ex("since-conj", 0, "It's been two years since I last saw him.", "It's been two years since I have last seen him."))
e = E["ought-modal"]
plant("ought-modal", "senses[0].examples", "example-grammar", "nonstandard 'You don't ought to speak to her like that'",
      lambda: ex("ought-modal", 0, "You oughtn't to speak to her like that.", "You don't ought to speak to her like that."))
plant("ought-modal", "usage_note", "usage-note", "false frequency claim: ought to more common than should in American speech",
      lambda: e.update(usage_note=rep(e["usage_note"], "feels more formal and moralistic and is much less frequent; most everyday speech uses **should** for both advice and probability", "is more common than **should** in everyday American speech, and **should** sounds more formal")))
e = E["look-up-phrv"]
plant("look-up-phrv", "senses[0].cross_references", "cross-reference", "look for given as a synonym of look up (information)",
      lambda: e["senses"][0]["synonyms"].append({"slug": "look-for-phrv", "note": None}))
plant("look-up-phrv", "pronunciation.american", "pronunciation", "main stress moved from the particle to the verb: ˈlʊk ˌʌp",
      lambda: e["pronunciation"]["american"].update(ipa="ˈlʊk ˌʌp"))
e = E["during-prep"]
plant("during-prep", "senses[0].examples", "example-grammar", "'during three hours' (a length of time needs for), contradicting its own learner error",
      lambda: ex("during-prep", 0, "I felt sick during the flight.", "I felt sick during three hours."))
plant("during-prep", "usage_note", "usage-note", "false claim that during can take a clause with its own subject",
      lambda: e.update(usage_note=rep(e["usage_note"], "is followed by a noun (*during the movie*)", "is followed by a noun or by a clause with its own subject (*during the movie*, *during we were eating*)")))
e = E["record-v"]
plant("record-v", "pronunciation.american", "pronunciation", "noun stress ˈrɛk.ɚd on the verb, contradicting its own usage note",
      lambda: e["pronunciation"]["american"].update(ipa="ˈrɛk.ɚd"))
plant("record-v", "senses[1].collocations", "collocation", "'record a photo' (one takes a photo)",
      lambda: col("record-v", 1, "verb + noun", "record a video", "record a photo"))

for s, entry in E.items():
    entry["provenance"]["status"] = "draft"
    (HERE / "inputs" / f"{s}.json").write_text(json.dumps(entry, ensure_ascii=False, indent=2) + "\n")
(HERE / "planted.json").write_text(json.dumps(KEY, ensure_ascii=False, indent=1) + "\n")
print(sum(k["set"] == "subtle" for k in KEY), "subtle defects planted;", len(KEY), "in all")
