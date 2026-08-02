# coding=utf-8
"""客户回访 AI 话术建议：汇总客户/任务/历史沟通上下文，生成结构化话术。"""

from __future__ import annotations

import datetime
import json
from typing import Any, Dict, List, Optional

from django.db.models import Count

from baseinfo.models import Empl, Goods, Serviece
from cashier.models import Expense, Expvstoll
from crm.models import CrmCase, CrmCaseDetail, VipCaseDetail


def _mask_phone(phone: Optional[str]) -> str:
    s = (phone or "").strip()
    if len(s) >= 11:
        return s[:3] + "****" + s[-4:]
    if len(s) >= 7:
        return s[:3] + "****" + s[-3:]
    return s or ""


def _parse_yyyymmdd(raw: Optional[str]) -> Optional[datetime.date]:
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%Y%m%d", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _empl_names(company: str, ecodes: List[str]) -> Dict[str, str]:
    codes = [c for c in ecodes if c]
    if not codes:
        return {}
    return dict(
        Empl.objects.filter(company=company, ecode__in=codes, flag="Y")
        .values_list("ecode", "ename")
    )


def _recent_visits(company: str, vip) -> List[Dict[str, Any]]:
    rows = []
    for t in (
        Expvstoll.objects.filter(company=company, flag="Y", valiflag="Y", vipuuid=vip)
        .order_by("-vsdate", "-create_time")[:6]
    ):
        rows.append({
            "vsdate": t.vsdate or "",
            "ttype": t.ttype or "",
            "amount": float(t.totmount or 0),
        })
    return rows


def _preferred_items(company: str, vip) -> List[Dict[str, Any]]:
    agg = list(
        Expense.objects.filter(
            company=company,
            flag="Y",
            transuuid__vipuuid=vip,
            ttype__in=("S", "G"),
            stype="N",
        )
        .values("srvcode", "ttype")
        .annotate(cnt=Count("uuid"))
        .order_by("-cnt")[:5]
    )
    if not agg:
        return []
    srv_codes = [r["srvcode"] for r in agg if r["ttype"] == "S" and r["srvcode"]]
    goods_codes = [r["srvcode"] for r in agg if r["ttype"] == "G" and r["srvcode"]]
    srv_map = dict(
        Serviece.objects.filter(company=company, svrcdoe__in=srv_codes)
        .values_list("svrcdoe", "svrname")
    )
    goods_map = dict(
        Goods.objects.filter(company=company, gcode__in=goods_codes)
        .values_list("gcode", "gname")
    )
    items = []
    for r in agg:
        name = srv_map.get(r["srvcode"]) or goods_map.get(r["srvcode"]) or r["srvcode"] or ""
        items.append({"name": name, "count": r["cnt"]})
    return items


def _communication_logs(company: str, vip, limit: int = 10) -> List[Dict[str, Any]]:
    logs = VipCaseDetail.objects.filter(company=company, flag="Y", vipuuid=vip).order_by(
        "-create_time"
    )[:limit]
    return [
        {
            "create_time": log.create_time.strftime("%Y-%m-%d") if log.create_time else "",
            "casetype": log.casetype or "",
            "content": (log.detail or log.detaildescription or "").strip(),
            "ecode": log.ecode or "",
        }
        for log in logs
        if (log.detail or log.detaildescription or "").strip()
    ]


def _task_attempts(task: CrmCase, limit: int = 10) -> List[Dict[str, Any]]:
    attempts = CrmCaseDetail.objects.filter(caseid=task, flag="Y").order_by("create_time")[:limit]
    return [
        {
            "create_time": a.create_time.strftime("%Y-%m-%d") if a.create_time else "",
            "channel": a.channel or "",
            "outcome": a.outcome or "",
            "content": (a.detail or a.detaildescription or "").strip(),
        }
        for a in attempts
        if (a.detail or a.detaildescription or "").strip()
    ]


