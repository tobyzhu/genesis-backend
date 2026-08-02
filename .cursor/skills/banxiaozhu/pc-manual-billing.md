# PC 开单与收银（genesis_pc）知识

## 语义配色与主题（强制 · 全站）

- **范围**：`layouts` + `views` + `components` 全站生效（侧栏/顶栏/登录/业务页）；换主题应同步改变壳层、金额、提醒、Element 主色。
- Token：[`genesis_pc/src/styles/tokens.css`](../../../genesis_pc/src/styles/tokens.css)；切换逻辑：[`theme.ts`](../../../genesis_pc/src/styles/theme.ts)；工具类：`.g-money` / `.g-warning-box` / `.g-danger-box`（[`style.css`](../../../genesis_pc/src/style.css)）。
- 预设：`azure`（静海蓝）/ `salon`（雾玫瑰）/ `moss`（松烟绿）；`localStorage` 键 `genesis_pc_theme`；顶栏「配色」下拉（`MainLayout`）+ `appStore.setTheme`；壳层含 `--g-color-sidebar*`、`--g-color-auth-grad-*`。色板偏低饱和、金额用沉稳金属色、提醒用浅底琥珀，避免高饱和霓虹。
- **角色拆分**：金额 `--g-color-money*`；知情提醒 `--g-color-warning*`；须处理 `--g-color-danger*`；主操作/选中 `--g-color-primary*`。禁止金额与提醒共用同一色。
- **新 UI / 改样式**：业务色只写 `var(--g-*)`，禁止新增业务相关裸十六进制。
- **验收**：`rg '#e6a23c|#409eff|#f56c6c' src/views src/components src/layouts`（排除 `* 2.*`、打印 `document.write`、`tokens.css`）应为空；三主题下侧栏与主按钮同步变化。
- **除外**：打印小票 `document.write` HTML、macOS 重复文件 `* 2.*`。

## 入口与页面

| 菜单 | 路由 | 页面 | 职责 |
|------|------|------|------|
| 开单 → 手工开单 | `/adviser/billing-v2` | `genesis_pc/src/views/adviser/BillingPageV2.vue` | 手工开单、售卡、充值、活动、退款 |
| 开单 → 开单管理 | `/adviser/hungs` | `genesis_pc/src/views/adviser/HungOrdersPage.vue` | 挂单列表/明细、结账弹窗、作废、消费单 |
| 收银 → 收银结账 | `/cashier/checkout` | `genesis_pc/src/views/cashier/CheckoutPage.vue` | 审核结账（队列、明细编辑、付款拆分） |
| 收银 → 修改单据 | `/cashier/modify` | `genesis_pc/src/views/cashier/ModifyPage.vue` | 修改已结账单据的员工/付款方式 |
| 收银 → 作废单据 | `/cashier/void` | `genesis_pc/src/views/cashier/VoidPage.vue` | 占位页；实际作废在开单管理/手工开单 |
| 收银 → 交班日结 | `/cashier/shift` | `genesis_pc/src/views/cashier/ShiftPage.vue` | 交班、日结、付款报表、日结历史 |

- 业务引擎：`genesis_pc/src/composables/useBillingEngine.ts`（纯响应式状态，可单测）
- 付款分配补充：`.cursor/skills/banxiaozhu/billing-flow.md`
- 旧页面勿作开发基础：`BillingPage.vue`（路由已重定向到 v2）、`CashierPage.vue`（未挂路由）

## 开单主流程（硬性顺序）

1. 先搜索并确定会员（`searchVip` / `selectVip`）。**未选会员禁止添加任何品项**，引擎统一走 `requireVip()`，提示“请先选择会员”。
2. 可选：选择付款卡（`selectCard`），成为新明细行默认付款方式；计次卡自动带出关联项目。
3. 选品项：服务/商品/售卡/充值/活动。每次新增只对新行定价。
4. 明细行可改：属性（正常/赠送）、折扣率、金额折扣、扣款方式（现金/卡/储值卡余额）、开单员工、美疗师1/2、**是否指定美疗师1**（`secoldcustflag` / `secoldcustflag_hung`，Y/N；结账复制到 `expense.secoldcustflag`）。收银结账页可查看并修改后随 `update_hung_items_audit` 落库。
5. 保存挂账：`saveHung` → `POST /adviser/save_hung/` → `expvstoll_hung` + `expense_hung`。
6. 审核结账：收银台审核弹窗 → `POST /cashier/batch_checkout/`。

## 员工角色标题（appoption）

开单明细/开单管理里三位员工字段的**列标题与 placeholder** 必须来自公司字典，禁止写死「开单/美疗师」：

