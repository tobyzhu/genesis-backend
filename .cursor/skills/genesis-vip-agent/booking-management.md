# 预约管理模块

## 概述

Genesis PC 的预约管理系统位于 `genesis_pc/src/views/booking/BookingPage.vue`，后端 API 在 `genesis_backend/booking/views.py`。提供时间线看板（员工/房间/仪器三视图）、排班管理、新建/编辑/状态流转等完整功能。

## 后端

### 数据模型（`adviser/models.py`）

| 模型 | 表 | 说明 |
|------|-----|------|
| `Bookingevent` | `bookingevent` | 预约主表，含 `bookingstartdate/starttime/endtime`、`vcode/vname/mtcode`（客户）、`ecode`（员工）、`roomid`（房间）、`instrumentid`（仪器）、`bookingstatus`（状态 100-390）、`bookingdetail`（备注） |
| `Timeset` | `timeset` | 时段模板，`timeid`、`flag` |
| `Emplschedule` | `emplschedule` | 员工排班，`vsdate`（日期）、`ecode`（员工）、`scheduleid`（早班/中班/晚班/正常班/休息） |
| `Room` | `room` | 房间定义，`roomid`、`roomname` |
| `Instrument` | `instrument` | 仪器定义，`instrumentid`、`instrumentname` |
| `Position` | `position` | 岗位定义，`bookingflag`（Y=可预约）、`flag` |

### 预约状态编码

| 编码 | 含义 |
|------|------|
| 100 | 未到店（初始状态） |
| 110 | 临近 |
| 120 | 推迟 |
| 130 | 确认 |
| 200 | 已到店 |
| 210 | 进房间 |
| 220 | 开始服务 |
| 224 | 仪器开始 |
| 227 | 仪器结束 |
| 230 | 服务结束 |
| 240 | 离房 |
| 250 | 呼叫清洁 |
| 260 | 开始清洁 |
| 270 | 清洁结束 |
| 290 | 离店 |
| 390 | 取消 |

状态流转无单向限制，任意方向可跳转（已在 `events_status` 中去掉校验）。

### API 端点（`booking/views.py` + `booking/urls.py`）

**旧端点（保留，banxiaozhu 依赖）：**
- `GET /booking/querybooking/` — 按房间查预约
- `GET /booking/queryroom/` — 房间列表
- `POST /booking/changestatus/` — 状态变更
- `GET /booking/checkpwd/` — 密码验证
- `GET /booking/QueryBookingStatus/` — 状态查询

**新 REST 端点：**
- `GET /booking/events/` — 按日期查预约列表（排除取消状态，联查员工/房间/仪器名称）
- `GET /booking/events/{id}/` — 单条预约明细
- `POST /booking/events/create/` — 新建预约（会员不存在时自动创建散客 `viptype='30'`）
- `PUT /booking/events/{id}/update/` — 更新预约（字段级部分更新）
- `POST /booking/events/{id}/status/` — 自由状态流转（仅记录时间戳）
- `POST /booking/events/{id}/cancel/` — 快捷取消
- `GET /booking/events/{id}/check-conflicts/` — 冲突检测（同员工/同房间重叠）
- `GET /booking/timesets/` — 时段模板
- `GET /booking/schedules/` — 员工排班查询（按日期）
- `POST /booking/schedules/save/` — 批量保存排班（按 company/storecode/vsdate/ecode 的 upsert）
- `GET /booking/schedules/shift-list/` — 班次列表（SCHEDULELIST）

### 员工可见条件

```python
empl.status='Y' AND empl.flag='Y'       # 在职且启用
AND position.bookingflag='Y'            # 岗位可预约
AND position.flag='Y'                   # 岗位启用
```

## 前端（BookingPage.vue）

### 页面结构

```
┌─ 工具栏 ─────────────────────────────────────────────────┐
│ ◀ 日期 ▶  今天   日期标签       [员工] [房间] [仪器] [列表]   新建预约 │
├─ 统计摘要 ───────────────────────────────────────────────┤
│ 今日预约 / 在店 / 未到店 / 已完成 / 已取消   排班管理      │
├─ 时间线视图 ───────────────────────────────────────────┤
│ 员工/排班  09:00  09:30  10:00  10:30  ...  21:00      │
│ ┌──────┐                                                │
│ │张技师│ ▓▓▓▓ 排班 ▓▓  ┌─────┐                         │
│ │早班  │                │李小花│                         │
│ │      │                │面部  │                         │
│ │      │                │10:00 │                         │
│ └──────┘                └─────┘                         │
├─ 列表视图 ──────────────────────────────────────────────┤
│ 时间 | 客户 | 手机 | 员工 | 房间 | 项目 | 状态      操作 │
└─────────────────────────────────────────────────────────┘
```

### 功能

| 功能 | 说明 |
|------|------|
| **三视图** | 员工 / 房间 / 仪器，共用时间线模板 |
| **时间线** | 09:00-21:00，每小时 120px 宽度，半时刻度线 |
| **当前时间线** | 红色竖线，每分钟自动刷新 |
| **预约方块** | 38px 双行（客户名+时间 / 备注+员工），顶部色条表示状态 |
| **冲突堆叠** | 多预约重叠自动垂直堆叠 |
| **Hover 浮层** | 悬停显示快速状态操作按钮 |
| **Drawer 详情** | 点击方块展开完整信息 + 状态进度条 |
| **双击新建** | 双击时间线空白 → 预填员工/房间/仪器 + 时间 → 自动+2h |
| **排班管理** | 周排班表格，5 种班次，批量保存 |
| **工作台联动** | DashboardPage 工作台显示今日预约概览 |

### 时间线计算

```javascript
// px/h 比率
timeSlotWidth = 120    // 每小时占 120px

// 时间 → px
timeToPx(t) = (timeToMinutes(t) - HOUR_START * 60) * (timeSlotWidth / 60)

// 堆叠
stackIndex: 按重叠分配最低可用索引
rowHeight = maxStack * 40 + 8
blockOffset = stackIndex * 40 + 2
```

### 排班管理

弹窗中的周排班表格，按「本周」为标准，左右切换周次。每个单元格下拉选择班次（早班/中班/晚班/正常班/休息），批量保存。

## 排班种类（SCHEDULELIST）

定义在 `genesis_backend/common/constants.py`：
```python
SCHEDULELIST = (
    ('早班', '早班'),
    ('中班', '中班'),
    ('晚班', '晚班'),
    ('正常班', '正常班'),
    ('休息', '休息'),
)
```

保存排班时通过 `update_or_create` 写入 `emplschedule` 表，按 `(company, storecode, vsdate, ecode)` 唯一约束。

## 关键文件

| 文件 | 用途 |
|------|------|
| `genesis_backend/booking/views.py` | 后端 API（19 个端点） |
| `genesis_backend/booking/urls.py` | 路由注册 |
| `genesis_backend/common/constants.py` | SCHEDULELIST 定义 |
| `genesis_backend/adviser/models.py` | Bookingevent / Timeset / Emplschedule / Room / Instrument |
| `genesis_pc/src/views/booking/BookingPage.vue` | 前端时间线看板 |
| `genesis_pc/src/views/DashboardPage.vue` | 工作台今日预约卡片 |
| `genesis_pc/src/api/booking.ts` | 前端 API 层 |
| `genesis_pc/src/types/index.ts` | Booking 类型定义 |
