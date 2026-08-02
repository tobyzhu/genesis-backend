#coding:utf-8
import json
from collections import OrderedDict
from django.apps import apps
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator

from .registry import get_registry


def model_list(request):
    """GET /sysadmin/models/ — 返回分组后的模型列表"""
    groups = get_registry()
    result = []
    group_order = ['基础配置', '核心业务', '营销']
    for g in group_order:
        models = groups.get(g, [])
        if not models:
            continue
        result.append({
            'name': g,
            'models': [{
                'id': f"{m['app_label']}.{m['model_name']}",
                'verbose_name': m['verbose_name'],
                'icon': m['icon'],
            } for m in models],
        })
    return JsonResponse({'groups': result})


def _get_display_field(model):
    """获取模型的显示字段（用于 FK 下拉）"""
    for field_name in ['name', 'title', 'ename', 'pname', 'cardname', 'storename', 'itemname', 'ttname']:
        if hasattr(model, field_name):
            f = model._meta.get_field(field_name)
            if f and f.get_internal_type() in ('CharField', 'TextField'):
                return field_name
    return 'pk'


def _get_verbose(model):
    return str(model._meta.verbose_name) if model._meta.verbose_name else ''


def _coerce_fk_values(model, data):
    """把通用 CRUD 提交的外键主键字符串解析为模型实例。"""
    for name in list(data.keys()):
        value = data.get(name)
        if value in (None, ''):
            continue
        try:
            field = model._meta.get_field(name)
        except Exception:
            continue
        if not field.is_relation or not field.related_model:
            continue
        if isinstance(value, field.related_model):
            continue
        try:
            data[name] = field.related_model.objects.get(pk=value)
        except Exception:
            continue


def model_meta(request, app_label, model_name):
    """GET /sysadmin/models/{app}.{model}/meta/ — 字段元数据"""
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({'error': f'Model {app_label}.{model_name} not found'}, status=404)

    fields = []
    for field in model._meta.fields:
        internal_type = field.get_internal_type()
        entry = OrderedDict()
        entry['name'] = field.name
        entry['verbose_name'] = str(field.verbose_name or field.name)
        entry['type'] = internal_type
        entry['required'] = not field.null and not field.blank and not field.primary_key
        entry['read_only'] = field.primary_key or getattr(field, 'auto_now_add', False) or getattr(field, 'auto_now', False)
        entry['max_length'] = getattr(field, 'max_length', None)

        if field.choices:
            entry['choices'] = [{'value': str(k), 'label': str(v)} for k, v in field.choices]

        if field.is_relation and field.related_model:
            related = field.related_model
            entry['related_model'] = f"{related._meta.app_label}.{related._meta.model_name}"
            entry['related_name_field'] = _get_display_field(related)
            entry['related_verbose'] = str(related._meta.verbose_name) if related._meta.verbose_name else ''
            entry['related_count'] = related.objects.count()

        fields.append(entry)

    return JsonResponse({
        'fields': fields,
        'verbose_name': str(model._meta.verbose_name or model_name),
        'verbose_name_plural': str(model._meta.verbose_name_plural or ''),
        'model_name': model_name,
    })


