# PC 前端收银结账 — 付款分配逻辑

> 完整 PC 开单/收银流程见 [pc-manual-billing.md](pc-manual-billing.md)；本文件只讲付款分配交互。

## 数据模型

| 表 | 字段 | 说明 |
|-----|------|------|
| `Toll` | `pcode` | 付款方式编码（Paymode.pcode，如 `'A'`=现金） |
| `Toll` | `ccode` | 付款卡号（如 `'0100361-0001'`） |
| `Toll` | `totmount` | 付款金额 |
| `Toll` | `qty` | 付款次数（疗程卡用） |
| `Expense` | `otherserno` | 关联卡号，用于追踪卡消费/充值 |
| `Expense` | `ttype` | 项目类型：`'S'`=服务, `'G'`=商品, `'C'`=售卡, `'I'`=充值 |
| `Paymode` | `iscash` | `'0'`=卡付类, `'1'`=现金类, `'2'`=赠送类 |

## 付款分配交互逻辑

```
初始: [默认付款方式(现金'A'), 金额=待付总额, _default: true]

改付款方式(select):
  └─ 仅取消 _default 标记，金额不变，不新增行

改金额(input-number):
  ├─ 超付(paid > total):
  │   └─ 警告"多付了"，截断超出部分
  ├─ 少付(paid < total):
  │   ├─ 有默认行(_default true) → 调整默认行金额补足
  │   └─ 无默认行 → 自动新增一行默认付款方式的付款记录(金额=差额)
  └─ 刚好 → 已平衡

添加付款方式(按钮):
  └─ 金额自动填入剩余待付金额，_default: false

移除付款方式(✕按钮):
  └─ 若只剩1行不可移除，否则移除后自动调平
```

## 关键函数（HungOrdersPage.vue / CheckoutPage.vue）

| 函数 | 作用 |
|------|------|
| `rebalancePayments()`（HungOrdersPage） | 客户结账核心调平：合计=待付，超付警告，少付补默认行或自动新增 |
| `custOnPmChange(idx)` | 改付款方式：取消默认标记，不新增行 |
| `custOnAmountChange()` | 金额改变：调用 rebalancePayments |
| `custAddPayment()` | 添加付款行：填入剩余金额 |
| `custRemovePayment(idx)` | 移除付款行：移除后调平 |
| `initAuditSplitsForOrder()`（CheckoutPage） | 审核结账初始化拆分：paycode 卡先扣余额，剩余补默认现金行 |
| `rebalanceAuditSplits(o)`（CheckoutPage） | 审核拆分配平：超付截断非默认行、少付调默认行/自动新增 |
| `addAuditSplit` / `removeAuditSplit`（CheckoutPage） | 审核拆分增删行 |
| `onAuditSplitAmountChange` / `onAuditSplitMethodChange`（CheckoutPage） | 金额上限（卡余额）与卡号联动 |
| `custPendingTotal` / `custPaidTotal` / `custRemaining` | computed：待付总额 / 已分配合计 / 剩余待分配 |

## 后端接口

| 接口 | 方法 | 作用 |
|------|------|------|
| `/adviser/payment_methods/` | GET | 返回付款方式列表 + 默认编码 |
| `/adviser/customer_checkout/` | GET | 客户结账汇总（待付金额按 stype 分类） |
| `/adviser/customer_checkout_confirm/` | POST | 客户结账确认 |
| `/adviser/batch_checkout/` | POST | 单笔结账 |
| `/adviser/get_receipt/` | GET | 获取消费单数据 |
