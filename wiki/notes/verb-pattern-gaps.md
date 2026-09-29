# Verb-pattern gaps in the closed list

*Observed 2026-09-29 (build, *show-v*). Status: open; no change made.*

The closed list `verb_patterns` in `schema/vocabularies.json` has **verb + wh-word + to-infinitive** (*decide what to do*) but no **verb + object + wh-word + to-infinitive** (*show us where to put the coats*, *tell me how to get there*, *teach her what to say*). reviewer-b flagged the object-less value on *show* sense 2 as wrong, and it was.

Working practice: use **verb + object + wh-clause** for these examples, the nearest value that has the object.

A later run may add the missing value by a logged decision, in the same pull request as the first entry that needs it (`CLAUDE.md`, rule 3). The likely users are *show*, *tell*, *teach*, *ask*, *advise*, and *remind*; check how those entries label such examples before adding it.
