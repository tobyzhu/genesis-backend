import request from './request'

/** 获取商品大类树形结构 */
export function getGoodsctTree(params?: Record<string, any>) {
  return request.get<{tree: Array<Record<string, any>>}>('/adviser/goodsct-tree/', { params })
}

/** 新增/编辑商品大类 */
export function saveGoodsct(data: Record<string, any>) {
  return request.post('/adviser/goodsct-save/', data)
}

/** 软删除商品大类 */
export function deleteGoodsct(pk: number | string) {
  return request.post('/adviser/goodsct-delete/', { pk })
}

/** 获取商品快速列表 */
export function getGoodsFastList(params?: Record<string, any>) {
  return request.get('/adviser/goods-list/', { params })
}

/** 获取 Appoption 选项（品牌/显示分类等） */
export function getAppOptionList(seg: string, params?: Record<string, any>) {
  return request.get('/adviser/appoption-list/', { params: { seg, ...params } })
}
