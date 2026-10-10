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

## 2026-09-26: thirteenth lint pass, no new switch-offs

The five disabled pairs' counts are unchanged. Live fields: `reviewer-a` `ALL` 0.70 (1571/2245); `reviewer-b` `ALL` 0.68 (539/790). No family crossed under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` is 0.33 (99), still the nearest live family to the line. Under twenty: `reviewer-a` `etymology` 0.40 (15), `inflection` 0.10 (10, one escalation); `reviewer-b` `phrase` 0.41 (17), `adaptation` 0.56 (16).

## 2026-09-26: fourteenth lint pass, no new switch-offs

Disabled pairs unchanged. Live fields: `reviewer-a` `ALL` 0.71 (1694/2403); `reviewer-b` `ALL` 0.66 (573/867). No family under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` rose to 0.34 (103). `reviewer-b` `spelling-or-format` fell to 0.60 (167): about thirty rejections today are the quoted-headword flag on adaptation notes, a settled house convention it repeats every entry. Under twenty: `reviewer-a` `etymology` 0.40 (15), `inflection` 0.10 (10); `reviewer-b` `phrase` 0.41 (17).

## 2026-09-26: fifteenth lint pass, no new switch-offs

Disabled pairs unchanged. Live: `reviewer-a` `ALL` 0.70 (1756/2496); `reviewer-b` `ALL` 0.66 (590/897). No family under 30 percent at twenty or more decisions; `reviewer-a` `pronunciation` 0.33 (105), two rejections from the line (both today were the American length mark, a fence). `reviewer-b` `spelling-or-format` 0.56 (177), still falling on the quoted-headword flag.

## 2026-09-26: sixteenth lint pass, no new switch-offs

Disabled pairs unchanged. Live: `reviewer-a` `ALL` 0.70 (1824/2597); `reviewer-b` `ALL` 0.65 (614/944). No family under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` 0.32 (35/110): three rejections this session (British *diaper* with a final r, British *organisation*, American *resource*), all panel- and CMU-verified; one or two more and it crosses the line. `reviewer-b` `spelling-or-format` 0.53 (205), still falling on the quoted-headword flag and on requests to hand-mark listed forms (six on `read-v`). Under twenty: `reviewer-a` `inflection` 0.08 (12); `reviewer-b` `phrase` 0.41 (17).

## 2026-09-26: seventeenth lint pass, no new switch-offs

Disabled pairs unchanged. Live: `reviewer-a` `ALL` 0.71 (1894/2685); `reviewer-b` `ALL` 0.65 (634/980). No family under 30 percent at twenty or more decisions; `reviewer-a` `pronunciation` 0.32 (111), with no new rejection in the last five runs. `reviewer-b` `spelling-or-format` 0.51 (215), still falling on the quoted-headword flag. Under twenty: `reviewer-a` `inflection` 0.07 (15); `reviewer-b` `phrase` 0.41 (17).

## 2026-09-27: eighteenth lint pass, no new switch-offs

Disabled pairs unchanged. `reviewer-a` `ALL` 0.70 (1948/2766); `reviewer-b` `ALL` 0.65 (660/1018). No live family under 30 percent at twenty or more decisions; `reviewer-a` `pronunciation` 0.32 (36/112). `reviewer-b` `spelling-or-format` 0.50 (220). Under twenty: `reviewer-a` `inflection` 0.06 (16), four decisions from the line; `reviewer-b` `phrase` 0.41 (17).

## 2026-09-28: nineteenth lint pass, no new switch-offs

