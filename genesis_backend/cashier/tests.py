
from django.test import SimpleTestCase
import importlib


class CheckoutFunctionsMovedInTest(SimpleTestCase):
    """验证结账功能已迁入 cashier.views（目标状态）"""

    def setUp(self):
        self.cashier_views = importlib.import_module('cashier.views')

    def _test_function_exists(self, name):
        self.assertTrue(hasattr(self.cashier_views, name),
                        f'{name} 不存在于 cashier.views')

    def test_customer_checkout_exists(self):
        self._test_function_exists('customer_checkout')

    def test_customer_checkout_confirm_exists(self):
        self._test_function_exists('customer_checkout_confirm')

    def test_payment_methods_exists(self):
        self._test_function_exists('payment_methods')

    def test_batch_checkout_exists(self):
        self._test_function_exists('batch_checkout')

    def test_get_checkedout_orders_exists(self):
        self._test_function_exists('get_checkedout_orders')

    def test_get_receipt_exists(self):
        self._test_function_exists('get_receipt')

    def test_get_checkout_shortfall_exists(self):
        self._test_function_exists('get_checkout_shortfall')

    def test_checkout_hungs_exists(self):
        self._test_function_exists('checkout_hungs')

    def test__resolve_hung_itemname_exists(self):
        self._test_function_exists('_resolve_hung_itemname')


class ReexportedFunctionsTest(SimpleTestCase):
    """验证选品接口通过重导出在 cashier 中仍可用，且指向 adviser 的同一个函数"""

    def setUp(self):
        self.cashier_views = importlib.import_module('cashier.views')
        self.adviser_views = importlib.import_module('adviser.views')

    def test_service_items_reexported(self):
        self.assertIs(
            self.cashier_views.service_items,
            self.adviser_views.service_items,
            'service_items 应当是 adviser.views 的同一函数对象',
        )

    def test_goods_items_reexported(self):
        self.assertIs(
            self.cashier_views.goods_items,
            self.adviser_views.goods_items,
        )

    def test_cardtype_items_reexported(self):
        self.assertIs(
            self.cashier_views.cardtype_items,
            self.adviser_views.cardtype_items,
        )


import json
from django.test import TestCase

# 模型（在 setUpTestData 中使用）
from baseinfo.models import Vip, Cardtype, Serviece, Paymode
from adviser.models import Cardinfo, ExpvstollHung, ExpenseHung
from cashier.models import Expvstoll, Expense

COMPANY = 'test'
STORECODE = '01'
OPEN_STATUSES = ('10', '20', '30', '40', '50', '60')


