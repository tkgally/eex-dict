# Results of pronunciation model test v1

Normalization: N2 v0 (as frozen in section 4, before the amendment).
Scored 500 words; roles present: drafter, pronunciation-1, pronunciation-2, pronunciation-3; threshold 2; CMU reachable.

## 1. Agreement with the CMU Pronouncing Dictionary (American), phoneme level N2 (exact N1 in parentheses)

| role | defining | mid | rare | loan | all |
|---|---|---|---|---|---|
| drafter | 93.5% (65.5%) n=200 | 85.6% (52.6%) n=97 | 69.3% (38.6%) n=88 | 76.6% (38.3%) n=47 | 85.0% (54.2%) n=432 |
| pronunciation-1 | 88.0% (41.0%) n=200 | 82.5% (58.8%) n=97 | 73.9% (44.3%) n=88 | 83.0% (42.6%) n=47 | 83.3% (45.8%) n=432 |
| pronunciation-2 | 87.5% (42.5%) n=200 | 84.5% (56.7%) n=97 | 68.2% (38.6%) n=88 | 83.0% (61.7%) n=47 | 82.4% (47.0%) n=432 |
| pronunciation-3 | 91.0% (56.0%) n=200 | 88.7% (54.6%) n=97 | 76.1% (52.3%) n=88 | 83.0% (44.7%) n=47 | 86.6% (53.7%) n=432 |

Heteronyms are excluded from the CMU comparison (CMU does not mark the part of speech).

## 2. Pairwise inter-model agreement (N2)

**american**: drafter vs pronunciation-1 90.0%; drafter vs pronunciation-2 91.0%; drafter vs pronunciation-3 93.0%; pronunciation-1 vs pronunciation-2 92.9%; pronunciation-1 vs pronunciation-3 92.0%; pronunciation-2 vs pronunciation-3 93.7%
**british**: drafter vs pronunciation-1 90.2%; drafter vs pronunciation-2 89.6%; drafter vs pronunciation-3 91.8%; pronunciation-1 vs pronunciation-2 89.4%; pronunciation-1 vs pronunciation-3 90.8%; pronunciation-2 vs pronunciation-3 91.6%

## 3. The pre-registered rule applied to the drafter's transcriptions

- American: verified 470, disputed 28, unverified 2.
- **Verified precision** (verified and agrees with CMU, over verified words CMU has): 88.2%.
- **Disputed recall** (drafter disagrees with CMU and the rule did not mark it verified): 26.2% of 65 drafter errors.
- British (panel only): verified 458, disputed 33, unverified 9.

| stratum | n | American verified | disputed | unverified | British verified | disputed | unverified |
|---|---|---|---|---|---|---|---|
| defining | 200 | 192 | 8 | 0 | 185 | 14 | 1 |
| mid | 100 | 96 | 4 | 0 | 92 | 7 | 1 |
| rare | 100 | 88 | 11 | 1 | 87 | 8 | 5 |
| heteronym | 50 | 47 | 3 | 0 | 50 | 0 | 0 |
| loan | 50 | 47 | 2 | 1 | 44 | 4 | 2 |
