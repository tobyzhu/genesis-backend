"""模型注册中心 — 所有可管理的模型在这里注册"""

ADMIN_REGISTRY = []

def register(app_label, model_name, verbose_name, icon='Setting', group='基础配置'):
    _group_names = {'基础配置': 'base', '核心业务': 'core', '营销': 'marketing'}
    ADMIN_REGISTRY.append({
        'app_label': app_label,
        'model_name': model_name,
        'verbose_name': verbose_name,
        'icon': icon,
        'group': group,
        '_group_key': _group_names.get(group, 'other'),
    })

# ===== 基础配置 =====
register('baseinfo', 'storeinfo', '门店管理', 'Shop')
register('baseinfo', 'position', '岗位管理', 'UserFilled')
register('baseinfo', 'paymode', '付款方式', 'Coin')
register('baseinfo', 'team', '组别管理', 'Flag')
register('baseinfo', 'bankaccount', '银行账户', 'CreditCard')
register('baseinfo', 'supplier', '供应商', 'Truck')
register('baseinfo', 'appoption', '系统选项', 'Setting')
register('baseinfo', 'goodsct', '商品分类', 'CollectionTag')

# ===== 核心业务 =====
register('baseinfo', 'empl', '员工管理', 'Avatar', '核心业务')
register('baseinfo', 'serviece', '服务项目', 'List', '核心业务')
register('baseinfo', 'goods', '商品管理', 'Goods', '核心业务')
register('baseinfo', 'cardtype', '卡类定义', 'CreditCard', '核心业务')
register('baseinfo', 'srvtopty', '服务大类', 'FolderOpened', '核心业务')
register('baseinfo', 'cardsupertype', '卡大类', 'Collection', '核心业务')
register('baseinfo', 'cardsvsdi', '卡类项目关联', 'Link', '核心业务')

# ===== 营销 =====
# Promotions/Promotionsdetail 模型定义在 baseinfo app，注册路径必须与 apps.get_model 一致
register('baseinfo', 'promotions', '活动管理', 'Promotion', '营销')
register('baseinfo', 'promotionsdetail', '活动明细', 'List', '营销')

# ===== 工具 =====
def get_registry():
    """返回分组后的注册列表"""
    groups = {}
    for m in ADMIN_REGISTRY:
        g = m.get('group', '基础配置')
        if g not in groups:
            groups[g] = []
        groups[g].append(m)
    return groups
