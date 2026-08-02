import { ref } from 'vue'
import { exportCSV, exportExcel } from '@/utils/export'

export type ReportExportFormat = 'csv' | 'excel'

/** 复用 CSV / Excel 导出 */
export function useReportExport() {
  const exportFormat = ref<ReportExportFormat>('csv')

  function exportRows(
    columns: { label: string; prop: string }[],
    rows: any[],
    filename: string,
  ) {
    if (exportFormat.value === 'excel') {
      exportExcel(columns, rows, filename)
    } else {
      exportCSV(columns, rows, filename)
    }
  }

  return { exportFormat, exportRows }
}
