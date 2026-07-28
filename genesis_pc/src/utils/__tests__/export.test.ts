import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { exportCSV, exportExcel } from '../export'

let mockAnchor: { href: string; download: string; click: ReturnType<typeof vi.fn> }

beforeEach(() => {
  mockAnchor = { href: '', download: '', click: vi.fn() }
  vi.spyOn(document, 'createElement').mockImplementation((tag: string) => {
    if (tag === 'a') return mockAnchor as unknown as HTMLAnchorElement
    return document.createElement(tag)
  })
  vi.spyOn(URL, 'createObjectURL').mockImplementation(() => 'blob:mock/url')
  vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
})

afterEach(() => { vi.restoreAllMocks() })

describe('exportCSV', () => {
  const columns = [
    { label: '姓名', prop: 'name' },
    { label: '手机号', prop: 'phone' },
    { label: '余额', prop: 'balance' },
  ]
  const data = [
    { name: '张三', phone: '13800138000', balance: 500 },
    { name: '李四', phone: '13900139000', balance: 1200.5 },
  ]

  it('should create download link with .csv filename', () => {
    exportCSV(columns, data, '会员列表')
    expect(mockAnchor.download).toBe('会员列表.csv')
    expect(mockAnchor.click).toHaveBeenCalledTimes(1)
  })

  it('should pass blob to createObjectURL and revoke after click', () => {
    exportCSV(columns, data, 'test')
    expect(URL.createObjectURL).toHaveBeenCalledOnce()
    expect(mockAnchor.href).toBe('blob:mock/url')
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:mock/url')
  })

  it('should handle empty data without throwing', () => {
    expect(() => exportCSV(columns, [], 'empty')).not.toThrow()
    expect(mockAnchor.click).toHaveBeenCalled()
  })

  it('should escape values with commas and quotes', () => {
    const special = [{ name: '王,五', phone: '"test"', balance: 100 }]
    expect(() => exportCSV(columns, special, 'escape')).not.toThrow()
  })
})

describe('exportExcel', () => {
  const columns = [{ label: '项目', prop: 'item' }, { label: '金额', prop: 'amount' }]
  const data = [{ item: '面部护理', amount: 380 }, { item: '肩颈按摩', amount: 280 }]

  it('should create download link with .xls filename', () => {
    exportExcel(columns, data, '报表')
    expect(mockAnchor.download).toBe('报表.xls')
    expect(mockAnchor.click).toHaveBeenCalled()
  })

  it('should handle empty data', () => {
    expect(() => exportExcel(columns, [], 'empty')).not.toThrow()
    expect(mockAnchor.click).toHaveBeenCalled()
  })

  it('should create and revoke blob URL', () => {
    exportExcel(columns, data, 'test')
    expect(URL.createObjectURL).toHaveBeenCalledOnce()
    expect(URL.revokeObjectURL).toHaveBeenCalled()
  })
})
