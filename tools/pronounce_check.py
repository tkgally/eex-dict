#!/usr/bin/env python3
"""Check an entry's American and British IPA against a panel of models (and, for
American, the CMU Pronouncing Dictionary consulted at run time), and set the
transcription's ``status`` and ``checked_by``.

    python3 tools/pronounce_check.py <slug> [<slug> ...] [--threshold 2] [--no-cmu] [--dry-run]
    python3 tools/pronounce_check.py --panel-only <slug> ...      # skip the CMU consultation

The rule (wiki/decisions/pronunciation-pipeline.md, pre-registered in
experiments/pronunciation-model-test-v1/design.md section 6): votes are the panel
members named pronunciation-1, -2, -3 in config/models.md, plus CMU for American
when it is reachable and has the word.  ``verified`` = at least THRESHOLD votes
agree with the drafter's transcription under the phoneme-level normalization N2;
``disputed`` = fewer than THRESHOLD agree with the drafter and at least two votes
agree with each other on something else; ``unverified`` = anything else.

Only ``checked_by`` and ``status`` are written; the ``ipa`` strings are the
drafter's and are never rewritten by this tool.  The CMU file is fetched to
.tmp/ (gitignored) and nothing from it is written into the repository: an entry
records only ``cmudict:agree`` / ``cmudict:disagree`` / ``cmudict:absent``.
This module is also the library the pronunciation experiment uses, so the
prompt and the normalization live here and nowhere else.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

THRESHOLD = 2            # votes that must agree with the drafter (design §6; adjusted only by the note)
PANEL_ROLES = ["pronunciation-1", "pronunciation-2", "pronunciation-3"]
CMU_URL = "https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict"
CMU_TMP = ROOT / ".tmp" / "cmudict.dict"

PROMPT = (
    "For each word below give its pronunciation in IPA for General American and for Standard "
    "Southern British English (Received Pronunciation). Mark primary stress with ˈ and secondary "
    "stress with ˌ before the syllable, separate syllables with a period, and write no slashes or "
    "brackets. Use these symbols: American vowels i ɪ ɛ æ ɑ ɔ ʊ u ʌ ə ɚ ɝ eɪ oʊ aɪ aʊ ɔɪ; "
    "British vowels iː ɪ e æ ɑː ɒ ɔː ʊ uː ʌ ə ɜː eɪ əʊ aɪ aʊ ɔɪ ɪə eə ʊə; consonants p b t d k ɡ "
    "tʃ dʒ f v θ ð s z ʃ ʒ h m n ŋ l r w j. Give the pronunciation of the word as the part of "
    "speech shown. Return JSON: {\"items\": [{\"w\": \"word\", \"pos\": \"code\", \"american\": "
    "\"...\", \"british\": \"...\"}]} in the input order.\n\nWords (word|pos):\n"
)

ARPABET = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ", "B": "b", "CH": "tʃ",
    "D": "d", "DH": "ð", "EH": "ɛ", "ER": "ɝ", "EY": "eɪ", "F": "f", "G": "ɡ", "HH": "h",
    "IH": "ɪ", "IY": "i", "JH": "dʒ", "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ŋ",
    "OW": "oʊ", "OY": "ɔɪ", "P": "p", "R": "r", "S": "s", "SH": "ʃ", "T": "t", "TH": "θ",
    "UH": "ʊ", "UW": "u", "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ",
}
VOWELS = set("iɪeɛæaɑɒɔoʊuʌəɚɝɜɐyø")
STRESS = {"ˈ", "ˌ"}


# --- normalization ----------------------------------------------------------

def arpabet_to_ipa(phones: str) -> str:
    out = []
    for ph in phones.split():
        m = re.match(r"([A-Z]+)([012])?$", ph)
        if not m:
            continue
        base, stress = m.group(1), m.group(2)
        ipa = ARPABET.get(base, "")
        if base == "AH" and stress == "0":
            ipa = "ə"
        if base == "ER" and stress == "0":
            ipa = "ɚ"
        if stress == "1":
            ipa = "ˈ" + ipa
        elif stress == "2":
            ipa = "ˌ" + ipa
        out.append(ipa)
    return "".join(out)


def _move_stress_to_vowel(s: str) -> str:
    out, pending = [], None
    for ch in s:
        if ch in STRESS:
            pending = ch if pending != "ˈ" else pending  # primary wins if both queued
            continue
        if pending and ch in VOWELS:
            out.append(pending)
            pending = None
        out.append(ch)
    return "".join(out)


def normalize_n1(ipa: str) -> str:
    """Exact-match normalization: notation differences only (design §4)."""
    s = unicodedata.normalize("NFD", (ipa or "").strip())
    s = re.sub(r"[/\[\]()]", "", s)
    s = s.replace("ʧ", "tʃ").replace("ʤ", "dʒ").replace("ɹ", "r").replace("ɡ", "g").replace("ɾ", "t")
    s = s.replace("ɫ", "l").replace("ʍ", "w").replace("ˑ", "").replace("ː", "").replace(":", "")
    for c in "rlnm":                                   # syllabic consonants become ə plus the consonant
        s = s.replace("ə" + c + "̩", "ə" + c).replace(c + "̩", "ə" + c)
    s = s.replace("͡", "").replace("͜", "").replace("‿", "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("'", "ˈ").replace("ˌ", "ˌ").replace(",", "ˌ").replace(".", "").replace(" ", "").replace("-", "")
    s = _move_stress_to_vowel(s)
    return s


def normalize_n2(ipa: str, variety: str) -> str:
    """Phoneme-level normalization (design §4, amended §4a): N1 plus documented mergers."""
    s = normalize_n1(ipa)
    if "ˈ" not in s:                                   # a monosyllable written without a stress mark
        for i, ch in enumerate(s):
            if ch in VOWELS:
                s = s[:i] + "ˈ" + s[i:]
                break
    s = s.replace("ˌ", "")                             # secondary stress conventions differ between sources
    s = re.sub(r"a(?![ɪʊ])", "æ", s)
    s = re.sub(r"ɪ$", "i", s)
    s = re.sub(r"(?<![ˈeaɔ])ɪ", "ə", s)                # unstressed ɪ merges with ə (roses / Rosa's)
    s = re.sub(r"(?<!ˈ)ʌ", "ə", s)                     # unstressed ʌ merges with ə (un-, -um)
    s = s.replace("ŋk", "nk")                          # ŋ before k is automatic
    if variety == "american":
        s = s.replace("ɛ", "e").replace("ɒ", "ɑ")
        s = re.sub(r"ɔ(?![ɪr])", "ɑ", s)                # cot-caught merge, but for/far stay distinct
        s = s.replace("ær", "er")                      # marry-merry merger
        s = s.replace("ɚ", "ər").replace("ɝ", "ɜr").replace("ʌr", "ɜr").replace("ɜːr", "ɜr")
        s = s.replace("əʊ", "o").replace("oʊ", "o")
    else:
        s = s.replace("ɛ", "e").replace("oʊ", "əʊ").replace("ɝ", "ɜ").replace("ɚ", "ə")
        s = s.replace("eə", "ɛə").replace("ɛə", "eə")
    return s


def agree(a: str, b: str, variety: str) -> bool:
    if not a or not b:
        return False
    x, y = normalize_n2(a, variety), normalize_n2(b, variety)
    if "ˈ" not in x or "ˈ" not in y:                    # a source that omitted stress altogether
        x, y = x.replace("ˈ", ""), y.replace("ˈ", "")
    return x == y


# --- CMU consultation (run time only; nothing stored) -------------------------

def fetch_cmudict(offline: bool = False) -> dict[str, list[str]] | None:
    """word -> list of IPA strings, or None when unreachable. Kept in .tmp/, never committed."""
    if not CMU_TMP.exists():
        if offline:
            return None
        try:
            CMU_TMP.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(CMU_URL, timeout=60) as r:
                CMU_TMP.write_bytes(r.read())
        except Exception as e:  # noqa: BLE001
            print(f"cmudict unreachable ({e}); continuing with the panel only", file=sys.stderr)
            return None
    d: dict[str, list[str]] = {}
    for line in CMU_TMP.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line or line.startswith(";;;"):
            continue
        parts = line.split("#", 1)[0].split()
        if len(parts) < 2:
            continue
        word = re.sub(r"\(\d+\)$", "", parts[0]).lower()
        d.setdefault(word, []).append(arpabet_to_ipa(" ".join(parts[1:])))
    return d


# --- the panel ------------------------------------------------------------

def ask_panel(items: list[tuple[str, str]], roles: list[str], purpose: str, chunk: int = 50,
              temperature: float = 0.1) -> dict[str, dict[tuple[str, str], dict]]:
    """items = [(word, pos)]. Returns role -> {(word, pos): {"american":..., "british":..., "model":...}}."""
    import openrouter  # local import so the normalization functions work without a key
    out: dict[str, dict[tuple[str, str], dict]] = {r: {} for r in roles}
    for role in roles:
        model = openrouter.resolve_role(role)
        for i in range(0, len(items), chunk):
            batch = items[i:i + chunk]
            user = PROMPT + "\n".join(f"{w}|{p}" for w, p in batch)
            est = openrouter.estimate_cost(model, 500 + 8 * len(batch), 60 * len(batch))
            try:
                res = openrouter.call_with_budget(model, [{"role": "user", "content": user}],
                                                  purpose=f"{purpose}:{role}", estimate_usd=est,
                                                  max_tokens=60 * len(batch) + 600, temperature=temperature,
                                                  response_format={"type": "json_object"},
                                                  reasoning=openrouter.reasoning_for(model, "pronunciation"))
                data = openrouter.parse_json_reply(res["text"])
            except Exception as e:  # noqa: BLE001  (a failed chunk leaves this role's votes empty)
                print(f"{role}: chunk of {len(batch)} failed: {str(e)[:160]}", file=sys.stderr)
                continue
            for it in data.get("items", []) if isinstance(data, dict) else []:
                if not isinstance(it, dict):
                    continue
                key = (str(it.get("w", "")).strip().lower(), str(it.get("pos", "")).strip().lower())
                out[role][key] = {"american": str(it.get("american", "")), "british": str(it.get("british", "")),
                                  "model": res.get("model") or model, "cost_usd": res.get("cost")}
    return out


# --- the rule ---------------------------------------------------------------

def verdict(drafter: str, votes: dict[str, str], variety: str, threshold: int = THRESHOLD) -> tuple[str, str]:
    """votes: source name -> transcription ('' when the source had nothing).
    Returns (status, checked_by)."""
    agreeing = [src for src, ipa in votes.items() if ipa and agree(drafter, ipa, variety)]
    have = [src for src, ipa in votes.items() if ipa]
    parts = [f"agreement:{len(agreeing)}/{len(have)}"]
    if "cmudict" in votes:
        parts.append("cmudict:" + ("agree" if "cmudict" in agreeing else ("disagree" if votes["cmudict"] else "absent")))
    checked_by = ";".join(parts)
    if len(agreeing) >= threshold:
        return "verified", checked_by
    others = Counter(normalize_n2(ipa, variety) for src, ipa in votes.items()
                     if ipa and src not in agreeing)
    if others and others.most_common(1)[0][1] >= 2:
        return "disputed", checked_by
    return "unverified", checked_by


def update_disputed_flag(flags: list, any_disputed: bool, flag: str = "pronunciation-disputed") -> None:
    """Keep provenance.flags in sync with the current verdicts: present iff any variety is disputed."""
    if any_disputed and flag not in flags:
        flags.append(flag)
    elif not any_disputed and flag in flags:
        flags.remove(flag)


def cmu_votes(word: str, cmu: dict[str, list[str]] | None, drafter: str) -> str:
    """The CMU transcription used as the vote: the variant that agrees with the drafter if any, else the first."""
    if cmu is None:
        return ""
    forms = cmu.get(word.lower())
    if not forms:
        return ""
    for f in forms:
        if agree(drafter, f, "american"):
            return f
    return forms[0]


# --- CLI ----------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="+")
    ap.add_argument("--threshold", type=int, default=THRESHOLD)
    ap.add_argument("--no-cmu", "--panel-only", action="store_true", dest="no_cmu")
    ap.add_argument("--dry-run", action="store_true", help="print verdicts; write nothing")
    ap.add_argument("--roles", default=",".join(PANEL_ROLES))
    a = ap.parse_args()
    import eexlib
    entries = []
    for slug in a.slugs:
        p = eexlib.entry_path(slug)
        if not p.exists():
            print(f"ERROR no such entry: {slug}")
            return 2
        entries.append((p, eexlib.load_json(p)))
    items = []
    for _p, e in entries:
        if e["pronunciation"].get("american") or e["pronunciation"].get("british"):
            items.append((e["headword"].lower(), e["pos"]))
    if not items:
        print("nothing to check")
        return 0
    panel = ask_panel(items, a.roles.split(","), purpose="pronounce_check")
    cmu = None if a.no_cmu else fetch_cmudict()
    changed = 0
    for p, e in entries:
        key = (e["headword"].lower(), e["pos"])
        any_disputed = False
        any_checked = False
        for variety in ("american", "british"):
            tr = e["pronunciation"].get(variety)
            if not tr:
                continue
            votes = {role: (panel[role].get(key) or {}).get(variety, "") for role in panel}
            if variety == "american" and cmu is not None and " " not in key[0]:
                votes["cmudict"] = cmu_votes(key[0], cmu, tr["ipa"])
            status, checked_by = verdict(tr["ipa"], votes, variety, a.threshold)
            print(f"{e['slug']:24s} {variety:9s} {tr['ipa']:22s} -> {status:10s} {checked_by}")
            any_checked = True
            if status == "disputed":
                any_disputed = True
            if not a.dry_run:
                tr["status"], tr["checked_by"] = status, checked_by
                changed += 1
        if not a.dry_run and any_checked:
            update_disputed_flag(e["provenance"].setdefault("flags", []), any_disputed)
        if not a.dry_run:
            e["provenance"]["modified"] = eexlib.utcnow_iso()
            eexlib.save_json(p, e)
    if not a.dry_run:
        print(f"updated {changed} transcription(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
