# coding=utf-8
"""Mini program assistant API (company/storecode/ecode auth, no CSRF)."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, Tuple

from django.db import DatabaseError
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import common.constants as common_constants
from assistant.models import AssistantMessage, AssistantThread
from assistant.views import (
    _assistant_db_error_response,
    _decode_db_text,
    _encode_db_text,
    _serialize_thread,
    run_assistant_turn,
)
from common.genesis_auth import validate_genesis_store_access

logger = logging.getLogger(__name__)


def _parse_json_body(request: HttpRequest) -> Tuple[Optional[Dict[str, Any]], Optional[JsonResponse]]:
    try:
        return json.loads(request.body.decode("utf-8") or "{}"), None
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None, JsonResponse({"ok": False, "error": "无效的 JSON 请求体"}, status=400)


def _mp_auth(body: Dict[str, Any]) -> Tuple[Optional[Any], Optional[JsonResponse]]:
    company = (body.get("company") or "").strip()
    storecode = (body.get("storecode") or "").strip()
    ecode = (body.get("ecode") or body.get("usercode") or "").strip()

    if not company or not storecode or not ecode:
        return None, JsonResponse(
            {
                "ok": False,
                "error": "缺少 company、storecode 或 ecode",
            },
            status=400,
        )

    profile = validate_genesis_store_access(company, storecode, usercode=ecode)
    if not profile:
        return None, JsonResponse(
            {"ok": False, "error": "员工无权限或门店不匹配"},
            status=403,
        )
    return profile, None


def _profile_user(profile):
    return profile.user


@csrf_exempt
@require_http_methods(["POST"])
def mp_assistant_chat_api(request: HttpRequest):
    body, err = _parse_json_body(request)
    if err:
        return err

    profile, err = _mp_auth(body)
    if err:
        return err

    message = (body.get("message") or "").strip()
    if not message:
        return JsonResponse({"ok": False, "error": "message 不能为空"}, status=400)

    agent_id = (body.get("agent") or "deepseek").strip().lower()
    profile_id = (body.get("profile") or "general").strip().lower()
    company = (body.get("company") or getattr(common_constants, "COMPANYID", "demo") or "demo").strip()
    storecode = (body.get("storecode") or "88").strip()
    thread_id = body.get("thread_id")
    vipuuid = (body.get("vipuuid") or "").strip()

    user = _profile_user(profile)
    thread: AssistantThread | None = None

    try:
        if thread_id is not None and thread_id != "":
            try:
                tid = int(thread_id)
            except (TypeError, ValueError):
                return JsonResponse({"ok": False, "error": "thread_id 无效"}, status=400)
            thread = AssistantThread.objects.filter(pk=tid, user=user).first()
            if not thread:
                return JsonResponse({"ok": False, "error": "会话不存在或无权访问"}, status=404)
        else:
            auto_title = message[:120] if len(message) <= 120 else message[:117] + "..."
            thread = AssistantThread.objects.create(
                user=user,
                title=_encode_db_text(auto_title),
                company=company,
                storecode=storecode,
                agent_id=agent_id,
                profile_id=profile_id,
            )

        context_prefix = ""
        if vipuuid:
            context_prefix = f"[当前上下文：会员 vipuuid={vipuuid}]"

        result = run_assistant_turn(
            thread,
            message,
            company,
            storecode,
            agent_id=agent_id,
            profile_id=profile_id,
            context_prefix=context_prefix,
        )
        return JsonResponse(
            {
                "ok": True,
                "thread_id": result["thread_id"],
                "assistant_message_id": result["assistant_message_id"],
                "answer": result["answer"],
            }
        )
    except DatabaseError as exc:
        tid_out = thread.pk if thread is not None else None
        return _assistant_db_error_response(exc, {"thread_id": tid_out})
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    except Exception as exc:
        tid_out = thread.pk if thread is not None else None
        logger.exception(
            "mp_assistant_chat_api failed company=%s storecode=%s ecode=%s",
            company,
            storecode,
            body.get("ecode"),
        )
        err_text = str(exc) or exc.__class__.__name__
        if "DEEPSEEK_API_KEY" in err_text or "未配置" in err_text:
            err_text = "服务端未配置 DEEPSEEK_API_KEY，请在 genesis_backend/.env 中设置后重启后端。"
        elif "LLM HTTP" in err_text or "LLM 返回" in err_text or "LLM 响应" in err_text:
            err_text = "DeepSeek 调用失败：" + err_text[:500]
        return JsonResponse(
            {"ok": False, "error": err_text, "thread_id": tid_out},
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def mp_assistant_threads_api(request: HttpRequest):
    company = (request.GET.get("company") or "").strip()
    storecode = (request.GET.get("storecode") or "").strip()
    ecode = (request.GET.get("ecode") or request.GET.get("usercode") or "").strip()
    body = {"company": company, "storecode": storecode, "ecode": ecode}

    profile, err = _mp_auth(body)
    if err:
        return err

    user = _profile_user(profile)
    try:
        qs = (
            AssistantThread.objects.filter(user=user, company=company, storecode=storecode)
            .order_by("-updated_at")[:50]
        )
        return JsonResponse({"ok": True, "threads": [_serialize_thread(t) for t in qs]})
    except DatabaseError as exc:
        return _assistant_db_error_response(exc)


@csrf_exempt
@require_http_methods(["GET"])
def mp_assistant_thread_detail_api(request: HttpRequest, pk: int):
    company = (request.GET.get("company") or "").strip()
    storecode = (request.GET.get("storecode") or "").strip()
    ecode = (request.GET.get("ecode") or request.GET.get("usercode") or "").strip()
    body = {"company": company, "storecode": storecode, "ecode": ecode}

    profile, err = _mp_auth(body)
    if err:
        return err

    user = _profile_user(profile)
    try:
        t = AssistantThread.objects.filter(pk=pk, user=user).first()
        if not t:
            return JsonResponse({"ok": False, "error": "会话不存在或无权访问"}, status=404)
        msgs = [
            {
                "id": m.pk,
                "role": m.role,
                "content": _decode_db_text(m.content),
                "sequence": m.sequence,
                "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
            }
            for m in t.messages.order_by("sequence", "id")
            if m.role in (AssistantMessage.ROLE_USER, AssistantMessage.ROLE_ASSISTANT)
        ]
        return JsonResponse(
            {
                "ok": True,
                "thread": _serialize_thread(t, include_count=False),
                "messages": msgs,
            }
        )
    except DatabaseError as exc:
        return _assistant_db_error_response(exc)


@csrf_exempt
@require_http_methods(["POST"])
def mp_vip_lifecycle_api(request: HttpRequest):
    """小程序：门店客户生命周期分级（直连，不经 LLM）。"""
    body, err = _parse_json_body(request)
    if err:
        return err

    profile, err = _mp_auth(body)
    if err:
        return err

    company = (body.get("company") or "").strip()
    storecode = (body.get("storecode") or "").strip()
    segment = (body.get("segment") or "").strip()
    viptype = (body.get("viptype") or "").strip()
    ecode = (body.get("adviser_ecode") or body.get("ecode_filter") or "").strip()
    limit = body.get("limit", 100)
    try:
        limit = max(1, min(int(limit), 500))
    except (TypeError, ValueError):
        limit = 100

    from assistant.vip_lifecycle import compute_lifecycle_batch, get_lifecycle_config

    cfg = get_lifecycle_config(company)
    data = compute_lifecycle_batch(
        company,
        storecode,
        segment=segment,
        viptype=viptype,
        ecode=ecode,
        limit=limit,
    )
    return JsonResponse(
        {
            "ok": True,
            "config": {
                "inactive_days": cfg.inactive_days,
                "critical_days": cfg.critical_days,
                "trend_days": cfg.trend_days,
            },
            "data": data,
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def mp_vip_lifecycle_one_api(request: HttpRequest):
    """小程序：单客生命周期 + 运营方案（直连，不经 LLM）。"""
    body, err = _parse_json_body(request)
    if err:
        return err

    profile, err = _mp_auth(body)
    if err:
        return err

    company = (body.get("company") or "").strip()
    storecode = (body.get("storecode") or "").strip()
    telph = (body.get("telph") or "").strip()
    vipuuid = (body.get("vipuuid") or "").strip()
    vcode = (body.get("vcode") or "").strip()

    from assistant.vip_lifecycle import tool_vip_lifecycle_one

    row = tool_vip_lifecycle_one(
        company,
        storecode,
        telph=telph,
        vipuuid=vipuuid,
        vcode=vcode,
    )
    if row.get("error"):
        return JsonResponse({"ok": False, "error": row["error"]}, status=404)
    return JsonResponse({"ok": True, "data": row})


@csrf_exempt
@require_http_methods(["POST"])
def mp_vip_lifecycle_migrations_api(request: HttpRequest):
    body, err = _parse_json_body(request)
    if err:
        return err

    profile, err = _mp_auth(body)
    if err:
        return err

    company = (body.get("company") or "").strip()
    storecode = (body.get("storecode") or "").strip()
    try:
        days_back = int(body.get("days_back") or 7)
    except (TypeError, ValueError):
        days_back = 7
    try:
        limit = int(body.get("limit") or 100)
    except (TypeError, ValueError):
        limit = 100

    from assistant.vip_lifecycle import compute_lifecycle_migrations

    data = compute_lifecycle_migrations(
        company,
        storecode,
        days_back=days_back,
        transition=(body.get("transition") or "").strip(),
        limit=limit,
    )
    return JsonResponse({"ok": True, "data": data})


@csrf_exempt
@require_http_methods(["POST"])
def mp_vip_lifecycle_crm_tasks_api(request: HttpRequest):
    body, err = _parse_json_body(request)
    if err:
        return err

    profile, err = _mp_auth(body)
    if err:
        return err

    company = (body.get("company") or "").strip()
    storecode = (body.get("storecode") or "").strip()
    ecode = (body.get("ecode") or body.get("usercode") or "").strip()
    dry_run = str(body.get("dry_run") or "true").lower() in ("1", "true", "yes")
    try:
        limit = int(body.get("limit") or 50)
    except (TypeError, ValueError):
        limit = 50

    from assistant.vip_lifecycle_crm import create_lifecycle_crm_tasks

    result = create_lifecycle_crm_tasks(
        company,
        storecode,
        segment=(body.get("segment") or "at_risk").strip(),
        ecode=ecode,
        limit=limit,
        dry_run=dry_run,
        creater_ecode=ecode,
    )
    if result.get("error"):
        return JsonResponse({"ok": False, "error": result["error"]}, status=400)
    return JsonResponse({"ok": True, "result": result})
