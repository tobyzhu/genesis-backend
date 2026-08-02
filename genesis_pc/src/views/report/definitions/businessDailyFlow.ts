import { fetchBusinessDailyFlow } from '@/api/report'
import type { ReportColumn, ReportDefinition, ReportKpiDef } from '@/types/report'

const LINE_COLUMNS: ReportColumn[] = [
  { label: '门店', prop: 'storecode', width: 60 },
  { label: '结账区', prop: 'cashposition', width: 70 },
  { label: '发生日期', prop: 'vsdate', width: 100 },
  { label: '发生时间', prop: 'vstime', width: 90 },
  { label: '类型', prop: 'ttype_label', width: 70 },
  { label: '代码', prop: 'srvcode', width: 90 },
  { label: '名称', prop: 'item_name', minWidth: 140 },
  { label: '数量', prop: 's_qty', width: 70, align: 'right', format: 'number' },
  { label: '单价', prop: 's_price', width: 90, align: 'right', format: 'money', summary: false },
  { label: '折扣率', prop: 'secdisc', width: 80, align: 'right', format: 'percent', summary: false },
  { label: '金额', prop: 's_mount', width: 100, align: 'right', format: 'money' },
  { label: '免单', prop: 'free_amount', width: 80, align: 'right', format: 'money' },
  { label: '现金类金额', prop: 'cash_amount', width: 100, align: 'right', format: 'money' },
  { label: '卡付类金额', prop: 'card_amount', width: 100, align: 'right', format: 'money' },
  { label: '赠送类金额', prop: 'send_amount', width: 100, align: 'right', format: 'money' },
  { label: '开单', prop: 'pmname', width: 80 },
  { label: '美疗师1', prop: 'assname1', width: 80 },
  { label: '美疗师2', prop: 'assname2', width: 80 },
  { label: '卡号', prop: 'ccode', width: 110 },
  { label: '会员号', prop: 'vcode', width: 90 },
  { label: '客人姓名', prop: 'vname', width: 80 },
  { label: '客人类型', prop: 'viptype_label', width: 90 },
  { label: '活动编号', prop: 'promotionsid', width: 90 },
  { label: '记账日期', prop: 'cdate', width: 100 },
  { label: '是否指定', prop: 'specified', width: 80 },
  { label: '付款信息', prop: 'pay_info', minWidth: 140 },
]

const SUMMARY_COLUMNS: ReportColumn[] = [
  { label: '日期', prop: 'vsdate', width: 100 },
  { label: '店号', prop: 'storecode', width: 70 },
  { label: '门店', prop: 'storename', minWidth: 120 },
  { label: '服务金额', prop: 'am_S', width: 110, align: 'right', format: 'money' },
  { label: '商品金额', prop: 'am_G', width: 110, align: 'right', format: 'money' },
  { label: '售卡金额', prop: 'am_C', width: 110, align: 'right', format: 'money' },
  { label: '充值金额', prop: 'am_I', width: 110, align: 'right', format: 'money' },
  { label: '合计', prop: 'total', width: 120, align: 'right', format: 'money' },
  { label: '单数', prop: 'trans_count', width: 70, align: 'right', format: 'number' },
]

const LINE_KPIS: ReportKpiDef[] = [
  { key: 'am_S', label: '服务金额', money: true },
  { key: 'am_G', label: '商品金额', money: true },
  { key: 'am_C', label: '售卡金额', money: true },
  { key: 'am_I', label: '充值金额', money: true },
  { key: 'total', label: '合计金额', money: true },
  { key: 'cash_amount', label: '现金类', money: true },
  { key: 'card_amount', label: '卡付类', money: true },
  { key: 'send_amount', label: '赠送类', money: true },
  { key: 'row_count', label: '明细行数' },
  { key: 'trans_count', label: '单据数' },
]

const SUMMARY_KPIS: ReportKpiDef[] = [
  { key: 'am_S', label: '服务金额', money: true },
  { key: 'am_G', label: '商品金额', money: true },
  { key: 'am_C', label: '售卡金额', money: true },
  { key: 'am_I', label: '充值金额', money: true },
  { key: 'total', label: '合计金额', money: true },
  { key: 'trans_count', label: '单据数' },
]

/** 营业流水表：默认消费明细行（对齐传统流水导出） */
export const businessDailyFlowDef: ReportDefinition = {
  id: 'business_daily_flow',
  title: '营业流水表',
  subtitle: '消费明细流水；可切换店×日 / 按店汇总',
  exportFilename: '营业流水表',
  showDateRange: true,
  defaultView: 'line',
  groupModeOptions: [
    { value: 'line', label: '明细' },
    { value: 'daily', label: '店×日' },
    { value: 'by_store', label: '按店合计' },
  ],
  kpis: LINE_KPIS,
  columns: LINE_COLUMNS,
  resolveColumns(_cols, _rows, ctx) {
    if (ctx.view === 'line') return LINE_COLUMNS
    if (ctx.view === 'by_store') {
      return SUMMARY_COLUMNS.filter(c => c.prop !== 'vsdate')
    }
    return SUMMARY_COLUMNS
  },
  resolveKpis(_kpis, ctx) {
    return ctx.view === 'line' ? LINE_KPIS : SUMMARY_KPIS
  },
  fetch: fetchBusinessDailyFlow,
}
