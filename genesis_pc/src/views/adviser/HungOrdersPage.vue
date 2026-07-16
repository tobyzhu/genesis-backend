<template>
  <div style="height:100%;display:flex;flex-direction:column">
    <h2 style="flex-shrink:0;margin:0 0 12px 0;font-size:18px;font-weight:600">开单管理</h2>

    <!-- 状态筛选标签 -->
    <el-card shadow="never" style="margin-bottom:12px;flex-shrink:0">
      <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap">
        <span style="font-size:13px;color:#606266;white-space:nowrap">状态：</span>
        <el-radio-group v-model="filterStatus" size="small" @change="onStatusChange">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button value="10">开单</el-radio-button>
          <el-radio-button value="40">服务完成</el-radio-button>
          <el-radio-button value="50">可结账</el-radio-button>
          <el-radio-button value="60">挂账</el-radio-button>
          <el-radio-button value="70">已结账</el-radio-button>
          <el-radio-button value="__void__">已作废</el-radio-button>
        </el-radio-group>
        <el-date-picker v-if="filterStatus === '70' || filterStatus === '__void__'" v-model="dateRange" type="daterange"
          range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"
          size="small" style="width:240px" value-format="YYYYMMDD"
          @change="fetchData" />

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
    <el-card shadow="never" class="hung-card" style="flex:1;min-height:0;display:flex;flex-direction:column">
      <div style="flex:5.5;min-height:0;overflow-y:auto" v-loading="loading">
      <div v-if="!hungList.length && !loading" style="padding:40px;text-align:center;color:#c0c4cc;font-size:14px">暂无开单管理</div>
      <div v-for="group in groupedByDate" :key="group.date" class="date-group">
        <div class="date-group-header">
          📅 <span style="font-weight:600">{{ formatDate(group.date) }}</span>
          <span class="date-count">{{ group.items.length }} 单</span>
        </div>
        <el-table :data="group.items" size="small" stripe
          @row-click="selectRow" :row-class-name="selectedRowClass">
          <el-table-column label="挂单号" width="170">
            <template #default="{ row }">{{ row.exptxserno }}</template>
          </el-table-column>
          <el-table-column label="会员" width="150">
            <template #default="{ row }">{{ row.vname || '--' }}<span style="color:#909399;font-size:11px;margin-left:4px">（{{ row.vcode || '' }}）</span></template>
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
          <el-table-column label="类型" width="55">
            <template #default="{ row }">{{ ttypeLabel(row.ttype) }}</template>
          </el-table-column>
          <el-table-column label="付款卡" width="120">
            <template #default="{ row }">{{ row.paycode || '--' }}</template>
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
              <el-button v-if="row.psstatus !== '70' && row.valiflag !== 'N'" text type="warning" size="small" @click.stop="checkout(row)">结账</el-button>
              <el-button v-if="row.psstatus !== '70' && row.valiflag !== 'N'" text type="danger" size="small" @click.stop="voidHung(row)">作废</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      </div>
      <el-card shadow="never" class="hung-detail-card" style="flex:4.5;min-height:0;display:flex;flex-direction:column;margin-top:12px">
        <template #header>
          <div style="display:flex;justify-content:space-between;align-items:center">
            <span>明细<span v-if="selectedOrder"> - {{ selectedOrder.exptxserno }}</span></span>
            <el-button text type="info" size="small" @click="selectedOrder = null; detailItems = []">关闭</el-button>
          </div>
        </template>
        <el-table :data="detailItems" size="small" stripe v-loading="detailLoading">
          <el-table-column label="项目" min-width="160">
            <template #default="{ row }">{{ row.itemname || '--' }}<span style="color:#909399;font-size:11px;margin-left:4px">（{{ row.srvcode || '' }}）</span></template>
          </el-table-column>
          <el-table-column label="类型" width="50">
            <template #default="{ row }">{{ row.ttypename }}</template>
          </el-table-column>
          <el-table-column label="属性" width="55">
            <template #default="{ row }">{{ row.stypename || row.stype || '--' }}</template>
          </el-table-column>
          <el-table-column label="单价" width="100" align="right">
            <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="数量" width="55" align="right">
            <template #default="{ row }">{{ row.qty }}</template>
          </el-table-column>
          <el-table-column label="金额" width="110" align="right">
            <template #default="{ row }">¥{{ row.mount.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="员工" min-width="280">
            <template #default="{ row }">
              <div style="display:flex;gap:4px;align-items:center;flex-wrap:wrap">
                <el-select v-model="row.pmcode" size="small" placeholder="开单" @change="saveEmp(row)" style="width:80px">
                  <el-option label="--" value="" />
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
                <el-select v-model="row.asscode1" size="small" placeholder="美1" @change="saveEmp(row)" style="width:80px">
                  <el-option label="--" value="" />
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
                <el-select v-model="row.asscode2" size="small" placeholder="美2" @change="saveEmp(row)" style="width:80px">
                  <el-option label="--" value="" />
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!detailItems.length && !detailLoading" :description="selectedOrder ? '无明细数据' : '请从上方选择一条挂单'" />
      </el-card>

      <div v-if="stats.cardCount > 0" class="stats-bar" style="flex-shrink:0">
        <span>共 <b>{{ stats.cardCount }}</b> 单，会员 <b>{{ stats.vipCount }}</b> 人，总计 <b>¥{{ stats.totalAmount.toFixed(2) }}</b></span>
      </div>
      <el-empty v-if="!hungList.length && !loading" description="暂无开单管理" style="flex-shrink:0" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/store/app'
