# coding=utf-8
"""
Genesis 权限：以 Django auth.User 为主，OneToOne Profile 承载公司/门店；
兼容 legacy hdsysuser + useright。
"""
from __future__ import unicode_literals

from django.contrib.auth.models import User

from baseinfo.models import Hdsysuser, Storeinfo, Useright
import common.constants
from common.admin_utils import get_admin_company


def _stores_for_codes(company, codes):
    if not codes:
        return []
    qs = Storeinfo.objects.filter(
        company=company, flag='Y', storecode__in=codes
    ).order_by('storecode')
    return [
        {
            'storecode': s.storecode,
            'storename': (s.storename or s.storecode or '').strip(),
        }
        for s in qs
    ]


def _parse_storelist(raw, default_storecode=''):
    codes = []
    if raw:
        if isinstance(raw, (list, tuple)):
            for c in raw:
                p = str(c).strip()
                if p:
                    codes.append(p)
        else:
            for part in str(raw).replace('，', ',').split(','):
                p = part.strip()
                if p:
                    codes.append(p)
    home = (default_storecode or '').strip()
    if home and home not in codes:
        codes.insert(0, home)
    return codes


def profile_allowed_storecodes(profile):
    if profile.is_company_admin or profile.user.is_superuser:
        return list(
            Storeinfo.objects.filter(company=profile.company, flag='Y')
            .order_by('storecode')
            .values_list('storecode', flat=True)
        )
    return _parse_storelist(profile.storelist, profile.default_storecode)


def profile_can_access_store(profile, storecode):
    sc = (storecode or '').strip()
    if not sc:
        return False
    if profile.user.is_superuser:
        return True
    if profile.is_company_admin:
        return Storeinfo.objects.filter(
            company=profile.company, flag='Y', storecode=sc
        ).exists()
    return sc in profile_allowed_storecodes(profile)


def profile_linked_hdsysuser(profile):
    if profile.hdsysuser_uuid:
        hu = Hdsysuser.objects.filter(uuid=profile.hdsysuser_uuid, flag='Y').first()
        if hu:
            return hu
    ecode = (profile.employee_code or profile.user.username or '').strip()
    if ecode:
        return (
            Hdsysuser.objects.filter(
                company=profile.company, sys_userid=ecode, flag='Y'
            )
            .order_by('-last_modified')
            .first()
        )
    return None


def profile_module_rights(profile, storecode=None):
    sc = (storecode or profile.default_storecode or '').strip()
    hu = profile_linked_hdsysuser(profile)
    if hu:
        return hu.module_rights(sc)
    key = profile.rights_user_key()
    if not key or not sc:
        return Useright.objects.none()
    return Useright.objects.filter(
        company=profile.company,
        storecode=sc,
        sys_userid=key,
        flag='Y',
    ).order_by('sys_module')


def authenticate_django_user(company, usercode, password, storecode=None):
    """Django User + GenesisUserProfile 登录。"""
    from common.models import GenesisUserProfile

    company = (company or '').strip()
    usercode = (usercode or '').strip()
    if not company or not usercode:
        return None

    user = User.objects.filter(username=usercode, is_active=True).first()
    if not user or not user.check_password(password):
        return None

    try:
        profile = user.genesis_profile
    except GenesisUserProfile.DoesNotExist:
        if user.is_superuser:
            profile = GenesisUserProfile.objects.create(
                user=user,
                company=company,
                is_company_admin=True,
            )
        else:
            return None

    if profile.company != company and not user.is_superuser:
        return None

    allowed = profile_allowed_storecodes(profile)
    if not allowed and not user.is_superuser:
        return None

    sc = (storecode or '').strip()
    if sc:
        if not profile_can_access_store(profile, sc):
            return None
        current_store = sc
    else:
        current_store = (profile.default_storecode or '').strip() or (
            allowed[0] if allowed else ''
        )

    return {
        'auth_type': 'django',
        'django_user': user,
        'profile': profile,
        'hdsysuser': profile_linked_hdsysuser(profile),
        'storecode': current_store,
        'allowed_storecodes': allowed,
        'stores': _stores_for_codes(profile.company, allowed),
    }


def authenticate_genesis_user(company, usercode, password, storecode=None):
    """仅 Django User + GenesisUserProfile；不再使用 hdsysuser 密码表。"""
    return authenticate_django_user(company, usercode, password, storecode)


def serialize_genesis_session(auth_ctx, include_permissions=True):
    """序列化 Django User + Profile 登录结果（auth_type 恒为 django）。"""
    storecode = auth_ctx['storecode']
    user = auth_ctx['django_user']
    profile = auth_ctx['profile']
    hu = auth_ctx.get('hdsysuser')
    payload = {
        'code': 200,
        'auth_type': 'django',
        'company': profile.company,
        'storecode': storecode,
        'allowed_storecodes': auth_ctx['allowed_storecodes'],
        'stores': auth_ctx['stores'],
        'django_user_id': user.id,
        'username': user.username,
        'uuid': str(hu.uuid) if hu else '',
        'sys_userid': profile.employee_code or user.username,
        'sys_fullname': (
            profile.display_name or user.get_full_name() or user.username
        ),
        'sys_adm': 'Y' if profile.is_company_admin else 'N',
        'costpriceflag': profile.costpriceflag or 'N',
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
    }
    rights_qs = profile_module_rights(profile, storecode)
    if include_permissions:
        payload['permissions'] = [
            {
                'module': r.sys_module,
                'read': (r.sys_readrights or 'N').upper(),
                'write': (r.sys_writerights or 'N').upper(),
                'modulegrp': r.sys_modulegrp or '',
            }
            for r in rights_qs
        ]
    return payload


def validate_genesis_store_access(
    company, storecode, usercode=None, password=None, user_uuid=None, django_user_id=None
):
    """DRF / 接口：仅 Django User Profile 校验门店权限（useright 仍经 hdsysuser 关联读）。"""
    from common.models import GenesisUserProfile

    company = (company or '').strip()
    storecode = (storecode or '').strip()
    if not company or not storecode:
        return None

    if django_user_id:
        try:
            profile = User.objects.get(pk=int(django_user_id), is_active=True).genesis_profile
            if profile_can_access_store(profile, storecode):
                return profile
        except (User.DoesNotExist, GenesisUserProfile.DoesNotExist, ValueError, TypeError):
            pass

    usercode = (usercode or '').strip()
    if usercode and password:
        ctx = authenticate_django_user(company, usercode, password, storecode)
        if ctx:
            return ctx['profile']
        return None

    if usercode:
        try:
            profile = GenesisUserProfile.objects.select_related('user').get(
                user__username=usercode, company=company, user__is_active=True
            )
            if profile_can_access_store(profile, storecode):
                return profile
        except GenesisUserProfile.DoesNotExist:
            pass

    return None


def genesis_company_for_request(request):
    """Admin / 请求上下文：Profile.company。"""
    return get_admin_company(request, allow_all_for_superuser=False)
