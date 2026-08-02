<template>
  <div class="chk-page">
    <!-- 顶栏：关键数字 + 日期筛选 -->
    <div class="chk-top">
      <div class="chk-top-stats">
        <span class="top-stat"><b>{{ totalPending }}</b> 待结单</span>
        <span class="top-stat accent"><b>¥{{ totalPendingAmount.toFixed(2) }}</b> 待结</span>
        <span v-if="pendingWarningCount" class="top-stat warn"><b>{{ pendingWarningCount }}</b> 需注意</span>
        <span class="top-stat muted">今日已结 ¥{{ todaySettledAmount.toFixed(2) }} · {{ todaySettledCustomers }} 客</span>
      </div>
      <el-radio-group v-model="dateFilter" size="default">
        <el-radio-button value="today">今天</el-radio-button>
        <el-radio-button value="week">本周</el-radio-button>
        <el-radio-button value="all">全部</el-radio-button>
      </el-radio-group>
    </div>

    <div class="chk-body" v-loading="loading">
      <!-- 左：待结会员队列 -->
      <aside class="chk-queue">
        <el-input
          v-model="keyword"
          placeholder="搜会员姓名 / 手机 / 单号"
          clearable
          size="large"
          class="queue-search"
        />
        <div class="queue-meta">{{ vipGroups.length }} 位待结 · {{ queueDateGroups.length }} 天</div>
        <div v-if="!loading && !queueDateGroups.length" class="queue-empty">暂无待结账挂单</div>
        <div class="queue-list">
          <div v-for="dg in queueDateGroups" :key="dg.date" class="queue-date-block">
            <div class="queue-date-head">
              <span class="queue-date-label">{{ dg.label }}</span>
              <span class="queue-date-meta">{{ dg.items.length }} 人 · {{ dg.orderCount }} 单 · ¥{{ dg.totalAmount.toFixed(2) }}</span>
            </div>
            <div
              v-for="entry in dg.items"
              :key="dg.date + '-' + entry.vipuuid"
              class="queue-item"
              :class="{
                active: selectedVipUuid === entry.vipuuid && selectedFocusDate === entry.date,
                warn: entry.warn,
              }"
              @click="selectQueueEntry(entry)"
            >
              <div class="qi-main">
                <div class="qi-name">
                  {{ entry.vname || entry.vcode || '--' }}
                  <span v-if="entry.warn" class="qi-dot" title="有缺员工或遗留单" />
                  <el-tag v-if="entry.pendingPaycard" size="small" type="warning" effect="plain">卡未生效</el-tag>
                </div>
                <div class="qi-sub">{{ entry.vcode }} · {{ entry.orders.length }} 单</div>
              </div>
              <div class="qi-amount">¥{{ entry.totalAmount.toFixed(2) }}</div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右：当前会员结账区 -->
      <section class="chk-detail">
        <div v-if="!selectedGroup" class="detail-empty">
          <div class="detail-empty-title">请先选择左侧会员</div>
          <div class="detail-empty-desc">搜索或点选待结客人，在此核对明细并结账</div>
        </div>

        <template v-else>
          <div class="detail-header">
            <div class="dh-left">
              <div class="dh-name">{{ selectedGroup.vname || selectedGroup.vcode }}</div>
              <div class="dh-code">
                {{ selectedGroup.vcode }}
                <el-button text type="primary" @click="vipProfile.showProfile(selectedGroup.vipuuid)">会员详情</el-button>
              </div>
            </div>
            <div class="dh-right">
              <div class="dh-amount">¥{{ auditGroupLiveTotal.toFixed(2) }}</div>
              <div class="dh-amount-hint">已选 {{ selectedOrderCount }} / {{ selectedGroup.orders.length }} 单</div>
            </div>
          </div>

          <div class="detail-toolbar">
            <el-checkbox
              :model-value="allOrdersSelected(selectedGroup)"
              :indeterminate="headerIndeterminate(selectedGroup)"
              @change="(v:any) => onToggleAllSelected(selectedGroup, v)"
            >全选本客单据</el-checkbox>
            <span class="toolbar-spacer" />
            <span class="cashier-line">收银员 {{ auditCashierName || auditCashier || '未设置' }}</span>
            <el-button text type="primary" @click="showAuditCashierPicker = true">切换</el-button>
          </div>

          <div v-if="auditIssues.length" class="audit-issues">
            <div class="issues-title">须处理</div>
            <div v-for="(issue, ii) in auditIssues" :key="ii" class="issues-row">{{ issue }}</div>
          </div>
          <div v-if="auditNotices.length" class="audit-notices">
            <div class="notices-title">已自动改现金</div>
            <div v-for="(notice, ni) in auditNotices" :key="ni" class="notices-row">{{ notice }}</div>
          </div>

          <div class="detail-scroll">
            <div v-for="o in selectedGroup.orders" :key="o.uuid" class="audit-order-card" :class="{ off: !orderSelections[o.uuid] }">
              <div class="audit-order-header">
                <el-checkbox v-model="orderSelections[o.uuid]" @change="() => onOrderSelectionChange(selectedGroup)" />
                <span class="ao-serno">{{ o.exptxserno }}</span>
                <span class="ao-date">{{ fmtDate(o.vsdate) }}</span>
                <el-tag v-if="hasEmpIssues(o)" size="small" type="warning" effect="plain">缺员工</el-tag>
                <el-tag v-if="isStale(o)" size="small" type="danger" effect="plain">遗留单</el-tag>
                <template v-if="o.paycode">
                  <span class="ao-paycard">开单付款卡 {{ o.paycode }}</span>
                  <el-tag v-if="originPaycardState(o) === 'pending'" size="small" type="warning" effect="plain">未生效</el-tag>
                  <el-tag v-else-if="originPaycardState(o) === 'missing'" size="small" type="info" effect="plain">不可用</el-tag>
                </template>
                <span class="ao-amount">¥{{ auditOrderTotal(o).toFixed(2) }}</span>
              </div>

              <template v-if="orderSelections[o.uuid]">
                <div class="audit-items">
                  <div class="audit-items-header">
                    <span style="flex:1.4">项目</span>
                    <span style="width:40px;text-align:center">数量</span>
                    <span style="width:58px;text-align:right">单价</span>
                    <span style="width:44px;text-align:center">折扣</span>
                    <span style="width:64px;text-align:right">金额</span>
                    <span style="width:48px;text-align:center">属性</span>
                    <span style="width:96px;text-align:center">{{ empTitles.pmname }}</span>
                    <span style="width:96px;text-align:center">{{ empTitles.secname }}</span>
                    <span style="width:44px;text-align:center" :title="'是否指定' + empTitles.secname">指定</span>
                    <span style="width:96px;text-align:center">{{ empTitles.thrname }}</span>
                  </div>
                  <div
                    v-for="(d, di) in o.item_details"
                    :key="d.uuid || di"
                    class="audit-item-row"
                    :class="{ 'emp-missing': !d.pmcode && !d.asscode1 && !d.asscode2 }"
                  >
                    <span class="ai-name">{{ (d.ttypename ? d.ttypename + '-' : '') + d.name }}</span>
                    <span style="width:40px;text-align:center">×{{ Number(d.qty).toFixed(0) }}</span>
                    <span style="width:58px;text-align:right">¥{{ Number(d.price).toFixed(2) }}</span>
                    <span style="width:44px;text-align:center;color:var(--g-color-text-muted)">{{ Math.round(Number(d.secdisc ?? 1) * 100) }}%</span>
                    <span style="width:64px;text-align:right;font-weight:600">¥{{ auditItemSubtotal(d).toFixed(2) }}</span>
                    <span style="width:48px;text-align:center">
                      <el-tag size="small" effect="plain" :type="d.stype === 'P' ? 'warning' : 'info'">{{ d.stype === 'P' ? '赠送' : '正常' }}</el-tag>
                    </span>
                    <span style="width:96px;text-align:center">
                      <el-select v-model="d.pmcode" size="small" style="width:90px" filterable clearable :placeholder="empTitles.pmname">
                        <el-option label="--" value="" />
                        <el-option v-for="emp in employees" :key="'p-' + emp.ecode" :label="emp.ename" :value="emp.ecode" />
                      </el-select>
                    </span>
                    <span style="width:96px;text-align:center">
                      <el-select v-model="d.asscode1" size="small" style="width:90px" filterable clearable :placeholder="empTitles.secname">
                        <el-option label="--" value="" />
                        <el-option v-for="emp in employees" :key="'s-' + emp.ecode" :label="emp.ename" :value="emp.ecode" />
                      </el-select>
                    </span>
                    <span style="width:44px;text-align:center">
                      <el-checkbox
                        :model-value="d.secoldcustflag === 'Y'"
                        @change="(v: any) => { d.secoldcustflag = v ? 'Y' : 'N' }"
                      />
                    </span>
                    <span style="width:96px;text-align:center">
                      <el-select v-model="d.asscode2" size="small" style="width:90px" filterable clearable :placeholder="empTitles.thrname">
                        <el-option label="--" value="" />
                        <el-option v-for="emp in employees" :key="'t-' + emp.ecode" :label="emp.ename" :value="emp.ecode" />
                      </el-select>
                    </span>
                  </div>
                </div>

                <div v-if="originPaycardFallbackTip(o)" class="pay-fallback-tip">{{ originPaycardFallbackTip(o) }}</div>
                <div class="audit-payment">
                  <span class="pay-label">付款</span>
                  <div v-if="originPaycardUnusable(o)" class="audit-split-chip origin-card-chip">
                    <span class="origin-card-label">原卡 {{ o.paycode }} · 不可用</span>
                  </div>
                  <template v-for="(sp, si) in auditSplits[o.uuid]" :key="si">
                    <div class="audit-split-chip">
                      <el-select v-model="sp.pcode" size="default" style="width:130px" filterable @change="() => onAuditSplitMethodChange(o, si)">
                        <el-option v-for="pm in auditSplitOptions(o, sp)" :key="pm.value" :label="pm.label" :value="pm.value" />
                      </el-select>
                      <span v-if="splitCardNo(sp)" class="pay-ccode">卡号 {{ splitCardNo(sp) }}</span>
                      <el-input-number
                        v-model="sp.amount"
                        :min="0"
                        :max="sp.cardBalance || auditOrderTotal(o)"
                        size="default"
                        :controls="false"
                        :precision="2"
                        style="width:110px"
                        :step="0.01"
                        @change="() => onAuditSplitAmountChange(o, si)"
                      />
                      <span class="pay-unit">元</span>
                      <el-button v-if="!sp._default" text type="danger" :disabled="(auditSplits[o.uuid]?.length || 0) <= 1" @click="removeAuditSplit(o, si)" :icon="Close" />
                      <span v-if="sp._default" class="pay-default">默认</span>
                    </div>
                  </template>
                  <el-button text type="primary" @click="addAuditSplit(o)">+ 拆分</el-button>
                  <span class="pay-remain" :class="{ ok: auditSplitRemaining(o) <= 0.01 }">
                    剩余应补 ¥{{ auditSplitRemaining(o).toFixed(2) }}
                  </span>
                </div>
              </template>
            </div>
          </div>

          <div class="detail-footer">
            <el-button
              v-if="canQuickCheckoutSelected"
              size="large"
              :loading="quickCheckoutLoading === selectedGroup.vipuuid"
              @click="quickCheckout(selectedGroup)"
            >一键结账</el-button>
            <el-button
              type="primary"
              size="large"
              :loading="auditSubmitting"
              :disabled="selectedOrderCount === 0"
              @click="confirmAudit"
            >确认结账 · ¥{{ auditGroupLiveTotal.toFixed(2) }}</el-button>
          </div>
        </template>
      </section>
    </div>

    <VipProfileDrawer :profile="vipProfile" :employees="employees" />

    <el-dialog v-model="showAuditCashierPicker" title="选择收银员" width="400px" :close-on-click-modal="false">
      <div style="margin-bottom:10px">
        <el-input v-model="auditCashierSearchKw" placeholder="输入工号或姓名搜索" clearable @keyup.enter="searchAuditCashier" @clear="auditCashierSearchRes=[]">
          <template #append><el-button @click="searchAuditCashier" :loading="auditCashierSearching">搜索</el-button></template>
        </el-input>
      </div>
      <div v-if="auditCashierSearchRes.length" style="border:1px solid var(--g-color-border);border-radius:6px;max-height:300px;overflow-y:auto">
        <div
          v-for="u in auditCashierSearchRes" :key="u.uuid" class="cashier-result-item"
          :style="{ background: auditCashier === u.sys_userid ? 'var(--g-color-primary-soft)' : 'transparent' }"
          @click="selectAuditCashier(u)"
        >
          <span style="font-size:14px;font-weight:500">{{ u.sys_fullname || u.sys_userid }}</span>
          <span style="font-size:12px;color:var(--g-color-text-muted);margin-left:6px">{{ u.sys_userid }}</span>
          <el-tag v-if="auditCashier === u.sys_userid" size="small" type="success" style="margin-left:auto">当前</el-tag>
        </div>
      </div>
      <el-empty v-if="!auditCashierSearching && auditCashierSearchKw && !auditCashierSearchRes.length" description="未找到匹配的用户" :image-size="50" />
      <template #footer><el-button @click="showAuditCashierPicker = false">取消</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useVipProfile } from '@/composables/useVipProfile'
