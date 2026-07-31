# 预约管理系统（Genesis PC）

## 概述

预约管理系统为 genesis_pc 提供时间线看板和排班管理功能。后端 API 在 `genesis_backend/booking/views.py`，前端页面在 `genesis_pc/src/views/booking/BookingPage.vue`。

**技能入口文件：**
- `genesis_backend/booking/views.py` — 后端 API
- `genesis_backend/booking/urls.py` — 路由注册
- `genesis_pc/src/views/booking/BookingPage.vue` — 前端时间线看板

**注意：** banxiaozhu（微信小程序）的预约功能使用 `/adviser/` 下的旧端点（`get_bookinglist`、`add_bookingevent` 等），与 PC 端新端点独立。修改 `booking/` 下的代码不会影响 banxiaozhu。

## 数据模型

| 模型 | 位置 | 表 | 关键字段 |
|------|------|-----|---------|
| `Bookingevent` | `adviser/models.py` | `bookingevent` | `bookingeventid`, `bookingstartdate/starttime/endtime`, `vcode/vname/mtcode`（客户）, `ecode`（员工）, `roomid`, `instrumentid`, `bookingstatus`（100-390）, `bookingdetail`（备注）, `bookingflag` |
| `Timeset` | `adviser/models.py` | `timeset` | `timeid`, `flag` |
| `Emplschedule` | `adviser/models.py` | `emplschedule` | `vsdate`（日期 YYYYMMDD）, `ecode`（员工编码）, `scheduleid`（班次） |
| `Room` | `adviser/models.py` | `room` | `roomid`, `roomname` |
| `Instrument` | `adviser/models.py` | `instrument` | `instrumentid`, `instrumentname` |

## 后端 API

### 旧端点（保留，banxiaozhu 依赖）

| 端点 | 文件位置 | 用途 |
|------|---------|------|
| `GET /booking/querybooking/` | `booking/views.py` | 按房间查当日预约 |
| `GET /booking/queryroom/` | `booking/views.py` | 房间列表 |
| `POST /booking/changestatus/` | `booking/views.py` | 预约状态变更（旧版，full if-else） |
| `GET /booking/checkpwd/` | `booking/views.py` | 密码验证 |
| `GET /booking/QueryBookingStatus/` | `booking/views.py` | 单条预约状态查询 |

### 新端点（PC 端使用）

| 端点 | 函数 | 说明 |
|------|------|------|
| `GET /booking/events/` | `events_list` | 按日期查预约（排除 390 取消状态） |
| `GET /booking/events/{id}/` | `events_detail` | 单条预约明细 |
| `POST /booking/events/create/` | `events_create` | 新建预约（会员不存在时自动创建散客） |
| `PUT /booking/events/{id}/update/` | `events_update` | 更新预约 |
| `POST /booking/events/{id}/status/` | `events_status` | 自由状态流转（无方向限制，仅记录时间戳） |
| `POST /booking/events/{id}/cancel/` | `events_cancel` | 快捷取消 |
| `GET /booking/events/{id}/check-conflicts/` | `events_check_conflicts` | 冲突检测 |
| `GET /booking/timesets/` | `timesets_list` | 时段模板 |
| `GET /booking/schedules/` | `schedules_list` | 员工排班（按日期） |
| `POST /booking/schedules/save/` | `schedules_save` | 批量保存排班 |
| `GET /booking/schedules/shift-list/` | `shift_list` | 班次列表 |
| `GET /booking/employees/` | `employees_list` | 可预约员工 |
| `GET /booking/rooms/` | `rooms_list` | 房间列表 |
| `GET /booking/instruments/` | `instruments_list` | 仪器列表 |

### 关键业务逻辑

**员工可见条件：**
```sql
empl.status='Y' AND empl.flag='Y'       -- 在职且启用
AND position.bookingflag='Y'            -- 岗位有预约权限
AND position.flag='Y'                   -- 岗位启用
AND empl.company=X AND empl.storecode=X -- 本店
```

**新建预约时会员处理：**
1. 通过 `vip_uuid` 查找会员
2. 未找到则通过 `vcode` 查找
3. 仍未找到则自动创建散客（`viptype='30'`）

## 前端功能

### 时间线看板（BookingPage.vue）

**三视图：**
- 员工 / 房间 / 仪器（顶部 radio-group 切换）
- 共用时间线模板，左侧信息区 + 右侧时间轴

**时间线布局：**
| 属性 | 值 |
|------|-----|
| 时间范围 | 09:00 - 21:00 |
| 每小时宽度 | 120px |
| 半时刻度 | 有（浅灰色虚线） |
| 当前时间线 | 红色竖线，每分钟自动刷新 |

**预约方块：**
- 38px 高，双行文字布局
- 第一行：客户名 + 时间
- 第二行：备注/项目 + 员工名
- 顶部 3px 色条表示状态
- 颜色：黄=未到店、绿=已到店、蓝=服务中、灰=已完成、红=取消
- 重叠时自动堆叠（`stackIndex` 算法）

**交互：**
| 操作 | 行为 |
|------|------|
| 悬停方块 | 弹出 Hover 浮层，显示快速操作按钮（到店/进房/开始服务/取消） |
| 点击方块 | 打开 Drawer 详情面板，含状态进度条 |
| 双击空白 | 弹出新建预约弹窗，预填员工/房间/仪器 + 时间（自动 +2h） |

### 排班管理

弹窗内周排班表格：
- 员工 × 7 天
- 左右箭头切换周次 + 「本周」按钮
- 每格下拉选择班次
- 班次选项：早班 / 中班 / 晚班 / 正常班 / 休息
- 批量保存

### 时间线核心算法

```javascript
// 像素换算
timeSlotWidth = 120  // 每小时宽度
function timeToPx(t) {
  const base = HOUR_START * 60
  return Math.max(0, (timeToMinutes(t) - base) * (timeSlotWidth / 60))
}

// 冲突堆叠
// 1. 按开始时间排序
// 2. 遍历每个预约，检查与已激活预约的重叠
// 3. 分配最低可用堆叠索引
// 4. 行高 = maxStack × 40 + 8
// 5. 方块 top 偏移 = stackIndex × 40 + 2
```

## 相关文件

| 文件 | 用途 |
|------|------|
| `genesis_backend/booking/views.py` | 后端 REST API |
| `genesis_backend/booking/urls.py` | 路由注册 |
| `genesis_backend/common/constants.py` | SCHEDULELIST 班次定义 |
| `genesis_backend/adviser/models.py` | 数据模型 |
| `genesis_pc/src/views/booking/BookingPage.vue` | 前端时间线看板 |
| `genesis_pc/src/api/booking.ts` | 前端 API 函数 |
| `genesis_pc/src/types/index.ts` | Booking 类型定义 |
