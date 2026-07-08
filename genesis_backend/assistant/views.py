#coding = utf-8
import json
import re
from typing import Any, Dict, List, Optional, Set

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.db import DatabaseError, transaction
from django.db.models import Max
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

import common.constants as common_constants
from baseinfo.models import _ITEM_APPOPTION_SEG_BASES
from assistant.agents import chat_completion, list_agent_choices
from assistant.agent_profiles import (
    answer_system_prompt_for_profile,
    get_agent_profile,
    list_agent_profiles,
    planner_system_prompt_for_profile,
)
from assistant.context_pack import build_system_lexicon
from assistant.data_tools import (
    run_tool_plan,
    safe_json_dumps,
)
from assistant.vip_tools import (
    BATCH_EXPORT_MAX,
    fetch_sleeping_vips_for_export,
    fetch_store_vips_for_export,
    tool_vip_sleeping_alert,
)
from assistant.plan_heuristic import heuristic_plan
from assistant.export_fields import attach_field_meta_to_datasets, build_field_glossary_for_datasets
from assistant.export_tables import flatten_panel_payload, flatten_tool_results_for_export
from assistant.export_xlsx import build_xlsx_http_response
from assistant.models import AssistantMessage, AssistantThread


def _assistant_db_error_response(
    exc: BaseException, extra: Optional[Dict[str, Any]] = None
) -> JsonResponse:
    """助手会话表未迁移或其它 DB 异常时返回 JSON，避免 DEBUG 下整页 HTML 500。"""
    msg = str(exc)
    low = msg.lower()
    hint = "助手会话功能需要数据库表。请在 genesis_backend 目录执行：python manage.py migrate assistant"
    if "doesn't exist" in low or "不存在" in msg or "unknown table" in low or "no such table" in low:
        hint = (
            "缺少助手相关数据表（assistant_thread / assistant_message）。"
            "请在项目目录执行：python manage.py migrate assistant"
        )
    payload: Dict[str, Any] = {"ok": False, "error": hint, "detail": msg[:2000]}
    if extra:
        payload.update(extra)
    return JsonResponse(payload, status=503)


