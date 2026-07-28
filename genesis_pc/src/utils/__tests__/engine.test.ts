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

// ====== New tests below ======

describe('useBillingEngine — searchVip', () => {
  it('should not search when keyword is empty', async () => {
    const e = useBillingEngine()
    e.vipKeyword.value = '  '
    await e.searchVip()
    expect(e.selectedVip.value).toBeNull()
  })

  it('should auto-select single result', async () => {
    const mockSearchVip = (await import('@/api/vip')).searchVip as any
    const vip = { uuid: 'v-1', vname: '张三', vcode: 'V001', mtcode: '13800138000' }
    mockSearchVip.mockResolvedValue({ data: { results: [vip] } })

    const e = useBillingEngine()
    e.vipKeyword.value = '张三'
    await e.searchVip()
    expect(e.selectedVip.value?.vname).toBe('张三')
    expect(e.searchResults.value).toEqual([])
  })

  it('should show multiple results', async () => {
    const mockSearchVip = (await import('@/api/vip')).searchVip as any
    const results = [
      { uuid: 'v-1', vname: '张三', vcode: 'V001' },
      { uuid: 'v-2', vname: '张三丰', vcode: 'V002' },
    ]
    mockSearchVip.mockResolvedValue({ data: { results } })

    const e = useBillingEngine()
    e.vipKeyword.value = '张三'
    await e.searchVip()
    expect(e.selectedVip.value).toBeNull()
    expect(e.searchResults.value).toHaveLength(2)
    expect(e.noResults.value).toBe(false)
  })

  it('should set noResults when no matches', async () => {
    const mockSearchVip = (await import('@/api/vip')).searchVip as any
    mockSearchVip.mockResolvedValue({ data: { results: [] } })

    const e = useBillingEngine()
    e.vipKeyword.value = '不可达'
    await e.searchVip()
    expect(e.selectedVip.value).toBeNull()
    expect(e.noResults.value).toBe(true)
  })

  it('should handle search API failure', async () => {
    const mockSearchVip = (await import('@/api/vip')).searchVip as any
    mockSearchVip.mockRejectedValue(new Error('API error'))

    const e = useBillingEngine()
    e.vipKeyword.value = '错误'
    await e.searchVip()
    expect(e.selectedVip.value).toBeNull()
    expect(e.noResults.value).toBe(true)
  })
})

describe('useBillingEngine — selectVip', () => {
  it('should reset cart and set employees on select', async () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'old', name: 'Old', price: 10, ttype: 'S' })

    const vip = { uuid: 'v-3', vname: '李四', vcode: 'V003', ecode: 'E001', ecode2: 'E002' }
    await e.selectVip(vip)

    expect(e.selectedVip.value?.vname).toBe('李四')
    expect(e.cart.value).toEqual([])
    expect(e.selectedCard.value).toBeNull()
    const def = e.getDefaultEmployees()
    expect(def.pmcode).toBe('E001')
    expect(def.asscode1).toBe('E002')
    expect(def.asscode2).toBe('')
  })
})

