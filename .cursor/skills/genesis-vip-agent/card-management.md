# 卡类管理（卡类 / 折扣设定）

## 概述

卡类管理把会员卡分成四种消费模式，统一由“卡类 + 规则”驱动定价和消费权限。PC 新代码只读新的折扣分类规则表，老代码（banxiaozhu / 旧结账）继续读旧的服务大类折扣表，两套数据通过同步命令保持镜像。

核心文件：
- 模型：`genesis_backend/baseinfo/models.py`（Cardtype、Cardvsdi、CardtypeVsDiscountClass、Ruler）
- 规则与定价：`genesis_backend/baseinfo/card_rules.py`
- API：`genesis_backend/adviser/views.py`（ruler / cardtype-discount / card-pricing）
- 同步命令：`genesis_backend/baseinfo/management/commands/sync_card_discount_rules.py`
- 前端：`genesis_pc/src/views/sysadmin/CardtypeAdminPage.vue`，路由 `/sysadmin/cardtype`
- 前端 API：`genesis_pc/src/api/card-admin.ts`

## 卡类四种模式

| 模式 | 字段 | 核心逻辑 |
|------|------|---------|
| 计次卡 | `comptype='times'` + `ttype(S/G)` + `sguuid` | 绑定具体服务/商品，卡类编号默认=项目编号；结账扣 `leftqty` |
| 计费卡 | `comptype='amount'` | 储值消费；按折扣分类规则打折或固定价；`consume_flag='N'` 的项目不可用此卡 |
| 逻辑卡 | `comptype='amount'` + `ruler` | 计费卡特例；绑定单一项目；按自然月到店次数取 Ruler 阶梯价（如第1次1260/第2次960/之后720） |
| 时效卡 | `comptype='period'` + 绑定项目 | 一般限定服务项目；按 `validays` 计算 `valdate`；有效期内不限次数/金额，结账只校验有效期和绑定项目 |

## 折扣与权限规则

- 新规则表 `CardtypeVsDiscountClass`：`(卡类, ttype, discountclass) → discounttype(DISC/PRICE) + disc/price + consume_flag + emplguideperc`，PC 新代码只读它。
- 旧表 `Cardvsdi`：按服务大类 `topcode` 的折扣，保留给老代码读取；不再在界面维护。
- 折扣分类字典按 `ttype` 分开：`srvdiscountclass`（服务大类同步）、`goodsdiscountclass`（商品大类同步）、`discountclass`（通用）；项目按自己类型读对应字典。
- `ttype=C`（卡）的折扣分类：卡大类（Cardsupertype）编号/名称同步到通用 `discountclass` 字典，卡类规则 ttype=C 使用它。
- 定价优先级：`Ruler 阶梯价 > consume_flag 权限 > 折扣分类规则 > 服务大类兼容（过渡期）> 原价`。
- `consume_flag` 表示“可否消费”，与 `flag`（软删除）语义分离；老 `Cardvsdi.flag='N'` 通过同步迁移为 `consume_flag='N'` 且 `flag='Y'`。

## 逻辑卡 Ruler

- `Ruler` 表：`rulername` + `ruler` 文本，`Cardtype.ruler` 外键选择规则。
- 规则格式：`#ttype=S#srvcode=105001#1sttimes=1260#2ndtimes=960#others=720#`，支持 `srvcode/gcode`、`1sttimes..Nthtimes`、`others`。
- 解析与取价：`parse_ruler()`、`ruler_lookup(parsed, usecount)` 在 `baseinfo/card_rules.py`。
- 自然月计数：`Cardinfo.logic_cycle_month + logic_usecount`，跨自然月重置；每笔结账 +1（到店次数口径）；作废/退款回退；可用流水重算对账。

## 结账四分支

- `amount`：按定价结果扣 `leftmoney`
- `times`：扣 `leftqty`
- `period`：只校验 `valdate` 和绑定项目，不扣
- `logic`：按阶梯价扣 `leftmoney`，计数 +1

## 数据同步与迁移

`sync_card_discount_rules`（management command）：
1. `ensure_card_rule_schema()` 幂等补列：`cardvsdi.consume_flag`、`cardinfo.logic_cycle_month/logic_usecount`；老 `flag` 一次性迁移到 `consume_flag`。
2. 服务/商品大类写入 `Appoption` 的 `srvdiscountclass/goodsdiscountclass`，并合并通用 `discountclass` 条目。
3. 服务项目 `discountclass` 为空时回填 `topcode`，商品回填 `goodsct`。
4. `Cardvsdi` 镜像为 `CardtypeVsDiscountClass` 行。

注意事项：
- 空 `topcode/ttname` 或空 `goodsct/goodsctname` 的大类必须跳过，避免 `Appoption.itemname` 非空约束报错。
- 大批量同步使用 `bulk_create/bulk_update` 和 SQL `update`，不要逐行 `update_or_create`。
- 生产迁移：先备份，低峰执行同一命令，跑对账（按卡类+ttype+大类对比数量与折扣值），再灰度切换新结算入口。

## 前端页面

`CardtypeAdminPage.vue` 编辑弹窗五个区：
- 基本信息：编号、名称、卡大类、消费模式、面值、可用金额、有效期。
- 关联项目：计次/时效/逻辑卡选择 `ttype(S/G)` + 服务/商品项目（`sguuid`）；计次卡自动把编号填为项目编号。
- 逻辑规则：选择 `Ruler` 并可新建规则，展示规则文本解析预览。
- 折扣设定：按折扣分类维护规则行（折扣率/固定价/可否消费），批量保存到新规则表。
- 控制设定：可销售、有效开关。

折扣分类下拉需合并读取 `discountclass + srvdiscountclass + goodsdiscountclass` 三个 seg，否则服务/商品大类同步出的选项不会显示。

## 测试

- 后端：`genesis_backend/baseinfo/tests_card_rules.py`（Ruler 解析、自然月阶梯、折扣分类规则、consume_flag 禁止、服务大类兼容回退、时效/计次绑定、同步幂等、API）。
- 前端：`genesis_pc/src/api/__tests__/card-admin.test.ts`。
