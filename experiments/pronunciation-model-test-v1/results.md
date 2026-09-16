# Results of pronunciation model test v1

Normalization: N2 v1 (amended, design section 4a).
Scored 500 words; roles present: drafter, pronunciation-1, pronunciation-2, pronunciation-3; threshold 2; CMU reachable.

## 1. Agreement with the CMU Pronouncing Dictionary (American), phoneme level N2 (exact N1 in parentheses)

| role | defining | mid | rare | loan | all |
|---|---|---|---|---|---|
| drafter | 98.5% (65.5%) n=200 | 96.9% (52.6%) n=97 | 80.7% (38.6%) n=88 | 80.9% (38.3%) n=47 | 92.6% (54.2%) n=432 |
| pronunciation-1 | 98.0% (41.0%) n=200 | 93.8% (58.8%) n=97 | 81.8% (44.3%) n=88 | 85.1% (42.6%) n=47 | 92.4% (45.8%) n=432 |
| pronunciation-2 | 97.5% (42.5%) n=200 | 93.8% (56.7%) n=97 | 75.0% (38.6%) n=88 | 83.0% (61.7%) n=47 | 90.5% (47.0%) n=432 |
| pronunciation-3 | 98.5% (56.0%) n=200 | 97.9% (54.6%) n=97 | 84.1% (52.3%) n=88 | 85.1% (44.7%) n=47 | 94.0% (53.7%) n=432 |

Heteronyms are excluded from the CMU comparison (CMU does not mark the part of speech).

## 2. Pairwise inter-model agreement (N2)

**american**: drafter vs pronunciation-1 93.2%; drafter vs pronunciation-2 94.3%; drafter vs pronunciation-3 94.8%; pronunciation-1 vs pronunciation-2 93.5%; pronunciation-1 vs pronunciation-3 94.0%; pronunciation-2 vs pronunciation-3 95.7%
**british**: drafter vs pronunciation-1 92.6%; drafter vs pronunciation-2 91.6%; drafter vs pronunciation-3 92.8%; pronunciation-1 vs pronunciation-2 89.8%; pronunciation-1 vs pronunciation-3 92.4%; pronunciation-2 vs pronunciation-3 92.9%

## 3. The pre-registered rule applied to the drafter's transcriptions

- American: verified 479, disputed 19, unverified 2.
- **Verified precision** (verified and agrees with CMU, over verified words CMU has): 95.0%.
- **Disputed recall** (drafter disagrees with CMU and the rule did not mark it verified): 34.4% of 32 drafter errors.
- British (panel only): verified 468, disputed 23, unverified 9.

| stratum | n | American verified | disputed | unverified | British verified | disputed | unverified |
|---|---|---|---|---|---|---|---|
| defining | 200 | 196 | 4 | 0 | 194 | 5 | 1 |
| mid | 100 | 98 | 2 | 0 | 93 | 6 | 1 |
| rare | 100 | 90 | 9 | 1 | 87 | 8 | 5 |
| heteronym | 50 | 47 | 3 | 0 | 50 | 0 | 0 |
| loan | 50 | 48 | 1 | 1 | 44 | 4 | 2 |
