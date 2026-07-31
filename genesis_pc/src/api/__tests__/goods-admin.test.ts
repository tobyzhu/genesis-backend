import { describe, it, expect, vi, beforeEach } from 'vitest'
import request from '../request'

vi.mock('../request', () => ({
  default: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }
}))

import {
  getGoodsctTree, saveGoodsct, deleteGoodsct,
  getGoodsFastList, getAppOptionList
} from '../goods-admin'

describe('goods-admin API', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('getGoodsctTree calls correct endpoint', async () => {
    await getGoodsctTree({ company: 'yiren' })
    expect(request.get).toHaveBeenCalledWith('/adviser/goodsct-tree/', { params: { company: 'yiren' } })
  })

  it('saveGoodsct posts to save endpoint', async () => {
    await saveGoodsct({ goodsct: '01', goodsctname: '护肤' })
    expect(request.post).toHaveBeenCalledWith('/adviser/goodsct-save/', { goodsct: '01', goodsctname: '护肤' })
  })

  it('deleteGoodsct posts pk to delete endpoint', async () => {
    await deleteGoodsct('uuid-1')
    expect(request.post).toHaveBeenCalledWith('/adviser/goodsct-delete/', { pk: 'uuid-1' })
  })

  it('getGoodsFastList calls correct endpoint with params', async () => {
    await getGoodsFastList({ goodsct: '01', page: 1 })
    expect(request.get).toHaveBeenCalledWith('/adviser/goods-list/', { params: { goodsct: '01', page: 1 } })
  })

  it('getAppOptionList passes seg and params', async () => {
    await getAppOptionList('brand')
    expect(request.get).toHaveBeenCalledWith('/adviser/appoption-list/', { params: { seg: 'brand' } })
  })
})
