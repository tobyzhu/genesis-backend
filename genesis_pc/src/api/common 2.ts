import request from './request'

export function getCompanyStores(company: string) {
  return request.get('/common/company_stores/', { params: { company } })
}

export function login(data: { company: string; usercode: string; password: string; storecode?: string }) {
  return request.get('/common/hdsysuser_login/', { params: data })
}

export function logout() {
  return request.post('/common/logout/')
}

export function switchStore(params: { company: string; storecode: string; username: string }) {
  return request.get('/common/switch_store/', { params })
}

export function changePassword(data: { old_password: string; new_password: string }) {
  return request.post('/common/change_password/', data)
}

export function getDict(key: string) {
  return request.get<Record<string, any>>('/common/dict/', { params: { key } })
}

export function getEmployeeList(params?: Record<string, any>) {
  return request.get('/baseinfo/employees/', { params })
}