Disabled pairs unchanged. `reviewer-a` `ALL` 0.70 (2026/2883); `reviewer-b` `ALL` 0.63 (671/1070). No live family under 30 percent at twenty or more decisions; `reviewer-a` `pronunciation` 0.33 (37/113). `reviewer-a` `inflection` 0.06 (1 applied, 17 rejected, 1 escalated): one more rejection reaches twenty and switches it off. `reviewer-b` `spelling-or-format` 0.46 (246), falling on the quoted-headword flag (18 rejections in this run's three review cycles); its `definition-style` 0.65 (117) is being pulled down by objections to the sentence form of `core_idea`, which the style guide requires.

## 2026-09-28: twentieth lint pass, `reviewer-a` `inflection` switched off

`reviewer-a` `inflection` reached the line: 0.05 over 21 decisions (1 applied, 19 rejected, 1 escalated). It is now the sixth disabled pair in `tools/review_panel.py`. Inflections come from `tools/inflect.py`'s rules and the exceptions table, so a reviewer inflection objection was nearly always a misreading of a generated form; `reviewer-b` still checks the family (0 of 5, under twenty). Live: `reviewer-a` `ALL` 0.70 (2074/2955); `reviewer-b` `ALL` 0.62 (681/1105). `reviewer-a` `pronunciation` 0.33 (39/119) is now the nearest live family to the line. `reviewer-b` `spelling-or-format` 0.43 (265), still falling on the quoted-headword flag.

## 2026-09-28: twenty-first lint pass, no new switch-offs

Disabled pairs unchanged. `reviewer-a` `ALL` 0.70 (2174/3098); `reviewer-b` `ALL` 0.62 (705/1139). No live family under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` 0.32 (39/122), three rejections since the last pass, all the American length mark (a fence): still the nearest live family to the line. `reviewer-b` `spelling-or-format` 0.43 (269). Under twenty: `reviewer-b` `inflection` 0.00 (5), `reviewer-a` `etymology` 0.47 (17).

## 2026-09-29: twenty-second lint pass, no new switch-offs

Disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (2270/3219); `reviewer-b` `ALL` 0.62 (713/1154). No live family under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` 0.32 (41/129), still the nearest live family to the line. `reviewer-b` `spelling-or-format` 0.42 (271). Under twenty: `reviewer-a` `etymology` 0.47 (17); `reviewer-b` `inflection` 0.00 (5).

## 2026-09-29: twenty-third lint pass, no new switch-offs

Disabled pairs unchanged. `reviewer-a` `ALL` 0.71 (2388/3364); `reviewer-b` `ALL` 0.62 (725/1170). No live family under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` 0.32 (41/130), one more fence rejection (American *swip*); still the nearest live family to the line. `reviewer-b` `spelling-or-format` 0.43 (272). Under twenty: `reviewer-a` `etymology` 0.47 (17); `reviewer-b` `inflection` 0.00 (5).

## 2026-09-30: twenty-fourth lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (2474/3493); `reviewer-b` `ALL` 0.62 (738/1190). No live family under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` 0.32 (44/137), still the nearest live family to the line. `reviewer-b` `spelling-or-format` 0.42 (274). Under twenty: `reviewer-a` `etymology` 0.47 (17); `reviewer-b` `inflection` 0.00 (5), `phrase` 0.39 (18).

## 2026-09-30: twenty-fifth lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (2556/3614); `reviewer-b` `ALL` 0.61 (750/1229). No live family under 30 percent at twenty or more decisions. `reviewer-a` `spelling-or-format` 0.34 (11/32) is now the nearest live family to the line: five rejections this run, all the quoted-headword fence it has started to repeat. `reviewer-a` `pronunciation` 0.32 (44/137), unchanged. `reviewer-b` `spelling-or-format` 0.39 (297), 23 fence rejections this run. Under twenty: `reviewer-a` `etymology` 0.47 (17); `reviewer-b` `phrase` 0.39 (18), `inflection` 0.00 (5).

## 2026-09-30: twenty-sixth lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.70 (2636/3742); `reviewer-b` `ALL` 0.60 (769/1276). No live family under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` 0.31 (45/146) and `spelling-or-format` 0.32 (11/34) are the nearest live families to the line; both fall mainly on fence rejections (American length marks, syllable breaks, quoted headwords). `reviewer-b` `spelling-or-format` 0.38 (315). Under twenty: `reviewer-a` `etymology` 0.50 (18); `reviewer-b` `phrase` 0.37 (19), `inflection` 0.00 (5).

## 2026-10-01: twenty-seventh lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (2788/3931); `reviewer-b` `ALL` 0.60 (801/1333). No live family under 30 percent at twenty or more decisions. `reviewer-a` `pronunciation` 0.30 (47/156) sits exactly on the line, falling on the American length-mark fence (*wiv*, *but* this run); one more rejection without an apply puts it under. `reviewer-a` `spelling-or-format` rose to 0.39 (16/41): its *roadblock* and *bookshelf* calls were right. `reviewer-b` `spelling-or-format` 0.39 (322). Under twenty: `reviewer-a` `etymology` 0.53 (19); `reviewer-b` `inflection` 0.00 (5).

## 2026-10-01: twenty-eighth lint pass, `reviewer-a` `pronunciation` under the line, switch-off held

`reviewer-a` `pronunciation` fell to 0.29 (47 applied, 113 rejected, 160 decisions) on one more fence rejection (*button*'s syllabic n). The 30-percent rule calls for switching it off. This run's attempt to add the pair to `DISABLED_FAMILIES` was refused by the session's safety check as a reduction of review, so the change was reverted and the decision is left to the owner (`reviews/needs_curator.txt`). Until then the family stays live; its rejections are almost all settled fences (American length marks, syllable breaks), cheap to reject. Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (2873/4054); `reviewer-b` `ALL` 0.60 (815/1356). `reviewer-b` `phrase` 0.32 (7/22) is the next nearest live family. Under twenty: `reviewer-a` `etymology` 0.53 (19).

## 2026-10-01: twenty-ninth lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (2967/4199); `reviewer-b` `ALL` 0.59 (830/1396). `reviewer-a` `pronunciation` 0.29 (47/163), three more fence rejections (*friz*, the American length mark, among them); its switch-off still waits on the owner (`reviews/needs_curator.txt`), so it stays live. `reviewer-b` `phrase` 0.32 (7/22) is the next nearest live family; `reviewer-b` `spelling-or-format` 0.37 (349), still falling on the quoted-headword fence (fifteen rejections in this run's cycles). Under twenty: `reviewer-a` `etymology` 0.53 (19).

## 2026-10-02: thirtieth lint pass, `reviewer-b` `phrase` under the line, switch-off held

`reviewer-b` `phrase` fell to 0.29 (7 applied, 17 rejected, 24 decisions) on one more rejection (*bricks and mortar*, 2026-10-02). Almost all of its rejections are the keyword-rule fence (*at least*, *either ... or*, idioms under *bit*). The 30-percent rule calls for a switch-off, but it is the same kind of edit the session's safety check refused for `reviewer-a` `pronunciation` on 2026-10-01, so it is held with that pair for the owner's ruling (`reviews/needs_curator.txt`); both stay live and their fence objections are rejected. `reviewer-a` `pronunciation` 0.28 (47/165). Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3040/4308); `reviewer-b` `ALL` 0.59 (836/1429). `reviewer-b` `spelling-or-format` 0.35 (371), six more quoted-headword rejections. Under twenty: `reviewer-a` `etymology` 0.53 (19).

## 2026-10-02: thirty-first lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3134/4429); `reviewer-b` `ALL` 0.58 (849/1475). `reviewer-a` `pronunciation` 0.28 (47/165) and `reviewer-b` `phrase` 0.29 (7/24) are unchanged since the last pass and still held for the owner (`reviews/needs_curator.txt`). `reviewer-b` `spelling-or-format` fell to 0.33 (130/400): this run's three cycles rejected eighteen of its flags, nearly all the quoted-headword fence, and accepted one (*racecourse*), so it is now the nearest live family to the line after the two held ones. Under twenty: `reviewer-a` `etymology` 0.53 (19).

## 2026-10-02: thirty-second lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3271/4624); `reviewer-b` `ALL` 0.57 (880/1554). `reviewer-a` `pronunciation` 0.28 (49/174) and `reviewer-b` `phrase` 0.28 (7/25) are still held for the owner (`reviews/needs_curator.txt`). `reviewer-b` `spelling-or-format` is at 0.30 (132/436), on the line but not under it; nearly all its rejections are the quoted-headword fence. One more rejection without an apply puts it under; it would then be held with the other two. Under twenty: `reviewer-a` `etymology` 0.53 (19); `reviewer-b` `inflection` 0.00 (6).

## 2026-10-03: thirty-third lint pass, `reviewer-b` `spelling-or-format` under the line, switch-off held

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3367/4748); `reviewer-b` `ALL` 0.56 (890/1605). `reviewer-b` `spelling-or-format` fell to 0.28 (133 applied, 335 rejected, 468 decisions): nearly every rejection this run was the quoted-headword fence in adaptation notes (eleven in this run's first and third cycles). The 30-percent rule calls for a switch-off; it is held with `reviewer-a` `pronunciation` 0.28 (51/180) and `reviewer-b` `phrase` 0.28 (7/25) for the owner, for the reason given on 2026-10-01 (`reviews/needs_curator.txt`). A narrower fix is possible later: tell reviewer-b in its prompt that an opening quoted headword is house style.

## 2026-10-03: thirty-fourth lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3426/4834); `reviewer-b` `ALL` 0.55 (900/1626). The three held pairs are unchanged in standing and still wait on the owner (`reviews/needs_curator.txt`): `reviewer-a` `pronunciation` 0.28 (51/181), `reviewer-b` `phrase` 0.28 (7/25), `reviewer-b` `spelling-or-format` 0.28 (135/474). No other live family at twenty or more decisions is under 30 percent; the nearest is `reviewer-a` `spelling-or-format` 0.38 (23/60). Under twenty: `reviewer-a` `etymology` 0.55 (20 decisions, now at the threshold); `reviewer-b` `inflection` 0.00 (6).

## 2026-10-03: thirty-fifth lint pass, `reviewer-b` `phrase` back above the line

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3496/4927); `reviewer-b` `ALL` 0.55 (913/1662). `reviewer-b` `phrase` rose to 0.36 (10 applied, 18 rejected, 28 decisions), so it no longer meets the switch-off rule; its curator line is closed. Two pairs stay held for the owner (`reviews/needs_curator.txt`): `reviewer-a` `pronunciation` 0.28 (52/185) and `reviewer-b` `spelling-or-format` 0.28 (136/490), the latter still falling almost entirely on the quoted-headword fence (eight more rejections in this run). No other live family at twenty or more decisions is under 30 percent; the nearest is `reviewer-a` `spelling-or-format` 0.38 (24/64). Under twenty: `reviewer-b` `inflection` 0.00 (7).

