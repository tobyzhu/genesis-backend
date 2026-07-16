/** 导出CSV文件 */
export function exportCSV(columns: { label: string; prop: string }[], data: any[], filename: string) {
  const BOM = '\uFEFF'
  const header = columns.map(c => c.label).join(',')
  const body = data.map(row =>
    columns.map(c => {
      const val = row[c.prop] ?? ''
      const str = String(val).replace(/"/g, '""')
      return `"${str}"`
    }).join(',')
  ).join('\n')
  const blob = new Blob([BOM + header + '\n' + body], { type: 'text/csv;charset=utf-8;' })
  download(blob, `${filename}.csv`)
}

/** 导出Excel（HTML表格格式，无需外置库） */
export function exportExcel(columns: { label: string; prop: string }[], data: any[], filename: string) {
  const rows = [
    `<tr>${columns.map(c => `<th>${c.label}</th>`).join('')}</tr>`,
    ...data.map(row =>
      `<tr>${columns.map(c => `<td>${row[c.prop] ?? ''}</td>`).join('')}</tr>`
    ),
  ].join('\n')

  const html = `<html xmlns:o="urn:schemas-microsoft-com:office:office"
  xmlns:x="urn:schemas-microsoft-com:office:excel"
  xmlns="http://www.w3.org/TR/REC-html40">
  <head><meta charset="UTF-8"><!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet>
  <x:Name>Sheet1</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet>
  </x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]--></head>
  <body><table>${rows}</table></body></html>`

  const blob = new Blob(['\uFEFF' + html], { type: 'application/vnd.ms-excel;charset=utf-8' })
  download(blob, `${filename}.xls`)
}

function download(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = name
  a.click()
  URL.revokeObjectURL(url)
}
