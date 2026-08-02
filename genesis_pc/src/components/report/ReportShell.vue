<template>
  <div class="page report-shell">
    <div class="page-header">
      <div>
        <h3 class="page-title">{{ definition.title }}</h3>
        <span v-if="definition.subtitle" class="page-subtitle">{{ definition.subtitle }}</span>
      </div>
      <slot name="actions" />
    </div>

    <el-card shadow="never" class="filter-card">
      <div class="filter-bar">
        <template v-if="showDateRange">
          <span class="filter-label">日期：</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始"
            end-placeholder="结束"
            size="small"
            class="report-date-range"
            format="YYYY-MM-DD"
            value-format="YYYYMMDD"
          />
        </template>

        <StoreScopeFilter
          :stores="allowedStores"
          :current-storecode="currentStorecode"
          @change="onStoreScopeChange"
        />

        <el-radio-group
          v-if="viewOptions.length > 1"
          v-model="viewMode"
          size="small"
          @change="runQuery"
        >
          <el-radio-button
            v-for="opt in viewOptions"
            :key="opt.value"
            :value="opt.value"
          >{{ opt.label }}</el-radio-button>
        </el-radio-group>

        <slot name="filters" />

        <el-button size="small" type="primary" :loading="loading" @click="runQuery">
          查询
        </el-button>

        <el-radio-group v-model="exportFormat" size="small">
          <el-radio-button value="csv">CSV</el-radio-button>
          <el-radio-button value="excel">Excel</el-radio-button>
        </el-radio-group>
        <el-button size="small" :disabled="!rows.length" @click="onExport">导出</el-button>
      </div>
    </el-card>

    <div v-if="kpiCards.length" class="stat-grid report-kpis">
      <div v-for="k in kpiCards" :key="k.key" class="stat-card">
        <div class="stat-value" :class="{ money: k.money }">{{ k.display }}</div>
        <div class="stat-label">{{ k.label }}</div>
      </div>
    </div>

    <el-alert
      v-if="error"
      type="error"
      :title="error"
      show-icon
      :closable="false"
      style="margin-top: 12px"
    />
    <el-alert
      v-else-if="truncatedTip"
      type="warning"
      :title="truncatedTip"
      show-icon
      :closable="false"
      style="margin-top: 12px"
    />

    <el-card shadow="never" class="report-table-card">
      <slot name="table" :rows="rows" :loading="loading" :columns="visibleColumns">
        <el-table
          :data="rows"
          size="small"
          stripe
          show-summary
          :summary-method="getSummaries"
          sum-text="合计"
          v-loading="loading"
          max-height="calc(100vh - 320px)"
          class="report-data-table"
          style="width: 100%"
        >
          <el-table-column
            v-for="col in visibleColumns"
            :key="`${col.prop}-${filterEpoch}`"
            :label="col.label"
            :prop="col.prop"
            :width="col.width"
            :min-width="col.minWidth"
            :align="col.align || 'left'"
            :filters="columnFilterOptions[col.prop]"
            :filter-method="columnFilterOptions[col.prop] ? filterMethod : undefined"
            :filter-multiple="true"
            filter-placement="bottom-end"
          >
            <template #default="{ row }">
              {{ formatCell(row, col) }}
            </template>
          </el-table-column>
        </el-table>
      </slot>

      <el-empty v-if="!rows.length && !loading && !error" description="暂无数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import StoreScopeFilter from '@/components/report/StoreScopeFilter.vue'
import { useReportContext } from '@/composables/useReportContext'
import { useReportQuery } from '@/composables/useReportQuery'
import { useReportExport } from '@/composables/useReportExport'
import type { ReportColumn, ReportDefinition, ReportViewMode } from '@/types/report'

const props = withDefaults(defineProps<{
  definition: ReportDefinition
  extras?: Record<string, any>
}>(), {
  extras: () => ({}),
})

const { company, allowedStores, currentStorecode, djangoUserId } = useReportContext()
const { exportFormat, exportRows } = useReportExport()

const today = new Date()
const from = new Date(today)
from.setDate(today.getDate() - 29)

function fmt(d: Date): string {
  return (
    d.getFullYear()
    + String(d.getMonth() + 1).padStart(2, '0')
    + String(d.getDate()).padStart(2, '0')
  )
}

