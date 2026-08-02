<template>
  <div class="page dashboard">
    <div class="page-header">
      <div class="dash-title-wrap">
        <h3 class="page-title">运营工作台</h3>
        <span class="page-subtitle">{{ todayLabel }} · {{ storeLabel }}</span>
      </div>
      <el-button size="small" text type="primary" :icon="Refresh" @click="loadAll">刷新数据</el-button>
    </div>

    <div class="stat-grid dashboard-kpis">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total }}</div>
        <div class="stat-label">今日预约</div>
      </div>
      <div class="stat-card">
        <div class="stat-value primary">{{ stats.inStore }}</div>
        <div class="stat-label">在店 / 服务中</div>
      </div>
      <div class="stat-card">
        <div class="stat-value success">{{ stats.completed }}</div>
        <div class="stat-label">已完成</div>
      </div>
      <div class="stat-card">
        <div class="stat-value warn">{{ stats.cancelled }}</div>
        <div class="stat-label">已取消</div>
      </div>
      <div class="stat-card">
        <div class="stat-value money">¥{{ todayAmount.toFixed(0) }}</div>
        <div class="stat-label">今日业绩</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ pendingHungs }}</div>
        <div class="stat-label">待结挂单</div>
      </div>
    </div>

    <div class="dashboard-body">
      <div class="section dashboard-timeline">
        <div class="section-head">
          <span>今日预约时间线</span>
          <span class="section-hint">{{ timeline.length }} 单</span>
        </div>
        <div class="timeline-list" v-loading="loading">
          <div v-if="!timeline.length && !loading" class="empty-state">今日暂无预约</div>
          <div v-for="item in timeline" :key="item.id" class="timeline-item">
            <div class="tl-time">{{ item.time }}</div>
            <span class="status-dot" :style="{ background: item.statusColor }"></span>
            <div class="tl-main">
              <div class="tl-name">
                {{ item.vname }}
                <span v-if="item.mtcode" class="tl-mt">{{ item.mtcode }}</span>
              </div>
              <div class="tl-sub">{{ item.employee }}</div>
            </div>
            <el-tag size="small" effect="plain">{{ item.statusLabel }}</el-tag>
          </div>
        </div>
      </div>

      <div class="dashboard-right">
        <div class="section">
          <div class="section-head"><span>快捷入口</span></div>
          <div class="quick-grid">
            <div v-for="q in quickActions" :key="q.path" class="quick-item" @click="$router.push(q.path)">
              <el-icon :size="20"><component :is="q.icon" /></el-icon>
              <span>{{ q.title }}</span>
            </div>
          </div>
        </div>
        <div class="section">
          <div class="section-head"><span>门店今日概况</span></div>
          <div class="overview-list">
            <div class="ov-row"><span>营业日期</span><b>{{ todayLabel }}</b></div>
            <div class="ov-row"><span>今日预约</span><b>{{ stats.total }} 单</b></div>
            <div class="ov-row"><span>在店会员</span><b>{{ stats.inStore }} 人</b></div>
            <div class="ov-row"><span>待结挂单</span><b>{{ pendingHungs }} 单</b></div>
            <div class="ov-row"><span>今日业绩</span><b class="money">¥{{ todayAmount.toFixed(2) }}</b></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getBookingList } from '@/api/booking'
import request from '@/api/request'
import { computeBookingStats, buildTimeline } from '@/utils/dashboard'
import { Ticket, Coin, User, Calendar, Promotion, DataAnalysis, Refresh } from '@element-plus/icons-vue'

const company = localStorage.getItem('genesis_pc_company') || ''
const storecode = localStorage.getItem('genesis_pc_storecode') || ''
const storeName = localStorage.getItem('genesis_pc_storename') || ''
const storeLabel = storeName || storecode || '当前门店'

const loading = ref(false)
const bookings = ref<any[]>([])
const pendingHungs = ref(0)
const todayAmount = ref(0)

const todayLabel = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' })

