import { ref, type Ref } from 'vue'

export interface ReportEnvelope<T = any> {
  ok?: boolean
  meta?: Record<string, any>
  kpis?: Record<string, number>
  rows?: T[]
  totals?: Record<string, number>
  error?: string
}

/** loading / rows / error / refresh 通用报表查询状态 */
export function useReportQuery<T = any>(
  fetcher: () => Promise<ReportEnvelope<T>>,
) {
  const loading = ref(false)
  const rows: Ref<T[]> = ref([])
  const kpis = ref<Record<string, number>>({})
  const totals = ref<Record<string, number>>({})
  const meta = ref<Record<string, any>>({})
  const error = ref('')

  async function refresh() {
    loading.value = true
    error.value = ''
    try {
      const data = await fetcher()
      if (data?.ok === false && data.error) {
        error.value = data.error
        rows.value = []
        kpis.value = {}
        totals.value = {}
        meta.value = data.meta || {}
        return data
      }
      rows.value = Array.isArray(data?.rows) ? data.rows : []
      kpis.value = data?.kpis || {}
      totals.value = data?.totals || {}
      meta.value = data?.meta || {}
      return data
    } catch (e: any) {
      error.value = e?.response?.data?.error || e?.message || '查询失败'
      rows.value = []
      kpis.value = {}
      totals.value = {}
      meta.value = {}
      return null
    } finally {
      loading.value = false
    }
  }

  return { loading, rows, kpis, totals, meta, error, refresh }
}