import VipProfileDrawer from '@/components/VipProfileDrawer.vue'
import request from '@/api/request'
import { getAppoptionBySeg } from '@/api/vip'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/store/app'
import { Close } from '@element-plus/icons-vue'

const company = localStorage.getItem('genesis_pc_company') || ''
const storecode = localStorage.getItem('genesis_pc_storecode') || ''

const loading = ref(false)
const vipProfile = useVipProfile()
const orderSelections = ref<Record<string, boolean>>({})
const todaySettledOrders = ref<any[]>([])
const orders = ref<any[]>([])
const employees = ref<{ ecode: string; ename: string }[]>([])
/** 三位员工角色标题：appoption seg=common 的 pmname/secname/thrname */
const empTitles = ref({ pmname: '开单', secname: '美疗师1', thrname: '美疗师2' })
const keyword = ref('')
// 默认「全部」：昨日遗留挂单（如 vsdate=昨天）在「今天」筛选下会被挡住
const dateFilter = ref('all')
const selectedVipUuid = ref('')
/** 左侧点选时所在日期分组，用于高亮；右栏仍展示该会员筛选范围内全部单据 */
const selectedFocusDate = ref('')

interface VipGroup { vipuuid: string; vcode: string; vname: string; orders: any[]; totalAmount: number; latestDate: string }
interface QueueVipEntry {
  vipuuid: string
  vcode: string
  vname: string
  date: string
  orders: any[]
  totalAmount: number
  warn: boolean
  pendingPaycard: boolean
}
interface QueueDateGroup {
  date: string
  label: string
  items: QueueVipEntry[]
  orderCount: number
  totalAmount: number
}

