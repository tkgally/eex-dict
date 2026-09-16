# Slugs, IDs, and URLs

*Decided by the founding session, 2026-09-16, under the owner's instruction that URLs and IDs are the session's call; the ruling that nothing is ever renumbered or deleted is the owner's. Charter: [PROJECT.md](../../PROJECT.md).*

**Decision.** The slug is the ID. Slug = headword lowercased, spaces to hyphens, apostrophes and periods dropped, non-ASCII letters transliterated, then a hyphen and the part-of-speech code; a later homograph takes `-2`, `-3` in creation order. Idiom sub-entries have a `sub_id` unique within the entry and are addressed `<slug>#<sub_id>`. Site pages are one per headword (`w/<headword>.html`) with anchors `#<slug>` and `#<slug>-<sub_id>`. The file path is a function of the slug (`entries/<shard>/<slug>.json`; shard = first two letters, or one, or `0-9`).

**Why deterministic slugs.** Two overlapping runs in the earlier project claimed the same numeric IDs because each saw only its own container. A deterministic slug makes a duplicate a duplicate file path, which CI rejects, and lets claims name the slug before the entry exists.

**Renames.** Add a line to `headwords/redirects.json`, keep the old file as a stub pointing forward, let the site emit a redirect page. Exact rules: [conventions](../conventions.md) section 2.
