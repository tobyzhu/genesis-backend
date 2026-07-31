# VIP 客户生命周期 — Admin 配置与定时同步

按到店与消费趋势将会员分为 **活跃 / 流失预警 / 休眠 / 未消费新客**，并可自动回写 `vip.status`。

相关代码：`genesis_backend/assistant/vip_lifecycle.py`

---

## 一、业务口径

| 分级 | 代码 | 判定 |
|------|------|------|
| 活跃 | `active` | 休眠阈值内有有效消费（`valiflag=Y`） |
| 流失预警 | `at_risk` | 仍属活跃，但近一周期**消费或到店频次下降** |
| 休眠 | `sleeping` | ≥ 休眠天数无有效消费 |
| 未消费新客 | `never_visited` | 建档后尚未消费，且未超过休眠阈值 |

**休眠天数、趋势对比天数为公司级统一配置**，全部门店共用同一套参数。

---

## 二、Django Admin 配置（系统配置 / Appoption）

登录后台 → **基础信息 → 系统配置**（模型 `Appoption`）。

> 需先执行迁移 `python manage.py migrate baseinfo`，使「类别」下拉出现 **客户生命周期**（`vip_lifecycle`）。

### 2.1 生命周期阈值（seg = `vip_lifecycle`）

为**每个公司**新增 3 条记录（`company` 由当前登录公司自动带入）：

| 类别 (seg) | 编码 (itemname) | 名称 (itemvalues) | 说明 |
|------------|-----------------|-------------------|------|
| 客户生命周期 | `inactive_days` | `90` | 休眠阈值（天），30–3650 |
| 客户生命周期 | `critical_days` | `180` | 深度休眠参考（天），≥ inactive_days |
| 客户生命周期 | `trend_days` | `90` | 预警趋势对比周期（天），30–365 |

注意：`itemvalues` 填**纯数字**（天数），不是中文说明。

示例（公司 `yiren`）：

```
seg=vip_lifecycle  itemname=inactive_days   itemvalues=90
seg=vip_lifecycle  itemname=critical_days   itemvalues=180
seg=vip_lifecycle  itemname=trend_days      itemvalues=90
```

未配置时，依次回退：环境变量 → 默认值 90 / 180 / 90。

环境变量（`genesis_backend/.env`）：

```env
VIP_LIFECYCLE_INACTIVE_DAYS=90
VIP_LIFECYCLE_CRITICAL_DAYS=180
VIP_LIFECYCLE_TREND_DAYS=90
```

**优先级：Appoption > 环境变量 > 默认值。**

### 2.2 会员状态码（seg = `vipstatus`）

同步任务会把休眠客 `vip.status` 改为「休眠」码，恢复活跃客改为「活跃」码。

在 **系统配置** 中确认已有 `seg=vipstatus` 记录，且 **名称 (itemvalues)** 含关键字：

| 关键字 | 用途 | 默认编码 (itemname) |
|--------|------|---------------------|
| 活跃 | 正常在店客户 | `10` |
| 休眠 | 长期未到店 | `20` |
| 流失 | 深度流失（分级展示用） | `30` |

匹配规则：扫描本公司 `vipstatus`，`itemvalues` 文案**包含**「活跃」「休眠」「流失」即采用对应 `itemname` 作为状态码。

若本公司无配置，会回退到 `company=common` 的 `vipstatus`。

---

## 三、手动同步与查询

### 3.1 命令行同步 status

```bash
cd genesis_backend

# 预览（不写库）
.venv/bin/python manage.py sync_vip_lifecycle --company=yiren --dry-run

# 全公司所有门店
.venv/bin/python manage.py sync_vip_lifecycle --company=yiren

# 仅单店
.venv/bin/python manage.py sync_vip_lifecycle --company=yiren --storecode=01
```

### 3.2 Web 助手面板

`/assistant/` → profile **vip_crm** → **客户生命周期** 面板：

- 查询分级列表
- 导出 Excel
- **同步 vip.status**（等同命令行非 dry-run）

### 3.3 API

