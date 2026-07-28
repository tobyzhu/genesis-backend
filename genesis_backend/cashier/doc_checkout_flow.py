"""
结账流程集成测试文档
════════════════════

测试场景:
  1. 现金支付结账 → 验证 Expvstoll / Expense / Toll 三表都有数据
  2. 储值卡支付   → 验证 Cardinfo.leftmoney 扣减
  3. 计次卡支付   → 验证 Cardinfo.leftqty  扣减

运行方式:
  此文件被 pytest 自动发现 (test_*.py)，但所有测试方法使用 pytest.mark.skip
  标记，不会自动执行。

  在 MySQL 可用的环境中，将本文件复制或移动到同目录下名为
  test_checkout_flow.py 并去掉 skip 标记后执行:

    cd genesis_backend
    cp cashier/doc_checkout_flow.py cashier/test_checkout_flow.py
    .venv/bin/python manage.py test \\
        cashier.test_checkout_flow \\
        --settings=genesis.settings
    rm cashier/test_checkout_flow.py

  或者直接执行:

    cd genesis_backend
    .venv/bin/python -m pytest cashier/test_checkout_flow.py

"""

import json
from decimal import Decimal
from django.test import TestCase
import pytest

from baseinfo.models import Vip, Cardtype, Serviece, Paymode
from adviser.models import Cardinfo, ExpvstollHung, ExpenseHung
from cashier.models import Expvstoll, Expense, Toll

COMPANY = 'test'
STORECODE = '01'


