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
      // 并行取主数据（第4个不阻塞）
      const [detailRes, cardsRes, consRes] = await Promise.allSettled([
        getVipDetail(vipUuid),
        getVipCards(vipUuid),
        getVipConsumption(vipUuid),
      ])
      if (detailRes.status === 'fulfilled') basicInfo.value = detailRes.value.data
      if (cardsRes.status === 'fulfilled') {
        cards.value = (Array.isArray(cardsRes.value.data) ? cardsRes.value.data : cardsRes.value.data?.results ?? [])
      }
      if (consRes.status === 'fulfilled') {
        consumption.value = (Array.isArray(consRes.value.data) ? consRes.value.data : consRes.value.data?.results ?? [])
      }
      console.log('[VipProfile] detail/cards/cons loaded')
      // 沟通记录单独请求，不阻塞
      getVipCommunication(vipUuid).then(r => {
        communications.value = Array.isArray(r.data) ? r.data : (r.data?.results ?? [])
      }).catch(() => {})
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
