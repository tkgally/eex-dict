#!/usr/bin/env python3
"""Read the subagent transcripts of this session (JSONL, outside the repository; the path is the first argument)
and write per-task token usage and wall time into outputs/<arm>/meta.json and judge/meta.json.

    python3 agent_usage.py <tasks-dir>

Each transcript is matched to its job by the output path named in its first prompt
(outputs/<arm>/<slug>.raw.json, judge/<slug>.verdicts.json, or inputs/ for the drafter)."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAT = re.compile(r"(?:claude-reviewers-v1/)?(outputs/(\w[\w-]*)/([\w-]+)\.raw\.json|judge/([\w-]+)\.verdicts\.json)")


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def main(tasks_dir):
    meta = {}
    for f in sorted(Path(tasks_dir).glob("*.output")):
        try:
            rows = [json.loads(ln) for ln in f.read_text().splitlines() if ln.strip()]
        except ValueError:
            continue                                   # a shell task's output, not a transcript
        first = next((r for r in rows if r.get("type") == "user"), None)
        if not first:
            continue
        content = first["message"]["content"]
        text = content if isinstance(content, str) else " ".join(c.get("text", "") for c in content if isinstance(c, dict))
        m = PAT.search(text)
        if not m:
            key = ("drafter", "all") if "Draft exactly these 8 entries" in text else None
            if not key:
                continue
        else:
            key = (m.group(2), m.group(3)) if m.group(2) else ("judge", m.group(4))
        seen, u = set(), {"input": 0, "cache_write": 0, "cache_read": 0, "output": 0, "thinking": 0, "turns": 0}
        model, times = None, []
        for r in rows:
            if r.get("timestamp"):
                times.append(ts(r["timestamp"]))
            msg = r.get("message") if isinstance(r.get("message"), dict) else None
            if r.get("type") != "assistant" or not msg or not msg.get("usage"):
                continue
            if msg.get("id") in seen:
                continue
            seen.add(msg.get("id"))
            us = msg["usage"]
            model = msg.get("model") or model
            u["input"] += us.get("input_tokens", 0)
            u["cache_write"] += us.get("cache_creation_input_tokens", 0)
            u["cache_read"] += us.get("cache_read_input_tokens", 0)
            u["output"] += us.get("output_tokens", 0)
            u["thinking"] += (us.get("output_tokens_details") or {}).get("thinking_tokens", 0)
            u["turns"] += 1
        u["model"] = model
        u["seconds"] = round((max(times) - min(times)).total_seconds(), 1) if times else None
        meta.setdefault(key[0], {})[key[1]] = u
    for arm, d in meta.items():
        out = (HERE / "judge" / "meta.json") if arm == "judge" else (HERE / "outputs" / arm / "meta.json")
        if arm == "drafter":
            out = HERE / "outputs" / "drafter-meta.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        old = json.loads(out.read_text()) if out.exists() else {}
        old.update(d)
        out.write_text(json.dumps(old, indent=1, sort_keys=True) + "\n")
        print(arm, len(d), "tasks")


if __name__ == "__main__":
    main(sys.argv[1])
