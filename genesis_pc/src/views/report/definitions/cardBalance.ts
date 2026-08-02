import { fetchCardBalanceReport } from '@/api/report'
import type { ReportColumn, ReportDefinition } from '@/types/report'

const BASE_COLUMNS: ReportColumn[] = [
  { label: '卡大类', prop: 'suptype_name', width: 90 },
  { label: '卡类', prop: 'cardtype_name', minWidth: 120 },
  { label: '模式', prop: 'comptype_label', width: 80 },
  { label: '品牌', prop: 'brand', width: 80 },
  { label: '正常张数', prop: 'normal_count', width: 80, align: 'right', format: 'number' },
  { label: '正常余额', prop: 'normal_leftmoney', width: 100, align: 'right', format: 'money' },
  { label: '正常余次', prop: 'normal_leftqty', width: 80, align: 'right', format: 'number' },
  { label: '赠送张数', prop: 'gift_count', width: 80, align: 'right', format: 'number' },
  { label: '赠送余额', prop: 'gift_leftmoney', width: 100, align: 'right', format: 'money' },
  { label: '赠送余次', prop: 'gift_leftqty', width: 80, align: 'right', format: 'number' },
  { label: '合计张数', prop: 'total_count', width: 80, align: 'right', format: 'number' },
  { label: '合计余额', prop: 'total_leftmoney', width: 110, align: 'right', format: 'money' },
  { label: '合计余次', prop: 'total_leftqty', width: 80, align: 'right', format: 'number' },
]

const TIMES_PROPS = new Set(['normal_leftqty', 'gift_leftqty', 'total_leftqty'])

/** 卡余额汇总：按可管门店卡类聚合 */
export const cardBalanceDef: ReportDefinition = {
  id: 'card_balance',
  title: '卡余额汇总',
  subtitle: '按可管门店汇总有效卡余额 / 余次',
  exportFilename: '卡余额汇总',
  showDateRange: false,
  kpis: [
    { key: 'card_count', label: '卡片总数' },
    { key: 'normal_amount', label: '正常余额', money: true },
    { key: 'gift_amount', label: '赠送余额', money: true },
    { key: 'total_amount', label: '总计余额', money: true },
    { key: 'normal_times', label: '正常余次' },
    { key: 'gift_times', label: '赠送余次' },
  ],
  columns: BASE_COLUMNS,
  resolveColumns(cols, rows) {
    const showTimes = rows.some(
      (r: any) => r.comptype === 'times' || Number(r.total_leftqty || 0) > 0,
    )
    if (showTimes) return cols
    return cols.filter(c => !TIMES_PROPS.has(c.prop))
  },
  fetch: fetchCardBalanceReport,
}
