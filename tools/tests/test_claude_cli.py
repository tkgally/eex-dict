"""Tests for the headless-Claude route in tools/openrouter.py (slugs "claude-cli/<model id>"), with
subprocess.run patched: no process is started and no subscription is used."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import openrouter  # noqa: E402

SLUG = "claude-cli/claude-sonnet-5-5"


def reply(structured=None, result="", is_error=False):
    body = {"type": "result", "is_error": is_error, "result": result, "stop_reason": "end_turn", "total_cost_usd": 0.07,
            "usage": {"input_tokens": 2, "cache_creation_input_tokens": 11000, "cache_read_input_tokens": 500,
                      "output_tokens": 2600, "output_tokens_details": {"thinking_tokens": 900}},
            "modelUsage": {"claude-sonnet-5-5": {}}}
    if structured is not None:
        body["structured_output"] = structured
    return subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(body), stderr="")


class ClaudeCliTests(unittest.TestCase):
    def call(self, fake, **kw):
        with mock.patch.object(openrouter, "_run", fake), mock.patch.object(openrouter, "_sleep", lambda s: None):
            return openrouter.chat(SLUG, [{"role": "system", "content": "SYS"}, {"role": "user", "content": "USER"}], **kw)

    def test_command_and_result(self):
        seen = {}

        def fake(cmd, **kw):
            seen["cmd"], seen["input"], seen["cwd"] = cmd, kw["input"], kw["cwd"]
            return reply(structured={"verdicts": [], "summary": "ok"})

        schema = {"type": "object", "properties": {"verdicts": {"type": "array"}}, "required": ["verdicts"]}
        res = self.call(fake, response_format={"type": "json_object"}, json_schema=schema,
                        reasoning=openrouter.reasoning_for(SLUG))
        cmd = seen["cmd"]
        self.assertEqual(cmd[:4], ["claude", "-p", "--model", "claude-sonnet-5-5"])
        self.assertEqual(cmd[cmd.index("--tools") + 1], "")
        self.assertEqual(cmd[cmd.index("--system-prompt") + 1], "SYS")
        self.assertEqual(cmd[cmd.index("--effort") + 1], "high")
        self.assertEqual(json.loads(cmd[cmd.index("--json-schema") + 1]), schema)
        self.assertEqual(seen["input"], "USER")
        self.assertNotIn(str(openrouter.ROOT), str(seen["cwd"]))          # run outside the repository
        self.assertEqual(json.loads(res["text"]), {"verdicts": [], "summary": "ok"})
        self.assertEqual(res["cost"], 0.0)
        self.assertEqual(res["tokens_in"], 11502)
        self.assertEqual(res["tokens_out"], 2600)
        self.assertEqual(res["model"], SLUG)

    def test_plain_result_when_no_schema(self):
        seen = {}

        def fake(cmd, **kw):
            seen["cmd"] = cmd
            return reply(result="OK")

        res = self.call(fake, response_format={"type": "json_object"})
        self.assertEqual(res["text"], "OK")
        self.assertNotIn("--json-schema", seen["cmd"])        # a bare json_object asks for no schema

    def test_retries_then_raises(self):
        calls = []

        def fake(cmd, **kw):
            calls.append(1)
            return subprocess.CompletedProcess(args=[], returncode=1, stdout="not json", stderr="boom")

        with self.assertRaises(openrouter.OpenRouterError):
            self.call(fake)
        self.assertEqual(len(calls), 1 + len(openrouter.CLAUDE_CLI_RETRIES))

    def test_error_reply_is_retried(self):
        replies = [reply(result="overloaded", is_error=True), reply(result="OK")]
        res = self.call(lambda cmd, **kw: replies.pop(0))
        self.assertEqual(res["text"], "OK")

    def test_reasoning(self):
        self.assertEqual(openrouter.reasoning_for(SLUG), {"effort": "high"})
        self.assertEqual(openrouter.reasoning_for(SLUG, "pronunciation"), {"effort": "low"})
        self.assertEqual(openrouter.reasoning_for("openai/gpt-5.6-terra"), {"enabled": False})

    def test_budget_records_zero_cost_with_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.json"
            with mock.patch.object(openrouter, "_run", lambda cmd, **kw: reply(result="OK")):
                res = openrouter.call_with_budget(SLUG, "hi", purpose="test", estimate_usd=0.0, ledger=ledger)
            led = json.loads(ledger.read_text())
            self.assertEqual(res["spent_today_usd"], 0.0)
            self.assertEqual(led["calls"][-1]["cost_usd"], 0.0)
            self.assertEqual(led["calls"][-1]["tokens_out"], 2600)
            self.assertEqual(led["calls"][-1]["model"], SLUG)

    def test_no_key_needed(self):
        with mock.patch.dict("os.environ", {}, clear=False):
            import os
            os.environ.pop(openrouter.KEY_VAR, None)
            res = self.call(lambda cmd, **kw: reply(result="OK"))
        self.assertEqual(res["text"], "OK")


if __name__ == "__main__":
    unittest.main()
