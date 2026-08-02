# PC 营销活动 / 活动设定（genesis_pc）

## 概述

活动设定供手工开单的活动选择使用，活动分三类：特价（`10`）、特殊折扣（`20`）、组合销售（`30`）。
特价/折扣活动通过「活动分组 + 分组明细」主从结构配置；组合销售直接用活动明细。

## 数据模型（baseinfo）

| 表 | 模型 | 说明 |
|----|------|------|
| `promotions` | `Promotions` | 活动主表：`promotionsid` / `promotionsname` / `mainttype` / `promotionsstatus` / `fromdate` / `todate` / `s_price` / `disc` / `mainpgroupid` |
| `promotionsdetail` | `Promotionsdetail` | 活动明细：按 `promotionsuuid` / `promotionsid` 关联活动（组合销售用） |
| `promotionsgroup` | `Promotionsgroup` | 活动分组主表：`pgroupid` 唯一 + `pgroupname` / `pgrouptype` / `fromdate` / `todate` / `status` |
| `promotionsgroupdetail` | `Promotionsgroupdetail` | 分组明细：`pgroupuuid` / `pgroupid` 关联分组 |

## 关联关系（关键）

- `promotions.mainpgroupid` → `promotionsgroup.pgroupid`，**仅在特价（10）/ 特殊折扣（20）生效**。
- `promotionsgroup.pgroupid` ↔ `promotionsgroupdetail.pgroupid`，主从关系。
- `pgrouptype`：`BUY` = 适用于“购买”的内容，`SEND` = 适用于“赠送”的内容。
- 开单读取（`active_promotions`）：
  - 10/20：按 `mainpgroupid` 查 `Promotionsgroupdetail`。
  - 30：按 `promotionsid` / `promotionsuuid` 查 `Promotionsdetail`。

## 活动大类

| `mainttype` | 名称 | 明细载体 | 定价字段 |
|------------|------|----------|----------|
| `10` | 特价活动 | 活动分组主从 | `price1` / `amount1` |
| `20` | 特殊折扣活动 | 活动分组主从 | 头部 `disc` + `price1` |
| `30` | 组合销售活动 | 活动明细 | `promotionsprice` / `promotionsamount` |

## 前端

- 入口：基础资料 → 营销活动，`/campaign` → `genesis_pc/src/views/campaign/CampaignPage.vue`。
- 列表：服务端分页 + 筛选（`mainttype` / `promotionsstatus` / `search`），不再全量拉取。
- 编辑：10/20 显示「活动分组 + 分组明细」主从编辑区；30 显示活动明细表。
- 分组类型：下拉 `购买(BUY)` / `赠送(SEND)`，新建默认 `BUY`，后端强制校验。
- 项目下拉：售卡显示「卡类名称（卡类编号）」，编号缺失时按编号回查名称。
- 保存：`POST /adviser/save_promotion_setup/`（原子提交，替代逐条通用 CRUD）。
- 回显：`GET /adviser/get_promotion_setup/?uuid=`。

## 后端接口

| 接口 | 方法 | 作用 |
|------|------|------|
| `/adviser/save_promotion_setup/` | POST | 原子保存活动头部 + 分组主从 / 明细 |
| `/adviser/get_promotion_setup/` | GET | 返回活动完整配置（头部 + 明细 + 分组主从） |
| `/adviser/active_promotions/` | GET | 开单/小程序读取有效活动 |
| `/adviser/sysadmin-data/baseinfo.promotions/` | GET/POST/PUT/DELETE | 通用 CRUD |
| `/adviser/sysadmin-data/baseinfo.promotionsgroup/` | GET/POST/PUT/DELETE | 通用 CRUD |
| `/adviser/sysadmin-data/baseinfo.promotionsgroupdetail/` | GET/POST/PUT/DELETE | 通用 CRUD |

## 保存规则（save_promotion_setup）

- 10/20：`group` 必填；`pgroupid` 必填；`pgrouptype ∈ {BUY, SEND}`；至少一条分组明细；重建分组明细（旧行 `flag=N`），并清空该活动 `Promotionsdetail`。
- 30：`items` 至少一条；重建 `Promotionsdetail`；`mainpgroupid` 置空。
- 全程 `transaction.atomic()`；校验失败返回 `ok=false + message`。

## 通用 CRUD 注意

- sysadmin 注册路径是 `baseinfo`（模型定义在 baseinfo app），不是 `adviser`。
- 列表接口自动 `select_related` 外键，图片字段（ImageField/FileField）输出字符串，避免 N+1 和 JSON 序列化 500。
- 外键用 UUID 字符串提交时，通用接口自动解析为模型实例。

## 测试

- `genesis_backend/adviser/tests_promotion_setup.py`：分组主从保存/重建/回显/校验、BUY/SEND。
- `genesis_backend/sysadmin/tests_promotions_api.py`：活动通用 CRUD + 外键字符串。
- `genesis_backend/sysadmin/tests_model_data.py`：商品图片字段序列化回归。
- 运行：
  ```bash
  cd genesis_backend && GENESIS_USE_TEST_DB=1 .venv/bin/python -m pytest \
    adviser/tests_promotion_setup.py sysadmin/tests_promotions_api.py sysadmin/tests_model_data.py -q
  ```