describe('useBillingEngine — cart operations', () => {
  it('should remove item by index', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 10, ttype: 'S' })
    e.addToCart({ code: 'b', name: 'B', price: 20, ttype: 'S' })
    expect(e.cart.value).toHaveLength(2)
    e.removeFromCart(0)
    expect(e.cart.value).toHaveLength(1)
    expect(e.cart.value[0].code).toBe('b')
  })

  it('should clear entire cart', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 10, ttype: 'S' })
    e.addToCart({ code: 'b', name: 'B', price: 20, ttype: 'S' })
    e.clearCart()
    expect(e.cart.value).toEqual([])
    expect(e.cartTotal.value).toBe(0)
  })

  it('should update individual cart item fields', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 100, ttype: 'S' })
    e.updateCartItem(0, 'secdisc', 0.8)
    e.updateCartItem(0, 'qty', 3)
    expect(e.cart.value[0].secdisc).toBe(0.8)
    expect(e.cart.value[0].qty).toBe(3)
    expect(e.cartTotal.value).toBe(240)
  })

  it('should use default employees from selectedVip', () => {
    const e = useBillingEngine()
    e.selectedVip.value = { uuid: 'v-1', vname: '张三', ecode: 'E001', ecode2: 'E002' } as any
    e.addToCart({ code: 's1', name: '服务1', price: 200, ttype: 'S' })
    expect(e.cart.value[0].pmcode).toBe('E001')
    expect(e.cart.value[0].asscode1).toBe('E002')
    expect(e.cart.value[0].asscode2).toBe('')
  })

  it('should not deduplicate across different ttypes', () => {
    vi.useFakeTimers()
    const e = useBillingEngine()
    e.addToCart({ code: 'x', name: 'X', price: 100, ttype: 'S' })
    vi.advanceTimersByTime(400)
    e.addToCart({ code: 'x', name: 'X', price: 100, ttype: 'G' })
    expect(e.cart.value).toHaveLength(2)
    vi.useRealTimers()
  })

  it('should set default payMethod to cash when no card selected', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 50, ttype: 'S' })
    expect(e.cart.value[0].payMethod).toBe('cash')
  })

  it('should set payMethod to card when card selected', () => {
    const e = useBillingEngine()
    e.selectedCard.value = { uuid: 'c-1', ccode: 'C001', cardname: '金卡' } as any
    e.addToCart({ code: 'a', name: 'A', price: 50, ttype: 'S' })
    expect(e.cart.value[0].payMethod).toBe('card:C001')
  })

  it('should compute cartGroups in correct order (S, G, C, I)', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'c', name: 'C', price: 30, ttype: 'C' })
    e.addToCart({ code: 's', name: 'S', price: 10, ttype: 'S' })
    e.addToCart({ code: 'g', name: 'G', price: 20, ttype: 'G' })
    expect(e.cartGroups.value.map(g => g.ttype)).toEqual(['S', 'G', 'C'])
  })
})

describe('useBillingEngine — saveHung', () => {
  it('should return false when no VIP selected', async () => {
    const e = useBillingEngine()
    const result = await e.saveHung()
    expect(result).toBe(false)
  })

  it('should save and clear cart on success', async () => {
    vi.useFakeTimers()
    const e = useBillingEngine()
    e.selectedVip.value = { uuid: 'v-1' } as any
    e.addToCart({ code: 's1', name: 'S1', price: 100, ttype: 'S' })
    vi.advanceTimersByTime(400)
    e.addToCart({ code: 'g1', name: 'G1', price: 50, ttype: 'G' })
    vi.useRealTimers()

    const request = (await import('@/api/request')).default as any
    request.post.mockResolvedValue({ data: { ok: true } })

    const result = await e.saveHung()
    expect(result).toBe(true)
    expect(e.cart.value).toEqual([])
  })

  it('should return false on save failure', async () => {
    const e = useBillingEngine()
    e.selectedVip.value = { uuid: 'v-1' } as any
    e.addToCart({ code: 's1', name: 'S1', price: 100, ttype: 'S' })

    const request = (await import('@/api/request')).default as any
    request.post.mockRejectedValue(new Error('Save failed'))

    const result = await e.saveHung()
    expect(result).toBe(false)
  })
})

describe('useBillingEngine — switchBillingMode', () => {
  it('should switch between normal and refund mode', () => {
    const e = useBillingEngine()
    expect(e.billingMode.value).toBe('normal')
    e.switchBillingMode('refund')
    expect(e.billingMode.value).toBe('refund')
    e.switchBillingMode('normal')
    expect(e.billingMode.value).toBe('normal')
  })
})

