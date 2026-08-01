import { describe, it, expect, vi, beforeEach } from 'vitest'
import request from '../request'

vi.mock('../request', () => ({
  default: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }
}))

import {
  getCardtypeFastList, getRulerList, saveRuler, deleteRuler,
  getCardtypeDiscountRules, saveCardtypeDiscountRules, getCardPricing
} from '../card-admin'

describe('card-admin API', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('getCardtypeFastList calls correct endpoint', async () => {
    await getCardtypeFastList({ comptype: 'amount', page: 1 })
    expect(request.get).toHaveBeenCalledWith('/adviser/cardtype-list/', {
      params: { comptype: 'amount', page: 1 },
    })
  })

  it('getRulerList calls correct endpoint', async () => {
    await getRulerList()
    expect(request.get).toHaveBeenCalledWith('/adviser/ruler-list/', { params: undefined })
  })

  it('saveRuler posts to save endpoint', async () => {
    await saveRuler({ rulername: '拓客卡', ruler: '#ttype=S#srvcode=105001#1sttimes=1260#others=720#' })
    expect(request.post).toHaveBeenCalledWith('/adviser/ruler-save/', {
      rulername: '拓客卡',
      ruler: '#ttype=S#srvcode=105001#1sttimes=1260#others=720#',
    })
  })

  it('deleteRuler posts id', async () => {
    await deleteRuler(1)
    expect(request.post).toHaveBeenCalledWith('/adviser/ruler-delete/', { id: 1 })
  })

  it('getCardtypeDiscountRules passes cardtype', async () => {
    await getCardtypeDiscountRules('CT001')
    expect(request.get).toHaveBeenCalledWith('/adviser/cardtype-discount-list/', {
      params: { cardtype: 'CT001' },
    })
  })

  it('saveCardtypeDiscountRules posts batch rules', async () => {
    const rules = [{ ttype: 'S', discountclass: '10', discounttype: 'DISC', disc: 0.8 }]
    await saveCardtypeDiscountRules('CT001', rules)
    expect(request.post).toHaveBeenCalledWith('/adviser/cardtype-discount-save/', {
      cardtype: 'CT001',
      rules,
    })
  })

  it('getCardPricing posts items payload', async () => {
    const payload = { cardtypeuuid: 'uuid-1', items: [{ ttype: 'S', code: 'SV001', price: 1000 }] }
    await getCardPricing(payload)
    expect(request.post).toHaveBeenCalledWith('/adviser/card-pricing/', payload)
  })
})
