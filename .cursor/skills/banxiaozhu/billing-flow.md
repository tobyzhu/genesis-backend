# 手工开单业务流程（genesis_pc ↔ adviser）

## 数据流总览（v2 新版）

```
BillingPageV2.vue (模板层, ~500行)
└─ useBillingEngine.ts (业务逻辑层, ~420行)
     ├─ 搜索会员 → searchVip/selectVip
     │   ├─ fetchVipCards    → /adviser/get_vip_cardlist/
     │   ├─ fetchItems       → /adviser/categorized_items/ (分类树)
     │   ├─ fetchEmployees   → /adviser/get_bookingable_empllist/
     │   └─ fetchPromotions  → /adviser/active_promotions/
     │
     ├─ 选品区(S/G/C/I标签)
     │   ├─ 分类树(左) + 项目网格(右)
     │   ├─ 缓存: sessionStorage, 30min TTL
     │   └─ 防抖: addToCart 300ms 过滤双击
     │
     ├─ 活动标签(P)
     │   ├─ 两级加载: 列表(无uuid) → 明细(有uuid)
     │   ├─ 缓存: 列表10min, 明细不缓存
     │   └─ selectAndLoadPromotion 懒加载明细
     │
     ├─ 购物车(Tree View)
     │   ├─ cartGroups computed → 按 S/G/C/I 分组
     │   ├─ 每行: 属性/数量/单价/折扣率%/金额折扣/小计/正退/扣款/员工
     │   ├─ secdisc: el-input-number formatter="80%" parser="->0.8"
     │   └─ 退款/作废独立 panel, 不混在购物车里
     │
     └─ 保存 → saveHung → POST /adviser/save_hung/
          ├─ items + voidItems + refundItems 合并发送
          ├─ promotionsid 校验 (同一活动不能混单)
          └─ 保存后刷新名下卡片
```

## 前端关键文件

| 文件 | 行数 | 说明 |
|---|---|---|
| `genesis_pc/src/views/adviser/BillingPageV2.vue` | ~500 | 手工开单 v2 主页面 |
| `genesis_pc/src/composables/useBillingEngine.ts` | ~420 | 开单业务逻辑引擎(可复用/可测试) |
| `genesis_pc/src/api/cashier.ts` | ~100 | 开单/保存/活动 API |
| `genesis_pc/src/api/common.ts` | 员工列表 API |
| `genesis_pc/src/utils/cache.ts` | sessionStorage 缓存工具(TTL) |

## 后端关键文件 (adviser/views.py)

| 函数 | 路由 | 说明 |
|---|---|---|
| `save_hung_order()` | `POST /adviser/save_hung/` | 保存挂账单(含售卡/充值/活动校验) |
| `getserno()` | 内部 | 生成流水号 |
| `categorized_items()` | `GET /adviser/categorized_items/` | 按 displayclass1 分类树 + 项目列表 |
| `active_promotions()` | `GET /adviser/active_promotions/` | 营销活动(两级: list/detail) |
| `get_checkedout_orders()` | `GET /adviser/get_checkedout_orders/` | 已结账订单(退款用) |
| `cardtype_service_items()` | `GET /adviser/cardtype_service_items/` | 计次卡关联服务项目 |
| `cardtype_prices()` | `GET /adviser/cardtype_prices/` | 疗程卡价格选项 |
| `NewCardHung()` | `POST /adviser/newcardhung/` | 售卡(帮小主) |
| `FillCardHung()` | `POST /adviser/fillcardhung/` | 充值(帮小主) |
| `get_hung_list()` | `GET /adviser/get_hung_list/` | 挂单列表 |
| `get_hung_detail()` | `GET /adviser/get_hung_detail/` | 挂单明细(含员工code) |
| `get_hung_byvipuuid()` | `GET /adviser/get_hung_byvipuuid/` | 某会员未结账挂单 |

## 营销活动支持

### 活动类型

| mainttype | 名称 | 数据来源 | 关联字段 |
|---|---|---|---|
| '10' | 特价活动 | Promotionsgroupdetail | pgroupid = promotions.mainpgroupid |
| '20' | 特殊折扣活动 | Promotionsgroupdetail | pgroupid = promotions.mainpgroupid |
| '30' | 组合销售活动 | Promotionsdetail | promotionsid = promotions.promotionsid |

### 活动明细字段映射

**特价/折扣活动 (Promotionsgroupdetail):**
```
pgcode → sgcode (项目编码)
ttype → ttype (S/G)
qty1 → s_qty / promotionsqty (数量)
price1 → promotionsprice (活动价)
oriprice → s_price (原价)
amount1 → promotionsamount (金额)
```