describe('useBillingEngine — void flow', () => {
  it('should toggle void panel', () => {
    const e = useBillingEngine()
    expect(e.voidPanelOpen.value).toBe(false)
    e.openVoidPanel()
    expect(e.voidPanelOpen.value).toBe(true)
    e.openVoidPanel()
    expect(e.voidPanelOpen.value).toBe(false)
  })

  it('should toggle void item selection', () => {
    const e = useBillingEngine()
    e.toggleVoidItem('order-1', 'item-1')
    expect(e.voidSelections.value['order-1']['item-1']).toBe(true)
    e.toggleVoidItem('order-1', 'item-1')
    expect(e.voidSelections.value['order-1']['item-1']).toBe(false)
  })

  it('should add void items to cart when confirmed', () => {
    const e = useBillingEngine()
    e.voidOrderItems.value['order-1'] = [
      { ditem: 'd1', srvcode: 'srv1', itemname: '服务1', qty: 2, price: 100, ttype: 'S' },
    ]
    e.voidSelections.value['order-1'] = { d1: true }
    e.confirmVoid()
    expect(e.voidItems.value).toHaveLength(1)
    expect(e.voidItems.value[0].code).toBe('srv1')
    expect(e.voidItems.value[0].qty).toBe(-2)
  })
})

describe('useBillingEngine — category filtering', () => {
  it('should filter items by category and keyword', () => {
    const e = useBillingEngine()
    e.categories.value = [
      { code: 'root', name: '全部', children: [
        { code: 'cat1', name: '面部', children: [
          { code: 'sub1', name: '清洁' },
          { code: 'sub2', name: '补水' },
        ]},
        { code: 'cat2', name: '身体' },
      ]},
    ] as any
    e.allItems.value = [
      { code: 'a', name: '清洁A', price: 100, ttype: 'S', category: 'sub1' } as any,
      { code: 'b', name: '补水B', price: 200, ttype: 'S', category: 'sub2' } as any,
      { code: 'c', name: '身体C', price: 300, ttype: 'S', category: 'cat2' } as any,
    ]

    e.selectedCategory.value = 'root'
    expect(e.filteredItems.value).toHaveLength(3)
  })

  it('should filter by keyword across items', () => {
    const e = useBillingEngine()
    e.itemKeyword.value = '清洁'
    e.allItems.value = [
      { code: 'a', name: '清洁A', price: 100, ttype: 'S' } as any,
      { code: 'b', name: '补水B', price: 200, ttype: 'S' } as any,
    ]
    expect(e.filteredItems.value).toHaveLength(1)
    expect(e.filteredItems.value[0].code).toBe('a')
  })
})

describe('useBillingEngine — card sale mode', () => {
  it('should filter card sale items by comptype', () => {
    const e = useBillingEngine()
    e.allItems.value = [
      { code: 'c1', name: '储值卡', price: 1000, comptype: 'amount' } as any,
      { code: 'c2', name: '疗程卡', price: 2000, comptype: 'times' } as any,
    ]
    expect(e.cardSaleItems.value).toHaveLength(1)
    expect(e.cardSaleItems.value[0].code).toBe('c1')

    e.cardSaleMode.value = 'times'
    expect(e.cardSaleItems.value).toHaveLength(1)
    expect(e.cardSaleItems.value[0].code).toBe('c2')
  })
})

describe('useBillingEngine — card groups', () => {
  it('should group cards by promotionsid and comptype', () => {
    const e = useBillingEngine()
    e.vipCards.value = [
      { uuid: 'c1', ccode: 'C001', cardname: '金卡', promotionsid: '0', comptype: 'amount', leftmoney: 1000 } as any,
      { uuid: 'c2', ccode: 'C002', cardname: '银卡', promotionsid: '0', comptype: 'amount', leftmoney: 500 } as any,
      { uuid: 'c3', ccode: 'C003', cardname: '次卡A', promotionsid: '0', comptype: 'times', leftqty: 10 } as any,
      { uuid: 'c4', ccode: 'C004', cardname: '活动卡', promotionsid: 'promo-1', comptype: 'amount', leftmoney: 2000, promotionname: '双十一活动' } as any,
    ]

    const groups = e.cardGroups.value
    expect(groups).toHaveLength(2)
    const normalGroup = groups.find(g => g.promotionName === '正常销售')
    expect(normalGroup).toBeDefined()
    expect(normalGroup!.comptypeGroups).toHaveLength(2)

    const promoGroup = groups.find(g => g.promotionName === '双十一活动')
    expect(promoGroup).toBeDefined()
    expect(promoGroup!.comptypeGroups).toHaveLength(1)
  })
})

