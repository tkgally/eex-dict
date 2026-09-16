#!/usr/bin/env python3
"""openrouter.py -- a small OpenRouter chat client (urllib only) plus a CLI.

Library
    resolve_role(role)                  role -> model slug from config/models.md
    list_roles()                        the rows of that table
    estimate_cost(slug, t_in, t_out)    US dollars from the table's "Price in/out"
                                        column (per million tokens); 5.00/25.00
                                        when the slug is not in the table
    chat(model, messages, ...)          one chat completion; returns
                                        {"text", "cost", "tokens_in", "tokens_out",
                                         "model", "finish_reason", "raw"}
    chat_json(model, messages, ...)     chat with response_format json_object and
                                        a tolerant parse of the reply (adds "json")
    parse_json_reply(text)              that tolerant parse (fences stripped, first
                                        { or [ found); ValueError on failure
    call_with_budget(role_or_model, messages, purpose, estimate_usd, **kw)
                                        spend.py check -> call -> spend.py record

Transport: POST https://openrouter.ai/api/v1/chat/completions with the key from
OPENROUTER_API_KEY (RuntimeError when unset; the key is never printed or written),
HTTP-Referer https://github.com/tkgally/eex-dict, X-Title eex-dict, and
"usage": {"include": true} so the billed usage.cost comes back. HTTP 408/429/5xx
and transport errors are retried up to 4 times with 2, 4, 8, 16 second backoff;
any other 4xx raises OpenRouterError with the response body. urllib honours
HTTPS_PROXY and the SSL_CERT_FILE bundle by itself; TLS verification stays on.

CLI
    python3 tools/openrouter.py --role reviewer-a --prompt "Say OK" [--max-tokens 20] [--json]
    python3 tools/openrouter.py --model openai/gpt-5.6-terra --prompt "..."
    python3 tools/openrouter.py --list-roles

A CLI call goes through call_with_budget, so it is refused when the estimate
would exceed the daily cap and is recorded in config/budget-ledger.json after.
"""

from __future__ import annotations

import argparse
import http.client
import importlib.util
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODELS_MD = ROOT / "config" / "models.md"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
REFERER = "https://github.com/tkgally/eex-dict"
TITLE = "eex-dict"
KEY_VAR = "OPENROUTER_API_KEY"
RETRY_BACKOFF = (2, 4, 8, 16)          # seconds before retry 1, 2, 3, 4
RETRY_STATUSES = {408, 429}            # plus every 5xx
FALLBACK_PRICE = (5.00, 25.00)         # USD per million tokens, in / out
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TIMEOUT = 180

_sleep = time.sleep                     # patched by tests


class OpenRouterError(RuntimeError):
    """A failed request. .status is the HTTP status (None for transport errors), .body the reply."""

    def __init__(self, message: str, status: int | None = None, body: str = ""):
        super().__init__(message)
        self.status = status
        self.body = body


# ----------------------------------------------------------------------------
# config/models.md
# ----------------------------------------------------------------------------

def parse_models_table(models_md: Path | None = None) -> list[dict]:
    """Rows of the first markdown table whose header has Role and Model slug columns.

    Each row is a dict keyed by the lower-cased header text ("role",
    "model slug", "verified", "price in/out", "notes").
    """
    path = Path(models_md) if models_md else MODELS_MD
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"models table not found: {path}") from None
    header: list[str] | None = None
    rows: list[dict] = []
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            if header is not None and rows:
                break                      # the table ended
            header = None
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            lowered = [c.lower() for c in cells]
            if "role" in lowered and "model slug" in lowered:
                header = lowered
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue                       # the |---|---| separator
        row = dict(zip(header, cells))
        if row.get("role") and row.get("model slug"):
            row["model slug"] = row["model slug"].strip("`")
            rows.append(row)
    if header is None:
        raise ValueError(f"{path} has no table with 'Role' and 'Model slug' columns")
    return rows


def list_roles(models_md: Path | None = None) -> list[dict]:
    return parse_models_table(models_md)


def resolve_role(role: str, models_md: Path | None = None) -> str:
    """The model slug behind a role in config/models.md; KeyError when the role is absent."""
    rows = parse_models_table(models_md)
    for row in rows:
        if row["role"].lower() == role.strip().lower():
            return row["model slug"]
    known = ", ".join(r["role"] for r in rows) or "(none)"
    path = Path(models_md) if models_md else MODELS_MD
    raise KeyError(f"role {role!r} is not in {path}; known roles: {known}. "
                   f"Code refers to roles, so add a row there rather than a slug here.")


