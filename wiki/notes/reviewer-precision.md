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

## 2026-09-19: second lint pass, no new switch-offs

The five disabled pairs' counts are unchanged (they stop generating decisions once downgraded to `ok`), so the seed-set figures above still hold for them. Over the fields still live, none crossed under 30 percent at twenty or more decisions: `reviewer-a` `definition-style` grew to 0.65 (55, up from 0.60/47 — moving away from the threshold, not toward it); `pronunciation` sits at 0.37 (41); `reviewer-b` `definition-style` is 0.58 (31). `reviewer-a`'s overall precision is now 0.57 (512/892); `reviewer-b`'s is 0.49 (137/280), up from 0.37/222 — too few added decisions yet to revisit open question 2. Nothing actionable this run; keep watching `definition-style` (both roles) and `reviewer-a` `pronunciation` as they accumulate.

## 2026-09-20: third lint pass, no new switch-offs

The five disabled pairs' counts (`example-policy` for both roles, `reviewer-a` `grammar-code` and `sense-structure`, `reviewer-b` `explanation`) are still exactly the seed-set figures — confirms `DISABLED_FAMILIES` in `tools/review_panel.py` is working as intended (no decisions accrue once a family is downgraded to `ok`). Over the fields still live: `reviewer-a` `ALL` is 0.60 (572/960, up from 0.57); `reviewer-b` `ALL` is 0.53 (169/318, up from 0.49). No family crossed under 30 percent at twenty or more decisions this pass; the nearest is `reviewer-a` `grammar-code`'s neighbor `pronunciation` at 0.36 (42, unchanged) and `reviewer-a` `sense-structure`'s neighbor `label` at 0.52 (46). Nothing actionable; keep watching the same families.

## 2026-09-20: fourth lint pass, no new switch-offs

The five disabled pairs' counts are unchanged again (`reviewer-a` `example-policy` 7/44, `grammar-code` 20/75, `sense-structure` 14/48; `reviewer-b` `example-policy` 4/83, `explanation` 5/21) — the mechanism keeps holding. Over the fields still live: `reviewer-a` `ALL` is 0.62 (665/1064, up from 0.60); `reviewer-b` `ALL` is 0.58 (211/363, up from 0.53). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` moved further from the threshold, 0.36 (47, up from 42); `reviewer-a` `label` is 0.55 (51, up from 46), also moving away. Nothing under 20 decisions changed enough to flag. Nothing actionable; keep watching `pronunciation` and `label` (reviewer-a) as they accumulate.

## 2026-09-21: fifth lint pass, no new switch-offs

The five disabled pairs' counts are unchanged again (`reviewer-a` `example-policy` 7/44, `grammar-code` 20/75, `sense-structure` 14/48; `reviewer-b` `example-policy` 4/83, `explanation` 5/21), confirming the downgrade-to-`ok` mechanism still holds after two more build/closure runs. Over the fields still live: `reviewer-a` `ALL` is 0.64 (742/1154, up from 0.62); `reviewer-b` `ALL` is 0.62 (258/413, up from 0.58). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `label` kept moving away from the threshold, 0.62 (60, up from 0.55/51); `reviewer-a` `pronunciation` held roughly flat at 0.37 (49, was 0.36/47) and stays the nearest live family to the line — keep watching it. Nothing under 20 decisions changed enough to flag.

## 2026-09-21: sixth lint pass, no new switch-offs

The five disabled pairs' counts are unchanged again (`reviewer-a` `example-policy` 7/44, `grammar-code` 20/75, `sense-structure` 14/48; `reviewer-b` `example-policy` 4/83, `explanation` 5/21), over one closure run and two review rounds since the last measurement. Over the fields still live: `reviewer-a` `ALL` is 0.67 (896/1347, up from 0.64); `reviewer-b` `ALL` is 0.65 (319/489, up from 0.62). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` moved toward the threshold rather than away from it this time, 0.33 (60, down from 0.37/49) — still above 30 percent, but now the nearest live family to the line, ahead of its former neighbor `label`, which kept climbing to 0.66 (74). Watch `pronunciation` (reviewer-a) closely at the next pass. Nothing under 20 decisions changed enough to flag.

## 2026-09-22: seventh lint pass, no new switch-offs

