#!/usr/bin/env python3
"""dclient.py -- minimal client for OpenRouter's Decisions API (urllib only).

decide(model, state, questions) -> {"answers", "cost", "tokens_in", "latency", "model", "error"}
The key comes from OPENROUTER_API_KEY and is never printed or written.
"""
from __future__ import annotations
import json, os, time, urllib.request, urllib.error

URL = "https://openrouter.ai/api/alpha/decisions"
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {"HTTP-Referer": "https://github.com/tkgally/eex-dict", "X-Title": "eex-dict"}


def _post(url, body, timeout=120):
    key = os.environ["OPENROUTER_API_KEY"]
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": "Bearer " + key,
                                          "Content-Type": "application/json", **HEADERS})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _retrying(url, body, tries=5):
    err = None
    for i in range(tries):
        t0 = time.time()
        try:
            return _post(url, body), time.time() - t0, None
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:300]
            err = f"HTTP {e.code}: {msg}"
            if e.code not in (408, 429) and e.code < 500:
                return None, time.time() - t0, err
        except Exception as e:  # transport
            err = f"{type(e).__name__}: {e}"[:300]
        time.sleep(2 ** (i + 1))
    return None, 0, err


def decide(model, state, questions):
    data, lat, err = _retrying(URL, {"model": model, "state": state, "questions": questions})
    if data is None:
        return {"answers": None, "cost": 0.0, "tokens_in": 0, "latency": lat, "model": model, "error": err}
    u = data.get("usage") or {}
    return {"answers": data.get("answers"), "cost": float(u.get("cost") or 0), "tokens_in": u.get("input_tokens", 0),
            "latency": lat, "model": data.get("model", model), "error": data.get("error")}


def chat(model, messages, max_tokens=300, reasoning=None, response_format=None):
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "usage": {"include": True}, "temperature": 0}
    if reasoning is not None:
        body["reasoning"] = reasoning
    if response_format:
        body["response_format"] = response_format
    data, lat, err = _retrying(CHAT_URL, body)
    if data is None:
        return {"text": None, "cost": 0.0, "tokens_in": 0, "tokens_out": 0, "latency": lat, "error": err}
    u = data.get("usage") or {}
    ch = (data.get("choices") or [{}])[0]
    return {"text": (ch.get("message") or {}).get("content"), "cost": float(u.get("cost") or 0),
            "tokens_in": u.get("prompt_tokens", 0), "tokens_out": u.get("completion_tokens", 0),
            "latency": lat, "error": None if ch else json.dumps(data)[:300]}
