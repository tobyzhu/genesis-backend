import { describe, it, expect, vi, beforeEach } from 'vitest'

vi.mock('@/api/cashier', () => ({
  getServiceItems: vi.fn(() => Promise.resolve({ data: [] })),
  getGoodsItems: vi.fn(() => Promise.resolve({ data: [] })),
  getCardtypeItems: vi.fn(() => Promise.resolve({ data: [] })),
  getCategorizedItems: vi.fn(() => Promise.resolve({ data: { categories: [], items: [] } })),
  getHungByVipUuid: vi.fn(() => Promise.resolve({ data: [] })),
  getHungDetail: vi.fn(() => Promise.resolve({ data: [] })),
  getCardtypeServiceItems: vi.fn(() => Promise.resolve({ data: [] })),
  getCheckedOutOrders: vi.fn(() => Promise.resolve({ data: [] })),
  getActivePromotions: vi.fn(() => Promise.resolve({ data: [] })),
  saveHungOrder: vi.fn(() => Promise.resolve({ data: { ok: true } })),
  getCardtypePrices: vi.fn(() => Promise.resolve({ data: [] })),
}))

vi.mock('@/api/vip', () => ({
  searchVip: vi.fn(() => Promise.resolve({ data: { results: [] } })),
  getVipCards: vi.fn(() => Promise.resolve({ data: [] })),
}))

vi.mock('@/api/request', () => ({ default: { get: vi.fn(), post: vi.fn() } }))

beforeEach(() => {
  localStorage.setItem('genesis_pc_company', 'test')
  localStorage.setItem('genesis_pc_storecode', '01')
})

import { useBillingEngine } from '@/composables/useBillingEngine'

describe('useBillingEngine cart', () => {
  it('should start empty', () => {
    const e = useBillingEngine()
    expect(e.cart.value).toEqual([])
    expect(e.cartTotal.value).toBe(0)
  })

  it('should add items', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 100, ttype: 'S' })
    expect(e.cart.value).toHaveLength(1)
    expect(e.cartTotal.value).toBe(100)
  })

  it('should deduplicate same code after debounce', () => {
    vi.useFakeTimers()
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 100, ttype: 'S' })
    vi.advanceTimersByTime(400)
    e.addToCart({ code: 'a', name: 'A', price: 100, ttype: 'S' })
    expect(e.cart.value).toHaveLength(1)
    expect(e.cart.value[0].qty).toBe(2)
    expect(e.cartTotal.value).toBe(200)
    vi.useRealTimers()
  })

  it('should handle discount', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 200, ttype: 'S' })
    e.cart.value[0].secdisc = 0.8
    e.cart.value[0].srvmondisc = 10
    expect(e.cartTotal.value).toBe(150)
  })

  it('should group by ttype', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 's', name: 'S', price: 10, ttype: 'S' })
    e.addToCart({ code: 'g', name: 'G', price: 20, ttype: 'G' })
    e.addToCart({ code: 'c', name: 'C', price: 30, ttype: 'C' })
    expect(e.cartGroups.value).toHaveLength(3)
    expect(e.cartGroups.value[0].ttype).toBe('S')
    expect(e.cartGroups.value[1].ttype).toBe('G')
  })

  it('should toggle refund', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 100, ttype: 'S' })
    e.toggleRefund(0)
    expect(e.cart.value[0].qty).toBe(-1)
    e.toggleRefund(0)
    expect(e.cart.value[0].qty).toBe(1)
  })
})
