<template>
  <div class="completed-orders-page">
    <div class="page-header" style="margin-bottom:12px">
      <h3 class="page-title">已完成开单</h3>
    </div>

    <!-- 搜索栏 -->
    <el-card shadow="never" class="search-card">
      <el-form :model="filters" size="small" layout="inline" class="search-form">
        <el-form-item label="日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYYMMDD"
            style="width:240px"
          />
        </el-form-item>
        <el-form-item label="客户搜索">
          <el-input
            v-model="filters.keyword"
            placeholder="姓名/手机号/会员号"
            clearable
            style="width:180px"
            @keyup.enter="search"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="search">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never" class="table-card">
      <el-table
        :data="orders"
        size="small"
        stripe
        v-loading="loading"
        @row-click="showDetail"
        style="cursor:pointer"
      >
        <el-table-column label="开单时间" width="140">
          <template #default="{ row }">{{ row.order_time }}</template>
        </el-table-column>
        <el-table-column label="客户" min-width="120">
          <template #default="{ row }">
            <div class="vip-cell">
              <span class="vip-name">{{ row.vname }}</span>
              <span class="vip-code">{{ row.vcode }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="手机号" width="120">
          <template #default="{ row }">{{ row.mtcode }}</template>
        </el-table-column>
        <el-table-column label="项目数" width="70" align="center">
          <template #default="{ row }">{{ row.item_count }}</template>
        </el-table-column>
        <el-table-column label="总金额" width="120" align="right">
          <template #default="{ row }">
            <span style="font-weight:600;color:var(--g-color-money)">¥{{ row.totmount.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="员工" width="100">
          <template #default="{ row }">{{ row.ecode_hung }}</template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="success">已完成</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="70" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click.stop="showDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-bar" v-if="total > 0">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          small
          @current-change="loadOrders"
        />
      </div>

      <el-empty v-if="!loading && !orders.length" description="暂无已完成开单" />
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="showDetailDialog" title="开单详情" width="700px" top="5vh">
      <template v-if="detailData">
        <div class="detail-header">
          <div class="dh-row">
            <span class="dh-label">客户：</span>
            <span class="dh-value">{{ detailData.hung.vname }} ({{ detailData.hung.vcode }})</span>
            <span class="dh-label" style="margin-left:24px">手机：</span>
            <span class="dh-value">{{ detailData.hung.mtcode }}</span>
          </div>
          <div class="dh-row">
            <span class="dh-label">开单时间：</span>
            <span class="dh-value">{{ detailData.hung.order_time }}</span>
            <span class="dh-label" style="margin-left:24px">单据号：</span>
            <span class="dh-value">{{ detailData.hung.exptxserno }}</span>
          </div>
          <div class="dh-row">
            <span class="dh-label">员工：</span>
            <span class="dh-value">{{ detailData.hung.ecode_hung || '--' }}</span>
            <span class="dh-label" style="margin-left:24px">备注：</span>
            <span class="dh-value">{{ detailData.hung.remark || '--' }}</span>
          </div>
        </div>

        <el-divider style="margin:12px 0" />

        <h4 style="margin:0 0 8px 0;font-size:14px">项目明细</h4>
        <el-table :data="detailData.items" size="small" stripe>
          <el-table-column label="项目" min-width="130">
            <template #default="{ row }">{{ row.itemname }}</template>
          </el-table-column>
          <el-table-column label="类型" width="60">
            <template #default="{ row }">{{ row.ttypename }}</template>
          </el-table-column>
          <el-table-column label="属性" width="60">
            <template #default="{ row }">{{ row.stypename }}</template>
          </el-table-column>
          <el-table-column label="数量" width="60" align="right">
            <template #default="{ row }">{{ row.qty }}</template>
          </el-table-column>
          <el-table-column label="单价" width="100" align="right">
            <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="折扣率" width="70" align="right">
            <template #default="{ row }">{{ (row.secdisc * 100).toFixed(0) }}%</template>
          </el-table-column>
          <el-table-column label="金额折扣" width="80" align="right">
            <template #default="{ row }">¥{{ row.srvmondisc.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="小计" width="100" align="right">
            <template #default="{ row }">
              <span style="font-weight:600;color:var(--g-color-money)">¥{{ row.amount.toFixed(2) }}</span>
            </template>
          </el-table-column>
        </el-table>

        <div class="detail-total">
          <span>合计：</span>
          <span class="total-amount">¥{{ detailData.hung.totmount.toFixed(2) }}</span>
        </div>
      </template>
      <div v-else class="detail-loading">
        <el-icon class="is-loading" :size="24"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { getCompletedHungs, getCompletedOrderDetail } from '@/api/cashier'

const loading = ref(false)
const orders = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const dateRange = ref<string[]>([todayStr(), todayStr()])
const filters = ref({
  keyword: '',
})

const showDetailDialog = ref(false)
const detailData = ref<any>(null)

function todayStr(): string {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}${m}${day}`
}

function loadOrders() {
  loading.value = true
  const params: Record<string, any> = {
    page: page.value,
    page_size: pageSize.value,
  }
  if (dateRange.value && dateRange.value.length === 2) {
    params.date_from = dateRange.value[0]
    params.date_to = dateRange.value[1]
  }
  if (filters.value.keyword) {
    params.keyword = filters.value.keyword.trim()
  }

  getCompletedHungs(params)
    .then((res: any) => {
      if (res.data?.ok) {
        orders.value = res.data.rows || []
        total.value = res.data.total || 0
      } else {
        orders.value = []
        total.value = 0
      }
    })
    .catch(() => {
      ElMessage.error('获取已完成开单列表失败')
      orders.value = []
      total.value = 0
    })
    .finally(() => {
      loading.value = false
    })
}

function search() {
  page.value = 1
  loadOrders()
}

function resetFilters() {
  dateRange.value = [todayStr(), todayStr()]
  filters.value.keyword = ''
  page.value = 1
  loadOrders()
}

async function showDetail(row: any) {
  showDetailDialog.value = true
  detailData.value = null
  try {
    const res = await getCompletedOrderDetail(row.hunguuid)
    if (res.data?.ok) {
      detailData.value = {
        hung: res.data.hung,
        items: res.data.items || [],
      }
    } else {
      ElMessage.error(res.data?.message || '获取详情失败')
      showDetailDialog.value = false
    }
  } catch {
    ElMessage.error('获取开单详情失败')
    showDetailDialog.value = false
  }
}

onMounted(() => {
  loadOrders()
})
</script>

<style scoped>
.completed-orders-page { padding: 0; }

.search-card { margin-bottom: 12px; }
.search-card :deep(.el-card__body) { padding: 12px 16px; }
.search-form { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; }
.search-form .el-form-item { margin-bottom: 0; }

.table-card { }
.table-card :deep(.el-card__body) { padding: 0; }
.pagination-bar { display: flex; justify-content: flex-end; padding: 12px 16px; }

.vip-cell { display: flex; flex-direction: column; }
.vip-name { font-weight: 500; font-size: 13px; }
.vip-code { font-size: 11px; color: var(--g-color-text-muted); }

.detail-header { padding: 0 4px; }
.dh-row { margin-bottom: 6px; font-size: 13px; }
.dh-label { color: var(--g-color-text-muted); }
.dh-value { color: var(--g-color-text); font-weight: 500; }

.detail-total { display: flex; justify-content: flex-end; align-items: center; gap: 8px; margin-top: 12px; font-size: 16px; }
.total-amount { font-size: 20px; font-weight: 700; color: var(--g-color-money); }

.detail-loading { display: flex; flex-direction: column; align-items: center; gap: 8px; padding: 40px; color: var(--g-color-text-muted); }
</style>
