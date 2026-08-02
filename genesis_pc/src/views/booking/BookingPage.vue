<template>
  <div class="booking-page">
    <!-- ===== 顶部操作栏 ===== -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button-group>
          <el-button @click="prevDay" :icon="ArrowLeft" />
          <el-button @click="nextDay" :icon="ArrowRight" />
        </el-button-group>
        <el-date-picker
          v-model="currentDate"
          type="date"
          value-format="YYYY-MM-DD"
          placeholder="选择日期"
          class="date-picker"
        />
        <el-button @click="goToday" :disabled="isToday">今天</el-button>
        <span class="date-label">{{ displayDateLabel }}</span>
      </div>
      <div class="toolbar-right">
        <el-radio-group v-model="viewMode" size="small">
          <el-radio-button value="timeline">员工</el-radio-button>
          <el-radio-button value="room">房间</el-radio-button>
          <el-radio-button value="instrument">仪器</el-radio-button>
          <el-radio-button value="list">列表</el-radio-button>
        </el-radio-group>
        <el-button type="primary" @click="openCreateDialog" :icon="Plus">新建预约</el-button>
        <el-button @click="scheduleDialogVisible = true" :icon="Calendar">排班管理</el-button>
      </div>
    </div>

    <!-- ===== 统计摘要 ===== -->
    <div class="stats-bar">
      <span class="stat-item"><span class="stat-num">{{ bookingStats.total }}</span> 今日预约</span>
      <span class="stat-item stat-instore"><span class="stat-num">{{ bookingStats.inStore }}</span> 在店</span>
      <span class="stat-item stat-pending"><span class="stat-num">{{ bookingStats.pending }}</span> 未到店</span>
      <span class="stat-item stat-done"><span class="stat-num">{{ bookingStats.completed }}</span> 已完成</span>
      <span class="stat-item stat-cancel"><span class="stat-num">{{ bookingStats.cancelled }}</span> 已取消</span>
      <span class="stat-divider"></span>
      <el-button size="small" @click="scheduleDialogVisible = true" :icon="Calendar">排班管理</el-button>
    </div>

    <!-- ===== 时间线视图 ===== -->

    <div v-show="viewMode !== 'list'" ref="timelineWrapper" class="timeline-wrapper">
      <div class="timeline-scroll" v-if="employeeRows.length">
        <div class="timeline-header" :style="{ minWidth: timelineWidth + 'px' }">
          <div class="emp-header-cell">员工 / 排班</div>
          <div
            v-for="h in timeSlots"
            :key="h"
            class="time-header-cell"
            :style="{ width: timeSlotWidth + 'px' }"
          >
            {{ h }}
          </div>
        </div>

        <div class="timeline-body">
          <div
            v-for="row in timelineRows"
            :key="row.ecode"
            class="timeline-row"
            :class="{ 'row-off': row.isOff }"
            :style="{ height: row.rowHeight + 'px', minWidth: timelineWidth + 'px' }"
          >
            <div class="emp-cell">
              <div class="emp-name">{{ row.name }}</div>
              <template v-if="viewMode === 'timeline'">
                <div class="emp-schedule" v-if="!row.isOff">{{ row.scheduleLabel }}</div>
                <el-tag v-else size="small" type="info" effect="plain">休息</el-tag>
                <el-tag v-if="!row.canBook && !row.isOff" size="small" type="warning" effect="plain" class="no-book-tag">不可预约</el-tag>
              </template>
              <div v-else-if="viewMode === 'room' || viewMode === 'instrument'" class="emp-schedule">{{ row.subtitle }}</div>
            </div>

            <div class="timeline-track" @dblclick="onTimelineDblClick(row, $event)">
              <!-- 半时刻度线 -->
              <div
                v-for="(pos, gi) in halfHourPositions"
                :key="'g'+gi"
                class="half-hour-line"
                :style="{ left: pos + 'px' }"
              ></div>
              <!-- 当前时间指示线 -->
              <div
                v-if="currentTimePx > 0 && currentTimePx < timelineWidth"
                class="current-time-line"
                :style="{ left: currentTimePx + 'px' }"
              ></div>
              <!-- 排班时段底纹（仅员工视图） -->
              <div
                v-if="viewMode === 'timeline' && row.scheduleStart"
                class="schedule-highlight"
                :style="{
                  left: timeToPx(row.scheduleStart || '') + 'px',
                  width: timeDiffPx(row.scheduleStart || '', row.scheduleEnd || '') + 'px'
                }"
              ></div>
              <!-- 预约方块 -->
              <div
                v-for="b in row.bookings"
                :key="b.id"
                class="booking-block"
                :class="'status-' + b.status"
                :style="{
                  left: timeToPx(b.start_time) + 'px',
                  width: timeDiffPx(b.start_time, b.end_time) + 'px',
                  top: b.stackIndex * 40 + 2 + 'px'
                }"
                @mouseenter="hoveredBooking = b"
                @mouseleave="hoveredBooking = null"
                @click="openDetailDrawer(b)"
              >
                <div class="block-inner two-line">
                  <div class="block-line block-line-top">
                    <span class="block-name">{{ b.vname }}</span>
                    <span class="block-time">{{ b.start_time }}-{{ b.end_time }}</span>
                  </div>
                  <div class="block-line block-line-bottom">
                    <span class="block-detail">{{ b.detail || b.employee_name || '' }}</span>
                    <span class="block-emp">{{ b.employee_name || '' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Hover 弹出的快速操作浮层 -->
      <div
        v-if="hoveredBooking"
        class="hover-popover"
        :style="hoverPopoverStyle"
      >
        <div class="popover-header">
          <strong>{{ hoveredBooking.vname }}</strong>
          <el-tag size="small" :color="getStatusInfo(hoveredBooking.status).color" effect="dark">
            {{ getStatusInfo(hoveredBooking.status).label }}
          </el-tag>
        </div>
        <div class="popover-info">{{ hoveredBooking.start_time }} - {{ hoveredBooking.end_time }} | {{ hoveredBooking.employee_name }}</div>
        <div class="popover-info" v-if="hoveredBooking.mtcode">{{ hoveredBooking.mtcode }}</div>
        <div class="popover-actions">
          <template v-for="(action, ai) in getNextActions(hoveredBooking?.status || '100')" :key="ai">
            <el-button size="small" :type="action.type" @click="doStatusChange(hoveredBooking, action.status)">
              {{ action.label }}
            </el-button>
          </template>
          <el-button size="small" @click="hoveredBooking = null">关闭</el-button>
        </div>
      </div>

      <el-empty v-if="!employeeRows.length && loaded" description="该日暂无预约" />
    </div>

    <!-- ===== 列表视图 ===== -->
    <div v-show="viewMode === 'list'" class="list-view">
      <el-table :data="allBookings" stripe style="width: 100%" v-loading="loading" empty-text="暂无预约">
        <el-table-column label="时间" width="120">
          <template #default="{ row }">{{ row.start_time }} - {{ row.end_time }}</template>
        </el-table-column>
        <el-table-column prop="vname" label="客户" width="100" />
        <el-table-column prop="mtcode" label="手机号" width="120" />
        <el-table-column prop="employee_name" label="员工" width="80" />
        <el-table-column prop="room_name" label="房间" width="80" />
        <el-table-column prop="detail" label="备注" min-width="120" show-overflow-tooltip />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :color="getStatusInfo(row.status).color" size="small" effect="dark">
              {{ getStatusInfo(row.status).label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="(s: string) => doStatusChange(row as any, s)">
              <el-button size="small" :icon="Share">状态</el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-for="(action, ai) in getNextActions(row.status)" :key="ai" :command="action.status">
                    {{ action.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button size="small" @click="openDetailDrawer(row as any)" :icon="View">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- ===== Drawer 预约详情 ===== -->
    <el-drawer v-model="detailDrawerVisible" title="预约详情" size="500px" v-if="detailBooking">
      <template #default>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="客户姓名">{{ detailBooking.vname }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ detailBooking.mtcode }}</el-descriptions-item>
          <el-descriptions-item label="会员号">{{ detailBooking.vcode }}</el-descriptions-item>
          <el-descriptions-item label="预约日期">{{ detailBooking.booking_date }}</el-descriptions-item>
          <el-descriptions-item label="预约时间">{{ detailBooking.start_time }} ~ {{ detailBooking.end_time }}</el-descriptions-item>
          <el-descriptions-item label="员工">{{ detailBooking.employee_name }}</el-descriptions-item>
          <el-descriptions-item label="房间">{{ detailBooking.room_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="仪器">{{ detailBooking.instrument_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注">{{ detailBooking.detail || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :color="getStatusInfo(detailBooking.status).color" effect="dark">{{ getStatusInfo(detailBooking.status).label }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="drawer-status-section">
          <div class="section-title">状态变更</div>
          <div class="status-progress">
            <div
              v-for="(s, idx) in statusFlow"
              :key="s.code"
              class="status-step"
              :class="{ active: getStatusIndex() >= idx, done: getStatusIndex() > idx }"
              @click="doStatusChange(detailBooking, s.code)"
            >
              <div class="step-dot" :style="{ background: s.color }" ></div>
              <div class="step-label">{{ s.label }}</div>
            </div>
          </div>
        </div>

        <div class="drawer-actions">
          <el-button :icon="Edit" @click="openEditDialog">编辑预约</el-button>
          <el-button :icon="Delete" type="danger" @click="doStatusChange(detailBooking, '390')">取消预约</el-button>
        </div>
      </template>
    </el-drawer>

    <!-- ===== Dialog 新建/编辑预约 ===== -->
    <el-dialog
      v-model="formDialogVisible"
      :title="isEditing ? '编辑预约' : '新建预约'"
      width="520px"
      @close="resetForm"
    >
      <el-form :model="form" label-width="80px" size="default">
        <el-form-item label="客户姓名" required>
          <el-input v-model="form.vname" placeholder="输入姓名或搜索会员" @input="onVipSearch" />
        </el-form-item>
        <template v-if="vipSuggestions.length">
/* 排班管理 */
.schedule-toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.schedule-week-label { font-size: 14px; font-weight: 600; color: var(--g-color-text); min-width: 130px; text-align: center; }
          <div class="search-suggestions">
            <div
              v-for="v in vipSuggestions"
              :key="v.uuid"
              class="suggestion-item"
              @click="selectVip(v)"
            >
              {{ v.vname }} ({{ v.mtcode }})
            </div>
          </div>
        </template>
        <el-form-item label="手机号">
          <el-input v-model="form.mtcode" />
        </el-form-item>
        <el-form-item label="日期" required>
          <el-date-picker v-model="form.booking_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
          <el-form-item label="开始时间" required>
            <el-time-picker
              v-model="form.start_time"
              format="HH:mm"
              value-format="HH:mm"
              placeholder="选择开始时间"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="结束时间" required>
            <el-time-picker
              v-model="form.end_time"
              format="HH:mm"
              value-format="HH:mm"
              placeholder="选择结束时间"
              style="width: 100%"
            />
          </el-form-item>
        <el-form-item label="员工">
          <el-select v-model="form.employee_code" placeholder="选择员工" clearable filterable style="width: 100%">
            <el-option v-for="e in employees" :key="e.ecode" :label="e.ename" :value="e.ecode" />
          </el-select>
        </el-form-item>
        <el-form-item label="房间">
          <el-select v-model="form.room_id" placeholder="选择房间" clearable style="width: 100%">
            <el-option v-for="r in rooms" :key="r.roomid" :label="r.roomname" :value="r.roomid" />
          </el-select>
        </el-form-item>
        <el-form-item label="仪器">
          <el-select v-model="form.instrument_id" placeholder="选择仪器" clearable style="width: 100%">
            <el-option v-for="i in instruments" :key="i.instrumentid" :label="i.instrumentname" :value="i.instrumentid" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.detail" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
    <!-- ===== 排班管理弹窗 ===== -->
    <el-dialog v-model="scheduleDialogVisible" title="排班管理" width="900px" top="5vh" @open="loadScheduleWeek">
      <div class="schedule-toolbar">
        <el-button :icon="ArrowLeft" size="small" @click="prevScheduleWeek" />
        <span class="schedule-week-label">{{ scheduleWeekLabel }}</span>
        <el-button :icon="ArrowRight" size="small" @click="nextScheduleWeek" />
        <el-button size="small" @click="resetScheduleWeek">本周</el-button>
        <el-button type="primary" size="small" @click="saveSchedule" :loading="savingSchedule">保存排班</el-button>
      </div>
      <el-table :data="scheduleRows" border max-height="480" size="small" style="width: 100%">
        <el-table-column prop="ename" label="员工" width="80" fixed />
        <el-table-column v-for="(day, idx) in scheduleDays" :key="idx" :label="day.label" min-width="100" align="center">
          <template #default="{ row }">
            <el-select
              v-model="row.schedule[day.date]"
              placeholder="选择"
              size="small"
              style="width: 90px"
              @change="scheduleChanged = true"
            >
              <el-option
                v-for="s in shiftOptions"
                :key="s.value"
                :label="s.label"
                :value="s.value"
              />
            </el-select>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="scheduleDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="saveSchedule" :loading="savingSchedule">保存排班</el-button>
      </template>
    </el-dialog>

</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, ArrowRight, Plus, Share, View, Edit, Delete, Calendar
} from '@element-plus/icons-vue'
import {
  getBookingList, createBooking, updateBooking, cancelBooking,
  changeBookingStatus, getBookingDetail, getBookingTimesets,
  getEmployeeSchedule, getBookingEmployees, getBookingRooms,
  getBookingInstruments, checkBookingConflicts, saveSchedules, getShiftList,
} from '@/api/booking'
import { searchVip } from '@/api/vip'
import type {
  Booking, BookingEmployee, BookingRoom, BookingInstrument,
  BookingSchedule, BookingTimeset, ConflictInfo,
} from '@/types'
import { BOOKING_STATUS_MAP } from '@/types'

// ====== 状态 ======
const currentDate = ref(new Date().toISOString().slice(0, 10))
const viewMode = ref<'timeline' | 'room' | 'instrument' | 'list'>('timeline')
const loading = ref(false)
const loaded = ref(false)
const submitting = ref(false)
const scheduleDialogVisible = ref(false)
const savingSchedule = ref(false)
const getMonday = (d: Date): Date => {
  const day = d.getDay()
  const diff = day === 0 ? -6 : 1 - day
  const m = new Date(d)
  m.setDate(d.getDate() + diff)
  return m
}
const scheduleWeekStart = ref(getMonday(new Date()))
const scheduleRows = ref<Array<{ecode: string; ename: string; schedule: Record<string, string>}>>([])
const scheduleDays = ref<Array<{label: string; date: string}>>([])
const shiftOptions = ref<Array<{value: string; label: string}>>([])
const scheduleChanged = ref(false)

const allBookings = ref<Booking[]>([])
const employees = ref<BookingEmployee[]>([])
const rooms = ref<BookingRoom[]>([])
const instruments = ref<BookingInstrument[]>([])
const schedules = ref<BookingSchedule[]>([])
const timesets = ref<BookingTimeset[]>([])
const timelineWrapper = ref<HTMLElement | null>(null)
const hoveredBooking = ref<Booking | null>(null)
const hoverPopoverStyle = ref<Record<string, string>>({})

// Detail drawer
const detailDrawerVisible = ref(false)
const detailBooking = ref<Booking | null>(null)

// Form dialog
const formDialogVisible = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)
const vipSuggestions = ref<Array<{ uuid: string; vname: string; mtcode: string; vcode: string }>>([])

const form = ref({
  vname: '',
  mtcode: '',
  vcode: '',
  vip_uuid: '',
  booking_date: '',
  start_time: '',
  end_time: '',
  employee_code: '',
  room_id: '',
  instrument_id: '',
  detail: '',
  operecode: '',
})


// ====== 设置 ======
const HOUR_START = 9
const HOUR_END = 21
const timeSlotWidth = 120
const currentTimePx = ref(-1)

function updateCurrentTime() {
  const now = new Date()
  const minutes = now.getHours() * 60 + now.getMinutes()
  const base = HOUR_START * 60
  if (minutes >= base && minutes <= HOUR_END * 60) {
    currentTimePx.value = (minutes - base) * (timeSlotWidth / 60)
  } else {
    currentTimePx.value = -1
  }
}

const timelineWidth = computed(() => (HOUR_END - HOUR_START) * timeSlotWidth)

const timeSlots = computed(() => {
  const slots: string[] = []
  for (let h = HOUR_START; h <= HOUR_END; h++) {
    slots.push(String(h).padStart(2, '0') + ':00')
  }
  return slots
})

const halfHourPositions = computed(() => {
  const positions: number[] = []
  for (let h = HOUR_START; h < HOUR_END; h++) {
    positions.push((h - HOUR_START) * timeSlotWidth + timeSlotWidth / 2)
  }
  return positions
})

const bookingStats = computed(() => {
  const all = allBookings.value
  return {
    total: all.length,
    inStore: all.filter(b => ['200','210','220','224','227'].includes(b.status)).length,
    pending: all.filter(b => b.status === '100').length,
    completed: all.filter(b => ['230','290'].includes(b.status)).length,
    cancelled: all.filter(b => b.status === '390').length,
  }
})

const statusFlow = computed(() => {
  const codes = ['100', '200', '210', '220', '230', '290']
  return codes.map(c => ({
    code: c,
    label: BOOKING_STATUS_MAP[c]?.label ?? c,
    color: BOOKING_STATUS_MAP[c]?.color ?? 'var(--g-color-text-muted)',
  }))
})

const isToday = computed(() => {
  return currentDate.value === new Date().toISOString().slice(0, 10)
})

const displayDateLabel = computed(() => {
  const d = new Date(currentDate.value)
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  return `${currentDate.value} (周${weekdays[d.getDay()]})`
})

// ====== 员工行（时间线） ======
interface EmployeeRow {
  ecode: string
  ename: string
  name: string
  canBook: boolean
  isOff: boolean
  scheduleStart: string | null
  scheduleEnd: string | null
  scheduleLabel: string
  bookings: (Booking & { stackIndex: number })[]
  rowHeight: number
}


// ====== 工具函数 ======
function timeToMinutes(t: string): number {
  const parts = t.split(':')
  return parseInt(parts[0] || '0') * 60 + parseInt(parts[1] || '0')
}

function timeToPx(t: string): number {
  const m = timeToMinutes(t)
  const base = HOUR_START * 60
  return Math.max(0, (m - base) * (timeSlotWidth / 60))
}

function timeDiffPx(start: string, end: string): number {
  return Math.max(20, timeToMinutes(end) - timeToMinutes(start)) * (timeSlotWidth / 60)
}

function getStatusInfo(code: string) {
  return BOOKING_STATUS_MAP[code] || { label: '未知', color: 'var(--g-color-text-muted)' }
}

// ====== 状态操作定义 ======
const NEXT_ACTIONS: Record<string, Array<{ label: string; type: 'primary' | 'success' | 'warning' | 'danger' | 'info'; status: string }>> = {
  '100': [{ label: '确认到店', type: 'success', status: '200' }, { label: '取消预约', type: 'danger', status: '390' }],
  '200': [{ label: '进房间', type: 'primary', status: '210' }, { label: '开始服务', type: 'primary', status: '220' }, { label: '取消预约', type: 'danger', status: '390' }],
  '210': [{ label: '开始服务', type: 'primary', status: '220' }, { label: '取消预约', type: 'danger', status: '390' }],
  '220': [{ label: '服务完成', type: 'success', status: '230' }],
  '224': [{ label: '仪器结束', type: 'primary', status: '227' }],
  '227': [{ label: '服务完成', type: 'success', status: '230' }],
  '230': [{ label: '离店', type: 'success', status: '290' }],
  '240': [{ label: '离店', type: 'success', status: '290' }],
}

function getNextActions(status: string) {
  return NEXT_ACTIONS[status] || []
}

const employeeRows = computed<EmployeeRow[]>(() => {
  // Build map of who's working today
  const scheduleMap = new Map<string, BookingSchedule>()
  for (const s of schedules.value) {
    scheduleMap.set(s.ecode, s)
  }

  // Build booking map per employee
  const bookingMap = new Map<string, Booking[]>()
  for (const b of allBookings.value) {
    const e = b.employee_code || '__no_empl__'
    if (!bookingMap.has(e)) bookingMap.set(e, [])
    bookingMap.get(e)!.push(b)
  }

  const rows: EmployeeRow[] = []
  for (const emp of employees.value) {
    const schedule = scheduleMap.get(emp.ecode)
    const empBookings = (bookingMap.get(emp.ecode) || []).sort(
      (a, b) => (a.start_time || '').localeCompare(b.start_time || '')
    )

    // Stacking detection
    interface TimeSlot { start: number; end: number; booking: Booking; stackIdx: number }
    const slots: TimeSlot[] = empBookings.map(b => ({
      start: timeToMinutes(b.start_time || '00:00'),
      end: timeToMinutes(b.end_time || '00:00'),
      booking: b,
      stackIdx: 0,
    }))
    // Assign stack index
    slots.sort((a, b) => a.start - b.start)
    const active: TimeSlot[] = []
    for (const s of slots) {
      // Remove finished
      for (let i = active.length - 1; i >= 0; i--) {
        if (active[i].end <= s.start) active.splice(i, 1)
      }
      // Find lowest free stack
      const used = new Set(active.map(a => a.stackIdx))
      let idx = 0
      while (used.has(idx)) idx++
      s.stackIdx = idx
      active.push(s)
    }
    const maxStack = Math.max(1, ...slots.map(s => s.stackIdx + 1))

    const isOff = !schedule || schedule.scheduleid === '休息'
    rows.push({
      ecode: emp.ecode,
      name: emp.ename || emp.ecode,
      ename: emp.ename || emp.ecode,
      canBook: true,
      isOff: isOff,
      scheduleStart: null,
      scheduleEnd: null,
      scheduleLabel: schedule?.scheduleid || '在岗',
      bookings: slots.map(s => ({ ...s.booking, stackIndex: s.stackIdx })),
      rowHeight: Math.max(56, maxStack * 40 + 8),
    })
  }

  return rows
})

// ====== 房间行（时间线） ======
const roomRows = computed(() => {
  const bookingMap = new Map<string, Booking[]>()
  for (const b of allBookings.value) {
    const rid = b.room_id || '__no_room__'
    if (!bookingMap.has(rid)) bookingMap.set(rid, [])
    bookingMap.get(rid)!.push(b)
  }
  const rows: any[] = []
  for (const rm of rooms.value) {
    const rBookings = (bookingMap.get(rm.roomid) || []).sort(
      (a, b) => (a.start_time || '').localeCompare(b.start_time || '')
    )
    const slots = rBookings.map(b => ({
      start: timeToMinutes(b.start_time || '00:00'),
      end: timeToMinutes(b.end_time || '00:00'),
      booking: b,
      stackIdx: 0,
    }))
    slots.sort((a, b) => a.start - b.start)
    const active: typeof slots = []
    for (const s of slots) {
      for (let i = active.length - 1; i >= 0; i--) {
        if (active[i].end <= s.start) active.splice(i, 1)
      }
      const used = new Set(active.map(a => a.stackIdx))
      let idx = 0
      while (used.has(idx)) idx++
      s.stackIdx = idx
      active.push(s)
    }
    const maxStack = Math.max(1, ...slots.map(s => s.stackIdx + 1))
    rows.push({
      id: rm.roomid,
      name: rm.roomname || rm.roomid,
      subtitle: '房间',
      bookings: slots.map(s => ({ ...s.booking, stackIndex: s.stackIdx })),
      rowHeight: Math.max(56, maxStack * 40 + 8),
    })
  }
  return rows
})

// ====== 仪器行（时间线） ======
const instrumentRows = computed(() => {
  const bookingMap = new Map<string, Booking[]>()
  for (const b of allBookings.value) {
    const iid = b.instrument_id || '__no_inst__'
    if (!bookingMap.has(iid)) bookingMap.set(iid, [])
    bookingMap.get(iid)!.push(b)
  }
  const rows: any[] = []
  for (const inst of instruments.value) {
    const iBookings = (bookingMap.get(inst.instrumentid) || []).sort(
      (a, b) => (a.start_time || '').localeCompare(b.start_time || '')
    )
    const slots = iBookings.map(b => ({
      start: timeToMinutes(b.start_time || '00:00'),
      end: timeToMinutes(b.end_time || '00:00'),
      booking: b,
      stackIdx: 0,
    }))
    slots.sort((a, b) => a.start - b.start)
    const active: typeof slots = []
    for (const s of slots) {
      for (let i = active.length - 1; i >= 0; i--) {
        if (active[i].end <= s.start) active.splice(i, 1)
      }
      const used = new Set(active.map(a => a.stackIdx))
      let idx = 0
      while (used.has(idx)) idx++
      s.stackIdx = idx
      active.push(s)
    }
    const maxStack = Math.max(1, ...slots.map(s => s.stackIdx + 1))
    rows.push({
      id: inst.instrumentid,
      name: inst.instrumentname || inst.instrumentid,
      subtitle: '仪器',
      bookings: slots.map(s => ({ ...s.booking, stackIndex: s.stackIdx })),
      rowHeight: Math.max(56, maxStack * 40 + 8),
    })
  }
  return rows
})

// ====== 按当前视图返回行数据 ======
const timelineRows = computed(() => {
  if (viewMode.value === 'room') return roomRows.value
  if (viewMode.value === 'instrument') return instrumentRows.value
  return employeeRows.value
})

// ====== 排班管理 ======
const scheduleWeekLabel = computed(() => {
  const start = scheduleWeekStart.value
  const end = new Date(start)
  end.setDate(end.getDate() + 6)
  const fmt = (d: Date) => `${d.getMonth()+1}/${d.getDate()}`
  return `${fmt(start)} - ${fmt(end)}`
})

function getWeekDayRange(start: Date): { date: string; label: string }[] {
  const days: { date: string; label: string }[] = []
  const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  for (let i = 0; i < 7; i++) {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    const ds = `${d.getFullYear()}${String(d.getMonth()+1).padStart(2,'0')}${String(d.getDate()).padStart(2,'0')}`
    days.push({ date: ds, label: `${weekDays[i]} ${d.getMonth()+1}/${d.getDate()}` })
  }
  return days
}



async function loadScheduleWeek() {
  scheduleDays.value = getWeekDayRange(scheduleWeekStart.value)
  let employees: Array<{ecode: string; ename: string}> = []
  try {
    const empRes = await getBookingEmployees()
    employees = empRes.data.results || []
  } catch {}
  try {
    const res = await getShiftList()
    shiftOptions.value = res.data.results || []
  } catch {}
  const scheduleMap = new Map<string, Map<string, string>>()
  for (const emp of employees) {
    scheduleMap.set(emp.ecode, new Map())
  }
  try {
    for (const day of scheduleDays.value) {
      const sRes = await getEmployeeSchedule({ date: day.date })
      const daySchedules = sRes.data.results || []
      for (const s of daySchedules) {
        if (scheduleMap.has(s.ecode)) {
          scheduleMap.get(s.ecode)!.set(day.date, s.scheduleid)
        }
      }
    }
  } catch {}
  scheduleRows.value = employees.map(emp => {
    const schedule: Record<string, string> = {}
    for (const day of scheduleDays.value) {
      schedule[day.date] = scheduleMap.get(emp.ecode)?.get(day.date) || ''
    }
    return { ecode: emp.ecode, ename: emp.ename || emp.ecode, schedule }
  })
  scheduleChanged.value = false
}

function prevScheduleWeek() {
  const d = new Date(scheduleWeekStart.value)
  d.setDate(d.getDate() - 7)
  scheduleWeekStart.value = d
  loadScheduleWeek()
}

function nextScheduleWeek() {
  const d = new Date(scheduleWeekStart.value)
  d.setDate(d.getDate() + 7)
  scheduleWeekStart.value = d
  loadScheduleWeek()
}

function resetScheduleWeek() {
  scheduleWeekStart.value = getMonday(new Date())
  loadScheduleWeek()
}

async function saveSchedule() {
  savingSchedule.value = true
  try {
    const schedules: Array<{ecode: string; vsdate: string; scheduleid: string}> = []
    for (const row of scheduleRows.value) {
      for (const day of scheduleDays.value) {
        const scheduleid = row.schedule[day.date]
        if (!scheduleid) continue
        schedules.push({ ecode: row.ecode, vsdate: day.date, scheduleid })
      }
    }
    if (!schedules.length) { ElMessage.warning('没有需要保存的排班'); return }
    const res = await saveSchedules({ schedules })
    ElMessage.success(`已保存 ${res.data.saved} 条排班`)
    scheduleChanged.value = false
    // 同步刷新时间线的排班数据
    const date = currentDate.value.replace(/-/g, '')
    try {
      const sRes = await getEmployeeSchedule({ date })
      schedules.value = sRes.data.results || []
    } catch {}
    await loadScheduleWeek()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally {
    savingSchedule.value = false
  }
}

// ====== 状态索引 ======
function getStatusIndex(): number {
  if (!detailBooking.value) return -1
  return statusFlow.value.findIndex(s => s.code === detailBooking.value!.status)
}

// ====== 数据加载 ======
async function loadData() {
  loading.value = true
  loaded.value = false
  const date = currentDate.value.replace(/-/g, '')
  try {
    const [bRes, sRes, eRes, rRes, iRes, tRes] = await Promise.all([
      getBookingList({ date }),
      getEmployeeSchedule({ date }),
      getBookingEmployees(),
      getBookingRooms(),
      getBookingInstruments(),
      getBookingTimesets(),
    ])
    allBookings.value = bRes.data.results || []
    schedules.value = sRes.data.results || []
    employees.value = eRes.data.results || []
    rooms.value = rRes.data.results || []
    instruments.value = iRes.data.results || []
    timesets.value = tRes.data.results || []
  } catch (e: any) {
    ElMessage.error('加载预约数据失败')
    console.error(e)
  } finally {
    loading.value = false
    loaded.value = true
  }
}

// ====== 日期导航 ======
function prevDay() {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() - 1)
  currentDate.value = d.toISOString().slice(0, 10)
}

function nextDay() {
  const d = new Date(currentDate.value)
  d.setDate(d.getDate() + 1)
  currentDate.value = d.toISOString().slice(0, 10)
}

function goToday() {
  currentDate.value = new Date().toISOString().slice(0, 10)
}

watch(currentDate, loadData)

// 开始时间变化时，结束时间自动延后2小时
watch(() => form.value.start_time, (val) => {
  if (!val) return
  const parts = val.split(':')
  let h = parseInt(parts[0]) + 2
  const m = parts[1] || '00'
  if (h >= 24) h = h - 24
  form.value.end_time = String(h).padStart(2, '0') + ':' + m
})

// ====== 预约详情 ======
async function openDetailDrawer(b: Booking) {
  try {
    const res = await getBookingDetail(b.id)
    detailBooking.value = res.data
  } catch {
    detailBooking.value = b
  }
  detailDrawerVisible.value = true
}

// ====== 状态变更 ======
async function doStatusChange(b: Booking, newStatus: string) {
  if (newStatus === '390') {
    try {
      await ElMessageBox.confirm('确定取消此预约？', '确认', { type: 'warning' })
    } catch {
      return
    }
  }
  try {
    const res = await changeBookingStatus(b.id, newStatus)
    ElMessage.success(getStatusInfo(newStatus).label + ' 成功')
    await loadData()
    if (detailBooking.value?.id === b.id) {
      detailBooking.value = { ...detailBooking.value, status: newStatus }
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.error || '状态变更失败')
  }
}

// ====== 新建 / 编辑 ======
function openCreateDialog() {
  isEditing.value = false
  editingId.value = null
  resetForm()
  form.value.booking_date = currentDate.value
  formDialogVisible.value = true
}

// 双击时间线空白区域 → 新建预约（预填员工和时间）
function onTimelineDblClick(row: any, event: MouseEvent) {
  // 点击在预约方块上时不触发（防止与打开详情冲突）
  if ((event.target as HTMLElement).closest('.booking-block')) return
  const wrapper = timelineWrapper.value
  if (!wrapper) return
  const rect = wrapper.getBoundingClientRect()
  const scrollLeft = wrapper.scrollLeft
  const EMP_CELL_WIDTH = 140
  // 计算点击位置在时间轴上的 X 坐标
  const clickX = event.clientX - rect.left + scrollLeft - EMP_CELL_WIDTH
  if (clickX < 0) return
  // 换算为分钟（从 HOUR_START 开始）
  const minutesFromStart = clickX / (timeSlotWidth / 60)
  const totalMinutes = HOUR_START * 60 + minutesFromStart
  if (totalMinutes < HOUR_START * 60 || totalMinutes > HOUR_END * 60) return
  // 四舍五入到最近 30 分钟
  const rounded = Math.round(totalMinutes / 30) * 30
  const h = Math.floor(rounded / 60)
  const m = rounded % 60
  const startTime = String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0')
  // 预填并打开
  isEditing.value = false
  editingId.value = null
  resetForm()
  form.value.booking_date = currentDate.value
  form.value.start_time = startTime
  // 结束时间 = 开始时间 + 2 小时
  const sp = startTime.split(':')
  let eh = parseInt(sp[0]) + 2
  const em = sp[1] || '00'
  if (eh >= 24) eh = eh - 24
  form.value.end_time = String(eh).padStart(2, '0') + ':' + em
  // 根据当前视图预填对应资源
  if (viewMode.value === 'room') {
    form.value.room_id = row.id || ''
  } else if (viewMode.value === 'instrument') {
    form.value.instrument_id = row.id || ''
  } else {
    form.value.employee_code = row.ecode || ''
  }
  formDialogVisible.value = true
}

function openEditDialog() {
  if (!detailBooking.value) return
  isEditing.value = true
  editingId.value = detailBooking.value.id
  const b = detailBooking.value
  form.value = {
    vname: b.vname,
    mtcode: b.mtcode,
    vcode: b.vcode,
    vip_uuid: b.vip_uuid,
    booking_date: b.booking_date,
    start_time: b.start_time,
    end_time: b.end_time,
    employee_code: b.employee_code,
    room_id: b.room_id,
    instrument_id: b.instrument_id,
    detail: b.detail,
    operecode: '',
  }
  form.value.start_time = b.start_time || '09:00'
  form.value.end_time = b.end_time || '10:00'
  formDialogVisible.value = true
}

function resetForm() {
  form.value = {
    vname: '', mtcode: '', vcode: '', vip_uuid: '',
    booking_date: currentDate.value, start_time: '', end_time: '',
    employee_code: '', room_id: '', instrument_id: '', detail: '', operecode: '',
  }
  form.value.start_time = '09:00'
  form.value.end_time = '11:00'
  vipSuggestions.value = []
}

let vipSearchTimer: ReturnType<typeof setTimeout> | null = null

async function onVipSearch() {
  if (vipSearchTimer) clearTimeout(vipSearchTimer)
  if (!form.value.vname || form.value.vname.length < 1) {
    vipSuggestions.value = []
    return
  }
  vipSearchTimer = setTimeout(async () => {
    try {
      const res = await searchVip(form.value.vname)
      vipSuggestions.value = (res.data.results || res.data || []).slice(0, 5).map((v: any) => ({
        uuid: v.uuid || v.id,
        vname: v.vname,
        mtcode: v.mtcode,
        vcode: v.vcode,
      }))
    } catch { vipSuggestions.value = [] }
  }, 300)
}

function selectVip(v: { uuid: string; vname: string; mtcode: string; vcode: string }) {
  form.value.vname = v.vname
  form.value.mtcode = v.mtcode
  form.value.vcode = v.vcode
  form.value.vip_uuid = v.uuid
  vipSuggestions.value = []
}

async function submitForm() {
  if (!form.value.vname) { ElMessage.warning('请输入客户姓名'); return }
  if (!form.value.booking_date) { ElMessage.warning('请选择预约日期'); return }
  if (!form.value.start_time || !form.value.end_time) { ElMessage.warning('请选择预约时间'); return }
  if (!form.value.employee_code) { ElMessage.warning('请选择员工'); return }
  if (!form.value.room_id) { ElMessage.warning('请选择房间'); return }
  submitting.value = true
  try {
    const payload = {
      ...form.value,
      start_time: form.value.start_time || '09:00',
      end_time: form.value.end_time || '10:00',
      company: localStorage.getItem('genesis_pc_company') || '',
      storecode: localStorage.getItem('genesis_pc_storecode') || '',
    }
    if (isEditing.value && editingId.value) {
      await updateBooking(editingId.value, payload)
      ElMessage.success('更新成功')
    } else {
      await createBooking(payload)
      ElMessage.success('新建成功')
    }
    formDialogVisible.value = false
    await loadData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  } finally {
    submitting.value = false
  }
}

// ====== 生命周期 ======
let timeInterval: ReturnType<typeof setInterval>

onMounted(() => {
  loadData()
  updateCurrentTime()
  timeInterval = setInterval(updateCurrentTime, 60000)
})

onUnmounted(() => {
  if (timeInterval) clearInterval(timeInterval)
})


</script>

<style scoped>
.booking-page { height: 100%; display: flex; flex-direction: column; }

/* 工具栏 */
.toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 16px; background:var(--g-color-surface); border-bottom: 1px solid var(--g-color-border);
  flex-shrink: 0; gap: 12px; flex-wrap: wrap;
}
.toolbar-left { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.toolbar-right { display: flex; align-items: center; gap: 8px; }
.date-picker { width: 140px; }
.date-label { font-size: 14px; color: var(--g-color-text-secondary); white-space: nowrap; }

/* 时间线 */
.timeline-wrapper { flex: 1; overflow: auto; position: relative; }
.timeline-scroll { min-width: 100%; padding-bottom: 16px; }

.timeline-header {
  display: flex; border-bottom: 1px solid var(--g-color-border-strong);
  position: sticky; top: 0; background: var(--g-color-surface-muted); z-index: 10;
}
.emp-header-cell {
  width: 140px; flex-shrink: 0; padding: 8px 12px;
  font-size: 12px; color: var(--g-color-text-muted); font-weight: 600; text-align: center;
}
.time-header-cell {
  flex-shrink: 0; padding: 8px 0; font-size: 12px; color: var(--g-color-text-muted); text-align: center;
  border-left: 1px solid var(--g-color-border-strong);
}

.timeline-body { }
.timeline-row {
  display: flex; border-bottom: 1px solid var(--g-color-border);
  position: relative; transition: background 0.15s;
}
.timeline-row:hover { background: var(--g-color-surface-muted); }
.row-off { opacity: 0.5; }

.emp-cell {
  width: 140px; flex-shrink: 0; padding: 6px 12px;
  display: flex; flex-direction: column; justify-content: center;
  border-right: 1px solid var(--g-color-border-strong); background:var(--g-color-surface); z-index: 5;
}
.emp-name { font-size: 14px; font-weight: 500; color: var(--g-color-text); }
.emp-schedule { font-size: 11px; color: var(--g-color-text-muted); margin-top: 1px; }
.no-book-tag { margin-top: 2px; }

.timeline-track {
  flex: 1; position: relative; min-height: 56px;
}

.schedule-highlight {
  position: absolute; top: 2px; bottom: 2px;
  background: var(--g-color-primary-soft); border-radius: 2px; z-index: 0;
}

.booking-block {
  position: absolute; height: 38px; cursor: pointer;
  border-radius: 3px; z-index: 2; overflow: hidden;
  transition: box-shadow 0.15s; min-width: 48px;
}
.booking-block:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.15); z-index: 20;
}
.booking-block.status-100 { background: var(--g-color-warning-bg); border-top: 3px solid var(--g-color-warning); }
.booking-block.status-200 { background: var(--g-color-success-soft); border-top: 3px solid var(--g-color-success); }
.booking-block.status-210 { background: var(--g-color-primary-soft); border-top: 3px solid var(--g-color-primary); }
.booking-block.status-220 { background: var(--g-color-primary-soft); border-top: 3px solid var(--g-color-primary); }
.booking-block.status-230,
.booking-block.status-290 { background: var(--g-color-surface-muted); border-top: 3px solid var(--g-color-text-muted); }
.booking-block.status-390 { background: var(--g-color-danger-bg); border-top: 3px solid var(--g-color-danger); opacity: 0.7; }
.booking-block.status-390 .block-line-top,
.booking-block.status-390 .block-line-bottom { opacity: 0.6; }

.block-inner.two-line {
  display: flex; flex-direction: column; gap: 0;
  padding: 2px 6px 1px; height: 100%; overflow: hidden;
}
.block-line {
  display: flex; justify-content: space-between; align-items: center;
  line-height: 1.3;
}
.block-line-top { margin-bottom: 0; }
.block-line-bottom { }
.block-name { font-size: 11px; font-weight: 600; color: var(--g-color-text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; flex: 1; }
.block-time { font-size: 9px; color: var(--g-color-text-muted); white-space: nowrap; margin-left: 4px; flex-shrink: 0; }
.block-detail { font-size: 10px; color: var(--g-color-text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; flex: 1; }
.block-emp { font-size: 9px; color: var(--g-color-text-muted); white-space: nowrap; margin-left: 4px; flex-shrink: 0; }

/* Hover 浮层 */
.hover-popover {
  position: fixed; z-index: 2000; background:var(--g-color-surface);
  border-radius: 6px; box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  padding: 12px; min-width: 200px; max-width: 320px;
}
.popover-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.popover-info { font-size: 12px; color: var(--g-color-text-secondary); margin-bottom: 2px; }
.popover-actions { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }

/* 列表 */
.list-view { flex: 1; padding: 16px; overflow: auto; }

/* Drawer */
.drawer-status-section { margin-top: 20px; }
.section-title { font-size: 14px; font-weight: 600; color: var(--g-color-text); margin-bottom: 12px; }
.status-progress { display: flex; gap: 4px; align-items: center; }
.status-step {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  cursor: pointer; padding: 4px 8px; border-radius: 4px;
  transition: background 0.15s;
}
.status-step:hover { background: var(--g-color-surface-muted); }
.status-step.active .step-dot { transform: scale(1.3); box-shadow: 0 0 0 3px color-mix(in srgb, var(--g-color-primary) 30%, transparent); }
.status-step.done { opacity: 0.6; }
.step-dot { width: 12px; height: 12px; border-radius: 50%; transition: 0.15s; }
.step-label { font-size: 11px; color: var(--g-color-text-secondary); white-space: nowrap; }

.drawer-actions { display: flex; gap: 8px; margin-top: 20px; }

/* 搜索提示 */
/* 排班管理 */
.schedule-toolbar { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.schedule-week-label { font-size: 14px; font-weight: 600; color: var(--g-color-text); min-width: 130px; text-align: center; }
.search-suggestions {
  border: 1px solid var(--g-color-border-strong); border-radius: 4px; max-height: 160px; overflow-y: auto;
  margin-bottom: 8px;
}
.suggestion-item { padding: 6px 12px; cursor: pointer; font-size: 13px; }
.suggestion-item:hover { background: var(--g-color-surface-muted); }

/* 统计摘要 */
.stats-bar {
  display: flex; align-items: center; gap: 16px;
  padding: 8px 16px; background:var(--g-color-surface);
  border-bottom: 1px solid var(--g-color-border); flex-shrink: 0;
  font-size: 13px; color: var(--g-color-text-secondary);
}
.stat-item { white-space: nowrap; }
.stat-num { font-size: 18px; font-weight: 700; margin-right: 4px; }
.stat-instore .stat-num { color: var(--g-color-primary); }
.stat-pending .stat-num { color: var(--g-color-money); }
.stat-done .stat-num { color: var(--g-color-success); }
.stat-cancel .stat-num { color: var(--g-color-text-muted); }
.stat-divider { flex: 1; }

/* 半时刻度线 */
.half-hour-line {
  position: absolute; top: 0; bottom: 0;
  width: 1px; background: repeating-linear-gradient(
    to bottom,
    transparent 0px, transparent 4px,
    var(--g-color-border-strong) 4px, var(--g-color-border-strong) 5px
  ); z-index: 1; pointer-events: none;
}

/* 当前时间指示线 */
.current-time-line {
  position: absolute; top: 0; bottom: 0;
  width: 2px; background: var(--g-color-danger); z-index: 15;
  pointer-events: none;
}
.current-time-line::before {
  content: ''; position: absolute; top: 0; left: -4px;
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--g-color-danger);
}

</style>