def _parse_json_object(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    if not text:
        raise ValueError("规划模型返回为空，无法解析 JSON。请重试；若持续失败请检查 DEEPSEEK_API_KEY 或换用 deepseek 模型。")
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for m in re.finditer(r"\{[\s\S]*?\}", text):
            frag = m.group(0)
            try:
                obj = json.loads(frag)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "tools" in obj:
                return obj
        m = re.search(r"\{[\s\S]*\}", text)
        if m:
            return json.loads(m.group(0))
        raise ValueError(
            "规划模型未返回合法 JSON。"
            f"原始内容开头: {text[:300]!r}"
        ) from None


def _normalize_tool_specs(plan_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    tools = plan_obj.get("tools")
    if not isinstance(tools, list):
        return []
    normalized: List[Dict[str, Any]] = []
    for t in tools:
        if not isinstance(t, dict):
            continue
        name = (t.get("name") or "").strip()
        args = t.get("args") if isinstance(t.get("args"), dict) else {}
        if name:
            normalized.append({"name": name, "args": args})
    return normalized


def _resolve_plan_object(
    agent_id: str,
    plan_messages: List[Dict[str, str]],
    *,
    profile_id: str,
    user_message: str,
    allowed_tools: Set[str],
) -> tuple[Dict[str, Any], str, str, bool]:
    """
    调用规划模型并解析 JSON。失败时重试（json_mode）→ 启发式回退。
    返回 (plan_obj, plan_raw, plan_model, used_heuristic)。
    """
    plan_raw, plan_model = chat_completion(
        agent_id, plan_messages, temperature=0.0, json_mode=True
    )
    try:
        return _parse_json_object(plan_raw), plan_raw, plan_model, False
    except ValueError:
        pass

    retry_messages = list(plan_messages) + [
        {"role": "assistant", "content": (plan_raw or "")[:800]},
        {
            "role": "user",
            "content": (
                "错误：你刚才输出了自然语言/表格，不是 JSON。"
                '请仅输出一个 JSON 对象：{"tools":[{"name":"工具名","args":{...}}],"brief":"..."}，'
                "不要 markdown、不要代码块、不要解释、不要直接回答用户。"
            ),
        },
    ]
    plan_raw, plan_model = chat_completion(
        agent_id, retry_messages, temperature=0.0, json_mode=True
    )
    try:
        return _parse_json_object(plan_raw), plan_raw, plan_model, False
    except ValueError:
        pass

    fallback = heuristic_plan(profile_id, user_message, allowed_tools)
    if fallback:
        return fallback, json.dumps(fallback, ensure_ascii=False), plan_model, True
    raise ValueError(
        "规划模型未返回合法 JSON，且无法根据问题自动选择工具。"
        f"原始内容开头: {(plan_raw or '')[:300]!r}"
    )


def _truncate(s: str, n: int) -> str:
    if len(s) <= n:
        return s
    return s[: max(0, n - 24)] + "\n...[truncated]..."


MAX_PLANNER_TOOL_JSON = 6000
MAX_ANSWER_PRIOR_CHARS = 12000

_DB_ESC_PREFIX = "__UE__"


def _encode_db_text(s: str) -> str:
    text = s or ""
    # 统一以 ASCII 安全形式持久化，兼容非 utf8mb4 库表。
    return _DB_ESC_PREFIX + text.encode("unicode_escape").decode("ascii")


def _decode_db_text(s: str) -> str:
    text = s or ""
    if text.startswith(_DB_ESC_PREFIX):
        body = text[len(_DB_ESC_PREFIX):]
        try:
            return bytes(body, "ascii").decode("unicode_escape")
        except Exception:
            return body
    return text

def _next_sequence(thread: AssistantThread) -> int:
    v = thread.messages.aggregate(m=Max("sequence"))["m"]
    return (v or 0) + 1


def _serialize_thread(t: AssistantThread, include_count: bool = True) -> Dict[str, Any]:
    d: Dict[str, Any] = {
        "id": t.pk,
        "title": (_decode_db_text(t.title or "")).strip() or f"会话 #{t.pk}",
        "company": t.company or "",
        "storecode": t.storecode or "",
        "agent_id": t.agent_id or "deepseek",
        "profile_id": t.profile_id or "general",
        "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S") if t.created_at else "",
        "updated_at": t.updated_at.strftime("%Y-%m-%d %H:%M:%S") if t.updated_at else "",
    }
    if include_count:
        d["message_count"] = t.messages.count()
    return d


def _serialize_message(m: AssistantMessage) -> Dict[str, Any]:
    return {
        "id": m.pk,
        "role": m.role,
        "content": _decode_db_text(m.content),
        "metadata": m.metadata or {},
        "sequence": m.sequence,
        "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
    }


def _messages_to_planner_payload(messages: List[AssistantMessage]) -> List[Dict[str, str]]:
    """将已落库消息转为规划模型多轮对话（助手轮附带结构化查询结果便于延续分析）。"""
    out: List[Dict[str, str]] = []
    for m in messages:
        if m.role == AssistantMessage.ROLE_USER:
            out.append({"role": "user", "content": _decode_db_text(m.content)})
        elif m.role == AssistantMessage.ROLE_ASSISTANT:
            meta = m.metadata or {}
            plan = meta.get("plan") if isinstance(meta.get("plan"), dict) else {}
            brief = plan.get("brief") or ""
            tools_used: List[str] = []
            for t in plan.get("tools") or []:
                if isinstance(t, dict) and t.get("name"):
                    tools_used.append(str(t["name"]))
            compact = f"[上轮已执行规划] brief={brief}; tools={tools_used}"
            tr = meta.get("tool_results")
            if tr is not None:
                compact += "\n[结构化查询结果 JSON]\n" + _truncate(
                    safe_json_dumps(tr), MAX_PLANNER_TOOL_JSON
                )
            out.append({"role": "assistant", "content": compact})
    return out


def _prior_dialog_for_answer(prior_messages: List[AssistantMessage]) -> str:
    lines: List[str] = []
    for m in prior_messages:
        if m.role == AssistantMessage.ROLE_USER:
            lines.append("用户: " + _decode_db_text(m.content))
        elif m.role == AssistantMessage.ROLE_ASSISTANT:
            lines.append("助手: " + _decode_db_text(m.content))
    return _truncate("\n\n".join(lines), MAX_ANSWER_PRIOR_CHARS)


def _assistant_api_urls() -> Dict[str, str]:
    """
    使用 reverse 生成绝对路径，避免页面在 /assistant 无尾斜杠时相对路径 api/… 被解析到站点根下而返回 HTML 404。
    """
    sentinel_pk = 2_147_483_647  # 占位（避免 JS 大整数精度问题），前端替换为真实 thread id
    return {
        "url_chat": reverse("assistant:assistant_chat_api"),
        "url_threads": reverse("assistant:assistant_threads_api"),
        "url_agents": reverse("assistant:assistant_agents_api"),
        "url_profiles": reverse("assistant:assistant_profiles_api"),
        "url_thread_detail_template": reverse(
            "assistant:assistant_thread_detail_api",
            kwargs={"pk": sentinel_pk},
        ),
        "thread_detail_pk_placeholder": sentinel_pk,
        "url_switch_user": reverse("assistant:assistant_switch_user"),
        "url_logout_admin_home": reverse("assistant:assistant_logout_admin_home"),
        "url_export": reverse("assistant:assistant_export_api"),
        "url_export_datasets": reverse("assistant:assistant_export_datasets_api"),
        "url_vip_sleeping_alert": reverse("assistant:assistant_vip_sleeping_alert_api"),
        "url_vip_batch_export": reverse("assistant:assistant_vip_batch_export_api"),
        "url_store_dimension_sales": reverse("report:get_store_dimension_sales"),
    }


@staff_member_required
@ensure_csrf_cookie
@require_http_methods(["GET"])
def assistant_page(request: HttpRequest):
    agents = list_agent_choices()
    profiles = list_agent_profiles()
    default_company = getattr(common_constants, "COMPANYID", "demo") or "demo"
    store_dimension_choices = [
        {"value": v, "label": "%s — %s" % (v, lab)} for v, lab in _ITEM_APPOPTION_SEG_BASES
    ] + [{"value": "ttype", "label": "ttype — 项目大类"}]
    return render(
        request,
        "assistant/chat.html",
        {
            "default_company": request.GET.get("company") or default_company,
            "default_storecode": request.GET.get("storecode") or "88",
            "agents": agents,
            "profiles": profiles,
            "assistant_api_urls": _assistant_api_urls(),
            "current_username": request.user.get_username(),
            "store_dimension_choices": store_dimension_choices,
        },
    )


@require_http_methods(["GET"])
def assistant_switch_user(request: HttpRequest):
    # 彻底清空当前会话上下文，避免不同账号共享旧 session 环境。
    try:
        request.session.flush()
    except Exception:
        pass
    logout(request)
    login_url = reverse("admin:login")
    next_url = reverse("assistant:assistant_page")
    return redirect(f"{login_url}?next={next_url}")


@require_http_methods(["GET"])
def assistant_logout_admin_home(request: HttpRequest):
    try:
        request.session.flush()
    except Exception:
        pass
    logout(request)
    return redirect(reverse("admin:index"))


@staff_member_required
@require_http_methods(["GET", "POST"])
def assistant_threads_api(request: HttpRequest):
    if request.method == "GET":
        try:
            qs = AssistantThread.objects.filter(user=request.user).order_by("-updated_at")[:120]
            return JsonResponse(
                {"ok": True, "threads": [_serialize_thread(t) for t in qs]},
            )
        except DatabaseError as exc:
            return _assistant_db_error_response(exc)
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        body = {}
    company = (body.get("company") or getattr(common_constants, "COMPANYID", "demo") or "demo").strip()
    storecode = (body.get("storecode") or "88").strip()
    title = (body.get("title") or "新对话").strip()[:200]
    agent_id = (body.get("agent") or "deepseek").strip().lower()
    profile_id = (body.get("profile") or "general").strip().lower()
    try:
        t = AssistantThread.objects.create(
            user=request.user,
            title=_encode_db_text(title),
            company=company,
            storecode=storecode,
            agent_id=agent_id,
            profile_id=profile_id,
        )
        return JsonResponse({"ok": True, "thread": _serialize_thread(t)})
    except DatabaseError as exc:
        return _assistant_db_error_response(exc)


@staff_member_required
@require_http_methods(["GET"])
def assistant_thread_detail_api(request: HttpRequest, pk: int):
    try:
        t = AssistantThread.objects.filter(pk=pk, user=request.user).first()
        if not t:
            return JsonResponse({"ok": False, "error": "会话不存在或无权访问"}, status=404)
        msgs = [_serialize_message(m) for m in t.messages.order_by("sequence", "id")]
        return JsonResponse(
            {
                "ok": True,
                "thread": _serialize_thread(t, include_count=False),
                "messages": msgs,
            },
        )
    except DatabaseError as exc:
        return _assistant_db_error_response(exc)


@staff_member_required
@require_http_methods(["POST"])
def assistant_chat_api(request: HttpRequest):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "无效的 JSON 请求体"}, status=400)

    message = (body.get("message") or "").strip()
    if not message:
        return JsonResponse({"ok": False, "error": "message 不能为空"}, status=400)

    agent_id = (body.get("agent") or "deepseek").strip().lower()
    profile_id = (body.get("profile") or "general").strip().lower()
    company = (body.get("company") or getattr(common_constants, "COMPANYID", "demo") or "demo").strip()
    storecode = (body.get("storecode") or "88").strip()
    thread_id = body.get("thread_id")
    thread: AssistantThread | None = None

    try:
        if thread_id is not None and thread_id != "":
            try:
                tid = int(thread_id)
            except (TypeError, ValueError):
                return JsonResponse({"ok": False, "error": "thread_id 无效"}, status=400)
            thread = AssistantThread.objects.filter(pk=tid, user=request.user).first()
            if not thread:
                return JsonResponse({"ok": False, "error": "会话不存在或无权访问"}, status=404)
        else:
            auto_title = message[:120] if len(message) <= 120 else message[:117] + "..."
            thread = AssistantThread.objects.create(
                user=request.user,
                title=_encode_db_text(auto_title),
                company=company,
                storecode=storecode,
                agent_id=agent_id,
                profile_id=profile_id,
            )
            tid = thread.pk

        thread = AssistantThread.objects.get(pk=tid, user=request.user)
        thread.company = company
        thread.storecode = storecode
        thread.agent_id = agent_id
        thread.profile_id = profile_id
        thread.save(update_fields=["company", "storecode", "agent_id", "profile_id", "updated_at"])

        prior_db = list(thread.messages.order_by("sequence", "id"))
        was_empty = len(prior_db) == 0
    except DatabaseError as exc:
        return _assistant_db_error_response(exc)

    profile = get_agent_profile(profile_id)
    try:
        lex = build_system_lexicon(company)
    except Exception as ex:
        lex = f"【系统字典加载失败，已降级】{ex}"
    plan_messages: List[Dict[str, str]] = [
        {"role": "system", "content": planner_system_prompt_for_profile(profile_id) + "\n\n" + lex},
    ]
    plan_messages.extend(_messages_to_planner_payload(prior_db))
    plan_messages.append({"role": "user", "content": message})

    try:
        allowed_tools = set(profile.tool_registry.keys())
        plan_obj, plan_raw, plan_model, used_heuristic = _resolve_plan_object(
            agent_id,
            plan_messages,
            profile_id=profile_id,
            user_message=message,
            allowed_tools=allowed_tools,
        )
        normalized = _normalize_tool_specs(plan_obj)

        tool_results, tool_errors = run_tool_plan(
            company, storecode, normalized, registry=profile.tool_registry
        )

        prior_text = _prior_dialog_for_answer(prior_db)
        answer_user_parts = []
        if prior_text.strip():
            answer_user_parts.append("以下为此前多轮对话（含助手已给出的结论，请在指代「上次」「前面结果」时结合理解）：\n" + prior_text)
        answer_user_parts.append(
            f"当前公司 company={company!r}，门店 storecode={storecode!r}。\n"
            f"当前用户问题：{message}\n\n"
            f"本轮规划说明：{plan_obj.get('brief') or ''}\n\n"
            f"本轮系统新查询结果（JSON）：\n{safe_json_dumps(tool_results)}"
        )
        answer_messages = [
            {"role": "system", "content": answer_system_prompt_for_profile(profile_id) + "\n\n" + lex},
            {"role": "user", "content": "\n\n".join(answer_user_parts)},
        ]
        answer_text, answer_model = chat_completion(agent_id, answer_messages, temperature=0.3)

        meta_out = {
            "plan": plan_obj,
            "plan_raw": plan_raw,
            "plan_model": plan_model,
            "plan_heuristic": used_heuristic,
            "profile_id": profile_id,
            "tool_results": tool_results,
            "tool_errors": tool_errors,
            "answer_model": answer_model,
        }

        with transaction.atomic():
            seq = _next_sequence(thread)
            AssistantMessage.objects.create(
                thread=thread,
                role=AssistantMessage.ROLE_USER,
                content=_encode_db_text(message),
                sequence=seq,
                metadata={"company": company, "storecode": storecode},
            )
            assistant_msg = AssistantMessage.objects.create(
                thread=thread,
                role=AssistantMessage.ROLE_ASSISTANT,
                content=_encode_db_text(answer_text),
                sequence=seq + 1,
                metadata=meta_out,
            )
            if was_empty:
                thread.title = _encode_db_text(message[:120] if len(message) <= 120 else message[:117] + "...")
                thread.save(update_fields=["title", "updated_at"])

        return JsonResponse(
            {
                "ok": True,
                "thread_id": thread.pk,
                "assistant_message_id": assistant_msg.pk,
                "answer": answer_text,
                "plan": {"raw": plan_raw, "parsed": plan_obj, "model": plan_model},
                "tool_results": tool_results,
                "tool_errors": tool_errors,
                "answer_model": answer_model,
            }
        )
    except DatabaseError as e:
        tid_out = thread.pk if thread is not None else None
        return _assistant_db_error_response(e, {"thread_id": tid_out})
    except Exception as e:
        tid_out = thread.pk if thread is not None else None
        return JsonResponse(
            {
                "ok": False,
                "error": str(e),
                "thread_id": tid_out,
            },
            status=500,
        )


