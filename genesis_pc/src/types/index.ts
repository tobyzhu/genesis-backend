// ====== 通用分页响应 ======
export interface PageResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// ====== 用户 / 登录 ======
export interface LoginParams {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  user?: {
    id: number
    username: string
    display_name?: string
  }
}

// ====== VIP 客户 ======
export interface Vip {
  uuid: string
  vcode: string
  vname: string
  mtcode: string        // 手机号
  viplevel: string
  sex: string
  birth: string
  indate: string
  status: string
  viptype: string
  telph: string
  wechat: string
  addr: string
  email: string
  qq: string
  source: string
  occupation: string
  ecode: string
  ecode2: string
  company: string
  storecode: string
  vdesc: string
}

// ====== 项目 / 商品 ======
export interface Item {
  id: number
  name: string
  category: string
  price: number
  cost_price?: number
  unit?: string
  status?: boolean
}

// ====== 卡类 ======
export interface CardInfo {
  id: number
  name: string
  stype: string       // 卡类型：stored_value | package | period
  price: number
  balance?: number
  valid_days?: number
  status?: boolean
}

// ====== 预约 ======
export interface Booking {
  id: number
  vip_id: number
  vip_name: string
  item_name: string
  employee_name?: string
  start_time: string
  end_time?: string
  status: string       // pending | confirmed | completed | cancelled
  remark?: string
}

// ====== 收银开单 ======
export interface CheckoutItem {
  item_id: number
  item_name: string
  quantity: number
  price: number
  discount?: number
  card_id?: number
}

export interface CheckoutParams {
  vip_id: number
  items: CheckoutItem[]
  pay_type: string
  remark?: string
}

// ====== 报表 ======
export interface ReportRow {
  label: string
  value: number
  rate?: number
}

// ====== 会员卡 ======
export interface VipCard {
  uuid: string
  vcode: string
  ccode: string
  cardtype: string
  cardname: string
  cardtypeuuid: string
  leftmoney: number
  s_price: number
  leftqty: number
  promotionsid: string
  suptype: string
  comptype: string
  status: string
  stype: string
  valdate: string
  promotionname: string
  carddesc: string
}

// ====== 可添加到购物车的项目 ======
export interface CartableItem {
  code: string
  name: string
  price: number
  ttype: string
}

// ====== 分组卡片数据 ======
export interface CardGroup {
  promotionName: string
  comptypeGroups: Array<{
    typeName: string
    cards: VipCard[]
  }>
}
