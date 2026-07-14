import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, removeToken } from '@/utils/storage'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL as string || '/api',
  timeout: 30000,
})

// 请求拦截器：附加 Token + 当前公司/门店
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `JWT ${token}`
    }
    // 附加公司/门店头信息，供后端区分租户
    const company = localStorage.getItem('genesis_pc_company')
    const storecode = localStorage.getItem('genesis_pc_storecode')
    if (company) {
      config.headers['X-Company'] = company
    }
    if (storecode) {
      config.headers['X-Storecode'] = storecode
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    if (error.response) {
      const { status, data } = error.response
      switch (status) {
        case 401:
          removeToken()
          window.location.href = '/#/login'
          ElMessage.error('登录已过期，请重新登录')
          break
        case 403:
          ElMessage.error('权限不足')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(data?.detail || `请求失败 (${status})`)
      }
    } else if (error.code === 'ERR_NETWORK') {
      ElMessage.error('网络连接失败，请检查后端服务是否启动')
    } else {
      ElMessage.error('请求异常')
    }
    return Promise.reject(error)
  },
)

export default request