const dateFrom = computed(() => {
  if (dateFilter.value === 'today') {
    const d = new Date()
    return '' + d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0')
  }
  if (dateFilter.value === 'week') {
    const d = new Date()
    d.setDate(d.getDate() - d.getDay())
    return '' + d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0')
  }
  return ''
})

const vipGroups = computed(() => {
  let list = orders.value
  const kw = keyword.value.trim().toLowerCase()
  if (kw) {
    list = list.filter((o: any) =>
      (o.vname || '').toLowerCase().includes(kw)
      || (o.vcode || '').toLowerCase().includes(kw)
      || (o.mtcode || '').toLowerCase().includes(kw)
      || (o.exptxserno || '').toLowerCase().includes(kw)
    )
  }
  if (dateFrom.value) list = list.filter((o: any) => (o.vsdate || '') >= dateFrom.value)
  const map = new Map<string, any[]>()
  for (const o of list) {
    const key = o.vipuuid || o.vcode || 'unknown'
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(o)
  }
  const groups: VipGroup[] = []
  for (const [key, olist] of map) {
    const first = olist[0]
    const sorted = olist.slice().sort((a: any, b: any) => (b.vsdate || '').localeCompare(a.vsdate || ''))
    groups.push({
      vipuuid: key,
      vcode: first.vcode || '',
      vname: first.vname || '',
      orders: sorted,
      totalAmount: sorted.reduce((s: number, o: any) => s + auditOrderTotal(o), 0),
      latestDate: sorted[0]?.vsdate || '',
    })
  }
  return groups.sort((a, b) => (b.latestDate || '').localeCompare(a.latestDate || '') || b.totalAmount - a.totalAmount)
})

/** 左侧队列：按开单日期分组，最近日期在上；同日内按金额降序 */
const queueDateGroups = computed((): QueueDateGroup[] => {
  let list = orders.value
  const kw = keyword.value.trim().toLowerCase()
  if (kw) {
    list = list.filter((o: any) =>
      (o.vname || '').toLowerCase().includes(kw)
      || (o.vcode || '').toLowerCase().includes(kw)
      || (o.mtcode || '').toLowerCase().includes(kw)
      || (o.exptxserno || '').toLowerCase().includes(kw)
    )
  }
  if (dateFrom.value) list = list.filter((o: any) => (o.vsdate || '') >= dateFrom.value)

  const byDate = new Map<string, Map<string, any[]>>()
  for (const o of list) {
    const date = o.vsdate || ''
    if (!date) continue
    const vipKey = o.vipuuid || o.vcode || 'unknown'
    if (!byDate.has(date)) byDate.set(date, new Map())
    const vipMap = byDate.get(date)!
    if (!vipMap.has(vipKey)) vipMap.set(vipKey, [])
    vipMap.get(vipKey)!.push(o)
  }

  const dates = [...byDate.keys()].sort((a, b) => b.localeCompare(a))
  return dates.map((date) => {
    const vipMap = byDate.get(date)!
    const items: QueueVipEntry[] = [...vipMap.entries()].map(([vipKey, olist]) => {
      const first = olist[0]
      return {
        vipuuid: vipKey,
        vcode: first.vcode || '',
        vname: first.vname || '',
        date,
        orders: olist,
        totalAmount: olist.reduce((s: number, o: any) => s + auditOrderTotal(o), 0),
        warn: olist.some((o: any) => hasEmpIssues(o) || isStale(o)),
        pendingPaycard: olist.some((o: any) => orderHasPendingPaycardOnList(o)),
      }
    }).sort((a, b) => b.totalAmount - a.totalAmount)
    return {
      date,
      label: dateGroupLabel(date),
      items,
      orderCount: items.reduce((s, it) => s + it.orders.length, 0),
      totalAmount: items.reduce((s, it) => s + it.totalAmount, 0),
    }
  })
})

const selectedGroup = computed(() => vipGroups.value.find((g) => g.vipuuid === selectedVipUuid.value) || null)

const totalPending = computed(() => vipGroups.value.reduce((s, g) => s + g.orders.length, 0))
const totalPendingAmount = computed(() => vipGroups.value.reduce((s, g) => s + g.totalAmount, 0))
const pendingWarningCount = computed(() => {
  let c = 0
  for (const g of vipGroups.value) for (const o of g.orders) { if (hasEmpIssues(o) || isStale(o)) c++ }
  return c
})

function fmtDate(d: string) { return d ? d.slice(0, 4) + '/' + d.slice(4, 6) + '/' + d.slice(6, 8) : '' }
function yesterdayStr() {
  const d = new Date(); d.setDate(d.getDate() - 1)
  return '' + d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0')
}
function dateGroupLabel(ymd: string): string {
  if (!ymd) return '未知日期'
  if (ymd === todayStr()) return `今天 ${fmtDate(ymd)}`
  if (ymd === yesterdayStr()) return `昨天 ${fmtDate(ymd)}`
  return fmtDate(ymd)
}
function isStale(o: any) { const d = o.vsdate || ''; return d.length === 8 && d < date7daysAgo() }
function date7daysAgo() {
  const d = new Date(); d.setDate(d.getDate() - 7)
  return '' + d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0')
}
function hasEmpIssues(o: any): boolean {
  if (!o.item_details?.length) return false
  return o.item_details.some((it: any) => !it.pmcode && !it.asscode1 && !it.asscode2)
}
function groupHasWarning(group: VipGroup): boolean {
  return group.orders.some((o: any) => hasEmpIssues(o) || isStale(o))
}
/** 列表阶段：挂单自带的付款卡状态（未加载会员卡列表时用） */
function orderHasPendingPaycardOnList(o: any): boolean {
  const pc = (o?.paycode || '').trim()
  if (!pc) return false
  return (o.paycard_status || '') === 'P'
}

