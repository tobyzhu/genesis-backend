import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock the API modules
vi.mock('@/api/vip', () => ({
  getVipDetail: vi.fn(),
  getVipCards: vi.fn(),
  getVipConsumption: vi.fn(),
  getVipCommunication: vi.fn(),
}))

vi.mock('@/api/cashier', () => ({
  getServiceItems: vi.fn(),
  getGoodsItems: vi.fn(),
  getCardtypeItems: vi.fn(),
}))

vi.mock('@/api/request', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

import { useVipProfile } from '../useVipProfile'
import { getVipDetail, getVipCards, getVipConsumption, getVipCommunication } from '@/api/vip'

beforeEach(() => {
  vi.clearAllMocks()
  localStorage.setItem('genesis_pc_company', 'test')
  localStorage.setItem('genesis_pc_storecode', '01')
})

describe('useVipProfile', () => {
  it('should initialize with closed state', () => {
    const p = useVipProfile()
    expect(p.drawerVisible.value).toBe(false)
    expect(p.loading.value).toBe(false)
    expect(p.basicInfo.value).toBeNull()
    expect(p.cards.value).toEqual([])
    expect(p.consumption.value).toEqual([])
    expect(p.communications.value).toEqual([])
  })

  it('should set loading state and fetch data on showProfile', async () => {
    const vipData = { uuid: 'vip-1', vname: '张三', vcode: 'V001' }
    const cardsData = [{ uuid: 'c1', ccode: 'C001', cardname: '金卡' }]
    const consumptionData = [{ vsdate: '20260701', srvname: '面部护理', s_amount: 380 }]
    const commData = [{ created_date: '20260708', casetype: '20', detail: '回访' }]

    const mockGetVipDetail = getVipDetail as any
    const mockGetVipCards = getVipCards as any
    const mockGetVipConsumption = getVipConsumption as any
    const mockGetVipCommunication = getVipCommunication as any

    mockGetVipDetail.mockResolvedValue({ data: vipData })
    mockGetVipCards.mockResolvedValue({ data: cardsData })
    mockGetVipConsumption.mockResolvedValue({ data: consumptionData })
    mockGetVipCommunication.mockResolvedValue({ data: commData })

    const p = useVipProfile()
    const promise = p.showProfile('vip-1')
    expect(p.drawerVisible.value).toBe(true)
    expect(p.loading.value).toBe(true)

    await promise

    expect(p.loading.value).toBe(false)
    expect(p.basicInfo.value).toEqual(vipData)
    expect(p.cards.value).toEqual(cardsData)
    expect(p.consumption.value).toEqual(consumptionData)
    expect(p.communications.value).toEqual(commData)

    expect(mockGetVipDetail).toHaveBeenCalledWith('vip-1')
    expect(mockGetVipCards).toHaveBeenCalledWith('vip-1')
    expect(mockGetVipConsumption).toHaveBeenCalledWith('vip-1')
    expect(mockGetVipCommunication).toHaveBeenCalledWith('vip-1')
  })

  it('should handle partial API failures gracefully', async () => {
    const vipData = { uuid: 'vip-2', vname: '李四' }

    const mockGetVipDetail = getVipDetail as any
    const mockGetVipCards = getVipCards as any
    const mockGetVipConsumption = getVipConsumption as any
    const mockGetVipCommunication = getVipCommunication as any

    mockGetVipDetail.mockResolvedValue({ data: vipData })
    mockGetVipCards.mockRejectedValue(new Error('cards failed'))
    mockGetVipConsumption.mockResolvedValue({ data: [{ vsdate: '20260701' }] })
    mockGetVipCommunication.mockRejectedValue(new Error('comm failed'))

    const p = useVipProfile()
    await p.showProfile('vip-2')

    expect(p.basicInfo.value).toEqual(vipData)
    expect(p.cards.value).toEqual([])
    expect(p.consumption.value).toEqual([{ vsdate: '20260701' }])
    expect(p.communications.value).toEqual([])
    expect(p.loading.value).toBe(false)
  })

  it('should handle cards response as object with results field', async () => {
    const vipData = { uuid: 'vip-3', vname: '王五' }
    const cardsData = { results: [{ uuid: 'c2', ccode: 'C002' }] }

    const mockGetVipDetail = getVipDetail as any
    const mockGetVipCards = getVipCards as any
    const mockGetVipConsumption = getVipConsumption as any
    const mockGetVipCommunication = getVipCommunication as any

    mockGetVipDetail.mockResolvedValue({ data: vipData })
    mockGetVipCards.mockResolvedValue({ data: cardsData })
    mockGetVipConsumption.mockResolvedValue({ data: [] })
    mockGetVipCommunication.mockResolvedValue({ data: [] })

    const p = useVipProfile()
    await p.showProfile('vip-3')
    expect(p.cards.value).toEqual([{ uuid: 'c2', ccode: 'C002' }])
  })

  it('should handle consumption response as object with results field', async () => {
    const vipData = { uuid: 'vip-4', vname: '赵六' }
    const consumptionData = { results: [{ vsdate: '20260702', srvname: '按摩' }] }

    const mockGetVipDetail = getVipDetail as any
    const mockGetVipCards = getVipCards as any
    const mockGetVipConsumption = getVipConsumption as any
    const mockGetVipCommunication = getVipCommunication as any

    mockGetVipDetail.mockResolvedValue({ data: vipData })
    mockGetVipCards.mockResolvedValue({ data: [] })
    mockGetVipConsumption.mockResolvedValue({ data: consumptionData })
    mockGetVipCommunication.mockResolvedValue({ data: [] })

    const p = useVipProfile()
    await p.showProfile('vip-4')
    expect(p.consumption.value).toEqual([{ vsdate: '20260702', srvname: '按摩' }])
  })

  it('should close drawer and keep old data', () => {
    const p = useVipProfile()
    p.drawerVisible.value = true
    p.basicInfo.value = { vname: '测试' } as any
    p.closeProfile()
    expect(p.drawerVisible.value).toBe(false)
    // data should remain (clearing happens on next showProfile)
    expect(p.basicInfo.value).toEqual({ vname: '测试' })
  })

  it('should reset data on new showProfile call', async () => {
    const vipData = { uuid: 'vip-5', vname: '新客户' }

    const mockGetVipDetail = getVipDetail as any
    const mockGetVipCards = getVipCards as any
    const mockGetVipConsumption = getVipConsumption as any
    const mockGetVipCommunication = getVipCommunication as any

    mockGetVipDetail.mockResolvedValue({ data: vipData })
    mockGetVipCards.mockResolvedValue({ data: [] })
    mockGetVipConsumption.mockResolvedValue({ data: [] })
    mockGetVipCommunication.mockResolvedValue({ data: [] })

    const p = useVipProfile()
    // First call with some data
    p.basicInfo.value = { vname: '旧数据' } as any
    p.cards.value = [{ uuid: 'old' }] as any
    await p.showProfile('vip-5')
    // Should be replaced with new data
    expect(p.basicInfo.value).toEqual(vipData)
    expect(p.cards.value).toEqual([])
  })
})
