# coding=utf-8
"""
Hdsysuser 公司 / 多门店权限：认证、合并同账号多行、序列化登录上下文。
与 useright（模块读写权限）及 storelist（可用门店）配合使用。
"""
from __future__ import unicode_literals

from baseinfo.models import Hdsysuser, Storeinfo


def find_hdsysusers(company, usercode, password):
    """已废弃用于登录；仅 sync_genesis_profiles_from_hdsysuser 等迁移脚本可能读取。"""
    return list(
        Hdsysuser.objects.filter(
            company=company,
            sys_userid=usercode,
            sys_passwd=password,
            flag='Y',
        ).order_by('-last_modified')
    )


def merged_allowed_storecodes(users):
    codes = set()
    for u in users:
        codes.update(u.allowed_storecodes())
    return sorted(codes)


def pick_user_for_store(users, storecode):
    """优先返回能访问该门店的那条 hdsysuser 记录。"""
    sc = (storecode or '').strip()
    for u in users:
        if u.can_access_store(sc):
            return u
    return None


def authenticate_hdsysuser(company, usercode, password, storecode=None):
    """
    已废弃：登录仅使用 Django User（见 common.genesis_auth.authenticate_genesis_user）。
    保留函数签名以免旧代码 import 报错；始终返回 None。
    """
    return None


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


def serialize_hdsysuser_session(auth_ctx, include_permissions=True):
    """登录成功后的 JSON 结构（小程序 / DRF 共用）。"""
    user = auth_ctx['user']
    storecode = auth_ctx['storecode']
    payload = {
        'code': 200,
        'uuid': str(user.uuid),
        'sys_userid': user.sys_userid,
        'sys_fullname': user.sys_fullname or '',
        'company': user.company,
        'storecode': storecode,
        'sys_adm': user.sys_adm or '',
        'costpriceflag': user.costpriceflag or 'N',
        'allowed_storecodes': auth_ctx['allowed_storecodes'],
        'stores': auth_ctx['stores'],
    }
    if include_permissions:
        payload['permissions'] = [
            {
                'module': r.sys_module,
                'read': (r.sys_readrights or 'N').upper(),
                'write': (r.sys_writerights or 'N').upper(),
                'modulegrp': r.sys_modulegrp or '',
            }
            for r in user.module_rights(storecode)
        ]
    return payload


def validate_store_access(company, usercode, storecode, password=None, user_uuid=None):
    """已废弃：请用 common.genesis_auth.validate_genesis_store_access（返回 Profile）。"""
    from common.genesis_auth import validate_genesis_store_access

    return validate_genesis_store_access(
        company=company,
        usercode=usercode,
        storecode=storecode,
        password=password,
        user_uuid=user_uuid,
    )