const dateRange = ref<[string, string]>([fmt(from), fmt(today)])
const storecodes = ref<string[]>([])
const viewMode = ref<ReportViewMode>(props.definition.defaultView || 'line')

const showDateRange = computed(() => props.definition.showDateRange !== false)

const viewOptions = computed(() => {
  if (props.definition.groupModeOptions?.length) {
    return props.definition.groupModeOptions
  }
  const modes = props.definition.groupModes || []
  const labelMap: Record<string, string> = {
    line: '明细',
    daily: '店×日',
    detail: '店×日',
    by_store: '按店合计',
  }
  return modes.map(value => ({ value, label: labelMap[value] || value }))
})

const { loading, rows, kpis, meta, error, refresh } = useReportQuery(() =>
  props.definition.fetch({
    company: company.value,
    storecodes: storecodes.value,
    from_date: showDateRange.value ? (dateRange.value?.[0] || '') : '',
    to_date: showDateRange.value ? (dateRange.value?.[1] || '') : '',
    view: viewMode.value,
    django_user_id: djangoUserId.value,
    extras: props.extras || {},
  }),
)

const truncatedTip = computed(() => {
  if (!meta.value?.truncated) return ''
  const lim = meta.value.limit || 5000
  return `明细结果已截断为前 ${lim} 行，请缩小日期或门店范围后再查`
})

const FILTER_MAX_OPTIONS = 80

const visibleColumns = computed(() => {
  let cols = props.definition.columns
  if (props.definition.resolveColumns) {
    cols = props.definition.resolveColumns(cols, rows.value, { view: viewMode.value })
  } else if (viewMode.value === 'by_store') {
    cols = cols.filter(c => c.prop !== 'vsdate')
  }
  return cols
})

/** 数据刷新后重建列筛选选项（避免 EP 缓存旧 filters） */
const filterEpoch = computed(() => `${rows.value.length}:${viewMode.value}:${dateRange.value?.join('-')}`)

const columnFilterOptions = computed(() => {
  const map: Record<string, Array<{ text: string; value: string }>> = {}
  for (const col of visibleColumns.value) {
    if (col.filterable === false) continue
    const seen = new Set<string>()
    const opts: Array<{ text: string; value: string }> = []
    for (const row of rows.value) {
      const raw = row?.[col.prop]
      const key = raw === null || raw === undefined || raw === '' ? '' : String(raw)
      if (seen.has(key)) continue
      seen.add(key)
      opts.push({ text: formatFilterLabel(col, raw), value: key })
      if (opts.length > FILTER_MAX_OPTIONS) break
    }
    if (!opts.length || opts.length > FILTER_MAX_OPTIONS) continue
    opts.sort((a, b) => a.text.localeCompare(b.text, 'zh-CN', { numeric: true }))
    map[col.prop] = opts
  }
  return map
})

const activeKpis = computed(() => {
  const base = props.definition.kpis
  if (props.definition.resolveKpis) {
    return props.definition.resolveKpis(base, { view: viewMode.value })
  }
  return base
})

const kpiCards = computed(() =>
  activeKpis.value.map((def) => {
    const raw = kpis.value[def.key]
    const num = typeof raw === 'number' ? raw : Number(raw || 0)
    return {
      key: def.key,
      label: def.label,
      money: !!def.money,
      display: def.money ? `¥${num.toFixed(2)}` : String(Math.round(num)),
    }
  }),
)

function colNeedsSummary(col: ReportColumn) {
  if (col.summary === true) return true
  if (col.summary === false) return false
  return col.format === 'money' || col.format === 'number'
}

function formatCell(row: any, col: ReportColumn) {
  const val = row?.[col.prop]
  if (col.format === 'money') {
    return `¥${Number(val || 0).toFixed(2)}`
  }
  if (col.format === 'percent') {
    return `${Number(val || 0).toFixed(2)}%`
  }
  if (col.format === 'number') {
    const n = Number(val || 0)
    // 数量等允许一位小数
    if (Number.isInteger(n)) return String(n)
    return n.toFixed(1).replace(/\.0$/, '')
  }
  if (val === null || val === undefined || val === '') return '--'
  return String(val)
}

