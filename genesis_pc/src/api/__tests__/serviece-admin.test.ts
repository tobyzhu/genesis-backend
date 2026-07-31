import { describe, it, expect, vi, beforeEach } from 'vitest'
import request from '../request'

vi.mock('../request', () => ({
  default: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() }
}))

import { getSrvtoptyTree, getServieceList, getServieceMeta } from '../serviece-admin'

describe('serviece-admin API', () => {
  beforeEach(() => { vi.clearAllMocks() })

  it('getSrvtoptyTree calls correct endpoint', async () => {
    await getSrvtoptyTree({ company: 'yiren' })
    expect(request.get).toHaveBeenCalledWith('/adviser/srvtopty-tree/', { params: { company: 'yiren' } })
  })

  it('getServieceList calls correct endpoint with filters', async () => {
    await getServieceList({ topcode: '100', page: 1 })
    expect(request.get).toHaveBeenCalledWith('/adviser/sysadmin-data/baseinfo.serviece/', { params: { topcode: '100', page: 1 } })
  })

  it('getServieceMeta calls correct endpoint', async () => {
    await getServieceMeta()
    expect(request.get).toHaveBeenCalledWith('/adviser/sysadmin-models/baseinfo.serviece/meta/')
  })
})
