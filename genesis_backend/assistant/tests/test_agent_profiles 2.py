# coding=utf-8

from assistant.agent_profiles import PROFILE_VIP_CRM, get_agent_profile
from assistant.vip_tools import VIP_ONLY_REGISTRY


def test_vip_crm_registry_includes_profile_tools():
    profile = get_agent_profile("vip_crm")
    assert "vip_profile" in profile.tool_registry
    assert "vip_churn_risk" in profile.tool_registry
    assert profile.tool_registry["vip_profile"] is VIP_ONLY_REGISTRY["vip_profile"]


def test_vip_crm_planner_prompt_mentions_profile_tools():
    profile = get_agent_profile("vip_crm")
    text = profile.planner_extra + profile.tool_catalog_text
    assert "vip_profile" in text
    assert "vip_churn_risk" in text


def test_general_profile_is_distinct():
    general = get_agent_profile("general")
    vip = get_agent_profile("vip_crm")
    assert general.id == "general"
    assert vip.id == PROFILE_VIP_CRM.id