function auditItemSubtotal(d: any): number {
  const price = Number(d?.price || 0)
  const qty = Number(d?.qty || 0)
  const secdisc = Number(d?.secdisc ?? 1)
  const mondisc = Number(d?.mondisc ?? 0)
  return Math.round((price * qty * secdisc - mondisc) * 100) / 100
}
function auditOrderTotal(o: any): number {
  if (Array.isArray(o?.item_details) && o.item_details.length) {
    return Math.round(o.item_details.reduce((s: number, d: any) => s + auditItemSubtotal(d), 0) * 100) / 100
  }
  return Number(o?.totmount || 0)
}
function syncOrderItemSubtotals(o: any) {
  if (!Array.isArray(o?.item_details)) return
  for (const d of o.item_details) d.subtotal = auditItemSubtotal(d)
  o.totmount = auditOrderTotal(o)
}

/** 卡付拆分：展示付款卡号（ccode，或选项值本身就是卡号时） */
function splitCardNo(sp: any): string {
  if (!sp) return ''
  if (sp.ccode) return String(sp.ccode)
  if (sp._isCard && sp.pcode) return String(sp.pcode)
  const card = auditCards.value.find((c: any) => c.ccode === sp.pcode)
  return card?.ccode || ''
}

const todaySettledAmount = computed(() =>
  todaySettledOrders.value.reduce((s: number, o: any) => s + auditOrderTotal(o), 0)
)
const todaySettledCustomers = computed(() => {
  const vipSet = new Set(todaySettledOrders.value.map((o: any) => o.vipuuid || o.vcode))
  return vipSet.size
})
function todayStr() {
  const d = new Date()
  return '' + d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0')
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
    const sel: Record<string, boolean> = {}
    for (const o of orders.value) sel[o.uuid] = orderSelections.value[o.uuid] || false
    orderSelections.value = sel
    if (selectedVipUuid.value && !vipGroups.value.some((g) => g.vipuuid === selectedVipUuid.value)) {
      selectedVipUuid.value = ''
      selectedFocusDate.value = ''
      auditGroup.value = null
      auditSplits.value = {}
    } else if (selectedGroup.value) {
      await preparePaymentContext(selectedGroup.value)
    }
  } catch { orders.value = [] }
  finally { loading.value = false }
}

async function loadEmployees() {
  try {
    const res = await request.get('/adviser/get_bookingable_empllist/', { params: { company, storecode } })
    const list = Array.isArray(res.data) ? res.data : res.data?.results ?? []
    employees.value = list.map((e: any) => ({ ecode: e.ecode || '', ename: e.ename || '' }))
  } catch { employees.value = [] }
}

async function loadEmpTitles() {
  try {
    const res = await getAppoptionBySeg('common')
    const list = Array.isArray(res.data) ? res.data : []
    const map: Record<string, string> = {}
    for (const row of list) {
      if (row?.itemname) map[row.itemname] = (row.itemvalues || '').trim()
    }
    empTitles.value = {
      pmname: map.pmname || '开单',
      secname: map.secname || '美疗师1',
      thrname: map.thrname || '美疗师2',
    }
  } catch { /* 保持默认 */ }
}

const quickCheckoutLoading = ref('')
const allOrdersSelected = (group: VipGroup) => group.orders.every((o: any) => orderSelections.value[o.uuid])
const headerIndeterminate = (group: VipGroup) => {
  const sel = group.orders.filter((o: any) => orderSelections.value[o.uuid])
  return sel.length > 0 && sel.length < group.orders.length
}
const groupSelectedOrders = (group: VipGroup) => group.orders.filter((o: any) => orderSelections.value[o.uuid])
const selectedOrderCount = computed(() => selectedGroup.value ? groupSelectedOrders(selectedGroup.value).length : 0)

function onToggleAllSelected(group: VipGroup, val: boolean) {
  for (const o of group.orders) orderSelections.value[o.uuid] = !!val
  onOrderSelectionChange(group)
}

const canQuickCheckoutSelected = computed(() => {
  if (!selectedGroup.value) return false
  const selected = groupSelectedOrders(selectedGroup.value)
  if (!selected.length) return false
  return selected.every((o: any) => !hasEmpIssues(o) && !isStale(o) && auditIssues.value.length === 0)
})

async function quickCheckout(group: VipGroup) {
  const selected = groupSelectedOrders(group)
  if (!selected.length) { ElMessage.warning('请先勾选单据'); return }
  quickCheckoutLoading.value = group.vipuuid
  try {
    if (!auditCards.value.length || !auditPaymodes.value.length) {
      await preparePaymentContext(group)
    }
    const defPcode = auditPaymodeDefaults.value?.normal_pcode || ''
    const splits: Record<string, any[]> = {}
    const fallbackMsgs: string[] = []
    for (const o of selected) {
      const total = auditOrderTotal(o)
      const sps: any[] = []
      if (o.paycode) {
        const card = auditCards.value.find((c: any) => c.ccode === o.paycode)
        if (card && isActivePayCard(card)) {
          const bal = parseFloat(card.leftmoney || 0)
          const pm = auditPaymodes.value.find((pm: any) => pm.pcode === o.paytype)
          const pcode = (o.paytype && pm) ? o.paytype : defPcode
          sps.push({ pcode, ccode: o.paycode, amount: Math.min(total, bal) })
        } else if (originPaycardUnusable(o)) {
          fallbackMsgs.push(`${o.exptxserno}：开单付款卡 ${o.paycode} 未生效/不可用，已改用现金`)
        }
      }
      const r = total - sps.reduce((s: number, sp: any) => s + sp.amount, 0)
      if (r > 0.01 || sps.length === 0) sps.push({ pcode: defPcode, ccode: '', amount: Math.round(r * 100) / 100 })
      splits[o.uuid] = sps
    }
    if (fallbackMsgs.length) ElMessage.warning(fallbackMsgs.join('；'))
    const res = await request.post('/cashier/batch_checkout/', {
      company, storecode, cashier: auditCashier.value, uuids: selected.map((o: any) => o.uuid), splits,
    })
    if (res.data?.ok) {
      ElMessage.success('结账完成：' + (res.data.success || 0) + ' 单')
      await Promise.all([loadOrders(), loadTodaySettled()])
    } else ElMessage.error(res.data?.message || '结账失败')
  } catch (err: any) { ElMessage.error('结账失败: ' + (err?.message || '')) }
  finally { quickCheckoutLoading.value = '' }
}

