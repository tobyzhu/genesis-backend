import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getUser, setUser, setToken, clearAuth } from '@/utils/storage'
import {
  applyTheme,
  loadStoredTheme,
  THEME_OPTIONS,
  THEME_STORAGE_KEY,
  type ThemeId,
} from '@/styles/theme'

export const useAppStore = defineStore('app', () => {
  const user = ref<Record<string, any> | null>(getUser())
  const sidebarCollapsed = ref(false)
const cashierCode = ref<string>(localStorage.getItem('genesis_pc_cashier_code') ?? '')
const cashierName = ref<string>(localStorage.getItem('genesis_pc_cashier_name') ?? '')

  const currentCompany = ref<string>(localStorage.getItem('genesis_pc_company') ?? '')
  const currentStorecode = ref<string>(localStorage.getItem('genesis_pc_storecode') ?? '')
  const currentStoreName = ref<string>(localStorage.getItem('genesis_pc_storename') ?? '')
  const allowedStores = ref<Array<{ storecode: string; storename: string }>>(
    Array.isArray(user.value?.stores) ? user.value!.stores : [],
  )
  const themeId = ref<ThemeId>(loadStoredTheme())
  const themeOptions = THEME_OPTIONS

  const isLoggedIn = computed(() => !!user.value && !!currentCompany.value)
  const userName = computed(() => user.value?.username ?? '')
  const displayName = computed(() => user.value?.sys_fullname ?? user.value?.username ?? '')
const ecode = computed(() => user.value?.sys_userid ?? '')
const fullname = computed(() => user.value?.sys_fullname ?? '')
const permissions = computed(() => (user.value?.permissions ?? []) as Array<{module:string;read:string;write:string;modulegrp:string}>)
function hasPerm(module: string, operation: 'read' | 'write'): boolean {
  if (!user.value) return false
  if (user.value?.sys_adm === 'Y') return true
  const perms = user.value?.permissions ?? []
  const found = perms.find((p: any) => p.module === module)
  if (!found) return false
  if (operation === 'write') return found.write === 'Y'
  return found.read === 'Y'
}
function setCashier(code: string, name: string) {
  cashierCode.value = code
  cashierName.value = name
  localStorage.setItem('genesis_pc_cashier_code', code)
  localStorage.setItem('genesis_pc_cashier_name', name)
}
function resetCashier() {
  if (user.value) {
    setCashier(ecode.value, fullname.value)
  }
}

  function loginSuccess(token: string, userData: Record<string, any>) {
    setToken(token)
    setUser(userData)
    user.value = userData

    if (userData.company) {
      currentCompany.value = userData.company
      localStorage.setItem('genesis_pc_company', userData.company)
    }
    if (userData.storecode) {
      currentStorecode.value = userData.storecode
      localStorage.setItem('genesis_pc_storecode', userData.storecode)
    }
    if (userData.stores && userData.stores.length > 0) {
      allowedStores.value = userData.stores
      const cur = userData.stores.find((s: any) => s.storecode === userData.storecode)
      if (cur) {
        currentStoreName.value = cur.storename
        localStorage.setItem('genesis_pc_storename', cur.storename)
      }
    }
  }

  function selectStore(storecode: string, storename: string) {
    currentStorecode.value = storecode
    currentStoreName.value = storename
    localStorage.setItem('genesis_pc_storecode', storecode)
    localStorage.setItem('genesis_pc_storename', storename)
  }

  function setAllowedStores(stores: Array<{ storecode: string; storename: string }>) {
    allowedStores.value = stores
  }

  function logout() {
    clearAuth()
    user.value = null
    currentCompany.value = ''
    currentStorecode.value = ''
    currentStoreName.value = ''
    allowedStores.value = []
    localStorage.removeItem('genesis_pc_company')
    localStorage.removeItem('genesis_pc_storecode')
    localStorage.removeItem('genesis_pc_storename')
    cashierCode.value = ''
    cashierName.value = ''
    localStorage.removeItem('genesis_pc_cashier_code')
    localStorage.removeItem('genesis_pc_cashier_name')
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setTheme(id: ThemeId | string) {
    const next = applyTheme(id)
    themeId.value = next
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next)
    } catch { /* ignore */ }
  }

  return {
    user,
    sidebarCollapsed,
    cashierCode,
    cashierName,
    currentCompany,
    currentStorecode,
    currentStoreName,
    allowedStores,
    themeId,
    themeOptions,
    isLoggedIn,
    userName,
    displayName,
    ecode,
    fullname,
    permissions,
    hasPerm,
    setCashier,
    resetCashier,
    loginSuccess,
    selectStore,
    setAllowedStores,
    logout,
    toggleSidebar,
    setTheme,
  }
})
