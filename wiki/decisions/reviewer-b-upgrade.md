# Reviewer B upgrade

*Ruled by the owner through `inbox/` on 2026-10-05 (open question 2; inbox file archived as `inbox/archive/20261005_owner_rulings.txt`). Implemented the same day in `config/models.md`.*

**Why.** `reviewer-b` was a Flash-class model chosen for price. Its precision fell from 0.69 (2026-09-22) to 0.55 (2026-10-03) against reviewer-a's 0.71, and two of its issue families went under the 30-percent switch-off line ([reviewer-precision](../notes/reviewer-precision.md)).

**The change.** The `reviewer-b` role moves to the Pro-class candidate that `config/models.md` already named. Its slug was re-verified against the OpenRouter model list (`https://openrouter.ai/api/v1/models`) on 2026-10-05: present, priced at US$2.00 / 12.00 per million tokens in and out, against 0.75 / 3.75 before. The price table in `config/models.md` is what `tools/openrouter.py` uses for its budget estimates, so the estimates follow the change with no code edit. Only this role changes: `pronunciation-2` and `wordlist-2` keep the Flash-class model.

**Cost.** A review round costs roughly three times as much on the reviewer-b side. The daily cap stays US$15; the owner accepts the higher spend. The Google endpoint still refuses to switch reasoning off, so it runs at low effort (`tools/openrouter.py`, `reasoning_for`); a reply cut short by hidden reasoning shows as a hollow record, which the gate already refuses ([review-panel-parse-failures](../notes/review-panel-parse-failures.md)).

**Measuring it.** Decisions from 2026-10-05 on are reviewer-b's new model. Each lint pass reports its precision after the change beside the all-time figure, so the owner can see whether the upgrade paid.