const auditGroup = ref<VipGroup | null>(null)
const auditSplits = ref<Record<string, any[]>>({})
const auditCards = ref<any[]>([])
/** 当前 auditCards 对应的会员，用于判断「卡列表已加载但仍找不到」 */
const auditCardsLoadedVip = ref('')
const pendingPaycardToastVip = ref('')
const auditPaymodes = ref<any[]>([])
const auditPaymodeDefaults = ref<Record<string, string>>({})
const auditSubmitting = ref(false)
const appStore = useAppStore()
const auditCashier = ref(localStorage.getItem('genesis_pc_cashier_code') || appStore.ecode || '')
const auditCashierName = ref(localStorage.getItem('genesis_pc_cashier_name') || appStore.fullname || '')
const showAuditCashierPicker = ref(false)
const auditCashierSearchKw = ref('')
const auditCashierSearchRes = ref<any[]>([])
const auditCashierSearching = ref(false)

function isActivePayCard(card: any): boolean {
  return !!card && (card.status || 'O') === 'O'
}

/** 开单付款卡状态：active | pending | missing | unknown | none */
function originPaycardState(o: any): 'active' | 'pending' | 'missing' | 'unknown' | 'none' {
  const pc = (o?.paycode || '').trim()
  if (!pc) return 'none'
  const card = auditCards.value.find((c: any) => c.ccode === pc)
  if (card) return isActivePayCard(card) ? 'active' : 'pending'
  const listStatus = (o.paycard_status || '').trim()
  if (listStatus === 'O') return 'active'
  if (listStatus === 'P') return 'pending'
  if (listStatus) return 'missing'
  const vip = o.vipuuid || selectedVipUuid.value
  if (auditCardsLoadedVip.value && auditCardsLoadedVip.value === vip) return 'missing'
  return 'unknown'
}

function originPaycardUnusable(o: any): boolean {
  const st = originPaycardState(o)
  return st === 'pending' || st === 'missing'
}

function originPaycardFallbackTip(o: any): string {
  if (!originPaycardUnusable(o)) return ''
  const pc = (o.paycode || '').trim()
  if (originPaycardState(o) === 'pending') {
    return `开单付款卡 ${pc} 尚未生效（挂账卡），不能扣款，已改用现金。请先结清购卡单后再用此卡，或确认现金结账。`
  }
  return `开单付款卡 ${pc} 不存在或已无效，不能扣款，已改用现金。`
}

function auditCardBalance(o: any): number | null {
  if (!o.paycode) return null
  const card = auditCards.value.find((c: any) => c.ccode === o.paycode)
  if (!card || !isActivePayCard(card)) return null
  return parseFloat(card.leftmoney || 0)
}
function getOrderAuditCardPayAmt(o: any): number {
  const sps = auditSplits.value[o.uuid] || []
  const cardSplit = sps.find((sp: any) => sp._isCard || sp.ccode)
  return cardSplit ? (cardSplit.amount || 0) : 0
}

const auditIssues = computed(() => {
  const issues: string[] = []
  const group = auditGroup.value
  if (!group) return issues
  const _s = auditSplits.value
  void _s
  for (const o of group.orders) {
    if (!orderSelections.value[o.uuid]) continue
    if (hasEmpIssues(o)) issues.push(`${o.exptxserno}：部分项目未分配员工`)
    if (isStale(o)) issues.push(`${o.exptxserno}：该单已超过 7 天`)
    const sps = auditSplits.value[o.uuid] || []
    for (const sp of sps) {
      const ccode = (sp.ccode || '').trim()
      if (!ccode || !(sp.amount > 0)) continue
      const card = auditCards.value.find((c: any) => c.ccode === ccode)
      if (!card) {
        issues.push(`${o.exptxserno}：付款卡 ${ccode} 不存在或已无效`)
      } else if (!isActivePayCard(card)) {
        issues.push(`${o.exptxserno}：付款卡 ${ccode} 尚未生效（挂账卡），不能用于结账`)
      }
    }
    const bal = auditCardBalance(o)
    const cardPayAmt = getOrderAuditCardPayAmt(o)
    if (bal !== null && bal < cardPayAmt) {
      issues.push(`${o.exptxserno}：付款卡余额 ¥${bal.toFixed(2)}，卡需付 ¥${cardPayAmt.toFixed(2)}，差 ¥${(cardPayAmt - bal).toFixed(2)}`)
    }
  }
  return issues
})

/** 非阻断：因未生效/无效已改现金的说明 */
const auditNotices = computed(() => {
  const notices: string[] = []
  const group = auditGroup.value
  if (!group) return notices
  const _s = auditSplits.value
  void _s
  for (const o of group.orders) {
    if (!orderSelections.value[o.uuid]) continue
    if (!originPaycardUnusable(o)) continue
    const sps = auditSplits.value[o.uuid] || []
    const stillUsing = sps.some((sp: any) => sp.ccode === o.paycode && sp.amount > 0)
    if (stillUsing) continue
    if (originPaycardState(o) === 'pending') {
      notices.push(`${o.exptxserno}：开单付款卡 ${o.paycode} 尚未生效（挂账卡），不能扣款，已改用现金`)
    } else {
      notices.push(`${o.exptxserno}：开单付款卡 ${o.paycode} 不存在或已无效，已改用现金`)
    }
  }
  return notices
})

function initAuditSplitsForOrder(o: any) {
  const total = auditOrderTotal(o)
  const sps: any[] = []
  const defPcode = auditPaymodeDefaults.value?.normal_pcode || ''
  if (o.paycode) {
    const card = auditCards.value.find((c: any) => c.ccode === o.paycode)
    if (card && isActivePayCard(card)) {
      const bal = parseFloat(card.leftmoney || 0)
      const cardPcode = (o.paytype && auditPaymodes.value.find((pm: any) => pm.pcode === o.paytype)) ? o.paytype : defPcode
      sps.push({ pcode: cardPcode, ccode: o.paycode, amount: Math.min(total, bal), cardBalance: bal, _isCard: true })
    }
  }
  const r = total - sps.reduce((s: number, sp: any) => s + sp.amount, 0)
  if (r > 0.01 || sps.length === 0) sps.push({ pcode: defPcode, ccode: '', amount: Math.round(r * 100) / 100, _default: true })
  return sps
}

const auditGroupLiveTotal = computed(() => {
  if (!selectedGroup.value) return 0
  return groupSelectedOrders(selectedGroup.value).reduce((s: number, o: any) => s + auditOrderTotal(o), 0)
})

