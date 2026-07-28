<template>
  <div class="chk-page">
    <!-- 顶部统计 -->
    <div class="chk-stats">
      <div class="stat-item">
        <span class="stat-num">{{ totalPending }}</span>
        <span class="stat-label">待结单数</span>
      </div>
      <div class="stat-item">
        <span class="stat-num" style="color:#e6a23c">¥{{ totalPendingAmount.toFixed(0) }}</span>
        <span class="stat-label">待结金额</span>
      </div>
      <div class="stat-item">
        <span class="stat-num" style="color:#67c23a">¥{{ todaySettledAmount.toFixed(0) }}</span>
            <span class="stat-label">今日已结</span>
      </div>
      <div class="stat-item">
        <span class="stat-num">{{ todaySettledCustomers }}</span>
        <span class="stat-label">已结客数</span>
      </div>
      <div class="stat-item">
        <span class="stat-num">{{ todayPendingCustomers }}</span>
        <span class="stat-label">待结客数</span>
      </div>
      <div class="stat-item">
        <span class="stat-num">{{ pendingWarningCount }}</span>
        <span class="stat-label">问题提醒</span>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="chk-filters">
      <el-radio-group v-model="dateFilter" size="small">
        <el-radio-button value="today">今天</el-radio-button>
        <el-radio-button value="week">本周</el-radio-button>
        <el-radio-button value="all">全部</el-radio-button>
      </el-radio-group>
      <el-input v-model="keyword" placeholder="会员姓名/单号" clearable size="small" style="width:200px" />
      <span style="font-size:12px;color:#909399;margin-left:auto">{{ vipGroups.length }} 位会员，{{ vipOrdersCount }} 单</span>
    </div>

    <!-- VIP 分组卡片 -->
    <div v-if="loading" style="text-align:center;padding:30px;color:#909399">加载中...</div>
    <template v-else>
      <div v-if="!vipGroups.length" style="padding:60px;text-align:center;color:#c0c4cc;font-size:14px">暂无待结账挂单</div>
      <div v-for="group in vipGroups" :key="group.vipuuid" class="vip-card">
        <div class="vip-card-header">
          <div class="vip-card-left">
          <el-checkbox :model-value="allOrdersSelected(group)" :indeterminate="headerIndeterminate(group)" size="small" style="margin-right:4px" @change="(v:any) => toggleAllOrders(group, v)" />
            <span class="vip-card-name">👤 {{ group.vname || group.vcode || '--' }}</span>
            <span class="vip-card-code">{{ group.vcode }}</span>
            <el-button text type="primary" size="small" @click.stop="vipProfile.showProfile(group.vipuuid)" style="padding:0 4px;font-size:11px">查看详情</el-button>
          </div>
          <div class="vip-card-right">
            <span class="vip-card-orders">{{ groupSelectedCount(group) }}/{{ group.orders.length }} 单</span>
            <span class="vip-card-total">¥{{ groupSelectedAmount(group).toFixed(0) }}</span>
          </div>
        </div>
        <div class="vip-card-body">
          <div v-for="o in group.orders" :key="o.uuid" class="order-row" :class="{ 'order-stale': isStale(o) }">
          <el-checkbox v-model="orderSelections[o.uuid]" size="small" style="margin-right:4px;flex-shrink:0" />
            <div class="order-row-left">
              <div class="order-no">{{ o.exptxserno }}</div>
              <div class="order-date">{{ fmtDate(o.vsdate) }}</div>
              <div class="order-items">
                <span v-for="(it, ii) in o.item_details" :key="ii" class="order-item-tag">
                  {{ shortName(it.name) }}
                </span>
              </div>
            </div>
            <div class="order-row-right">
              <div class="order-amount">¥{{ (o.totmount || 0).toFixed(0) }}</div>
              <div v-if="o.paycode" class="order-card">{{ o.paycode }}</div>
              <div class="order-warnings">
                <el-tag v-if="hasEmpIssues(o)" size="small" type="warning">缺员工</el-tag>
                <el-tag v-if="isStale(o)" size="small" type="danger">遗留单</el-tag>
              </div>
            </div>
          </div>
        </div>
       <div class="vip-card-footer">
          <el-button v-if="groupCanQuickCheckout(group)" size="small" type="primary" :loading="quickCheckoutLoading === group.vipuuid" @click="quickCheckout(group)">一键结账</el-button>
          <el-button size="small" text type="primary" @click="toggleCheckoutPanel(group)">审核结账</el-button>
       </div>
      </div>
    </template>

    <!-- 审核结账弹窗 -->
    <el-dialog v-model="auditVisible" title="审核结账" width="780px" :close-on-click-modal="false" top="3vh" destroy-on-close>
      <template v-if="auditGroup">
        <div style="margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:linear-gradient(135deg,#f0f9ff,#e6f7ff);border-radius:8px">
          <div><span style="font-size:15px;font-weight:600">👤 {{ auditGroup.vname }}</span><span style="color:#909399;margin-left:8px">{{ auditGroup.vcode }}</span><el-button text type="primary" size="small" @click.stop="vipProfile.showProfile(auditGroup.vipuuid)" style="padding:0 4px;font-size:11px;margin-left:6px">查看详情</el-button></div>
          <div><span style="font-size:13px;color:#606266">{{ auditGroup.orders.length }} 单，</span><span style="font-size:16px;font-weight:700;color:#e6a23c">¥{{ auditGroup.totalAmount.toFixed(0) }}</span></div>
        </div>

        <div v-for="o in auditGroup.orders" :key="o.uuid" class="audit-order-card">
          <div class="audit-order-header">
            <span class="ao-serno">{{ o.exptxserno }}</span>
            <span class="ao-date">{{ fmtDate(o.vsdate) }}</span>
            <span class="ao-amount">¥{{ (o.totmount || 0).toFixed(2) }}</span>
            <el-tag v-if="isStale(o)" size="small" type="danger">遗留单</el-tag>
          </div>
          <div class="audit-items">
            <div class="audit-items-header">
              <span style="flex:1.5">项目</span><span style="width:44px;text-align:center">数量</span><span style="width:64px;text-align:right">单价</span>
              <span style="width:56px;text-align:center">折扣</span><span style="width:62px;text-align:right">金额</span>
              <span style="width:40px;text-align:center">赠送</span><span style="width:90px;text-align:center">员工</span>
            </div>
            <div v-for="(d, di) in o.item_details" :key="di" class="audit-item-row" :class="{ 'emp-missing': !d.pmcode && !d.asscode1 && !d.asscode2 }">
              <span style="flex:1.5;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ (d.ttypename ? d.ttypename + '-' : '') + d.name }}</span>
              <span style="width:44px;text-align:center">×{{ Number(d.qty).toFixed(0) }}</span>
              <span style="width:64px;text-align:right">¥{{ Number(d.price).toFixed(2) }}</span>
              <span style="width:56px;text-align:center">
                <el-input-number v-model="d.secdisc" :min="0" :max="1" :step="0.05" size="small" :controls="false" style="width:50px"
                  :formatter="(v:any) => Math.round((v||1)*100)+'%'" :parser="(v:any) => parseInt(String(v).replace('%',''))/100" />
              </span>
              <span style="width:62px;text-align:right;font-weight:500">¥{{ Number(d.subtotal || d.price * d.qty * (d.secdisc||1)).toFixed(2) }}</span>
              <span style="width:40px;text-align:center">
                <el-checkbox v-model="d.stype" true-value="P" false-value="N" @change="(v:any) => d.stype = v ? 'P' : 'N'" />
              </span>
              <span style="width:90px;text-align:center">
                <el-select v-model="d.pmcode" size="small" style="width:80px" filterable clearable placeholder="员工">
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
              </span>
            </div>
          </div>
          <div class="audit-payment">
            <span style="font-weight:500;font-size:12px;color:#606266">付款方式：</span>
            <template v-for="(sp, si) in auditSplits[o.uuid]" :key="si">
              <div class="audit-split-chip">
                <el-select v-model="sp.pcode" size="small" style="width:110px" filterable @change="(v:any) => onAuditSplitMethodChange(o, si)">
                  <el-option v-for="pm in auditSplitOptions(o, sp)" :key="pm.value" :label="pm.label" :value="pm.value" />
                </el-select>
                <el-input-number v-model="sp.amount" :min="0" :max="sp.cardBalance || (o.totmount||0)" size="small" :controls="false" :precision="2" style="width:100px" :step="0.01" @change="(v:any) => onAuditSplitAmountChange(o, si)" />
                <span style="font-size:10px;color:#909399">元</span>
                <el-button v-if="!sp._default" text type="danger" size="small" :disabled="auditSplits[o.uuid].length <= 1" @click="removeAuditSplit(o, si)" style="padding:0">✕</el-button>
                <span v-if="sp._default" style="font-size:10px;color:#c0c4cc">(默认)</span>
              </div>
            </template>
            <el-button size="small" text type="primary" @click="addAuditSplit(o)" style="font-size:11px;padding:0 4px">+ 添加</el-button>
            <span style="margin-left:auto;font-size:11px;color:#909399">剩余: <b :style="{color:auditSplitRemaining(o) <= 0.01 ? '#67c23a' : '#f56c6c'}">¥{{ auditSplitRemaining(o).toFixed(2) }}</b></span>
          </div>
        </div>

        <!-- 待处理问题 -->
        <div v-if="auditIssues.length" class="audit-issues">
          <div style="font-size:12px;font-weight:600;color:#e6a23c;margin-bottom:4px">⚠️ 待处理问题</div>
          <div v-for="(issue, ii) in auditIssues" :key="ii" style="font-size:12px;color:#606266;padding:3px 0;border-bottom:1px solid #f5f5f5">
            {{ issue }}
          </div>
        </div>

        <div class="audit-footer">
          <span style="font-size:13px;color:#606266">🔑 收银员：👤 {{ auditCashierName }}（{{ auditCashier }}）</span>
          <el-button text type="primary" size="small" @click="showAuditCashierPicker = true">切换</el-button>
        </div>
      </template>
      <template #footer>
        <el-button size="default" @click="auditVisible = false">取消</el-button>
        <el-button size="default" type="primary" :loading="auditSubmitting" @click="confirmAudit">✅ 确认结账</el-button>
      </template>
    </el-dialog>

    <VipProfileDrawer :profile="vipProfile" :employees="employees" />

    <!-- 切换收银员弹窗 -->
    <el-dialog v-model="showAuditCashierPicker" title="选择收银员" width="400px" :close-on-click-modal="false">
      <div style="margin-bottom:10px">
        <el-input v-model="auditCashierSearchKw" placeholder="输入工号或姓名搜索" clearable @keyup.enter="searchAuditCashier" @clear="auditCashierSearchRes=[]">
          <template #append><el-button @click="searchAuditCashier" :loading="auditCashierSearching">搜索</el-button></template>
        </el-input>
      </div>
      <div v-if="auditCashierSearchRes.length" style="border:1px solid #ebeef5;border-radius:6px;max-height:300px;overflow-y:auto">
        <div v-for="u in auditCashierSearchRes" :key="u.uuid" class="cashier-result-item"
          :style="{background: auditCashier === u.sys_userid ? '#ecf5ff' : 'transparent'}" @click="selectAuditCashier(u)">
          <span style="font-size:14px;font-weight:500">{{ u.sys_fullname || u.sys_userid }}</span>
          <span style="font-size:12px;color:#909399;margin-left:6px">{{ u.sys_userid }}</span>
          <el-tag v-if="auditCashier === u.sys_userid" size="small" type="success" style="margin-left:auto">当前</el-tag>
        </div>
      </div>
      <el-empty v-if="!auditCashierSearching && auditCashierSearchKw && !auditCashierSearchRes.length" description="未找到匹配的用户" :image-size="50" />
      <template #footer><el-button size="default" @click="showAuditCashierPicker = false">取消</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useVipProfile } from '@/composables/useVipProfile'
