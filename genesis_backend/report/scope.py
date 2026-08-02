# coding=utf-8
"""报表门店范围：解析请求参数并与用户可管门店取交集。"""
from django.contrib.auth.models import User


def parse_storecodes_param(raw):
    """把逗号分隔的 storecodes 解析为去重有序列表。"""
    if raw is None:
        return []
    codes = []
    seen = set()
    for part in str(raw).split(','):
        code = part.strip()
        if not code or code in seen:
            continue
        seen.add(code)
        codes.append(code)
    return codes


def intersect_storecodes(requested, allowed):
    """
    requested 为空 → 使用全部 allowed；
    否则取交集（保持 requested 顺序）。
    """
    allowed_list = [str(c).strip() for c in (allowed or []) if str(c).strip()]
    allowed_set = set(allowed_list)
    requested_list = [str(c).strip() for c in (requested or []) if str(c).strip()]
    if not requested_list:
        return list(allowed_list)
    return [c for c in requested_list if c in allowed_set]


def django_user_id_from_request(request):
    """从 query / Authorization(JWT django_{id}) / 头读取 django_user_id。"""
    raw = (request.GET.get('django_user_id') or '').strip()
    if not raw and request.method == 'POST':
        raw = str(request.POST.get('django_user_id') or '').strip()
    if raw.isdigit():
        return int(raw)

    auth = (request.META.get('HTTP_AUTHORIZATION') or '').strip()
    # JWT django_123 或 Bearer django_123
    token = auth
    for prefix in ('JWT ', 'Bearer ', 'jwt ', 'bearer '):
        if token.startswith(prefix):
            token = token[len(prefix):].strip()
            break
    if token.startswith('django_'):
        tail = token[len('django_'):]
        if tail.isdigit():
            return int(tail)
    return None


def resolve_report_store_scope(request, company):
    """
    解析报表门店范围。

    Returns:
        (ok, payload)
        ok=True 时 payload = {
            'storecodes': [...],
            'allowed_storecodes': [...],
            'profile': profile or None,
            'django_user_id': int or None,
        }
        ok=False 时 payload = JsonResponse 可用的 dict + 建议 status
    """
    from common.genesis_auth import profile_allowed_storecodes
    from common.models import GenesisUserProfile

    company = (company or '').strip()
    if not company:
        return False, {'ok': False, 'error': '缺少 company', 'status': 400}

    requested = parse_storecodes_param(request.GET.get('storecodes', ''))
    legacy = (request.GET.get('storecode') or '').strip()
    if legacy and legacy not in requested:
        requested.append(legacy)

    django_user_id = django_user_id_from_request(request)
    profile = None
    allowed = []

    if django_user_id is not None:
        try:
            user = User.objects.select_related('genesis_profile').get(
                pk=django_user_id, is_active=True
            )
            profile = user.genesis_profile
        except (User.DoesNotExist, GenesisUserProfile.DoesNotExist):
            return False, {
                'ok': False,
                'error': '用户不存在或未绑定档案',
                'status': 401,
            }
        if (profile.company or '').strip() != company:
            return False, {
                'ok': False,
                'error': '公司与用户档案不一致',
                'status': 403,
            }
        allowed = list(profile_allowed_storecodes(profile))
    else:
        # 无用户身份时：仅允许显式 storecodes（兼容旧调用），不能隐式全公司
        if not requested:
            return False, {
                'ok': False,
                'error': '缺少 django_user_id 或 storecodes',
                'status': 400,
            }
        allowed = list(requested)

    storecodes = intersect_storecodes(requested, allowed)
    if not storecodes:
        return False, {
            'ok': False,
            'error': '无权查看所选门店或无可管门店',
            'status': 403,
            'allowed_storecodes': allowed,
        }

    return True, {
        'storecodes': storecodes,
        'allowed_storecodes': allowed,
        'profile': profile,
        'django_user_id': django_user_id,
    }