## 2026-10-03: thirty-sixth lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3593/5068); `reviewer-b` `ALL` 0.55 (926/1688). Two pairs stay held for the owner (`reviews/needs_curator.txt`): `reviewer-a` `pronunciation` 0.28 (52/189) and `reviewer-b` `spelling-or-format` 0.28 (138/493). No other live family at twenty or more decisions is under 30 percent; the nearest is `reviewer-a` `spelling-or-format` 0.38 (24/64). Under twenty: `reviewer-b` `inflection` 0.00 (8).

## 2026-10-04: thirty-seventh lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3732/5233); `reviewer-b` `ALL` 0.55 (948/1714). Two pairs stay held for the owner (`reviews/needs_curator.txt`): `reviewer-a` `pronunciation` 0.27 (53/199), still falling on the American length-mark fence (three more rejections this run, on *food* and *beach*), and `reviewer-b` `spelling-or-format` 0.29 (142/498), which rose slightly because this run accepted two of its asterisk-style flags. No other live family at twenty or more decisions is under 30 percent. Under twenty: `reviewer-b` `inflection` 0.00 (8).

## 2026-10-04: thirty-eighth lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3824/5362); `reviewer-b` `ALL` 0.55 (959/1731). Two pairs stay held for the owner (`reviews/needs_curator.txt`): `reviewer-a` `pronunciation` 0.26 (53/202) and `reviewer-b` `spelling-or-format` 0.29 (144/501). No other live family at twenty or more decisions is under 30 percent. Under twenty: `reviewer-b` `inflection` 0.00 (8).

