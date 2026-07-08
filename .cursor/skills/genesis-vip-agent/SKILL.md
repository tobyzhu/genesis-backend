---
name: genesis-vip-agent
description: >-
  Genesis 美业 ERP 客户管理（VIP）专用 AI 助手：会员档案、消费记录、卡项、CRM 案例与回访。
  在 genesis_backend/assistant 中扩展 vip_crm profile、vip_tools 或客户相关 API 时使用。
---

# Genesis 客户管理 AI 助手（vip_crm）

## 概述

Genesis 中 **VIP = 会员/客户**，数据存储在 MySQL `vip` 表（模型 `baseinfo.models.Vip`）。  
客户管理专用助手 profile id 为 **`vip_crm`**，与 LLM 提供方（`deepseek` / `cursor`）分离。

| 概念 | 说明 |
|------|------|
| `agent_id` | LLM 提供方（`assistant/agents.py`） |
| `profile_id` | 业务助手类型（`assistant/agent_profiles.py`） |
| `vipuuid` | 客户主键 |
| `vcode` | 会员号 |
| `viptype` | `10`=会员，`20`=散客 |

## 关键文件

```
genesis_backend/assistant/
├── agent_profiles.py    # 助手 profile 注册（general / vip_crm）
├── vip_tools.py         # VIP 专用只读工具
├── data_tools.py        # 通用工具与 run_tool_plan
├── agents.py            # LLM 提供方配置
├── views.py             # /assistant/api/chat/ 对话入口
└── skills/vip-crm/      # 本 skill 的运行时说明副本
```

## vip_crm 可用工具

| 工具名 | 用途 |
|--------|------|
| `search_vips` | 按姓名/手机/会员号模糊搜索 |
| `get_vip_detail` | 会员档案详情 |
| `vip_sleeping_alert` | 沉睡会员预警（可筛顾问/会员类型） |
| `list_vip_cards` | 会员卡列表 |
| `list_vip_transactions` | 消费/成交记录 |
| `vip_consumption_summary` | 消费汇总 |
| `list_vip_crm_cases` | CRM 服务案例 |
| `list_vip_communications` | 沟通/回访记录 |
| `vip_maintenance_summary` | 门店会员维护统计 |
| `vip_profile` | 客户画像（消费、频次、偏好项目、末次到店） |
| `vip_churn_risk` | 单客流失风险（未到店天数、消费趋势） |
| `list_employees` | 解析顾问/美疗师姓名 |
| `describe_table` / `readonly_sql` | 高级只读查询 |

## 扩展新工具

1. 在 `vip_tools.py` 实现 `tool_*` 函数（只读、限定 `company` + `storecode`、结果有上限）。
2. 注册到 `VIP_ONLY_REGISTRY` 并更新 `VIP_ONLY_CATALOG_TEXT`。
3. 若需加入 vip_crm 子集，在 `agent_profiles.py` 的 `_VIP_SHARED_TOOL_NAMES` 或 `VIP_ONLY_REGISTRY` 中登记。
4. 勿在助手层实现写操作；会员 CRUD 走 `baseinfo/views.py`、`crm/views.py`。
5. 新工具须加 `assistant/tests/test_<tool>.py` 或扩展现有用例；跑 `GENESIS_USE_TEST_DB=1 pytest assistant/tests`。

## 测试

```bash
bash scripts/setup-test-db.sh   # 首次：克隆 test_<DB_NAME> 表结构
cd genesis_backend && GENESIS_USE_TEST_DB=1 .venv/bin/pytest assistant/tests -q
bash scripts/test-all.sh        # 含 banxiaozhu Jest
```

主要用例文件：

| 文件 | 覆盖 |
|------|------|
| `test_vip_profile.py` / `test_vip_churn_risk.py` | 客户画像、流失风险 |
| `test_search_vips.py` / `test_readonly_sql_tool.py` | 会员搜索、只读 SQL |
| `test_table_catalog.py` | `list_table_catalog` / `describe_table` |
| `test_assistant_api.py` | 沉睡预警、chat、导出 API |

CI：`.github/workflows/tests.yml`；Secrets 说明见 [`scripts/CI.md`](../../scripts/CI.md)。

## 沉睡会员预警

工具 `vip_sleeping_alert` 口径：**超过 N 天无 `valiflag=Y` 有效消费**。

| 字段 | 说明 |
|------|------|
| `risk_level` | `warning` / `critical` / `never_visited` |
| `days_since_last_visit` | 距末次消费天数 |
| `inactive_days` | 预警阈值（默认 90） |
| `critical_days` | 严重阈值（默认 180） |

直接 API（不经过 LLM）：

```http
POST /assistant/api/vip/sleeping-alert/
{"company":"demo","storecode":"88","inactive_days":90,"critical_days":180,"limit":200}
```

## 批量导出

```http
POST /assistant/api/vip/batch-export/
{"export_type":"sleeping_vips","company":"demo","storecode":"88","inactive_days":90,"limit":5000}
```

`export_type` 还支持 `store_vips`（导出门店全部会员，最多 5000 行）。

助手页「沉睡会员预警」面板提供：查询预警、导出 Excel、导出全部会员。

## 开单 / 结账表

| 状态 | 物理表 |
|------|--------|
| 未结账（挂单） | `expvstoll_hung`、`expense_hung` |
| 已结账（正式成交） | `expvstoll`、`expense`、`toll` |

`psstatus` / `psstatus_hung` 表示服务/配料流程节点，**不能**单独用来判断是否已结账。

## readonly_sql 表名

- 使用 **MySQL 物理表名**（`list_table_catalog` 的 `db_table`）
- 正确：`expvstoll`、`vip`、`toll`
- 错误：`cashier.expvstoll`、`baseinfo.vip`
- 系统会对 `FROM/JOIN` 中的 `app.表名` 自动改写为物理表名

```http
POST /assistant/api/chat/
{
  "message": "查一下张三最近的消费",
  "agent": "deepseek",
  "profile": "vip_crm",
  "company": "demo",
  "storecode": "88"
}
```

## 典型查询流程

1. `search_vips` → 获取 `vipuuid`
2. `get_vip_detail` → 档案
3. `list_vip_transactions` / `vip_consumption_summary` → 消费
4. `list_vip_crm_cases` + `list_vip_communications` → 回访
5. 问「这个客户怎么样」→ `vip_profile` + `vip_churn_risk`（可只传 `telph`）

## 相关数据模型

- `baseinfo.models.Vip` — 会员主档
- `adviser.models.Cardinfo` — 卡项
- `cashier.models.Expvstoll` — 成交主表（`valiflag='Y'` 为有效）
- `crm.models.CrmCase` / `VipCaseDetail` — 案例与沟通

## 迁移

新增 `profile_id` 字段后执行：

```bash
cd genesis_backend && python manage.py migrate assistant
```

## 测试问题示例

- 「门店本月新增了多少会员？」
- 「帮我查手机 138 开头的会员」
- 「会员号 V001 有哪些卡？余额多少？」
- 「张三上次消费是什么时候？总共消费多少？」
- 「138xxxx 这个客户怎么样？」
- 「这个客户有没有流失风险？」

## 相关 Skill

**微信小程序端**（帮小主 UI、wx.request、开单结账页面）见 [`banxiaozhu`](../banxiaozhu/SKILL.md)。本 skill 仅覆盖 `genesis_backend/assistant` 后端 AI 助手与只读 VIP 工具。
