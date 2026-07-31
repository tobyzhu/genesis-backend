import request from './request'

/** 获取服务大类树形结构 */
export function getSrvtoptyTree(params?: Record<string, any>) {
  return request.get<{tree: Array<Record<string, any>>}>('/adviser/srvtopty-tree/', { params })
}

/** 获取服务项目列表（按分类筛选） */
export function getServieceList(params?: Record<string, any>) {
  return request.get('/adviser/sysadmin-data/baseinfo.serviece/', { params })
}

/** 获取服务项目快速列表（只取列表所需字段） */
export function getServieceFastList(params?: Record<string, any>) {
  return request.get('/adviser/serviece-list/', { params })
}

/** 获取服务项目元数据 */
export function getServieceMeta() {
  return request.get('/adviser/sysadmin-models/baseinfo.serviece/meta/')
}

/** 新增/编辑服务大类 */
export function saveSrvtopty(data: Record<string, any>) {
  return request.post('/adviser/srvtopty-save/', data)
}

/** 软删除服务大类 */
export function deleteSrvtopty(pk: number) {
  return request.post('/adviser/srvtopty-delete/', { pk })
}

/** 获取 Appoption 选项（品牌/显示分类等） */
export function getAppOptionList(seg: string, params?: Record<string, any>) {
  return request.get('/adviser/appoption-list/', { params: { seg, ...params } })
}

/** 获取服务项目价位 */
export function getServiecePrices(srvcode: string) {
  return request.get('/adviser/servieceprice-list/', { params: { srvcode } })
}

/** 批量保存服务项目价位 */
export function saveServiecePrices(srvcode: string, prices: Array<Record<string, any>>) {
  return request.post('/adviser/servieceprice-save/', { srvcode, prices })
}
