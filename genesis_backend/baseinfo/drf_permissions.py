# coding=utf-8
"""DRF 权限：基于 GenesisUserProfile 的公司 + 门店上下文。"""
from rest_framework.permissions import BasePermission

from common.genesis_auth import validate_genesis_store_access


def _param(request, *keys):
    for k in keys:
        v = request.query_params.get(k) if hasattr(request, 'query_params') else None
        if v is None and hasattr(request, 'GET'):
            v = request.GET.get(k)
        if v is None and hasattr(request, 'data') and isinstance(request.data, dict):
            v = request.data.get(k)
        if v is not None and str(v).strip() != '':
            return str(v).strip()
    return ''


class HdsysuserStorePermission(BasePermission):
    """
    要求请求带 company + storecode，以及 ecode（工号）、django_user_id 或密码。
    校验 Profile 是否允许在该门店操作（useright 经关联 hdsysuser 读取）。
    """

    message = '无权访问该门店或用户无效'

    def has_permission(self, request, view):
        company = _param(request, 'company')
        storecode = _param(request, 'storecode')
        usercode = _param(request, 'ecode', 'usercode', 'sys_userid')
        user_uuid = _param(request, 'user_uuid', 'hdsysuser_uuid')
        if not company or not storecode:
            return True
        if not usercode and not user_uuid and not _param(request, 'django_user_id'):
            return True
        password = _param(request, 'password')
        did = _param(request, 'django_user_id')
        subject = validate_genesis_store_access(
            company=company,
            usercode=usercode,
            storecode=storecode,
            password=password or None,
            user_uuid=user_uuid or None,
            django_user_id=int(did) if did.isdigit() else None,
        )
        if subject:
            request.genesis_subject = subject
            if hasattr(subject, 'user'):
                request.genesis_profile = subject
                request.genesis_hdsysuser = None
            else:
                request.genesis_hdsysuser = subject
                request.genesis_profile = None
            request.genesis_storecode = storecode
            request.genesis_company = company
            return True
        return False


class HdsysuserModuleWritePermission(HdsysuserStorePermission):
    """在门店权限基础上，要求对 sys_module 有写权限。"""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        module = getattr(view, 'genesis_module', None) or _param(request, 'sys_module')
        if not module:
            return True
        profile = getattr(request, 'genesis_profile', None)
        hu = getattr(request, 'genesis_hdsysuser', None)
        if profile and (profile.is_company_admin or profile.user.is_superuser):
            return True
        if hu and hu.is_sys_admin():
            return True
        subject = profile or hu
        if not subject:
            return True
        sc = getattr(request, 'genesis_storecode', _param(request, 'storecode'))
        rights = subject.module_rights(sc).filter(sys_module=module).first()
        if not rights:
            return False
        return (rights.sys_writerights or '').upper() == 'Y'
