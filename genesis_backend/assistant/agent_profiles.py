#coding = utf-8
"""Genesis 业务智能体配置（领域助手，与 LLM 提供方 agents.py 分离）。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from assistant.data_tools import (
    TOOL_CATALOG_TEXT,
    TOOL_REGISTRY,
    answer_system_prompt,
    planner_system_prompt,
)
from assistant.vip_tools import VIP_ONLY_CATALOG_TEXT, VIP_ONLY_REGISTRY

ToolFn = Callable[..., Any]


@dataclass(frozen=True)
class AgentProfile:
    id: str
    label: str
    description: str
    tool_registry: Dict[str, ToolFn]
    tool_catalog_text: str
    planner_extra: str
    answer_extra: str


_VIP_SHARED_TOOL_NAMES = (
    "search_vips",
    "list_vip_cards",
    "search_cards",
    "list_store_vips",
    "list_employees",
    "vip_maintenance_summary",
    "describe_table",
    "readonly_sql",
)


VIP_CRM_LIFECYCLE_CATALOG = """
- vip_lifecycle_batch：门店客户生命周期分级（active 活跃 / at_risk 流失预警 / sleeping 休眠）。预警=近一周期消费或到店频次下降；休眠=公司统一 inactive_days 无有效消费。args: {} 或 {"segment":"at_risk|sleeping|active"}、{"viptype":"10"}、{"ecode":"顾问"}、{"limit":80}。含 recommended_actions 运营建议。
- vip_lifecycle_one：单客生命周期分级 + 建议方案。args: {"telph":"..."} 或 {"vipuuid":"..."} / {"vcode":"..."}。
- vip_lifecycle_create_crm_tasks：为 at_risk/sleeping 客户生成 CRM 回访任务（VipCaseDetail）。默认 dry_run 预览。args: {"segment":"at_risk|sleeping"}、{"ecode":"顾问"}、{"limit":50}、{"dry_run":false} 写库。
""".strip()


def _build_vip_tool_registry() -> Dict[str, ToolFn]:
    from assistant.vip_lifecycle import tool_vip_lifecycle_batch, tool_vip_lifecycle_one
    from assistant.vip_lifecycle_crm import tool_vip_lifecycle_create_crm_tasks

    reg: Dict[str, ToolFn] = {}
    for name in _VIP_SHARED_TOOL_NAMES:
        fn = TOOL_REGISTRY.get(name)
        if fn:
            reg[name] = fn
    reg.update(VIP_ONLY_REGISTRY)
    reg["vip_lifecycle_batch"] = tool_vip_lifecycle_batch
    reg["vip_lifecycle_one"] = tool_vip_lifecycle_one
    reg["vip_lifecycle_create_crm_tasks"] = tool_vip_lifecycle_create_crm_tasks
    return reg


def _vip_shared_catalog_lines() -> str:
    lines: List[str] = []
    for line in TOOL_CATALOG_TEXT.splitlines():
        t = line.strip()
        if not t.startswith("- "):
            continue
        for name in _VIP_SHARED_TOOL_NAMES:
            if t.startswith(f"- {name}：") or t.startswith(f"- {name}:"):
                lines.append(t)
                break
    return "\n".join(lines)


VIP_CRM_TOOL_CATALOG = (
    "可用工具（name 必须与下列完全一致）：\n"
    + _vip_shared_catalog_lines()
    + "\n"
    + VIP_ONLY_CATALOG_TEXT
    + "\n"
    + VIP_CRM_LIFECYCLE_CATALOG
).strip()

VIP_CRM_PLANNER_EXTRA = """
你是 Genesis 美业系统的「客户管理」专用规划模块，聚焦会员（vip 表）与 CRM。
【规划阶段】只输出 JSON 工具计划，禁止直接回答用户、禁止输出会员排名表格或消费金额。

客户 = 会员/散客。业务口语中的「vipuuid」是会员 UUID 值，不是 vip 表的列名：
- vip 表主键列：uuid（SELECT v.uuid，不要写 v.vipuuid）
- expvstoll / cardinfo 等表的外键列：vipuuid（指向 vip.uuid）

工作流程建议：
1. 用户提到姓名/手机/会员号时，先用 search_vips 定位 vipuuid，再查详情或消费。
2. 用户问「这个客户怎么样/画像/分析」或给出手机号想了解概况时，优先 vip_profile；需要流失/风险判断时加 vip_churn_risk（可只传 telph）。
3. 需要完整档案时用 get_vip_detail；需要消费历史用 list_vip_transactions 或 vip_consumption_summary。
4. 回访/案例相关用 list_vip_crm_cases、list_vip_communications。
5. 门店会员维护概览用 vip_maintenance_summary；客户生命周期分级/预警/休眠/运营方案用 vip_lifecycle_batch 或 vip_lifecycle_one（含 segment、recommended_actions、playbook_goals）；旧口径批量沉睡仍可用 vip_sleeping_alert。
6. 用户问「这个客户怎么办/给方案/如何维护」时，优先 vip_lifecycle_one（可配合 vip_profile）；批量问「预警/休眠客户」用 vip_lifecycle_batch。
7. 用户要导出查询结果时，说明每条助手回复下方有「导出结果」按钮（Excel/JSON/CSV/Markdown）；页顶维度统计、沉睡预警、生命周期面板查询后也可导出。
8. 查卡用 list_vip_cards / search_cards。
9. 会员消费排行（勿用 readonly_sql）：
   - 现金 → vip_top_cash_consumption
   - 卡付/刷卡 → vip_top_card_consumption
   - 赠送/赠金 → vip_top_send_consumption
   - 服务类（ttype=S，现金+卡付，不含赠送）→ vip_top_service_consumption
   - 商品类（ttype=G，现金+卡付，不含赠送）→ vip_top_goods_consumption
   可同时并列多个排行工具；args 含 days、top_n、date_field 等。
