#!/usr/bin/env python3
"""Put every IPA transcription into the house form (the owner's ruling B4 (iv) of 2026-10-24,
wiki/decisions/consistency-rules.md): a stress mark opens its syllable and is itself the
syllable break, so a period never stands directly before or after one.

    python3 tools/ipa_format.py            # dry run: count and list what would change
    python3 tools/ipa_format.py --apply    # rewrite the entries

A narrow, owner-approved exception to CLAUDE.md rule 2.  The script touches only IPA strings
(``pronunciation.american.ipa``, ``.british.ipa``, ``.variants[].ipa``, and the same under
``senses[].pronunciation``) and, so that an owner's ruling still finds its transcription, the
copy of the string inside an ``owner-ruling:<date>:<ipa>`` part of ``checked_by`` (a
script-owned field).  It moves nothing but periods: for every string it changes, it proves
that the old and the new string are equal once every period is removed, and it refuses the
whole run (writing nothing) if any string fails that proof.  No other field and no other
character is touched; ``provenance.modified`` is left as it is, as for ``validate.py
--fix-format``.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

OWNER_PART = re.compile(r"^(owner-ruling:\d{4}-\d{2}-\d{2}:)(.*)$")


def transcriptions(pron):
    """Yield (label, dict holding an ``ipa`` key) for every transcription of a pronunciation block."""
    if not isinstance(pron, dict):
        return
    for side in ("american", "british"):
        if isinstance(pron.get(side), dict):
            yield side, pron[side]
    for i, v in enumerate(pron.get("variants") or []):
        if isinstance(v, dict):
            yield "variants[%d]" % i, v


def blocks(entry):
    yield "pronunciation", entry.get("pronunciation")
    for i, s in enumerate(entry.get("senses") or []):
        if isinstance(s, dict) and s.get("pronunciation"):
            yield "senses[%d].pronunciation" % i, s["pronunciation"]


def format_entry(entry):
    """Apply the house form in place; return ``[(field, old, new)]``.  Raises ValueError on a failed proof."""
    changes = []
    for where, pron in blocks(entry):
        for label, tr in transcriptions(pron):
            old = tr.get("ipa")
            new = eexlib.ipa_house_form(old)
            if isinstance(old, str) and new != old:
                if not eexlib.ipa_only_periods_moved(old, new):
                    raise ValueError("%s.%s.ipa: %r -> %r changes more than periods" % (where, label, old, new))
                tr["ipa"] = new
                changes.append(("%s.%s.ipa" % (where, label), old, new))
            cb = tr.get("checked_by")
            if isinstance(cb, str) and "owner-ruling:" in cb:
                parts = cb.split(";")
                for k, part in enumerate(parts):
                    m = OWNER_PART.match(part)
                    if m:
                        fixed = eexlib.ipa_house_form(m.group(2))
                        if fixed != m.group(2):
                            if not eexlib.ipa_only_periods_moved(m.group(2), fixed):
                                raise ValueError("%s.%s.checked_by: %r changes more than periods" % (where, label, part))
                            parts[k] = m.group(1) + fixed
                new_cb = ";".join(parts)
                if new_cb != cb:
                    tr["checked_by"] = new_cb
                    changes.append(("%s.%s.checked_by" % (where, label), cb, new_cb))
    return changes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write the entries (default: dry run)")
    ap.add_argument("--root", default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    plan = []
    for path, e in eexlib.iter_entries(a.root):
        if eexlib.is_redirect_stub(e):
            continue
        try:
            changes = format_entry(e)
        except ValueError as exc:
            print("REFUSED %s: %s; nothing written" % (e.get("slug"), exc))
            return 1
        if changes:
            plan.append((path, e, changes))
    n_ipa = sum(1 for _p, _e, ch in plan for f, _o, _n in ch if f.endswith(".ipa"))
    n_cb = sum(1 for _p, _e, ch in plan for f, _o, _n in ch if f.endswith(".checked_by"))
    if not a.quiet:
        for _p, e, ch in plan:
            for field, old, new in ch:
                print("%s %s: %s -> %s" % (e["slug"], field, old, new))
    if a.apply:
        for path, e, _ch in plan:
            eexlib.save_json(path, e)
    print("ipa_format: %d transcriptions and %d owner-ruling references in %d entries %s; every change proved "
          "to move only periods" % (n_ipa, n_cb, len(plan), "rewritten" if a.apply else "would change (dry run)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
