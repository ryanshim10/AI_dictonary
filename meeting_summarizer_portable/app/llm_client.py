import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional


def _headers(cfg: Dict[str, str]) -> Dict[str, str]:
    auth_type = (cfg.get("auth_type") or "api-key").strip().lower()
    api_key = (cfg.get("api_key") or "").strip()
    api_key_header = (cfg.get("api_key_header") or "api-key").strip()

    h = {"Content-Type": "application/json"}
    if api_key:
        if auth_type == "bearer":
            h["Authorization"] = f"Bearer {api_key}"
        else:
            h[api_key_header] = api_key
    return h


def call_llm(cfg: Dict[str, Any], user_text: str) -> str:
    """Calls either chat_completions or responses API depending on cfg."""

    mode = (cfg.get("mode") or "chat_completions").strip().lower()
    timeout = int(cfg.get("timeout_sec") or 60)
    max_tokens = int(cfg.get("max_tokens") or 1200)

    if mode == "responses":
        url = (cfg.get("responses_url") or "").strip()
        model = (cfg.get("responses_model") or "gpt-4o-mini").strip()
        body = {
            "model": model,
            "input": user_text,
        }
        # try to limit output where supported
        body["max_output_tokens"] = max_tokens
    else:
        url = (cfg.get("chat_url") or "").strip()
        body = {
            "stream": False,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": user_text}],
                }
            ],
        }

    if not url:
        raise RuntimeError("LLM url is empty in config")

    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url=url, data=data, headers=_headers(cfg), method="POST")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else str(e)
        raise RuntimeError(f"LLM HTTPError {e.code}: {detail[:2000]}")
    except Exception as e:
        raise RuntimeError(f"LLM request failed: {e}")

    obj = json.loads(raw)

    # chat_completions
    if "choices" in obj:
        try:
            return obj["choices"][0]["message"]["content"].strip()
        except Exception:
            return str(obj)[:2000]

    # responses
    if "output_text" in obj and isinstance(obj["output_text"], str):
        return obj["output_text"].strip()

    # fallback: try to find output in generic shape
    if "output" in obj:
        return json.dumps(obj["output"], ensure_ascii=False)[:4000]

    return raw[:4000]