def price_table(models_md: Path | None = None) -> dict[str, tuple[float, float]]:
    """slug -> (USD per million input tokens, USD per million output tokens)."""
    prices: dict[str, tuple[float, float]] = {}
    for row in parse_models_table(models_md):
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*/\s*([0-9]+(?:\.[0-9]+)?)", row.get("price in/out", ""))
        if m:
            prices.setdefault(row["model slug"], (float(m.group(1)), float(m.group(2))))
    return prices


def estimate_cost(model_slug: str, tokens_in: int, tokens_out: int,
                  models_md: Path | None = None) -> float:
    """Estimated USD for a call, from the price table (fallback 5.00/25.00 per million)."""
    try:
        p_in, p_out = price_table(models_md).get(model_slug, FALLBACK_PRICE)
    except (FileNotFoundError, ValueError):
        p_in, p_out = FALLBACK_PRICE
    return round((tokens_in * p_in + tokens_out * p_out) / 1_000_000, 6)


# ----------------------------------------------------------------------------
# transport
# ----------------------------------------------------------------------------

def _api_key() -> str:
    key = os.environ.get(KEY_VAR, "").strip()
    if not key:
        raise RuntimeError(f"{KEY_VAR} is not set")
    return key


def _scrub(text: str) -> str:
    """Remove the key from any text that might be printed or raised."""
    key = os.environ.get(KEY_VAR, "")
    if key and key in text:
        text = text.replace(key, "<redacted>")
    return text


def _content_text(message: dict) -> str:
    content = message.get("content")
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):      # multimodal parts
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("type", "text") == "text":
                parts.append(str(part.get("text", "")))
            elif isinstance(part, str):
                parts.append(part)
        return "".join(parts)
    return str(content)