| 字段 | Appoption | 含义 |
|------|-----------|------|
| `pmcode` | `seg='common'`, `itemname='pmname'` → `itemvalues` | 第一位员工标题 |
| `asscode1` | `seg='common'`, `itemname='secname'` → `itemvalues` | 第二位员工标题 |
| `asscode2` | `seg='common'`, `itemname='thrname'` → `itemvalues` | 第三位员工标题 |

- 接口：`GET /baseinfo/get_appoption_byseg/?company=&seg=common`（PC 封装：`getAppoptionBySeg('common')`，`genesis_pc/src/api/vip.ts`）
- 缺省回退：`开单` / `美疗师1` / `美疗师2`
- 参考实现：`HungOrdersPage.vue` 的 `empTitles` + `loadEmpTitles()`、`CheckoutPage.vue` 的 `empTitles` + `loadEmpTitles()`
- 手工开单页、收银审核页若展示三位员工标题，同样遵循此规则

## 储值卡定价规则（关键）

- 定价触发：选卡、新增行、该行改付款方式。
- 接口 `POST /adviser/card-pricing/`：入参 `{cardtypeuuid 或 ccode, items:[{code,ttype,price,qty,discountclass,topcode}]}`；返回 `results` 含 `allowed / price / discounttype(DISC|PRICE) / disc / reason / source`。
- `card-pricing` 返回 `discounttype`：
  - `DISC`：只把该行 `secdisc = disc`，**单价不变**；金额折扣 `srvmondisc` 保留；小计 = 数量 × 单价 × 折扣率 − 金额折扣。
  - `PRICE` / 逻辑卡阶梯价：直接改 `price`，`secdisc = 1`，`srvmondisc = 0`。
  - 不可消费：`allowed = false` + `reason`，前端保存时拦截，后端 `save_hung` 与 `batch_checkout` 同样拦截。
- **按行定价**：只对“该行付款方式就是这张卡”的行询价/赋值；新增行只算新行；改付款方式只重算该行（先恢复原价/原折扣率，再按新卡算）；切回现金/储值卡余额只恢复，不调定价。
- 手动改过折扣率的行，之后若该行付款方式再变更，会被卡规则值覆盖。
- 选择卡片本身不触发全明细重算，只作为新行默认付款方式。

## 活动 / 售卡 / 充值 / 退款（手工开单）

- 活动 `mainttype`：`10`=特价（用 `promotionsprice` 改价）、`20`=特殊折扣（改 `secdisc`）、`30`=组合销售（套餐 `group_items`）。
- 同一张挂单只允许一个活动：加入不同活动项目会清空现有明细；后端 `save_hung` 也校验 `promotionsid` 数量 ≤ 1。
- 售卡 `ttype=C`：储值卡直接加行；疗程卡弹价格选择器（`GET /adviser/cardtype_prices/`，数量×单价）；保存挂账时后端创建 `Cardinfo status=P`，结账时激活为 `O`，作废时置 `C`。
- 充值 `ttype=I`：对会员名下储值卡输入金额；退款模式可对储值卡退金额、计次卡退次数，生成负数量行。
- 退款/作废入篮：勾选已结账订单明细（`GET /cashier/get_checkedout_orders/`）或未结挂单明细（`get_hung_byvipuuid` + `get_hung_detail`），转为 `qty<0` 行，与正常行一起保存挂账。

## 挂单状态机（psstatus）

| 状态 | 含义 | 说明 |
|------|------|------|
| `10` | 开单 | 新建挂单默认状态 |
| `20` | 到店 | 未结 |
| `30` | 配料 | 未结 |
| `40` | 服务完成 | 未结 |
| `50` | 可结账 | 未结 |
| `60` | 挂账 | 未结 |
| `70` | 已结账 | 结账终态 |

- 未结集合 `(10,20,30,40,50,60)`；作废不改变 `psstatus`，而是 `valiflag_hung='N'`（列表用 `psstatus=__void__` 查询）。
- 前端映射：`HungOrdersPage.vue` 的 `PSSTATUS_MAP`。

## 开单管理（HungOrdersPage）

- 列表：`GET /adviser/get_hung_list/`，参数 `company/storecode/psstatus/vipuuid/vsdate_from/vsdate_to/hdsysuserid`；默认只显示未结；`checkout_mode=1` 时按会员返回未结单供结账弹窗使用。
- 明细：`GET /adviser/get_hung_detail/?hunguuid=`，返回 `ditem/ttype/srvcode/itemname/price/qty/mount/stype/pmcode/asscode1/asscode2/paycardno`。
- 员工修改：`POST /adviser/update_hung_item_employees/`（`hunguuid+ditem+pmcode/asscode1/asscode2`）。
- 结账前批量修改：`POST /adviser/update_hung_items_audit/`，可改 `secdisc`（0~1）、`stype`（正常/赠送）、三位员工、`mondisc>=0`；后端逐行重算 `s_mount = qty × price × secdisc − mondisc`（2 位小数）并汇总 `totmount`。
- 作废：`POST /adviser/void_hung_order/` → `valiflag_hung='N'`；若单内售卡已生成 `Cardinfo(status=P)`，同步置 `status=C`。
- 消费单：`GET /cashier/get_receipt/?hunguuid=`，按会员+同 `vsdate` 聚合全部已结账单，返回明细、付款方式、员工姓名。

