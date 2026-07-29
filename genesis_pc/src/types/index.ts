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
  vip_uuid: string
  vcode: string
  vname: string
  mtcode: string
  employee_code: string
  employee_name: string
  booking_date: string
  start_time: string
  end_time: string
  room_id: string
  room_name: string
  instrument_id: string
  instrument_name: string
  room_start_time: string
  room_end_time: string
  instrument_start_time: string
  instrument_end_time: string
  staff_start_time: string
  staff_end_time: string
  status: string       // 100=未到店 200=已到店 210=进房间 220=服务中 230=已完成 290=离店 390=取消
  detail: string
  comein_time: string
  leave_time: string
}

/** 预约员工 */
export interface BookingEmployee {
  ecode: string
  ename: string
  position: string
  positiondesc: string
}

/** 房间 */
export interface BookingRoom {
  roomid: string
  roomname: string
}

/** 仪器 */
export interface BookingInstrument {
  instrumentid: string
  instrumentname: string
}

/** 排班 */
export interface BookingSchedule {
  ecode: string
  scheduleid: string
  operno: string
  flag: string
}

/** 时段模板 */
export interface BookingTimeset {
  timeid: string
  flag: string
}

/** 冲突检测结果 */
export interface ConflictInfo {
  type: string
  booking_id: number
  vname: string
  start: string
  end: string
}

/** 状态变更响应 */
export interface StatusChangeResult {
  status: string
  booking_status: string
  timestamp: string
}

/** 预约状态常量 */
export const BOOKING_STATUS_MAP: Record<string, { label: string; color: string }> = {
  '100': { label: '未到店', color: '#E6A23C' },
  '200': { label: '已到店', color: '#67C23A' },
  '210': { label: '进房间', color: '#409EFF' },
  '220': { label: '服务中', color: '#1890FF' },
  '224': { label: '仪器开始', color: '#722ED1' },
  '227': { label: '仪器结束', color: '#722ED1' },
  '230': { label: '已完成', color: '#52C41A' },
  '240': { label: '离房', color: '#13C2C2' },
  '250': { label: '呼叫清洁', color: '#FA8C16' },
  '260': { label: '清洁中', color: '#FA8C16' },
  '270': { label: '清洁完成', color: '#52C41A' },
  '290': { label: '离店', color: '#C0C4CC' },
  '390': { label: '取消', color: '#F56C6C' },
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

// ====== 商品主数据 ======
export interface Goods {
  uuid: string
  gcode: string
  gname: string
  brand: string
  spec: string
  barcode: string
  unit: string
  price: number
  price2: number
  price3: number
  buyprc: number
  qty: number
  minivalues: number
  maxvalues: number
  displayclass1: string
  displayclass2: string
  marketclass1: string
  marketclass2: string
  goodsct: string
  discountclass: string
  saleflag: string
  valiflag: string
  supplierid: string
  location: string
  desc1: string
  desc2: string
  desc3: string
  tags: string[]
  storelist: string[]
  costprc: number
}

// ====== 库存查询 ======
export interface StockItem {
  storecode: string
  whcode: string
  gcode: string
  qty: number
  vdate: string
  gname: string
  spec: string
  brand: string
  unit: string
  minivalues: number
  maxvalues: number
  goodsuuid: string
  alert: 'normal' | 'low' | 'high'
}

// ====== 库存流水 ======
export interface TranslogItem {
  gtranukid: number
  sukid: string
  saleatr: string
  saleatr_name: string
  vdate: string
  doccode: string
  storecode: string
  whcode: string
  gcode: string
  gname: string
  qty: number
  price: number
  amount: number
  qty2: number
  batch: string
  goodsvaldate: string
  gnote: string
  create_time: string
}

// ====== 仓库 ======
export interface Warehouse {
  wharehousecode: string
  wharehousename: string
  storecode: string
}

// ====== 门店 ======
export interface StoreOption {
  storecode: string
  storename: string
}
