import request from './request'
import type { ReportEnvelope, ReportFetchParams } from '@/types/report'

function baseReportParams(params: ReportFetchParams): Record<string, string> {
  const q: Record<string, string> = {
    company: params.company,
    storecodes: (params.storecodes || []).join(','),
  }
  if (params.django_user_id != null && params.django_user_id !== '') {
    q.django_user_id = String(params.django_user_id)
  }
  return q
}

/** 营业流水表（店×日 / 按店合计） */
export async function fetchBusinessDailyFlow(
  params: ReportFetchParams,
): Promise<ReportEnvelope> {
  const q = {
    ...baseReportParams(params),
    from_date: params.from_date || '',
    to_date: params.to_date || '',
    view: params.view || 'line',
  }
  const res = await request.get('/report/business_daily_flow_api/', { params: q })
  return res.data
}

/** 卡余额汇总 */
export async function fetchCardBalanceReport(
  params: ReportFetchParams,
): Promise<ReportEnvelope> {
  const extras = params.extras || {}
  const q: Record<string, string> = {
    ...baseReportParams(params),
    only_with_balance: extras.only_with_balance === false ? '0' : '1',
  }
  if (extras.comptype) q.comptype = String(extras.comptype)
  if (extras.nature) q.nature = String(extras.nature)
  if (extras.keyword) q.keyword = String(extras.keyword)
  const res = await request.get('/report/card_balance_report_api/', { params: q })
  return res.data
}
