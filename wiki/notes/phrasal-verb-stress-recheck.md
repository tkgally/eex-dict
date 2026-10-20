# Phrasal-verb stress: disputed earlier, verified now

*Observation, 2026-10-20 (eightieth lint pass). No tool change proposed.*

Ten band-1 phrasal verbs drafted 2026-10-19 carry `pronunciation-disputed`: `break-down`, `break-up`, `catch-up`, `check-out`, `clean-up`, `clear-up`, `come-back`, `come-in`, `come-on`, `come-out` (all `-phrv`). Each got 1 of 3 panel votes for stress on the particle; the curator file records the working assumption (particle stress, house practice).

On 2026-10-20 the same panel verified all 44 transcriptions of twenty-two new phrasal verbs (*cut down*–*find out*, *get away*–*go on*) with the same pattern, including verbs whose nouns take front stress (*cutoff*, *getaway*, *getup*).

`break-up-phrv` is also the only one whose transcriptions lack the secondary mark on the verb (`breɪk ˈʌp`, not `ˌbreɪk ˈʌp`).

Next step, in a paid build or review cycle (about US$0.10): add the missing `ˌ` to `break-up-phrv` and re-run `tools/pronounce_check.py` on the ten; clear the flag and the curator lines where they now verify.

**Re-run, 2026-10-20 13:20 (build cycle `20261020T131155Z-6s5qm1`).** The `ˌ` was added to `break-up-phrv` and the ten were re-checked: all twenty transcriptions are still disputed (1 of 3, one British *clear up* 0 of 3), so the flags and curator lines stay. The difference from the twenty-two verified verbs is not the transcriptions, which have the same shape. Do not re-run these again without a new reason; the owner's answer on the curator lines settles them.