import VipProfileDrawer from '@/components/VipProfileDrawer.vue'
import request from '@/api/request'
import { ElMessage, ElDrawer } from 'element-plus'
import { useAppStore } from '@/store/app'

const company = localStorage.getItem('genesis_pc_company') || ''
const storecode = localStorage.getItem('genesis_pc_storecode') || ''

// ── 数据 ──
const loading = ref(false)
const vipProfile = useVipProfile()
const orderSelections = ref<Record<string, boolean>>({})
const todaySettledOrders = ref<any[]>([])
const orders = ref<any[]>([])
const employees = ref<{ecode:string;ename:string}[]>([])
const keyword = ref('')
const dateFilter = ref('all')

// ── 筛选 ──
const dateFrom = computed(() => {
  if (dateFilter.value === 'today') {
    const d = new Date(); return '' + d.getFullYear() + String(d.getMonth()+1).padStart(2,'0') + String(d.getDate()).padStart(2,'0')
  }
  if (dateFilter.value === 'week') {
    const d = new Date(); d.setDate(d.getDate() - d.getDay()); return '' + d.getFullYear() + String(d.getMonth()+1).padStart(2,'0') + String(d.getDate()).padStart(2,'0')
  }
  return ''
})

// ── 分组 ──
interface VipGroup { vipuuid: string; vcode: string; vname: string; orders: any[]; totalAmount: number }
const vipGroups = computed(() => {
  let list = orders.value
  const kw = keyword.value.trim().toLowerCase()
  if (kw) list = list.filter((o:any) => (o.vname||'').toLowerCase().includes(kw) || (o.vcode||'').toLowerCase().includes(kw) || (o.exptxserno||'').toLowerCase().includes(kw))
  if (dateFrom.value) list = list.filter((o:any) => (o.vsdate||'') >= dateFrom.value)
  const map = new Map<string, any[]>()
  for (const o of list) {
    const key = o.vipuuid || o.vcode || 'unknown'
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(o)
  }
  const groups: VipGroup[] = []
  for (const [key, olist] of map) {
    const first = olist[0]
    groups.push({
      vipuuid: key, vcode: first.vcode || '', vname: first.vname || '',
      orders: olist.sort((a:any,b:any) => (b.vsdate||'').localeCompare(a.vsdate||'')),
      totalAmount: olist.reduce((s:number,o:any) => s + (o.totmount||0), 0),
    })
  }
  return groups.sort((a,b) => b.totalAmount - a.totalAmount)
})

