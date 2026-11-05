# Reviewer precision: the seed set (first measurement)

*Founding session, 2026-09-17. `python3 tools/metrics.py --precision` over the 798 adjudication lines for the 82 seed entries (run `20260916T134425Z-1yir52`). Precision is the share of a reviewer's issues that the session accepted (`apply`) rather than rejected; no issue was escalated. The lint run reads this page and switches off a family whose precision is under 30 percent for a role over twenty or more decisions (`routine-prompt.md`, lint mode).*

## Headline numbers

| role | issues decided | applied | precision |
|---|---|---|---|
| reviewer-a | 634 | 333 | 0.53 |
| reviewer-b | 164 | 34 | 0.21 |

Blocking issues: 525 (261 applied); minor: 273 (106 applied).

## Families under 30 percent with twenty or more decisions (candidates for switching off)

- reviewer-a **example-policy** 0.16 (44): almost every flag was a phrase with one example (the style guide allows one to three) or a generic example called a "checkable real-world claim" (*the wettest spring on record*, *a way of life for hundreds of years*).
- reviewer-a **grammar-code** 0.26 (73): patterns asked for adjectives, nouns, determiners, and modals that the closed verb-pattern list does not have; *often before another noun* read as a restriction; *comparative with more* read as missing the superlative.
- reviewer-a **sense-structure** 0.29 (42): sense splits the splitting principle does not license; one flag withdrew itself mid-sentence.
- reviewer-b **example-policy** 0.02 (81): the one-example-per-phrase flag, repeated on every phrase of every entry.
- reviewer-b **explanation** 0.06 (17, under the threshold): the explanation field on high-frequency verbs, modals, and abbreviations, which style guide section 3 allows.

The strongest families: definition-meaning 0.78, usage-note 0.75, synonym-discrimination 0.75 (reviewer-a); every reviewer-b collocation, cross-reference, and example-unnatural flag was applied, but there were few of them.

## Noise patterns, and what was done about them

Both reviewers were told the house conventions in the prompt and still flagged them. The list in `tools/review_panel.py` (`SYSTEM`) was extended after this run with the conventions the seed set exposed: entry-level labels cover every sense and phrase; monosyllables carry no stress mark; British transcriptions mark no linking r; respellings in pronunciation notes; etymologies name languages; explanations on use-hard verbs and modals; the closed pattern list; compounds in word families; a subsense with its own countability; generic examples. Two rules the flags exposed as real gaps went into the style guide: a subsense limited to one form (*look after yourself*) states the form in its explanation, not as a prefix in the definition; adaptation notes hedge claims about other languages (*often*, *many languages*), never *most* or *all*.

The largest genuine family was **adaptation** (reviewer-a, 0.65 over 130): unsupported "most languages" claims, and a few plain errors (*a hand, never hands*; *English always needs it*). The reviewers were also right about a dozen circular or prefixed subsense definitions, about *smell of* under the cause sense of *of*, and about *take someone to court* hiding in a movement sense.

## 2026-09-19: switched off, all-time figures

*Lint run, `tools/metrics.py --precision` over all 798 decisions logged since the founding session (the seed set plus the two build runs and the review run that followed).*

| role | family | applied | rejected | precision |
|---|---|---|---|---|
| reviewer-a | example-policy | 7 | 37 | 0.16 |
| reviewer-a | grammar-code | 20 | 55 | 0.27 |
| reviewer-a | sense-structure | 14 | 34 | 0.29 |
| reviewer-b | example-policy | 4 | 79 | 0.05 |
| reviewer-b | explanation | 5 | 16 | 0.24 |

All five are still under 30 percent over twenty or more decisions, so all five are now switched off in `tools/review_panel.py` (`DISABLED_FAMILIES`): an issue from one of these pairs is downgraded to `ok` before it reaches adjudication, so it never needs a decision line. `reviewer-a`'s `etymology` (0.25, 8) and `inflection` (0.00, 5) stay on: too few decisions to judge. `reviewer-b`'s `adaptation` (0.25, 4), `grammar-code` (0.14, 7), `inflection` (0.00, 3), and `phrase` (0.25, 8) likewise. `reviewer-a`'s overall precision this measurement is 0.56 (432/766); `reviewer-b`'s is 0.37 (82/222).

## What the next lint run should do

