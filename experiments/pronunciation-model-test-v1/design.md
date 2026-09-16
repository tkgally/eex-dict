# Pronunciation model test v1 — design (frozen 2026-09-16 before any run)

**Question.** Can model knowledge supply the dictionary's American and British IPA, and can agreement between models tell a right transcription from a wrong one well enough to mark entries `verified` without storing any external pronouncing data?

**Fixed by the charter** ([pronunciation](../../wiki/decisions/pronunciation.md)): transcriptions come from model knowledge; the CMU Pronouncing Dictionary may be consulted at run time as one more vote for American, nothing from it stored; Wiktionary may be consulted by hand in this experiment only, nothing stored.

## 1. Word list (500 words, `words.tsv`)

| Stratum | n | How chosen |
|---|---|---|
| defining | 200 | seeded random sample (`random.Random(20260916)`) from `schema/defining-vocabulary.txt`, stratified by part of speech in proportion to the list, excluding one-letter words and affixes |
| mid | 100 | seeded random sample from `experiments/defining-vocabulary-v1/bands.tsv` rows with median band 2 or 3, excluding words already in the defining stratum |
| rare | 100 | the fixed list in `make_words.py`, written from the session's own knowledge (band 4 to 5 words: abstruse, sesquipedalian, obfuscate, and so on); no external list |
| heteronym | 50 | the fixed list in `make_words.py`, each with its part of speech (record noun, record verb count as two items) |
| loan | 50 | the fixed list in `make_words.py`: loanwords and proper-noun-derived words (croissant, karaoke, sandwich, boycott) |

Each row: `word	pos	stratum`. Heteronyms are asked for with their part of speech; every other word is asked for as its most common part of speech.

## 2. Models

