import request from './request'
import type { PageResponse, Vip } from '@/types'

export function getVipList(params?: Record<string, any>) {
  return request.get<PageResponse<Vip>>('/crm/vip/', { params })
}

export function getVipDetail(uuid: string) {
  return request.get<Vip>(`/crm/vip/${uuid}/`)
}

export function createVip(data: Partial<Vip>) {
  return request.post<Vip>('/crm/vip/', data)
}

export function updateVip(uuid: string, data: Partial<Vip>) {
  return request.put<Vip>(`/crm/vip/${uuid}/`, data)
}

export function deleteVip(uuid: string) {
  return request.delete(`/crm/vip/${uuid}/`)
}

/** 获取筛选选项（等级等） */
export function getVipFilterOptions() {
  const company = localStorage.getItem('genesis_pc_company') || ''
  return request.get<{viplevels: string[]}>('/crm/vip_filter_options/', { params: { company } })
}

export function searchVip(keyword: string) {
  return request.get<PageResponse<Vip>>('/crm/vip/', { params: { search: keyword } })
}

/** 获取 appoption 选项（来店渠道等） */
export function getAppoptionBySeg(seg: string) {
  const company = localStorage.getItem('genesis_pc_company') || ''
  return request.get<Array<{itemname: string, itemvalues: string}>>('/baseinfo/get_appoption_byseg/', { params: { company, seg } })
}

/** 会员消费记录 */
export function getVipConsumption(vipUuid: string, params?: Record<string, any>) {
  const company = localStorage.getItem('genesis_pc_company') || ''
  return request.get('/crm/get_vipconsumelist/', { params: { vipuuid: vipUuid, company, ...params } })
}

/** 会员卡列表 */
export function getVipCards(vipUuid: string) {
  const cleaned = vipUuid.replace(/-/g, '')
  const company = localStorage.getItem('genesis_pc_company') || ''
  return request.get('/adviser/get_vip_cardlist/', { params: { vipuuid: cleaned, company } })
}


/** 获取会员沟通回访记录 */
export function getVipCommunication(vipUuid: string) {
  const company = localStorage.getItem('genesis_pc_company') || ''
  const cleaned = vipUuid.replace(/-/g, '')
  return request.get('/crm/get_vipcasedetail_byvipuuid/', {
    params: { company, vipuuid: cleaned, date_from: dateFrom || '', date_to: dateTo || '' },
  })
}

// ===== VIP 洞察 =====
export function getVipInsight(vipUuid: string, dateFrom?: string, dateTo?: string) {
  const company = localStorage.getItem('genesis_pc_company') || ''
  const cleaned = vipUuid.replace(/-/g, '')
  return request.get('/crm/vip_insight/', {
    params: { company, vipuuid: cleaned, date_from: dateFrom || '', date_to: dateTo || '' },
  })
}

// ===== 健康档案 =====
export function getHealthRecords(vipUuid: string) {
  const company = localStorage.getItem('genesis_pc_company') || ''
  const cleaned = vipUuid.replace(/-/g, '')
  return request.get('/crm/health_records/', {
    params: { company, vipuuid: cleaned, date_from: dateFrom || '', date_to: dateTo || '' },
  })
}

export function createHealthRecord(data: {
  vipuuid: string; skin_type?: string; allergies?: string;
  body_concerns?: string; contraindications?: string; notes?: string
}) {
  const company = localStorage.getItem('genesis_pc_company') || ''
  return request.post('/crm/health_records/', { company, ...data })
}

export function updateHealthRecord(uuid: string, data: Record<string, any>) {
  const company = localStorage.getItem('genesis_pc_company') || ''
  return request.put(`/crm/health_records/${uuid}/`, { company, ...data })
}

export function deleteHealthRecord(uuid: string) {
  return request.delete(`/crm/health_records/${uuid}/`)
}