function formatFilterLabel(col: ReportColumn, raw: unknown) {
  if (raw === null || raw === undefined || raw === '') return '(空)'
  if (col.format === 'money') return `¥${Number(raw || 0).toFixed(2)}`
  if (col.format === 'percent') return `${Number(raw || 0).toFixed(2)}%`
  return String(raw)
}

function filterMethod(value: string, row: any, column: { property?: string }) {
  const prop = column.property || ''
  const raw = row?.[prop]
  const key = raw === null || raw === undefined || raw === '' ? '' : String(raw)
  return key === value
}

function formatSummaryValue(col: ReportColumn, raw: number) {
  if (col.format === 'money') return `¥${Number(raw || 0).toFixed(2)}`
  if (col.format === 'number') return String(Math.round(Number(raw || 0)))
  if (Number.isInteger(raw)) return String(raw)
  return Number(raw || 0).toFixed(2)
}

function getSummaries(param: { columns: Array<{ property?: string }>; data: any[] }) {
  const { columns: tableCols, data } = param
  const cols = visibleColumns.value
  let labelPlaced = false

  // 按当前筛选后的 data 汇总，与表内可见行一致
  return tableCols.map((tableCol) => {
    const prop = tableCol.property || ''
    const col = cols.find(c => c.prop === prop)
    if (!col) return ''

    if (colNeedsSummary(col)) {
      const sum = data.reduce((acc, row) => acc + Number(row?.[col.prop] || 0), 0)
      return formatSummaryValue(col, sum)
    }

    if (!labelPlaced) {
      labelPlaced = true
      return '合计'
    }
    return ''
  })
}

function onStoreScopeChange(codes: string[]) {
  storecodes.value = codes
}

async function runQuery() {
  if (!company.value) {
    error.value = '未选择公司'
    rows.value = []
    return
  }
  if (!storecodes.value.length) {
    error.value = '请选择至少一家门店'
    rows.value = []
    return
  }
  await refresh()
}

function onExport() {
  const cols = visibleColumns.value.map(c => ({ label: c.label, prop: c.prop }))
  const exportData = rows.value.map((row: any) => {
    const out: Record<string, any> = {}
    for (const c of visibleColumns.value) {
      if (c.format === 'money') out[c.prop] = Number(row[c.prop] || 0).toFixed(2)
      else out[c.prop] = row[c.prop] ?? ''
    }
    return out
  })
  const fn = `${props.definition.exportFilename}_${new Date().toISOString().slice(0, 10)}`
  exportRows(cols, exportData, fn)
}

onMounted(() => {
  // StoreScopeFilter 挂载后会 emit；稍后再查，避免空 storecodes
  setTimeout(() => {
    if (storecodes.value.length) runQuery()
  }, 0)
})
</script>

<style scoped>
.filter-card { margin-bottom: 0; }
.filter-label {
  font-size: 13px;
  color: var(--g-color-text-secondary);
  white-space: nowrap;
}
/* 展示 YYYY-MM-DD（最多 10 字符）：输入框按 10ch 定宽，整体随内容贴边 */
.report-date-range.el-date-editor {
  --el-date-editor-width: fit-content;
  width: fit-content !important;
  max-width: none;
  padding: 0 2px 0 4px;
  justify-content: flex-start;
  gap: 0;
}
.report-date-range :deep(.el-range-input) {
  box-sizing: content-box;
  width: 10ch !important;
  flex: 0 0 10ch !important;
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0;
}
.report-date-range :deep(.el-range-separator) {
  flex: 0 0 auto;
  width: auto;
  padding: 0 1px;
  margin: 0;
  line-height: 24px;
  font-size: 12px;
}
.report-date-range :deep(.el-range__icon) {
  width: 12px;
  margin: 0 1px 0 0;
  font-size: 12px;
}
.report-date-range :deep(.el-range__close-icon) {
  width: 12px;
  margin: 0;
  font-size: 12px;
}
.report-kpis { margin-top: 12px; }
.report-table-card { margin-top: 12px; }
.stat-value.money { color: var(--g-color-money); }
.report-data-table :deep(.el-table__footer-wrapper td) {
  font-weight: 600;
  color: var(--g-color-text);
  background: var(--g-color-surface-muted);
}
.report-data-table :deep(.el-table__footer-wrapper .cell) {
  font-variant-numeric: tabular-nums;
}
</style>
