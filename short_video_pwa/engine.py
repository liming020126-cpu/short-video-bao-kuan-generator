#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import urllib.request
import urllib.error

DEFAULT_API_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


def call_openai_responses(system_prompt: str, user_prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("缺少 OPENAI_API_KEY 环境变量")
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    api_base = os.getenv("OPENAI_API_BASE", DEFAULT_API_BASE)

    url = f"{api_base}/responses"
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": user_prompt}]},
        ],
        "temperature": 0.7,
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            data = json.loads(raw)
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", errors="ignore")
        except Exception:
            detail = str(e)
        raise RuntimeError(f"API 请求失败：{detail}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"网络错误：{e}")

    return extract_text(data)


def extract_text(data: dict) -> str:
    texts = []
    for item in data.get("output", []):
        for c in item.get("content", []):
            if c.get("type") in ("output_text", "text"):
                t = c.get("text")
                if t:
                    texts.append(t)
    if not texts and "output_text" in data:
        texts.append(data.get("output_text"))
    return "\n".join(texts).strip()
