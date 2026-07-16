import { ref } from 'vue'
import type { VipCard } from '@/types'
import { getVipDetail, getVipCards, getVipConsumption, getVipCommunication } from '@/api/vip'

/** 客户 360° 资料（全局可复用） */
export function useVipProfile() {
  const drawerVisible = ref(false)
  const loading = ref(false)
  const basicInfo = ref<any>(null)
  const cards = ref<VipCard[]>([])
  const consumption = ref<any[]>([])
  const communications = ref<any[]>([])

  async function showProfile(vipUuid: string) {
    drawerVisible.value = true
    loading.value = true
    // 重置旧数据
    basicInfo.value = null
    cards.value = []
    consumption.value = []
    communications.value = []
    console.log('[VipProfile] showProfile uuid=', vipUuid)
    try {
      const results = await Promise.allSettled([
        getVipDetail(vipUuid),
        getVipCards(vipUuid),
        getVipConsumption(vipUuid),
        getVipCommunication(vipUuid),
      ])
      const labels = ['getVipDetail', 'getVipCards', 'getVipConsumption', 'getVipCommunication']
      results.forEach((r, i) => {
        if (r.status === 'fulfilled') {
          console.log('[VipProfile]', labels[i], 'OK, data keys:', Object.keys(r.value.data || {}).slice(0,5))
        } else {
          console.warn('[VipProfile]', labels[i], 'failed:', r.reason)
        }
      })
      // 各自独立赋值，某个失败不影响其他
      const infoRes = results[0]
      const cardsRes = results[1]
      const consRes = results[2]
      const commRes = results[3]
      if (infoRes.status === 'fulfilled') basicInfo.value = infoRes.value.data
      if (cardsRes.status === 'fulfilled') {
        cards.value = (Array.isArray(cardsRes.value.data) ? cardsRes.value.data : cardsRes.value.data?.results ?? [])
      }
      if (consRes.status === 'fulfilled') {
        consumption.value = (Array.isArray(consRes.value.data) ? consRes.value.data : consRes.value.data?.results ?? [])
      }
      if (commRes.status === 'fulfilled') {
        communications.value = (Array.isArray(commRes.value.data) ? commRes.value.data : commRes.value.data?.results ?? [])
      }
    } catch {
      // 极不可能走到这里（allSettled 不抛）
    } finally { loading.value = false }
  }

  function closeProfile() { drawerVisible.value = false }

  return {
    drawerVisible,
    loading,
    basicInfo,
    cards,
    consumption,
    communications,
    showProfile, closeProfile,
  }
}

export type VipProfile = ReturnType<typeof useVipProfile>
