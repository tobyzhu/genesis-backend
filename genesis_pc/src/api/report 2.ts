import request from './request'
import type { ReportRow } from '@/types'

/** 业绩报表 */
export function getPerformanceReport(params?: Record<string, any>) {
  return request.get<ReportRow[]>('/report/performance/', { params })
}

/** 卡类销售报表 */
export function getCardSalesReport(params?: Record<string, any>) {
  return request.get<ReportRow[]>('/report/card_sales/', { params })
}

/** 经营汇总 */
export function getBusinessSummary(params?: Record<string, any>) {
  return request.get<ReportRow[]>('/report/summary/', { params })
}

/** 员工业绩 */
export function getEmployeeReport(params?: Record<string, any>) {
  return request.get('/report/employee/', { params })
}
