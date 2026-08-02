import request from './request'

function crmScope() {
  return {
    company: localStorage.getItem('genesis_pc_company') || '',
    storecode: localStorage.getItem('genesis_pc_storecode') || '',
  }
}

/** 客户关怀字典 */
export function getCrmDicts() {
  return request.get('/crm/pc/dicts/', { params: crmScope() })
}

// ===== 关怀规则 =====
export function listCrmRules(params?: Record<string, any>) {
  return request.get('/crm/pc/rules/', { params: { ...crmScope(), ...params } })
}

export function createCrmRule(data: Record<string, any>) {
  return request.post('/crm/pc/rules/', { ...crmScope(), ...data })
}

export function updateCrmRule(uuid: string, data: Record<string, any>) {
  return request.put(`/crm/pc/rules/${uuid}/`, { ...crmScope(), ...data })
}

export function deleteCrmRule(uuid: string) {
  return request.delete(`/crm/pc/rules/${uuid}/`, { params: crmScope() })
}

export function previewCrmRule(uuid: string, params?: Record<string, any>) {
  return request.get(`/crm/pc/rules/${uuid}/preview/`, { params: { ...crmScope(), ...params } })
}

export function runCrmRule(uuid: string, params?: Record<string, any>) {
  return request.post(`/crm/pc/rules/${uuid}/run/`, { ...crmScope(), ...params })
}

// ===== 回访任务 =====
export function listCrmTasks(params?: Record<string, any>) {
  return request.get('/crm/pc/tasks/', { params: { ...crmScope(), ...params } })
}

export function getCrmTaskSummary(params?: Record<string, any>) {
  return request.get('/crm/pc/tasks/summary/', { params: { ...crmScope(), ...params } })
}

export function getCrmTask(uuid: string) {
  return request.get(`/crm/pc/tasks/${uuid}/`, { params: crmScope() })
}

export function createCrmTask(data: Record<string, any>) {
  return request.post('/crm/pc/tasks/', { ...crmScope(), ...data })
}

export function addCrmTaskAttempt(uuid: string, data: Record<string, any>) {
  return request.post(`/crm/pc/tasks/${uuid}/attempt/`, { ...crmScope(), ...data })
}

export function deleteCrmTaskAttempt(uuid: string, attemptUuid: string) {
  return request.delete(`/crm/pc/tasks/${uuid}/attempt/${attemptUuid}/`, { params: crmScope() })
}

export function suggestCrmTaskTouch(uuid: string, data: Record<string, any>) {
  return request.post(`/crm/pc/tasks/${uuid}/suggest/`, { ...crmScope(), ...data })
}

export function completeCrmTask(uuid: string, data: Record<string, any>) {
  return request.post(`/crm/pc/tasks/${uuid}/complete/`, { ...crmScope(), ...data })
}

export function updateCrmTaskStatus(uuid: string, data: Record<string, any>) {
  return request.post(`/crm/pc/tasks/${uuid}/status/`, { ...crmScope(), ...data })
}

// ===== 客户沟通流水 =====
export function listCrmTimeline(params?: Record<string, any>) {
  return request.get('/crm/pc/timeline/', { params: { ...crmScope(), ...params } })
}

export function createCrmTimeline(data: Record<string, any>) {
  return request.post('/crm/pc/timeline/', { ...crmScope(), ...data })
}

export function updateCrmTimeline(uuid: string, data: Record<string, any>) {
  return request.put(`/crm/pc/timeline/${uuid}/`, { ...crmScope(), ...data })
}

export function deleteCrmTimeline(uuid: string) {
  return request.delete(`/crm/pc/timeline/${uuid}/`, { params: crmScope() })
}
