# 卡类管理（Genesis PC / banxiaozhu 兼容）

## 概述

卡类管理覆盖 Genesis PC 和 banxiaozhu（微信小程序）两端的卡消费逻辑。新代码（PC）使用“折扣分类规则”表定价；老代码（banxiaozhu / 旧结账）继续使用“服务大类折扣”表 `Cardvsdi`。两套规则由同步命令镜像，互不影响。

核心文件：
- 模型：`genesis_backend/baseinfo/models.py`
- 规则与定价：`genesis_backend/baseinfo/card_rules.py`
- 同步命令：`genesis_backend/baseinfo/management/commands/sync_card_discount_rules.py`
- PC 页面：`genesis_pc/src/views/sysadmin/CardtypeAdminPage.vue`

## 四种卡类模式

| 模式 | 字段 | 说明 |
|------|------|------|
| 计次卡 | `comptype='times'` + `ttype(S/G)` + `sguuid` | 绑定项目，扣 `leftqty` |
| 计费卡 | `comptype='amount'` | 储值消费，按折扣分类规则打折/固定价 |
| 逻辑卡 | `comptype='amount'` + `ruler` | 绑定单一项目，按自然月到店次数取阶梯价 |
| 时效卡 | `comptype='period'` + 绑定项目 | 有效期内不限次数，只校验有效期 |

## banxiaozhu 兼容原则

- banxiaozhu 依赖 `/adviser/` 旧端点，消费扣款继续走 `Cardvsdi`（按服务大类）。
- 新增的 `ruler-list/save/delete`、`cardtype-discount-list/save`、`card-pricing` 都在 `/adviser/` 下，独立于旧端点。
- 同步命令把 `Cardvsdi` 镜像到 `CardtypeVsDiscountClass`，老代码数据不迁移、不破坏。
- `Cardvsdi.flag` 旧语义是“可否消费”，已改为 `consume_flag`；老数据一次性迁移：`consume_flag=旧flag`、`flag='Y'`。

## 规则与定价优先级

`Ruler 阶梯价 > consume_flag 权限 > 折扣分类规则 > 服务大类兼容（过渡期）> 原价`

折扣分类字典按 `ttype` 分开：`srvdiscountclass`（服务）、`goodsdiscountclass`（商品）、`discountclass`（通用）；卡大类（Cardsupertype）同步到通用 `discountclass` 供 ttype=C 使用。

## 同步与生产迁移

`sync_card_discount_rules`：幂等补 schema → 大类写折扣分类字典 → 项目 `discountclass` 空值回填 → `Cardvsdi` 镜像新规则。

注意：空编码/空名称的大类跳过；大批量用 `bulk_create/bulk_update`，不要逐行 `update_or_create`。生产执行前先备份，执行后对账再灰度。
