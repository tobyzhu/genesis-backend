import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAppStore } from '../app'

beforeEach(() => {
  setActivePinia(createPinia())
  localStorage.clear()
})

describe('appStore — initial state', () => {
  it('should start unauthenticated', () => {
    const store = useAppStore()
    expect(store.isLoggedIn).toBe(false)
    expect(store.user).toBeNull()
    expect(store.sidebarCollapsed).toBe(false)
  })

  it('should start with empty company/store', () => {
    const store = useAppStore()
    expect(store.currentCompany).toBe('')
    expect(store.currentStorecode).toBe('')
    expect(store.currentStoreName).toBe('')
  })

  it('should initialize cashier from localStorage if present', () => {
    localStorage.setItem('genesis_pc_cashier_code', 'E001')
    localStorage.setItem('genesis_pc_cashier_name', '张三')
    const store = useAppStore()
    expect(store.cashierCode).toBe('E001')
    expect(store.cashierName).toBe('张三')
  })
})

describe('appStore — loginSuccess', () => {
  it('should store token, user, company and storecode', () => {
    const store = useAppStore()
    const userData = {
      username: 'admin',
      sys_fullname: '管理员',
      sys_userid: 'E001',
      sys_adm: 'Y',
      company: 'test_company',
      storecode: '01',
      stores: [{ storecode: '01', storename: '总店' }, { storecode: '02', storename: '分店' }],
      permissions: [],
    }
    store.loginSuccess('token-123', userData)

    expect(store.isLoggedIn).toBe(true)
    expect(store.user).toEqual(userData)
    expect(store.currentCompany).toBe('test_company')
    expect(store.currentStorecode).toBe('01')
    expect(store.currentStoreName).toBe('总店')
    expect(store.allowedStores).toEqual(userData.stores)
    expect(store.ecode).toBe('E001')
    expect(store.displayName).toBe('管理员')

    // localStorage consistency
    expect(localStorage.getItem('genesis_pc_company')).toBe('test_company')
    expect(localStorage.getItem('genesis_pc_storecode')).toBe('01')
  })

  it('should handle user without company field', () => {
    const store = useAppStore()
    store.loginSuccess('tok', { username: 'test', sys_fullname: '测试' })

    expect(store.isLoggedIn).toBe(false)
    expect(store.currentCompany).toBe('')
    expect(store.displayName).toBe('测试')
    expect(store.userName).toBe('test')
  })

  it('should set fallback displayName when sys_fullname absent', () => {
    const store = useAppStore()
    store.loginSuccess('tok', { username: 'admin', sys_adm: 'Y' })
    expect(store.displayName).toBe('admin')
  })
})

describe('appStore — permissions', () => {
  it('should grant all permissions to admin', () => {
    const store = useAppStore()
    store.loginSuccess('tok', { username: 'admin', sys_adm: 'Y', permissions: [] })

    expect(store.hasPerm('vip', 'read')).toBe(true)
    expect(store.hasPerm('vip', 'write')).toBe(true)
    expect(store.hasPerm('any_random_module', 'write')).toBe(true)
  })

  it('should check module-level read/write permissions', () => {
    const store = useAppStore()
    store.loginSuccess('tok', {
      username: 'user',
      sys_adm: 'N',
      permissions: [
        { module: 'vip', read: 'Y', write: 'N' },
        { module: 'cashier', read: 'Y', write: 'Y' },
      ],
    })

    expect(store.hasPerm('vip', 'read')).toBe(true)
    expect(store.hasPerm('vip', 'write')).toBe(false)
    expect(store.hasPerm('cashier', 'read')).toBe(true)
    expect(store.hasPerm('cashier', 'write')).toBe(true)
    expect(store.hasPerm('report', 'read')).toBe(false)
    expect(store.hasPerm('report', 'write')).toBe(false)
  })
})

describe('appStore — selectStore', () => {
  it('should update current store and persist', () => {
    const store = useAppStore()
    store.selectStore('02', '分店')

    expect(store.currentStorecode).toBe('02')
    expect(store.currentStoreName).toBe('分店')
    expect(localStorage.getItem('genesis_pc_storecode')).toBe('02')
    expect(localStorage.getItem('genesis_pc_storename')).toBe('分店')
  })
})

describe('appStore — cashier', () => {
  it('should set cashier code and name', () => {
    const store = useAppStore()
    store.setCashier('E002', '李四')

    expect(store.cashierCode).toBe('E002')
    expect(store.cashierName).toBe('李四')
    expect(localStorage.getItem('genesis_pc_cashier_code')).toBe('E002')
    expect(localStorage.getItem('genesis_pc_cashier_name')).toBe('李四')
  })

  it('should reset cashier to current user if logged in', () => {
    const store = useAppStore()
    store.loginSuccess('tok', { username: 'admin', sys_userid: 'E001', sys_fullname: '管理员' })
    store.setCashier('E002', '旧收银')
    store.resetCashier()

    expect(store.cashierCode).toBe('E001')
    expect(store.cashierName).toBe('管理员')
  })
})

describe('appStore — logout', () => {
  it('should clear all auth state', () => {
    const store = useAppStore()
    store.loginSuccess('tok123', { username: 'admin', company: 'c', storecode: '01', stores: [], permissions: [] })
    store.setCashier('E001', '收银')
    localStorage.setItem('genesis_pc_company', 'c')
    localStorage.setItem('genesis_pc_storecode', '01')
    localStorage.setItem('genesis_pc_storename', '总店')

    store.logout()

    expect(store.isLoggedIn).toBe(false)
    expect(store.user).toBeNull()
    expect(store.currentCompany).toBe('')
    expect(store.currentStorecode).toBe('')
    expect(store.currentStoreName).toBe('')
    expect(store.cashierCode).toBe('')
    expect(store.cashierName).toBe('')
    expect(store.allowedStores).toEqual([])
  })
})

describe('appStore — toggleSidebar', () => {
  it('should toggle sidebar collapsed state', () => {
    const store = useAppStore()
    expect(store.sidebarCollapsed).toBe(false)
    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(true)
    store.toggleSidebar()
    expect(store.sidebarCollapsed).toBe(false)
  })
})

describe('appStore — setAllowedStores', () => {
  it('should update allowed stores', () => {
    const store = useAppStore()
    const stores = [{ storecode: '01', storename: 'A' }, { storecode: '02', storename: 'B' }]
    store.setAllowedStores(stores)
    expect(store.allowedStores).toEqual(stores)
  })
})