def _flatten_export_tables(tool_results: Any) -> List[Dict[str, Any]]:
    return flatten_tool_results_for_export(tool_results)


def _clean_export_datasets(datasets: Any) -> List[Dict[str, Any]]:
    cleaned: List[Dict[str, Any]] = []
    if not isinstance(datasets, list):
        return cleaned
    for ds in datasets:
        if not isinstance(ds, dict):
            continue
        name = str(ds.get("name") or "sheet")
        rows = ds.get("rows")
        if isinstance(rows, list) and rows and all(isinstance(x, dict) for x in rows):
            cleaned.append({"name": name, "rows": rows})
    return cleaned


@staff_member_required
@require_http_methods(["POST"])
def assistant_export_api(request: HttpRequest):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "无效的 JSON 请求体"}, status=400)

    format_type = (body.get("format") or "xlsx").strip().lower()
    if format_type not in {"xlsx"}:
        return JsonResponse({"ok": False, "error": "仅支持 format=xlsx"}, status=400)

    datasets = body.get("datasets")

    if not isinstance(datasets, list):
        panel_tool = (body.get("panel_tool") or "").strip()
        panel_data = body.get("panel_data")
        if panel_tool and panel_data is not None:
            datasets = flatten_panel_payload(panel_tool, panel_data)
        else:
            msg_id = body.get("message_id")
            thread_id = body.get("thread_id")
            if msg_id is not None:
                try:
                    msg_id_i = int(msg_id)
                except (TypeError, ValueError):
                    return JsonResponse({"ok": False, "error": "message_id 无效"}, status=400)
                msg_qs = AssistantMessage.objects.filter(
                    pk=msg_id_i, role=AssistantMessage.ROLE_ASSISTANT, thread__user=request.user
                )
                if thread_id is not None:
                    try:
                        thread_id_i = int(thread_id)
                        msg_qs = msg_qs.filter(thread_id=thread_id_i)
                    except (TypeError, ValueError):
                        return JsonResponse({"ok": False, "error": "thread_id 无效"}, status=400)
                msg = msg_qs.first()
                if not msg:
                    return JsonResponse({"ok": False, "error": "导出来源消息不存在或无权访问"}, status=404)
                datasets = _flatten_export_tables((msg.metadata or {}).get("tool_results"))
            else:
                datasets = _flatten_export_tables(body.get("tool_results"))

    cleaned = _clean_export_datasets(datasets)
    if not cleaned:
        return JsonResponse({"ok": False, "error": "没有可导出的表格数据"}, status=400)

    try:
        max_rows = max(1000, min(int(body.get("max_rows_per_sheet") or 50000), 200000))
    except (TypeError, ValueError):
        max_rows = 50000

    filename = (body.get("filename") or "assistant-export.xlsx").strip() or "assistant-export.xlsx"
    glossary = build_field_glossary_for_datasets(cleaned)
    return build_xlsx_http_response(
        cleaned,
        filename=filename,
        max_rows_per_sheet=max_rows,
        field_glossary=glossary,
    )