const totalPending = computed(() => vipGroups.value.reduce((s,g) => s + g.orders.length, 0))
const totalPendingAmount = computed(() => vipGroups.value.reduce((s,g) => s + g.totalAmount, 0))
const vipOrdersCount = computed(() => orders.value.length)
const pendingWarningCount = computed(() => {
  let c = 0
  for (const g of vipGroups.value) for (const o of g.orders) { if (hasEmpIssues(o)) c++; if (isStale(o)) c++ }
  return c
})


function shortName(n: string) { return (n||'').length > 6 ? (n||'').slice(0,6)+'…' : n||'' }
function fmtDate(d: string) { return d ? d.slice(0,4)+'/'+d.slice(4,6)+'/'+d.slice(6,8) : '' }
function isStale(o: any) { const d = o.vsdate||''; return d.length === 8 && d < date7daysAgo() }
function date7daysAgo() { const d = new Date(); d.setDate(d.getDate()-7); return '' + d.getFullYear() + String(d.getMonth()+1).padStart(2,'0') + String(d.getDate()).padStart(2,'0') }
function hasEmpIssues(o: any): boolean {
  if (!o.item_details?.length) return false
  return o.item_details.some((it:any) => !it.pmcode && !it.asscode1 && !it.asscode2)
}

// ── 加载 ──

