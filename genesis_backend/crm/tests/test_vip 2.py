"""CRM 模块测试 - VIP 洞察 + 健康档案"""
from django.test import TestCase
from rest_framework.test import APIClient
from baseinfo.models import Vip
from cashier.models import Expvstoll, Expense


class VipHealthRecordTest(TestCase):
    """健康档案 CRUD 测试"""

    def setUp(self):
        self.client = APIClient()
        self.vip = Vip.objects.create(
            company='yiren', storecode='01', flag='Y',
            vcode='V001', vname='测试客户', mtcode='13800138000',
        )

    def test_create_health_record(self):
        from crm.models import VipHealthRecord
        resp = self.client.post('/crm/health_records/', {
            'company': 'yiren', 'vipuuid': str(self.vip.uuid),
            'skin_type': '混合性', 'allergies': '花粉',
            'body_concerns': '肩颈酸痛', 'contraindications': '',
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['skin_type'], '混合性')

    def test_list_health_records(self):
        from crm.models import VipHealthRecord
        VipHealthRecord.objects.create(company='yiren', vipuuid=self.vip, skin_type='干性')
        resp = self.client.get('/crm/health_records/', {'company': 'yiren', 'vipuuid': str(self.vip.uuid)})
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.json()), 1)

    def test_update_health_record(self):
        from crm.models import VipHealthRecord
        rec = VipHealthRecord.objects.create(company='yiren', vipuuid=self.vip, skin_type='干性')
        resp = self.client.put(f'/crm/health_records/{rec.uuid}/', {
            'company': 'yiren', 'skin_type': '油性',
        }, format='json')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['skin_type'], '油性')

    def test_delete_health_record(self):
        from crm.models import VipHealthRecord
        rec = VipHealthRecord.objects.create(company='yiren', vipuuid=self.vip, skin_type='干性')
        resp = self.client.delete(f'/crm/health_records/{rec.uuid}/')
        self.assertEqual(resp.status_code, 204)


class VipInsightTest(TestCase):
    """VIP 洞察聚合 API 测试"""

    def setUp(self):
        self.client = APIClient()
        self.vip = Vip.objects.create(
            company='yiren', storecode='01', flag='Y',
            vcode='V002', vname='洞察客户', mtcode='13900139000',
        )

    def test_vip_insight_no_data(self):
        resp = self.client.get('/crm/vip_insight/', {
            'company': 'yiren', 'vipuuid': str(self.vip.uuid),
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['total_visits'], 0)
        self.assertIsNone(data['last_visit_date'])

    def test_vip_insight_with_data(self):
        head = Expvstoll.objects.create(
            company='yiren', storecode='01', flag='Y', valiflag='Y',
            vipuuid=self.vip, vsdate='20260701',
            totmount=500, sumdisc=0,
        )
        Expense.objects.create(
            company='yiren', storecode='01', flag='Y',
            ttype='S', srvcode='SV001',
            s_price=500, s_qty=1, s_mount=500,
            pmcode='E001', transuuid=head,
        )
        resp = self.client.get('/crm/vip_insight/', {
            'company': 'yiren', 'vipuuid': str(self.vip.uuid),
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('total_visits', data)
        self.assertIn('total_spent', data)
        self.assertIn('preferred_items', data)
