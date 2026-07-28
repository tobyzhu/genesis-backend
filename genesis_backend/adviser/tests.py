
from django.test import SimpleTestCase
import importlib


class CheckoutFunctionsRemovedTest(SimpleTestCase):
    """验证结账功能已从 adviser.views 移除（目标状态）"""

    def setUp(self):
        self.adviser_views = importlib.import_module('adviser.views')

    def _test_function_removed(self, name):
        self.assertFalse(hasattr(self.adviser_views, name),
                         f'{name} 仍然存在于 adviser.views')

    def test_customer_checkout_removed(self):
        self._test_function_removed('customer_checkout')

    def test_customer_checkout_confirm_removed(self):
        self._test_function_removed('customer_checkout_confirm')

    def test_payment_methods_removed(self):
        self._test_function_removed('payment_methods')

    def test_batch_checkout_removed(self):
        self._test_function_removed('batch_checkout')

    def test_get_checkedout_orders_removed(self):
        self._test_function_removed('get_checkedout_orders')

    def test_get_receipt_removed(self):
        self._test_function_removed('get_receipt')

    def test_checkout_hungs_removed(self):
        self._test_function_removed('checkout_hungs')

    def test_get_checkout_shortfall_removed(self):
        self._test_function_removed('get_checkout_shortfall')

    def test__resolve_hung_itemname_removed(self):
        # _resolve_hung_itemname 是 shared helper，从 common.views 导入
        # 所以 adviser.views 仍有该属性（import），不需要检查移除
        pass


class CheckoutUrlsRemovedTest(SimpleTestCase):
    """验证结账 URL 已从 adviser/urls.py 移除"""

    def setUp(self):
        self.adviser_urls = importlib.import_module('adviser.urls')

    def test_checkout_urls_gone(self):
        """逐一检查 adviser.urlpatterns 中没有 checkout 相关回调"""
        checkout_names = {
            'customer_checkout', 'customer_checkout_confirm',
            'payment_methods', 'batch_checkout', 'checkout_hungs',
            'get_checkedout_orders', 'get_receipt', 'get_checkout_shortfall',
        }
        for p in self.adviser_urls.urlpatterns:
            name = getattr(p, 'callback', None)
            if name is not None:
                self.assertNotIn(
                    name.__name__, checkout_names,
                    f'URL {p.pattern} 仍引用 {name.__name__} 在 adviser 中',
                )


class ItemFunctionsInAdviserTest(SimpleTestCase):
    """验证选品接口已迁入 adviser.views"""

    def setUp(self):
        self.adviser_views = importlib.import_module('adviser.views')

    def _test_function_in_adviser(self, name):
        self.assertTrue(hasattr(self.adviser_views, name),
                        f'{name} 不存在于 adviser.views')

    def test_service_items_in_adviser(self):
        self._test_function_in_adviser('service_items')

    def test_goods_items_in_adviser(self):
        self._test_function_in_adviser('goods_items')

    def test_cardtype_items_in_adviser(self):
        self._test_function_in_adviser('cardtype_items')

    def test_service_items_callable(self):
        self.assertTrue(callable(self.adviser_views.service_items))

    def test_goods_items_callable(self):
        self.assertTrue(callable(self.adviser_views.goods_items))

    def test_cardtype_items_callable(self):
        self.assertTrue(callable(self.adviser_views.cardtype_items))
