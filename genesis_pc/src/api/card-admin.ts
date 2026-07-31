import request from './request'

/** 获取逻辑卡规则列表 */
export function getRulerList(params?: Record<string, any>) {
  return request.get('/adviser/ruler-list/', { params })
}

/** 新增/编辑逻辑卡规则 */
export function saveRuler(data: Record<string, any>) {
  return request.post('/adviser/ruler-save/', data)
}

/** 软删除逻辑卡规则 */
export function deleteRuler(id: number | string) {
  return request.post('/adviser/ruler-delete/', { id })
}

/** 获取卡类折扣分类规则 */
export function getCardtypeDiscountRules(cardtype: string, params?: Record<string, any>) {
  return request.get('/adviser/cardtype-discount-list/', { params: { cardtype, ...params } })
}

/** 批量保存卡类折扣分类规则（全量替换） */
export function saveCardtypeDiscountRules(cardtype: string, rules: Array<Record<string, any>>) {
  return request.post('/adviser/cardtype-discount-save/', { cardtype, rules })
}

/** 批量计算卡支付单价与消费权限 */
export function getCardPricing(payload: Record<string, any>) {
  return request.post('/adviser/card-pricing/', payload)
}
