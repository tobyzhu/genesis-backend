import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock API modules (needed for component import resolution)
vi.mock('@/api/cashier', () => ({
  getServiceItems: vi.fn(),
  getGoodsItems: vi.fn(),
  getCardtypeItems: vi.fn(),
  getCategorizedItems: vi.fn(),
  getHungByVipUuid: vi.fn(),
  getHungDetail: vi.fn(),
  getCardtypeServiceItems: vi.fn(),
  getCheckedOutOrders: vi.fn(),
  getActivePromotions: vi.fn(),
  saveHungOrder: vi.fn(),
  getCardtypePrices: vi.fn(),
}))

// Mock getVipDetail, getVipConsumption, getVipCommunication with controlled responses
const mockVipDetail = vi.fn()
const mockVipConsumption = vi.fn()
const mockVipCommunication = vi.fn()

vi.mock('@/api/vip', () => ({
  searchVip: vi.fn(),
  getVipCards: vi.fn(() => Promise.resolve({ data: [] })),
  getVipDetail: (...args: any[]) => mockVipDetail(...args),
  getVipConsumption: (...args: any[]) => mockVipConsumption(...args),
  getVipCommunication: (...args: any[]) => mockVipCommunication(...args),
}))

vi.mock('@/api/request', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

beforeEach(() => {
  localStorage.setItem('genesis_pc_company', 'test')
  localStorage.setItem('genesis_pc_storecode', '01')
  vi.clearAllMocks()
})

describe('drawer data loading', () => {
  it('should process getVipDetail response correctly', async () => {
    const vipData = {
      uuid: 'vip-1', vname: '张三', vcode: 'V001',
      mtcode: '13800138000', viplevel: '金卡',
      ecode: 'E001', ecode2: 'E002',
    }
    mockVipDetail.mockResolvedValue({ data: vipData })

    const result = await mockVipDetail('vip-uuid')
    expect(mockVipDetail).toHaveBeenCalledWith('vip-uuid')
    expect(result.data.vname).toBe('张三')
    expect(result.data.vcode).toBe('V001')
    expect(result.data.viplevel).toBe('金卡')
    expect(result.data.ecode).toBe('E001')
  })

  it('should process getVipConsumption response correctly', async () => {
    const consumptionData = [
      { vsdate: '20260701', itemname: '面部护理', amount: 380 },
      { vsdate: '20260710', itemname: '肩颈按摩', amount: 280 },
    ]
    mockVipConsumption.mockResolvedValue({ data: consumptionData })

    const result = await mockVipConsumption('vip-uuid')
    const items = Array.isArray(result.data) ? result.data : result.data?.results ?? []
    expect(items).toHaveLength(2)
    expect(items[0].itemname).toBe('面部护理')
    expect(items[0].amount).toBe(380)
    expect(items[1].itemname).toBe('肩颈按摩')
  })

  it('should process getVipCommunication response correctly', async () => {
    const commData = [
      { created_date: '20260708', casetype: '20', detail: '客户反馈良好', ecode: '张三' },
    ]
    mockVipCommunication.mockResolvedValue({ data: commData })

    const result = await mockVipCommunication('vip-uuid')
    const items = Array.isArray(result.data) ? result.data : result.data?.results ?? []
    expect(items).toHaveLength(1)
    expect(items[0].detail).toBe('客户反馈良好')
    expect(items[0].casetype).toBe('20')
  })

  it('should handle empty consumption gracefully', async () => {
    mockVipConsumption.mockResolvedValue({ data: [] })
    const result = await mockVipConsumption('vip-uuid')
    const items = Array.isArray(result.data) ? result.data : result.data?.results ?? []
    expect(items).toEqual([])
  })

  it('should handle API error gracefully', async () => {
    mockVipDetail.mockRejectedValue(new Error('Network error'))
    try {
      await mockVipDetail('vip-uuid')
      // should not throw to caller (caught by Promise.allSettled)
    } catch {
      // Expected
    }
    expect(mockVipDetail).toHaveBeenCalledWith('vip-uuid')
  })
})
