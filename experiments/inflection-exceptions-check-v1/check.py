#!/usr/bin/env python3
"""Ask two reviewer roles to check schema/inflection-exceptions.json once (style guide
section 10; founding prompt). Raw replies are kept here as the record; the session
reads them, applies the corrections it agrees with, and writes
wiki/notes/inflection-exceptions-check.md.

    python3 experiments/inflection-exceptions-check-v1/check.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import openrouter  # noqa: E402

PROMPT = """You are checking a table of English inflection exceptions for a learner's dictionary (American English primary). Read every entry. Report ONLY entries you believe are wrong or incomplete: a wrong form, a missing common alternative, a word that does not belong in the section, or a common irregular word that is missing from the verbs, nouns, adjectives, or adverbs sections. For each, give the section, the word, what the table says, what you believe is correct, and your confidence (high, medium, low). Do not restate correct entries. Return JSON: {"problems": [{"section": "...", "word": "...", "table_says": "...", "should_be": "...", "confidence": "...", "reason": "..."}], "missing": [{"section": "...", "word": "...", "forms": "..."}]}

TABLE:
"""


def main() -> int:
    table = json.loads((ROOT / "schema/inflection-exceptions.json").read_text(encoding="utf-8"))
    table.pop("_doc", None)
    text = json.dumps(table, ensure_ascii=False, separators=(",", ":"))
    for role in ("reviewer-a", "reviewer-b"):
        out = HERE / f"{role}.json"
        if out.exists():
            print(f"{role}: exists, skipping"); continue
        model = openrouter.resolve_role(role)
        est = openrouter.estimate_cost(model, len(text) // 3 + 300, 2500)
        res = openrouter.call_with_budget(model, [{"role": "user", "content": PROMPT + text}],
                                          purpose=f"inflection-check:{role}", estimate_usd=est, max_tokens=6000,
                                          temperature=0.1, response_format={"type": "json_object"},
                                          reasoning=openrouter.reasoning_for(model))
        try:
            reply = openrouter.parse_json_reply(res["text"])
        except ValueError as e:
            reply = {"_parse_error": str(e)}
        out.write_text(json.dumps({"role": role, "model": res.get("model") or model, "cost_usd": res.get("cost"),
                                   "tokens_in": res.get("tokens_in"), "tokens_out": res.get("tokens_out"),
                                   "reply": reply}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        n = len(reply.get("problems", [])) if isinstance(reply, dict) else 0
        m = len(reply.get("missing", [])) if isinstance(reply, dict) else 0
        print(f"{role}: {n} problems, {m} missing, ${res.get('cost', 0):.4f}, finish {res.get('finish_reason')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