Re-measure after each review run and append to the table above; if a switched-off pair's issues (visible only by temporarily re-enabling it, or by the reviewer's raw `verdicts` before normalization) look to have improved, that is a judgment call for a future lint run, not an automatic re-enable — this project runs no A/B test on live entries to find out. Watch `reviewer-a` `etymology` and `sense-structure`'s neighbor `definition-style` (0.60, 47) as they approach or cross the threshold at higher counts.

## 2026-09-19 to 2026-10-05: second to forty-first passes (condensed)

All figures here are for the reviewer models replaced on 2026-10-25 and are kept in git history. `reviewer-a` `inflection` was switched off at the twentieth pass (0.05 over 21). Three pairs fell under the line and were held for the owner after the session's safety check refused the edit: `reviewer-a` `pronunciation` (switched off by the owner on 2026-10-05), `reviewer-b` `phrase` (back above the line at the thirty-fifth), and `reviewer-b` `spelling-or-format` (kept live by the owner's ruling).

## 2026-10-05: the owner's rulings

`reviewer-a` `pronunciation` (0.26 over 208) is switched off (seven disabled pairs); the pronunciation panel and the CMU check stay the check on transcriptions. `reviewer-b` `spelling-or-format` (0.27 over 554) stays live: the reviewer prompt now names the opening quoted headword of an adaptation note as house style; re-measure it, and raise it with the owner again if it stays under the line. `reviewer-b` moved to the Pro-class Google model the same day ([reviewer-b-upgrade](../decisions/reviewer-b-upgrade.md)): from the next pass, report its precision on decisions dated 2026-10-05 or later beside the all-time figure.

## 2026-10-05: forty-second lint pass

