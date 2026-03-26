#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
import os
import urllib.request
import urllib.error

DEFAULT_API_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_VISION_MODEL = "gpt-4o"


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
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
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


def call_openai_with_image(system_prompt: str, user_prompt: str, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Call OpenAI with an image attachment for vision-based analysis.

    Uses the Chat Completions API (/chat/completions) with standard vision
    format so it works with all OpenAI-compatible providers.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("缺少 OPENAI_API_KEY 环境变量")
    model = os.getenv("OPENAI_VISION_MODEL", DEFAULT_VISION_MODEL)
    api_base = os.getenv("OPENAI_API_BASE", DEFAULT_API_BASE)

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{mime_type};base64,{b64}"

    url = f"{api_base}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
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
        with urllib.request.urlopen(req, timeout=90) as resp:
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

    # Chat Completions response format
    choices = data.get("choices", [])
    if choices:
        msg = choices[0].get("message", {})
        content = msg.get("content", "")
        if content:
            return content.strip()
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
