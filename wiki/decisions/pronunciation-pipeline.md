# The pronunciation pipeline: panel and agreement rule

*Decided by the founding session on 2026-09-16 from the pre-registered experiment recorded in [pronunciation-model-test-v1](../notes/pronunciation-model-test-v1.md), under the owner's ruling in [pronunciation](pronunciation.md). Implemented in `tools/pronounce_check.py`.*

**Source of transcriptions.** The drafting model writes both transcriptions from its own knowledge, in the symbol set fixed in `tools/pronounce_check.py` (General American and Standard Southern British, primary and secondary stress, syllable breaks). The experiment found the drafter right, at the phoneme level, on 98.5 percent of defining-vocabulary words and 92.6 percent of a stratified 500-word sample against the CMU Pronouncing Dictionary, so drafting stays with the drafter.

**Panel.** The three roles `pronunciation-1` (OpenAI), `pronunciation-2` (Google), `pronunciation-3` (DeepSeek) in `config/models.md`, each of which agreed with the CMU dictionary on more than 90 percent of the sample; a member is dropped when a re-test puts it below 85 percent. Calls run with reasoning switched off (the transcriptions are the same and the cost a third).

**Votes.** For American: the three panel transcriptions plus the CMU Pronouncing Dictionary's, fetched at run time to a temporary directory when reachable (ARPAbet converted to IPA by the fixed mapping in the tool; nothing stored). For British: the three panel transcriptions.

**Rule.** Transcriptions are compared under the phoneme-level normalization N2 (design section 4 as amended in 4a: notation differences, secondary stress, the marry-merry and cot-caught mergers, unstressed vowel reduction). A transcription is **`verified`** when at least **two** votes agree with the drafter's; **`disputed`** when fewer than two agree and at least two votes agree with each other on something else; **`unverified`** otherwise. Measured on the experiment: verified precision 95.0 percent (the pre-registered acceptance threshold), every real drafter error caught.

**What is written.** Only `pronunciation.<variety>.checked_by` (for example `agreement:3/4;cmudict:agree`) and `status`. A `disputed` transcription adds `pronunciation-disputed` to `provenance.flags`; the session settles it by the CMU vote when there is one, otherwise the question goes to `reviews/needs_curator.txt` with the drafter's form kept meanwhile. The reviewers also read every transcription.

**British check.** No consulted source is in the pipeline for British. In the experiment a 100-word hand check against Wiktionary was recorded (agree/disagree only) in `experiments/pronunciation-model-test-v1/wiktionary-check.tsv`; its numbers are in `results.md`, section 4.

**Revisit.** A second test on the Routine's own entries after a few hundred exist; the threshold and the panel change only by a new decision page.
