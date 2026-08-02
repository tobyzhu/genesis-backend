import request from './request'

/** 获取模型列表（分组） */
export function getModelGroups() {
  return request.get<{groups: Array<{name: string; models: Array<{id: string; verbose_name: string; icon: string}>}>}>('/adviser/sysadmin-models/')
}

/** 获取字段元数据 */
export function getModelMeta(appLabel: string, modelName: string) {
  return request.get(`/adviser/sysadmin-models/${appLabel}.${modelName}/meta/`)
}

/** 获取数据列表 */
export function getModelData(appLabel: string, modelName: string, params?: Record<string, any>) {
  return request.get<{total: number; page: number; page_size: number; rows: any[]}>(`/adviser/sysadmin-data/${appLabel}.${modelName}/`, { params })
}

/** 新建记录 */
export function createModelData(appLabel: string, modelName: string, data: Record<string, any>) {
  return request.post(`/adviser/sysadmin-data/${appLabel}.${modelName}/`, data)
}

/** 更新记录 */
export function updateModelData(appLabel: string, modelName: string, pk: number, data: Record<string, any>) {
  return request.put(`/adviser/sysadmin-data/${appLabel}.${modelName}/${pk}/`, data)
}

/** 删除记录 */
export function deleteModelData(appLabel: string, modelName: string, pk: number) {
  return request.delete(`/adviser/sysadmin-data/${appLabel}.${modelName}/${pk}/`)
}

/** FK 搜索 */
export function searchRelated(modelPath: string, q: string, params?: Record<string, any>) {
  return request.get<{results: Array<{value: string; label: string}>}>('/adviser/sysadmin-search/', { params: { model: modelPath, q, ...params } })
}

/** 获取活动完整配置（头部 + 组合明细 + 活动分组主从） */
export function getPromotionSetup(uuid: string) {
  const company = localStorage.getItem('genesis_pc_company') || ''
  return request.get('/adviser/get_promotion_setup/', { params: { company, uuid } })
}

/** 原子保存活动配置 */
export function savePromotionSetup(data: Record<string, any>) {
  return request.post('/adviser/save_promotion_setup/', data)
}