```http
POST /assistant/api/vip/lifecycle/
{"company":"yiren","storecode":"01","segment":"at_risk","limit":200}

POST /assistant/api/vip/lifecycle/sync/
{"company":"yiren","storecode":"","dry_run":false}

POST /assistant/api/vip/lifecycle/snapshot/
{"company":"yiren","storecode":""}

GET /assistant/api/vip/lifecycle/migrations/?company=yiren&storecode=01&days_back=7
```

**status 回写规则（P2）**

| 分级 | vip.status |
|------|------------|
| 休眠（未达深度阈值） | 休眠码（Appoption vipstatus） |
| 休眠（≥ critical_days） | 流失码 |
| 活跃 / 预警 / 新客 | 恢复为活跃码（若原为休眠/流失） |

```bash
# 仅写快照
python manage.py snapshot_vip_lifecycle --company=yiren

# 同步 status + 快照
python manage.py sync_vip_lifecycle --company=yiren --snapshot

# 同步 + 快照 + CRM 回访任务
python manage.py sync_vip_lifecycle --company=yiren --snapshot --crm-tasks
```

---

## 四、Cron 定时任务

定时任务默认 **同步 vip.status 并写入当日快照**（`--snapshot`）。

| 变量 | 说明 |
|------|------|
| `VIP_LIFECYCLE_SNAPSHOT` | 默认 `1`；设为 `0` 则 cron 仅同步 status 不写快照 |
| `VIP_LIFECYCLE_CRM_TASKS` | 设为 `1` 时，同步+快照后为 `at_risk` / `sleeping` 自动生成 CRM 回访任务 |
| `VIP_LIFECYCLE_CRM_SEGMENTS` | 可选，默认 `at_risk,sleeping` |
| `VIP_LIFECYCLE_CRM_LIMIT` | 可选，每个 segment 最多生成条数，默认 `100` |

### 4.1 脚本

```bash
chmod +x scripts/cron/sync-vip-lifecycle.sh
```

脚本会：

- 调用 `manage.py sync_vip_lifecycle`（可选 `--snapshot`、`--crm-tasks`）
- 写日志到 `genesis_backend/logs/sync-vip-lifecycle-YYYYMMDD.log`
- 用锁目录避免并发重复执行

### 4.2 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `VIP_LIFECYCLE_COMPANIES` | 公司编码，逗号分隔 | `yiren` 或 `yiren,demo` |
| `GENESIS_PYTHON` | Python 路径 | `.../genesis_backend/.venv/bin/python` |
| `GENESIS_LOG_DIR` | 日志目录 | `/var/log/genesis` |
| `VIP_LIFECYCLE_DRY_RUN` | `1` 仅统计 | 调试时用 |
| `VIP_LIFECYCLE_CRM_TASKS` | `1` 同步后生成回访任务 | 生产可选开 |
| `VIP_LIFECYCLE_CRM_SEGMENTS` | 任务 segment | `at_risk,sleeping` |
| `VIP_LIFECYCLE_CRM_LIMIT` | 每 segment 上限 | `100` |

也可直接把公司编码作为第一个参数：`sync-vip-lifecycle.sh yiren`

### 4.3 安装 crontab（Linux 生产机）

1. 创建环境文件 `/etc/genesis/vip-lifecycle.env`：

```bash
VIP_LIFECYCLE_COMPANIES=yiren
GENESIS_PYTHON=/opt/Genesis/genesis_backend/.venv/bin/python
GENESIS_LOG_DIR=/var/log/genesis
VIP_LIFECYCLE_CRM_TASKS=1
```

2. 编辑 crontab：

```bash
sudo mkdir -p /var/log/genesis
crontab -e
```

3. 加入（路径按实际部署修改）：

```cron
0 2 * * * source /etc/genesis/vip-lifecycle.env && /opt/Genesis/scripts/cron/sync-vip-lifecycle.sh
```

完整示例见 [`scripts/cron/genesis-vip-lifecycle.crontab.example`](cron/genesis-vip-lifecycle.crontab.example)。

### 4.4 macOS 开发机（可选）

