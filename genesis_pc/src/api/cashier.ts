import request from './request'
import type { CartableItem } from '@/types'

const company = () => localStorage.getItem('genesis_pc_company') || ''

/** 获取可售服务项目 */
export function getServiceItems() {
  return request.get('/cashier/service_items/', { params: { company: company() } })
}

/** 获取可售商品 */
export function getGoodsItems() {
  return request.get('/cashier/goods_items/', { params: { company: company() } })
}

/** 获取卡类定义 */
export function getCardtypeItems() {
  return request.get('/cashier/cardtype_items/', { params: { company: company() } })
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
