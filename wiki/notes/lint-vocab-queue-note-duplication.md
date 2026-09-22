# `lint_vocab.py --queue` grows overlapping duplicate note text on repeat runs

Caught 2026-09-22, seventh lint pass, reading `headwords/queue.tsv` after `crossref.py --all --apply` and `lint_vocab.py --all --queue`.

## What was found

Two rows already `pending` from a prior lint pass (*achieve-n*, *permission-n*) grew a second, overlapping note segment this run:

- `achieve-n` before: `used in action-n senses[0].definition; pos guessed (no morphological signal), check before claiming; used in aim-n senses[0].definition; pos guessed (no morphological signal), check before claiming`
- `achieve-n` after: the same, plus `; used in action-n senses[0].definition; also in 1 other entry; pos guessed (no morphological signal), check before claiming`

The new segment repeats the same `action-n senses[0].definition` citation already present, just phrased slightly differently (`also in 1 other entry` added because this run's scan also found `aim-n`, whereas an earlier run's queuing pass evidently ran before `aim-n` existed or was scanned).

## Why it happens

`lint_vocab.py`'s `queue_lemmas()` (`tools/lint_vocab.py` line ~580) rebuilds one fresh note string per lemma from whatever citations *this run's* `--all` scan finds, and hands it to `queue.py add-batch`. `queue.py`'s merge (`add_rows`, line 87) only skips appending when the *entire new note string* is already a literal substring of the existing note (`n["note"] not in (r.get("note") or "")`). Because the freshly built note's wording (which citation comes first, whether `also in N other entries` is present) depends on the current run's scan order and set of entries, it is very unlikely to match a prior run's note string byte-for-byte, even when it reports the exact same underlying fact. The dedup check was written for a single new note against a stable existing one, not for two independently regenerated summaries of overlapping fact sets.

## Effect

Cosmetic so far — the row's `note` column (script-owned queue metadata, not a semantic field) grows redundant text on every `--all --queue` lint pass that rescans an already-queued lemma, rather than staying stable. Not yet long enough to threaten a cap, but it will keep growing every five runs as long as the affected lemma stays `pending`.

## Fix due a later run

`queue_lemmas()` or `add_rows()` needs to dedupe by *citation* (the `(slug, field)` pairs actually referenced) rather than by literal note-string containment — for example, parsing existing `used in X field` clauses out of the stored note before deciding whether a new citation is genuinely new. Out of scope for this lint pass (a script fix to shared tooling, not a semantic field, but a design call this pass did not make).
