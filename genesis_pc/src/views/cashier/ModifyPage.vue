<template>
  <div class="modify-page">
    <div class="header-row">
      <h2 style="margin:0;font-size:18px;font-weight:600">修改单据</h2>
      <div class="filters">
        <el-radio-group v-model="dateFilter" size="small" @change="loadOrders">
          <el-radio-button value="today">今天</el-radio-button>
          <el-radio-button value="week">本周</el-radio-button>
          <el-radio-button value="month">本月</el-radio-button>
        </el-radio-group>
        <el-input v-model="vipKeyword" placeholder="会员姓名/手机号" clearable size="small" style="width:170px" @keyup.enter="loadOrders" />
        <el-input v-model="sernoKeyword" placeholder="单号" clearable size="small" style="width:120px" @keyup.enter="loadOrders" />
        <el-button size="small" type="primary" @click="loadOrders">查询</el-button>
        <span style="font-size:12px;color:var(--g-color-text-muted);margin-left:4px">共 {{ filteredOrders.length }} 单</span>
      </div>
    </div>

    <el-table v-if="!loading" :data="filteredOrders" stripe size="small" max-height="calc(100vh - 260px)"
      highlight-current-row @row-click="selectOrder" :row-class-name="rowClassName">
      <el-table-column label="单号" prop="exptxserno" width="130" />
      <el-table-column label="会员" width="90">
        <template #default="{ row }">{{ row.vname || '--' }}</template>
      </el-table-column>
      <el-table-column label="会员号" width="80">
        <template #default="{ row }">{{ row.vcode || '--' }}</template>
      </el-table-column>
      <el-table-column label="日期" prop="vsdate" width="80" />
      <el-table-column label="金额" width="90" align="right">
        <template #default="{ row }">¥{{ (row.totmount || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="项目数" prop="itemcount" width="55" align="center" />
      <el-table-column label="付款卡号" width="150">
        <template #default="{ row }">{{ row.paycode || '--' }}</template>
      </el-table-column>
      <el-table-column label="卡类" width="70">
        <template #default="{ row }">{{ row.cardtypename || row.cardtype || '--' }}</template>
      </el-table-column>
      <el-table-column label="开单员" width="80">
        <template #default="{ row }">{{ empNameFromItem(row) }}</template>
      </el-table-column>
    </el-table>
    <div v-if="loading" style="text-align:center;padding:30px;color:var(--g-color-text-muted)">加载中...</div>
    <el-empty v-if="!loading && !filteredOrders.length" description="暂无已结账订单" />

    <el-card v-if="selectedOrder" shadow="never" class="detail-card">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span>{{ selectedOrder.exptxserno }} — {{ selectedOrder.vname || selectedOrder.vcode || '--' }} ｜ ¥{{ (selectedOrder.totmount || 0).toFixed(2) }}</span>
          <div style="display:flex;gap:6px">
            <el-button size="small" text @click="selectedOrder = null">关闭</el-button>
            <el-button size="small" type="primary" :loading="saving" @click="saveOrder">保存修改</el-button>
          </div>
        </div>
      </template>
      <div v-if="selectedOrderPayments.length" style="font-size:12px;color:var(--g-color-text-secondary);padding:6px 0 0">
        付款方式：<span v-for="(p, pi) in selectedOrderPayments" :key="pi" style="margin-right:8px">{{ p.name }} ¥{{ p.amount.toFixed(2) }}</span>
      </div>
      <el-table :data="selectedOrder.item_details" size="small" stripe>
        <el-table-column label="项目" min-width="140">
          <template #default="{ row }">{{ (row.ttypename ? row.ttypename + '-' : '') + (row.name || row.srvcode || '') }}</template>
        </el-table-column>
        <el-table-column label="数量" width="50" align="center">
          <template #default="{ row }">×{{ Number(row.qty).toFixed(0) }}</template>
        </el-table-column>
        <el-table-column label="金额" width="70" align="right">
          <template #default="{ row }">¥{{ Number(row.subtotal).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="属性" width="55" align="center">
          <template #default="{ row }"><el-tag size="small" effect="plain" :type="row.stypename === '赠送' ? 'warning' : undefined">{{ row.stypename }}</el-tag></template>
        </el-table-column>
        <el-table-column label="开单员" width="130">
          <template #default="{ row }">
            <el-select v-model="row.pmcode" size="small" filterable clearable placeholder="开单员" style="width:100%">
              <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename + '(' + emp.ecode + ')'" :value="emp.ecode" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="美疗师1" width="130">
          <template #default="{ row }">
            <el-select v-model="row.asscode1" size="small" filterable clearable placeholder="美疗师1" style="width:100%">
              <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename + '(' + emp.ecode + ')'" :value="emp.ecode" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="美疗师2" width="130">
          <template #default="{ row }">
            <el-select v-model="row.asscode2" size="small" filterable clearable placeholder="美疗师2" style="width:100%">
              <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename + '(' + emp.ecode + ')'" :value="emp.ecode" />
            </el-select>
          </template>
        </el-table-column>
      </el-table>
      <div v-if="selectedPayments.length" style="margin-top:8px;border-top:1px solid var(--g-color-border);padding-top:6px">
        <div style="font-size:12px;font-weight:600;color:var(--g-color-text-secondary);margin-bottom:4px">付款方式（可修改）</div>
        <div v-for="(p, pi) in selectedPayments" :key="pi" style="display:flex;align-items:center;gap:4px;padding:3px 0;font-size:12px">
          <el-select v-model="p.pcode" size="small" style="width:120px" filterable>
            <el-option v-for="opt in paymentOptionsForType(p)" :key="opt.pcode" :label="opt.pname" :value="opt.pcode"></el-option>
          </el-select>
          <span style="color:var(--g-color-text-muted)">¥{{ Number(p.amount).toFixed(2) }}</span>
          <span v-if="p._originalPcode !== p.pcode" style="font-size:10px;color:var(--g-color-money)">已修改</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const company = localStorage.getItem('genesis_pc_company') || ''