Seven disabled pairs (`reviewer-a` `pronunciation` joined them by the owner's ruling, frozen at 0.25 over 217). `reviewer-a` `ALL` 0.71 (4244/5958); `reviewer-b` `ALL` 0.54 (1012/1879). `reviewer-b` `spelling-or-format` 0.27 (155/568), kept live by the owner: measure again after a few cycles of the new prompt line. Nothing else live crossed under 30 percent at twenty or more decisions; `reviewer-b` `phrase` 0.37 (35). Upgraded reviewer-b, decisions from 2026-10-05 09:00 only: 2 applied of 8 (0.25), six of the rejections on the keyword-rule fence. Too few to judge; it also answered three of eleven entries with only its issues ([note](reviewer-b-partial-verdicts.md)).

## 2026-10-05: forty-third lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (4317/6054); `reviewer-b` `ALL` 0.54 (1018/1895). `reviewer-b` `spelling-or-format` 0.27 (155/568), unchanged since the last pass (no new decisions in that family), so the new prompt line cannot be judged yet. `reviewer-b` `phrase` 0.36 (36). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 8 applied of 24 (0.33). Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.08 (12).

## 2026-10-05: forty-fourth lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.71; `reviewer-b` `ALL` 0.54 (1034/1923). `reviewer-b` `spelling-or-format` 0.28 (161/577): since the new prompt line it is 6 applied of 9, up from the old rate, so it stays live as the owner asked. `reviewer-b` `phrase` 0.35 (37). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 24 applied of 54 (0.44). Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.07 (15).

## 2026-10-06: forty-fifth lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-b` `ALL` 0.54 (1039/1930). `reviewer-b` `spelling-or-format` 0.28 (161/577), no new decisions since the last pass; 6 applied of 9 since the prompt line, so it stays live. `reviewer-b` `phrase` 0.35 (37). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 29 applied of 59 (0.49). Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.07 (15).

## 2026-10-06: forty-sixth lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-b` `ALL` 0.54 (1043/1940). `reviewer-b` `spelling-or-format` 0.28 (161/577), no new decisions since the last pass; 6 applied of 9 since the prompt line, so it stays live. `reviewer-b` `phrase` 0.34 (38). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 33 applied of 69 (0.48); since the last pass 4 of 10. Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.07 (15). The reviewer-b issue rate fell to 0.10 applied per entry after the 2026-10-05 prompt fix; the warning line was softened this pass ([note](reviewer-b-partial-verdicts.md)).

## 2026-10-06: forty-seventh lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (4643/6533); `reviewer-b` `ALL` 0.54 (1052/1955). `reviewer-b` `spelling-or-format` 0.28 (161/578): one new decision since the last pass, a rejection (hand marks asked for in an example of *past*), so 6 applied of 10 since the prompt line; it stays live. `reviewer-b` `phrase` 0.34 (38). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 42 applied of 84 (0.50); since the last pass 9 of 15. Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.07 (15).

## 2026-10-07: forty-eighth lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (4730/6649); `reviewer-b` `ALL` 0.54 (1059/1971). `reviewer-b` `spelling-or-format` 0.28 (161/578), no new decisions since the last pass; 6 applied of 10 since the prompt line, so it stays live. `reviewer-b` `phrase` 0.33 (13/39), just above the line. Upgraded reviewer-b, decisions from 2026-10-05 09:00: 49 applied of 100 (0.49); since the last pass 7 of 16. Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.07 (15).

## 2026-10-07: forty-ninth lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (4864/6821); `reviewer-b` `ALL` 0.54 (1070/1983). `reviewer-b` `spelling-or-format` 0.28 (161/578), no new decisions since the last pass; it stays live. `reviewer-b` `phrase` 0.37 (15/41), back above the line (both *first-rate* calls on `rate-n` were right). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 60 applied of 114 (0.53); since the last pass 11 of 14. Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.07 (15).

## 2026-10-07: fiftieth lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (4948/6949); `reviewer-b` `ALL` 0.54 (1074/1995). `reviewer-b` `spelling-or-format` 0.28 (161/578), no new decisions since the last pass; it stays live. `reviewer-b` `phrase` 0.36 (15/42). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 64 applied of 124 (0.52); since the last pass 4 of 10. Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.07 (15).

## 2026-10-07: fifty-first lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (5096/7125); `reviewer-b` `ALL` 0.54 (1083/2007). `reviewer-b` `spelling-or-format` 0.28 (161/578), no new decisions since the last pass; it stays live. `reviewer-b` `phrase` 0.36 (15/42). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 73 applied of 136 (0.54); since the last pass 9 of 12. Nothing else live is under 30 percent at twenty or more decisions.

## 2026-10-08: fifty-second lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (5189/7259); `reviewer-b` `ALL` 0.54 (1083/2017). `reviewer-b` `spelling-or-format` 0.28 (161/578), no new decisions since the last pass; it stays live. `reviewer-b` `phrase` 0.36 (15/42). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 73 applied of 146 (0.50); since the last pass 0 of 10 (four "not phrasal" flags on `corner-n` phrases, two that withdrew themselves inside the same comment, one grammar-code consistency claim on `council-n`). Nothing else live is under 30 percent at twenty or more decisions. Watch reviewer-b `definition-style` (0.56 over 213) if self-withdrawn flags continue.

## 2026-10-08: fifty-third lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (5275/7382); `reviewer-b` `ALL` 0.54 (1092/2033). `reviewer-b` `spelling-or-format` 0.28 (161/578), no new decisions since the last pass; it stays live. `reviewer-b` `phrase` 0.36 (15/42). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 82 applied of 162 (0.51); since the last pass 9 of 16. Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.12 (16). `reviewer-b` `definition-style` 0.56 (216), steady.

## 2026-10-08: fifty-fourth lint pass, no new switch-offs

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (5417/7576); `reviewer-b` `ALL` 0.54 (1101/2054). `reviewer-b` `spelling-or-format` 0.28 (161/580): two new decisions since the last pass, both rejections (hand marks asked for in examples of `sound-n`); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.36 (15/42). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 91 applied of 183 (0.50); since the last pass 9 of 21. Nothing else live is under 30 percent at twenty or more decisions; under twenty: `reviewer-b` `inflection` 0.12 (17).

## 2026-10-08: fifty-fifth lint pass, no new switch-offs, reviewer-b yield falling

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (5511/7703); `reviewer-b` `ALL` 0.53 (1104/2067). `reviewer-b` `spelling-or-format` 0.28 (161/581); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.36 (15/42). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 94 applied of 198 (0.47); since the last pass 3 of 15. It raised 15 issues over the 42 entries of the four cycles since the last pass (two builds of twelve gave 2 and 0), so 0.07 applied per entry against 0.24 at the forty-eighth pass. If the next lint finds it still under 0.10, write the observation up as a note before any prompt change. Under twenty: `reviewer-b` `inflection` 0.11 (18).

## 2026-10-09: fifty-sixth lint pass, no new switch-offs, reviewer-b low-yield note

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (5630/7853); `reviewer-b` `ALL` 0.53 (1107/2074). `reviewer-b` `spelling-or-format` 0.28 (161/581), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.36 (15/42). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 97 applied of 203 (0.48); since the last pass 3 of 5. It raised 5 issues over 50 entries (0.06 applied per entry), still under 0.10: written up in [reviewer-b-low-yield](reviewer-b-low-yield.md). Under twenty: `reviewer-b` `inflection` 0.11 (18).

## 2026-10-09: fifty-seventh lint pass, no new switch-offs, reviewer-b yield recovered

Seven disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (5729/7984); `reviewer-b` `ALL` 0.53 (1122/2104). `reviewer-b` `spelling-or-format` 0.28 (161/581), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.35 (15/43). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 112 applied of 233 (0.48); since the last pass 15 of 30, over 58 entries (0.26 applied per entry), back above the 0.10 line of [reviewer-b-low-yield](reviewer-b-low-yield.md); most of its rejected flags asked for a bare *verb* pattern that the closed list lacks. Under twenty: `reviewer-b` `inflection` 0.11 (19).

## 2026-10-09: fifty-eighth lint pass, `reviewer-b` `inflection` switched off

`reviewer-b` `inflection` reached the line: 0.10 over 21 decisions (2 applied, 19 rejected). It is now the eighth disabled pair in `tools/review_panel.py`, and the family is off for both roles. Its rejected flags asked for plurals that `tools/inflect.py` owns or cannot yet write (the known gap in [inflect-uncountable-plural-gap](inflect-uncountable-plural-gap.md)), or for forms on auxiliaries, which carry none by schema. `reviewer-a` `ALL` 0.72 (5853/8146); `reviewer-b` `ALL` 0.53 (1133/2120). `reviewer-b` `spelling-or-format` 0.28 (161/581), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.35 (15/43). Upgraded reviewer-b since the last pass: 1 applied of 2 over 12 entries (0.08 applied per entry), under the 0.10 line of [reviewer-b-low-yield](reviewer-b-low-yield.md) again, on one build only: watch it.

## 2026-10-10: fifty-ninth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (5967/8293); `reviewer-b` `ALL` 0.54 (1148/2142). `reviewer-b` `spelling-or-format` 0.28 (161/581), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.38 (17/45). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 138 applied of 271 (0.51); since the last pass 15 of 22 over 60 entries (0.25 applied per entry). But the sampling check of [reviewer-b-low-yield](reviewer-b-low-yield.md) found it marked `ok` on 34 of 36 fields where reviewer-a's blocking fault was real: its yield figure hides misses. Nothing else live is under 30 percent at twenty or more decisions.


## 2026-10-10: sixtieth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6031/8388); `reviewer-b` `ALL` 0.54 (1153/2154). `reviewer-b` `spelling-or-format` 0.28 (161/582): one new decision, a rejection (*Way Out* on `exit-n` is a sign's words, so double marks are right); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.38 (17/45). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 143 applied of 283 (0.51); since the last pass 5 of 12 over about 37 entries (0.14 applied per entry), against reviewer-a's 64 of 94. Nothing else live is under 30 percent at twenty or more decisions.

## 2026-10-10: sixty-first lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6118/8509); `reviewer-b` `ALL` 0.53 (1161/2178). `reviewer-b` `spelling-or-format` 0.28 (161/582), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.38 (17/45). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 151 applied of 307 (0.49); since the last pass 7 of 10 over 26 entries (0.27 applied per entry), most of them on `brown-adj`, `busy-adj` and `calm-adj`; its one new sense-structure call (a skin-color sense for `brown-adj`) was applied. Nothing else live is under 30 percent at twenty or more decisions.

## 2026-10-11: sixty-second lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6215/8631); `reviewer-b` `ALL` 0.53 (1170/2200). `reviewer-b` `spelling-or-format` 0.28 (161/583), no new applied decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.37 (17/46). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 160 applied of 329 (0.49); this run's two cycles 2 of 9 (it asked four times to drop the house gradability codes and once for a *to* before a phrase definition). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-11: sixty-third lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6308/8763); `reviewer-b` `ALL` 0.53 (1182/2230). `reviewer-b` `spelling-or-format` 0.28 (162/584): one new decision, applied; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.35 (17/48). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 172 applied of 359 (0.48); since the last pass 12 of 30 over four cycles (three builds of twelve adjectives and one review). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-11: sixty-fourth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6417/8914); `reviewer-b` `ALL` 0.53 (1199/2249). `reviewer-b` `spelling-or-format` 0.28 (162/584), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.35 (17/48). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 189 applied of 378 (0.50); since the last pass 17 of 19 over four cycles (two reviews, a closure, and a build). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-11: sixty-fifth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6546/9084); `reviewer-b` `ALL` 0.53 (1216/2274). `reviewer-b` `spelling-or-format` 0.28 (162/584), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.35 (17/48). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 206 applied of 403 (0.51); since the last pass 17 of 25 over four cycles (three builds of twelve adjectives and one review). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-12: sixty-sixth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6612/9186); `reviewer-b` `ALL` 0.53 (1221/2287). `reviewer-b` `spelling-or-format` 0.28 (162/584), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.35 (17/49). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 211 applied of 416 (0.51); since the last pass 5 of 13 over one build cycle (*long*–*mental*). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-12: sixty-seventh lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6719/9331); `reviewer-b` `ALL` 0.53 (1241/2322). `reviewer-b` `spelling-or-format` 0.28 (162/584), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.34 (17/50). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 231 applied of 451 (0.51); since the last pass 20 of 35 over four cycles (three builds of adjectives and one review). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-12: sixty-eighth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6810/9477); `reviewer-b` `ALL` 0.53 (1245/2335). `reviewer-b` `spelling-or-format` 0.28 (162/584), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.33 (17/51). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 235 applied of 464 (0.51); since the last pass 4 of 13 over five cycles (two builds, two reviews, one originality check). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-12: sixty-ninth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (6939/9652); `reviewer-b` `ALL` 0.53 (1259/2367). `reviewer-b` `spelling-or-format` 0.28 (162/584), no new decisions; it stays live by the owner's ruling. `reviewer-b` `phrase` 0.33 (17/52). Upgraded reviewer-b, decisions from 2026-10-05 09:00: 249 applied of 496 (0.50); since the last pass 14 of 32 over four cycles (two builds, a review, and a closure). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-13: seventieth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (7055/9812); `reviewer-b` `ALL` 0.53 (1275/2393). `reviewer-b` `spelling-or-format` 0.28 (163/585); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.32 (17/53), the nearest live pair to the line. Since the last pass reviewer-b had 16 of 24 applied over three cycles (two builds, one review), most of them adverb uses caught in adjective examples. No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-13: seventy-first lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (7146/9937); `reviewer-b` `ALL` 0.53 (1284/2417). `reviewer-b` `spelling-or-format` 0.28 (163/585); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.32 (18/57), still the nearest live pair to the line. Since the last pass reviewer-b had 9 of 24 applied over four cycles (two builds, a review, a closure) and the originality cycle's panel (3 rejected on *public*). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-14: seventy-second lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (7263/10088); `reviewer-b` `ALL` 0.53 (1296/2446). `reviewer-b` `spelling-or-format` 0.28 (163/585); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.32 (18/57), still the nearest live pair to the line. In this run's three cycles reviewer-b had 11 of 26 applied (two builds and one review; 1 of 7 on the review). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-15: seventy-third lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (7357/10240); `reviewer-b` `ALL` 0.53 (1300/2461). `reviewer-b` `spelling-or-format` 0.28 (163/585); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.31 (18/59; two `meal-n` rejections on 2026-10-15), still the nearest live pair to the line. No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-15: seventy-fourth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (7472/10412); `reviewer-b` `ALL` 0.53 (1314/2476). `reviewer-b` `spelling-or-format` 0.28 (164/586); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.31 (18/59), still the nearest live pair to the line. In this run's three cycles reviewer-b had 4 of 5 applied (one review, one closure, one build). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-16: seventy-fifth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.72 (7543/10542); `reviewer-b` `ALL` 0.53 (1320/2492). `reviewer-b` `spelling-or-format` 0.28 (164/587); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.31 (18/59), still the nearest live pair to the line. In the five cycles since the last pass reviewer-b had 6 of 16 applied (two builds, two reviews, one originality check). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-17: seventy-sixth lint pass, no new switch-offs

Eight disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (7672/10758); `reviewer-b` `ALL` 0.53 (1326/2499). `reviewer-b` `spelling-or-format` 0.28 (164/587); it stays live by the owner's ruling. `reviewer-b` `phrase` 0.31 (18/59), still the nearest live pair to the line. In the three cycles since the last pass reviewer-b had 1 of 2 applied (it raised nothing on twenty review entries and one on twelve builds). No live pair is under 30 percent over twenty or more decisions except `reviewer-b` `spelling-or-format`, which the owner kept.

## 2026-10-18 to 2026-10-24: seventy-seventh to eighty-sixth passes (condensed)

No switch-offs. `reviewer-a` `ALL` 0.71 (its `coverage` 0.23, live by ruling B1); `reviewer-b` `ALL` 0.52 to 0.53, `spelling-or-format` 0.28 (live by the owner's ruling), `phrase` 0.30 to 0.31. Most reviewer-b rejections were the *say hello* noun claim and the *verb + adverb* pattern fence.

## 2026-10-25 to 2026-10-28: eighty-seventh to ninety-first passes (condensed)

No switch-offs. `reviewer-a:claude-sonnet-5-5` rose from 0.86 (272/316) to 0.80 (1611/2002) as decisions grew; its low pairs were `grammar-code` (gradability codes called duplicates of the inflection note, rejected by the fence), `coverage`, and `inflection`, under twenty decisions until the ninety-second pass. `reviewer-b:gemini-4-argon` held near 0.80; `spelling-or-format` stayed live by the owner's ruling; `phrase` fell to 0.17, under twenty, from keyword-rule rejections.

## 2026-10-28: ninety-second pass, reviewer A `inflection` switched off

`reviewer-a:claude-sonnet-5-5` 0.81 (1901/2351); `inflection` 0.21 (5/24), now over twenty and under the line: added to `DISABLED_FAMILIES` in `tools/review_panel.py`. Inflections are generated by `tools/inflect.py` from rules and the exceptions table, so nothing is lost. `reviewer-b:gemini-4-argon` 0.81 (735/910); `spelling-or-format` 0.29 (24/83), live by the owner's ruling; `phrase` 0.15 (2/13, under twenty).

## 2026-10-30: ninety-fourth pass, reviewer B `phrase` switched off

`reviewer-a:claude-sonnet-5-5` 0.83 (2689/3254); no pair newly under the line. `reviewer-b:gemini-4-argon` 0.81 (1110/1365); `phrase` 0.20 (4/20), now at twenty decisions and under the line: added to `DISABLED_FAMILIES`. Its rejected phrase issues were idioms filed under another keyword and phrasal verbs asked for as phrases; reviewer A still checks phrases. `spelling-or-format` 0.26 (32/122), live by the owner's ruling.

## 2026-10-29 to 2026-11-02: ninety-third, ninety-fifth to ninety-eighth passes, no new switch-offs

`reviewer-a:claude-sonnet-5-5` 0.83 (3729/4495 at the ninety-eighth); lowest live pairs `coverage` 0.59 (live by ruling B1) and `grammar-code` 0.64. `reviewer-b:gemini-4-argon` 0.81 (1623/2008); `spelling-or-format` 0.27 (46/172), live by the owner's ruling; `pronunciation` 0.35 (8/23, down from 0.38), the nearest live pair to the line; `inflection` 0.36 (4/11), under twenty.

## 2026-11-03 to 2026-11-04: ninety-ninth to hundred-and-first passes, no new switch-offs

`reviewer-a:claude-sonnet-5-5` 0.84 (4369/5229 at the hundred-and-first). `reviewer-b:gemini-4-argon` 0.81 (1935/2384); `spelling-or-format` 0.29 (59/207), live by the owner's ruling; `pronunciation` 0.38 (11/29), the nearest live pair to the line; `inflection` 0.36 (5/14), under twenty.

## 2026-11-05: hundred-and-second pass, reviewer B `pronunciation` switched off

`reviewer-a:claude-sonnet-5-5` 0.84 (4693/5604). `reviewer-b:gemini-4-argon` 0.82 (2086/2557); `pronunciation` 0.26 (11 applied, 29 rejected, 2 escalated), now over twenty and under the line: added to `DISABLED_FAMILIES`. Its rejections since 2026-11-03 were nearly all objections to the house IPA form (optional syllable periods, the whole *ʊʃ* in *butcher*, *form* and *warm* rhyming), each against a verified panel and CMU vote. Both reviewers are now off pronunciation; transcriptions are still checked by `tools/pronounce_check.py` (panel plus CMU). `spelling-or-format` 0.31 (68/219), live by the owner's ruling; `inflection` 0.33 (5/15), under twenty.
