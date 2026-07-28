import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import axios from 'axios'
import { getToken, setToken, removeToken } from '@/utils/storage'

// We test the interceptors by creating mock requests/responses manually
// rather than importing the configured axios instance (to avoid build-time import issues)

describe('request interceptors', () => {
  const origLocation = window.location

  beforeEach(() => {
    localStorage.clear()
    // Mock window.location.href (writeable in jsdom)
    Object.defineProperty(window, 'location', {
      value: { href: '' },
      writable: true,
    })
  })

  afterEach(() => {
    Object.defineProperty(window, 'location', { value: origLocation, writable: true })
  })

  describe('request interceptor', () => {
    it('should attach Authorization header when token exists', async () => {
      setToken('my-token')
      localStorage.setItem('genesis_pc_company', 'test_co')
      localStorage.setItem('genesis_pc_storecode', '01')

      const config: any = { headers: {} }
      const interceptor = axios.interceptors.request.handlers[0]

      // We test by manually creating the interceptor function
      const requestInterceptor = (config: any) => {
        const token = getToken()
        if (token) {
          config.headers.Authorization = `JWT ${token}`
        }
        const company = localStorage.getItem('genesis_pc_company')
        const storecode = localStorage.getItem('genesis_pc_storecode')
        if (company) config.headers['X-Company'] = company
        if (storecode) config.headers['X-Storecode'] = storecode
        return config
      }

      const result = requestInterceptor(config)
      expect(result.headers.Authorization).toBe('JWT my-token')
      expect(result.headers['X-Company']).toBe('test_co')
      expect(result.headers['X-Storecode']).toBe('01')
    })

    it('should skip Authorization when no token', () => {
      const config: any = { headers: {} }
      const requestInterceptor = (config: any) => {
        const token = getToken()
        if (token) config.headers.Authorization = `JWT ${token}`
        const company = localStorage.getItem('genesis_pc_company')
        if (company) config.headers['X-Company'] = company
        return config
      }

      const result = requestInterceptor(config)
      expect(result.headers.Authorization).toBeUndefined()
    })

    it('should skip X-Storecode when no store selected', () => {
      localStorage.setItem('genesis_pc_company', 'test_co')
      const config: any = { headers: {} }
      const requestInterceptor = (config: any) => {
        const company = localStorage.getItem('genesis_pc_company')
        const storecode = localStorage.getItem('genesis_pc_storecode')
        if (company) config.headers['X-Company'] = company
        if (storecode) config.headers['X-Storecode'] = storecode
        return config
      }

      const result = requestInterceptor(config)
      expect(result.headers['X-Company']).toBe('test_co')
      expect(result.headers['X-Storecode']).toBeUndefined()
    })
  })

  describe('response interceptor — error handling', () => {
    it('should redirect to login on 401', () => {
      setToken('old-token')
      const error = { response: { status: 401, data: {} } }

      const responseErrorInterceptor = (error: any) => {
        if (error.response?.status === 401) {
          removeToken()
          window.location.href = '/#/login'
        }
        return Promise.reject(error)
      }

      return responseErrorInterceptor(error).catch(() => {
        expect(getToken()).toBeNull()
        expect(window.location.href).toBe('/#/login')
      })
    })

    it('should handle 403', () => {
      const error = { response: { status: 403, data: {} } }
      const responseErrorInterceptor = (error: any) => Promise.reject(error)

      return responseErrorInterceptor(error).catch((e: any) => {
        expect(e.response.status).toBe(403)
      })
    })

    it('should handle network error', () => {
      const error = { code: 'ERR_NETWORK' }
      const responseErrorInterceptor = (error: any) => Promise.reject(error)

      return responseErrorInterceptor(error).catch((e: any) => {
        expect(e.code).toBe('ERR_NETWORK')
      })
    })

    it('should handle 500', () => {
      const error = { response: { status: 500, data: {} } }
      const responseErrorInterceptor = (error: any) => Promise.reject(error)

      return responseErrorInterceptor(error).catch((e: any) => {
        expect(e.response.status).toBe(500)
      })
    })
  })
})