The five disabled pairs' counts are unchanged again (`reviewer-a` `example-policy` 7/44, `grammar-code` 20/75, `sense-structure` 14/48; `reviewer-b` `example-policy` 4/83, `explanation` 5/21), over two build runs and one originality check since the last measurement. Over the fields still live: `reviewer-a` `ALL` is 0.68 (991/1452, up from 0.67); `reviewer-b` `ALL` is 0.69 (386/562, up from 0.65) — reviewer-b has now caught up to, and edged slightly past, reviewer-a's overall precision for the first time (open question 2 in `wiki/open-questions.md` updated to note this). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` held almost flat at 0.32 (62, was 0.33/60) — still the nearest live family to the line; `label` kept climbing to 0.69 (87, was 0.66/74), moving further away. Nothing under 20 decisions changed enough to flag.

## 2026-09-22: eighth lint pass, no new switch-offs

The five disabled pairs' counts are unchanged again (`reviewer-a` `example-policy` 7/44, `grammar-code` 20/75, `sense-structure` 14/48; `reviewer-b` `example-policy` 4/83, `explanation` 5/21), over two build runs, one review round, and one closure run since the last measurement. Over the fields still live: `reviewer-a` `ALL` is 0.69 (1138/1649, up from 0.68); `reviewer-b` `ALL` is 0.70 (442/630, up from 0.69). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` moved slightly toward the threshold, 0.34 (73, was 0.32/62) — still the nearest live family to the line; `label` eased back a touch to 0.66 (104, was 0.69/87) but remains well clear. Nothing under 20 decisions changed enough to flag.

## 2026-09-23: ninth lint pass, no new switch-offs

The five disabled pairs' counts are unchanged (`reviewer-a` `example-policy` 7/44, `grammar-code` 20/75, `sense-structure` 14/48; `reviewer-b` `example-policy` 4/83, `explanation` 5/21), over four build runs, one originality check, and one review round since the last measurement. Over the fields still live: `reviewer-a` `ALL` is 0.69 (1238/1788, flat); `reviewer-b` `ALL` is 0.70 (456/647, flat). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` is unchanged at 0.34 (79, was 73) and stays the nearest live family to the line. Under twenty decisions: `reviewer-a` `etymology` 0.40 (15), `inflection` 0.11 (9); `reviewer-b` `phrase` 0.41 (17) — watch these as they near twenty.

## 2026-09-24: tenth lint pass, no new switch-offs

The five disabled pairs' counts are unchanged (`reviewer-a` `example-policy` 7/44, `grammar-code` 20/75, `sense-structure` 14/48; `reviewer-b` `example-policy` 4/83, `explanation` 5/21), over four build runs and one originality check since the last measurement. Live fields: `reviewer-a` `ALL` 0.70 (1325/1898, up from 0.69); `reviewer-b` `ALL` 0.71 (470/665, up from 0.70). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` is 0.35 (81), still the nearest live family to the line. Under twenty: `reviewer-a` `etymology` 0.40 (15), `inflection` 0.11 (9, one escalation); `reviewer-b` `phrase` 0.41 (17), `adaptation` 0.50 (14). Watch `reviewer-b` `phrase`: three more decisions bring it to twenty.

## 2026-09-25: eleventh lint pass, no new switch-offs

The five disabled pairs' counts are unchanged. Live fields: `reviewer-a` `ALL` 0.70 (1432/2045); `reviewer-b` `ALL` 0.70 (498/708). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` is 0.34 (87), still the nearest live family to the line. Under twenty: `reviewer-a` `etymology` 0.40 (15), `inflection` 0.12 (9); `reviewer-b` `phrase` 0.41 (17), `adaptation` 0.56 (16).

## 2026-09-25: twelfth lint pass, no new switch-offs

The five disabled pairs' counts are unchanged. Live fields: `reviewer-a` `ALL` 0.70 (1515/2165); `reviewer-b` `ALL` 0.69 (521/754). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` is 0.33 (96), now within a few decisions of the line: two or three more rejections switch it off. Under twenty: `reviewer-a` `etymology` 0.40 (15); `reviewer-b` `phrase` 0.41 (17), `adaptation` 0.56 (16).
