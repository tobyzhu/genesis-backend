<template>
  <div>
    <h2 style="margin:0 0 16px 0;font-size:18px;font-weight:600">挂单管理</h2>

    <el-card shadow="never" class="filter-card">
      <div style="display:flex;gap:12px;align-items:center">
        <span style="font-size:13px;color:#606266;white-space:nowrap">按会员筛选：</span>
        <el-input v-model="vipKeyword" placeholder="输入姓名/手机号/会员号" clearable size="small" style="width:240px" @keyup.enter="searchVip" />
        <el-button size="small" type="primary" @click="searchVip">筛选</el-button>
        <el-button size="small" @click="clearFilter">清除筛选</el-button>
        <span v-if="selectedVip" style="font-size:13px;color:#409eff;margin-left:8px">
          当前: {{ selectedVip.vname }} ({{ selectedVip.vcode }})
        </span>
      </div>
    </el-card>

    <el-card shadow="never" style="margin-top:16px">
      <el-table :data="hungList" size="small" stripe v-loading="loading" max-height="calc(100vh - 280px)">
        <el-table-column label="挂单号" width="180">
          <template #default="{ row }">{{ row.exptxserno }}</template>
        </el-table-column>
        <el-table-column label="会员" width="150">
          <template #default="{ row }">{{ row.vcode || '--' }}</template>
        </el-table-column>
        <el-table-column label="日期" width="100">
          <template #default="{ row }">{{ row.vsdate || '--' }}</template>
        </el-table-column>
        <el-table-column label="时间" width="80">
          <template #default="{ row }">{{ row.vstime || '--' }}</template>
        </el-table-column>
        <el-table-column label="金额" width="100" align="right">
          <template #default="{ row }">¥{{ (row.totmount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="项目数" width="65" align="center">
          <template #default="{ row }">{{ row.itemcount || 0 }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusType(row.psstatus)" size="small">{{ statusLabel(row.psstatus) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="viewHung(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!hungList.length && !loading" description="暂无挂单数据" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '@/api/request'
import { searchVip as apiSearchVip } from '@/api/vip'
import { ElMessage } from 'element-plus'

const company = localStorage.getItem('genesis_pc_company') || ''
const storecode = localStorage.getItem('genesis_pc_storecode') || ''

const hungList = ref<any[]>([])
const loading = ref(false)
const vipKeyword = ref('')
const selectedVip = ref<any>(null)

const PSSTATUS_MAP: Record<string, { label: string; type: string }> = {
  '10': { label: '开单', type: 'info' },
  '20': { label: '到店', type: '' },
  '30': { label: '配料', type: '' },
  '40': { label: '服务完成', type: 'success' },
  '50': { label: '可结账', type: 'warning' },
  '60': { label: '挂账', type: 'warning' },
  '70': { label: '已结账', type: 'success' },
}

function statusLabel(s: string): string {
  return PSSTATUS_MAP[s]?.label || s || '--'
}
function statusType(s: string): string {
  return PSSTATUS_MAP[s]?.type || 'info'
}

async function fetchHungList() {
  loading.value = true
  try {
    const params: Record<string, string> = { company, storecode }
    if (selectedVip.value?.uuid) {
      params.vipuuid = selectedVip.value.uuid.replace(/-/g, '')
    }
    const res = await request.get('/adviser/get_hung_list/', { params })
    hungList.value = Array.isArray(res.data) ? res.data : []
  } catch { hungList.value = [] }
  finally { loading.value = false }
}

async function searchVip() {
  const kw = vipKeyword.value.trim()
  if (!kw) return
  try {
    const res = await apiSearchVip(kw)
    const list = (res.data as any)?.results ?? (Array.isArray(res.data) ? res.data : [])
    if (list.length === 1) {
      selectedVip.value = list[0]
      fetchHungList()
    } else if (list.length > 1) {
      ElMessage.info('找到多条记录，请输入更精确的关键字')
    } else {
      ElMessage.warning('未找到匹配会员')
    }
  } catch { ElMessage.error('查询失败') }
}

function clearFilter() {
  selectedVip.value = null
  vipKeyword.value = ''
  fetchHungList()
}

function viewHung(row: any) {
  ElMessage.info('挂单查看功能待实现')
}

onMounted(() => fetchHungList())
</script>
