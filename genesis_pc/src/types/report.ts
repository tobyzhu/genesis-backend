export type StoreScopeMode = 'one' | 'multi' | 'all_allowed'
export type ReportViewMode = 'line' | 'daily' | 'detail' | 'by_store'

export interface ReportColumn {
  label: string
  prop: string
  width?: number | string
  minWidth?: number | string
  align?: 'left' | 'center' | 'right'
  format?: 'money' | 'text' | 'number' | 'percent'
  /** 是否参与表底合计；默认 money/number 为 true，文本列为 false */
  summary?: boolean
  /** 列头筛选；默认开启（唯一值过多时自动隐藏） */
  filterable?: boolean
}

export interface ReportViewOption {
  value: ReportViewMode
  label: string
}

export interface ReportKpiDef {
  key: string
  label: string
  money?: boolean
}

export interface ReportFetchParams {
  company: string
  storecodes: string[]
  from_date: string
  to_date: string
  view: ReportViewMode
  django_user_id?: number | string | null
  /** 报表自定义筛选（卡类型、关键字等） */
  extras?: Record<string, any>
}

export interface ReportEnvelope<T = any> {
  ok?: boolean
  meta?: Record<string, any>
  kpis?: Record<string, number>
  rows?: T[]
  totals?: Record<string, number>
  error?: string
}

export interface ReportDefinition<T = any> {
  id: string
  title: string
  subtitle?: string
  exportFilename: string
  columns: ReportColumn[]
  kpis: ReportKpiDef[]
  /** @deprecated 使用 groupModeOptions */
  groupModes?: ReportViewMode[]
  groupModeOptions?: ReportViewOption[]
  defaultView?: ReportViewMode
  /** 是否显示日期范围，默认 true；卡余额等快照报表可关 */
  showDateRange?: boolean
  /** 按当前数据 / 视图动态裁剪列 */
  resolveColumns?: (
    cols: ReportColumn[],
    rows: T[],
    ctx: { view: ReportViewMode },
  ) => ReportColumn[]
  /** 按视图切换 KPI（不提供则始终用 kpis） */
  resolveKpis?: (kpis: ReportKpiDef[], ctx: { view: ReportViewMode }) => ReportKpiDef[]
  fetch: (params: ReportFetchParams) => Promise<ReportEnvelope<T>>
}
