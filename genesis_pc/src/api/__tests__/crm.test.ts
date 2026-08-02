import { describe, it, expect, vi, beforeEach } from 'vitest'
import request from '../request'

vi.mock('../request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
  }
}))

import {
  getCrmDicts,
  listCrmRules,
  createCrmRule,
  updateCrmRule,
  deleteCrmRule,
  previewCrmRule,
  runCrmRule,
  listCrmTasks,
  getCrmTaskSummary,
  getCrmTask,
  createCrmTask,
  addCrmTaskAttempt,
  suggestCrmTaskTouch,
  completeCrmTask,
  updateCrmTaskStatus,
  listCrmTimeline,
  createCrmTimeline,
  updateCrmTimeline,
  deleteCrmTimeline,
} from '../crm'

describe('crm API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.setItem('genesis_pc_company', 'testco')
    localStorage.setItem('genesis_pc_storecode', '99')
  })

  it('getCrmDicts passes company scope', async () => {
    await getCrmDicts()
    expect(request.get).toHaveBeenCalledWith('/crm/pc/dicts/', {
      params: { company: 'testco', storecode: '99' }
    })
  })

  it('rule CRUD', async () => {
    await listCrmRules()
    expect(request.get).toHaveBeenCalledWith('/crm/pc/rules/', {
      params: { company: 'testco', storecode: '99' }
    })
    await createCrmRule({ rule_name: '生日关怀' })
    expect(request.post).toHaveBeenCalledWith('/crm/pc/rules/', {
      company: 'testco', storecode: '99', rule_name: '生日关怀'
    })
    await updateCrmRule('r1', { rule_name: '新名称' })
    expect(request.put).toHaveBeenCalledWith('/crm/pc/rules/r1/', {
      company: 'testco', storecode: '99', rule_name: '新名称'
    })
    await deleteCrmRule('r1')
    expect(request.delete).toHaveBeenCalledWith('/crm/pc/rules/r1/', {
      params: { company: 'testco', storecode: '99' }
    })
  })

  it('rule preview and run', async () => {
    await previewCrmRule('r1', { date: '2026-08-01', limit: 10 })
    expect(request.get).toHaveBeenCalledWith('/crm/pc/rules/r1/preview/', {
      params: { company: 'testco', storecode: '99', date: '2026-08-01', limit: 10 }
    })
    await runCrmRule('r1', { limit: 20 })
    expect(request.post).toHaveBeenCalledWith('/crm/pc/rules/r1/run/', {
      company: 'testco', storecode: '99', limit: 20
    })
  })

  it('task workflow', async () => {
    await listCrmTasks({ status: '10' })
    expect(request.get).toHaveBeenCalledWith('/crm/pc/tasks/', {
      params: { company: 'testco', storecode: '99', status: '10' }
    })
    await getCrmTask('t1')
    expect(request.get).toHaveBeenCalledWith('/crm/pc/tasks/t1/', {
      params: { company: 'testco', storecode: '99' }
    })
    await createCrmTask({ vipuuid: 'v1' })
    expect(request.post).toHaveBeenCalledWith('/crm/pc/tasks/', {
      company: 'testco', storecode: '99', vipuuid: 'v1'
    })
    await addCrmTaskAttempt('t1', { channel: '10', outcome: '10', detail: '联系成功' })
    expect(request.post).toHaveBeenCalledWith('/crm/pc/tasks/t1/attempt/', {
      company: 'testco', storecode: '99', channel: '10', outcome: '10', detail: '联系成功'
    })
    await suggestCrmTaskTouch('t1', { channel: '20', outcome: '10' })
    expect(request.post).toHaveBeenCalledWith('/crm/pc/tasks/t1/suggest/', {
      company: 'testco', storecode: '99', channel: '20', outcome: '10'
    })
    await completeCrmTask('t1', { note: '完成' })
    expect(request.post).toHaveBeenCalledWith('/crm/pc/tasks/t1/complete/', {
      company: 'testco', storecode: '99', note: '完成'
    })
    await updateCrmTaskStatus('t1', { status: '40' })
    expect(request.post).toHaveBeenCalledWith('/crm/pc/tasks/t1/status/', {
      company: 'testco', storecode: '99', status: '40'
    })
  })

  it('task summary', async () => {
    await getCrmTaskSummary({ scope: 'store', keyword: '张' })
    expect(request.get).toHaveBeenCalledWith('/crm/pc/tasks/summary/', {
      params: { company: 'testco', storecode: '99', scope: 'store', keyword: '张' }
    })
  })

  it('timeline CRUD', async () => {
    await listCrmTimeline({ vipuuid: 'v1' })
    expect(request.get).toHaveBeenCalledWith('/crm/pc/timeline/', {
      params: { company: 'testco', storecode: '99', vipuuid: 'v1' }
    })
    await createCrmTimeline({ vipuuid: 'v1', detail: '电话关怀' })
    expect(request.post).toHaveBeenCalledWith('/crm/pc/timeline/', {
      company: 'testco', storecode: '99', vipuuid: 'v1', detail: '电话关怀'
    })
    await updateCrmTimeline('l1', { detail: '更新' })
    expect(request.put).toHaveBeenCalledWith('/crm/pc/timeline/l1/', {
      company: 'testco', storecode: '99', detail: '更新'
    })
    await deleteCrmTimeline('l1')
    expect(request.delete).toHaveBeenCalledWith('/crm/pc/timeline/l1/', {
      params: { company: 'testco', storecode: '99' }
    })
  })
})