def _post_once(body: dict, timeout: float) -> dict:
    """One HTTP round trip. Raises OpenRouterError (with .status) or a transport error."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {_api_key()}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("HTTP-Referer", REFERER)
    req.add_header("X-Title", TITLE)
    req.add_header("User-Agent", "eex-dict/tools/openrouter.py (python-urllib)")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", "replace")
        except Exception:
            err_body = ""
        raise OpenRouterError(_scrub(f"HTTP {e.code} from OpenRouter: {err_body[:2000]}"),
                              status=e.code, body=_scrub(err_body)) from None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise OpenRouterError(_scrub(f"HTTP {status} with a non-JSON body: {raw[:300]!r}"),
                              status=status, body=_scrub(raw)) from None
    if not isinstance(parsed, dict):
        raise OpenRouterError(f"unexpected reply shape: {raw[:300]!r}", status=status, body=raw)
    if "choices" not in parsed and "error" in parsed:
        # OpenRouter can report a provider error inside a 200 body.
        err = parsed["error"] or {}
        code = err.get("code") if isinstance(err, dict) else None
        msg = err.get("message") if isinstance(err, dict) else str(err)
        try:
            code = int(code)
        except (TypeError, ValueError):
            code = status
        raise OpenRouterError(_scrub(f"OpenRouter error {code}: {msg}"), status=code, body=_scrub(raw))
    return parsed


def _retryable(status: int | None) -> bool:
    return status is None or status in RETRY_STATUSES or 500 <= status < 600


def chat(model: str, messages, *, max_tokens: int = DEFAULT_MAX_TOKENS,
         temperature: float = DEFAULT_TEMPERATURE, response_format: dict | None = None,
         reasoning: dict | None = None, timeout: float = DEFAULT_TIMEOUT,
         extra: dict | None = None) -> dict:
    """One chat completion.

    messages: a list of {"role", "content"} dicts, or a plain string (one user turn).
    Returns {"text", "cost", "tokens_in", "tokens_out", "tokens_reasoning", "model",
    "finish_reason", "raw"}. A reasoning model may spend a small max_tokens on hidden
    reasoning and return an empty "text" with finish_reason "length".
    Retries HTTP 408/429/5xx and transport errors up to 4 times (2, 4, 8, 16 s);
    raises OpenRouterError on any other failure. Never includes the key in errors.
    """
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    body: dict = {
        "model": model,
        "messages": messages,
        "max_tokens": int(max_tokens),
        "temperature": temperature,
        "usage": {"include": True},
    }
    if response_format is not None:
        body["response_format"] = response_format
    if reasoning is not None:
        body["reasoning"] = reasoning
    if extra:
        body.update(extra)
    _api_key()                                   # fail fast, before any retry loop

    attempts = 1 + len(RETRY_BACKOFF)
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            data = _post_once(body, timeout)
            break
        except OpenRouterError as e:
            last = e
            if not _retryable(e.status):
                raise
        except (OSError, http.client.HTTPException) as e:   # URLError, timeouts, resets
            last = OpenRouterError(_scrub(f"transport error: {type(e).__name__}: {e}"))
        if attempt == attempts - 1:
            break
        delay = RETRY_BACKOFF[attempt]
        print(f"openrouter: attempt {attempt + 1}/{attempts} failed ({last}); "
              f"retrying in {delay}s", file=sys.stderr)
        _sleep(delay)
    else:  # pragma: no cover - loop always breaks or exhausts
        pass
    if last is not None and "data" not in locals():
        raise OpenRouterError(f"gave up after {attempts} attempts: {last}",
                              status=getattr(last, "status", None),
                              body=getattr(last, "body", ""))

    choices = data.get("choices") or []
    choice = choices[0] if choices else {}
    message = choice.get("message") or {}
    usage = data.get("usage") or {}
    cost = usage.get("cost")
    try:
        cost = float(cost) if cost is not None else 0.0
    except (TypeError, ValueError):
        cost = 0.0
    details = usage.get("completion_tokens_details") or {}
    return {
        "text": _content_text(message),
        "cost": round(cost, 6),
        "tokens_in": int(usage.get("prompt_tokens") or 0),
        "tokens_out": int(usage.get("completion_tokens") or 0),
        "tokens_reasoning": int(details.get("reasoning_tokens") or 0) if isinstance(details, dict) else 0,
        "model": data.get("model") or model,
        "finish_reason": choice.get("finish_reason") or choice.get("native_finish_reason"),
        "raw": data,
    }


# ----------------------------------------------------------------------------
# JSON replies
# ----------------------------------------------------------------------------

_FENCE_RE = re.compile(r"^\s*```[A-Za-z0-9_+-]*[ \t]*\r?\n(.*?)\r?\n?\s*```\s*$", re.S)


def parse_json_reply(text: str):
    """Tolerant JSON parse of a model reply.

    Strips a surrounding code fence, then tries the whole text, then a parse
    starting at each { or [ in turn (trailing prose is tolerated). Raises
    ValueError carrying the first 300 characters of the reply when nothing parses.
    """
    if text is None:
        raise ValueError("could not parse JSON from an empty reply")
    s = text.strip()
    m = _FENCE_RE.match(s)
    if m:
        s = m.group(1).strip()
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    starts = [i for i, ch in enumerate(s) if ch in "{["][:200]
    for i in starts:
        try:
            obj, _end = decoder.raw_decode(s, i)
            return obj
        except json.JSONDecodeError:
            continue
    raise ValueError(f"could not parse JSON from reply: {text[:300]!r}")


def chat_json(model: str, messages, **kw) -> dict:
    """chat() with response_format json_object; the parsed reply is returned under "json"."""
    kw.setdefault("response_format", {"type": "json_object"})
    result = chat(model, messages, **kw)
    result["json"] = parse_json_reply(result["text"])
    return result


# ----------------------------------------------------------------------------
# budget
# ----------------------------------------------------------------------------

def _load_spend():
    """Import tools/spend.py by path (no package needed)."""
    path = Path(__file__).resolve().parent / "spend.py"
    spec = importlib.util.spec_from_file_location("eex_spend", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def model_for(role_or_model: str, models_md: Path | None = None) -> str:
    """A slug (contains '/') is used as is; anything else is looked up as a role."""
    return role_or_model if "/" in role_or_model else resolve_role(role_or_model, models_md)


def call_with_budget(role_or_model: str, messages, purpose: str, estimate_usd: float,
                     *, ledger: Path | None = None, parse_json: bool = False,
                     run_id: str | None = None, models_md: Path | None = None, **kw) -> dict:
    """spend.py check --cost estimate, then the call, then spend.py record with the billed cost.

    Raises RuntimeError when the ledger refuses the estimate. Extra keyword
    arguments go to chat()/chat_json(). The result gains "spent_today_usd".
    """
    spend = _load_spend()
    ledger_path = Path(ledger) if ledger else spend.DEFAULT_LEDGER
    model = model_for(role_or_model, models_md)
    ok, left, led = spend.check(ledger_path, float(estimate_usd))
    if not ok:
        raise RuntimeError(
            f"budget check refused: estimated ${float(estimate_usd):.6f} for {purpose!r} would "
            f"exceed the ${float(led['daily_cap_usd']):.2f} daily cap "
            f"(spent ${float(led['spent_usd']):.6f} on {led['date']}, "
            f"${spend.remaining(led):.6f} left)")
    result = chat_json(model, messages, **kw) if parse_json else chat(model, messages, **kw)
    led = spend.record(ledger_path, result["cost"], purpose, result["model"],
                       result["tokens_in"], result["tokens_out"], run_id)
    result["spent_today_usd"] = led["spent_usd"]
    return result


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def format_roles_table(rows: list[dict]) -> str:
    cols = ["role", "model slug", "verified", "price in/out"]
    widths = [max(len(c), *(len(r.get(c, "")) for r in rows)) for c in cols]
    out = ["  ".join(c.ljust(w) for c, w in zip(cols, widths)),
           "  ".join("-" * w for w in widths)]
    for r in rows:
        out.append("  ".join(r.get(c, "").ljust(w) for c, w in zip(cols, widths)))
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Send one prompt to an OpenRouter model chosen by role (config/models.md) "
                    "or by slug, through the spending ledger; or list the roles. Reads the key "
                    "from OPENROUTER_API_KEY and never prints it.")
    parser.add_argument("--role", help="role in config/models.md, e.g. reviewer-a")
    parser.add_argument("--model", help="model slug, used instead of --role")
    parser.add_argument("--prompt", help="the user message")
    parser.add_argument("--system", help="an optional system message")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--reasoning-effort", metavar="LEVEL",
                        help="send reasoning {effort: LEVEL} (low, medium, high, ...); "
                             "'off' sends {enabled: false}")
    parser.add_argument("--json", action="store_true",
                        help="request a JSON object reply and print it parsed")
    parser.add_argument("--purpose", default="cli", help="ledger purpose (default: cli)")
    parser.add_argument("--estimate", type=float,
                        help="USD estimate for the budget check (default: from the price table)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--ledger", type=Path, help="ledger file override (default: config/budget-ledger.json)")
    parser.add_argument("--models-md", type=Path, help="models table override (default: config/models.md)")
    parser.add_argument("--raw", action="store_true", help="also print the raw response JSON")
    parser.add_argument("--list-roles", action="store_true", help="print the role table and exit")
    args = parser.parse_args(argv)

    if args.list_roles:
        print(format_roles_table(list_roles(args.models_md)))
        return 0
    if not (args.role or args.model):
        parser.error("give --role or --model (or --list-roles)")
    if args.role and args.model:
        parser.error("give either --role or --model, not both")
    if args.prompt is None:
        parser.error("--prompt is required")

    try:
        model = args.model or resolve_role(args.role, args.models_md)
    except KeyError as e:
        print(f"error: {e.args[0]}", file=sys.stderr)
        return 2

    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": args.prompt})

    reasoning = None
    if args.reasoning_effort:
        reasoning = {"enabled": False} if args.reasoning_effort == "off" else {"effort": args.reasoning_effort}

    approx_in = sum(len(m["content"]) for m in messages) // 4 + 32
    estimate = args.estimate if args.estimate is not None else estimate_cost(
        model, approx_in, args.max_tokens, args.models_md)

    try:
        result = call_with_budget(
            model, messages, args.purpose, estimate, ledger=args.ledger, parse_json=args.json,
            models_md=args.models_md, max_tokens=args.max_tokens, temperature=args.temperature,
            reasoning=reasoning, timeout=args.timeout)
    except (RuntimeError, ValueError) as e:      # includes OpenRouterError
        print(f"error: {_scrub(str(e))}", file=sys.stderr)
        return 1

    print(f"--- reply (model {result['model']}, finish {result['finish_reason']}) ---")
    if args.json:
        print(json.dumps(result["json"], indent=2, ensure_ascii=False))
    elif result["text"]:
        print(result["text"])
    elif result["finish_reason"] == "length":
        print("(empty reply: finish_reason is 'length', so max_tokens ran out before any visible "
              "text; a reasoning model spends tokens on hidden reasoning first. Raise --max-tokens "
              "or pass --reasoning-effort off)")
    else:
        print("(empty reply)")
    print("--- usage ---")
    print(f"cost: ${result['cost']:.6f}  (estimate was ${estimate:.6f})")
    reasoning_note = (f" (of which {result['tokens_reasoning']} reasoning)"
                      if result.get("tokens_reasoning") else "")
    print(f"tokens: {result['tokens_in']} in / {result['tokens_out']} out{reasoning_note}")
    print(f"spent today: ${result['spent_today_usd']:.6f}")
    if args.raw:
        print("--- raw ---")
        print(json.dumps(result["raw"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
