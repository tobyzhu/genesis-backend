#coding = utf-8
"""Registered LLM agents. Extend with new keys + env vars for additional providers."""

import base64
import json
import os
from typing import Any, Dict, List, Optional, Tuple

import requests


def get_agent_config(agent_id: str) -> Dict[str, Any]:
    agent_id = (agent_id or "deepseek").strip().lower()
    if agent_id == "deepseek":
        key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        if not key:
            raise ValueError("未配置 DEEPSEEK_API_KEY（请在 .env 中设置）")
        base = os.environ.get("DEEPSEEK_API_BASE", "https://api.deepseek.com").rstrip("/")
        return {
            "id": "deepseek",
            "label": "DeepSeek",
            "api_key": key,
            "chat_url": f"{base}/v1/chat/completions",
            "default_model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
            "auth": "bearer",
        }
    if agent_id == "cursor":
        key = os.environ.get("CURSOR_API_KEY", "").strip()
        if not key:
            raise ValueError("未配置 CURSOR_API_KEY（请在 .env 中设置）")
        base = os.environ.get("CURSOR_OPENAI_BASE", "").strip().rstrip("/")
        if not base:
            raise ValueError(
                "已设置 CURSOR_API_KEY，但未设置 CURSOR_OPENAI_BASE。"
                "本助手使用 OpenAI 兼容的 POST …/chat/completions；请在 .env 中配置 CURSOR_OPENAI_BASE（不含 /chat/completions），"
                "例如 https://api.openai.com/v1 或 https://openrouter.ai/api/v1，并设置 CURSOR_MODEL 为该网关支持的模型 id。"
                "说明：Dashboard 里 Integrations 的 Cursor API 密钥（常见 crsr_ 前缀）用于 api.cursor.com 的 Cloud Agents / 团队接口，"
                "官方不提供与本助手相同的 /v1/chat/completions 路径；若仅持有该类密钥，对话场景请继续用 DeepSeek，或为对话单独配置 OpenAI 兼容服务商。"
            )
        auth = (os.environ.get("CURSOR_HTTP_AUTH") or "bearer").strip().lower()
        if auth not in ("bearer", "basic"):
            auth = "bearer"
        return {
            "id": "cursor",
            "label": "Cursor（OpenAI 兼容网关）",
            "api_key": key,
            "chat_url": f"{base}/chat/completions",
            "default_model": os.environ.get("CURSOR_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini",
            "auth": auth,
        }
    raise ValueError(f"不支持的智能体: {agent_id}")


def chat_completion(
    agent_id: str,
    messages: List[Dict[str, str]],
    *,
    model: Optional[str] = None,
    temperature: float = 0.2,
    timeout: int = 120,
    json_mode: bool = False,
) -> Tuple[str, str]:
    """
    Returns (assistant_message_text, model_used).
    """
    cfg = get_agent_config(agent_id)
    use_model = model or cfg["default_model"]
    auth_mode = str(cfg.get("auth") or "bearer").lower()
    if auth_mode == "basic":
        basic = base64.b64encode(f"{cfg['api_key']}:".encode()).decode()
        auth_header = f"Basic {basic}"
    else:
        auth_header = f"Bearer {cfg['api_key']}"
    payload: Dict[str, Any] = {
        "model": use_model,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    resp = requests.post(
        cfg["chat_url"],
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=timeout,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f"LLM HTTP {resp.status_code}: {resp.text[:2000]}")
    body = (resp.text or "").strip()
    if not body:
        raise RuntimeError(f"LLM 返回空响应体（HTTP {resp.status_code}）")
    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        raise RuntimeError(f"LLM 响应不是合法 JSON（HTTP {resp.status_code}）: {body[:800]}") from e
    try:
        text = data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"LLM 响应格式异常: {data!r}") from e
    return text.strip(), use_model


def list_agent_choices() -> List[Dict[str, str]]:
    """UI / API: agents that appear to be configured."""
    out = []
    if os.environ.get("DEEPSEEK_API_KEY", "").strip():
        out.append({"id": "deepseek", "label": "DeepSeek"})
    if os.environ.get("CURSOR_API_KEY", "").strip():
        # 需要 CURSOR_OPENAI_BASE 才能真正调用；仍列出以便用户选用（首次请求会得到明确配置提示）
        label = "Cursor（OpenAI 兼容）"
        if not os.environ.get("CURSOR_OPENAI_BASE", "").strip():
            label += " — 需在 .env 设置 CURSOR_OPENAI_BASE"
        out.append({"id": "cursor", "label": label})
    return out
