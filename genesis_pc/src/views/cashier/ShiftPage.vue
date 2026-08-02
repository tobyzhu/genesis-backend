<template>
  <div class="page shift-page">
    <div class="page-header">
      <div class="shift-title-wrap">
        <h3 class="page-title">交班日结</h3>
        <span class="page-subtitle">{{ todayStr }}</span>
      </div>
      <el-button size="small" text type="primary" @click="showPaymentReport">查询付款明细</el-button>
    </div>

    <el-tabs v-model="activeTab" class="shift-tabs">
      <el-tab-pane name="handover">
        <template #label><el-icon class="tab-icon"><Refresh /></el-icon> 交班</template>
        <div v-if="!handoverResult" class="empty-state action-placeholder">
          <el-icon class="empty-icon"><Refresh /></el-icon>
          <p>点击下方按钮对当前未日结的单据进行班次标记</p>
          <el-button type="primary" size="large" :loading="handoverLoading" @click="doHandover">开始交班</el-button>
        </div>

        <template v-if="handoverResult">
          <div class="stat-grid summary-cards">
            <div class="stat-card summary-card">
              <div class="stat-value">{{ handoverResult.shift_no }} 班</div>
              <div class="stat-label">班次</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value">{{ handoverResult.order_count }}</div>
              <div class="stat-label">结账单数</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value money">¥{{ Number(handoverResult.total_amount).toFixed(0) }}</div>
              <div class="stat-label">总金额</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value date">{{ fmtDate(handoverResult.minvsdate) }}</div>
              <div class="stat-label">最小日期</div>
            </div>
          </div>

          <div class="section section-card">
            <div class="section-head">
              <span><el-icon class="head-icon"><Money /></el-icon> 付款方式汇总</span>
            </div>
            <div class="section-body">
              <div v-for="(pm, pcode) in handoverResult.payment_summary" :key="String(pcode)" class="pm-row">
                <span class="pm-name">{{ pm.name || pcode }}</span>
                <span class="pm-count">{{ pm.count }} 笔</span>
                <span class="pm-amount money">¥{{ Number(pm.total).toFixed(2) }}</span>
              </div>
            </div>
          </div>

          <div class="section section-card">
            <div class="section-head">
              <span><el-icon class="head-icon"><Wallet /></el-icon> 实际盘点</span>
              <span class="section-hint">输入各付款方式实际收款金额</span>
            </div>
            <div class="section-body">
              <div class="pm-row pm-head">
                <span class="pm-name">付款方式</span>
                <span class="pm-count">预期</span>
                <span class="pm-amount">实际</span>
                <span class="pm-amount">差额</span>
                <span class="pm-action">操作</span>
              </div>
              <div v-for="(pm, pcode) in handoverResult.payment_summary" :key="String(pcode)" class="pm-row">
                <span class="pm-name">{{ pm.name || pcode }}</span>
                <span class="pm-count">¥{{ Number(pm.total).toFixed(2) }}</span>
                <span class="pm-amount"><el-input-number v-model="handoverActuals[pcode]" :min="0" :step="10" size="small" :controls="false" :precision="2" style="width:80px" /></span>
                <span class="pm-amount" :class="(handoverActuals[pcode] - pm.total) === 0 ? 'diff-ok' : 'diff-bad'">¥{{ (handoverActuals[pcode] - pm.total).toFixed(2) }}</span>
                <span class="pm-action"><el-button text type="primary" size="small" @click="showPaymentDetail(pcode, pm.name || pcode)">查看明细</el-button></span>
              </div>
              <div class="pm-row pm-total">
                <span class="pm-name">合计</span>
                <span class="pm-count">¥{{ handoverTotalExpected.toFixed(2) }}</span>
                <span class="pm-amount">¥{{ handoverTotalActual.toFixed(2) }}</span>
                <span class="pm-amount" :class="(handoverTotalActual - handoverTotalExpected) === 0 ? 'diff-ok' : 'diff-bad'">¥{{ (handoverTotalActual - handoverTotalExpected).toFixed(2) }}</span>
                <span class="pm-action"></span>
              </div>
            </div>
          </div>

          <div class="action-row">
            <el-button size="default" @click="handoverResult = null">返回</el-button>
            <el-button size="default" type="success" :icon="CircleCheck" @click="confirmHandover">确认交班（记录盘点）</el-button>
            <el-button size="default" type="primary" :loading="handoverLoading" @click="doHandover">再次交班</el-button>
          </div>
        </template>
      </el-tab-pane>

      <el-tab-pane name="settlement">
        <template #label><el-icon class="tab-icon"><Calendar /></el-icon> 日结</template>
        <div v-if="settleLoading" class="empty-state action-placeholder">加载中...</div>

        <template v-if="settlePreview && !settleResult">
          <div class="stat-grid summary-cards">
            <div class="stat-card summary-card">
              <div class="stat-value date">{{ fmtDate(settlePreview.business_date) }}</div>
              <div class="stat-label">待日结日期</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value">{{ settlePreview.order_count }}</div>
              <div class="stat-label">待结单数</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value money">¥{{ Number(settlePreview.total_amount).toFixed(0) }}</div>
              <div class="stat-label">待结金额</div>
            </div>
          </div>
          <div class="action-row">
            <el-button type="danger" size="large" :icon="Warning" :loading="settleExecuting" @click="execSettlement">执行日结（不可逆）</el-button>
          </div>
        </template>

        <template v-if="settleResult">
          <div class="stat-grid summary-cards">
            <div class="stat-card summary-card">
              <div class="stat-value date">{{ fmtDate(settleResult.business_date) }}</div>
              <div class="stat-label">营业日期</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value">{{ settleResult.order_count }}</div>
              <div class="stat-label">日结单数</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value money">¥{{ Number(settleResult.total_amount).toFixed(0) }}</div>
              <div class="stat-label">日结金额</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value date">{{ fmtDate(settleResult.settle_date) }}</div>
              <div class="stat-label">日结日期</div>
            </div>
          </div>
          <div class="section section-card">
            <div class="section-head"><span><el-icon class="head-icon"><DataAnalysis /></el-icon> 班次分布</span></div>
            <div class="section-body">
              <template v-for="(val, key) in settleResult.shift_summary" :key="String(key)">
                <div class="shift-section">
                  <div class="shift-title">第 {{ key }} 班（{{ val.count }} 单 ¥{{ Number(val.total).toFixed(2) }}）</div>
                  <div v-for="(pm, pcode) in val.payment_summary" :key="String(pcode)" class="pm-row pm-nested">
                    <span class="pm-name">{{ pm.name || pcode }}</span>
                    <span class="pm-count">{{ pm.count }} 笔</span>
                    <span class="pm-amount money">¥{{ Number(pm.total).toFixed(2) }}</span>
                  </div>
                </div>
              </template>
            </div>
          </div>
          <div class="section section-card">
            <div class="section-head"><span><el-icon class="head-icon"><Money /></el-icon> 付款方式汇总</span></div>
            <div class="section-body">
              <div v-for="(pm, pcode) in settleResult.payment_summary" :key="String(pcode)" class="pm-row">
                <span class="pm-name">{{ pm.name || pcode }}</span>
                <span class="pm-count">{{ pm.count }} 笔</span>
                <span class="pm-amount money">¥{{ Number(pm.total).toFixed(2) }}</span>
              </div>
            </div>
          </div>
          <div class="action-row">
            <el-button size="default" @click="loadPendingSettlement">查看下一个待日结</el-button>
          </div>
        </template>

        <div v-if="noPending && !settleLoading" class="empty-state action-placeholder">
          <el-icon class="empty-icon success"><CircleCheck /></el-icon>
          <p>没有待日结的单据</p>
        </div>

        <div v-if="settleError && !settlePreview && !settleResult" class="empty-state action-placeholder">
          <p>{{ settleError }}</p>
          <el-button size="small" @click="loadPendingSettlement">重新检查</el-button>
        </div>
      </el-tab-pane>

      <el-tab-pane name="history">
        <template #label><el-icon class="tab-icon"><Search /></el-icon> 历史查询</template>
        <div v-if="historyDates.length > 0" class="filter-bar history-filter">
          <span class="filter-label">选择日结日期：</span>
          <el-select v-model="selectedHistoryDate" placeholder="选择日期" size="small" @change="loadHistoryDetail" style="width:160px">
            <el-option v-for="d in historyDates" :key="d" :label="fmtDate(d)" :value="d" />
          </el-select>
        </div>
        <div v-if="historyLoading" class="empty-state action-placeholder">加载中...</div>
        <template v-if="historyResult">
          <div class="stat-grid summary-cards">
            <div class="stat-card summary-card">
              <div class="stat-value date">{{ fmtDate(historyResult.cdate) }}</div>
              <div class="stat-label">日结批次</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value">{{ historyResult.order_count }}</div>
              <div class="stat-label">总单数</div>
            </div>
            <div class="stat-card summary-card">
              <div class="stat-value money">¥{{ Number(historyResult.total_amount).toFixed(0) }}</div>
              <div class="stat-label">总金额</div>
            </div>
          </div>
          <div class="section section-card">
            <div class="section-head"><span><el-icon class="head-icon"><DataAnalysis /></el-icon> 班次分布</span></div>
            <div class="section-body">
              <template v-for="(val, key) in historyResult.shift_summary" :key="String(key)">
                <div class="shift-section">
                  <div class="shift-title">第 {{ key }} 班（{{ val.count }} 单 ¥{{ Number(val.total).toFixed(2) }}）</div>
                  <div v-for="(pm, pcode) in val.payment_summary" :key="String(pcode)" class="pm-row pm-nested">
                    <span class="pm-name">{{ pm.name || pcode }}</span>
                    <span class="pm-count">{{ pm.count }} 笔</span>
                    <span class="pm-amount money">¥{{ Number(pm.total).toFixed(2) }}</span>
                  </div>
                </div>
              </template>
            </div>
          </div>
          <div class="section section-card">
            <div class="section-head"><span><el-icon class="head-icon"><Money /></el-icon> 付款方式汇总</span></div>
            <div class="section-body">
              <div v-for="(pm, pcode) in historyResult.payment_summary" :key="String(pcode)" class="pm-row">
                <span class="pm-name">{{ pm.name || pcode }}</span>
                <span class="pm-count">{{ pm.count }} 笔</span>
                <span class="pm-amount money">¥{{ Number(pm.total).toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </template>
        <div v-if="!historyLoading && historyDates.length === 0" class="empty-state action-placeholder">
          <el-icon class="empty-icon"><Search /></el-icon>
          <p>暂无历史日结记录</p>
        </div>
        <div v-if="historyError" class="empty-state">{{ historyError }}</div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="detailVisible" :title="detailPname + ' 交易明细'" width="650px" :close-on-click-modal="false" top="5vh">
      <div v-if="detailLoading" class="empty-state">加载中...</div>
      <template v-if="detailOrders.length">
        <div class="dialog-hint">{{ detailOrderCount }} 单，合计 ¥{{ detailTotal.toFixed(2) }}</div>
        <el-table :data="detailOrders" size="small" stripe max-height="400">
          <el-table-column label="单号" prop="exptxserno" width="130" />
          <el-table-column label="会员" width="100"><template #default="{ row }">{{ row.vname || row.vcode || '--' }}</template></el-table-column>
          <el-table-column label="日期" prop="vsdate" width="80" />
          <el-table-column label="总金额" width="80" align="right"><template #default="{ row }">¥{{ Number(row.totmount).toFixed(2) }}</template></el-table-column>
          <el-table-column label="付款金额" width="90" align="right"><template #default="{ row }">¥{{ Number(row.payment_amount).toFixed(2) }}</template></el-table-column>
        </el-table>
      </template>
      <template #footer><el-button size="default" @click="detailVisible = false">关闭</el-button></template>
    </el-dialog>

    <el-dialog v-model="reportVisible" title="付款明细查询" width="700px" :close-on-click-modal="false" top="5vh">
      <div class="filter-bar report-filter">
        <el-date-picker v-model="reportDateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
          end-placeholder="结束日期" size="small" style="width:260px" value-format="YYYYMMDD" />
        <el-button size="small" type="primary" :loading="reportLoading" @click="fetchPaymentReport">查询</el-button>
      </div>
      <div v-if="reportData" class="dialog-hint">
        {{ reportData.order_count }} 单，合计 ¥{{ Number(reportData.total_amount).toFixed(0) }}
      </div>
      <div v-if="reportData" class="pm-report-table">
        <div class="pm-report-header">
          <span class="pm-r-name">付款方式</span>
          <span class="pm-r-count">笔数</span>
          <span class="pm-r-amount">金额</span>
          <span class="pm-r-action">操作</span>
        </div>
        <div v-for="(info, pc) in reportPaymentSummary" :key="String(pc)" class="pm-report-row">
          <span class="pm-r-name">{{ info.name || pc }}</span>
          <span class="pm-r-count">{{ info.count }} 笔</span>
          <span class="pm-r-amount money">¥{{ Number(info.total).toFixed(2) }}</span>
          <span class="pm-r-action">
            <el-button text type="primary" size="small" @click="showReportDetail(info)">查看明细</el-button>
          </span>
        </div>
      </div>
      <el-empty v-if="reportQueried && !reportData" description="该日期范围暂无数据" :image-size="50" />
      <template #footer><el-button size="default" @click="reportVisible = false">关闭</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'
import { Refresh, Calendar, Search, Money, Wallet, DataAnalysis, Warning, CircleCheck } from '@element-plus/icons-vue'

const company = localStorage.getItem('genesis_pc_company') || ''
const storecode = localStorage.getItem('genesis_pc_storecode') || ''
const activeTab = ref('handover')
const todayStr = new Date().toLocaleDateString('zh-CN', { year:'numeric', month:'2-digit', day:'2-digit' })

function fmtDate(d: string) { return d ? d.slice(0,4)+'/'+d.slice(4,6)+'/'+d.slice(6,8) : '' }
const handoverTotalExpected = computed(() => {
  if (!handoverResult.value?.payment_summary) return 0
  let s = 0
  for (const pm of Object.values(handoverResult.value.payment_summary)) { s += (pm as any).total || 0 }
  return s
})
const handoverTotalActual = computed(() => {
  let s = 0
  for (const v of Object.values(handoverActuals.value)) { s += (v || 0) }
  return s
})

const handoverLoading = ref(false)
const handoverResult = ref<any>(null)
const detailVisible = ref(false)
const detailPname = ref('')
const detailOrders = ref<any[]>([])
const detailOrderCount = ref(0)
const detailTotal = ref(0)
const detailLoading = ref(false)

function showPaymentDetail(pcode: string, pname: string) {
  detailPname.value = pname
  detailVisible.value = true
  detailLoading.value = false
  const details = handoverResult.value?.details || []
  const filtered: any[] = []
  for (const exp of details) {
    const pmts = (exp.payments || []).filter((p: any) => p.pcode === pcode)
    for (const pmt of pmts) {
      filtered.push({
        exptxserno: exp.exptxserno || '',
        vsdate: exp.vsdate || '',
        totmount: exp.totmount || 0,
        payment_amount: pmt.amount || 0,
      })
    }
  }
  detailOrders.value = filtered
  detailOrderCount.value = filtered.length
  detailTotal.value = filtered.reduce((s: number, o: any) => s + (o.payment_amount || 0), 0)
}

const handoverActuals = ref<Record<string, number>>({})

async function doHandover() {
  handoverLoading.value = true; handoverResult.value = null
  try {
    const res = await request.post('/cashier/shift_handover/', { company, storecode })
    if (res.data?.ok) { 
      handoverResult.value = res.data
      const initA: Record<string, number> = {}
      for (const [pc, pm] of Object.entries(res.data.payment_summary || {})) { initA[pc] = (pm as any).total || 0 }
      handoverActuals.value = initA
      ElMessage.success('交班完成：第 ' + res.data.shift_no + ' 班') 
    }
    else ElMessage.error(res.data?.message || '交班失败')
  } catch (err: any) { ElMessage.error('交班失败: ' + (err?.message||'')) }
  finally { handoverLoading.value = false }
}

async function confirmHandover() {
  try {
    const res = await request.post('/cashier/shift_handover/', { company, storecode, actuals: handoverActuals.value, record_only: true })
    if (res.data?.ok) ElMessage.success('盘点差异已记录')
    else ElMessage.error(res.data?.message || '记录失败')
  } catch (err: any) { ElMessage.error('记录失败: ' + (err?.message||'')) }
}

const settleLoading = ref(false)
const settlePreview = ref<any>(null)
const settleResult = ref<any>(null)
const settleExecuting = ref(false)
const settleError = ref('')
const noPending = ref(false)

async function loadPendingSettlement() {
  settleLoading.value = true; settlePreview.value = null; settleResult.value = null; settleError.value = ''; noPending.value = false
  try {
    const res = await request.get('/cashier/daily_settlement/', { params: { company, storecode, preview: '1' } })
    const d = res.data
    if (d?.ok && d.has_pending) { settlePreview.value = d }
    else if (d?.ok && !d.has_pending) { noPending.value = true }
    else { settleError.value = d?.message || '查询失败' }
  } catch { settleError.value = '查询失败' }
  finally { settleLoading.value = false }
}

async function execSettlement() {
  settleExecuting.value = true
  try {
    const res = await request.post('/cashier/daily_settlement/', { company, storecode })
    const d = res.data
    if (d?.ok) { settleResult.value = d; settlePreview.value = null; ElMessage.success('日结完成：' + d.order_count + ' 单') }
    else ElMessage.error(d?.message || '日结失败')
  } catch (err: any) { ElMessage.error('日结失败: ' + (err?.message||'')) }
  finally { settleExecuting.value = false }
}


const historyDates = ref<string[]>([])
const selectedHistoryDate = ref('')
const historyLoading = ref(false)
const historyResult = ref<any>(null)
const historyError = ref('')

// ── 付款明细查询 ──
const reportVisible = ref(false)
const reportLoading = ref(false)
const reportDateRange = ref<any[]>([])
const reportData = ref<any>(null)
const reportQueried = ref(false)

const reportPaymentSummary = computed(() => {
  if (!reportData.value?.payment_summary) return {}
  return reportData.value.payment_summary
})

function showReportDetail(info: any) {
  detailPname.value = info.name || ''
  detailLoading.value = false
  detailOrders.value = info.orders || []
  detailOrderCount.value = info.count || 0
  detailTotal.value = info.total || 0
  detailVisible.value = true
}

async function fetchPaymentReport() {
  reportLoading.value = true
  reportData.value = null
  reportQueried.value = false
  if (!reportDateRange.value || reportDateRange.value.length < 2) { reportLoading.value = false; return }
  const df = reportDateRange.value[0]; const dt = reportDateRange.value[1]
  try {
    const res = await request.get('/cashier/payment_report/', { params: { company, storecode, date_from: df, date_to: dt } })
    if (res.data?.ok) { reportData.value = res.data; reportQueried.value = true }
    else { reportData.value = null; reportQueried.value = true }
  } catch { reportData.value = null; reportQueried.value = true }
  finally { reportLoading.value = false }
}

function showPaymentReport() {
  reportVisible.value = true
  reportData.value = null
  reportQueried.value = false
  // Default to today
  const d = new Date(); const ds = '' + d.getFullYear() + String(d.getMonth()+1).padStart(2,'0') + String(d.getDate()).padStart(2,'0')
  reportDateRange.value = [ds, ds]
}

async function loadHistoryDates() {
  try {
    const res = await request.get('/cashier/settlement_history/', { params: { company, storecode } })
    if (res.data?.ok) historyDates.value = res.data.dates || []
  } catch { historyDates.value = [] }
}

async function loadHistoryDetail() {
  if (!selectedHistoryDate.value) return
  historyLoading.value = true; historyResult.value = null; historyError.value = ''
  try {
    const res = await request.get('/cashier/settlement_detail/', { params: { company, storecode, cdate: selectedHistoryDate.value } })
    if (res.data?.ok) historyResult.value = res.data
    else historyError.value = res.data?.message || '查询失败'
  } catch { historyError.value = '查询失败' }
  finally { historyLoading.value = false }
}

onMounted(() => { loadPendingSettlement(); loadHistoryDates() })
</script>

<style scoped>
.shift-page { height: 100%; }
.shift-title-wrap { display: flex; align-items: baseline; gap: 10px; }
.shift-tabs { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.shift-tabs :deep(.el-tabs__content) { flex: 1; min-height: 0; overflow-y: auto; }
.tab-icon { vertical-align: -2px; margin-right: 4px; }

.action-placeholder { gap: 14px; }
.empty-icon { font-size: 44px; color: var(--g-color-text-muted); }
.empty-icon.success { color: var(--g-color-success); }
.action-row { display: flex; justify-content: center; gap: 10px; margin-top: 14px; }

.summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
.summary-card { text-align: left; }
.stat-value.money { color: var(--g-color-money); }
.stat-value.date { font-size: 16px; line-height: 1.6; }

.section-card { margin-bottom: 12px; }
.section-head .head-icon { vertical-align: -2px; margin-right: 4px; color: var(--g-color-text-secondary); }
.section-hint { font-size: 12px; font-weight: 400; color: var(--g-color-text-muted); }

.pm-row { display: flex; align-items: center; padding: 7px 0; border-bottom: 1px solid var(--g-color-border); font-size: 13px; }
.pm-row:last-child { border-bottom: none; }
.pm-head { font-weight: 600; color: var(--g-color-text-secondary); font-size: 12px; border-bottom: 1px solid var(--g-color-border-strong); }
.pm-total { border-top: 1px solid var(--g-color-border-strong); margin-top: 4px; padding-top: 8px; font-weight: 700; color: var(--g-color-text); }
.pm-nested { padding-left: 20px; }
.pm-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pm-count { width: 90px; text-align: center; color: var(--g-color-text-muted); font-size: 12px; }
.pm-amount { width: 100px; text-align: right; font-weight: 600; }
.pm-amount.money { color: var(--g-color-money); }
.pm-action { width: 80px; text-align: center; flex-shrink: 0; }
.diff-ok { color: var(--g-color-success); }
.diff-bad { color: var(--g-color-danger); }

.shift-section { margin-bottom: 8px; border: 1px solid var(--g-color-border); border-radius: var(--g-radius); overflow: hidden; }
.shift-title { font-weight: 600; font-size: 13px; color: var(--g-color-text); padding: 6px 12px; background: var(--g-color-surface-muted); border-bottom: 1px solid var(--g-color-border); }

.history-filter { margin-bottom: 12px; }
.filter-label { font-size: 13px; color: var(--g-color-text-secondary); }
.report-filter { margin-bottom: 12px; }
.dialog-hint { font-size: 12px; color: var(--g-color-text-muted); margin-bottom: 8px; }

.pm-report-table { border: 1px solid var(--g-color-border); border-radius: var(--g-radius); overflow: hidden; }
.pm-report-header { display: flex; padding: 7px 10px; background: var(--g-color-surface-muted); font-size: 12px; font-weight: 600; color: var(--g-color-text-secondary); border-bottom: 1px solid var(--g-color-border); }
.pm-report-row { display: flex; align-items: center; padding: 7px 10px; border-bottom: 1px solid var(--g-color-border); font-size: 13px; }
.pm-report-row:last-child { border-bottom: none; }
.pm-r-name { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.pm-r-count { width: 60px; text-align: center; color: var(--g-color-text-muted); }
.pm-r-amount { width: 110px; text-align: right; font-weight: 600; }
.pm-r-amount.money { color: var(--g-color-money); }
.pm-r-action { width: 80px; text-align: center; }
</style>
