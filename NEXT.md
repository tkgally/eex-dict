# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-18 by the session that processed the owner's feedback on the seed set. Read `resume-prompt.md` first.*

## State

- 82 entries: 78 `reviewed`, 4 `draft` (*can*, *child*, *each other*, *explain*: reviewer-b has read them; reviewer-a is still owed). Queue: 4,197 pending, 82 done.
- The owner's feedback of 2026-09-18 is processed: two decision pages (`wiki/decisions/inline-markup.md`, `wiki/decisions/part-of-speech-and-consistency.md`), style guide section 6 (the marks) and new rules in sections 4, 7, 11, 12, and 16, the tools and tests that render and check the marks, and a line in the Routine's review mode.
- Inline marks: 40 entries carry them in every prose field, added by hand; 42 carry `provenance.flags: markup-pending` and are converted by review runs, 20 per run, the flag removed when done. The site renders the marks (bold mention, italic illustration, bold headword in examples) and passed the browser check.
- `inbox/` is empty. The Routine may now be scheduled; the site goes live once the owner enables GitHub Pages.

## Queue (work top-down, one unit at a time)

1. **review**: the four `draft` entries first (`python3 tools/review_panel.py --roles reviewer-a can-modal child-n each-other-pron explain-v`, about US$0.15), adjudicate, set `reviewed`; then the `markup-pending` entries in blocks of 20 (panel, adjudicate, add the marks by hand field by field, remove the flag).
2. **build** from the queue in its order; `python3 tools/next_mode.py` decides (it currently says build). Entries the part-of-speech rule created are queued: *all* pron, *another* pron, *alone* adv, *favorite* n.
3. **closure**: 695 cross-reference targets and two definition words have no entry yet (sources `crossref`, `family`, `closure`); they come up through the queue.
4. First **lint** pass due after the fifth Routine run (`runs_since_lint` is now 2): apply the 30-percent rule in `wiki/notes/reviewer-precision.md`; check whether the new `consistency` verdict and the marks paragraph in the reviewer prompt produce noise.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them. The two pages dated 2026-09-18 are rulings from the owner's feedback.
- Marks: `**word**` and `*phrase*` only, never HTML, never a third syntax; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form; no script ever writes or converts a prose field, not even for the marks.
- Part of speech: a use of another part of speech gets its own entry and a pointer, never a sense. `be-v`, `have-v`, `do-v`, and `one-num` stay as they are until the owner answers open question 4.
- Pronunciation notes in plain words: `tools/validate.py` rejects *schwa*, *voiced*, *diphthong*, and the rest; describe a sound by comparison and stress by respelling.
- Model slugs live only in `config/models.md`; code names roles. `jsonschema` is not installed and must not be required.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- Reviewer flags that repeat a house convention are rejected with that reason; do not relitigate them entry by entry. Adaptation notes hedge claims about other languages (*often*, *many*); *most* and *all* are rewritten.

## For the owner

- Three items remain from `journal/2026-09-17.md`: enable GitHub Pages ("GitHub Actions" source); schedule the Routine on Sonnet 5 (the trigger prompt is one line: *Read `routine-prompt.md` in the repository root and follow it exactly*); decide the drafting model (assumption: in-session).
- New today (`journal/2026-09-18.md`): open question 4 in `wiki/open-questions.md`, whether *be*, *have*, *do* (auxiliary senses) and *one* (pronoun senses) should be split into separate entries under the part-of-speech rule (assumption: no, until you say so); and question 5, the look of the marks (bold and italic; one line of CSS each to change).
- `reviews/needs_curator.txt`: one line; the founding session's branch `claude/new-session-1yir52` is fully merged and can be deleted.