def build_touch_context(
    company: str,
    storecode: str,
    task: CrmCase,
    *,
    channel: str = "",
    outcome: str = "",
    current_ecode: str = "",
    current_ename: str = "",
) -> Dict[str, Any]:
    """组装话术所需的客户/任务/历史上下文。"""
    vip = task.vipuuid
    empl_names = _empl_names(company, [task.ecode or "", (vip.ecode if vip else "") or "", (vip.ecode2 if vip else "") or ""])
    casetype_choices = dict(CrmCaseDetail.CRM_CHANNEL)
    channel_name = casetype_choices.get(channel or "", channel or "")
    visits = _recent_visits(company, vip) if vip else []
    last_vsdate = visits[0]["vsdate"] if visits else ""
    last_date = _parse_yyyymmdd(last_vsdate)
    days_since = (datetime.date.today() - last_date).days if last_date else None
    risk_note = ""
    if days_since is not None and days_since >= 90:
        risk_note = "客户已超过 %d 天未到店，建议以关心近况为主，再自然引出到店邀约。" % days_since
    return {
        "customer": {
            "vname": (vip.vname if vip else "") or "",
            "vcode": (vip.vcode if vip else "") or "",
            "mtcode": _mask_phone(vip.mtcode if vip else ""),
            "birth": (vip.birth if vip else "") or "",
            "indate": (vip.indate.strftime("%Y-%m-%d") if vip and vip.indate else ""),
            "viplevel": (vip.viplevel if vip else "") or "",
            "viptype": (vip.viptype if vip else "") or "",
            "adviser": empl_names.get((vip.ecode if vip else "") or "", (vip.ecode if vip else "") or ""),
            "therapist": empl_names.get((vip.ecode2 if vip else "") or "", (vip.ecode2 if vip else "") or ""),
        },
        "task": {
            "casetype": task.casetype or "",
            "casedesc": task.casedesc or "",
            "rule_name": task.rule.rule_name if task.rule else "",
            "planbegindate": task.planbegindate.isoformat() if task.planbegindate else "",
            "planfinishdate": task.planfinishdate.isoformat() if task.planfinishdate else "",
            "ecode": task.ecode or "",
            "empl_name": empl_names.get(task.ecode or "", ""),
        },
        "channel": channel_name,
        "outcome": outcome or "",
        "current_employee": {
            "ecode": current_ecode or "",
            "ename": current_ename or "",
        },
        "recent_visits": visits,
        "preferred_items": _preferred_items(company, vip) if vip else [],
        "recent_communications": _communication_logs(company, vip) if vip else [],
        "task_attempts": _task_attempts(task),
        "risk_note": risk_note,
        "company": company,
        "storecode": storecode or "",
    }


def build_suggest_messages(context: Dict[str, Any], variants: int = 3) -> List[Dict[str, str]]:
    system = (
        "你是 Genesis 美业系统的客户回访话术助手。根据提供的客户档案、消费记录、历史沟通和当前回访任务，"
        "生成适合指定渠道的简体中文话术。\n"
        "要求：\n"
        "1. 只能基于提供的信息，不得虚构客户的消费、项目、效果或承诺。\n"
        "2. 结合历史沟通，不要重复客户已答复过的问题，不要提及客户已明确拒绝的内容。\n"
        "3. 话术口语化、自然，符合美业门店场景，避免夸大效果和强行推销。\n"
        "4. 输出严格 JSON 对象：{\"items\":[{\"opening\":\"...\",\"care_points\":[\"...\"],"
        "\"invitation\":\"...\",\"closing\":\"...\",\"avoid\":[\"...\"]}]}。\n"
        "5. items 必须包含 %d 个不同语气与切入角度的话术组合（如温馨关怀、邀约到店、简洁高效），"
        "每项精炼、可直接使用，且彼此有明显差异。" % int(variants)
    )
    user = "当前回访上下文：\n" + json.dumps(context, ensure_ascii=False, indent=1)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _static_fallback(context: Dict[str, Any], channel: str = "") -> Dict[str, Any]:
    customer = context.get("customer") or {}
    task = context.get("task") or {}
    vname = customer.get("vname") or "顾客"
    task_desc = task.get("casedesc") or task.get("rule_name") or "客户回访"
    channel_name = context.get("channel") or "电话"
    items = context.get("preferred_items") or []
    item_names = "、".join(i["name"] for i in items[:3])
    visits = context.get("recent_visits") or []
    last_date = visits[0]["vsdate"] if visits else ""
    risk_note = context.get("risk_note") or ""
    current_emp = context.get("current_employee") or {}
    current_name = (current_emp.get("ename") or "").strip()
    care_points = []
    if last_date:
        care_points.append("上次到店是 %s，先问问这段时间身体和皮肤状态如何。" % last_date)
    if item_names:
        care_points.append("可以自然提到她常做的 %s，关心最近是否有不适。" % item_names)
    if risk_note:
        care_points.append(risk_note)
    if not care_points:
        care_points.append("先问候近况，再按本次回访主题展开。")
    if channel_name == "短信":
        opening = "%s您好，我是%s门店顾问，今天是%s，想和您简单确认下近况。" % (vname, context.get("company", ""), task_desc[:30])
        invitation = "方便时回复我，我可以帮您安排到店护理。"
    else:
        opener = "我是%s，负责您的顾问" % current_name if current_name else "我是负责您的顾问"
        opening = "%s您好，%s。今天联系您主要是%s，想了解一下您最近的情况。" % (vname, opener, task_desc[:40])
        invitation = "这周如果有时间，我帮您安排一次到店护理，您看哪天方便？"
    return {
        "source": "fallback",
        "model": "",
        "opening": opening,
        "care_points": care_points[:3],
        "invitation": invitation,
        "closing": "那我们先这样，稍后再联系您，祝您生活愉快。",
        "avoid": [
            "不要重复询问历史沟通中已答复的问题",
            "不要承诺治疗效果或夸大活动力度",
            "客户表示不方便时不要继续推销",
        ],
    }


