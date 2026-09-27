# Entries thin out in the later cycles of a long run

*Observed 2026-09-27 in a review of the 2026-09-26 sessions. Status: acted on (run shape changed the same day).*

**What was seen.** The first two-hour sessions ran 13 and 15 cycles. Mean size of the entries each build cycle wrote (words of JSON), in cycle order:

- Session 2 (`-iujuq0`): 883, 942, 740, 687, 589, 680, 643, 469.
- Session 3 (`-poh5we`): 789, 736, 642, 571, 650, 636, 698.

Verbs written on 2026-09-25 averaged 4.6 senses, 0.40 idioms, and a learner-error box on 65 percent; session 3's verbs averaged 3.3 senses, 0.13 idioms, 55 percent. Some very common verbs came out short (*set-v* 7 senses, *put-v* 5). The later letters of the alphabet do not explain it: the decline runs within each session. The likely cause is a long conversation, summarized more than once, that keeps less of the style guide in view.

**What changed (2026-09-27, owner's request).** At most four cycles a run (`tools/run_clock.py`, `MAX_CYCLES`), a run every six hours, twelve entries a build cycle, and a run ends after a cycle once its conversation has been summarized. Review weight rose from 0.20 to 0.30 (build 0.55 to 0.45); review runs read the entries written after 2026-09-26T19:40Z first.

**What to watch.** `metrics/history.jsonl` does not record entry size; a lint can recompute the per-cycle mean from `provenance.run_id` as above. If cycle 4 is still clearly thinner than cycle 1, lower `MAX_CYCLES` to three.
