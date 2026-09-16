#!/usr/bin/env python3
"""Build headwords/queue.tsv from the settled lists (wiki/decisions/defining-vocabulary.md):

  band 1, source defining : every defining-vocabulary lemma with its parts of speech (band1-rows.tsv)
  band 1, source band     : a non-defining candidate the panel's median put in band 1
  bands 2 and 3, source band: candidates with a median of 2 or 3
  (bands 4 and 5 are not queued; they arrive later through closure)

    python3 experiments/defining-vocabulary-v1/build_queue.py
"""
from __future__ import annotations

import csv
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main() -> int:
    dv = {w.strip() for w in (ROOT / "schema/defining-vocabulary.txt").read_text(encoding="utf-8").splitlines()
          if w.strip() and not w.startswith("#")}
    rows = list(csv.DictReader((HERE / "band1-rows.tsv").open(encoding="utf-8"), delimiter="\t"))
    seen = {(r["headword"], r["pos"]) for r in rows}
    bands = list(csv.DictReader((HERE / "bands.tsv").open(encoding="utf-8"), delimiter="\t"))
    added = Counter()
    for b in bands:
        key = (b["word"], b["pos"])
        if b["word"] in dv or key in seen:
            continue
        med = int(b["band_median"])
        if med > 3 or int(b["votes"]) < 2:
            continue
        rows.append({"headword": b["word"], "pos": b["pos"], "band": str(med), "source": "band",
                     "note": f"panel median {med} ({b['by_role']})"})
        seen.add(key)
        added[med] += 1
    with tempfile.NamedTemporaryFile("w", suffix=".tsv", delete=False, encoding="utf-8") as tf:
        tf.write("headword\tpos\tband\tsource\tnote\n")
        for r in rows:
            tf.write("\t".join(r[c] for c in ("headword", "pos", "band", "source", "note")) + "\n")
    r = subprocess.run([sys.executable, str(ROOT / "tools/queue.py"), "add-batch", tf.name], capture_output=True, text=True, cwd=ROOT)
    print(r.stdout.strip() or r.stderr.strip())
    Path(tf.name).unlink(missing_ok=True)
    print("band rows added by median:", dict(sorted(added.items())))
    subprocess.run([sys.executable, str(ROOT / "tools/queue.py"), "counts"], cwd=ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
