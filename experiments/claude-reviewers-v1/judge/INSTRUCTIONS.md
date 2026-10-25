# Judge instructions (blind adjudication)

You are the adjudicator for one dictionary entry of the TKG English Learner's Dictionary. Several reviewers checked the entry field by field. Their issues have been pooled, shuffled, and stripped of any reviewer identity: you do not know, and must not guess, who raised which issue. Judge each issue only on whether it is right.

Read, in this order:

1. `prompts/system.txt` — the house rules every reviewer was given, including the list of house conventions that are **not** issues. An issue that objects to one of those conventions is wrong.
2. `../../wiki/style-guide.md` — the dictionary's style guide (the reference for what an entry should be).
3. `inputs/<slug>.json` — the entry as the reviewers saw it.
4. `judge/<slug>.pool.json` — the pooled issues, each with an `id`.
5. Only if the task names one: the list of planted defects for this entry (below in your task).

For **every** issue in the pool, decide:

- `valid`: `"yes"` when the reviewer is right that the quoted text is wrong, misleading, against a house rule, or clearly worth fixing for a learner, and a fix is warranted; `"partly"` when it points at a real problem but the reason or the proposed direction is wrong, or it is a matter of taste with a small real point; `"no"` when the reviewer is wrong, objects to a stated house convention, asks for something the house rules rule out, or flags mere taste ("too simple", "unlike other dictionaries").
- `finding`: for a `"yes"` issue only, a short label (`F1`, `F2`, ...) naming the underlying problem. Issues from different reviewers that point at the **same** problem in the entry share one label, even if worded or filed under different fields; different problems get different labels. Use `null` for `"partly"` and `"no"`.
- `planted`: the ids of any planted defects (from the list in your task) this issue identifies, else `[]`. An issue identifies a planted defect when it flags that specific problem (the right text and essentially the right reason).
- `note`: at most fifteen words on why.

Use your own expert knowledge of English. Be strict both ways: do not accept a wrong objection because it sounds confident, and do not reject a right one because the entry is otherwise good. Do not edit any file except your output.

Write your output to `judge/<slug>.verdicts.json` as JSON:

```json
{"slug": "<slug>", "issues": [{"id": 1, "valid": "yes", "finding": "F1", "planted": [], "note": "..."}],
 "findings": {"F1": "one-line description of the problem"},
 "missed": ["one line per real, blocking-level problem you see in the entry that NO issue in the pool raised"]}
```

Every `id` in the pool must appear exactly once in `issues`.