## 2026-10-04: thirty-ninth lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (3973/5570); `reviewer-b` `ALL` 0.55 (973/1776). Two pairs stay held for the owner (`reviews/needs_curator.txt`): `reviewer-a` `pronunciation` 0.26 (54/205) and `reviewer-b` `spelling-or-format` 0.28 (145/524); the latter fell again because the 13:01 review cycle rejected nine quoted-headword flags in one block of twelve. No other live family at twenty or more decisions is under 30 percent. Under twenty: `reviewer-b` `inflection` 0.11 (9).

## 2026-10-04: fortieth lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (4055/5678); `reviewer-b` `ALL` 0.55 (983/1799). Two pairs stay held for the owner (`reviews/needs_curator.txt`): `reviewer-a` `pronunciation` 0.27 (55/207), with one more length-mark rejection (*tube*) this run, and `reviewer-b` `spelling-or-format` 0.28 (147/534). No other live family at twenty or more decisions is under 30 percent. Under twenty: `reviewer-b` `inflection` 0.11 (9).

## 2026-10-05: forty-first lint pass, no new switch-offs

Disabled pairs unchanged (six). `reviewer-a` `ALL` 0.71 (4149/5816); `reviewer-b` `ALL` 0.54 (993/1832). Two pairs stay held for the owner (`reviews/needs_curator.txt`): `reviewer-a` `pronunciation` 0.26 (55/208), one more length-mark rejection (*leaf*), and `reviewer-b` `spelling-or-format` 0.27 (152/554), still mostly the quoted-headword fence. `reviewer-b` `phrase` 0.33 (11/33) stays above the line. No other live family at twenty or more decisions is under 30 percent. Under twenty: `reviewer-b` `inflection` 0.10 (10).

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
