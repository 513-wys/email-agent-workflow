"""Call DeepSeek's OpenAI-compatible API or a configured local Ollama model."""
import json
import re

import requests

from app import config, settings_store


def _parse_json(text):
    """把模型输出解析成 dict：去掉 markdown 围栏、容错截取第一个 JSON。"""
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        return {}


def _deepseek_chat(system, user, temperature, max_tokens, json_mode):
    url = config.DEEPSEEK_BASE_URL.rstrip("/") + "/chat/completions"
    api_key = settings_store.get("deepseek_api_key", config.DEEPSEEK_API_KEY)
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": config.DEEPSEEK_MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    r = requests.post(url, json=payload, headers=headers, timeout=90)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def _ollama_chat(system, user, temperature, max_tokens, json_mode):
    url = config.OLLAMA_BASE_URL.rstrip("/") + "/api/chat"
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "stream": False,
        "think": False,  # 关闭 Qwen3 思考模式，加速并保证 JSON 稳定
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    if json_mode:
        payload["format"] = "json"
    r = requests.post(url, json=payload, timeout=180)
    r.raise_for_status()
    return r.json()["message"]["content"]


def backend_name():
    return "deepseek" if settings_store.get("deepseek_api_key", config.DEEPSEEK_API_KEY) else "ollama"


def _chat(system, user, temperature, max_tokens, json_mode):
    if settings_store.get("deepseek_api_key", config.DEEPSEEK_API_KEY):
        return _deepseek_chat(system, user, temperature, max_tokens, json_mode)
    if config.OLLAMA_BASE_URL:
        return _ollama_chat(system, user, temperature, max_tokens, json_mode)
    raise RuntimeError("未配置任何大模型：请在 .env 填 DEEPSEEK_API_KEY，或启动 Ollama 后配 OLLAMA_BASE_URL。")


def chat_json(system, user, temperature=0.2, max_tokens=800):
    """要求模型返回严格 JSON，返回解析后的 dict。"""
    return _parse_json(_chat(system, user, temperature, max_tokens, json_mode=True))


def chat_text(system, user, temperature=0.3, max_tokens=1500):
    """返回纯文本。"""
    return _chat(system, user, temperature, max_tokens, json_mode=False)
