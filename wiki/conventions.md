# Conventions

*The schema of this knowledge base and every file format the project's tools read or write. `PROJECT.md` says what the dictionary is; this page says how its files are shaped. A change here is a logged decision (`wiki/decisions/`), never drift.*

## 1. The wiki

- **Page types.** `conventions.md` (this page); `style-guide.md` (house style, cap 3,500 words); `decisions/<topic>.md` (one decision per page, dated, with the owner's ruling or the session's rationale; never rewritten, superseded by a new page that links back); `notes/<topic>.md` (an observed problem, a method record, an experiment result); `open-questions.md` (questions for the owner, each with a working assumption); `index.md` (one line per page); `log.md` (append-only, newest first, header `## [YYYY-MM-DD] <operation> | <title>`; operations: `ingest`, `query`, `lint`, `decision`, `build`, `review`, `closure`, `site`, `originality`, `setup`).
- **Naming.** Lowercase, hyphens, `.md`. Decision and note pages are named for their topic, not their date.
- **Linking.** Relative markdown links; `tools/check_links.py` must pass before every commit. Link to a decision page whenever a rule is cited.
- **Provenance.** A factual claim on a wiki page cites its source (a decision page, an experiment file, a run's review file, or an external reference with title, URL, and access date) or is labelled as the project's own inference.
- **Caps** (enforced by `tools/check_caps.py`): the wiki excluding `index.md`, `log.md`, and `decisions/` at most 30,000 words; each log entry at most 200 words; `style-guide.md` at most 3,500 words; `CLAUDE.md` 1,500 words; `resume-prompt.md` 800 words; `routine-prompt.md` 2,500 words; `NEXT.md` 60 lines.
- **What the wiki does not hold.** A research library on lexicography. A principle worth keeping goes into the style guide or a decision page.

## 2. Entries

One JSON file per entry at `entries/<shard>/<slug>.json`, shaped by `schema/entry.schema.json`, values from `schema/vocabularies.json`. UTF-8, two-space indentation, keys in schema order, trailing newline; `tools/validate.py --fix-format` rewrites a file into this form without touching content.

**Slug and id.** `id` equals `slug`. Slug = headword lowercased; spaces to hyphens; apostrophes and periods dropped; non-ASCII letters transliterated by Unicode decomposition (`café` to `cafe`, `naïve` to `naive`); any remaining character that is not a letter, digit, or hyphen dropped; runs of hyphens collapsed; then `-` plus the part-of-speech code; a second homograph of the same part of speech takes `-2`, a third `-3`, numbered in creation order and never reassigned. Examples: `bank-n`, `bank-v`, `give-up-phrv`, `in-spite-of-prep`, `un-prefix`, `asap-abbr`, `oclock-adv`, `bat-n-2`. `tools/entry_path.py <slug>` prints the path; `tools/entry_path.py --slug "<headword>" <pos> [homograph]` prints the slug.

**Shard.** The leading run of ASCII letters of the slug: its first two letters when it has two or more, its one letter when it has one, and `0-9` when the slug starts with a digit. `entries/ba/bank-n.json`, `entries/a/a-det.json`, `entries/x/x-ray-n.json`, `entries/0-9/3d-adj.json`.

**Homographs.** Same spelling and same part of speech get separate entries only when unrelated in meaning and origin (`bat` the animal, `bat` the club). Related meanings are senses of one entry.

**Phrases.** Idioms and fixed phrases live in `phrases[]` of a keyword entry with a `sub_id` = the phrase text slugified without a part-of-speech suffix (`break-the-bank`, `give-someone-a-hand`); the address is `<slug>#<sub_id>`. The keyword is the first noun in the phrase, else the first verb, else the first content word; the style guide has the details.

**Renames.** Slugs are permanent. A rename adds `"old-slug": "new-slug"` to `headwords/redirects.json`, keeps the old file as a stub `{"schema_version": "1.0", "slug": "old-slug", "redirect_to": "new-slug", "renamed": "YYYY-MM-DD", "reason": "..."}`, and the site emits a redirect page. Nothing is ever deleted or renumbered.

**Fields beyond the founding prompt** (extensions recorded here as the schema requires): `senses[].grammar.transitivity` (a verb sense's transitivity, separate from its patterns); `inflections.note` (a plain remark shown on the site, such as an alternative past tense); `variants[].note`; `pronunciation.variants[]` as `{ipa, region, note}`; `word_family[]` as `{slug, form, note}` where `form` overrides the displayed word when the slug loses characters (`oclock-adv` displays as `o'clock`); cross-references (`synonyms`, `antonyms`, `compare`, `see_also`) as `{slug, note}` naming the target by its deterministic slug whether or not the entry exists yet; `synonym_discrimination` as `{words: [slugs], note}`; `etymology` as `{text, sources_consulted (at least two names), checked (date)}`; `subsenses[]` with a `letter`; `provenance.run_id` and `provenance.notes`; `provenance.reviews[]` as `{run_id, role, model, date, file, ok, issues, blocking}`. `provenance.drafted_by` is the model slug of the `drafter` role in `config/models.md` at drafting time (`anthropic/claude-sonnet-5` for Routine runs); the founding session's seed set records the founding model as `claude-fable-5-1`.

**Prose fields** (definition, explanation, example text and note, collocation items, notes of every kind, adaptation notes) are plain text with two inline marks ([inline-markup](decisions/inline-markup.md)): `**word**` around a word named as a word (in an example, a hand-marked form of the headword), `*phrase*` around language quoted as an illustration. A mark is paired, has no space just inside it, stays on one line, and does not nest; collocation items, phrase texts, and the incorrect and correct forms of a learner error carry none; an example carries only the double mark. The site marks the headword in examples itself from the entry's forms. No abbreviations: the deny list in `tools/validate.py` is `sb`, `sth`, `e.g.`, `i.e.`, `etc.`, `approx.`, `vs.`, `cf.`, `esp.`, `usu.`, `NB`; no technical terms (`schwa`, `voiced`, `diphthong`, the list is in `tools/validate.py`) in pronunciation notes. Links are placed at build time by `tools/link_words.py`; an author forces a target with `[[slug|visible text]]` only when the automatic link would be ambiguous, and a mark goes around the override (`**[[all-pron|all]]**`), never inside it.

**Counts and caps checked by `validate.py`.** Two to four examples per sense; one to four per subsense; one to three per phrase. Each of the five adaptation notes at most 60 words. Both `pronunciation.american` and `pronunciation.british` are required for every part of speech except `prefix`, `suffix`, `comb`, and `abbr`, where they may be null. `core_idea` is required when an entry has three or more senses (a warning, not an error, below three). At most 40 entries with `provenance.status: draft` may exist at once; `validate.py --gate` fails above that.

**Flags.** `provenance.flags` values are the closed set `provenance_flags`; `markup-pending` marks an entry whose prose predates the inline marks of 2026-09-18 and is removed by the review run that marks it up.

**Status.** `draft` until the pipeline in `CLAUDE.md` has run; `reviewed` only when schema-valid, inflections and pronunciation `verified` or explicitly flagged in `provenance.flags`, both reviewer records present in `provenance.reviews`, and every blocking issue adjudicated in `reviews/decisions.jsonl`. The site publishes `reviewed` entries only.

**The `l1` map.** Keyed by BCP-47 language code, empty until an adaptation begins. Future shape of a value: `{"equivalents": [], "note": null, "status": "draft"}`. Japanese is seeded on about 200 entries after milestone 1.

## 3. Runs, claims, and the queue

**Run id.** `<UTC time>Z-<branch tail>`, for example `20260916T130600Z-1yir52`: the time the run started, then the part of the git branch name after its last hyphen (`local` off a `claude/*` branch). `tools/claim.py` computes it and writes it to `.tmp/run-id` for the rest of the run.

**Claim file.** `headwords/claims/<run-id>.json`: `{"run_id", "branch", "claimed_at", "mode", "slugs": [...], "items": [{"headword", "pos", "slug"}]}`. Written before drafting, committed with the entries. A run reads every claim file on `origin/main` and on every `origin/claude/*` branch and treats every listed slug as taken. The lint mode prunes claim files whose slugs all have entries on `main`; `queue.py sync` (run by `claim.py --prune` and by every build) resets a `claimed` queue row that no claim file lists to `pending`.

**Queue.** `headwords/queue.tsv`, tab-separated with a header: `headword	pos	band	source	status	added	note`. One row per headword and part of speech; `band` 1 to 5; `source` and `status` from the vocabularies; `added` an ISO date; `note` free text (the declined reason, the entry that used the word). Only `tools/queue.py` edits it. `queue.py next` works the queue by band, then by part of speech (determiners, pronouns, prepositions, conjunctions, modals, verbs, nouns, adjectives, adverbs, then the rest, affixes and abbreviations last), then alphabetically.

**Redirects.** `headwords/redirects.json`: a flat object, old slug to new slug.

## 4. Reviews and adjudication

**Review file.** `reviews/<run-id>/<slug>.json`: `{"run_id", "slug", "entry_modified", "reviewers": [{"role", "model", "requested_at", "cost_usd", "tokens_in", "tokens_out", "verdicts": [{"field", "verdict", "quote", "severity", "family", "reason"}], "summary", "error"}]}`. `field` is a path such as `senses[0].definition` or `pronunciation.british`; `verdict` is `ok` or `issue`; on `issue`, `quote` is the exact text objected to, `severity` is `blocking` or `minor`, `family` is an issue family, `reason` is one line. Every field in the checklist gets a verdict.

**Decision ledger.** `reviews/decisions.jsonl`, append-only, one line per adjudicated issue: `{"ts", "run_id", "slug", "field", "role", "family", "severity", "decision", "note"}` with `decision` `apply`, `reject`, or `escalate` and `note` at most fifteen words. A noise family rejected in bulk gets one line with an `"n"` count and no `slug`. Reviewer precision = applied divided by (applied + rejected), computed by `tools/metrics.py` per role and family.

**Curator queue.** `reviews/needs_curator.txt`: one line per item, `<UTC time> <slug or -> <topic>: <question> | assumption: <what the session did meanwhile>`. Closed items are moved to the bottom under a `## Resolved` heading with the ruling and date.

**Originality.** `reviews/originality/<date>.md`: the sample, the searches run, the reviewer answers, the verdict.

## 5. Spending

`config/budget-ledger.json`: `{"daily_cap_usd", "date", "spent_usd", "calls": [{"ts", "run_id", "purpose", "model", "cost_usd", "tokens_in", "tokens_out"}], "history": {"YYYY-MM-DD": spent}}`. Only `tools/spend.py` writes it; `check --cost <estimate>` refuses when the estimate would exceed the cap for the current UTC day, `record --cost <actual>` appends the billed amount from the response's `usage.cost`. The key is read from `OPENROUTER_API_KEY` and never written anywhere.

## 6. Metrics, journal, inbox

- `metrics/history.jsonl`: one line per run from `tools/metrics.py`: counts by status and band, defining-vocabulary coverage, closure gap, queue counts, review counts and precision, spend, site build status.
- `journal/YYYY-MM-DD.md` (a `-2`, `-3` suffix when a day has several sessions): the owner report per `framework.md` section 4, published on the site. A guide for the owner is `journal/<date>-<topic>.md`.
- `inbox/`: anything there is unprocessed owner input and outranks the queue; processed files move to `inbox/archive/` with a line in `wiki/log.md`.
- `sources/README.md`: the register of resources consulted at run time. `sources/` holds markdown only; CI rejects anything else.

## 7. Configuration

- `config/models.md`: the roles (drafter, reviewer-a, reviewer-b, pronunciation panel, word-list panel) and the model slug behind each, with the date it was verified against the OpenRouter model list. Code refers to roles, never to slugs.
- `config/budget.md`: the spending rule. `config/routine-config.json`: mode weights, triggers, and per-run caps read by `tools/next_mode.py`.
