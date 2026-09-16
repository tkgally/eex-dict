# Register of resources consulted at run time

This directory holds markdown only. **No data file is ever stored here or anywhere in the repository.** A resource listed below may be fetched to a temporary directory outside the repository (`.tmp/`, gitignored) to check a single fact, and the entry then records only the verdict (for example `checked_by: "agreement:3/3;cmudict:agree"`). Nothing is copied from any of them into an entry, a list, or a table.

| Resource | Used for | How | Verified reachable |
|---|---|---|---|
| CMU Pronouncing Dictionary (`cmudict.dict`, raw file on GitHub, cmusphinx/cmudict) | one more vote on an American transcription in `tools/pronounce_check.py` | fetched to `.tmp/`, ARPAbet converted to IPA by a fixed mapping in the tool, compared, discarded | 2026-09-16 (HTTP 200, about 3.6 MB) |
| English Wiktionary (`en.wiktionary.org` API, `action=parse`) | a hand check of a sample of British transcriptions in the pronunciation experiment only; not part of the pipeline | read in the session, the verdict recorded per word | 2026-09-16 (HTTP 200) |
| OpenRouter model list (`openrouter.ai/api/v1/models`) | confirming that the model slugs in `config/models.md` exist | fetched, read, discarded | 2026-09-16 (443 models) |

**Not consulted for anything:** frequency lists (wordfreq, Google Books Ngrams), published word lists (the New General Service List, the Oxford lists, the General Service List), WordNet, and any commercial or copyrighted dictionary. The defining vocabulary, the headword queue, and the frequency bands were built from the models' own judgment alone; the method is in `../wiki/decisions/defining-vocabulary.md`.

**Originality check:** about every tenth Routine run, `tools/originality_check.py` samples definitions for exact-phrase web searches and a reviewer question; the results go to `../reviews/originality/`.