@csrf_exempt
def model_data(request, app_label, model_name):
    """GET/POST /sysadmin/data/{app}.{model}/ — 列表/新建"""
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({'error': 'Model not found'}, status=404)

    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        search = request.GET.get('search', '')
        ordering = request.GET.get('ordering', '-pk')

        qs = model.objects.all()

        # 按公司过滤（如果有 company 字段）
        company = request.GET.get('company') or request.headers.get('X-Company', '')
        if company and hasattr(model, 'company'):
            qs = qs.filter(company=company)
        # 默认只显示 flag='Y' 的记录
        if hasattr(model, 'flag'):
            flag_filter = request.GET.get('flag', '')
            if not flag_filter:
                qs = qs.filter(flag='Y')
        # 未分类：topcode 为空或 NULL
        if request.GET.get('uncategorized') == '1' and hasattr(model, 'topcode'):
            qs = qs.filter(Q(topcode__isnull=True) | Q(topcode=''))
        # 自定义过滤：允许通过 GET 参数筛选模型字段
        filterable = ['topcode', 'brand', 'displayclass1', 'valiflag']
        for key in filterable:
            val = request.GET.get(key, '')
            if val and hasattr(model, key):
                qs = qs.filter(**{key: val})
        # 任意字段过滤（用于通用 CRUD）
        for key in request.GET:
            if key not in ('page', 'page_size', 'search', 'ordering', 'company', 'storecode', *filterable):
                if hasattr(model, key) and request.GET[key]:
                    val = request.GET[key]
                    if val == '__null__':
                        qs = qs.filter(**{f'{key}__isnull': True})
                    elif val == '__blank__':
                        qs = qs.filter(Q(**{key: ''}) | Q(**{f'{key}__isnull': True}))
                    else:
                        qs = qs.filter(**{key: val})

        # 搜索
        if search:
            search_fields = [f.name for f in model._meta.fields if f.get_internal_type() in ('CharField', 'TextField')]
            if search_fields:
                q = Q()
                for sf in search_fields:
                    q |= Q(**{f'{sf}__icontains': search})
                qs = qs.filter(q)

        total = qs.count()
        try:
            qs = qs.order_by(ordering)
        except:
            qs = qs.order_by('-pk')

        # 预加载外键，避免逐行 getattr 触发 N+1 查询
        fk_names = [
            f.name for f in model._meta.fields
            if f.is_relation and f.related_model and not getattr(f, 'many_to_many', False)
        ]
        if fk_names:
            try:
                qs = qs.select_related(*fk_names)
            except Exception:
                pass

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        rows = []
        for obj in page_obj:
            row = OrderedDict()
            for f in model._meta.fields:
                val = getattr(obj, f.name, None)
                if val is not None:
                    if f.get_internal_type() in ('FileField', 'ImageField'):
                        val = str(val or '')
                    elif hasattr(val, 'strftime'):
                        val = val.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(val, Decimal):
                        val = float(val)
                    elif f.is_relation and f.related_model:
                        val = str(val)
                row[f.name] = val
            rows.append(row)

        return JsonResponse({
            'total': total,
            'page': page,
            'page_size': page_size,
            'rows': rows,
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({'error': '无效的 JSON'}, status=400)

        # 自动填充公司/门店
        if hasattr(model, 'company') and 'company' not in data:
            data['company'] = request.headers.get('X-Company', '')
        if hasattr(model, 'storecode') and 'storecode' not in data:
            data['storecode'] = request.headers.get('X-Storecode', '')
        if hasattr(model, 'flag') and 'flag' not in data:
            data['flag'] = 'Y'

        try:
            _coerce_fk_values(model, data)
            obj = model.objects.create(**data)
            return JsonResponse({'ok': True, 'pk': obj.pk})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def model_data_detail(request, app_label, model_name, pk):
    """GET/PUT/DELETE /sysadmin/data/{app}.{model}/{pk}/ — 详情/更新/删除"""
    try:
        model = apps.get_model(app_label, model_name)
    except LookupError:
        return JsonResponse({'error': 'Model not found'}, status=404)

    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        row = OrderedDict()
        for f in model._meta.fields:
            val = getattr(obj, f.name, None)
            if val is not None:
                if f.get_internal_type() in ('FileField', 'ImageField'):
                    val = str(val or '')
                elif hasattr(val, 'strftime'):
                    val = val.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(val, Decimal):
                    val = float(val)
                elif f.is_relation and f.related_model:
                    val = str(val)
            row[f.name] = val
        return JsonResponse(row)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({'error': '无效的 JSON'}, status=400)

        _coerce_fk_values(model, data)
        for key, val in data.items():
            if hasattr(obj, key):
                setattr(obj, key, val)
        try:
            obj.save()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            obj.delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def related_search(request):
    """GET /sysadmin/related-search/?model={app}.{name}&q=xxx — FK 搜索"""
    model_path = request.GET.get('model', '')
    q = request.GET.get('q', '')
    if not model_path:
        return JsonResponse({'results': []})
    try:
        app_label, model_name = model_path.split('.', 1)
        model = apps.get_model(app_label, model_name)
    except:
        return JsonResponse({'results': []})

    display_field = _get_display_field(model)
    qs = model.objects.all()

    # 按公司过滤
    company = request.GET.get('company') or request.headers.get('X-Company', '')
    if company and hasattr(model, 'company'):
        qs = qs.filter(company=company)

    if q and hasattr(model, display_field):
        qs = qs.filter(**{f'{display_field}__icontains': q})

    results = []
    for obj in qs[:50]:
        label = str(getattr(obj, display_field, obj.pk))
        results.append({'value': str(obj.pk), 'label': label})

    return JsonResponse({'results': results})


# Fix for Decimal not imported in the function body
from decimal import Decimal


def build_tree(items, parent_key='parentcode', key='topcode', label='ttname'):
    """将扁平列表转换为树形结构"""
    from collections import defaultdict
    children = defaultdict(list)
    existing_codes = {item[key] for item in items if item.get(key)}
    for item in items:
        parent = item.get(parent_key) or ''
        children[parent].append(item)
    
    def make_node(item):
        parent_val = item.get(parent_key) or ''
        node = {
            key: item[key],
            label: item.get(label) or item.get(key, ''),
            'pk': item.get('pk'),
            'parentcode': parent_val,
        }
        # 保留原始父级字段名（商品大类用 parent，服务大类用 parentcode）
        node[parent_key] = parent_val
        kids = children.get(item[key], [])
        if kids:
            node['children'] = [make_node(c) for c in kids]
        return node
    
    # 根节点：parentcode 为空，或者 parentcode 引用了不存在的节点
    roots_items = [c for c in items if not c.get(parent_key) or c.get(parent_key) not in existing_codes]
    roots = [make_node(c) for c in roots_items]
    return roots