function todayStr() {
  const d = new Date()
  return '' + d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0')
}

const stats = computed(() => computeBookingStats(bookings.value))
const timeline = computed(() => buildTimeline(bookings.value))

const quickActions = [
  { title: '手工开单', path: '/adviser/billing-v2', icon: Ticket },
  { title: '收银结账', path: '/cashier/checkout', icon: Coin },
  { title: '会员管理', path: '/vip', icon: User },
  { title: '预约管理', path: '/booking', icon: Calendar },
  { title: '营销活动', path: '/campaign', icon: Promotion },
  { title: '经营报表', path: '/report/performance', icon: DataAnalysis },
]

async function loadAll() {
  loading.value = true
  try {
    const today = todayStr()
    const [bookingRes, hungRes, perfRes] = await Promise.all([
      getBookingList({ date: today }),
      request.get('/adviser/get_hung_list/', { params: { company, storecode } }),
      request.get('/report/store_performance_api/', { params: { company, from_date: today, to_date: today } }),
    ])
    bookings.value = bookingRes.data?.results || []
    pendingHungs.value = (Array.isArray(hungRes.data) ? hungRes.data : []).length
    const rows = Array.isArray(perfRes.data) ? perfRes.data : []
    todayAmount.value = rows.reduce((s: number, r: any) => s + (Number(r.total) || 0), 0)
  } catch {
    bookings.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)
</script>

<style scoped>
.dashboard { max-width: 1440px; margin: 0 auto; }
.dash-title-wrap { display: flex; align-items: baseline; gap: 10px; }
.dashboard-kpis { margin-bottom: 4px; }
.stat-value.primary { color: var(--g-color-primary); }
.stat-value.success { color: var(--g-color-success); }
.stat-value.warn { color: var(--g-color-warning); }
.stat-value.money { color: var(--g-color-money); }

.dashboard-body { flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 12px; }
.dashboard-timeline { display: flex; flex-direction: column; min-height: 0; }
.dashboard-timeline .section-head { flex-shrink: 0; }
.section-hint { font-size: 12px; font-weight: 400; color: var(--g-color-text-muted); }
.timeline-list { flex: 1; min-height: 0; overflow-y: auto; padding: 4px 14px 12px; }
.timeline-item { display: flex; align-items: center; gap: 10px; padding: 9px 0; border-bottom: 1px solid var(--g-color-border); }
.timeline-item:last-child { border-bottom: none; }
.tl-time { width: 42px; font-size: 13px; font-weight: 600; color: var(--g-color-text); font-variant-numeric: tabular-nums; }
.tl-main { flex: 1; min-width: 0; }
.tl-name { font-size: 14px; font-weight: 600; color: var(--g-color-text); display: flex; align-items: center; gap: 6px; }
.tl-mt { font-size: 11px; font-weight: 400; color: var(--g-color-text-muted); }
.tl-sub { font-size: 12px; color: var(--g-color-text-muted); margin-top: 1px; }

.dashboard-right { display: flex; flex-direction: column; gap: 12px; min-height: 0; }
.quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 10px 14px 14px; }
.quick-item { display: flex; align-items: center; gap: 8px; padding: 10px 12px; border: 1px solid var(--g-color-border); border-radius: var(--g-radius); cursor: pointer; color: var(--g-color-text-secondary); transition: border-color 0.15s, background 0.15s; }
.quick-item:hover { border-color: var(--g-color-primary-border); background: var(--g-color-primary-soft); color: var(--g-color-primary); }
.quick-item span { font-size: 13px; font-weight: 500; }
.overview-list { padding: 4px 14px 12px; }
.ov-row { display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--g-color-border); font-size: 13px; }
.ov-row:last-child { border-bottom: none; }
.ov-row span { color: var(--g-color-text-secondary); }
.ov-row b { color: var(--g-color-text); font-weight: 600; }
.ov-row b.money { color: var(--g-color-money); }
</style>