Roles from `config/models.md`: `drafter` (Claude Sonnet 5, through OpenRouter, playing the Routine's drafter), `pronunciation-1` (GPT-5.6 Terra), `pronunciation-2` (Gemini 3.8 Flash), `pronunciation-3` (DeepSeek V4 Pro). Each is asked in chunks of 50 words, temperature 0.1, reasoning effort low where supported, with this fixed prompt:

> For each word below give its pronunciation in IPA for General American and for Standard Southern British English (Received Pronunciation). Mark primary stress with ˈ and secondary stress with ˌ before the syllable, separate syllables with a period, and write no slashes or brackets. Use these symbols: American vowels i ɪ ɛ æ ɑ ɔ ʊ u ʌ ə ɚ ɝ eɪ oʊ aɪ aʊ ɔɪ; British vowels iː ɪ e æ ɑː ɒ ɔː ʊ uː ʌ ə ɜː eɪ əʊ aɪ aʊ ɔɪ ɪə eə ʊə; consonants p b t d k ɡ tʃ dʒ f v θ ð s z ʃ ʒ h m n ŋ l r w j. Give the pronunciation of the word as the part of speech shown. Return JSON: {"items": [{"w": "word", "pos": "code", "american": "...", "british": "..."}]} in the input order.

Raw replies are committed under `outputs/<role>.json` (they are the models' own output, the project's record).

## 3. References, consulted at run time only

- **American:** the CMU Pronouncing Dictionary (`cmudict.dict`, fetched by `run.py` to `.tmp/`, deleted after; nothing from it is committed). ARPAbet is converted to IPA by the fixed mapping in `tools/pronounce_check.py` (AA ɑ, AE æ, AH0 ə, AH1/AH2 ʌ, AO ɔ, AW aʊ, AY aɪ, CH tʃ, DH ð, EH ɛ, ER0 ɚ, ER1/ER2 ɝ, EY eɪ, G ɡ, HH h, IH ɪ, IY i, JH dʒ, NG ŋ, OW oʊ, OY ɔɪ, SH ʃ, TH θ, UH ʊ, UW u, Y j, ZH ʒ; other consonants as themselves; stress digit 1 becomes ˈ and 2 becomes ˌ, placed before the vowel). When CMU lists several pronunciations, any one of them counts as a match. Heteronyms are compared against the CMU variant whose stress fits the part of speech only where CMU has variants; otherwise the word is excluded from the CMU comparison and noted.
- **British:** inter-model agreement, plus a hand consultation of Wiktionary for 100 words (seeded random: 40 defining, 20 mid, 20 rare, 10 heteronym, 10 loan) by the session, recording only `agree` or `disagree` per word and model in `wiktionary-check.tsv`.

## 4. Normalization

**N1 (exact).** Strip slashes and brackets; remove syllable periods and length marks (ː); ɹ to r, ɡ to g, ligature tʃ/dʒ spelled as two characters, tie bars removed; every stress mark moved to immediately before the next vowel symbol (so syllabification differences do not count); flapped ɾ to t; syllabic marks removed; trailing or double spaces removed.

**N2 (phoneme-level).** N1, then: secondary stress marks removed; in American, e and ɛ merge, ɔ and ɑ merge except before r or in ɔɪ, ɚ and ər merge, ɝ and ɜr and ʌr merge, final ɪ and i merge, ʊr and ɔr differences before r are kept; in British, ɛ and e merge, ɜ and ɜː merge, əʊ and oʊ merge, final ɪ and i merge, ɛə and eə merge, ɪə and ɪr differences are kept. Unstressed ɪ merges with ə in both varieties (roses, Rosa's); a syllabic consonant is written ə plus the consonant. Two transcriptions agree under N2 when the strings are identical after these steps; when either source omitted stress marks entirely, stress is ignored for that comparison. (Amended 2026-09-16 before any model was run, after a dry test of the normalizer on hand-written cases.)

**4a. Amendment after the first scoring (2026-09-16, before any verdict was adopted).** Reading the 65 drafter-versus-CMU disagreements showed that most were notation conventions, not transcription differences: monosyllables written without a stress mark (which the ɪ-to-ə rule then wrongly reduced), CMU's secondary stress on prefixes such as *in-* and *im-* (the models write none), the marry-merry merger (CMU writes *paradigm* with ɛr, the models with ær), ŋ before k, and unstressed ʌ in *un-* against CMU's ə. N2 now (a) supplies a primary stress mark before the first vowel of a transcription that has none, (b) removes secondary stress before the ɪ-to-ə merger, (c) merges unstressed ʌ with ə, (d) merges ŋk with nk, and (e) in American merges ær with er. The pre-registered rule and thresholds are unchanged; `results.md` reports the numbers under the original N2 and under the amended N2 so the effect of the amendment is visible.

## 5. Measures (per model, per variety)

1. Exact-match (N1) and phoneme-level (N2) agreement with CMU, American, over the words CMU has.
2. Pairwise inter-model agreement under N2, both varieties.
3. The drafter's agreement with CMU (its accuracy proxy) by stratum.
4. **Verified precision:** among words where the pre-registered rule below marks the drafter's American transcription `verified`, the share that also agree with CMU under N2. **Disputed recall:** among words where the drafter disagrees with CMU under N2, the share the rule marks `disputed` or `unverified`.
5. British: agreement with the Wiktionary hand check by stratum.

## 6. Pre-registered decision rule (what `tools/pronounce_check.py` will implement unless the data force a change, which the note must justify)

Votes for a transcription: the three panel members, plus CMU for American when it is reachable and has the word.

- `verified`: at least **two** votes agree with the drafter's transcription under N2.
- `disputed`: fewer than two votes agree with the drafter, and at least two votes agree with each other on some other transcription.
- `unverified`: anything else (no quorum, panel failure, word absent from every source).

**Acceptance thresholds, fixed in advance.** The rule is adopted as is if verified precision (measure 4) is at least 0.95 and the drafter's N2 agreement with CMU on the defining stratum is at least 0.90. If verified precision is below 0.95, the threshold rises to three votes. If the drafter's agreement is below 0.90, the note recommends that pronunciation be drafted by the best-scoring panel member instead of the drafter, and the rule is re-evaluated with that model as the source. A panel member whose own N2 agreement with CMU is below 0.85 is dropped from the panel.

## 7. What is committed

`design.md` (this file, unchanged after the run), `words.tsv`, `make_words.py`, `run.py`, `analyze.py`, `outputs/*.json` (model replies), `verdicts.tsv` (per word: stratum, each model's N1 and N2 agreement with the drafter and with CMU as yes/no, the rule's verdict), `wiktionary-check.tsv` (agree/disagree only), `results.md`. Never a CMU or Wiktionary transcription.