describe('useBillingEngine — ttypeLabel and formatDate', () => {
  it('should return correct ttype labels', () => {
    const e = useBillingEngine()
    expect(e.ttypeLabel('S')).toBe('服务')
    expect(e.ttypeLabel('G')).toBe('商品')
    expect(e.ttypeLabel('C')).toBe('售卡')
    expect(e.ttypeLabel('I')).toBe('充值')
    expect(e.ttypeLabel('X')).toBe('X')
  })

  it('should format 8-digit date', () => {
    const e = useBillingEngine()
    expect(e.formatDate('20260701')).toBe('2026-07-01')
    expect(e.formatDate('')).toBe('')
    expect(e.formatDate('2026')).toBe('2026')
  })
})

describe('useBillingEngine — click guard (debounce)', () => {
  it('should debounce rapid clicks to same item', () => {
    vi.useFakeTimers()
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 100, ttype: 'S' })
    e.addToCart({ code: 'a', name: 'A', price: 100, ttype: 'S' })
    expect(e.cart.value).toHaveLength(1)
    expect(e.cart.value[0].qty).toBe(1)
    vi.useRealTimers()
  })
})

describe('useBillingEngine — recharge flow', () => {
  it('should add recharge item to cart', () => {
    const e = useBillingEngine()
    e.selectedVip.value = { uuid: 'v-1', vname: '张三', ecode: 'E001' } as any
    const card = { uuid: 'c-1', ccode: 'C001', cardname: '储值卡' } as any
    e.rechargeAmounts.value['C001'] = 500
    e.addRecharge(card)

    expect(e.cart.value).toHaveLength(1)
    expect(e.cart.value[0].code).toBe('C001')
    expect(e.cart.value[0].name).toBe('储值卡 充值')
    expect(e.cart.value[0].price).toBe(500)
    expect(e.cart.value[0].ttype).toBe('I')
    expect(e.rechargeAmounts.value['C001']).toBe(0)
  })

  it('should not add recharge with zero amount', () => {
    const e = useBillingEngine()
    const card = { uuid: 'c-1', ccode: 'C001', cardname: '储值卡' } as any
    e.addRecharge(card)
    expect(e.cart.value).toHaveLength(0)
  })

  it('should add card refund with negative price', () => {
    const e = useBillingEngine()
    e.selectedVip.value = { uuid: 'v-1', vname: '张三', ecode: 'E001' } as any
    const card = { uuid: 'c-1', ccode: 'C001', cardname: '储值卡' } as any
    e.rechargeAmounts.value['C001'] = 300
    e.addCardRefund(card)
    expect(e.cart.value[0].price).toBe(-300)
    expect(e.cart.value[0].ttype).toBe('I')
  })

  it('should filter refundable cards by recharge mode', () => {
    const e = useBillingEngine()
    e.vipCards.value = [
      { uuid: 'c1', ccode: 'C001', comptype: 'amount', status: 'Y' } as any,
      { uuid: 'c2', ccode: 'C002', comptype: 'times', status: 'Y' } as any,
      { uuid: 'c3', ccode: 'C003', comptype: 'amount', status: 'P' } as any,
    ]
    expect(e.refundableCards.value).toHaveLength(1) // recharge mode

    e.rechargeMode.value = 'refund'
    expect(e.refundableCards.value).toHaveLength(2)
  })
})

describe('useBillingEngine — promotion flow', () => {
  it('should add promotion item with discounted price (mainttype 10)', async () => {
    const e = useBillingEngine()
    const promo = { promotionsid: 'p1', mainttype: '10' }
    const item = { sgcode: 'sg1', itemname: '特价服务', s_price: 100, promotionsprice: 80, ttype: 'S', s_qty: 1 }
    await e.addPromotionItem(promo, item)
    expect(e.cart.value).toHaveLength(1)
    expect(e.cart.value[0].price).toBe(80)
  })

  it('should handle percentage discount promotion (mainttype 20)', async () => {
    const e = useBillingEngine()
    const promo = { promotionsid: 'p2', mainttype: '20', disc: 0.85 }
    const item = { sgcode: 'sg2', itemname: '打折服务', s_price: 200, ttype: 'S', s_qty: 1 }
    await e.addPromotionItem(promo, item)
    expect(e.cart.value[0].secdisc).toBe(0.85)
    expect(e.cart.value[0].price).toBe(200)
  })
})

