#!/usr/bin/env python3
"""Send entries to the two reviewers (roles reviewer-a and reviewer-b in
config/models.md) with a field-by-field checklist and closed verdicts, write
reviews/<run-id>/<slug>.json, and record the review in the entry's provenance.

    python3 tools/review_panel.py <slug> [<slug> ...] [--roles reviewer-a,reviewer-b] [--dry-run]
    python3 tools/review_panel.py --report <slug>            # list the open issues from the latest review file
    python3 tools/review_panel.py --decide <slug> --field <field> --role <role> --decision apply|reject|escalate --note "..."

Every field in the checklist gets a verdict: ``ok`` or ``issue``; an issue
carries the exact text objected to, a severity (``blocking`` or ``minor``), a
family from schema/vocabularies.json, and a one-line reason. Costs go through
tools/spend.py. The reviewer never rewrites the entry: the session reads each
blocking issue, decides, and logs the decision with --decide (one line in
reviews/decisions.jsonl, wiki/conventions.md section 4).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import eexlib  # noqa: E402

DEFAULT_ROLES = ["reviewer-a", "reviewer-b"]

# Switched off by the 2026-09-19 lint run under the 30-percent rule (routine-prompt.md,
# lint mode): a (role, family) pair with precision under 30 percent over twenty or more
# adjudicated decisions, measured by `tools/metrics.py --precision` over all-time
# reviews/decisions.jsonl. Figures and rationale in wiki/notes/reviewer-precision.md.
# An issue from a switched-off pair is downgraded to "ok" before it reaches adjudication,
# so it is never counted, never printed, and never logged as a decision.
DISABLED_FAMILIES = {
    ("reviewer-a", "example-policy"),   # 0.16 over 44
    ("reviewer-a", "grammar-code"),     # 0.27 over 75
    ("reviewer-a", "sense-structure"),  # 0.29 over 48
    ("reviewer-b", "example-policy"),   # 0.05 over 83
    ("reviewer-b", "explanation"),      # 0.24 over 21
}

SYSTEM = """You are a senior lexicographer checking an entry of an English-English learner's dictionary for intermediate and advanced learners (CEFR B1 to C2). American English is the dictionary's primary variety; British forms are recorded in variant fields. The entry was written by a language model and must be checked field by field for factual and linguistic correctness, not for taste. You answer with JSON only.

