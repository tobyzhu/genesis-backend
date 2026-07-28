import request from './request'
import { getCache, setCache, cacheKey } from '@/utils/cache'
import type { CartableItem } from '@/types'

const company = () => localStorage.getItem('genesis_pc_company') || ''

/** 带缓存的 GET 请求 */
async function cachedGet<T = any>(url: string, params: Record<string, string>, ttlMs: number) {
  const key = cacheKey(url, params)
  const cached = getCache<T>(key)
  if (cached !== null) {
    return { data: cached } as any
  }
  const res = await request.get(url, { params })
  if (res.data !== undefined && res.data !== null) {
    setCache(key, res.data as T, ttlMs)
  }
  return res
}

/** 获取可售服务项目 */
export function getServiceItems() {
  return cachedGet<CartableItem[]>('/cashier/service_items/', { company: company() }, 30 * 60 * 1000)
}

/** 获取可售商品 */
export function getGoodsItems() {
  return cachedGet<CartableItem[]>('/cashier/goods_items/', { company: company() }, 30 * 60 * 1000)
}

/** 获取卡类定义 */
export function getCardtypeItems() {
  return cachedGet<CartableItem[]>('/cashier/cardtype_items/', { company: company() }, 30 * 60 * 1000)
}

/** 获取卡类关联的服务项目 */
export function getCardtypeServiceItems(cardtypeuuid: string, cardtype?: string) {
  return request.get('/adviser/cardtype_service_items/', { params: { company: company(), cardtypeuuid, cardtype } })
}

/** 获取卡类疗程价格选项 */
export function getCardtypePrices(cardtype: string) {
  return request.get<CartableItem[]>('/adviser/cardtype_prices/', { params: { company: company(), cardtype } })
}

/** 保存挂账单 */
export function saveHungOrder(data: {
  vipuuid: string
  storecode: string
  items: Array<{
    ttype: string
    srvcode: string
    s_qty: number
    s_price: number
    pay_type: string    // cash / card:ccode
    card_ccode?: string
  }>
}) {
  return request.post('/adviser/save_hung/', { ...data, company: company() })
}

/** 获取已完成开单列表 */
export function getCompletedHungs(params: {
  page?: number
  page_size?: number
  date_from?: string
  date_to?: string
  keyword?: string
}) {
  return request.get('/adviser/get_completed_hungs/', {
    params: { company: company(), ...params },
  })
}

/** 获取已完成开单详情 */
export function getCompletedOrderDetail(hunguuid: string) {
  return request.get('/adviser/get_completed_order_detail/', {
    params: { company: company(), hunguuid },
  })
}


/** 获取分类树 + 项目列表 */
export function getCategorizedItems(ttype: string) {
  // 分类树缓存 30 分钟
  return cachedGet('/adviser/categorized_items/', { company: company(), ttype }, 30 * 60 * 1000)
}


/** 获取会员已完成开单（退款用） */
export function getHungByVipUuid(vipuuid: string) {
  return request.get('/adviser/get_hung_byvipuuid/', {
    params: { company: company(), vipuuid },
  })
}

/** 获取挂单明细 */
export function getHungDetail(hunguuid: string) {
  return request.get('/adviser/get_hung_detail/', {
    params: { company: company(), hunguuid },
  })
}


/** 获取会员已结账的订单（用于退款） */
export function getCheckedOutOrders(vipuuid: string, dateFrom?: string, dateTo?: string) {
  const sc = localStorage.getItem('genesis_pc_storecode') || ''
  const params: Record<string, string> = { company: company(), storecode: sc, vipuuid }
  if (dateFrom) params.date_from = dateFrom
  if (dateTo) params.date_to = dateTo
  return request.get('/cashier/get_checkedout_orders/', { params })
}


/** 获取当前有效的营销活动 */
export function getActivePromotions(uuid?: string) {
  const params: Record<string, string> = { company: company() }
  if (uuid) {
    params.uuid = uuid
    return request.get('/adviser/active_promotions/', { params })
  }
  // 活动列表缓存 10 分钟
  return cachedGet<any[]>('/adviser/active_promotions/', params, 10 * 60 * 1000)
}
