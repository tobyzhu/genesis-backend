import { describe, it, expect, vi, beforeEach } from 'vitest'
import request from '../request'

// Mock request module
vi.mock('../request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
}))

import {
  getModelGroups, getModelMeta, getModelData,
  createModelData, updateModelData, deleteModelData,
  searchRelated
} from '../sysadmin'

describe('sysadmin API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('getModelGroups', () => {
    it('calls GET /adviser/sysadmin-models/', async () => {
      await getModelGroups()
      expect(request.get).toHaveBeenCalledWith('/adviser/sysadmin-models/')
    })
  })

  describe('getModelMeta', () => {
    it('calls GET with app_label.model_name', async () => {
      await getModelMeta('baseinfo', 'paymode')
      expect(request.get).toHaveBeenCalledWith('/adviser/sysadmin-models/baseinfo.paymode/meta/')
    })
  })

  describe('getModelData', () => {
    it('calls GET with params', async () => {
      await getModelData('baseinfo', 'paymode', { page: 1, page_size: 20 })
      expect(request.get).toHaveBeenCalledWith(
        '/adviser/sysadmin-data/baseinfo.paymode/',
        { params: { page: 1, page_size: 20 } }
      )
    })

    it('works without params', async () => {
      await getModelData('baseinfo', 'paymode')
      expect(request.get).toHaveBeenCalledWith(
        '/adviser/sysadmin-data/baseinfo.paymode/',
        { params: undefined }
      )
    })
  })

  describe('createModelData', () => {
    it('calls POST with data', async () => {
      const data = { pcode: 'A', pname: '现金', iscash: '1' }
      await createModelData('baseinfo', 'paymode', data)
      expect(request.post).toHaveBeenCalledWith(
        '/adviser/sysadmin-data/baseinfo.paymode/',
        data
      )
    })
  })

  describe('updateModelData', () => {
    it('calls PUT with pk and data', async () => {
      const data = { pname: 'Updated' }
      await updateModelData('baseinfo', 'paymode', 1, data)
      expect(request.put).toHaveBeenCalledWith(
        '/adviser/sysadmin-data/baseinfo.paymode/1/',
        data
      )
    })
  })

  describe('deleteModelData', () => {
    it('calls DELETE with pk', async () => {
      await deleteModelData('baseinfo', 'paymode', 1)
      expect(request.delete).toHaveBeenCalledWith('/adviser/sysadmin-data/baseinfo.paymode/1/')
    })
  })

  describe('searchRelated', () => {
    it('calls GET /adviser/sysadmin-search/ with params', async () => {
      await searchRelated('baseinfo.storeinfo', 'yiren')
      expect(request.get).toHaveBeenCalledWith('/adviser/sysadmin-search/', {
        params: { model: 'baseinfo.storeinfo', q: 'yiren' }
      })
    })
  })
})