@staff_member_required
@require_http_methods(["POST"])
def assistant_export_datasets_api(request: HttpRequest):
    """将 tool_results / 面板数据扁平化为 datasets（供前端 JSON/CSV 导出）。"""
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "无效的 JSON 请求体"}, status=400)

    datasets = body.get("datasets")
    if not isinstance(datasets, list):
        panel_tool = (body.get("panel_tool") or "").strip()
        panel_data = body.get("panel_data")
        if panel_tool and panel_data is not None:
            datasets = flatten_panel_payload(panel_tool, panel_data)
        else:
            msg_id = body.get("message_id")
            thread_id = body.get("thread_id")
            if msg_id is not None:
                try:
                    msg_id_i = int(msg_id)
                except (TypeError, ValueError):
                    return JsonResponse({"ok": False, "error": "message_id 无效"}, status=400)
                msg_qs = AssistantMessage.objects.filter(
                    pk=msg_id_i, role=AssistantMessage.ROLE_ASSISTANT, thread__user=request.user
                )
                if thread_id is not None:
                    try:
                        thread_id_i = int(thread_id)
                        msg_qs = msg_qs.filter(thread_id=thread_id_i)
                    except (TypeError, ValueError):
                        return JsonResponse({"ok": False, "error": "thread_id 无效"}, status=400)
                msg = msg_qs.first()
                if not msg:
                    return JsonResponse({"ok": False, "error": "导出来源消息不存在或无权访问"}, status=404)
                datasets = _flatten_export_tables((msg.metadata or {}).get("tool_results"))
            else:
                datasets = _flatten_export_tables(body.get("tool_results"))

    cleaned = _clean_export_datasets(datasets)
    if not cleaned:
        return JsonResponse({"ok": False, "error": "没有可导出的表格数据"}, status=400)
    glossary = build_field_glossary_for_datasets(cleaned)
    return JsonResponse(
        {
            "ok": True,
            "datasets": attach_field_meta_to_datasets(cleaned),
            "field_glossary": glossary,
            "sheet_count": len(cleaned),
        }
    )


