# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-17 by the founding session at the end of Stage D. Read `resume-prompt.md` first.*

## State

- The founding session is complete: scaffold, schema, vocabularies, decisions, the defining vocabulary (2,394 lemmas), the queue (4,281 rows), every pipeline and site tool, `routine-prompt.md` (dry-run tested), and 82 entries: 78 `reviewed`, 4 `draft` (*can*, *child*, *each other*, *explain*: reviewer-b has read them; reviewer-a was stopped by the budget cap).
- The site builds from the reviewed entries and passes `tools/site_check.py`; it goes live once the owner enables GitHub Pages with the "GitHub Actions" source.
- **The Routine must not be scheduled until the owner has reviewed the seed set** (`journal/2026-09-16-seed-review-guide.md`) and answered the four items in `journal/2026-09-17.md`. Comments go in `inbox/`.

## Queue (work top-down, one unit at a time)

1. **review**: finish the four `draft` entries: `python3 tools/review_panel.py --roles reviewer-a can-modal child-n each-other-pron explain-v` (about US$0.15), adjudicate (`--report`, `--decide`), fix, `validate.py`, set `provenance.status: reviewed`, rebuild the site.
2. Anything in `inbox/` (owner comments on the seed set outrank everything below).
3. **build** runs from the queue in its order (determiners and other function words first, then band 1): `python3 tools/next_mode.py` decides; 20 entries a run at most, ten to fifteen substantial ones are better.
4. **closure**: 692 cross-reference targets and two definition words have no entry yet (`crossref.py --queue` and `lint_vocab.py --queue` have queued them, source `crossref` and `closure`); they come up through the queue.
5. First **lint** pass due after the fifth Routine run: apply the 30-percent rule in `wiki/notes/reviewer-precision.md` to reviewer-a example-policy and grammar-code and reviewer-b example-policy if the next twenty decisions confirm them.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Model slugs live only in `config/models.md`; code names roles. Reasoning is switched off for pronunciation, word-list, and review calls except on Google models (which refuse; they run at low effort).
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- `jsonschema` is not installed and must not be required: `tools/schema_check.py` is the validator.
- Reviewer flags that repeat a house convention (one to three examples per phrase, no GA length marks, no stress mark on a monosyllable, entry-level labels covering senses, patterns only from the closed list, explanations on use-hard verbs) are rejected with that reason; do not relitigate them entry by entry.
- Adaptation notes hedge claims about other languages (*often*, *many*); "most" and "all" are rewritten, not defended.

## For the owner

- Four items, listed in `journal/2026-09-17.md`: enable GitHub Pages ("GitHub Actions" source); review the seed set and drop comments in `inbox/`; schedule the Routine; decide whether drafting moves to a flagship OpenRouter model. Open questions with working assumptions: `wiki/open-questions.md`.
