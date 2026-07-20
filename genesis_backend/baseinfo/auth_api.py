# coding=utf-8
"""Genesis 登录 / 门店 / 权限 — DRF 与 JSON 接口（Django User + Profile）。"""
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

import common.constants
from common.genesis_auth import (
    authenticate_genesis_user,
    serialize_genesis_session,
    validate_genesis_store_access,
)


def _login_params(request):
    g = request.GET
    return {
        'company': g.get('company', common.constants.COMPANYID),
        'storecode': g.get('storecode', ''),
        'usercode': g.get('usercode', g.get('ecode', '')),
        'password': g.get('password', ''),
    }


@csrf_exempt
def hdsysuser_login_json(request):
    """
    GET/POST：company, usercode, password, storecode(可选)
    返回完整登录上下文（含 stores、permissions）。
    """
    if request.method not in ('GET', 'POST'):
        return JsonResponse({'code': 405, 'msg': 'method not allowed'}, status=405)
    p = _login_params(request)
    auth = authenticate_genesis_user(
        p['company'], p['usercode'], p['password'], p['storecode'] or None
    )
    if not auth:
        return JsonResponse({'code': 500, 'msg': '用户名/密码错误或无权登录该门店'}, status=401)
    return JsonResponse(serialize_genesis_session(auth))


@csrf_exempt
def hdsysuser_stores(request):
    """已认证用户可登录的门店列表。"""
    p = _login_params(request)
    auth = authenticate_genesis_user(
        p['company'], p['usercode'], p['password'], None
    )
    if not auth:
        return JsonResponse({'code': 500, 'stores': []}, status=401)
    sess = serialize_genesis_session(auth, include_permissions=False)
    return JsonResponse(
        {
            'code': 200,
            'company': sess['company'],
            'sys_userid': sess['sys_userid'],
            'auth_type': sess['auth_type'],
            'stores': auth['stores'],
            'allowed_storecodes': auth['allowed_storecodes'],
        }
    )


@csrf_exempt
def hdsysuser_permissions(request):
    """指定门店下的模块权限。"""
    company = request.GET.get('company', common.constants.COMPANYID)
    storecode = request.GET.get('storecode', '')
    usercode = request.GET.get('usercode', request.GET.get('ecode', ''))
    password = request.GET.get('password', '')
    user_uuid = request.GET.get('user_uuid', '')
    django_user_id = request.GET.get('django_user_id', '')

    subject = validate_genesis_store_access(
        company=company,
        storecode=storecode,
        usercode=usercode,
        password=password or None,
        user_uuid=user_uuid or None,
        django_user_id=int(django_user_id) if str(django_user_id).isdigit() else None,
    )
    if not subject:
        return JsonResponse({'code': 500, 'permissions': []}, status=403)

    if hasattr(subject, 'module_rights'):
        rights_qs = subject.module_rights(storecode)
        sys_userid = getattr(subject, 'employee_code', None) or getattr(
            subject, 'sys_userid', ''
        )
        if hasattr(subject, 'user'):
            sys_userid = subject.employee_code or subject.user.username
    else:
        rights_qs = subject.module_rights(storecode)
        sys_userid = subject.sys_userid

    perms = [
        {
            'module': r.sys_module,
            'read': (r.sys_readrights or 'N').upper(),
            'write': (r.sys_writerights or 'N').upper(),
        }
        for r in rights_qs
    ]
    return JsonResponse(
        {
            'code': 200,
            'company': company,
            'storecode': storecode,
            'sys_userid': sys_userid,
            'permissions': perms,
        }
    )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])

@csrf_exempt
def hdsysuser_search_json(request):
    """搜索 Hdsysuser：按工号或姓名模糊匹配，限定同一公司"""
    if request.method != 'GET':
        return JsonResponse({'code': 405, 'msg': 'method not allowed'}, status=405)
    company = request.GET.get('company', '').strip()
    keyword = request.GET.get('keyword', '').strip()
    if not company or not keyword:
        return JsonResponse([])
    try:
        from django.db.models import Q
        from baseinfo.models import Hdsysuser
        qs = Hdsysuser.objects.filter(
            company=company,
            sys_userstatus=1,
        ).filter(
            Q(sys_userid__icontains=keyword) |
            Q(sys_fullname__icontains=keyword)
        ).order_by('sys_userid')[:30]
        data = []
        for u in qs:
            sl = u.parse_storelist_codes() if hasattr(u, 'parse_storelist_codes') else []
            data.append({
                'uuid': str(u.uuid),
                'sys_userid': u.sys_userid or '',
                'sys_fullname': u.sys_fullname or '',
                'storelist': ', '.join(sl) if sl else '',
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)})

def api_v1_hdsysuser_login(request):
    """DRF 版登录（/baseinfo/api/v1/auth/login/）。"""
    data = request.data if request.method == 'POST' and isinstance(request.data, dict) else {}
    company = data.get('company') or request.query_params.get('company', common.constants.COMPANYID)
    storecode = data.get('storecode') or request.query_params.get('storecode', '')
    usercode = (
        data.get('usercode')
        or data.get('ecode')
        or request.query_params.get('usercode')
        or request.query_params.get('ecode', '')
    )
    password = data.get('password') or request.query_params.get('password', '')
    auth = authenticate_genesis_user(company, usercode, password, storecode or None)
    if not auth:
        return Response(
            {'code': 401, 'msg': '用户名/密码错误或无权登录该门店'},
            status=401,
        )
    return Response(serialize_genesis_session(auth))