function toastPendingPaycardFallback(selected: any[], vipKey: string) {
  if (pendingPaycardToastVip.value === vipKey) return
  const msgs: string[] = []
  for (const o of selected) {
    if (!originPaycardUnusable(o)) continue
    const sps = auditSplits.value[o.uuid] || []
    if (sps.some((sp: any) => sp.ccode === o.paycode && sp.amount > 0)) continue
    if (originPaycardState(o) === 'pending') {
      msgs.push(`${o.exptxserno}：付款卡 ${o.paycode} 尚未生效，已改用现金`)
    } else {
      msgs.push(`${o.exptxserno}：付款卡 ${o.paycode} 不可用，已改用现金`)
    }
  }
  if (msgs.length) {
    pendingPaycardToastVip.value = vipKey
    ElMessage.warning(msgs.join('；'))
  }
}

async function preparePaymentContext(group: VipGroup) {
  const selected = groupSelectedOrders(group)
  for (const o of selected) syncOrderItemSubtotals(o)
  auditGroup.value = {
    ...group,
    orders: selected,
    totalAmount: selected.reduce((s: number, o: any) => s + auditOrderTotal(o), 0),
    latestDate: group.latestDate,
  }
  try {
    const [cardRes, pmRes] = await Promise.all([
      request.get('/adviser/get_vip_cardlist/', { params: { company, vipuuid: group.vipuuid } }),
      request.get('/cashier/payment_methods/', { params: { company } }),
    ])
    const cardList = Array.isArray(cardRes.data) ? cardRes.data : cardRes.data?.cards ?? []
    auditCards.value = cardList.map((c: any) => ({
      ccode: c.ccode || '', cardname: c.cardname || '', comptype: c.comptype || '',
      leftmoney: c.leftmoney || 0, leftqty: c.leftqty || 0, status: c.status || 'O',
    }))
    auditCardsLoadedVip.value = group.vipuuid
    auditPaymodes.value = pmRes.data?.paymodes || []
    auditPaymodeDefaults.value = pmRes.data?.defaults || {}
  } catch {
    auditCards.value = []
    auditCardsLoadedVip.value = group.vipuuid
    auditPaymodes.value = []
  }
  const nextSplits: Record<string, any[]> = { ...auditSplits.value }
  for (const o of selected) {
    if (!nextSplits[o.uuid]) nextSplits[o.uuid] = initAuditSplitsForOrder(o)
  }
  auditSplits.value = nextSplits
  toastPendingPaycardFallback(selected, group.vipuuid)
}

async function selectQueueEntry(entry: QueueVipEntry) {
  const group = vipGroups.value.find((g) => g.vipuuid === entry.vipuuid)
  if (!group) return
  if (selectedVipUuid.value !== entry.vipuuid) {
    pendingPaycardToastVip.value = ''
  }
  selectedVipUuid.value = entry.vipuuid
  selectedFocusDate.value = entry.date
  const focusIds = new Set(entry.orders.map((o: any) => o.uuid))
  for (const o of group.orders) {
    // 点某日期分组：默认勾选该日单据；同会员其他日期单据保留可见但不默认勾选
    orderSelections.value[o.uuid] = focusIds.has(o.uuid)
  }
  auditSplits.value = {}
  await preparePaymentContext(group)
}

function onOrderSelectionChange(group: VipGroup) {
  const selected = groupSelectedOrders(group)
  for (const o of selected) {
    syncOrderItemSubtotals(o)
    if (!auditSplits.value[o.uuid]) {
      auditSplits.value[o.uuid] = initAuditSplitsForOrder(o)
    }
  }
  auditGroup.value = {
    ...group,
    orders: selected,
    totalAmount: selected.reduce((s: number, o: any) => s + auditOrderTotal(o), 0),
    latestDate: group.latestDate,
  }
}

function auditSplitOptions(o: any, currentSp: any) {
  const opts: { label: string; value: string; isCard?: boolean; balance?: number }[] = []
  for (const pm of auditPaymodes.value) {
    opts.push({ label: (pm.iscash === '0' ? '卡 ' : pm.iscash === '1' ? '现 ' : '') + pm.pname, value: pm.pcode })
  }
  for (const c of auditCards.value) {
    if (!isActivePayCard(c)) continue
    if (!opts.some((x: any) => x.value === c.ccode)) {
      const bal = c.comptype === 'times' ? parseFloat(c.leftqty || 0) : parseFloat(c.leftmoney || 0)
      const unit = c.comptype === 'times' ? '次' : '元'
      opts.push({
        label: (c.cardname || c.ccode) + ' (' + bal.toFixed(c.comptype === 'times' ? 0 : 2) + unit + ')',
        value: c.ccode, isCard: true, balance: bal,
      })
    }
  }
  const sps = auditSplits.value[o.uuid] || []
  const used = new Set(sps.map((s: any) => s.pcode))
  return opts.filter((opt: any) => !used.has(opt.value) || opt.value === currentSp.pcode)
}

function auditSplitRemaining(o: any) {
  const sps = auditSplits.value[o.uuid]
  if (!sps) return auditOrderTotal(o)
  return auditOrderTotal(o) - sps.reduce((s: number, sp: any) => s + (sp.amount || 0), 0)
}