House rules you check against:
- Definitions are phrasal (a noun by a noun phrase, a verb by a base-form verb phrase without "to"), present tense, not circular, no padding such as "used to describe" or "refers to", and written in plain words an intermediate learner knows. Exception: for function words, discourse markers, and interjections the formula "used to ..." / "used when ..." is the house style and is never an issue.
- An explanation field exists only for words whose use is easier to explain than to define (function words, discourse markers, modals, affixes).
- Senses: a new sense only where learners need a different definition, grammar, collocation set, or translation; most useful first; signposts of one to three words; a core-idea line on entries with three or more senses.
- Examples: two to four per sense, natural American English, showing typical collocations and patterns; NO checkable real-world facts (dates, statistics, named events, science claims, prices), no brand names, culturally neutral settings, personal names only from: Kim, Mari, Sam, Ana, Lee, Omar, Yuki, Ravi, Sara.
- Grammar values, labels, and patterns must be right for the sense (countability, transitivity, verb patterns, adjective position, register, region, domain, currency, attitude).
- Pronunciation: General American and British IPA; a one-syllable word carries no stress mark (that is the house convention, not an issue); multi-word headwords have a space between words. Inflections must be the real forms.
- Collocations must be genuinely typical; cross-references must be real synonyms, antonyms, or confusable words; learner errors must be errors learners actually make and the correction must be right.
- Notes of every kind (usage note, synonym discrimination, etymology, adaptation notes) must be factually true; adaptation notes must be language-neutral (never naming a language) and at most 60 words.
- No abbreviations anywhere in prose: never sb, sth, e.g., i.e., etc.
- Inline marks in prose are house style, not an issue: double asterisks around a word named as a word (**all** goes before a plural noun), single asterisks around a phrase quoted as an illustration (*all the students*). Example sentences carry no marks (the site marks the headword itself) unless the headword appears in an irregular or separated form, which is then marked with double asterisks. A plainly wrong mark (a quoted phrase in double asterisks, a mention in single ones) is a minor spelling-or-format issue.
- One entry per headword and part of speech: a use that belongs to another part of speech (a determiner's pronoun use, an adjective's adverb use, a noun's verb use) is not a sense, a subsense, or an example of this entry; it belongs in its own entry, and this entry may only point to it in one clause. Flag such a use under headword_and_pos.
- The fields of an entry must agree with each other: what an explanation, a usage note, a synonym-discrimination note, a learner-error note, or an adaptation note says about the word must not contradict another field or the grammar values. A statement about where a word comes from belongs only in the etymology field; elsewhere it is an issue.
- Pronunciation notes and pronunciation adaptation notes are written in plain words for a learner (a sound compared with a familiar word, a respelling in capitals for stress); technical terms such as schwa, rhotic, voiced, or diphthong are an issue.
- House conventions that are NOT issues: a core-idea line on a two-sense entry (optional there); periods in IPA (they mark syllable breaks); no length marks in General American IPA; one form per inflection slot with alternatives in its note; "online" as a region label; one to three examples on a phrase; "used to ..." definitions for function words; an adaptation note that mentions "some languages", "many languages", a country, or a variety (language-neutral means it is not written for one target language); an entry-level label (vulgar, informal) that covers every sense and phrase without being repeated; no stress mark on a monosyllable; a British transcription with no linking r; a plain-English respelling in a pronunciation note; an etymology that names source languages; an explanation field on a high-frequency verb, modal, or abbreviation whose use is harder than its meaning; grammar patterns only from the closed list (no adjective, noun, or determiner patterns: those go in collocations); compounds in a word family; a subsense with its own countability; a generic example (the wettest spring on record) that states no real-world fact.
- Etymology appears only when it helps a learner use the word today; a wrong or doubtful origin is an issue.

Severity: "blocking" for anything wrong, misleading, ungrammatical, unnatural, unsafe for a learner to copy, or against the example rules; "minor" for something worth improving that a learner could still safely use. Quote the exact text you object to. Do not flag a definition for being plain, short, or unlike a published dictionary's; plain and short is the house style. Do not flag the absence of a sense unless it is a common current sense a learner would need."""

FAMILIES_HINT = ("definition-meaning, definition-style, definition-vocabulary, explanation, example-unnatural, example-grammar, "
                 "example-policy, grammar-code, label, collocation, cross-reference, learner-error, synonym-discrimination, "
                 "usage-note, etymology, pronunciation, inflection, sense-structure, phrase, adaptation, spelling-or-format, other")


def checklist(entry: dict) -> list[str]:
    fields = ["headword_and_pos", "variants", "pronunciation.american", "pronunciation.british", "inflections", "labels", "core_idea"]
    for i, s in enumerate(entry.get("senses", [])):
        base = f"senses[{i}]"
        fields += [f"{base}.signpost", f"{base}.definition", f"{base}.explanation", f"{base}.grammar", f"{base}.labels",
                   f"{base}.examples", f"{base}.collocations", f"{base}.cross_references", f"{base}.adaptation"]
        for j, _ in enumerate(s.get("subsenses", [])):
            fields += [f"{base}.subsenses[{j}].definition", f"{base}.subsenses[{j}].examples"]
        if s.get("pronunciation"):
            fields.append(f"{base}.pronunciation")
    for i, _p in enumerate(entry.get("phrases", [])):
        base = f"phrases[{i}]"
        fields += [f"{base}.text_and_placement", f"{base}.definition", f"{base}.labels", f"{base}.examples", f"{base}.adaptation"]
    fields += ["word_family", "synonym_discrimination", "usage_note", "learner_errors", "etymology", "see_also",
               "adaptation", "sense_structure", "consistency"]
    return fields


def strip_for_review(entry: dict) -> dict:
    e = json.loads(json.dumps(entry))
    e.pop("provenance", None)
    e.pop("id", None)
    for tr in ("american", "british"):
        t = (e.get("pronunciation") or {}).get(tr)
        if isinstance(t, dict):
            t.pop("source", None); t.pop("checked_by", None); t.pop("status", None)
    inf = e.get("inflections") or {}
    for k in ("source", "status", "regular"):
        inf.pop(k, None)
    e.pop("l1", None)
    for s in e.get("senses", []):
        s.pop("l1", None)
    for p in e.get("phrases", []):
        p.pop("l1", None)
    return e


def user_prompt(entry: dict) -> str:
    fields = checklist(entry)
    return (
        "Check every field of this entry. For EACH field name in the checklist return one verdict object. "
        "Fields: " + ", ".join(fields) + ".\n\n"
        "Return JSON of the form {\"verdicts\": [{\"field\": \"<name from the checklist>\", \"verdict\": \"ok\" | \"issue\", "
        "\"quote\": \"<exact text objected to, or null>\", \"severity\": \"blocking\" | \"minor\" | null, "
        "\"family\": \"<one of: " + FAMILIES_HINT + ">\" | null, \"reason\": \"<one line, or null>\"}], "
        "\"summary\": \"<one or two sentences>\"}. A field with several problems gets several objects with the same field name. "
        "\"sense_structure\" is the verdict on the set of senses as a whole (missing, over-split, misordered); "
        "\"headword_and_pos\" is whether the headword, part of speech, and homograph split are right and whether every sense and every use "
        "described belongs to this part of speech; "
        "\"consistency\" is whether the fields agree with one another across the whole entry (an explanation against a usage note, a note "
        "against the grammar values, a claim made twice in two ways); "
        "\"cross_references\" covers synonyms, antonyms, and compare of that sense.\n\n"
        "ENTRY (JSON):\n" + json.dumps(strip_for_review(entry), ensure_ascii=False, indent=1)
    )


def normalize_verdicts(raw: dict, fields: list[str], role: str | None = None) -> tuple[list[dict], str | None]:
    families = set(eexlib.vocab_values("issue_families"))
    out, seen = [], set()
    err = None
    items = raw.get("verdicts") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        return [], "no verdicts list in the reply"
    for it in items:
        if not isinstance(it, dict):
            continue
        field = str(it.get("field", "")).strip()
        verdict = str(it.get("verdict", "")).strip().lower()
        if verdict not in ("ok", "issue"):
            verdict = "issue" if it.get("severity") else "ok"
        v = {"field": field, "verdict": verdict, "quote": None, "severity": None, "family": None, "reason": None}
        if verdict == "issue":
            sev = str(it.get("severity") or "minor").strip().lower()
            v["severity"] = sev if sev in ("blocking", "minor") else "minor"
            fam = str(it.get("family") or "other").strip().lower()
            v["family"] = fam if fam in families else "other"
            if (role, v["family"]) in DISABLED_FAMILIES:
                v = {"field": field, "verdict": "ok", "quote": None, "severity": None, "family": None, "reason": None}
            else:
                v["quote"] = (str(it.get("quote")) if it.get("quote") not in (None, "") else None)
                v["reason"] = (str(it.get("reason")) if it.get("reason") not in (None, "") else None)
        out.append(v)
        seen.add(field)
    missing = [f for f in fields if f not in seen]
    if missing:
        err = f"no verdict for {len(missing)} field(s): {', '.join(missing[:6])}{'...' if len(missing) > 6 else ''}"
    return out, err


def run_review(entry: dict, roles: list[str], run_id: str, dry_run: bool) -> dict:
    import openrouter
    fields = checklist(entry)
    prompt = user_prompt(entry)
    record = {"run_id": run_id, "slug": entry["slug"], "entry_modified": entry["provenance"]["modified"], "reviewers": []}
    for role in roles:
        model = openrouter.resolve_role(role)
        est = openrouter.estimate_cost(model, len(SYSTEM) // 4 + len(prompt) // 4, 40 * len(fields) + 200)
        rev = {"role": role, "model": model, "requested_at": eexlib.utcnow_iso(), "cost_usd": 0.0, "tokens_in": 0,
               "tokens_out": 0, "verdicts": [], "summary": None, "error": None}
        if dry_run:
            rev["error"] = "dry run"
            record["reviewers"].append(rev)
            continue
        try:
            res = openrouter.call_with_budget(model, [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
                                              purpose=f"review:{entry['slug']}:{role}", estimate_usd=est,
                                              max_tokens=120 * len(fields) + 3000, temperature=0.1,
                                              response_format={"type": "json_object"},
                                              reasoning=openrouter.reasoning_for(model))
            rev.update({"model": res.get("model") or model, "cost_usd": res.get("cost"), "tokens_in": res.get("tokens_in"),
                        "tokens_out": res.get("tokens_out")})
            try:
                raw = openrouter.parse_json_reply(res["text"])
            except ValueError as e:
                rev["error"] = f"{e} | finish={res.get('finish_reason')} | head={(res.get('text') or '')[:300]!r}"
                record["reviewers"].append(rev)
                continue
            verdicts, err = normalize_verdicts(raw, fields, role)
            if err and not verdicts:
                err = f"{err} | finish={res.get('finish_reason')} | head={(res.get('text') or '')[:300]!r}"
            rev["verdicts"] = verdicts
            rev["summary"] = str(raw.get("summary")) if isinstance(raw, dict) and raw.get("summary") else None
            rev["error"] = err
        except Exception as e:  # noqa: BLE001
            msg = f"{type(e).__name__}: {str(e)[:300]}"
            if "budget check refused" in msg:
                print(f"  [{role}] skipped: {msg}", file=sys.stderr)
                continue                                   # no record: the review did not happen
            rev["error"] = msg
        record["reviewers"].append(rev)
    return record


def write_record(record: dict, entry_path: Path, entry: dict) -> Path:
    out = eexlib.ROOT / "reviews" / record["run_id"] / f"{record['slug']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():                                   # merge: keep earlier successful records of other roles
        old = eexlib.load_json(out)
        new_roles = {r["role"] for r in record["reviewers"]}
        kept = [r for r in old.get("reviewers", []) if r["role"] not in new_roles and not r.get("error")]
        record["reviewers"] = kept + record["reviewers"]
    eexlib.save_json(out, record)
    for rev in record["reviewers"]:
        issues = [v for v in rev["verdicts"] if v["verdict"] == "issue"]
        entry["provenance"].setdefault("reviews", []).append({
            "run_id": record["run_id"], "role": rev["role"], "model": rev["model"],
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "file": str(out.relative_to(eexlib.ROOT)),
            "ok": sum(1 for v in rev["verdicts"] if v["verdict"] == "ok"), "issues": len(issues),
            "blocking": sum(1 for v in issues if v["severity"] == "blocking")})
    entry["provenance"]["modified"] = eexlib.utcnow_iso()
    eexlib.save_json(entry_path, entry)
    return out


def latest_review_file(slug: str) -> Path | None:
    files = sorted((eexlib.ROOT / "reviews").glob(f"*/{slug}.json"))
    return files[-1] if files else None


def print_issues(record: dict) -> int:
    n = 0
    for rev in record["reviewers"]:
        if rev.get("error"):
            print(f"  [{rev['role']}] error: {rev['error']}")
        for v in rev["verdicts"]:
            if v["verdict"] == "issue":
                n += 1
                q = (v.get("quote") or "")[:80].replace("\n", " ")
                print(f"  [{rev['role']}] {v['severity']:8s} {v['family']:22s} {v['field']}: {v.get('reason') or ''}  «{q}»")
    return n


def decide(a) -> int:
    f = latest_review_file(a.slug)
    if f is None:
        print(f"no review file for {a.slug}"); return 1
    rec = eexlib.load_json(f)
    match = None
    for rev in rec["reviewers"]:
        if rev["role"] != a.role:
            continue
        for v in rev["verdicts"]:
            if v["verdict"] == "issue" and v["field"] == a.field:
                match = v
    if match is None:
        print(f"no issue by {a.role} on {a.field} in {f}"); return 1
    line = {"ts": eexlib.utcnow_iso(), "run_id": rec["run_id"], "slug": a.slug, "field": a.field, "role": a.role,
            "family": match["family"], "severity": match["severity"], "decision": a.decision, "note": a.note}
    with (eexlib.ROOT / "reviews" / "decisions.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    print("logged:", json.dumps(line, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--roles", default=",".join(DEFAULT_ROLES))
    ap.add_argument("--run-id", help="defaults to .tmp/run-id or a fresh id from tools/claim.py")
    ap.add_argument("--dry-run", action="store_true", help="build the prompts and write nothing")
    ap.add_argument("--report", metavar="SLUG", help="print the issues from the latest review file")
    ap.add_argument("--decide", metavar="SLUG", dest="slug")
    ap.add_argument("--field"); ap.add_argument("--role"); ap.add_argument("--decision", choices=["apply", "reject", "escalate"])
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    if a.report:
        f = latest_review_file(a.report)
        if f is None:
            print("no review file"); return 1
        print(f"{a.report}: {f.relative_to(eexlib.ROOT)}")
        n = print_issues(eexlib.load_json(f))
        print(f"  {n} issue(s)")
        return 0
    if a.slug:
        if not (a.field and a.role and a.decision):
            ap.error("--decide needs --field, --role, --decision")
        return decide(a)
    if not a.slugs:
        ap.error("give at least one slug")
    run_id = a.run_id
    if not run_id:
        import subprocess
        run_id = subprocess.run([sys.executable, str(HERE / "claim.py"), "--id"], capture_output=True, text=True,
                                cwd=eexlib.ROOT).stdout.strip() or "local"
    roles = a.roles.split(",")
    total_cost = 0.0
    for slug in a.slugs:
        p = eexlib.entry_path(slug)
        if not p.exists():
            print(f"ERROR no such entry: {slug}"); continue
        entry = eexlib.load_json(p)
        record = run_review(entry, roles, run_id, a.dry_run)
        if a.dry_run:
            print(f"{slug}: {len(checklist(entry))} checklist fields; prompt {len(user_prompt(entry))} chars")
            continue
        if not record["reviewers"]:
            print(f"{slug}: no reviewer ran (budget); nothing written"); continue
        out = write_record(record, p, entry)
        cost = sum(float(r.get("cost_usd") or 0) for r in record["reviewers"])
        total_cost += cost
        print(f"{slug}: review written to {out.relative_to(eexlib.ROOT)} (${cost:.4f})")
        n = print_issues(record)
        print(f"  {n} issue(s)")
    print(f"panel cost this call: ${total_cost:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
