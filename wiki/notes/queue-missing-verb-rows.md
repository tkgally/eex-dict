# Queue: missing verb rows for noun-first lemmas

*Observed 2026-10-02 (thirty-first lint pass). Status: rows added by hand; a check for other parts of speech is due a later lint.*

## What happened

The build of 2026-10-02 drafted `cry-n` and linked its word family to `cry-v`. `crossref.py --queue` then found no queue row for the verb at all and added one at band 3, source `family`. *Cry* is one of the commonest verbs in English.

## Cause

The band 1 rows were built in 2026-09-16 from three models' proposals, one row per lemma and part of speech that two or more models proposed ([defining-vocabulary](../decisions/defining-vocabulary.md)). Where the models put a lemma in a noun chunk (feelings, the body, the home), only the noun row was created. The defining list itself is lemma-based, so *laugh* is on the list, but only `laugh|n` was queued.

## Scope

A scan of the defining list on 2026-10-02 found 926 lemmas with a noun row, no verb row, and no verb entry. Most are rightly noun-only (*aunt*, *bathroom*). By judgment, 43 verbs were queued by hand with source `defining`. Band 1 (12): *laugh, smile, shake, knock, smoke, plant, promise, report, sign, wave, escape, switch*. Band 2 (31): *frown, scratch, flood, glue, risk, sweat, trap, trick, display, demand, deal, debate, file, plug, pause, schedule, stress, tip, tour, track, upload, download, value, dust, joke, load, fish, drill, stroke, experiment, protest*. `cry|v` and `print|v` were raised to band 1. Each added row carries a note saying so.

## Still to do

The same gap probably exists the other way (verb-first lemmas missing a noun row) and for adjectives (*cold*, *dark*). A later lint should run the same scan for those pairs and judge each lemma by hand. No tool change is proposed: the judgment of which lemmas need a second part of speech is editorial.
