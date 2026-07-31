# coding=utf-8
"""
Django Admin 公司/门店上下文：基于 auth.User + GenesisUserProfile，替代 companylist[username] 硬编码。
"""
from __future__ import unicode_literals

from datetime import datetime

import common.constants

# 原 baseinfo/admin.py 中的公司分组（字段布局用）
COMPANYGROUP1 = ['yiren', 'demo']
COMPANYGROUP2 = ['yfy', 'xuedan', 'dsdemo']


def get_admin_username(request):
    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        return user.username
    return 'anonymous'


def get_admin_company(request, allow_all_for_superuser=False):
    """
    当前 Admin 登录用户所属公司。
    - 有 Profile：用 profile.company
    - 超级用户且无 Profile：allow_all 时返回 None（列表不过滤 company）
    - 否则：common.constants.COMPANYID
    """
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'is_authenticated', False):
        return common.constants.COMPANYID

    profile = None
    try:
        profile = user.genesis_profile
    except Exception:
        profile = None

    if profile and (profile.company or '').strip():
        return profile.company.strip()

    if user.is_superuser and allow_all_for_superuser:
        return None

    return common.constants.COMPANYID


def get_admin_storecodes(request):
    user = getattr(request, 'user', None)
    if not user or not getattr(user, 'is_authenticated', False):
        return []
    try:
        return user.genesis_profile.allowed_storecodes()
    except Exception:
        return []


def filter_queryset_by_admin_company(qs, request, company_field='company', flag_field='flag'):
    """Genesis 业务表常用：flag=Y + 当前用户公司。"""
    if flag_field and hasattr(qs.model, flag_field):
        qs = qs.filter(**{flag_field: 'Y'})
    company = get_admin_company(request, allow_all_for_superuser=True)
    if company and company_field and hasattr(qs.model, company_field):
        qs = qs.filter(**{company_field: company})
    return qs


class GenesisCompanyAdminMixin(object):
    """ModelAdmin：按 Profile 公司过滤；保存时写入 company / creater。"""

    def get_queryset(self, request):
        qs = super(GenesisCompanyAdminMixin, self).get_queryset(request)
        return filter_queryset_by_admin_company(qs, request)

    def save_model(self, request, obj, form, change):
        company = get_admin_company(request)
        username = get_admin_username(request)
        if hasattr(obj, 'company') and company:
            obj.company = company
        if hasattr(obj, 'creater'):
            obj.creater = username
        if hasattr(obj, 'last_modified'):
            obj.last_modified = datetime.now()
        super(GenesisCompanyAdminMixin, self).save_model(request, obj, form, change)


class GenesisCompanyInlineMixin(object):
    def get_queryset(self, request):
        qs = super(GenesisCompanyInlineMixin, self).get_queryset(request)
        return filter_queryset_by_admin_company(qs, request)
