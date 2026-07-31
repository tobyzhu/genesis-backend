#coding:utf-8
"""sysadmin 模块测试"""
import unittest
from .registry import ADMIN_REGISTRY, get_registry


class TestRegistry(unittest.TestCase):
    """测试模型注册中心"""

    def test_registry_not_empty(self):
        """注册列表不为空"""
        self.assertTrue(len(ADMIN_REGISTRY) > 0)

    def test_registry_has_required_keys(self):
        """每条注册记录包含必要字段"""
        for item in ADMIN_REGISTRY:
            self.assertIn('app_label', item)
            self.assertIn('model_name', item)
            self.assertIn('verbose_name', item)
            self.assertIn('icon', item)

    def test_registry_contains_core_models(self):
        """包含核心业务模型"""
        models = {(m['app_label'], m['model_name']) for m in ADMIN_REGISTRY}
        self.assertIn(('baseinfo', 'storeinfo'), models)
        self.assertIn(('baseinfo', 'paymode'), models)
        self.assertIn(('baseinfo', 'empl'), models)
        self.assertIn(('baseinfo', 'serviece'), models)
        self.assertIn(('baseinfo', 'goods'), models)
        self.assertIn(('baseinfo', 'cardtype'), models)
        self.assertIn(('adviser', 'promotions'), models)

    def test_get_registry_groups(self):
        """get_registry 返回分组字典"""
        groups = get_registry()
        self.assertIn('基础配置', groups)
        self.assertIn('核心业务', groups)

    def test_registry_each_model_in_group(self):
        """每个模型都在某个分组中"""
        for item in ADMIN_REGISTRY:
            self.assertIn('group', item)


class TestModelList(unittest.TestCase):
    """测试模型列表（通过 URL 导入）"""

    def test_urls_import(self):
        """URL 配置可导入"""
        try:
            from .urls import urlpatterns
            self.assertTrue(len(urlpatterns) > 0)
        except Exception as e:
            self.fail(f"导入 urls.py 失败: {e}")

    def test_views_import(self):
        """视图函数可导入"""
        try:
            from .views import model_list, model_meta, model_data, model_data_detail, related_search
        except Exception as e:
            self.fail(f"导入 views.py 失败: {e}")


class TestURLPatterns(unittest.TestCase):
    """测试 URL 路由"""

    def setUp(self):
        from .urls import urlpatterns
        self.patterns = urlpatterns

    def test_has_model_list_route(self):
        models_routes = [p for p in self.patterns if 'models/' in str(p.pattern)]
        self.assertTrue(len(models_routes) > 0)

    def test_has_data_route(self):
        data_routes = [p for p in self.patterns if 'data/' in str(p.pattern)]
        self.assertTrue(len(data_routes) > 0)

    def test_has_related_search_route(self):
        search_routes = [p for p in self.patterns if 'related-search' in str(p.pattern)]
        self.assertEqual(len(search_routes), 1)


if __name__ == '__main__':
    unittest.main()

class TestTreeBuilder(unittest.TestCase):
    """测试树形结构构建"""

    def test_build_tree(self):
        """测试从扁平列表构建树"""
        from .views import build_tree
        items = [
            {'topcode': '100', 'ttname': '面部', 'parentcode': None},
            {'topcode': '110', 'ttname': '清洁', 'parentcode': '100'},
            {'topcode': '120', 'ttname': '补水', 'parentcode': '100'},
            {'topcode': '200', 'ttname': '身体', 'parentcode': None},
        ]
        tree = build_tree(items)
        self.assertEqual(len(tree), 2)  # 2 root nodes
        self.assertEqual(tree[0]['ttname'], '面部')
        self.assertEqual(len(tree[0]['children']), 2)  # 2 children
        self.assertEqual(tree[0]['children'][0]['ttname'], '清洁')

    def test_build_tree_empty(self):
        from .views import build_tree
        self.assertEqual(build_tree([]), [])

    def test_build_tree_no_parent(self):
        from .views import build_tree
        items = [
            {'topcode': '100', 'ttname': '面部', 'parentcode': None},
            {'topcode': '200', 'ttname': '身体', 'parentcode': None},
        ]
        tree = build_tree(items)
        self.assertEqual(len(tree), 2)

    def test_build_tree_with_missing_parent(self):
        """子节点引用了不存在的父节点"""
        from .views import build_tree
        items = [
            {'topcode': '110', 'ttname': '清洁', 'parentcode': '100'},  # 100 doesn't exist
        ]
        # Should not crash, child goes to root level (or be dropped)
        tree = build_tree(items)
        # The child with missing parent should be placed at root level
        self.assertEqual(len(tree), 1)


class TestTreeBuilderCustomKeys(unittest.TestCase):
    """商品大类树（自定义字段名）测试"""

    def test_build_tree_with_goods_keys(self):
        """goodsct 树使用 goodsct/goodsctname/parent 字段"""
        from .views import build_tree
        items = [
            {'pk': 'uuid-1', 'goodsct': '01', 'goodsctname': '护肤', 'parent': ''},
            {'pk': 'uuid-2', 'goodsct': '0101', 'goodsctname': '面膜', 'parent': '01'},
            {'pk': 'uuid-3', 'goodsct': '02', 'goodsctname': '身体', 'parent': ''},
        ]
        tree = build_tree(items, key='goodsct', label='goodsctname', parent_key='parent')
        self.assertEqual(len(tree), 2)
        root = tree[0]
        self.assertEqual(root['goodsct'], '01')
        self.assertEqual(root['goodsctname'], '护肤')
        self.assertEqual(root['parent'], '')
        self.assertEqual(len(root['children']), 1)
        child = root['children'][0]
        self.assertEqual(child['goodsct'], '0101')
        self.assertEqual(child['parent'], '01')
        # 兼容旧字段名
        self.assertEqual(child['parentcode'], '01')

    def test_build_tree_goods_missing_parent(self):
        """孤儿商品分类归根节点且保留父级编号"""
        from .views import build_tree
        items = [
            {'pk': 'uuid-2', 'goodsct': '0101', 'goodsctname': '面膜', 'parent': '01'},
        ]
        tree = build_tree(items, key='goodsct', label='goodsctname', parent_key='parent')
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]['parent'], '01')
        self.assertEqual(tree[0]['parentcode'], '01')


class TestUUIDDetailRoute(unittest.TestCase):
    """sysadmin 通用详情路由支持 UUID 主键（GenesisModel）"""

    def test_sysadmin_detail_pattern_accepts_uuid(self):
        """sysadmin 内部详情路由的正则支持 UUID"""
        from sysadmin.urls import urlpatterns
        detail = [p for p in urlpatterns if 'pk' in str(p.pattern)][0]
        self.assertRegex(
            'data/baseinfo.goods/3f2504e0-4f89-41d3-9a0c-0305e82c3301/',
            str(detail.pattern)
        )

    def test_adviser_detail_accepts_uuid(self):
        """前端实际使用的 /adviser/sysadmin-data/ 详情路由支持 UUID"""
        from django.urls import resolve
        uuid_str = '3f2504e0-4f89-41d3-9a0c-0305e82c3301'
        match = resolve(f'/adviser/sysadmin-data/baseinfo.goods/{uuid_str}/')
        self.assertIsNotNone(match.func)
        self.assertEqual(match.kwargs['pk'], uuid_str)
