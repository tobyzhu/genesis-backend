import { computed, watchEffect } from 'vue'
import { useAppStore } from '@/store/app'

/** 报表公共上下文：公司、可管门店、当前店、django_user_id */
export function useReportContext() {
  const appStore = useAppStore()

  // 刷新后从本地 user 恢复可管门店
  watchEffect(() => {
    if (!appStore.allowedStores.length && appStore.user?.stores?.length) {
      appStore.setAllowedStores(appStore.user.stores)
    }
  })

  const company = computed(() => appStore.currentCompany || '')
  const allowedStores = computed(() => appStore.allowedStores)
  const currentStorecode = computed(() => appStore.currentStorecode || '')
  const currentStoreName = computed(() => appStore.currentStoreName || '')
  const djangoUserId = computed(() => appStore.user?.django_user_id ?? null)

  return {
    company,
    allowedStores,
    currentStorecode,
    currentStoreName,
    djangoUserId,
  }
}
