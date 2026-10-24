# Re-banding the queue and the entries (2026-10-24)

*The owner's ruling A1 and A4 of 2026-10-24 (`inbox/archive/20261024_owner_rulings.txt`; status table in [owner-rulings-2026-10-24](owner-rulings-2026-10-24.md)). It keeps [frequency-bands](frequency-bands.md) (editorial bands 1 to 5, no CEFR, script-owned) and replaces how a band is given.*

## Why

The founding bands ([defining-vocabulary](defining-vocabulary.md)) were given only to the words the panel proposed. Every row queued later by `crossref`, `family`, or `closure` took band 3 by default, and every defining-vocabulary row was forced into band 1. So *receive*, *finish* (verb), *interesting*, *boring*, *vacation*, and *airplane* waited at band 3, while *rug* and *governor* showed "very common" though the panel had voted band 2.

## The rule

1. **Who votes.** The word-list panel (`wordlist-1` to `wordlist-3` in `config/models.md`) gives a band from 1 to 5 to every pending queue row and every built entry, using the written scale below. Each word is voted on with its part of speech, so *run* (noun) and *run* (verb) get separate bands.
2. **How a band is settled.** The band is the lower median of the three votes (the middle vote; with a missing vote, the lower of the two). Where the votes span more than one band (for example 1, 2, 4), the session reads the item and settles it, as the founding session did; each settlement is listed in the vote's record.
3. **Target shares**, over the eventual 10,000 headwords: about 20, 25, 25, 20, and 10 percent for bands 1 to 5. They shaped the scale; they are not quotas.
4. **Defining vocabulary** stays a separate flag (`frequency.defining_vocabulary`) and no longer forces band 1.
5. **Restamping.** `tools/queue.py stamp` then writes the new bands into the built entries; `frequency.band` is a script-owned field.
6. **The founding votes** (`experiments/defining-vocabulary-v1/bands.tsv`) are used only as a cross-check; the vote's record reports how far the two agree.
7. **Siblings and phrasal verbs (A4)** that entries already use or point to (`about-adv`, `like-conj`, `run-n`, *turn out*, *come across*, *get along*, *give in*, *run into*, *go off*) are banded like everything else. If the panel puts one in band 1, it is built in band 1's turn.

## The scale (sent to every panel member, word for word)

- **1, very common** (about 2,000 headwords): words nearly every learner meets in the first years of study and every speaker uses every day: core everyday vocabulary and the function words (*house*, *eat*, *good*, *because*, *receive*).
- **2, common** (about 2,500): general everyday words an intermediate learner needs, frequent in conversation, the news, and school (*borrow*, *audience*, *careful*, *vacation*).
- **3, fairly common** (about 2,500): words an educated adult uses regularly, common in newspapers, at work, and in general reading (*appetite*, *reluctant*, *negotiate*).
- **4, less common** (about 2,000): words known to most adult native speakers but met mainly in particular topics or more specialized reading (*hamper*, *frugal*, *ventilate*).
- **5, rare** (about 1,000): words most native speakers recognize but seldom use: literary, technical, or specialized words a learner's dictionary still includes (*quell*, *serrated*, *archipelago*).

A word's band is for its most common present-day use in that part of speech, in any variety of English.

## What replaces the default band 3

**Chosen: `unbanded`.** A row that a tool adds with source `crossref`, `family`, or `closure` (and any row added without `--band`) gets the queue status `unbanded` and an empty band. `queue.py next` and `claim.py --from-queue` never hand it out. The next band vote (`tools/band_vote.py --unbanded`, run in a lint pass when unbanded rows exist) gives it a band and sets it `pending`. Asking the panel at queue time was the alternative; it was not chosen because it would put a paid call inside every lint and crossref run, and a few days' wait costs nothing while milestone 1 and band 2 come first ([build-order](build-order.md)).

`unbanded` is a new value of the closed vocabulary `queue_statuses`, added by this decision.

## Result (2026-10-24)

Carried out the same day; the full record, with the 30 biggest moves in each direction, is [the vote's README](../../experiments/band-vote-2026-10-24/README.md). 8,283 items banded for US$1.03: band 1 1,539 (19 percent), band 2 3,157 (38), band 3 2,813 (34), band 4 753 (9), band 5 21. The queue holds few rare words yet, because bands 4 and 5 arrive through closure, so the shares sit above the target in bands 2 and 3. The three votes were within one band on 8,086 items; the session settled the 197 wider splits and changed eight of them from the lower median. Against the founding votes: the same band on 79 percent of the 4,085 shared items, within one band on 99 percent. The named cases: *finish* (verb), *receive*, *interesting*, *boring* 3→1; *vacation*, *airplane* 3→2; *rug*, *governor* 1→2; `about-adv`, `run-n`, `turn-out-phrv`, `go-off-phrv` 3→1; `like-conj` queued and banded 1. Fifteen defining-vocabulary words that had no queue row at all were queued and banded, among them six of the grammar terms of [build-order](build-order.md).