const storecode = localStorage.getItem('genesis_pc_storecode') || ''

const dateFilter = ref('today')
const vipKeyword = ref('')
const sernoKeyword = ref('')
const loading = ref(false)
const orders = ref<any[]>([])
const employees = ref<{ecode:string;ename:string}[]>([])
const selectedOrder = ref<any>(null)
const saving = ref(false)
const selectedOrderPayments = ref<any[]>([])
const selectedPayments = ref<any[]>([])
const paymodes = ref<any[]>([])

function dateFromFilter(): string {
  const d = new Date()
  if (dateFilter.value === 'today')
    return '' + d.getFullYear() + String(d.getMonth()+1).padStart(2,'0') + String(d.getDate()).padStart(2,'0')
  if (dateFilter.value === 'week') {
    d.setDate(d.getDate() - ((d.getDay() + 6) % 7 + 1))
    return '' + d.getFullYear() + String(d.getMonth()+1).padStart(2,'0') + String(d.getDate()).padStart(2,'0')
  }
  if (dateFilter.value === 'month') {
    d.setDate(1)
    return '' + d.getFullYear() + String(d.getMonth()+1).padStart(2,'0') + String(d.getDate()).padStart(2,'0')
  }
  return ''
}

const filteredOrders = computed(() => {
  let list = orders.value
  const vk = vipKeyword.value.trim().toLowerCase()
  if (vk) list = list.filter((o:any) => (o.vname||'').toLowerCase().includes(vk) || (o.vcode||'').toLowerCase().includes(vk))
  const sk = sernoKeyword.value.trim().toLowerCase()
  if (sk) list = list.filter((o:any) => (o.exptxserno||'').toLowerCase().includes(sk))
  return list
})

function rowClassName({ row }: any) {
  return (selectedOrder.value?.exptxserno === row.exptxserno) ? 'selected-row' : ''
}

