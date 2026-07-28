<template>
  <div class="shift-page">
    <div class="header-row">
      <h2 style="margin:0;font-size:18px;font-weight:600">交班日结</h2>
      <span style="font-size:12px;color:#909399">{{ todayStr }}</span>
      <el-button size="small" text type="primary" @click="showPaymentReport" style="margin-left:auto">查询付款明细</el-button>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="🔄 交班" name="handover">
        <div v-if="!handoverResult" class="action-placeholder">
          <div style="font-size:48px;margin-bottom:8px">🔄</div>
          <p style="color:#909399;font-size:13px">点击下方按钮对当前未日结的单据进行班次标记</p>
          <el-button type="primary" size="large" :loading="handoverLoading" @click="doHandover">开始交班</el-button>
        </div>

        <template v-if="handoverResult">
          <div class="summary-cards">
            <div class="summary-card"><div class="sc-num">第 {{ handoverResult.shift_no }} 班</div><div class="sc-label">班次</div></div>
            <div class="summary-card"><div class="sc-num">{{ handoverResult.order_count }}</div><div class="sc-label">结账单数</div></div>
            <div class="summary-card"><div class="sc-num" style="color:#e6a23c">¥{{ Number(handoverResult.total_amount).toFixed(0) }}</div><div class="sc-label">总金额</div></div>
            <div class="summary-card"><div class="sc-num" style="font-size:14px">{{ fmtDate(handoverResult.minvsdate) }}</div><div class="sc-label">最小日期</div></div>
          </div>
    <el-dialog v-model="detailVisible" :title="'💰 ' + detailPname + ' 交易明细'" width="650px" :close-on-click-modal="false" top="5vh">
      <div v-if="detailLoading" style="text-align:center;padding:30px;color:#909399">加载中...</div>
      <template v-if="detailOrders.length">
        <div style="font-size:12px;color:#909399;margin-bottom:6px">{{ detailOrderCount }} 单，合计 ¥{{ detailTotal.toFixed(2) }}</div>
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
          <el-card shadow="never" class="section-card">
            <template #header>💰 付款方式汇总</template>
            <div v-for="(pm, pcode) in handoverResult.payment_summary" :key="String(pcode)" class="pm-row">
              <span class="pm-name">{{ pm.name || pcode }}</span>
              <span class="pm-count">{{ pm.count }} 笔</span>
              <span class="pm-amount">¥{{ Number(pm.total).toFixed(2) }}</span>
            </div>
          </el-card>
          <el-card shadow="never" class="section-card">
            <template #header>💵 实际盘点 <span style="font-size:11px;color:#909399;font-weight:400">输入各付款方式实际收款金额</span></template>
            <div class="pm-row" style="font-weight:600;color:#303133">
              <span class="pm-name">付款方式</span><span class="pm-count">预期</span><span class="pm-amount" style="width:80px">实际</span><span class="pm-amount" style="width:80px">差额</span><span style="width:60px;text-align:center">操作</span>
            </div>
            <div v-for="(pm, pcode) in handoverResult.payment_summary" :key="String(pcode)" class="pm-row">
              <span class="pm-name">{{ pm.name || pcode }}</span>
              <span class="pm-count">¥{{ Number(pm.total).toFixed(2) }}</span>
              <span class="pm-amount" style="width:80px"><el-input-number v-model="handoverActuals[pcode]" :min="0" :step="10" size="small" :controls="false" :precision="2" style="width:80px" /></span>
              <span class="pm-amount" :style="{color: (handoverActuals[pcode] - pm.total) === 0 ? '#67c23a' : '#f56c6c', fontWeight:600, width:'80px'}">¥{{ (handoverActuals[pcode] - pm.total).toFixed(2) }}</span>
              <span style="width:60px;text-align:center"><el-button text type="primary" size="small" @click="showPaymentDetail(pcode, pm.name || pcode)">查看明细</el-button></span>
            </div>
            <div class="pm-row" style="border-top:2px solid #e6a23c;margin-top:4px;padding-top:6px;font-weight:600">
              <span class="pm-name">合计</span>
              <span class="pm-count">¥{{ handoverTotalExpected.toFixed(2) }}</span>
              <span class="pm-amount" style="width:80px">¥{{ handoverTotalActual.toFixed(2) }}</span>
              <span class="pm-amount" :style="{color: (handoverTotalActual - handoverTotalExpected) === 0 ? '#67c23a' : '#f56c6c', fontWeight:700, width:'80px'}">¥{{ (handoverTotalActual - handoverTotalExpected).toFixed(2) }}</span>
              <span style="width:60px"></span>
            </div>
          </el-card>
          <div style="margin-top:8px;text-align:center">
            <el-button size="default" @click="handoverResult = null">返回</el-button>
            <el-button size="default" type="success" @click="confirmHandover">✅ 确认交班（记录盘点）</el-button>
            <el-button size="default" type="primary" @click="doHandover" :loading="handoverLoading">再次交班</el-button>
          </div>
        </template>
      </el-tab-pane>

      <el-tab-pane label="📅 日结" name="settlement">
        <div v-if="settleLoading" style="text-align:center;padding:30px;color:#909399">加载中...</div>
        
        <template v-if="settlePreview && !settleResult">
          <div class="summary-cards">
            <div class="summary-card"><div class="sc-num" style="font-size:16px">{{ fmtDate(settlePreview.business_date) }}</div><div class="sc-label">待日结日期</div></div>
            <div class="summary-card"><div class="sc-num">{{ settlePreview.order_count }}</div><div class="sc-label">待结单数</div></div>
            <div class="summary-card"><div class="sc-num" style="color:#e6a23c">¥{{ Number(settlePreview.total_amount).toFixed(0) }}</div><div class="sc-label">待结金额</div></div>
          </div>
          <div style="text-align:center;margin-top:12px">
            <el-button type="danger" size="large" :loading="settleExecuting" @click="execSettlement">⚠️ 执行日结（不可逆）</el-button>
          </div>
        </template>

        <template v-if="settleResult">
          <div class="summary-cards">
            <div class="summary-card"><div class="sc-num" style="font-size:14px">{{ fmtDate(settleResult.business_date) }}</div><div class="sc-label">营业日期</div></div>
            <div class="summary-card"><div class="sc-num">{{ settleResult.order_count }}</div><div class="sc-label">日结单数</div></div>
            <div class="summary-card"><div class="sc-num" style="color:#67c23a">¥{{ Number(settleResult.total_amount).toFixed(0) }}</div><div class="sc-label">日结金额</div></div>
            <div class="summary-card"><div class="sc-num" style="font-size:14px">{{ fmtDate(settleResult.settle_date) }}</div><div class="sc-label">日结日期</div></div>
          </div>
          <el-card shadow="never" class="section-card">
            <template #header>📊 班次分布</template>
            <template v-for="(val, key) in settleResult.shift_summary" :key="String(key)">
              <div class="shift-section">
                <div class="shift-title">第 {{ key }} 班（{{ val.count }} 单 ¥{{ Number(val.total).toFixed(2) }}）</div>
                <div v-for="(pm, pcode) in val.payment_summary" :key="String(pcode)" class="pm-row" style="padding-left:20px">
                  <span class="pm-name">{{ pm.name || pcode }}</span>
                  <span class="pm-count">{{ pm.count }} 笔</span>
                  <span class="pm-amount">¥{{ Number(pm.total).toFixed(2) }}</span>
                </div>
              </div>
            </template>
          </el-card>
          <el-card shadow="never" class="section-card">
            <template #header>💰 付款方式汇总</template>
            <div v-for="(pm, pcode) in settleResult.payment_summary" :key="String(pcode)" class="pm-row">
              <span class="pm-name">{{ pm.name || pcode }}</span>
              <span class="pm-count">{{ pm.count }} 笔</span>
              <span class="pm-amount">¥{{ Number(pm.total).toFixed(2) }}</span>
            </div>
          </el-card>
          <div style="margin-top:8px;text-align:center">
            <el-button size="default" @click="loadPendingSettlement">查看下一个待日结</el-button>
          </div>
        </template>

        <div v-if="noPending && !settleLoading" class="action-placeholder">
          <div style="font-size:48px;margin-bottom:8px;color:#67c23a">✅</div>
          <p style="color:#909399">没有待日结的单据</p>
        </div>

        <div v-if="settleError && !settlePreview && !settleResult" class="action-placeholder">
          <p style="color:#909399">{{ settleError }}</p>
          <el-button size="small" @click="loadPendingSettlement">重新检查</el-button>
        </div>
      </el-tab-pane>
      <el-tab-pane label="📋 历史查询" name="history">
        <template v-if="historyDates.length > 0">
          <div style="margin-bottom:10px">
            <span style="font-size:13px;color:#606266;margin-right:8px">选择日结日期：</span>
            <el-select v-model="selectedHistoryDate" placeholder="选择日期" size="small" @change="loadHistoryDetail" style="width:160px">
              <el-option v-for="d in historyDates" :key="d" :label="fmtDate(d)" :value="d" />
            </el-select>
          </div>
        </template>
        <div v-if="historyLoading" style="text-align:center;padding:30px;color:#909399">加载中...</div>
        <template v-if="historyResult">
          <div class="summary-cards">
            <div class="summary-card"><div class="sc-num" style="font-size:16px">{{ fmtDate(historyResult.cdate) }}</div><div class="sc-label">日结批次</div></div>
            <div class="summary-card"><div class="sc-num">{{ historyResult.order_count }}</div><div class="sc-label">总单数</div></div>
            <div class="summary-card"><div class="sc-num" style="color:#e6a23c">¥{{ Number(historyResult.total_amount).toFixed(0) }}</div><div class="sc-label">总金额</div></div>
          </div>
          <el-card shadow="never" class="section-card">
            <template #header>📊 班次分布</template>
            <template v-for="(val, key) in historyResult.shift_summary" :key="String(key)">
              <div class="shift-section">
                <div class="shift-title">第 {{ key }} 班（{{ val.count }} 单 ¥{{ Number(val.total).toFixed(2) }}）</div>
                <div v-for="(pm, pcode) in val.payment_summary" :key="String(pcode)" class="pm-row" style="padding-left:20px">
                  <span class="pm-name">{{ pm.name || pcode }}</span>
                  <span class="pm-count">{{ pm.count }} 笔</span>
                  <span class="pm-amount">¥{{ Number(pm.total).toFixed(2) }}</span>
                </div>
              </div>
            </template>
          </el-card>
          <el-card shadow="never" class="section-card">
            <template #header>💰 付款方式汇总</template>
            <div v-for="(pm, pcode) in historyResult.payment_summary" :key="String(pcode)" class="pm-row">
              <span class="pm-name">{{ pm.name || pcode }}</span>
              <span class="pm-count">{{ pm.count }} 笔</span>
              <span class="pm-amount">¥{{ Number(pm.total).toFixed(2) }}</span>
            </div>
          </el-card>
        </template>
        <div v-if="!historyLoading && historyDates.length === 0" class="action-placeholder">
          <p style="color:#909399">暂无历史日结记录</p>
        </div>
        <div v-if="historyError" style="text-align:center;padding:20px;color:#909399">{{ historyError }}</div>
      </el-tab-pane>
    <!-- 付款明细查询 -->
    <el-dialog v-model="reportVisible" title="付款明细查询" width="700px" :close-on-click-modal="false" top="5vh">
      <div style="display:flex;gap:10px;margin-bottom:12px;align-items:center">
        <el-date-picker v-model="reportDateRange" type="daterange" range-separator="至" start-placeholder="开始日期"
          end-placeholder="结束日期" size="small" style="width:260px" value-format="YYYYMMDD" />
        <el-button size="small" type="primary" :loading="reportLoading" @click="fetchPaymentReport">查询</el-button>
      </div>
      <div v-if="reportData" style="font-size:12px;color:#909399;margin-bottom:6px">
        {{ reportData.order_count }} 单，合计 ¥{{ Number(reportData.total_amount).toFixed(0) }}
      </div>
      <div v-if="reportData" class="pm-report-table">
        <div class="pm-report-header">
          <span class="pm-r-name">付款方式</span>
          <span class="pm-r-count">笔数</span>
          <span class="pm-r-amount">金额</span>
          <span style="width:80px;text-align:center">操作</span>
        </div>
        <div v-for="(info, pc) in reportPaymentSummary" :key="String(pc)" class="pm-report-row">
          <span class="pm-r-name">{{ info.name || pc }}</span>
          <span class="pm-r-count">{{ info.count }} 笔</span>
          <span class="pm-r-amount">¥{{ Number(info.total).toFixed(2) }}</span>
          <span style="width:80px;text-align:center">
            <el-button text type="primary" size="small" @click="showReportDetail(info)">查看明细</el-button>
          </span>
        </div>
      </div>
      <el-empty v-if="reportQueried && !reportData" description="该日期范围暂无数据" :image-size="50" />
      <template #footer><el-button size="default" @click="reportVisible = false">关闭</el-button></template>
    </el-dialog>

    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

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
.shift-page { display:flex; flex-direction:column; gap:10px; height:100%; }
.header-row { display:flex; justify-content:space-between; align-items:center; flex-shrink:0; }
.action-placeholder { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:60px 0; gap:12px; }
.summary-cards { display:flex; gap:12px; margin-bottom:10px; }
.summary-card { flex:1; text-align:center; padding:12px; background:#fff; border:1px solid #ebeef5; border-radius:8px; }
.sc-num { font-size:28px; font-weight:700; color:#303133; }
.sc-label { font-size:12px; color:#909399; margin-top:2px; }
.section-card { margin-bottom:8px; }
.section-card :deep(.el-card__body) { padding:8px 12px; }
.pm-row { display:flex; align-items:center; padding:5px 0; border-bottom:1px solid #f5f5f5; font-size:13px; }
.pm-row:last-child { border-bottom:none; }
.shift-section { margin-bottom:6px; border:1px solid #f0f0f0; border-radius:6px; padding:4px 0; background:#fafafa; }
.shift-title { font-weight:600; font-size:13px; color:#303133; padding:4px 10px; background:#f5f7fa; border-bottom:1px solid #ebeef5; }
.pm-name { flex:1; }
.pm-count { width:60px; text-align:center; color:#909399; font-size:12px; }
.pm-amount { width:100px; text-align:right; font-weight:600; }

.pm-report-table { border:1px solid #ebeef5; border-radius:6px; overflow:hidden; }
.pm-report-header { display:flex; padding:6px 10px; background:#f5f7fa; font-size:12px; font-weight:600; color:#606266; border-bottom:1px solid #ebeef5; }
.pm-report-row { display:flex; align-items:center; padding:6px 10px; border-bottom:1px solid #f5f5f5; font-size:13px; }
.pm-report-row:last-child { border-bottom:none; }
.pm-r-name { flex:1; }
.pm-r-count { width:60px; text-align:center; color:#909399; }
.pm-r-amount { width:100px; text-align:right; font-weight:600; }
</style>