def _static_variants(context: Dict[str, Any], channel: str = "", count: int = 3) -> List[Dict[str, Any]]:
    """静态兜底话术组合，支持多套差异模板。"""
    base = _static_fallback(context, channel)
    vname = (context.get("customer") or {}).get("vname") or "顾客"
    task_desc = (context.get("task") or {}).get("casedesc") or (context.get("task") or {}).get("rule_name") or "客户回访"
    second = {
        **base,
        "opening": "%s您好，最近身体和皮肤状态怎么样？上次护理后感觉如何？" % vname,
        "invitation": "这周我帮您预留了方便的时间段，您看周几到店比较合适？",
    }
    third = {
        **base,
        "opening": "您好，我是您的顾问，今天想跟您确认下%s是否方便。" % task_desc[:30],
        "invitation": "您方便的话，我直接帮您安排到店时间。",
        "closing": "收到，那我按您方便的时间安排。",
    }
    templates = [base, second, third]
    if count <= 3:
        return templates[:count]
    return templates + [templates[i % 3] for i in range(3, count)]


def generate_touch_suggestion(
    company: str,
    storecode: str,
    task: CrmCase,
    *,
    channel: str = "",
    outcome: str = "",
    agent_id: str = "deepseek",
    variants: int = 3,
    current_ecode: str = "",
    current_ename: str = "",
) -> Dict[str, Any]:
    """生成多套结构化话术；LLM 不可用时返回静态兜底。"""
    context = build_touch_context(
        company,
        storecode,
        task,
        channel=channel,
        outcome=outcome,
        current_ecode=current_ecode,
        current_ename=current_ename,
    )
    variants = max(1, min(int(variants or 3), 5))
    fallback_items = _static_variants(context, channel, variants)
    try:
        from assistant.agents import chat_completion

        raw, model = chat_completion(
            agent_id,
            build_suggest_messages(context, variants),
            temperature=0.7,
            json_mode=True,
            timeout=30,
        )
        data = json.loads(raw or "{}")
        items = data.get("items") if isinstance(data, dict) else None
        if not isinstance(items, list) or not items:
            raise ValueError("话术输出缺少 items 数组")
        result_items = []
        for i in range(variants):
            item = items[i] if i < len(items) and isinstance(items[i], dict) else {}
            fb = fallback_items[i] if i < len(fallback_items) else fallback_items[0]
            result_items.append({
                "source": "llm",
                "model": model,
                "opening": str(item.get("opening") or fb["opening"]),
                "care_points": item.get("care_points") if isinstance(item.get("care_points"), list) else fb["care_points"],
                "invitation": str(item.get("invitation") or fb["invitation"]),
                "closing": str(item.get("closing") or fb["closing"]),
                "avoid": item.get("avoid") if isinstance(item.get("avoid"), list) else fb["avoid"],
            })
        return {"source": "llm", "model": model, "count": len(result_items), "variants": result_items}
    except Exception as exc:  # noqa: BLE001
        return {
            "source": "fallback",
            "model": "",
            "count": len(fallback_items),
            "variants": fallback_items,
            "error": str(exc)[:200],
        }
