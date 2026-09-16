# Usage labels: an original set

*Designed by the founding session, 2026-09-16, under the owner's ruling that the label set is original to this dictionary, in plain words, with no abbreviations. Charter: [PROJECT.md](../../PROJECT.md).*

**The five sets** (values and one-line meanings in `schema/vocabularies.json`):

- **register** (11): formal, informal, very informal, slang, humorous, literary, technical, vulgar, offensive, polite, childish.
- **region** (16, open-ended): American, British, Australian, New Zealand, Canadian, Irish, Scottish, Indian, Pakistani, Singaporean, Malaysian, Philippine, Nigerian, South African, Caribbean, online.
- **domain** (47): from agriculture to weather; the full list is in the vocabularies file.
- **currency** (5): old-fashioned, dated, old use, historical, new.
- **attitude** (6): approving, disapproving, ironic, euphemistic, affectionate, dismissive.

**Rationale.** Five orthogonal dimensions rather than one flat list, so that a word can be `informal` + `British` + `humorous` without a compound label. Register is a scale of formality with a few off-scale markers (slang, humorous, literary, technical) and two warning labels (vulgar, offensive) that always appear when they apply. `polite` and `childish` mark words chosen for the hearer rather than the setting. Region says where a word is *mainly* used, not exclusively; `online` exists because a growing share of new vocabulary belongs to no place. Domain is applied only when the word is tied to the field, never to every word that can appear in it; `human body` and `sex` exist because a learner's dictionary needs neutral anatomical and sexual vocabulary that is neither medical nor vulgar. Currency separates words that sound old (old-fashioned, dated, old use, a scale of receding use) from current words for past things (historical); `new` warns that a word may not last. Attitude marks the speaker's stance, which learners cannot infer from a definition.

**Why not the familiar abbreviations.** `fml`, `infml`, `BrE`, `AmE`, `derog`, `euph` are a barrier for the reader and a drift risk for the writer; plain words are both readable and closed.

**Growth.** A new value in any set is a logged decision (a new page here, linking back) in the same pull request as the first entry that uses it. Region is expected to grow with the World Englishes phase.
