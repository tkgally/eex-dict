#!/usr/bin/env python3
"""Fetch the British IPA lines from English Wiktionary for the 100-word hand check
(design.md section 3) into .tmp/ so that the session can read them and record
agree/disagree verdicts. Nothing fetched is written inside the repository.

    python3 experiments/pronunciation-model-test-v1/wiktionary_fetch.py     # writes .tmp/wiktionary-british.txt
"""
from __future__ import annotations

import csv
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 20260916
QUOTA = {"defining": 40, "mid": 20, "rare": 20, "heteronym": 10, "loan": 10}
UA = "eex-dict-founding-session/0.1 (https://github.com/tkgally/eex-dict; verification only, nothing stored)"


def sample() -> list[dict]:
    rng = random.Random(SEED)
    with (HERE / "words.tsv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    out = []
    for stratum, n in QUOTA.items():
        pool = [r for r in rows if r["stratum"] == stratum]
        rng.shuffle(pool)
        out += pool[:n]
    return out


def fetch(word: str) -> list[str]:
    url = "https://en.wiktionary.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "parse", "page": word, "prop": "wikitext", "format": "json", "formatversion": "2"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.loads(r.read().decode("utf-8"))
    text = data.get("parse", {}).get("wikitext", "")
    # English section only
    m = re.search(r"==English==(.*?)(\n==[^=]|\Z)", text, re.S)
    sect = m.group(1) if m else text
    lines = [ln.strip() for ln in sect.splitlines() if "{{IPA|en|" in ln or "{{a|" in ln and "IPA" in ln]
    return lines


def main() -> int:
    out = ROOT / ".tmp" / "wiktionary-british.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = sample()
    with out.open("w", encoding="utf-8") as f:
        for r in rows:
            try:
                lines = fetch(r["word"])
            except Exception as e:  # noqa: BLE001
                lines = [f"(fetch failed: {e})"]
            f.write(f"### {r['word']} | {r['pos']} | {r['stratum']}\n")
            for ln in lines[:12]:
                f.write(ln[:300] + "\n")
            f.write("\n")
            time.sleep(0.3)
    print(f"wrote {out} for {len(rows)} words (temporary; not committed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
