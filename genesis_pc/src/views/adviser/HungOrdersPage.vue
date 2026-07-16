<template>
  <div>
    <h2 style="margin:0 0 16px 0;font-size:18px;font-weight:600">已完成开单</h2>

    <!-- 状态筛选标签 -->
    <el-card shadow="never" style="margin-bottom:12px">
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
        <span style="font-size:13px;color:#606266;white-space:nowrap">状态：</span>
        <el-radio-group v-model="filterStatus" size="small" @change="fetchData">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="10">开单</el-radio-button>
          <el-radio-button value="40">服务完成</el-radio-button>
          <el-radio-button value="50">可结账</el-radio-button>
          <el-radio-button value="60">挂账</el-radio-button>
          <el-radio-button value="70">已结账</el-radio-button>
        </el-radio-group>

        <div style="flex:1" />

        <!-- 会员快捷筛选 -->
        <span style="font-size:13px;color:#606266;white-space:nowrap">会员：</span>
        <div class="vip-chips">
          <el-tag
            v-for="vip in vipList" :key="vip.vcode"
            :type="filterVip === vip.vcode ? 'primary' : 'info'"
            size="small"
            style="cursor:pointer;margin-right:4px"
            @click="toggleVipFilter(vip.vcode)"
          >
            {{ vip.vname }} ({{ vip.count }})
          </el-tag>
          <el-tag v-if="filterVip" type="danger" size="small" style="cursor:pointer" @click="filterVip = ''">
            清除筛选
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- 挂单列表 -->
    <el-card shadow="never">
      <el-table :data="hungList" size="small" stripe v-loading="loading" max-height="calc(100vh - 300px)"
        @row-click="selectRow" highlight-current-row>
        <el-table-column label="挂单号" width="170">
          <template #default="{ row }">{{ row.exptxserno }}</template>
        </el-table-column>
        <el-table-column label="会员" width="100">
          <template #default="{ row }">{{ row.vcode || '--' }}</template>
        </el-table-column>
        <el-table-column label="日期" width="90">
          <template #default="{ row }">{{ row.vsdate ? row.vsdate.slice(0,8) : '--' }}</template>
        </el-table-column>
        <el-table-column label="时间" width="70">
          <template #default="{ row }">{{ row.vstime || '--' }}</template>
        </el-table-column>
        <el-table-column label="金额" width="105" align="right">
          <template #default="{ row }">¥{{ (row.totmount || 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="项目数" width="60" align="center">
          <template #default="{ row }">{{ row.itemcount || 0 }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="statusType(row.psstatus)" size="small" effect="dark" style="cursor:pointer" @click="filterStatus = row.psstatus; fetchData()">
              {{ statusLabel(row.psstatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click.stop="viewHung(row)">明细</el-button>
            <el-button text type="success" size="small" @click.stop="continueBilling(row)">开单</el-button>
            <el-button v-if="row.psstatus !== '70'" text type="warning" size="small" @click.stop="checkout(row)">结账</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-card v-if="selectedOrder" shadow="never" style="margin-top:12px">
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span>明细 - {{ selectedOrder.exptxserno }}</span>
            <el-button text type="info" size="small" @click="selectedOrder = null; detailItems = []">关闭</el-button>
          </div>
        </template>
        <el-table :data="detailItems" size="small" stripe v-loading="detailLoading">
          <el-table-column label="项目" min-width="120">
            <template #default="{ row }">{{ row.itemname || row.srvcode || '--' }}</template>
          </el-table-column>
          <el-table-column label="类型" width="50">
            <template #default="{ row }">{{ row.ttypename }}</template>
          </el-table-column>
          <el-table-column label="单价" width="70" align="right">
            <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="数量" width="55" align="right">
            <template #default="{ row }">{{ row.qty }}</template>
          </el-table-column>
          <el-table-column label="金额" width="85" align="right">
            <template #default="{ row }">¥{{ row.mount.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="员工" width="130">
            <template #default="{ row }">{{ [row.pmcode, row.asscode1, row.asscode2].filter(Boolean).join(', ') || '--' }}</template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!detailItems.length && !detailLoading" description="无明细数据" />
      </el-card>

      <div v-if="stats.cardCount > 0" class="stats-bar">
        <span>共 <b>{{ stats.cardCount }}</b> 单，会员 <b>{{ stats.vipCount }}</b> 人，总计 <b>¥{{ stats.totalAmount.toFixed(2) }}</b></span>
      </div>
      <el-empty v-if="!hungList.length && !loading" description="暂无已完成开单" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/api/request'
import { ElMessage } from 'element-plus'

const router = useRouter()
const company = localStorage.getItem('genesis_pc_company') || ''
const storecode = localStorage.getItem('genesis_pc_storecode') || ''

const fullData = ref<any[]>([])
const selectedOrder = ref<any>(null)
const detailItems = ref<any[]>([])
const detailLoading = ref(false)

const hungList = computed(() => {
  if (!filterVip.value) return fullData.value
  return fullData.value.filter((h: any) => h.vcode === filterVip.value)
})

const loading = ref(false)
const filterStatus = ref('')
const filterVip = ref('')

const PSSTATUS_MAP: Record<string, { label: string; type: string }> = {
  '10': { label: '开单', type: 'info' },
  '20': { label: '到店', type: '' },
  '30': { label: '配料', type: '' },
  '40': { label: '服务完成', type: 'success' },
  '50': { label: '可结账', type: 'warning' },
  '60': { label: '挂账', type: 'warning' },
  '70': { label: '已结账', type: 'success' },
}

function statusLabel(s: string): string { return PSSTATUS_MAP[s]?.label || s || '--' }
function statusType(s: string): string { return PSSTATUS_MAP[s]?.type || 'info' }

// 从当前数据中提取 VIP 列表
const vipList = computed(() => {
  const map = new Map<string, { vcode: string; vname: string; count: number }>()
  for (const h of fullData.value) {
    const name = h.vname || h.vcode || ''
    if (!name) continue
    const key = name
    if (map.has(key)) {
      map.get(key)!.count++
    } else {
      map.set(key, { vcode: h.vcode || '', vname: name, count: 1 })
    }
  }
  return Array.from(map.values()).sort((a, b) => b.count - a.count)
})

const stats = computed(() => {
  const data = hungList.value
  const vips = new Set(data.map((h: any) => h.vcode))
  return {
    cardCount: data.length,
    vipCount: vips.size,
    totalAmount: data.reduce((s: number, h: any) => s + (h.totmount || 0), 0),
  }
})

function toggleVipFilter(vcode: string) {
  filterVip.value = filterVip.value === vcode ? '' : vcode
}

function removeVipFilter(vcode: string) {
  if (filterVip.value === vcode) filterVip.value = ''
}

async function fetchData() {
  loading.value = true
  try {
    const params: Record<string, string> = { company, storecode }
    if (filterStatus.value) {
      params.psstatus = filterStatus.value
    }
    const res = await request.get('/adviser/get_hung_list/', { params })
    fullData.value = Array.isArray(res.data) ? res.data : []
  } catch { fullData.value = [] }
  finally { loading.value = false }
}


async function selectRow(row: any) {
  if (selectedOrder.value?.uuid === row.uuid) {
    selectedOrder.value = null
    detailItems.value = []
    return
  }
  selectedOrder.value = row
  detailLoading.value = true
  try {
    const res = await request.get('/adviser/get_hung_detail/', { params: { hunguuid: row.uuid, company } })
    detailItems.value = Array.isArray(res.data) ? res.data : []
  } catch { detailItems.value = [] }
  finally { detailLoading.value = false }
}

function viewHung(row: any) {
  ElMessage.info('订单：' + row.exptxserno + ' 共 ' + row.itemcount + ' 项')
}

function continueBilling(row: any) {
  // 跳转到开单页并选中该会员
  router.push('/adviser/billing')
}

function checkout(row: any) {
  ElMessage.info('结账功能待实现')
}

onMounted(() => fetchData())
</script>

<style scoped>
.vip-chips { display:flex; flex-wrap:wrap; gap:4px; }
.stats-bar { margin-top:12px; padding:8px 12px; background:#f5f7fa; border-radius:6px; font-size:13px; color:#606266; }
</style>