@pytest.mark.skip(reason='需要 MySQL 测试数据库')
class CheckoutIntegrationTest(TestCase):
    """结账流程集成测试（需 MySQL 测试数据库）"""

    INITIAL_BALANCE = Decimal('500')
    DEBIT_AMOUNT = Decimal('80')

    @classmethod
    def setUpTestData(cls):
        # ── VIP ──
        cls.vip = Vip.objects.create(
            vcode='T001', vname='测试会员', mtcode='13800138000',
            company=COMPANY, storecode=STORECODE, status='O', flag='Y',
        )
        # ── 服务项目 ──
        Serviece.objects.create(
            company=COMPANY, svrcdoe='SV001', svrname='测试服务项目', flag='Y',
        )
        # ── 付款方式 ──
        Paymode.objects.create(
            company=COMPANY, pcode='A', pname='现金', iscash='1', flag='Y',
        )
        # ── 两种卡类 ──
        Cardtype.objects.create(
            company=COMPANY, cardtype='CT001', cardname='测试储值卡',
            suptype='10', comptype='amount', price=1000, flag='Y',
        )
        Cardtype.objects.create(
            company=COMPANY, cardtype='CT002', cardname='测试计次卡',
            suptype='20', comptype='times', price=500, flag='Y',
        )
        cls.amount_ct = Cardtype.objects.get(company=COMPANY, cardtype='CT001')
        cls.times_ct = Cardtype.objects.get(company=COMPANY, cardtype='CT002')

        # ── 储值卡 ──
        Cardinfo.objects.create(
            company=COMPANY, ccode='T001-CARD-A', cardtype='CT001',
            cardtypeuuid=cls.amount_ct, vipuuid=cls.vip,
            leftmoney=cls.INITIAL_BALANCE, s_price=1000.0000, leftqty=999,
            status='O', stype='N', flag='Y',
        )
        # ── 计次卡 ──
        Cardinfo.objects.create(
            company=COMPANY, ccode='T001-CARD-T', cardtype='CT002',
            cardtypeuuid=cls.times_ct, vipuuid=cls.vip,
            leftmoney=Decimal('0'), leftqty=Decimal('5'),
            s_price=100.0000, status='O', stype='N', flag='Y',
        )

        # ═══════════════ 现金挂单 ═══════════════
        cls.cash_hung = ExpvstollHung.objects.create(
            company=COMPANY, storecode=STORECODE, vipuuid=cls.vip,
            exptxserno_hung=f'{COMPANY}{STORECODE}_hung_10',
            ttype_hung='S', psstatus_hung='10', valiflag_hung='Y',
            ccode_hung='', flag='Y',
        )
        ExpenseHung.objects.create(
            company=COMPANY, storecode=STORECODE, hunguuid=cls.cash_hung,
            ttype_hung='S', srvcode_hung='SV001', stype_hung='N',
            s_qty_hung=1, s_price_hung=Decimal('100'),
            s_mount_hung=Decimal('100'), otherserno_hung='',
            pmcode_hung='', asscode1_hung='', asscode2_hung='',
            ditem_hung='0001',
            exptxserno_hung=f'{COMPANY}{STORECODE}_hung_10', flag='Y',
        )

        # ═══════════════ 储值卡挂单 ═══════════════
        cls.card_hung = ExpvstollHung.objects.create(
            company=COMPANY, storecode=STORECODE, vipuuid=cls.vip,
            exptxserno_hung=f'{COMPANY}{STORECODE}_hung_11',
            ttype_hung='S', psstatus_hung='10', valiflag_hung='Y',
            ccode_hung='T001-CARD-A', flag='Y',
        )
        ExpenseHung.objects.create(
            company=COMPANY, storecode=STORECODE, hunguuid=cls.card_hung,
            ttype_hung='S', srvcode_hung='SV001', stype_hung='N',
            s_qty_hung=1, s_price_hung=Decimal('80'),
            s_mount_hung=Decimal('80'),
            otherserno_hung='T001-CARD-A',
            pmcode_hung='', asscode1_hung='', asscode2_hung='',
            ditem_hung='0001',
            exptxserno_hung=f'{COMPANY}{STORECODE}_hung_11', flag='Y',
        )

        # ═══════════════ 计次卡挂单 ═══════════════
        cls.times_hung = ExpvstollHung.objects.create(
            company=COMPANY, storecode=STORECODE, vipuuid=cls.vip,
            exptxserno_hung=f'{COMPANY}{STORECODE}_hung_12',
            ttype_hung='S', psstatus_hung='10', valiflag_hung='Y',
            ccode_hung='T001-CARD-T', flag='Y',
        )
        ExpenseHung.objects.create(
            company=COMPANY, storecode=STORECODE, hunguuid=cls.times_hung,
            ttype_hung='S', srvcode_hung='SV001', stype_hung='N',
            s_qty_hung=1, s_price_hung=Decimal('100'),
            s_mount_hung=Decimal('100'),
            otherserno_hung='T001-CARD-T',
            pmcode_hung='', asscode1_hung='', asscode2_hung='',
            ditem_hung='0001',
            exptxserno_hung=f'{COMPANY}{STORECODE}_hung_12', flag='Y',
        )

    # ══════════════════════════════════════
    # 场景 1：现金支付
    # ══════════════════════════════════════
    def test_01_cash_payment_flow(self):
        """现金支付 → customer_checkout → confirm → 三表验证"""
        # 结账汇总
        sresp = self.client.get('/cashier/customer_checkout/', {
            'company': COMPANY, 'storecode': STORECODE,
            'vipuuid': str(self.vip.uuid),
        })
        self.assertTrue(sresp.json().get('ok'))

        # 确认结账
        cresp = self.client.post(
            '/cashier/customer_checkout_confirm/',
            data=json.dumps({
                'company': COMPANY, 'storecode': STORECODE,
                'vipuuid': str(self.vip.uuid), 'cashier': 'E001',
                'payments': [],
            }),
            content_type='application/json',
        )
        self.assertTrue(cresp.json().get('ok'))

        # 三表验证
        self._assert_three_tables(COMPANY, self.cash_hung.exptxserno_hung)

    # ══════════════════════════════════════
    # 场景 2：储值卡支付
    # ══════════════════════════════════════
    def test_02_amount_card_payment(self):
        """储值卡支付 → batch_checkout(split) → 扣款验证"""
        card = Cardinfo.objects.get(company=COMPANY, ccode='T001-CARD-A', flag='Y')
        bal_before = card.leftmoney
        debit = self.DEBIT_AMOUNT

        resp = self._exec_split(self.card_hung, [
            {'pcode': 'A', 'ccode': 'T001-CARD-A', 'amount': float(debit)},
        ])
        self._assert_ok(resp)

        # 三表
        self._assert_three_tables(COMPANY, self.card_hung.exptxserno_hung)

        # 扣款
        card.refresh_from_db()
        expected = bal_before - debit
        self.assertEqual(card.leftmoney, expected,
                         f'储值卡 {card.ccode} 余额: {bal_before} - {debit} = {expected}')

    # ══════════════════════════════════════
    # 场景 3：计次卡支付
    # ══════════════════════════════════════
    def test_03_times_card_payment(self):
        """计次卡支付 → batch_checkout(split) → 扣次验证"""
        card = Cardinfo.objects.get(company=COMPANY, ccode='T001-CARD-T', flag='Y')
        qty_before = card.leftqty

        resp = self._exec_split(self.times_hung, [
            {'pcode': 'A', 'ccode': 'T001-CARD-T', 'amount': 1.0},
        ])
        self._assert_ok(resp)

        # 三表
        self._assert_three_tables(COMPANY, self.times_hung.exptxserno_hung)

        # 扣次
        card.refresh_from_db()
        expected = qty_before - Decimal('1')
        self.assertEqual(card.leftqty, expected,
                         f'计次卡 {card.ccode} 余次: {qty_before} - 1 = {expected}')

    # ══════════════════════════════════════
    # 场景 4：错误场景
    # ══════════════════════════════════════
    def test_04_error_empty_vip(self):
        resp = self.client.get('/cashier/customer_checkout/', {
            'company': COMPANY, 'storecode': STORECODE, 'vipuuid': '',
        })
        self.assertFalse(resp.json().get('ok', True))

    def test_05_error_nonexistent_vip(self):
        resp = self.client.get('/cashier/customer_checkout/', {
            'company': COMPANY, 'storecode': STORECODE,
            'vipuuid': '00000000-0000-0000-0000-000000000000',
        })
        self.assertFalse(resp.json().get('ok', True))

    def test_06_confirm_rejects_get(self):
        resp = self.client.get('/cashier/customer_checkout_confirm/')
        self.assertFalse(resp.json().get('ok', True))

    # ══════════════════════════════════════
    # 辅助方法
    # ══════════════════════════════════════
    def _exec_split(self, hung, splits):
        return self.client.post(
            '/cashier/batch_checkout/',
            data=json.dumps({
                'company': COMPANY, 'storecode': STORECODE,
                'cashier': 'E001',
                'uuids': [str(hung.uuid)],
                'payments': {},
                'splits': {str(hung.uuid): splits},
            }),
            content_type='application/json',
        )

    def _assert_ok(self, resp):
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        items = data if isinstance(data, list) else [data]
        for item in items:
            self.assertTrue(item.get('ok', False), msg=str(item))

    def _assert_three_tables(self, company, hungserno):
        """验证结账后 Expvstoll / Expense / Toll 三个表都有数据"""
        # Expvstoll
        tx_qs = Expvstoll.objects.filter(company=company, hungserno=hungserno)
        tx_cnt = tx_qs.count()
        self.assertGreater(tx_cnt, 0, f'Expvstoll 缺失 (hungserno={hungserno})')

        # Expense
        exp_cnt = Expense.objects.filter(company=company, hungserno=hungserno).count()
        self.assertGreater(exp_cnt, 0, f'Expense 缺失 (hungserno={hungserno})')

        # Toll
        tx = tx_qs.first()
        toll_cnt = Toll.objects.filter(company=company, transuuid=tx).count()
        self.assertGreater(toll_cnt, 0, f'Toll 缺失 (transuuid={tx.uuid})')

        print(f'  ✅ 三表: Expvstoll={tx_cnt}  Expense={exp_cnt}  Toll={toll_cnt}')