**组合活动 (Promotionsdetail):**
```
sgcode → sgcode (项目编码)
ttype → ttype (S/G/C)
promotionsqty → qty (数量)
promotionsprice → price (单价)
promotionsamount → amount (金额)
combo_total = sum(各明细 promotionsamount) (套餐总价)
```

### 加入购物车规则

| 场景 | 行为 |
|---|---|
| 购物车为空 | 直接添加 |
| 已有同一活动的项目(promotionsid相同) | 合并添加, 不弹框 |
| 已有不同/无活动的项目 | 弹框确认 → 清空 → 添加 |
| 组合活动(点任意明细项) | 全部添加(同上规则) |

### API: active_promotions

```
GET /adviser/active_promotions/?company=yiren
  → 列表(无明细), 缓存10min

GET /adviser/active_promotions/?company=yiren&uuid=xxx
  → 完整明细(含items/group_items), 不缓存
```

## 模型关系

```
ExpvstollHung (挂单主表)
│  pk: uuid
│  exptxserno_hung  (流水号: yiren01_hung_N)
│  vsdate_hung, vstime_hung
│  vipuuid → Vip
│  vcode_hung, vipcode (会员编码)
│  ccode_hung (付款卡号), cardtype_hung (付款卡类)
│  totmount_hung (总金额, 含折扣)
│  psstatus_hung (10=开单, 40=服务完成, 50=可结账, 60=挂账, 70=已结账)
│  ttype_hung (S/G/C/I)
│  promotionsid (活动编号, 活动开单时记录)
│  valiflag_hung='Y', flag='Y'
│
└── ExpenseHung (挂单明细, FK: hunguuid → ExpvstollHung)
      ditem_hung (4位顺序号, 0001-9999)
      ttype_hung (S/G/C/I)
      stype_hung (N=正常, P=赠送)
      srvcode_hung (项目编码)
      s_price_hung (单价)
      s_qty_hung (数量, 可负=退款/作废)
      secdisc_hung (折扣率, 0~1)
      srvmondisc_hung (金额折扣)
      s_mount_hung = s_qty * s_price * secdisc - srvmondisc
      srvactmount_hung = s_mount_hung
      pmcode_hung (开单员工ecode)
      asscode1_hung (美疗师1 ecode)
      asscode2_hung (美疗师2 ecode)
      otherserno_hung (付款卡号)
      depositeflag ('N')
```

### 活动相关模型

```
Promotions (活动主表)
├─ promotionsid (活动编号, CharField)
├─ promotionsname (活动名称)
├─ mainttype: 10=特价, 20=折扣, 30=组合
├─ fromdate / todate (有效期 YYYYMMDD, 空则不限制)
├─ disc (折扣率)
├─ s_price (组合活动总价)
├─ mainpgroupid (CharField, 特价/折扣→Promotionsgroupdetail)
├─ promotionsgroupid (FK→Promotionsgroup, 组合活动分组)
└─ promotionsstatus ('active'=有效, 'past'=过期)

Promotionsdetail (活动明细)
├─ promotionsuuid (FK→Promotions, 所有活动通用)
├─ promotionsid (CharField, 组合活动用此关联)
├─ ttype (S/G/C)
├─ sgcode (项目编码)
├─ s_qty / s_price (原始数量/单价)
├─ promotionsqty / promotionsprice / promotionsamount (活动数量/单价/金额)
└─ stype (N=正常, P=赠送)

Promotionsgroupdetail (折扣分类活动明细)
├─ pgroupid (CharField = promotions.mainpgroupid)
├─ ttype (S/G)
├─ pgcode (项目编码)
├─ qty1 / price1 (活动数量/单价)
├─ oriprice (原价)
├─ amount1 (金额)
└─ disc (折扣)
```

## 购物车数据结构 (CartItem)

```typescript
interface CartItem {
  code: string           // 项目编码
  name: string           // 项目名称
  price: number          // 单价
  qty: number            // 数量(负数=退款/作废)
  ttype: 'S'|'G'|'C'|'I'// 类型
  stype: 'N'|'P'         // 正常/赠送
  secdisc: number        // 折扣率 0~1 (前端显示为 %)
  srvmondisc: number     // 金额折扣
  payMethod: string      // cash / card:卡号 / balance
  pmcode: string         // 开单员工
  asscode1: string       // 美疗师1
  asscode2: string       // 美疗师2
  availableCards: VipCard[]
  promotionsid?: string  // 活动编号(活动项目携带)
}
```

## 业务规则

