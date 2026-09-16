"""Tests for tools/openrouter.py without any network call.

Covers resolve_role and estimate_cost against a temporary models.md, the
tolerant JSON parse, the missing-key error, the retry policy (transport
patched), and call_with_budget against a temporary ledger (chat patched).
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import openrouter  # noqa: E402

MODELS_MD = """# Models and roles

Some prose with a | pipe that is not a table.

| Role | Model slug | Verified | Price in/out | Notes |
|---|---|---|---|---|
| drafter | anthropic/claude-sonnet-5 | 2026-09-16 | 2.00 / 10.00 | Drafts in-session. |
| reviewer-a | openai/gpt-5.6-terra | 2026-09-16 | 2.00 / 12.00 | OpenAI. |
| reviewer-b | google/gemini-3.8-flash | 2026-09-16 | 0.75 / 3.75 | Google; candidate google/x-pro (2.00 / 12.00). |
| unpriced | example/no-price | 2026-09-16 | n/a | no price listed |

Text after the table.
"""


class ModelsTableTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.models_md = Path(self.tmp.name) / "models.md"
        self.models_md.write_text(MODELS_MD, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_resolve_role(self):
        self.assertEqual(openrouter.resolve_role("reviewer-a", self.models_md), "openai/gpt-5.6-terra")
        self.assertEqual(openrouter.resolve_role("Reviewer-B ", self.models_md), "google/gemini-3.8-flash")
        self.assertEqual(openrouter.model_for("reviewer-b", self.models_md), "google/gemini-3.8-flash")
        self.assertEqual(openrouter.model_for("some/slug", self.models_md), "some/slug")

    def test_resolve_role_missing_is_helpful(self):
        with self.assertRaises(KeyError) as cm:
            openrouter.resolve_role("nobody", self.models_md)
        msg = cm.exception.args[0]
        self.assertIn("'nobody'", msg)
        self.assertIn("reviewer-a", msg)
        self.assertIn(str(self.models_md), msg)

    def test_list_roles(self):
        rows = openrouter.list_roles(self.models_md)
        self.assertEqual([r["role"] for r in rows], ["drafter", "reviewer-a", "reviewer-b", "unpriced"])
        self.assertIn("reviewer-a", openrouter.format_roles_table(rows))

    def test_price_table_and_estimate(self):
        prices = openrouter.price_table(self.models_md)
        self.assertEqual(prices["google/gemini-3.8-flash"], (0.75, 3.75))
        self.assertNotIn("example/no-price", prices)
        # 1,000,000 in at $2 + 500,000 out at $12
        self.assertEqual(openrouter.estimate_cost("openai/gpt-5.6-terra", 1_000_000, 500_000, self.models_md), 8.0)
        self.assertEqual(openrouter.estimate_cost("google/gemini-3.8-flash", 1000, 100, self.models_md), 0.001125)
        # fallback 5.00 / 25.00 for unknown or unpriced slugs
        self.assertEqual(openrouter.estimate_cost("unknown/model", 1000, 100, self.models_md), 0.0075)
        self.assertEqual(openrouter.estimate_cost("example/no-price", 1000, 100, self.models_md), 0.0075)
        missing = Path(self.tmp.name) / "absent.md"
        self.assertEqual(openrouter.estimate_cost("openai/gpt-5.6-terra", 1000, 100, missing), 0.0075)

    def test_missing_models_file(self):
        with self.assertRaises(FileNotFoundError):
            openrouter.resolve_role("reviewer-a", Path(self.tmp.name) / "absent.md")


class ParseJsonReplyTests(unittest.TestCase):
    def test_plain_object_and_array(self):
        self.assertEqual(openrouter.parse_json_reply('{"a": 1}'), {"a": 1})
        self.assertEqual(openrouter.parse_json_reply(' [1, 2] '), [1, 2])

    def test_code_fences(self):
        self.assertEqual(openrouter.parse_json_reply('```json\n{"a": [1, 2]}\n```'), {"a": [1, 2]})
        self.assertEqual(openrouter.parse_json_reply('```\n{"a": 1}```'), {"a": 1})

    def test_surrounding_prose(self):
        self.assertEqual(openrouter.parse_json_reply('Here is the result:\n{"ok": true}\nDone.'), {"ok": True})
        self.assertEqual(openrouter.parse_json_reply('Sure {not json} then {"x": "y"}'), {"x": "y"})
        self.assertEqual(openrouter.parse_json_reply('Values: [1, 2, 3] as requested'), [1, 2, 3])

    def test_failure_carries_snippet(self):
        long_reply = "no json here " * 50
        with self.assertRaises(ValueError) as cm:
            openrouter.parse_json_reply(long_reply)
        self.assertIn(long_reply[:300], str(cm.exception))
        self.assertNotIn(long_reply[:301], str(cm.exception))
        with self.assertRaises(ValueError):
            openrouter.parse_json_reply("")
        with self.assertRaises(ValueError):
            openrouter.parse_json_reply("{unterminated: ")


class TransportTests(unittest.TestCase):
    """The transport is patched; nothing here touches the network."""

    def test_missing_key_raises_before_any_request(self):
        with mock.patch.dict(os.environ):
            os.environ.pop(openrouter.KEY_VAR, None)
            with mock.patch.object(openrouter, "_post_once", side_effect=AssertionError("no request expected")):
                with self.assertRaises(RuntimeError) as cm:
                    openrouter.chat("a/b", "hi")
        self.assertEqual(str(cm.exception), "OPENROUTER_API_KEY is not set")

    def _reply(self, text="OK", cost=0.000123, model="a/b-echo"):
        return {"id": "x", "model": model,
                "choices": [{"finish_reason": "stop", "message": {"role": "assistant", "content": text}}],
                "usage": {"prompt_tokens": 7, "completion_tokens": 2, "cost": cost}}

    def test_chat_result_shape_and_body(self):
        sent = {}

        def fake_post(body, timeout):
            sent["body"] = body
            sent["timeout"] = timeout
            return self._reply()

        with mock.patch.dict(os.environ, {openrouter.KEY_VAR: "test-key-000"}):
            with mock.patch.object(openrouter, "_post_once", side_effect=fake_post):
                r = openrouter.chat("a/b", "hi", max_tokens=20, reasoning={"effort": "low"},
                                    extra={"seed": 1}, timeout=9)
        self.assertEqual(sent["body"]["messages"], [{"role": "user", "content": "hi"}])
        self.assertEqual(sent["body"]["usage"], {"include": True})
        self.assertEqual(sent["body"]["max_tokens"], 20)
        self.assertEqual(sent["body"]["reasoning"], {"effort": "low"})
        self.assertEqual(sent["body"]["seed"], 1)
        self.assertEqual(sent["timeout"], 9)
        self.assertEqual(r["text"], "OK")
        self.assertEqual(r["cost"], 0.000123)
        self.assertEqual((r["tokens_in"], r["tokens_out"]), (7, 2))
        self.assertEqual(r["model"], "a/b-echo")
        self.assertEqual(r["finish_reason"], "stop")
        self.assertIs(r["raw"]["usage"], r["raw"]["usage"])

    def test_chat_json_parses_and_sets_response_format(self):
        sent = {}

        def fake_post(body, timeout):
            sent["body"] = body
            return self._reply(text='```json\n{"verdict": "ok"}\n```')

        with mock.patch.dict(os.environ, {openrouter.KEY_VAR: "test-key-000"}):
            with mock.patch.object(openrouter, "_post_once", side_effect=fake_post):
                r = openrouter.chat_json("a/b", [{"role": "user", "content": "x"}])
        self.assertEqual(sent["body"]["response_format"], {"type": "json_object"})
        self.assertEqual(r["json"], {"verdict": "ok"})

    def test_retries_on_429_and_5xx_with_backoff(self):
        calls = []
        sleeps = []
        responses = [openrouter.OpenRouterError("rate", status=429),
                     openrouter.OpenRouterError("boom", status=503),
                     ConnectionResetError("reset"),
                     self._reply("fine")]

        def fake_post(body, timeout):
            calls.append(1)
            item = responses[len(calls) - 1]
            if isinstance(item, Exception):
                raise item
            return item

        with mock.patch.dict(os.environ, {openrouter.KEY_VAR: "test-key-000"}):
            with mock.patch.object(openrouter, "_post_once", side_effect=fake_post), \
                 mock.patch.object(openrouter, "_sleep", side_effect=sleeps.append), \
                 mock.patch("sys.stderr"):
                r = openrouter.chat("a/b", "hi")
        self.assertEqual(r["text"], "fine")
        self.assertEqual(len(calls), 4)
        self.assertEqual(sleeps, [2, 4, 8])

    def test_gives_up_after_four_retries(self):
        sleeps = []
        with mock.patch.dict(os.environ, {openrouter.KEY_VAR: "test-key-000"}):
            with mock.patch.object(openrouter, "_post_once",
                                   side_effect=openrouter.OpenRouterError("down", status=500)), \
                 mock.patch.object(openrouter, "_sleep", side_effect=sleeps.append), \
                 mock.patch("sys.stderr"):
                with self.assertRaises(openrouter.OpenRouterError) as cm:
                    openrouter.chat("a/b", "hi")
        self.assertEqual(sleeps, [2, 4, 8, 16])
        self.assertIn("gave up after 5 attempts", str(cm.exception))
        self.assertEqual(cm.exception.status, 500)

    def test_other_4xx_raises_immediately_with_body_and_no_key(self):
        sleeps = []
        key = "sk-or-test-SECRET-abc"
        err = openrouter.OpenRouterError(openrouter._scrub(f"HTTP 400 from OpenRouter: bad request {key}"),
                                         status=400, body="bad request")
        with mock.patch.dict(os.environ, {openrouter.KEY_VAR: key}):
            err = openrouter.OpenRouterError(openrouter._scrub(f"HTTP 400: bad request {key}"), status=400)
            with mock.patch.object(openrouter, "_post_once", side_effect=err), \
                 mock.patch.object(openrouter, "_sleep", side_effect=sleeps.append):
                with self.assertRaises(openrouter.OpenRouterError) as cm:
                    openrouter.chat("a/b", "hi")
        self.assertEqual(sleeps, [])
        self.assertEqual(cm.exception.status, 400)
        self.assertIn("bad request", str(cm.exception))
        self.assertNotIn(key, str(cm.exception))
        self.assertIn("<redacted>", str(cm.exception))


class CallWithBudgetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self.tmp.name) / "ledger.json"
        self.models_md = Path(self.tmp.name) / "models.md"
        self.models_md.write_text(MODELS_MD, encoding="utf-8")
        self._quiet = contextlib.redirect_stderr(io.StringIO())   # ledger-creation note
        self._quiet.__enter__()

    def tearDown(self):
        self._quiet.__exit__(None, None, None)
        self.tmp.cleanup()

    def test_records_actual_cost(self):
        fake = mock.Mock(return_value={"text": "OK", "cost": 0.000321, "tokens_in": 9, "tokens_out": 1,
                                       "model": "google/gemini-3.8-flash", "finish_reason": "stop", "raw": {}})
        with mock.patch.object(openrouter, "chat", fake):
            r = openrouter.call_with_budget("reviewer-b", "hi", "unit-test", 0.01, ledger=self.ledger,
                                            run_id="t", models_md=self.models_md, max_tokens=5)
        fake.assert_called_once_with("google/gemini-3.8-flash", "hi", max_tokens=5)
        self.assertEqual(r["spent_today_usd"], 0.000321)
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(data["spent_usd"], 0.000321)
        self.assertEqual(data["calls"][0]["purpose"], "unit-test")
        self.assertEqual(data["calls"][0]["model"], "google/gemini-3.8-flash")
        self.assertEqual(data["calls"][0]["run_id"], "t")
        self.assertEqual((data["calls"][0]["tokens_in"], data["calls"][0]["tokens_out"]), (9, 1))

    def test_refused_when_estimate_exceeds_cap(self):
        fake = mock.Mock(side_effect=AssertionError("must not be called"))
        with mock.patch.object(openrouter, "chat", fake):
            with self.assertRaises(RuntimeError) as cm:
                openrouter.call_with_budget("reviewer-b", "hi", "unit-test", 5.5, ledger=self.ledger,
                                            models_md=self.models_md)
        self.assertIn("budget check refused", str(cm.exception))
        fake.assert_not_called()
        data = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(data["calls"], [])


if __name__ == "__main__":
    unittest.main()