describe('useBillingEngine — card menu and drag', () => {
  it('should show and close card context menu', () => {
    const e = useBillingEngine()
    const card = { uuid: 'c-1', ccode: 'C001' } as any
    e.showCardMenu({ clientX: 100, clientY: 200, preventDefault: () => {} } as any, card)
    expect(e.cardMenuVisible.value).toBe(true)
    expect(e.cardMenuPos.value.x).toBe(100)
    expect(e.cardMenuPos.value.y).toBe(200)
    e.closeCardMenu()
    expect(e.cardMenuVisible.value).toBe(false)
    expect(e.cardMenuCard.value).toBeNull()
  })

  it('should track dragged card', () => {
    const e = useBillingEngine()
    const card = { uuid: 'c-1' } as any
    e.onCardDragStart(card)
    expect(e.draggedCard.value?.uuid).toBe('c-1')
  })

  it('should handle drop and auto-load card items for times card', () => {
    vi.useFakeTimers()
    const e = useBillingEngine()
    const card = { uuid: 'c-1', ccode: 'C001', comptype: 'times' } as any
    e.draggedCard.value = card
    e.onCardDrop()
    expect(e.selectedCard.value?.uuid).toBe('c-1')
    vi.useRealTimers()
  })
})

describe('useBillingEngine — selectCard updates cart payment', () => {
  it('should update payment method for cart items when card selected', () => {
    const e = useBillingEngine()
    e.addToCart({ code: 'a', name: 'A', price: 100, ttype: 'S' })
    const card = { uuid: 'c-1', ccode: 'C001', cardname: '金卡' } as any
    e.selectCard(card)
    expect(e.selectedCard.value?.uuid).toBe('c-1')
    expect(e.cart.value[0].availableCards.some((c: any) => c.ccode === 'C001')).toBe(true)
  })
})

describe('useBillingEngine — saveHung payload structure', () => {
  it('should send srvcode=i.code for card sale (ttype=C)', async () => {
    // 售卡时，前端传的是卡类编号，后端负责转成卡号
    const e = useBillingEngine()
    e.selectedVip.value = { uuid: 'v-1' } as any
    e.addToCart({ code: '10010', name: '测试卡类', price: 1000, ttype: 'C' } as any)

    const request = (await import('@/api/request')).default as any
    let sentPayload: any = null
    request.post.mockImplementation((_url: string, body: any) => {
      sentPayload = body
      return Promise.resolve({ data: { ok: true } })
    })

    await e.saveHung()
    expect(sentPayload).not.toBeNull()
    expect(sentPayload.items).toHaveLength(1)
    expect(sentPayload.items[0].ttype).toBe('C')
    // 前端传卡类编号（后端在 save_hung_order 中会转为真实卡号）
    expect(sentPayload.items[0].srvcode).toBe('10010')
  })

  it('should send srvcode=card.ccode for recharge (ttype=I)', async () => {
    const e = useBillingEngine()
    e.selectedVip.value = { uuid: 'v-1', vname: '张三', ecode: 'E001' } as any
    const card = { uuid: 'c-1', ccode: 'YIREN01-000002', cardname: '储值卡' } as any
    e.rechargeAmounts.value['YIREN01-000002'] = 500
    e.addRecharge(card)

    const request = (await import('@/api/request')).default as any
    let sentPayload: any = null
    request.post.mockImplementation((_url: string, body: any) => {
      sentPayload = body
      return Promise.resolve({ data: { ok: true } })
    })

    await e.saveHung()
    expect(sentPayload).not.toBeNull()
    expect(sentPayload.items).toHaveLength(1)
    expect(sentPayload.items[0].ttype).toBe('I')
    // 充值时前端传的是真实卡号
    expect(sentPayload.items[0].srvcode).toBe('YIREN01-000002')
  })
})
