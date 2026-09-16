#!/usr/bin/env python3
"""Claim headwords for this run so that overlapping runs never draft the same entry.

    python3 tools/claim.py --id                      # print this run's id (and write .tmp/run-id)
    python3 tools/claim.py --taken                   # every slug claimed on origin/main, origin/claude/*, or locally, plus existing entries
    python3 tools/claim.py "bank|n" "give up|phrv"   # claim these headwords (headword|pos[|homograph])
    python3 tools/claim.py --from-queue --n 20 [--band 1] [--source closure] [--pos n]
    python3 tools/claim.py --prune                   # delete claim files whose slugs all have entries on origin/main (lint mode)

A claim is headwords/claims/<run-id>.json (wiki/conventions.md section 3), written
before drafting and committed with the entries. `git fetch origin` runs first so
that claims on unmerged branches count. At most 20 slugs per claim. Slugs are
deterministic, so a duplicate that slips through is a duplicate file path and CI
rejects it.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

CAP = 20


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=eexlib.ROOT, capture_output=True, text=True)


def branch_name() -> str:
    r = git("rev-parse", "--abbrev-ref", "HEAD")
    return r.stdout.strip() if r.returncode == 0 else "local"


def run_id() -> str:
    p = eexlib.ROOT / ".tmp" / "run-id"
    if p.exists() and p.read_text(encoding="utf-8").strip():
        return p.read_text(encoding="utf-8").strip()
    b = branch_name()
    tail = b.rsplit("-", 1)[-1] if b.startswith("claude/") else "local"
    tail = re.sub(r"[^a-z0-9]", "", tail.lower()) or "local"
    rid = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + tail
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(rid + "\n", encoding="utf-8")
    return rid


def claim_files_on(ref: str) -> list[str]:
    r = git("ls-tree", "--name-only", ref, "headwords/claims/")
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip().endswith(".json")] if r.returncode == 0 else []


def slugs_in(ref: str, path: str) -> set[str]:
    r = git("show", f"{ref}:{path}")
    if r.returncode != 0:
        return set()
    try:
        return set(json.loads(r.stdout).get("slugs", []))
    except json.JSONDecodeError:
        return set()


def taken(fetch: bool = True) -> tuple[set[str], set[str]]:
    """(claimed slugs, existing entry slugs)."""
    if fetch:
        git("fetch", "origin", "--quiet")
    claimed: set[str] = set()
    refs = ["origin/main"]
    r = git("branch", "-r", "--list", "origin/claude/*")
    refs += [ln.strip() for ln in r.stdout.splitlines() if ln.strip() and "->" not in ln]
    for ref in refs:
        for path in claim_files_on(ref):
            claimed |= slugs_in(ref, path)
    for p in (eexlib.ROOT / "headwords" / "claims").glob("*.json"):
        try:
            claimed |= set(json.loads(p.read_text(encoding="utf-8")).get("slugs", []))
        except json.JSONDecodeError:
            pass
    existing = {p.stem for p in eexlib.iter_entry_paths()}
    r = git("ls-tree", "-r", "--name-only", "origin/main", "entries/")
    if r.returncode == 0:
        existing |= {Path(ln).stem for ln in r.stdout.splitlines() if ln.endswith(".json")}
    return claimed, existing


def write_claim(items: list[dict], mode: str) -> Path:
    rid = run_id()
    path = eexlib.ROOT / "headwords" / "claims" / f"{rid}.json"
    data = {"run_id": rid, "branch": branch_name(), "claimed_at": eexlib.utcnow_iso(), "mode": mode,
            "slugs": [it["slug"] for it in items], "items": items}
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        merged = {it["slug"]: it for it in old.get("items", [])}
        for it in items:
            merged[it["slug"]] = it
        if len(merged) > CAP:
            raise SystemExit(f"error: this run already claims {len(old.get('slugs', []))} slugs; the cap is {CAP}")
        data["items"] = list(merged.values()); data["slugs"] = list(merged.keys()); data["claimed_at"] = old.get("claimed_at", data["claimed_at"])
    path.parent.mkdir(parents=True, exist_ok=True)
    eexlib.save_json(path, data)
    return path


def parse_item(s: str) -> dict:
    parts = [x.strip() for x in s.split("|")]
    if len(parts) < 2:
        raise SystemExit(f"error: expected headword|pos[|homograph], got {s!r}")
    hw, pos = parts[0], parts[1]
    hom = int(parts[2]) if len(parts) > 2 else 1
    if pos not in eexlib.vocab_values("pos"):
        raise SystemExit(f"error: {pos!r} is not a part-of-speech code")
    return {"headword": hw, "pos": pos, "slug": eexlib.slugify(hw, pos, hom)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("items", nargs="*", help="headword|pos[|homograph]")
    ap.add_argument("--id", action="store_true")
    ap.add_argument("--taken", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--from-queue", action="store_true")
    ap.add_argument("--n", type=int, default=CAP)
    ap.add_argument("--band"); ap.add_argument("--source"); ap.add_argument("--pos")
    ap.add_argument("--mode", default="build")
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--prune", action="store_true")
    a = ap.parse_args()
    if a.id:
        print(run_id()); return 0
    if a.taken:
        claimed, existing = taken(fetch=not a.no_fetch)
        for s in sorted(claimed | existing):
            print(s)
        if not a.quiet:
            print(f"# {len(claimed)} claimed, {len(existing)} existing", file=sys.stderr)
        return 0
    if a.prune:
        git("fetch", "origin", "--quiet")
        r = git("ls-tree", "-r", "--name-only", "origin/main", "entries/")
        on_main = {Path(ln).stem for ln in r.stdout.splitlines() if ln.endswith(".json")}
        removed = 0
        for p in sorted((eexlib.ROOT / "headwords" / "claims").glob("*.json")):
            slugs = set(json.loads(p.read_text(encoding="utf-8")).get("slugs", []))
            if slugs and slugs <= on_main:
                p.unlink(); removed += 1; print(f"pruned {p.name}")
        print(f"pruned {removed} claim file(s)")
        return 0
    if a.from_queue:
        cmd = [sys.executable, str(HERE / "queue.py"), "next", "--n", str(min(a.n, CAP))]
        for flag, val in (("--band", a.band), ("--source", a.source), ("--pos", a.pos)):
            if val:
                cmd += [flag, val]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=eexlib.ROOT)
        items = []
        for ln in r.stdout.splitlines():
            slug, hw, pos, _band, _src = ln.split("\t")
            items.append({"headword": hw, "pos": pos, "slug": slug})
    else:
        items = [parse_item(s) for s in a.items]
    if not items:
        print("nothing to claim"); return 1
    if len(items) > CAP:
        raise SystemExit(f"error: {len(items)} slugs asked for; the cap is {CAP} per run")
    claimed, existing = taken(fetch=not a.no_fetch)
    clash = [it["slug"] for it in items if it["slug"] in claimed or it["slug"] in existing]
    if clash:
        raise SystemExit("error: already taken: " + ", ".join(clash))
    path = write_claim(items, a.mode)
    for it in items:
        subprocess.run([sys.executable, str(HERE / "queue.py"), "set", it["headword"], it["pos"], "claimed"], capture_output=True, text=True, cwd=eexlib.ROOT)
    print(f"claimed {len(items)} slug(s) in {path.relative_to(eexlib.ROOT)}:")
    for it in items:
        print("  " + it["slug"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