### 售卡 (ttype='C')
- 卡号：`Vip.nextccode()` → `vcode-XXXX` 格式(会员维度)
- 储值卡：`leftmoney = s_price`, `promotionsid` 记录活动编号
- 疗程卡：`leftqty = s_qty`, `promotionsid` 记录活动编号
- 字段：`cardtype=srvcode`, `cardtypeuuid=Cardtype`, `isic='0'`
- 疗程卡售卡时可修改数量/单价, 折扣率用%, 差额用金额折扣补齐

### 充值 (ttype='I')
- 按卡号(`srvcode`) 查找 Cardinfo
- 储值卡：`leftmoney += s_price`
- 疗程卡：`leftqty += s_price`
- s_price 可为负数(退卡), s_qty 可为负数(退服务/商品)

### 退款 (独立面板)
- 退款开单模式 → 显示已结账订单列表(最近1个月, 可日期筛选)
- 勾选明细项 → 加入购物车(数量为负, 员工信息保留原单)
- 与正常开单数据隔离

### 作废 (独立面板)
- 作废开单模式 → 显示未结账挂单
- 勾选明细项 → 加入购物车(数量为负)
- 不走财务流程, 仅取消未结账交易

### 折扣计算
- `小计 = qty × price × secdisc − srvmondisc`
- `totmount_hung = sum(各明细小计)`(含折扣)
- 折扣率前端用百分比显示(80% ↔ 0.8), el-input-number formatter/parser

### 员工默认值
- 开单 = vip.ecode (负责顾问)
- 美疗师1 = vip.ecode2 (负责美疗师)
- 美疗师2 = 空(手动选择)
- 退款时员工自动取原单的 pmcode/asscode1/asscode2

### 活动开单约束
- 同一张挂单只能有一个活动的项目
- 不同活动的 promotionsid 不能混在同一张单上
- 活动项目加入购物车时, 购物车已有同活动项目则合并, 不同活动则清空提醒
- save_hung 时校验: `if len(promo_ids) > 1 → 报错`

### 缓存策略
- 服务/商品/卡类列表: sessionStorage, TTL=30min
- 分类树: sessionStorage, TTL=30min
- 活动列表: sessionStorage, TTL=10min
- 活动明细: 不缓存(按需加载)
- 名下卡片/会员搜索: 不缓存(实时数据)
- 缓存 key 带版本号, 后端结构变更时递增

## 路由

| 路径 | 页面 | 说明 |
|---|---|---|
| `/adviser/billing` | BillingPage | 手工开单(v1 旧版) |
| `/adviser/billing-v2` | BillingPageV2 | 手工开单v2(新版) |
| `/adviser/hungs` | HungOrdersPage | 已完成开单 |
| `/report` | ReportPage | 卡余额汇总 |
| `/report/performance` | StorePerformancePage | 门店业绩流水表 |

## 菜单结构 (MainLayout.vue)

```
├─ 工作台
├─ 开单
│  ├ 手工开单
│  ├ 手工开单-v2
│  └ 已完成开单
├─ 客户管理 (会员管理 / 客户关怀)
├─ 业务运营 (预约管理 / 商品管理 / 营销活动)
└─ 数据与分析 (卡余额汇总 / 门店业绩 / AI 助手 / 数据管理)
```

## PSSTATUS 状态码

| 值 | 含义 | 说明 |
|----|------|------|
| 10 | 开单 | 已保存挂账, 未开始 |
| 20 | 到店 | 客人已到店 |
| 30 | 配料 | 开始准备 |
| 40 | 服务完成 | 服务已做完 |
| 50 | 可结账 | 可进入结账流程 |
| 60 | 挂账 | 已挂账待处理 |
| 70 | 已结账 | 已完成结账 |

## 付款信息存储设计

### 设计背景
- 挂账阶段不确定客户最终如何付款, 但需要记录开单时选定的扣款方式作为结账默认值
- 报表需要按 `项目类型×付款方式` 统计(服务卡收款/服务现金收款/商品卡收款/商品现金收款等)
- 员工提成按项目类型和付款方式不同

### 存储方案

| 字段 | 位置 | 用途 | 值规则 |
|------|------|------|--------|
| `ccode_hung` | ExpvstollHung | 主卡号(整单默认/结账预填) | 金额最大的那张卡号, 全现金则`''` |
| `otherserno_hung` | ExpenseHung | 各明细项的扣款卡号 | `''`=现金, `'K001'`=卡K001 |

### 各场景的数据示例

#### 场景1: 全现金
```
ccode_hung = ''
expense_hung:
  行1: ttype=S, s_mount=5000, otherserno_hung=''
  行2: ttype=G, s_mount=3000, otherserno_hung=''
```