## 审核结账（CheckoutPage）

- 队列按开单日期分组、同日内金额降序；日期筛选默认“全部”，避免昨日遗留单被“今天”筛选挡住。
- 审核金额以选中订单明细合计为准：`Σ(price × qty × secdisc − mondisc)`，统一 2 位小数；文案“剩余应补”。
- 预警分级：`auditIssues`（须处理，阻断结账）vs `auditNotices`（已自动改现金，不阻断）。
- `auditIssues`：缺员工、遗留单、付款卡余额不足、拆分仍引用未生效卡。
- `auditNotices` / 单据头 / 付款区：始终展示开单 `paycode`；未生效打 tag「未生效」，灰色「原卡·不可用」chip + 黄底说明「已改用现金」；首次进入会员详情 `ElMessage.warning`。
- 左侧队列：挂单 `paycard_status=P` 时显示「卡未生效」。
- 付款卡选项只展示已生效卡（`status=O`）；未生效卡不进可扣款拆分，默认现金可结。
- 结账前可编辑明细：`secdisc/stype/员工/mondisc` → 先 `update_hung_items_audit` 再 `batch_checkout`。
- 收银员：默认 `appStore.cashierCode || ecode`，可搜索 `GET /adviser/search_user/` 选择并写入 localStorage（`genesis_pc_cashier_code/name`）。
- 快捷结账：`status=O` 才扣卡，否则改现金并警告（不整单阻断）。

## 客户结账汇总（HungOrdersPage 内）

- `GET /cashier/customer_checkout/`：按会员汇总未结挂单：`times_cards`（计次卡，`deduct_qty`）、`auto_cards`（储值卡，`deduct_amount`）、`gift`（`stype=P` 赠送）、`pending`（待付）。
- 付款分配交互：初始一行默认现金 `amount=待付`；改付款方式只取消 `_default` 标记；改金额超付警告并截断、少付补默认行或自动新增；添加付款方式填入剩余金额；移除后调平。
- `POST /cashier/customer_checkout_confirm/`：逐单结账后，按各单金额占比把 `payments` 分摊写入 `Toll`。

## 付款拆分与 Toll 数据

- `Paymode.iscash`：`0`=卡付类、`1`=现金类、`2`=赠送类；`GET /cashier/payment_methods/` 返回 `paymodes` + `defaults.normal_pcode / send_pcode`。
- `Toll`：`pcode`=付款方式编码、`ccode`=付款卡号、`totmount`=金额（计次卡为次数）、`qty`=付款次数。
- `Expense.otherserno`：明细扣款卡号，报表/提成按 项目类型 × 付款方式 统计。
- 初始化拆分：`paycode` 卡先扣 `min(合计, 卡余额)`，剩余补默认现金行；卡拆分不可超过 `leftmoney`。
- 配平规则：超付从最后一个非默认行截断；少付优先调大默认行，无默认行时自动新增默认付款行。

## 修改单据（ModifyPage）

- 列表查已结账单：`GET /adviser/get_hung_list/?psstatus=70` + 日期范围。
- 单笔付款：`GET /cashier/get_order_payment/?exptxserno=`。
- 保存：`POST /cashier/update_checkedout/`，可改明细员工（`pmcode/asscode1/asscode2`）与付款方式（`payments:[{old_pcode,new_pcode,amount}]`）；前端只允许在同 `iscash` 类别内切换付款方式。

## 交班日结（ShiftPage）

- 交班：`POST /cashier/shift_handover/`，对未日结单据生成班次号（`Expvstoll.times = 当前 max + 1`），返回 `payment_summary/details`；可传 `actuals` + `record_only=true` 记录盘点差异。
- 日结：`GET/POST /cashier/daily_settlement/`，`preview=1` 预览最早未日结 `vsdate`；POST 执行时把该日单据写 `cdate`，返回 `shift_summary`（按班次）+ `payment_summary`。
- 付款报表：`GET /cashier/payment_report/`，按 `date_from/date_to` 汇总各付款方式订单明细。
- 日结历史：`GET /cashier/settlement_history/`、`GET /cashier/settlement_detail/?cdate=`。

## 后端校验（save_hung_order / batch_checkout）