async function loadOrders() {
  loading.value = true; selectedOrder.value = null
  const params: Record<string, string> = { company, storecode, psstatus: '70' }
  const df = dateFromFilter()
  if (df) params.vsdate_from = df
  const _d = new Date(); params.vsdate_to = '' + _d.getFullYear() + String(_d.getMonth()+1).padStart(2,'0') + String(_d.getDate()).padStart(2,'0')
  try {
    const res = await request.get('/adviser/get_hung_list/', { params })
    orders.value = Array.isArray(res.data) ? res.data : []
  } catch { orders.value = [] }
  finally { loading.value = false }
}

async function loadEmployees() {
  try {
    const res = await request.get('/adviser/get_bookingable_empllist/', { params: { company, storecode } })
    const list = Array.isArray(res.data) ? res.data : res.data?.results ?? []
    employees.value = list.map((e:any) => ({ ecode: e.ecode||'', ename: e.ename||'' }))
  } catch { employees.value = [] }
}

async function loadPaymodes() {
  try {
    const res = await request.get('/cashier/payment_methods/', { params: { company } })
    paymodes.value = res.data?.paymodes || []
  } catch { paymodes.value = [] }
}

function selectOrder(row: any) {
  selectedOrder.value = row
  selectedOrderPayments.value = []
  selectedPayments.value = []
  if (row?.exptxserno) {
    request.get('/cashier/get_order_payment/', { params: { company, exptxserno: row.exptxserno } })
      .then(r => {
        if (r.data?.ok) {
          selectedOrderPayments.value = r.data.payments || []
          selectedPayments.value = (r.data.payments || []).map((p: any) => ({ ...p, _originalPcode: p.pcode }))
        }
      })
      .catch(() => {})
  }
}

function empNameFromItem(row: any): string {
  const items = row.item_details
  if (!items?.length) return '--'
  const pmcode = items[0].pmcode || ''
  if (!pmcode) return '--'
  const emp = employees.value.find((e: any) => e.ecode === pmcode)
  return emp ? emp.ename : pmcode
}

function paymentOptionsForType(p: any): any[] {
  const pm = paymodes.value.find((x: any) => x.pcode === p._originalPcode || x.pcode === p.pcode)
  const isc = pm?.iscash || ''
  if (!isc) return paymodes.value
  return paymodes.value.filter((x: any) => x.iscash === isc)
}

async function saveOrder() {
  if (!selectedOrder.value) return
  saving.value = true
  try {
    const expenses = (selectedOrder.value.item_details || []).map((d:any) => ({
      ditem: String(d.ditem || ''),
      pmcode: String(d.pmcode || ''),
      asscode1: String(d.asscode1 || ''),
      asscode2: String(d.asscode2 || ''),
    }))
    const res = await request.post('/cashier/update_checkedout/', {
      company, exptxserno: selectedOrder.value.exptxserno,
      changes: { ecode: '', expenses,
        payments: selectedPayments.value
          .filter((p: any) => p._originalPcode !== p.pcode)
          .map((p: any) => ({ old_pcode: p._originalPcode, new_pcode: p.pcode, amount: p.amount })),
      },
    })
    if (res.data?.ok) { ElMessage.success('修改已保存'); selectedOrder.value = null }
    else ElMessage.error(res.data?.message || '保存失败')
  } catch (err:any) { ElMessage.error('保存失败: ' + (err?.message||'')) }
  finally { saving.value = false }
}

loadPaymodes(); loadEmployees(); loadOrders()
</script>

<style scoped>
.modify-page { display:flex; flex-direction:column; gap:10px; height:100%; }
.header-row { display:flex; justify-content:space-between; align-items:center; flex-shrink:0; flex-wrap:wrap; gap:6px; }
.filters { display:flex; align-items:center; gap:6px; flex-wrap:wrap; }
.detail-card { flex-shrink:0; }
</style>
