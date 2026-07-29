<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in statsCards" :key="card.label">
        <el-card shadow="never" class="stat-card">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" class="mt-4">
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>今日预约</template>
          <el-empty v-if="!todaysBookings.length" description="今日暂无预约" />
          <div v-else>
            <div v-for="b in todaysBookings" :key="b.id" class="booking-row">
              <span>{{ b.vname }} - {{ b.employee_name }}</span>
              <el-tag size="small" :color="getStatusColor(b.status)" effect="dark">
                {{ getStatusLabel(b.status) }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>快捷操作</template>
          <div class="quick-actions">
            <el-button @click="$router.push('/vip')" :icon="User">会员管理</el-button>
            <el-button @click="$router.push('/cashier')" :icon="Ticket">快速开单</el-button>
            <el-button @click="$router.push('/booking')" :icon="Calendar">预约管理</el-button>
            <el-button @click="$router.push('/report')" :icon="DataAnalysis">查看报表</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { BOOKING_STATUS_MAP } from '@/types'
import { getBookingList } from '@/api/booking'
import { User, Ticket, Calendar, DataAnalysis } from '@element-plus/icons-vue'

const statsCards = ref([
  { label: '今日到店', value: '12 人' },
  { label: '今日预约', value: '8 单' },
  { label: '今日业绩', value: '¥ 3,280' },
  { label: '在店会员', value: '5 人' },
])

const todaysBookings = ref<any[]>([])
const getStatusColor = (s: string) => BOOKING_STATUS_MAP[s]?.color || '#999'
const getStatusLabel = (s: string) => BOOKING_STATUS_MAP[s]?.label || s

// 加载今日预约
const loadTodayBookings = async () => {
  try {
    const res = await getBookingList({ date: new Date().toISOString().slice(0, 10).replace(/-/g, '') })
    todaysBookings.value = res.data.results || []
  } catch {}
}
loadTodayBookings()
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}
.stat-card {
  text-align: center;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}
.mt-4 {
  margin-top: 16px;
}
.booking-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #f2f2f2;
}
.booking-row:last-child {
  border-bottom: none;
}
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
</style>