const todaySettledAmount = computed(() => 
  todaySettledOrders.value.reduce((s: number, o: any) => s + (o.totmount || 0), 0)
)
const todaySettledCustomers = computed(() => {
  const vipSet = new Set(todaySettledOrders.value.map((o: any) => o.vipuuid || o.vcode))
  return vipSet.size
})
const todayPendingCustomers = computed(() => {
  const today = todayStr()
  const todayPending = orders.value.filter((o: any) => (o.vsdate || '') >= today)
  const vipSet = new Set(todayPending.map((o: any) => o.vipuuid || o.vcode))
  return vipSet.size
})

function todayStr() {
  const d = new Date()
  return '' + d.getFullYear() + String(d.getMonth()+1).padStart(2,'0') + String(d.getDate()).padStart(2,'0')
}

async function loadTodaySettled() {
  const today = todayStr()
  try {
    const res = await request.get('/adviser/get_hung_list/', { params: { company, storecode, psstatus: '70', vsdate_from: today, vsdate_to: today } })
    todaySettledOrders.value = Array.isArray(res.data) ? res.data : []
  } catch { todaySettledOrders.value = [] }
}

async function loadOrders() {
  loading.value = true
  try {
    const res = await request.get('/adviser/get_hung_list/', { params: { company, storecode } })
    orders.value = Array.isArray(res.data) ? res.data : []
    const sel: Record<string, boolean> = {}; for (const o of orders.value) sel[o.uuid] = false; orderSelections.value = sel
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

const quickCheckoutLoading = ref('')

const allOrdersSelected = (group: VipGroup) => group.orders.every((o: any) => orderSelections.value[o.uuid])
const headerIndeterminate = (group: VipGroup) => {
  const sel = group.orders.filter((o: any) => orderSelections.value[o.uuid])
  return sel.length > 0 && sel.length < group.orders.length
}
const groupSelectedOrders = (group: VipGroup) => group.orders.filter((o: any) => orderSelections.value[o.uuid])
const groupSelectedCount = (group: VipGroup) => groupSelectedOrders(group).length
const groupSelectedAmount = (group: VipGroup) => groupSelectedOrders(group).reduce((s: number, o: any) => s + (o.totmount || 0), 0)
function toggleAllOrders(group: VipGroup, val: boolean) {
  for (const o of group.orders) orderSelections.value[o.uuid] = val
}

function groupCanQuickCheckout(group: VipGroup): boolean {
  const selected = groupSelectedOrders(group)
  if (selected.length === 0) return false
  for (const o of selected) {
    if (hasEmpIssues(o)) return false
  }
  return true
}

async function quickCheckout(group: VipGroup) {
  quickCheckoutLoading.value = group.vipuuid
  try {
    const [cardRes, pmRes] = await Promise.all([
      request.get('/adviser/get_vip_cardlist/', { params: { company, vipuuid: group.vipuuid } }),
      request.get('/cashier/payment_methods/', { params: { company } }),
    ])
    const cards = Array.isArray(cardRes.data) ? cardRes.data : cardRes.data?.cards ?? []
    const paymodes = pmRes.data?.paymodes || []
    const defPcode = (pmRes.data?.defaults || {}).normal_pcode || ''
    const splits: Record<string, any[]> = {}
    for (const o of group.orders) {
      const total = o.totmount || 0; const sps: any[] = []
      if (o.paycode) {
        const card = cards.find((c: any) => c.ccode === o.paycode)
        const bal = parseFloat(card?.leftmoney || 0)
        const pm = paymodes.find((pm: any) => pm.pcode === o.paytype)
        const pcode = (o.paytype && pm) ? o.paytype : defPcode
        sps.push({ pcode, ccode: o.paycode, amount: Math.min(total, bal) })
      }
      const r = total - sps.reduce((s: number, sp: any) => s + sp.amount, 0)
      if (r > 0.01 || sps.length === 0) sps.push({ pcode: defPcode, ccode: '', amount: Math.round(r * 100) / 100 })
      splits[o.uuid] = sps
    }
    const res = await request.post('/cashier/batch_checkout/', {
      company, storecode, cashier: auditCashier.value, uuids: groupSelectedOrders(group).map((o: any) => o.uuid), splits,
    })
    if (res.data?.ok) { ElMessage.success('结账完成：' + (res.data.success || 0) + ' 单'); loadOrders() }
    else ElMessage.error(res.data?.message || '结账失败')
  } catch (err: any) { ElMessage.error('结账失败: ' + (err?.message || '')) }
  finally { quickCheckoutLoading.value = '' }
}


// ── 审核弹窗 ──
const auditVisible = ref(false)
const auditGroup = ref<VipGroup | null>(null)
const auditSplits = ref<Record<string, any[]>>({})
const auditCards = ref<any[]>([])
const auditPaymodes = ref<any[]>([])
const auditPaymodeDefaults = ref<Record<string,string>>({})
const auditSubmitting = ref(false)
const appStore = useAppStore()
const auditCashier = ref(localStorage.getItem('genesis_pc_cashier_code') || appStore.ecode || '')
const auditCashierName = ref(localStorage.getItem('genesis_pc_cashier_name') || appStore.fullname || '')
const showAuditCashierPicker = ref(false)
const auditCashierSearchKw = ref('')
const auditCashierSearchRes = ref<any[]>([])
const auditCashierSearching = ref(false)



function auditCardBalance(o: any): number | null {
  if (!o.paycode) return null
  const card = auditCards.value.find((c:any) => c.ccode === o.paycode)
  return card ? parseFloat(card.leftmoney || 0) : null
}

function getOrderAuditCardPayAmt(o: any): number {
  const sps = auditSplits.value[o.uuid] || []
  const cardSplit = sps.find((sp: any) => sp._isCard || sp.ccode)
  return cardSplit ? (cardSplit.amount || 0) : 0
}

const auditIssues = computed(() => {
  const issues: string[] = []
  if (!auditGroup.value) return issues
  const _s = auditSplits.value  // 使 computed 对付款拆分变更响应
  for (const o of auditGroup.value.orders) {
    if (hasEmpIssues(o)) issues.push(`${o.exptxserno}：部分项目未分配员工`)
    if (isStale(o)) issues.push(`${o.exptxserno}：该单已超过 7 天`)
    const bal = auditCardBalance(o)
    const cardPayAmt = getOrderAuditCardPayAmt(o)
    if (bal !== null && bal < cardPayAmt) {
      issues.push(`${o.exptxserno}：付款卡余额 ¥${bal.toFixed(0)}，卡需付 ¥${cardPayAmt.toFixed(2)}，差 ¥${(cardPayAmt - bal).toFixed(2)}`)
    }
  }
  return issues
})

function initAuditSplitsForOrder(o: any) {
  const total = o.totmount || 0; const sps: any[] = []
  const defPcode = auditPaymodeDefaults.value?.normal_pcode || ''
  if (o.paycode) {
    const card = auditCards.value.find((c:any) => c.ccode === o.paycode)
    const bal = parseFloat(card?.leftmoney || 0)
    const cardPcode = (o.paytype && auditPaymodes.value.find((pm:any) => pm.pcode === o.paytype)) ? o.paytype : defPcode
    sps.push({ pcode: cardPcode, ccode: o.paycode, amount: Math.min(total, bal), cardBalance: bal, _isCard: true })
  }
  const r = total - sps.reduce((s:number,sp:any) => s+sp.amount,0)
  if (r > 0.01 || sps.length === 0) sps.push({ pcode: defPcode, ccode: '', amount: Math.round(r*100)/100, _default: true })
  return sps
}

async function toggleCheckoutPanel(group: VipGroup) {
  auditGroup.value = {...group, orders: groupSelectedOrders(group)}
  auditVisible.value = true
  const vipuuid = group.vipuuid
  // Load cards + paymodes
  try {
    const [cardRes, pmRes] = await Promise.all([
      request.get('/adviser/get_vip_cardlist/', { params: { company, vipuuid } }),
      request.get('/cashier/payment_methods/', { params: { company } }),
    ])
    const cardList = Array.isArray(cardRes.data) ? cardRes.data : cardRes.data?.cards ?? []
    auditCards.value = cardList.map((c:any) => ({ ccode: c.ccode||'', cardname: c.cardname||'', comptype: c.comptype||'', leftmoney: c.leftmoney||0, leftqty: c.leftqty||0 }))
    auditPaymodes.value = pmRes.data?.paymodes || []
    auditPaymodeDefaults.value = pmRes.data?.defaults || {}
  } catch { auditCards.value = []; auditPaymodes.value = [] }
  // Init splits
  auditSplits.value = {}
  for (const o of group.orders) auditSplits.value[o.uuid] = initAuditSplitsForOrder(o)
}

function auditSplitOptions(o: any, currentSp: any) {
  const opts: {label:string;value:string;isCard?:boolean;balance?:number}[] = []
  for (const pm of auditPaymodes.value) opts.push({ label: (pm.iscash==='0'?'💳':pm.iscash==='1'?'💵':'🎁')+' '+pm.pname, value: pm.pcode })
  for (const c of auditCards.value) {
    if (!opts.some((x:any) => x.value === c.ccode)) {
      const bal = c.comptype === 'times' ? parseFloat(c.leftqty||0) : parseFloat(c.leftmoney||0)
      opts.push({ label: '💳 '+(c.cardname||c.ccode)+' (余额¥'+bal.toFixed(0)+')', value: c.ccode, isCard: true, balance: bal })
    }
  }
  const sps = auditSplits.value[o.uuid] || []
  const used = new Set(sps.map((s:any) => s.pcode))
  return opts.filter((opt:any) => !used.has(opt.value) || opt.value === currentSp.pcode)
}

function auditSplitRemaining(o: any) {
  const sps = auditSplits.value[o.uuid]
  if (!sps) return (o.totmount||0)
  return (o.totmount||0) - sps.reduce((s:number,sp:any) => s+(sp.amount||0),0)
}

function addAuditSplit(o: any) {
  const sps = auditSplits.value[o.uuid]; if (!sps) return
  const used = new Set(sps.map((s:any) => s.pcode))
  const firstAvail = auditSplitOptions(o, sps[0]).find((opt:any) => !used.has(opt.value) && opt.value !== '')
  if (!firstAvail) return
  const di = sps.findIndex((s:any) => s._default)
  const amt = di >= 0 ? Math.min(sps[di].amount, o.totmount||0) : 0
  sps.splice(di >= 0 ? di : sps.length, 0, { pcode: firstAvail.value, ccode: firstAvail.isCard ? firstAvail.value : '', amount: amt, cardBalance: firstAvail.balance, _isCard: !!firstAvail.isCard })
  if (di >= 0) sps[sps.length-1].amount = Math.max(0, (o.totmount||0) - sps.reduce((s:number,sp2:any,i:number) => s+(i !== sps.length-1 ? sp2.amount : 0),0))
}

function removeAuditSplit(o: any, si: number) {
  const sps = auditSplits.value[o.uuid]
  if (!sps || si >= sps.length || sps.length <= 1) return
  sps.splice(si, 1)
  rebalanceAuditSplits(o)
}
function rebalanceAuditSplits(o: any) {
  const sps = auditSplits.value[o.uuid]
  if (!sps || !sps.length) return
  const total = o.totmount || 0
  const paid = sps.reduce((s: number, sp: any) => s + (sp.amount || 0), 0)
  const diff = paid - total
  if (diff > 0.01) {
    ElMessage.warning('多付了※实际应付 ¥' + total.toFixed(2))
    for (let i = sps.length - 1; i >= 0; i--) {
      if (!sps[i]._default) {
        sps[i].amount = Math.max(0, Math.round((sps[i].amount - diff) * 100) / 100)
        break
      }
    }
  } else if (diff < -0.01) {
    const def = sps.find((sp: any) => sp._default)
    if (def) {
      def.amount = Math.max(0, Math.round((total - (paid - (def.amount || 0))) * 100) / 100)
    } else {
      const dPcode = auditPaymodeDefaults.value?.normal_pcode || ''
      sps.push({ pcode: dPcode, ccode: '', amount: Math.round(-diff * 100) / 100, _default: true })
    }
    // 不足部分自动用默认付款方式补齐，提示用户核对
    const filledPcode = sps.find((sp: any) => sp._default)?.pcode || auditPaymodeDefaults.value?.normal_pcode || ''
    const filledPm = auditPaymodes.value.find((pm: any) => pm.pcode === filledPcode)
    const pmName = filledPm ? filledPm.pname : filledPcode
    ElMessage.warning('不足部分已用「' + pmName + '」补齐，请注意核对')
  }
}

function onAuditSplitAmountChange(o: any, si: number) {
  const sps = auditSplits.value[o.uuid]
  if (!sps || si >= sps.length) return
  const sp = sps[si]
  if (sp._isCard && sp.cardBalance && sp.amount > sp.cardBalance) sp.amount = sp.cardBalance
  if (sp.amount < 0) sp.amount = 0
  rebalanceAuditSplits(o)
}

function onAuditSplitMethodChange(o: any, si: number) {
  const sps = auditSplits.value[o.uuid]
  if (!sps || si >= sps.length) return
  const sp = sps[si]
  const card = auditCards.value.find((c: any) => c.ccode === sp.pcode)
  if (card) {
    sp.ccode = sp.pcode
    sp._isCard = true
    sp.cardBalance = parseFloat(card.leftmoney || 0)
  } else {
    sp.ccode = ''
    sp._isCard = false
    sp.cardBalance = undefined
  }
}


function searchAuditCashier() {
  const kw = auditCashierSearchKw.value.trim()
  if (!kw) return
  auditCashierSearching.value = true
  request.get('/adviser/search_user/', { params: { company, keyword: kw } })
    .then(r => { auditCashierSearchRes.value = Array.isArray(r.data) ? r.data : [] })
    .catch(() => { auditCashierSearchRes.value = [] })
    .finally(() => { auditCashierSearching.value = false })
}

function selectAuditCashier(u: any) {
  auditCashier.value = u.sys_userid || ''
  auditCashierName.value = u.sys_fullname || u.sys_userid || ''
  showAuditCashierPicker.value = false
  auditCashierSearchRes.value = []; auditCashierSearchKw.value = ''
}



async function confirmAudit() {
  if (!auditGroup.value) return
  auditSubmitting.value = true
  const uuids = auditGroup.value.orders.map((o:any) => o.uuid)
  const splits: Record<string, any[]> = {}
  for (const uuid of uuids) {
    const sp = auditSplits.value[uuid]
    if (sp?.length) splits[uuid] = sp.map((s:any) => ({ pcode: s.pcode, ccode: s.ccode||'', amount: s.amount }))
  }
  try {
    const res = await request.post('/cashier/batch_checkout/', {
      company, storecode, cashier: auditCashier.value, uuids, splits,
    })
    if (res.data?.ok) {
      ElMessage.success(`结账完成：${res.data.success || 0} 单`)
      auditVisible.value = false; loadOrders()
    } else ElMessage.error(res.data?.message || '结账失败')
  } catch (err:any) { ElMessage.error('结账失败: '+(err?.message||'')) }
  finally { auditSubmitting.value = false }
}

loadOrders(); loadEmployees(); loadTodaySettled()
</script>

<style scoped>
.chk-page { display:flex; flex-direction:column; gap:8px; height:100%; }
.chk-stats { display:flex; gap:16px; padding:10px 14px; background:#fff; border-radius:8px; border:1px solid #ebeef5; flex-shrink:0; }
.stat-item { display:flex; flex-direction:column; align-items:center; flex:1; border-right:1px solid #f0f0f0; }
.stat-item:last-child { border-right:none; }
.stat-num { font-size:22px; font-weight:700; color:#303133; }
.stat-label { font-size:11px; color:#909399; margin-top:2px; }
.chk-filters { display:flex; align-items:center; gap:10px; flex-shrink:0; }
.vip-card { background:#fff; border:1px solid #ebeef5; border-radius:8px; margin-bottom:6px; overflow:hidden; }
.vip-card-header { display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:#fafafa; border-bottom:1px solid #ebeef5; }
.vip-card-left { display:flex; align-items:center; gap:6px; }
.vip-card-name { font-size:14px; font-weight:600; color:#303133; }
.vip-card-code { font-size:11px; color:#909399; }
.vip-card-right { display:flex; align-items:center; gap:10px; }
.vip-card-orders { font-size:12px; color:#909399; }
.vip-card-body { padding:4px 12px; }
.order-row { display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #f5f5f5; }
.order-row:last-child { border-bottom:none; }
.order-row.order-stale { background:#fef7e0; margin:0 -12px; padding:6px 12px; }
.order-row-left { flex:1; min-width:0; }
.order-no { font-family:monospace; font-size:11px; color:#303133; }
.order-date { font-size:10px; color:#c0c4cc; }
.order-items { display:flex; gap:3px; flex-wrap:wrap; margin-top:2px; }
.order-item-tag { font-size:10px; color:#606266; background:#f5f7fa; padding:0 4px; border-radius:3px; }
.order-row-right { text-align:right; flex-shrink:0; }
.order-amount { font-size:14px; font-weight:600; color:#e6a23c; }
.order-card { font-size:10px; color:#409eff; }
.order-warnings { display:flex; gap:2px; justify-content:flex-end; margin-top:2px; }
.vip-card-footer { display:flex; justify-content:flex-end; gap:6px; padding:6px 12px; border-top:1px solid #f0f0f0; }

/* 审核弹窗 */
.audit-order-card { border:1px solid #ebeef5; border-radius:6px; margin-bottom:8px; overflow:hidden; }
.audit-order-header { display:flex; align-items:center; gap:8px; padding:6px 10px; background:#fafafa; border-bottom:1px solid #ebeef5; font-size:12px; }
.ao-serno { font-family:monospace; font-weight:600; }
.ao-date { color:#909399; }
.ao-amount { margin-left:auto; font-weight:600; color:#e6a23c; }
.audit-items { padding:4px 10px; font-size:12px; }
.audit-items-header { display:flex; align-items:center; gap:4px; padding:3px 0; color:#909399; font-weight:500; border-bottom:1px solid #ebeef5; }
.audit-item-row { display:flex; align-items:center; gap:4px; padding:3px 0; border-bottom:1px solid #f5f5f5; }
.audit-item-row.emp-missing { background:#fef0f0; margin:0 -10px; padding:3px 10px; }
.audit-payment { display:flex; align-items:center; gap:4px; flex-wrap:wrap; padding:6px 10px; background:#f8f8f8; border-top:1px solid #ebeef5; font-size:12px; }
.audit-split-chip { display:inline-flex; align-items:center; gap:2px; padding:2px 4px; background:#fff; border:1px solid #ebeef5; border-radius:4px; }
.audit-issues { border:1px solid #fef0f0; border-radius:6px; padding:8px 10px; margin:8px 0; background:#fef7e0; }
.audit-footer { display:flex; align-items:center; gap:6px; margin-top:10px; padding:8px 10px; background:#fafafa; border-radius:6px; font-size:12px; }
.cashier-result-item { display:flex; align-items:center; padding:8px 10px; border-bottom:1px solid #f5f5f5; cursor:pointer; border-radius:4px; }
.cashier-result-item:hover { background:#ecf5ff; }
:deep(.el-dialog__body) { padding:14px 18px; }
:deep(.el-input-number .el-input__inner) { height:26px; font-size:12px; }
:deep(.el-select .el-input__inner) { height:26px; font-size:12px; }
</style>
