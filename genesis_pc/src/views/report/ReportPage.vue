<template>
  <div>
    <h2 style="margin:0 0 16px 0;font-size:18px;font-weight:600">卡余额汇总</h2>

    <el-card shadow="never" class="filter-card">
      <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">
        <span style="font-size:13px;color:#606266">门店：</span>
        <el-select v-model="filterStore" size="small" style="width:120px" clearable placeholder="全部">
          <el-option label="全部" value="" />
          <el-option v-for="s in storeOptions" :key="s.storecode" :label="s.storename" :value="s.storecode" />
        </el-select>

        <span style="font-size:13px;color:#606266">卡类型：</span>
        <el-select v-model="filterComptype" size="small" style="width:110px" clearable placeholder="全部">
          <el-option label="全部" value="" />
          <el-option label="储值卡" value="amount" />
          <el-option label="疗程卡" value="times" />
        </el-select>

        <span style="font-size:13px;color:#606266">属性：</span>
        <el-select v-model="filterNature" size="small" style="width:100px" clearable placeholder="全部">
          <el-option label="全部" value="" />
          <el-option label="正常" value="正常" />
          <el-option label="赠送" value="赠送" />
        </el-select>

        <el-input v-model="filterKeyword" placeholder="卡号/会员号/卡类" clearable size="small" style="width:200px" @keyup.enter="fetchData" />
        <el-button size="small" type="primary" @click="fetchData">查询</el-button>
        <el-radio-group v-model="exportFormat" size="small">
          <el-radio-button value="csv">CSV</el-radio-button>
          <el-radio-button value="excel">Excel</el-radio-button>
        </el-radio-group>
        <el-button size="small" @click="exportData">导出</el-button>
        <el-checkbox v-model="onlyWithBalance" size="small">仅显示有余额</el-checkbox>
      </div>
    </el-card>

    <el-card shadow="never" style="margin-top:16px">
      <el-table :data="rows" size="small" stripe v-loading="loading" max-height="calc(100vh - 300px)">
        <el-table-column label="卡大类" width="80">
          <template #default="{ row }">{{ row.suptype_name || '—' }}</template>
        </el-table-column>
        <el-table-column label="卡类" min-width="120">
          <template #default="{ row }">{{ row.cardtype_name || row.cardtype_code || '—' }}</template>
        </el-table-column>
        <el-table-column label="模式" width="80">
          <template #default="{ row }">{{ row.comptype_label || '—' }}</template>
        </el-table-column>
        <el-table-column label="品牌" width="80">
          <template #default="{ row }">{{ row.brand || '—' }}</template>
        </el-table-column>
        <el-table-column label="正常张数" width="80" align="right">
          <template #default="{ row }">{{ row.normal_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="正常余额" width="100" align="right">
          <template #default="{ row }">¥{{ (row.normal_leftmoney || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column v-if="showTimesCol" label="正常余次" width="80" align="right">
          <template #default="{ row }">{{ Math.round(row.normal_leftqty || 0) }}</template>
        </el-table-column>
        <el-table-column label="赠送张数" width="80" align="right">
          <template #default="{ row }">{{ row.gift_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="赠送余额" width="100" align="right">
          <template #default="{ row }">¥{{ (row.gift_leftmoney || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column v-if="showTimesCol" label="赠送余次" width="80" align="right">
          <template #default="{ row }">{{ Math.round(row.gift_leftqty || 0) }}</template>
        </el-table-column>
        <el-table-column label="合计张数" width="80" align="right">
          <template #default="{ row }">{{ row.total_count || 0 }}</template>
        </el-table-column>
        <el-table-column label="合计余额" width="110" align="right">
          <template #default="{ row }">¥{{ (row.total_leftmoney || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column v-if="showTimesCol" label="合计余次" width="80" align="right">
          <template #default="{ row }">{{ Math.round(row.total_leftqty || 0) }}</template>
        </el-table-column>
      </el-table>

      <div v-if="grand.card_count > 0" class="grand-total">
        <span>合计：{{ grand.card_count }} 张卡，正常余额 ¥{{ (grand.normal_amount || 0).toFixed(2) }}，赠送余额 ¥{{ (grand.gift_amount || 0).toFixed(2) }}</span>
        <span v-if="grand.total_times > 0">，正常余次 {{ Math.round(grand.normal_times) }}，赠送余次 {{ Math.round(grand.gift_times) }}</span>
        <span>，总计 ¥{{ (grand.total_amount || 0).toFixed(2) }}</span>
      </div>

      <el-empty v-if="!rows.length && !loading" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import request from '@/api/request'

const company = localStorage.getItem('genesis_pc_company') || ''

const filterStore = ref('')
const filterComptype = ref('')
const filterNature = ref('')
const filterKeyword = ref('')
const onlyWithBalance = ref(true)
const loading = ref(false)
const rows = ref<any[]>([])
const grand = ref<any>({ card_count: 0 })
const storeOptions = ref<Array<{storecode: string, storename: string}>>([])

const showTimesCol = computed(() => rows.value.some(r => r.comptype === 'times'))

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, string> = { company }
    if (filterStore.value) params.storecode = filterStore.value
    if (filterComptype.value) params.comptype = filterComptype.value
    if (filterNature.value) params.nature = filterNature.value
    if (filterKeyword.value) params.keyword = filterKeyword.value
    params.only_with_balance = onlyWithBalance.value ? '1' : '0'

    const res = await request.get('/report/card_balance_report_api/', { params })
    const data = res.data || {}
    rows.value = data.summary_rows || []
    grand.value = data.grand_totals || { card_count: 0 }
  } catch {
    rows.value = []
    grand.value = { card_count: 0 }
  }
  finally { loading.value = false }
}

function resetFilter() {
  filterStore.value = ''
  filterComptype.value = ''
  filterNature.value = ''
  filterKeyword.value = ''
  onlyWithBalance.value = true
  fetchData()
}

onMounted(() => {
  fetchData()
  request.get('/common/company_stores/', { params: { company } }).then(res => {
    const list = Array.isArray(res.data) ? res.data : res.data?.results ?? []
    storeOptions.value = list.map((s: any) => ({ storecode: s.storecode || '', storename: s.storename || s.storecode || '' }))
  }).catch(() => {})
})

// 导出相关
const exportFormat = ref('csv')
const exportColumns = [
  { label: '卡大类', prop: 'suptype_name' },
  { label: '卡类', prop: 'cardtype_name' },
  { label: '模式', prop: 'comptype_label' },
  { label: '品牌', prop: 'brand' },
  { label: '正常张数', prop: 'normal_count' },
  { label: '正常余额', prop: 'normal_leftmoney' },
  { label: '正常余次', prop: 'normal_leftqty' },
  { label: '赠送张数', prop: 'gift_count' },
  { label: '赠送余额', prop: 'gift_leftmoney' },
  { label: '赠送余次', prop: 'gift_leftqty' },
  { label: '总计余额', prop: 'total_leftmoney' },
]

function exportData() {
  const fn = '卡余额汇总_' + new Date().toISOString().slice(0, 10)
  if (exportFormat.value === 'csv') exportCSV(exportColumns, rows.value, fn)
  else exportExcel(exportColumns, rows.value, fn)
}
</script>

<style scoped>
.grand-total { margin-top:12px; padding:10px 12px; background:#f5f7fa; border-radius:6px; font-size:14px; font-weight:600; color:#303133; }
</style>