import request from '@/api/request'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const appStore = useAppStore()
const hdsysuserid = appStore.user?.username || ''
const company = localStorage.getItem('genesis_pc_company') || ''
const storecode = localStorage.getItem('genesis_pc_storecode') || ''
const dateRange = ref<string[]>([])

const fullData = ref<any[]>([])
const selectedOrder = ref<any>(null)
const detailItems = ref<any[]>([])
const employees = ref<{ecode: string; ename: string}[]>([])
const detailLoading = ref(false)

const hungList = computed(() => {
  if (!filterVip.value) return fullData.value
  return fullData.value.filter((h: any) => h.vcode === filterVip.value)
})

function formatDate(s: string): string {
  if (!s || s.length < 8) return s || '--'
  return s.slice(0,4) + '-' + s.slice(4,6) + '-' + s.slice(6,8)
}

const groupedByDate = computed(() => {
  const map = new Map<string, any[]>()
  for (const h of hungList.value) {
    const d = (h.vsdate || '').slice(0, 8) || '未知'
    if (!map.has(d)) map.set(d, [])
    map.get(d)!.push(h)
  }
  return Array.from(map.entries())
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([date, items]) => ({ date, items }))
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
function ttypeLabel(t: string): string {
  const map: Record<string, string> = { S: '服务', G: '商品', C: '售卡', I: '充值' }
  return map[t] || t || '--'
}

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

function onStatusChange() {
  const fmt = (d: Date) => {
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return y + m + day
  }
  const today = fmt(new Date())
  if (filterStatus.value === '__void__') {
    dateRange.value = [today, today]
  } else if (filterStatus.value === '70') {
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 30)
    dateRange.value = [fmt(start), fmt(end)]
  }
  fetchData()
}

async function fetchData() {
  selectedOrder.value = null
  detailItems.value = []
  loading.value = true
  try {
    const params: Record<string, string> = { company, storecode }
    if (filterStatus.value) {
      params.psstatus = filterStatus.value
    }
    if (hdsysuserid) {
      params.hdsysuserid = hdsysuserid
    }
    if ((filterStatus.value === '70' || filterStatus.value === '__void__') && dateRange.value && dateRange.value.length === 2) {
      params.vsdate_from = dateRange.value[0]
      params.vsdate_to = dateRange.value[1]
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

function selectedRowClass({ row }: { row: any }): string {
  return selectedOrder.value?.uuid === row.uuid ? 'selected-row' : ''
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

onMounted(() => { fetchData(); fetchEmployees() })

async function fetchEmployees() {
  try {
    const res = await request.get('/adviser/get_bookingable_empllist/', { params: { company, storecode } })
    const list = Array.isArray(res.data) ? res.data : res.data?.results ?? []
    employees.value = list.map((e: any) => ({ ecode: e.ecode || '', ename: e.ename || '' }))
  } catch { employees.value = [] }
}

async function saveEmp(row: any) {
  if (!selectedOrder.value?.uuid) return
  try {
    await request.post('/adviser/update_hung_item_employees/', {
      hunguuid: selectedOrder.value.uuid,
      ditem: row.ditem,
      company,
      pmcode: row.pmcode || '',
      asscode1: row.asscode1 || '',
      asscode2: row.asscode2 || '',
    })
  } catch {}
}
async function voidHung(row: any) {
  try {
    await ElMessageBox.confirm('确认作废挂单「' + row.exptxserno + '」？此操作不可恢复。', '确认作废', { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' })
  } catch { return }
  try {
    const res = await request.post('/adviser/void_hung_order/', { hunguuid: row.uuid, company })
    if (res.data?.ok) {
      ElMessage.success('已作废')
      if (selectedOrder.value?.uuid === row.uuid) {
        selectedOrder.value = null
        detailItems.value = []
      }
      fetchData()
    } else {
      ElMessage.error(res.data?.message || '作废失败')
    }
  } catch (e: any) {
    ElMessage.error('作废失败: ' + (e?.message || String(e)))
  }
}

</script>

<style scoped>

.hung-card { flex:1; min-height:0; display:flex; flex-direction:column; }
.hung-card :deep(.el-card__body) { flex:1; min-height:0; display:flex; flex-direction:column; padding:12px; }
.hung-detail-card { display:flex; flex-direction:column; min-height:0; }
.hung-detail-card :deep(.el-card__body) { flex:1; min-height:0; display:flex; flex-direction:column; overflow:auto; }
.date-group { margin-bottom:10px; }
.date-group-header { padding:6px 10px; font-size:13px; color:#606266; background:#f5f7fa; border-radius:4px; margin-bottom:2px; display:flex; align-items:center; gap:6px; }
.date-count { font-weight:400; color:#909399; font-size:12px; margin-left:auto; }
:deep(.selected-row) { background-color: var(--el-table-current-row-bg-color, #ecf5ff); }
:deep(.selected-row td:first-child .cell)::before { content: "● "; color: #409eff; font-size:13px; font-weight:700; }
.vip-chips { display:flex; flex-wrap:wrap; gap:4px; }
.stats-bar { margin-top:12px; padding:8px 12px; background:#f5f7fa; border-radius:6px; font-size:13px; color:#606266; }
</style>
