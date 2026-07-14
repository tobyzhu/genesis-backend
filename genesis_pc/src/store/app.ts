import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getUser, setUser, setToken, clearAuth } from '@/utils/storage'

export const useAppStore = defineStore('app', () => {
  const user = ref<Record<string, any> | null>(getUser())
  const sidebarCollapsed = ref(false)

  const currentCompany = ref<string>(localStorage.getItem('genesis_pc_company') ?? '')
  const currentStorecode = ref<string>(localStorage.getItem('genesis_pc_storecode') ?? '')
  const currentStoreName = ref<string>(localStorage.getItem('genesis_pc_storename') ?? '')
  const allowedStores = ref<Array<{ storecode: string; storename: string }>>([])

  const isLoggedIn = computed(() => !!user.value && !!currentCompany.value)
  const userName = computed(() => user.value?.username ?? '')
  const displayName = computed(() => user.value?.sys_fullname ?? user.value?.username ?? '')

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
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  return {
    user,
    sidebarCollapsed,
    currentCompany,
    currentStorecode,
    currentStoreName,
    allowedStores,
    isLoggedIn,
    userName,
    displayName,
    loginSuccess,
    selectStore,
    setAllowedStores,
    logout,
    toggleSidebar,
  }
})