def _parse_vip_scope(body: Dict[str, Any], request: HttpRequest) -> tuple[str, str]:
    company = (body.get("company") or request.GET.get("company") or getattr(common_constants, "COMPANYID", "demo") or "demo").strip()
    storecode = (body.get("storecode") or request.GET.get("storecode") or "88").strip()
    return company, storecode


@staff_member_required
@require_http_methods(["GET", "POST"])
def assistant_vip_sleeping_alert_api(request: HttpRequest):
    if request.method == "GET":
        try:
            body = dict(request.GET.items())
        except Exception:
            body = {}
    else:
        try:
            body = json.loads(request.body.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({"ok": False, "error": "无效的 JSON 请求体"}, status=400)

    company, storecode = _parse_vip_scope(body, request)
    try:
        inactive_days = int(body.get("inactive_days") or 90)
    except (TypeError, ValueError):
        inactive_days = 90
    try:
        critical_days = int(body.get("critical_days") or 180)
    except (TypeError, ValueError):
        critical_days = 180
    try:
        limit = int(body.get("limit") or 200)
    except (TypeError, ValueError):
        limit = 200
    try:
        min_lifetime_amount = float(body.get("min_lifetime_amount") or 0)
    except (TypeError, ValueError):
        min_lifetime_amount = 0

    data = tool_vip_sleeping_alert(
        company=company,
        storecode=storecode,
        inactive_days=inactive_days,
        critical_days=critical_days,
        viptype=(body.get("viptype") or "").strip(),
        min_lifetime_amount=min_lifetime_amount,
        ecode=(body.get("ecode") or "").strip(),
        limit=min(limit, 500),
    )
    return JsonResponse({"ok": True, "data": data})


@staff_member_required
@require_http_methods(["POST"])
def assistant_vip_batch_export_api(request: HttpRequest):
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "无效的 JSON 请求体"}, status=400)

    export_type = (body.get("export_type") or "sleeping_vips").strip().lower()
    company, storecode = _parse_vip_scope(body, request)
    try:
        limit = max(1, min(int(body.get("limit") or BATCH_EXPORT_MAX), BATCH_EXPORT_MAX))
    except (TypeError, ValueError):
        limit = BATCH_EXPORT_MAX

    datasets: List[Dict[str, Any]] = []
    filename = "vip-export.xlsx"

    if export_type == "sleeping_vips":
        try:
            inactive_days = int(body.get("inactive_days") or 90)
        except (TypeError, ValueError):
            inactive_days = 90
        try:
            critical_days = int(body.get("critical_days") or 180)
        except (TypeError, ValueError):
            critical_days = 180
        try:
            min_lifetime_amount = float(body.get("min_lifetime_amount") or 0)
        except (TypeError, ValueError):
            min_lifetime_amount = 0
        result = fetch_sleeping_vips_for_export(
            company=company,
            storecode=storecode,
            limit=limit,
            inactive_days=inactive_days,
            critical_days=critical_days,
            viptype=(body.get("viptype") or "").strip(),
            min_lifetime_amount=min_lifetime_amount,
            ecode=(body.get("ecode") or "").strip(),
        )
        rows = result.get("sleeping_vips") or []
        summary_rows = [result.get("summary") or {}]
        criteria_rows = [result.get("criteria") or {}]
        datasets = [
            {"name": "vip_sleeping_alert_sleeping_vips", "rows": rows},
            {"name": "summary", "rows": summary_rows},
            {"name": "criteria", "rows": criteria_rows},
        ]
        filename = f"sleeping-vips-{storecode}.xlsx"
    elif export_type == "store_vips":
        rows = fetch_store_vips_for_export(
            company=company,
            storecode=storecode,
            limit=limit,
            viptype=(body.get("viptype") or "").strip(),
        )
        datasets = [{"name": "batch_store_vips", "rows": rows}]
        filename = f"store-vips-{storecode}.xlsx"
    else:
        return JsonResponse(
            {"ok": False, "error": "export_type 仅支持 sleeping_vips 或 store_vips"},
            status=400,
        )

    cleaned = _clean_export_datasets(datasets)
    if not cleaned or not any(ds.get("rows") for ds in cleaned):
        return JsonResponse({"ok": False, "error": "没有可导出的会员数据"}, status=400)

    try:
        max_rows = max(1000, min(int(body.get("max_rows_per_sheet") or 50000), 200000))
    except (TypeError, ValueError):
        max_rows = 50000

    glossary = build_field_glossary_for_datasets(cleaned)
    return build_xlsx_http_response(
        cleaned,
        filename=filename,
        max_rows_per_sheet=max_rows,
        field_glossary=glossary,
    )


@staff_member_required
@require_http_methods(["GET"])
def assistant_agents_api(_request: HttpRequest):
    return JsonResponse({"ok": True, "agents": list_agent_choices()})


@staff_member_required
@require_http_methods(["GET"])
def assistant_profiles_api(_request: HttpRequest):
    return JsonResponse({"ok": True, "profiles": list_agent_profiles()})
