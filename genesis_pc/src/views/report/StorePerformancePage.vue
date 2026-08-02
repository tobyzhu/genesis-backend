<template>
  <div>
    <div class="page-header" style="margin-bottom:12px">
      <h3 class="page-title">门店业绩流水表</h3>
    </div>

    <el-card shadow="never" class="filter-card">
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
        <span style="font-size:13px;color:var(--g-color-text-secondary);white-space:nowrap">日期：</span>
        <el-date-picker v-model="dateRange" type="daterange" range-separator="至"
          start-placeholder="开始日期" end-placeholder="结束日期"
          size="small" style="width:260px" value-format="YYYYMMDD" />
        <span style="font-size:13px;color:var(--g-color-text-secondary);white-space:nowrap">门店：</span>
        <el-select v-model="filterStore" size="small" style="width:120px" clearable placeholder="全部">
          <el-option label="全部" value="" />
          <el-option v-for="s in storeOptions" :key="s.storecode" :label="s.storename" :value="s.storecode" />
        </el-select>
        <el-button size="small" type="primary" @click="fetchData">查询</el-button>
        <el-radio-group v-model="exportFormat" size="small">
          <el-radio-button value="csv">CSV</el-radio-button>
          <el-radio-button value="excel">Excel</el-radio-button>
        </el-radio-group>
        <el-button size="small" @click="exportData">导出</el-button>
      </div>
    </el-card>

    <div class="stat-grid perf-stats">
      <div class="stat-card"><div class="stat-value money">¥{{ totals.am_S.toFixed(2) }}</div><div class="stat-label">服务金额</div></div>
      <div class="stat-card"><div class="stat-value money">¥{{ totals.am_G.toFixed(2) }}</div><div class="stat-label">商品金额</div></div>
      <div class="stat-card"><div class="stat-value money">¥{{ totals.am_C.toFixed(2) }}</div><div class="stat-label">售卡金额</div></div>
      <div class="stat-card"><div class="stat-value money">¥{{ totals.am_I.toFixed(2) }}</div><div class="stat-label">充值金额</div></div>
      <div class="stat-card"><div class="stat-value money">¥{{ totals.total.toFixed(2) }}</div><div class="stat-label">合计金额</div></div>
    </div>

    <el-card shadow="never" style="margin-top:16px">
      <el-table :data="rows" size="small" stripe v-loading="loading" max-height="calc(100vh - 280px)">
        <el-table-column label="日期" width="90">
          <template #default="{ row }">{{ row.vsdate || '--' }}</template>
        </el-table-column>
        <el-table-column label="门店" width="60">
          <template #default="{ row }">{{ row.storecode || '--' }}</template>
        </el-table-column>
        <el-table-column label="服务金额" width="110" align="right">
          <template #default="{ row }">¥{{ (row.am_S || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="商品金额" width="110" align="right">
          <template #default="{ row }">¥{{ (row.am_G || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="售卡金额" width="110" align="right">
          <template #default="{ row }">¥{{ (row.am_C || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="充值金额" width="110" align="right">
          <template #default="{ row }">¥{{ (row.am_I || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="合计" width="120" align="right">
          <template #default="{ row }">¥{{ (row.total || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="单数" width="55" align="right">
          <template #default="{ row }">{{ row.trans_count || 0 }}</template>
        </el-table-column>
      </el-table>

      <div v-if="totals.total > 0" class="grand-total">
        <span>合计：服务 ¥{{ totals.am_S.toFixed(2) }} | 商品 ¥{{ totals.am_G.toFixed(2) }} | 售卡 ¥{{ totals.am_C.toFixed(2) }} | 充值 ¥{{ totals.am_I.toFixed(2) }} | 总计 ¥{{ totals.total.toFixed(2) }}</span>
      </div>
      <el-empty v-if="!rows.length && !loading" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/api/request'
import { exportCSV, exportExcel } from '@/utils/export'
import { useAppStore } from '@/store/app'

const appStore = useAppStore()
const company = appStore.currentCompany || localStorage.getItem('genesis_pc_company') || ''

const exportFormat = ref('csv')
const exportColumns = [
  { label: '日期', prop: 'vsdate' },
  { label: '门店', prop: 'storecode' },
  { label: '服务金额', prop: 'am_S' },
  { label: '商品金额', prop: 'am_G' },
  { label: '售卡金额', prop: 'am_C' },
  { label: '充值金额', prop: 'am_I' },
  { label: '合计', prop: 'total' },
  { label: '单数', prop: 'trans_count' },
]

function exportData() {
  const fn = '门店业绩流水_' + new Date().toISOString().slice(0,10)
  if (exportFormat.value === 'csv') exportCSV(exportColumns, rows.value, fn)
  else exportExcel(exportColumns, rows.value, fn)
}

const year = new Date().getFullYear()
const month = new Date().getMonth()
const today = new Date()
const thirtyDaysAgo = new Date(year, month, today.getDate() - 29)

function fmt(d: Date): string {
  return d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0')
}

const dateRange = ref<[string, string]>([fmt(thirtyDaysAgo), fmt(today)])
const filterStore = ref('')
const loading = ref(false)
const rows = ref<any[]>([])
const storeOptions = ref<Array<{storecode: string, storename: string}>>([])

const totals = computed(() => {
  const t = { am_S: 0, am_G: 0, am_C: 0, am_I: 0, total: 0 }
  for (const r of rows.value) {
    t.am_S += r.am_S || 0
    t.am_G += r.am_G || 0
    t.am_C += r.am_C || 0
    t.am_I += r.am_I || 0
    t.total += r.total || 0
  }
  return t
})

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, string> = { company }
    if (dateRange.value) {
      params.from_date = dateRange.value[0]
      params.to_date = dateRange.value[1]
    }
    if (filterStore.value) params.storecode = filterStore.value
    const res = await request.get('/report/store_performance_api/', { params })
    rows.value = Array.isArray(res.data) ? res.data : []
  } catch { rows.value = [] }
  finally { loading.value = false }
}

onMounted(() => {
  if (!appStore.allowedStores.length && appStore.user?.stores?.length) {
    appStore.setAllowedStores(appStore.user.stores)
  }
  storeOptions.value = [...appStore.allowedStores]
  fetchData()
})
</script>

<style scoped>
.grand-total { margin-top:12px; padding:8px 12px; background:var(--g-color-surface-muted); border-radius:6px; font-size:13px; color:var(--g-color-text-secondary); }
.perf-stats { margin-top: 16px; }
.stat-value.money { color: var(--g-color-money); }
</style>
