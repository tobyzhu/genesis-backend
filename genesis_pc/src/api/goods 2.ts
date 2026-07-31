import request from './request'
import type { PageResponse, Goods, StockItem, TranslogItem, Warehouse, StoreOption } from '@/types'

const company = () => localStorage.getItem('genesis_pc_company') || ''
const storecode = () => localStorage.getItem('genesis_pc_storecode') || ''

// ===== 商品主数据 CRUD =====

export function getGoodsList(params?: Record<string, any>) {
  return request.get<PageResponse<Goods>>('/baseinfo/goods/', {
    params: { company: company(), ...params },
  })
}

export function getGoods(uuid: string) {
  return request.get<Goods>(`/baseinfo/goods/${uuid}/`)
}

export function createGoods(data: Partial<Goods>) {
  return request.post<Goods>('/baseinfo/goods/', { ...data, company: company(), flag: 'Y' })
}

export function updateGoods(uuid: string, data: Partial<Goods>) {
  return request.patch<Goods>(`/baseinfo/goods/${uuid}/`, data)
}

export function deleteGoods(uuid: string) {
  return request.delete(`/baseinfo/goods/${uuid}/`)
}

// ===== 品牌 / 分类选项 =====

export function getGoodsBrands() {
  return request.get<Array<{ code: string; name: string }>>('/baseinfo/get_brandlist/', {
    params: { company: company(), type: 'goods' },
  })
}

export function getGoodsDisplayClasses(brand?: string) {
  return request.get<Array<{ code: string; name: string }>>('/baseinfo/get_displayclass_bybrand/', {
    params: { company: company(), type: 'goods', brand: brand || '' },
  })
}

export function getAppoptionBySeg(seg: string) {
  return request.get<Array<{ itemname: string; itemvalues: string }>>('/baseinfo/get_appoption_byseg/', {
    params: { company: company(), seg },
  })
}

// ===== 库存查询 =====

export function getStockQuery(params?: Record<string, any>) {
  return request.get<StockItem[]>('/goods/stock-query/', {
    params: { company: company(), ...params },
  })
}

// ===== 入库 =====

export function createInbound(data: {
  storecode: string
  whcode: string
  vdate?: string
  note?: string
  supplierid?: string
  ecode?: string
  items: Array<{
    gcode: string
    qty: number
    price?: number
    goodsvaldate?: string
    batch?: string
  }>
}) {
  return request.post('/goods/inbound/', { company: company(), ...data })
}

// ===== 出库 =====

export function createOutbound(data: {
  storecode: string
  whcode: string
  out_type?: 'O' | 'U' | 'F'
  vdate?: string
  note?: string
  ecode?: string
  items: Array<{
    gcode: string
    qty: number
    price?: number
    goodsvaldate?: string
    batch?: string
  }>
}) {
  return request.post('/goods/outbound/', { company: company(), ...data })
}

// ===== 调拨 =====

export function createTransfer(data: {
  out_storecode: string
  out_whcode: string
  in_storecode: string
  in_whcode: string
  vdate?: string
  note?: string
  ecode?: string
  items: Array<{
    gcode: string
    qty: number
    price?: number
    goodsvaldate?: string
    batch?: string
  }>
}) {
  return request.post('/goods/transfer/', { company: company(), ...data })
}

// ===== 库存流水 =====

export function getTranslog(params?: Record<string, any>) {
  return request.get<{
    count: number
    page: number
    page_size: number
    results: TranslogItem[]
  }>('/goods/translog/', { params: { company: company(), ...params } })
}

// ===== 仓库 / 门店 =====

export function getWharehouses(storecodeParam?: string) {
  return request.get<Warehouse[]>('/goods/wharehouses/', {
    params: { company: company(), storecode: storecodeParam || '' },
  })
}

export function getStores() {
  return request.get<StoreOption[]>('/goods/stores/', {
    params: { company: company() },
  })
}

// ===== 单据确认 / 作废 / 列表 =====

export function confirmDocument(sukid: string, ecode?: string) {
  return request.post('/goods/confirm/', { company: company(), sukid, ecode: ecode || '' })
}

export function cancelDocument(sukid: string) {
  return request.post('/goods/cancel/', { company: company(), sukid })
}

export function getDocumentList(params?: Record<string, any>) {
  return request.get<{ count: number; results: any[] }>('/goods/documents/', {
    params: { company: company(), ...params },
  })
}

export function getDocumentDetail(sukid: string) {
  return request.get('/goods/document-detail/', { params: { company: company(), sukid } })
}

export function getSuppliers() {
  return request.get<Array<{supplierid: string; suppliername: string}>>('/goods/suppliers/', {
    params: { company: company() },
  })
}

export function updateDocument(sukid: string, data: { note?: string; items?: Array<{gcode: string; qty: number; price: number; goodsvaldate?: string}> }) {
  return request.post('/goods/document-update/', { company: company(), sukid, ...data })
}
