#!/usr/bin/env python3
"""One-time fix (2026-09-16): the first run of make_words.py labelled single-vote defining
words with a default part of speech; the sample was kept and the labels corrected.
This relabels items already collected in outputs/*.json to the labels now in words.tsv
(the label does not affect a non-heteronym's transcription; heteronyms were never mislabelled)."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
old = {r["word"]: r["pos"] for r in csv.DictReader(open(HERE.parent.parent / ".tmp" / "words-old.tsv", encoding="utf-8"), delimiter="\t")} if (HERE.parent.parent / ".tmp" / "words-old.tsv").exists() else {}
new_rows = list(csv.DictReader(open(HERE / "words.tsv", encoding="utf-8"), delimiter="\t"))
by_word = {}
for r in new_rows:
    by_word.setdefault(r["word"].lower(), []).append(r["pos"])
for p in sorted((HERE / "outputs").glob("*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    changed = 0
    for it in d["items"]:
        poses = by_word.get(it["w"].lower(), [])
        if len(poses) == 1 and it["pos"] != poses[0]:
            it["pos"] = poses[0]; changed += 1
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{p.name}: relabelled {changed}")