function addAuditSplit(o: any) {
  const sps = auditSplits.value[o.uuid]
  if (!sps) return
  const used = new Set(sps.map((s: any) => s.pcode))
  const firstAvail = auditSplitOptions(o, sps[0]).find((opt: any) => !used.has(opt.value) && opt.value !== '')
  if (!firstAvail) return
  const di = sps.findIndex((s: any) => s._default)
  const amt = di >= 0 ? Math.min(sps[di].amount, auditOrderTotal(o)) : 0
  sps.splice(di >= 0 ? di : sps.length, 0, {
    pcode: firstAvail.value, ccode: firstAvail.isCard ? firstAvail.value : '',
    amount: amt, cardBalance: firstAvail.balance, _isCard: !!firstAvail.isCard,
  })
  if (di >= 0) {
    sps[sps.length - 1].amount = Math.max(0, auditOrderTotal(o) - sps.reduce((s: number, sp2: any, i: number) => s + (i !== sps.length - 1 ? sp2.amount : 0), 0))
  }
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
  const total = auditOrderTotal(o)
  const paid = sps.reduce((s: number, sp: any) => s + (sp.amount || 0), 0)
  const diff = paid - total
  if (diff > 0.01) {
    ElMessage.warning('多付了，实际应付 ¥' + total.toFixed(2))
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
    const filledPcode = sps.find((sp: any) => sp._default)?.pcode || auditPaymodeDefaults.value?.normal_pcode || ''
    const filledPm = auditPaymodes.value.find((pm: any) => pm.pcode === filledPcode)
    ElMessage.warning('不足部分已用「' + (filledPm ? filledPm.pname : filledPcode) + '」补齐，请核对')
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
    .then((r) => { auditCashierSearchRes.value = Array.isArray(r.data) ? r.data : [] })
    .catch(() => { auditCashierSearchRes.value = [] })
    .finally(() => { auditCashierSearching.value = false })
}

function selectAuditCashier(u: any) {
  auditCashier.value = u.sys_userid || ''
  auditCashierName.value = u.sys_fullname || u.sys_userid || ''
  localStorage.setItem('genesis_pc_cashier_code', auditCashier.value)
  localStorage.setItem('genesis_pc_cashier_name', auditCashierName.value)
  showAuditCashierPicker.value = false
  auditCashierSearchRes.value = []
  auditCashierSearchKw.value = ''
}

async function persistAuditItemEdits(): Promise<boolean> {
  if (!auditGroup.value) return false
  const items: any[] = []
  for (const o of auditGroup.value.orders) {
    syncOrderItemSubtotals(o)
    for (const d of o.item_details || []) {
      if (!d.uuid && !d.ditem) {
        ElMessage.error(`${o.exptxserno}：明细缺少标识，请刷新后重试`)
        return false
      }
      items.push({
        hunguuid: o.uuid,
        uuid: d.uuid || '',
        ditem: d.ditem || '',
        secdisc: d.secdisc ?? 1,
        stype: d.stype || 'N',
        pmcode: d.pmcode || '',
        asscode1: d.asscode1 || '',
        asscode2: d.asscode2 || '',
        secoldcustflag: d.secoldcustflag === 'Y' ? 'Y' : 'N',
        mondisc: d.mondisc ?? 0,
      })
    }
  }
  if (!items.length) return true
  const res = await request.post('/adviser/update_hung_items_audit/', { company, storecode, items })
  if (!res.data?.ok) {
    ElMessage.error(res.data?.message || '保存审核修改失败')
    return false
  }
  return true
}

async function confirmAudit() {
  if (!selectedGroup.value) return
  onOrderSelectionChange(selectedGroup.value)
  if (!auditGroup.value?.orders.length) {
    ElMessage.warning('请先勾选要结账的单据')
    return
  }
  for (const o of auditGroup.value.orders) {
    if (Math.abs(auditSplitRemaining(o)) > 0.01) {
      ElMessage.warning(`${o.exptxserno}：付款金额未配平`)
      return
    }
  }
  const inactiveCardIssue = auditIssues.value.find((msg) => msg.includes('尚未生效') || msg.includes('不存在或已无效'))
  if (inactiveCardIssue) {
    ElMessage.error(inactiveCardIssue)
    return
  }
  if (!auditCashier.value) {
    ElMessage.warning('请先选择收银员')
    showAuditCashierPicker.value = true
    return
  }
  auditSubmitting.value = true
  const uuids = auditGroup.value.orders.map((o: any) => o.uuid)
  const splits: Record<string, any[]> = {}
  for (const uuid of uuids) {
    const sp = auditSplits.value[uuid]
    if (sp?.length) splits[uuid] = sp.map((s: any) => ({ pcode: s.pcode, ccode: s.ccode || '', amount: s.amount }))
  }
  try {
    const saved = await persistAuditItemEdits()
    if (!saved) return
    const res = await request.post('/cashier/batch_checkout/', {
      company, storecode, cashier: auditCashier.value, uuids, splits,
    })
    if (res.data?.ok) {
      const failed = (res.data.results || []).filter((r: any) => !r.ok)
      if (failed.length) {
        ElMessage.error(failed[0].message || '部分单据结账失败')
        await Promise.all([loadOrders(), loadTodaySettled()])
      } else {
        ElMessage.success(`结账完成：${res.data.success || 0} 单`)
        selectedVipUuid.value = ''
        selectedFocusDate.value = ''
        auditGroup.value = null
        auditSplits.value = {}
        await Promise.all([loadOrders(), loadTodaySettled()])
      }
    } else ElMessage.error(res.data?.message || '结账失败')
  } catch (err: any) { ElMessage.error('结账失败: ' + (err?.message || '')) }
  finally { auditSubmitting.value = false }
}

// 筛选变化时，若当前选中人不在列表里则清空
watch(vipGroups, (groups) => {
  if (selectedVipUuid.value && !groups.some((g) => g.vipuuid === selectedVipUuid.value)) {
    selectedVipUuid.value = ''
    selectedFocusDate.value = ''
    auditGroup.value = null
  }
})

loadOrders(); loadEmployees(); loadEmpTitles(); loadTodaySettled()
</script>

<style scoped>
.chk-page { display:flex; flex-direction:column; gap:10px; height:100%; min-height:0; }
.chk-top {
  display:flex; align-items:center; justify-content:space-between; gap:12px; flex-shrink:0;
  padding:10px 14px; background:var(--g-color-surface); border:1px solid var(--g-color-border); border-radius:8px;
}
.chk-top-stats { display:flex; align-items:center; gap:16px; flex-wrap:wrap; }
.top-stat { font-size:14px; color:var(--g-color-text-secondary); }
.top-stat b { font-size:18px; font-weight:700; color:var(--g-color-text); margin-right:4px; }
.top-stat.accent b { color:var(--g-color-money); }
.top-stat.warn b { color:var(--g-color-danger); }
.top-stat.muted { color:var(--g-color-text-muted); font-size:13px; }

.chk-body { flex:1; min-height:0; display:flex; gap:12px; }

.chk-queue {
  width:300px; flex-shrink:0; display:flex; flex-direction:column; gap:8px; min-height:0;
  background:var(--g-color-surface); border:1px solid var(--g-color-border); border-radius:8px; padding:12px;
}
.queue-search { width:100%; }
.queue-meta { font-size:12px; color:var(--g-color-text-muted); padding:0 2px; }
.queue-empty { flex:1; display:flex; align-items:center; justify-content:center; color:var(--g-color-text-muted); font-size:14px; }
.queue-list { flex:1; min-height:0; overflow-y:auto; display:flex; flex-direction:column; gap:12px; }
.queue-date-block { display:flex; flex-direction:column; gap:6px; }
.queue-date-head {
  display:flex; align-items:baseline; justify-content:space-between; gap:8px;
  padding:4px 2px 2px; position:sticky; top:0; background:var(--g-color-surface); z-index:1;
}
.queue-date-label { font-size:13px; font-weight:700; color:var(--g-color-text); }
.queue-date-meta { font-size:11px; color:var(--g-color-text-muted); white-space:nowrap; }
.queue-item {
  display:flex; align-items:center; gap:10px; padding:12px 12px;
  border:1px solid var(--g-color-border); border-radius:8px; cursor:pointer; transition:.12s;
}
.queue-item:hover { border-color:var(--g-color-primary-border); background:var(--g-color-primary-soft); }
.queue-item.active { border-color:var(--g-color-primary); background:var(--g-color-primary-soft); }
.queue-item.warn { border-left:3px solid var(--g-color-warning); }
.qi-main { flex:1; min-width:0; }
.qi-name { font-size:15px; font-weight:700; color:var(--g-color-text); display:flex; align-items:center; gap:6px; }
.qi-dot { width:8px; height:8px; border-radius:50%; background:var(--g-color-warning); flex-shrink:0; }
.qi-sub { margin-top:3px; font-size:12px; color:var(--g-color-text-muted); }
.qi-amount { flex-shrink:0; font-size:16px; font-weight:700; color:var(--g-color-money); }

.chk-detail {
  flex:1; min-width:0; min-height:0; display:flex; flex-direction:column;
  background:var(--g-color-surface); border:1px solid var(--g-color-border); border-radius:8px; overflow:hidden;
}
.detail-empty {
  flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; color:var(--g-color-text-muted);
}
.detail-empty-title { font-size:18px; font-weight:600; color:var(--g-color-text-muted); }
.detail-empty-desc { font-size:14px; }

.detail-header {
  display:flex; justify-content:space-between; align-items:center; gap:16px;
  padding:14px 18px; border-bottom:1px solid var(--g-color-border);
  background:linear-gradient(135deg, var(--g-color-primary-soft), var(--g-color-surface));
  flex-shrink:0;
}
.dh-name { font-size:20px; font-weight:700; color:var(--g-color-text); }
.dh-code { margin-top:2px; font-size:13px; color:var(--g-color-text-muted); display:flex; align-items:center; gap:6px; }
.dh-right { text-align:right; }
.dh-amount { font-size:26px; font-weight:700; color:var(--g-color-money); line-height:1.1; }
.dh-amount-hint { margin-top:4px; font-size:12px; color:var(--g-color-text-muted); }

.detail-toolbar {
  display:flex; align-items:center; gap:8px; padding:8px 18px; border-bottom:1px solid var(--g-color-border); flex-shrink:0;
}
.toolbar-spacer { flex:1; }
.cashier-line { font-size:13px; color:var(--g-color-text-secondary); }

.detail-scroll { flex:1; min-height:0; overflow-y:auto; padding:12px 16px; }
.detail-footer {
  display:flex; justify-content:flex-end; gap:10px; padding:12px 18px;
  border-top:1px solid var(--g-color-border); background:var(--g-color-surface-muted); flex-shrink:0;
}

.audit-order-card { border:1px solid var(--g-color-border); border-radius:8px; margin-bottom:10px; overflow:hidden; }
.audit-order-card.off { opacity:.55; }
.audit-order-header {
  display:flex; align-items:center; gap:10px; padding:10px 12px;
  background:var(--g-color-surface-muted); border-bottom:1px solid var(--g-color-border); font-size:13px;
}
.ao-serno { font-family:ui-monospace, Menlo, monospace; font-weight:700; }
.ao-date { color:var(--g-color-text-muted); }
.ao-paycard {
  font-size:12px; color:var(--g-color-text-secondary); font-family:ui-monospace, Menlo, monospace;
  max-width:180px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
.ao-amount { margin-left:auto; font-size:16px; font-weight:700; color:var(--g-color-money); }

.audit-items { padding:6px 12px; font-size:13px; }
.audit-items-header {
  display:flex; align-items:center; gap:4px; padding:4px 0; color:var(--g-color-text-muted); font-size:12px;
  border-bottom:1px solid var(--g-color-border);
}
.audit-item-row {
  display:flex; align-items:center; gap:4px; padding:6px 0; border-bottom:1px solid var(--g-color-border);
}
.audit-item-row.emp-missing { background:var(--g-color-danger-bg); margin:0 -12px; padding:6px 12px; }
.ai-name { flex:1.5; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }

.pay-fallback-tip {
  margin:0 12px; padding:8px 10px 8px 12px; font-size:12px; line-height:1.45;
  color:var(--g-color-warning-text);
  background:var(--g-color-warning-bg);
  border:1px solid var(--g-color-warning-border);
  border-left:3px solid var(--g-color-warning);
  border-radius:6px;
}
.audit-payment {
  display:flex; align-items:center; gap:8px; flex-wrap:wrap;
  padding:10px 12px; background:var(--g-color-surface-muted); border-top:1px solid var(--g-color-border); font-size:13px;
}
.pay-label { font-weight:600; color:var(--g-color-text-secondary); }
.audit-split-chip {
  display:inline-flex; align-items:center; gap:4px; padding:4px 6px;
  background:var(--g-color-surface); border:1px solid var(--g-color-border); border-radius:6px;
}
.origin-card-chip { background:var(--g-color-surface-muted); border-color:var(--g-color-border-strong); }
.origin-card-label { font-size:12px; color:var(--g-color-text-muted); font-family:ui-monospace, Menlo, monospace; }
.pay-unit { font-size:12px; color:var(--g-color-text-muted); }
.pay-ccode {
  font-size:13px; font-weight:600; color:var(--g-color-primary);
  font-family:ui-monospace, Menlo, monospace; padding:0 2px;
}
.pay-default { font-size:12px; color:var(--g-color-text-muted); }
.pay-remain { margin-left:auto; font-size:13px; color:var(--g-color-danger); font-weight:600; }
.pay-remain.ok { color:var(--g-color-success); }

.audit-issues {
  margin:10px 16px 0; border:1px solid var(--g-color-danger-border); border-radius:8px;
  padding:10px 12px; background:var(--g-color-danger-bg); flex-shrink:0;
  border-left:3px solid var(--g-color-danger);
}
.issues-title { font-size:13px; font-weight:700; color:var(--g-color-danger-text); margin-bottom:4px; }
.issues-row { font-size:13px; color:var(--g-color-text-secondary); padding:3px 0; }
.audit-notices {
  margin:8px 16px 0; border:1px solid var(--g-color-warning-border); border-radius:8px;
  padding:10px 12px; background:var(--g-color-warning-bg); flex-shrink:0;
  border-left:3px solid var(--g-color-warning);
}
.notices-title { font-size:13px; font-weight:700; color:var(--g-color-warning-text); margin-bottom:4px; }
.notices-row { font-size:13px; color:var(--g-color-text-secondary); padding:3px 0; }

.cashier-result-item {
  display:flex; align-items:center; padding:8px 10px; border-bottom:1px solid var(--g-color-border); cursor:pointer;
}
.cashier-result-item:hover { background:var(--g-color-primary-soft); }
</style>