#### 场景2: 全部同一张卡
```
ccode_hung = 'K001'
expense_hung:
  行1: ttype=S, s_mount=5000, otherserno_hung='K001'
  行2: ttype=G, s_mount=3000, otherserno_hung='K001'
```

#### 场景3: 卡+现金混合(卡余额不够)
```
卡余额¥2000, 服务¥5000用卡, 商品¥3000现金
ccode_hung = 'K001'  (主卡,按金额取)
expense_hung:
  行1: ttype=S, s_mount=5000, otherserno_hung='K001'
  行2: ttype=G, s_mount=3000, otherserno_hung=''
```

#### 场景4: 两张不同卡
```
ccode_hung = 'K001'  (金额较大的卡)
expense_hung:
  行1: ttype=S, s_mount=5000, otherserno_hung='K001'
  行2: ttype=G, s_mount=3000, otherserno_hung='K002'
```

#### 场景5: 售卡+用此卡消费
```
ccode_hung = 'K002'  (消费用的卡)
expense_hung:
  行1: ttype=C, srvcode=面诊卡, otherserno_hung=''       ← 售卡不涉及扣款
  行2: ttype=S, srvcode=服务A, s_mount=500, otherserno_hung='K002'  ← 用新卡付
```

### 结账时转换
```
expense_hung.otherserno_hung → expense.otherserno  (逐行复制)
toll: 按支付方式汇总
  - pcode='card', ccode='K001', totmount=5000
  - pcode='cash', ccode='',     totmount=3000
expvstoll:  ccode=主卡号

说明: toll 是整单级别的付款拆分, 不绑定到具体明细项
      逐行扣款信息存在 expense.otherserno, 供提成/报表按项目类型×付款方式统计
```

### 报表查询示例
```sql
-- 服务 - 现金收款
SELECT sum(s_mount) FROM expense WHERE ttype='S' AND (otherserno='' OR otherserno IS NULL)
-- 服务 - 卡收款
SELECT sum(s_mount) FROM expense WHERE ttype='S' AND otherserno != ''
-- 商品 - 现金收款
SELECT sum(s_mount) FROM expense WHERE ttype='G' AND (otherserno='' OR otherserno IS NULL)
-- 某张卡的扣款明细
SELECT * FROM expense WHERE otherserno='K001'
```

### 设计约束
- `ccode_hung` 是快照, 结账时可修改(最终以 toll 为准)
- `otherserno_hung` 不用于关账/对账, 仅用于提成和报表统计的辅助维度
- 已结账数据以 `toll` 表的付款记录为财务依据

---

## 付款拆分策略 (2026-07-16 终版)

### 核心逻辑
- 一次保存挂账 → 后端按 `card_ccode` 自动拆分 → 每组生成独立的 `ExpvstollHung` + `ExpenseHung`
- 储值卡同一组(现金归入缺口最大的), 计次卡独立成组, 全现金单独成组

### 分组算法

```python
def group_items_by_card(company, items):
    # 1. 查询所有涉及卡的类型(储值/计次)和余额
    # 2. 按 card_ccode 分组:
    #    - 无card → cash_items
    #    - comptype='times' → times_groups(每张计次卡独立)
    #    - 其他 → amount_groups(储值卡)
    # 3. 现金归入缺口最大的储值卡组(余额最不足的)
    # 4. 所有卡都够用时 → 现金独立成组
    # 5. 合并储值卡组和计次卡组返回
```

### 流水号设计
```
单组:  {company}{storecode}_hung_{serno}
多组:  {company}{storecode}_hung_{serno}-1
      {company}{storecode}_hung_{serno}-2 ...
```

### 完整场景矩阵

| # | 场景 | 挂账数 | 说明 |
|---|------|-------|------|
| 1 | 全现金 | **1** | `ccode_hung=''` |
| 2 | 全一张储值卡 | **1** | `ccode_hung='K001'` |
| 3 | 一张储值卡+现金 | **1** | 现金归入此卡组 |
| 4 | 多储值卡+现金 | **N个卡组** | 现金归入缺口最大的卡 |
| 5 | 全计次卡 | **N** | 每张独立 |
| 6 | 储值卡+计次卡+现金 | **N+1** | 计次卡独立，现金归入缺口最大储值卡 |
| 7 | 售卡+用卡消费 | 售卡归入对应组 | 消费用卡独立成组 |

### 后端改动
- `views.py` 新增 `group_items_by_card()` 辅助函数
- `save_hung_order()` 改为按分组循环创建挂账记录
- 返回值新增 `count`(组数) 和 `exptxsernos`(流水号数组)
- 新增导入: `from collections import defaultdict`