- 会员必须属于当前公司（`_validate_hung_items`）。
- 开单保存：付款卡必须存在、状态 `O/P`、属于该会员；项目必须通过 `resolve_card_item_price` 权限校验；计次卡余次足够。
- 折扣率 0~1、金额折扣 ≥ 0、单价 ≥ 0。
- 分组规则（`group_items_by_card`）：S/G 按付款卡分组——储值卡同组、现金行独立成组（`__cash__`）、计次卡每张独立成组；售卡（C）每张独立成组（`__C_i__`）、充值（I）每笔独立成组（`__I_i__`）。
- 每组生成一张 `ExpvstollHung`：`ccode_hung`=组卡号、`totmount`=组内合计、`psstatus=10`；多组时 `exptxserno` 加 `-1/-2` 后缀。
- 结账：`_validate_paycards_active` 要求实际付款卡 `status=O`（挂账卡 `P` / 非 `O` 一律禁止并提示）；有 `splits` 时只校验拆分卡号，无拆分时校验抬头卡 + 明细 `otherserno`。
- 结账前 `_validate_hung_checkout_permission` 再校验已生效卡的消费权限，禁止时明确报错而非静默转现金。
- `batch_checkout`：`cashier` 必填；`splits[uuid] = [{pcode, ccode, amount}]` 创建多条 `Toll`；卡付扣 `leftmoney`/`leftqty`；售卡产生的卡片 `status P→O`；挂单置 `70`。

## 关键接口

| 接口 | 方法 | 作用 |
|------|------|------|
| `/adviser/save_hung/` | POST | 保存挂账单（按卡分组，售卡建卡） |
| `/adviser/card-pricing/` | POST | 卡支付单价/折扣率/权限 |
| `/adviser/get_hung_list/` | GET | 挂单列表（含明细、`paycode`、`paycard_status` O/P，收银台/开单管理用） |
| `/adviser/get_hung_byvipuuid/` | GET | 会员未完成挂单 |
| `/adviser/get_hung_detail/` | GET | 挂单明细 |
| `/adviser/update_hung_item_employees/` | POST | 修改挂单明细员工 |
| `/adviser/update_hung_items_audit/` | POST | 结账前批量改折扣/赠送/员工并重算金额 |
| `/adviser/void_hung_order/` | POST | 作废挂单（售卡卡片 P→C） |
| `/adviser/active_promotions/` | GET | 活动列表/明细 |
| `/adviser/categorized_items/` | GET | 分类树 + 可售项目 |
| `/adviser/cardtype_prices/` | GET | 卡类疗程价格选项 |
| `/adviser/get_vip_cardlist/` | GET | 会员卡列表（余额/余次） |
| `/adviser/get_bookingable_empllist/` | GET | 可预约员工列表 |
| `/cashier/batch_checkout/` | POST | 批量结账（付款拆分） |
| `/cashier/customer_checkout/` | GET | 客户结账汇总 |
| `/cashier/customer_checkout_confirm/` | POST | 客户级结账确认 |
| `/cashier/payment_methods/` | GET | 付款方式 + 默认编码 |
| `/cashier/get_receipt/` | GET | 消费单数据 |
| `/cashier/get_checkedout_orders/` | GET | 会员已结账订单（退款用） |
| `/cashier/update_checkedout/` | POST | 修改已结账单据 |
| `/cashier/get_order_payment/` | GET | 已结账单付款方式 |
| `/cashier/shift_handover/` | POST | 交班 |
| `/cashier/daily_settlement/` | GET/POST | 日结预览/执行 |
| `/cashier/payment_report/` | GET | 付款方式报表 |
| `/cashier/settlement_history/` | GET | 日结历史日期 |
| `/cashier/settlement_detail/` | GET | 日结明细 |

## 测试

- 前端：`genesis_pc/src/utils/__tests__/engine.test.ts`（vitest；覆盖会员前置、按行定价、活动分组、退款/作废、数量查询、save_hung payload）
- 后端：
  - `adviser/tests_save_hung_validation.py`（save_hung 校验/分组）
  - `adviser/tests_hung_list_perf.py`（挂单列表性能）
  - `adviser/tests_update_hung_items_audit.py`（结账前批量修改/重算）
  - `cashier/tests_batch_checkout.py`（结账拆分/扣卡）
- 运行：
  - `cd genesis_pc && ./node_modules/.bin/vitest run src/utils/__tests__/engine.test.ts`
  - `cd genesis_backend && GENESIS_USE_TEST_DB=1 .venv/bin/python -m pytest adviser/tests_save_hung_validation.py adviser/tests_hung_list_perf.py adviser/tests_update_hung_items_audit.py cashier/tests_batch_checkout.py -q`