macOS 默认可用 `crontab`；若用 launchd，可将上述脚本包一层 `ProgramArguments`，每天 2:00 执行一次即可。

本地试跑：

```bash
VIP_LIFECYCLE_DRY_RUN=1 bash scripts/cron/sync-vip-lifecycle.sh yiren
tail -f genesis_backend/logs/sync-vip-lifecycle-$(date +%Y%m%d).log
```

---

## 五、智能助手

Web / 小程序助手（profile=`vip_crm`）可自然语言提问，例如：

- 「有哪些流失预警的客户？」
- 「休眠客户有多少？」
- 「138xxxx 这个客户给运营方案」

工具：`vip_lifecycle_batch`、`vip_lifecycle_one`（见 `assistant/agent_profiles.py`）。

助手回答会按 playbook 结构化输出：**现状 → 风险原因 → 运营目标 → 建议动作 → 参考话术**。

---

## 六、小程序（P1）

| 入口 | 路径 |
|------|------|
| 店务 Tab → **客户生命周期** | `/assistant/lifecycle/lifecycle` |
| 店务 Tab → **CRM 助手** | `/assistant/chat/chat?profile=vip_crm` |
| 客户详情 → 运营方案 | `/assistant/lifecycle/detail?vipuuid=...` |

直连 API（不经 LLM，秒级返回）：

```http
POST /assistant/mp/api/vip/lifecycle/
{"company":"yiren","storecode":"01","ecode":"E001","segment":"at_risk","limit":100}

POST /assistant/mp/api/vip/lifecycle/one/
{"company":"yiren","storecode":"01","ecode":"E001","vipuuid":"..."}
```

Playbook 配置：`genesis_backend/assistant/playbooks/vip_lifecycle.json`（含 `when` 条件与 `template` 话术模板）。

---

## 七、P3：高价值层 + CRM 回访任务

### 高价值（RFM 简化）

活跃客中，近 `high_value_days`（默认 365 天）消费处于门店 **Top `high_value_percent`%**（默认 20%）标记 `value_tier=high_value`。

Appoption（`seg=vip_lifecycle`）：

| itemname | 默认值 |
|----------|--------|
| `high_value_percent` | 20 |
| `high_value_days` | 365 |

查询时 `segment=high_value` 可筛高价值活跃客。

### CRM 回访任务

为 **at_risk / sleeping** 客户写入 `vipcasedetail`（小程序「计划回访」可见）：

```bash
# 预览
python manage.py create_lifecycle_crm_tasks --company=yiren --storecode=01 --segment=at_risk --dry-run

# 写库
python manage.py create_lifecycle_crm_tasks --company=yiren --storecode=01 --segment=at_risk
```

API：

```http
POST /assistant/api/vip/lifecycle/crm-tasks/
{"company":"yiren","storecode":"01","segment":"at_risk","dry_run":false,"limit":100}

POST /assistant/mp/api/vip/lifecycle/crm-tasks/
{"company":"yiren","storecode":"01","ecode":"E001","segment":"at_risk","dry_run":false}
```

同一客户已有未完成的 `[生命周期…]` 任务会自动跳过。

小程序生成任务后可直接跳转 **计划回访**（`/todolist/planvipcase/planvipcase`）。

Cron 自动生成（同步完成后）：

```bash
VIP_LIFECYCLE_CRM_TASKS=1 bash scripts/cron/sync-vip-lifecycle.sh yiren
```

---

## 八、常见问题

**Q：改了 Appoption 后何时生效？**  
查询与同步下一请求即读新配置；无需重启（Django 进程会重新查库）。

**Q：预警客户会改 status 吗？**  
不会。仅 **休眠** 写休眠码，**活跃**（含从休眠恢复）写活跃码。

**Q：Admin 里看不到「客户生命周期」类别？**  
执行 `python manage.py migrate baseinfo` 更新字段 choices。

**Q：多公司部署？**  
`VIP_LIFECYCLE_COMPANIES=yiren,other` 或在 crontab 写多行，每行一个公司。