9. 解析员工编号 ecode 时可调用 list_employees。
10. 当用户需要「分析会员卡项余额/卡项分类」时（勿用 readonly_sql 替代）：
    - 用 list_vip_cards / search_cards 查 cardinfo + cardtype（参数 vipuuid）
    - 按 comptype 分金额计费卡（amount）和计次卡（times）
    - 有效卡 = leftmoney>0 或 leftqty>0
    - 金额计费卡按 suptype 或品牌分组；计次卡按 brand 或 displayclass1 分组
    - 品牌/displayclass1 代码从 appoption 字典翻译（see 系统字典 appoption 说明）
    - 标注赠送卡（stype=P）和已关闭卡（status=C），提醒余额>0已关闭的卡


规则：
- 本助手只读查询，不创建/修改会员或案例。
- 所有查询限定当前 company + storecode。
- 不要用 uuid 瞎猜；必须先 search_vips 或用户提供明确 vipuuid/vcode。
""".strip()

VIP_CRM_ANSWER_EXTRA = """
你是 Genesis 美业系统的「客户管理」业务助手，专门回答会员档案、消费、卡项、CRM 案例与回访相关问题。
- 用表格或分点呈现会员信息，保护隐私：手机号可部分脱敏展示（如 138****1234）除非用户明确要求完整号码。
- 结合 viptype（10=会员/20=散客）、status、viplevel 解释客户状态。
- 说明消费数据时注明统计区间与 date_field（vsdate/cdate）。
- 会员消费排行结果含 indate（入会日期）、last_visit_date（最后一次有效到店日期）、ecode/adviser_name、ecode2/therapist_name、birth、viplevel 及各类消费金额字段。
- 若会员有沉睡/流失风险或需要运营方案，优先 vip_lifecycle_batch / vip_lifecycle_one（含 segment、risk_factors、playbook_goals、recommended_actions）；说明预警口径为「趋势下降=at_risk；>=inactive_days 无有效消费=sleeping」。
- 当工具返回 recommended_actions 时，回答必须按以下结构组织（禁止编造 tool 中不存在的金额/日期/姓名）：
  1. **客户现状**：segment 中文含义、末次到店/天数、消费与到店趋势
  2. **风险原因**：逐条引用 risk_factors（若无则写「暂无额外风险因素」）
  3. **运营目标**：引用 playbook_goals
  4. **建议动作**：按 recommended_actions 的 priority 排序，每条含 title、detail；若有 suggested_script 则作为「参考话术」单独一行
  5. **下一步**：明确顾问应在几天内完成的首个动作
- 客户画像类问题用 vip_profile 结果组织自然语言：概括身份、累计消费、到店习惯、常做项目、末次到店。
- 每条有查询数据的助手回复下方提供导出（Excel/JSON/CSV/Markdown）；页顶「管理维度营业」「沉睡会员预警」查询后也可导出。
""".strip()


PROFILE_GENERAL = AgentProfile(
    id="general",
    label="通用业务助手",
    description="门店营业、交易、挂单、报表等综合查询",
    tool_registry=TOOL_REGISTRY,
    tool_catalog_text=TOOL_CATALOG_TEXT,
    planner_extra="",
    answer_extra="",
)

PROFILE_VIP_CRM = AgentProfile(
    id="vip_crm",
    label="客户管理助手",
    description="会员档案、消费记录、卡项、CRM 案例与回访沟通",
    tool_registry=_build_vip_tool_registry(),
    tool_catalog_text=VIP_CRM_TOOL_CATALOG,
    planner_extra=VIP_CRM_PLANNER_EXTRA,
    answer_extra=VIP_CRM_ANSWER_EXTRA,
)

_PROFILES: Dict[str, AgentProfile] = {
    PROFILE_GENERAL.id: PROFILE_GENERAL,
    PROFILE_VIP_CRM.id: PROFILE_VIP_CRM,
}


def get_agent_profile(profile_id: str) -> AgentProfile:
    pid = (profile_id or PROFILE_GENERAL.id).strip().lower()
    return _PROFILES.get(pid, PROFILE_GENERAL)


def list_agent_profiles() -> List[Dict[str, str]]:
    return [
        {"id": p.id, "label": p.label, "description": p.description}
        for p in _PROFILES.values()
    ]


def planner_system_prompt_for_profile(profile_id: str) -> str:
    profile = get_agent_profile(profile_id)
    base = planner_system_prompt()
    if profile.id == PROFILE_GENERAL.id:
        return base
    # 替换工具目录为 profile 子集
    base_lines = base.split("\n", 1)
    header = base_lines[0]
    rest = base_lines[1] if len(base_lines) > 1 else ""
    rules_idx = rest.find("\n规则：")
    rules = rest[rules_idx:] if rules_idx >= 0 else ""
    out = f"{header}\n{profile.tool_catalog_text}{rules}"
    if profile.planner_extra:
        out = out + "\n\n" + profile.planner_extra
    return out


def answer_system_prompt_for_profile(profile_id: str) -> str:
    profile = get_agent_profile(profile_id)
    base = answer_system_prompt()
    if profile.answer_extra:
        return base + "\n\n" + profile.answer_extra
    return base
