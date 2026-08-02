<template>
  <div class="campaign-page">
    <div class="campaign-top">
      <div class="campaign-title">
        <h3>营销活动</h3>
        <span class="campaign-sub">活动设定：特价 / 特殊折扣 / 组合销售</span>
      </div>
      <div class="campaign-filters">
        <el-select v-model="typeFilter" placeholder="活动大类" clearable size="default" style="width:150px" @change="applyFilters">
          <el-option v-for="t in mainttypeOptions" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
        <el-select v-model="statusFilter" placeholder="状态" clearable size="default" style="width:120px" @change="applyFilters">
          <el-option label="启用" value="active" />
          <el-option label="停用" value="inactive" />
        </el-select>
        <el-input
          v-model="keyword"
          placeholder="搜索编号/名称..."
          clearable
          style="width:220px"
          @keyup.enter="applyFilters"
          @clear="applyFilters"
        />
        <el-button type="primary" :icon="Plus" @click="openCreate">新增活动</el-button>
        <el-button :icon="Refresh" @click="fetchActivities">刷新</el-button>
      </div>
    </div>

    <div class="campaign-stats">
      <div class="stat-item">
        <span class="stat-value">{{ total }}</span>
        <span class="stat-label">活动总数</span>
      </div>
      <div class="stat-item">
        <span class="stat-value enabled">{{ enabledCount }}</span>
        <span class="stat-label">启用中</span>
      </div>
      <div class="stat-item">
        <span class="stat-value combo">{{ comboCount }}</span>
        <span class="stat-label">组合销售</span>
      </div>
    </div>

    <el-card shadow="never" class="campaign-card">
      <el-table :data="allRows" stripe border size="small" v-loading="loading" style="width:100%">
        <el-table-column label="活动编号" width="120">
          <template #default="{ row }">
            <span class="code-link" @click="openEdit(row)">{{ row.promotionsid || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="promotionsname" label="活动名称" min-width="160" show-overflow-tooltip />
        <el-table-column label="活动大类" width="120" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="mainttypeTag(row.mainttype)">{{ mainttypeName(row.mainttype) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small" :type="row.promotionsstatus === 'active' ? 'success' : 'info'">
              {{ row.promotionsstatus === 'active' ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="生效日期" width="180" align="center">
          <template #default="{ row }">
            <span v-if="row.fromdate || row.todate">{{ fmtDate(row.fromdate) }} ~ {{ fmtDate(row.todate) }}</span>
            <span v-else class="muted">不限</span>
          </template>
        </el-table-column>
        <el-table-column label="活动价" width="100" align="right">
          <template #default="{ row }">
            <span v-if="row.s_price != null">¥{{ Number(row.s_price).toFixed(2) }}</span>
            <span v-else class="muted">--</span>
          </template>
        </el-table-column>
        <el-table-column label="折扣率" width="90" align="center">
          <template #default="{ row }">
            {{ row.disc != null ? Number(row.disc).toFixed(2) : '--' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" :icon="View" circle @click="openPreview(row)" />
            <el-button size="small" :icon="Edit" circle @click="openEdit(row)" />
            <el-button size="small" type="danger" :icon="Delete" circle @click="handleDelete(row)" />
          </template>
        </el-table-column>
      </el-table>

      <div class="campaign-pagination">
        <el-pagination
          v-if="total > 0"
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          background
          @current-change="fetchActivities"
        />
      </div>
    </el-card>

    <!-- 新增/编辑活动 -->
    <el-dialog
      v-model="dialogVisible"
      :title="form.__pk ? '编辑活动' : '新增活动'"
      width="980px"
      top="4vh"
      :close-on-click-modal="false"
      @closed="resetDialog"
    >
      <el-form :model="form" label-width="90px" size="small">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="活动编号" required>
              <el-input v-model="form.promotionsid" placeholder="如 ACT001" maxlength="16" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="活动名称" required>
              <el-input v-model="form.promotionsname" placeholder="活动名称" maxlength="64" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="活动大类" required>
              <el-select v-model="form.mainttype" style="width:100%">
                <el-option v-for="t in mainttypeOptions" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="状态">
              <el-select v-model="form.promotionsstatus" style="width:100%">
                <el-option label="启用（开单可选）" value="active" />
                <el-option label="停用" value="" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="开始日期">
              <el-date-picker v-model="form.fromdate" type="date" value-format="YYYYMMDD" placeholder="开始日期" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="结束日期">
              <el-date-picker v-model="form.todate" type="date" value-format="YYYYMMDD" placeholder="结束日期" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="12">
          <el-col :span="6">
            <el-form-item label="活动售价">
              <el-input-number v-model="form.s_price" :min="0" :precision="2" :controls="false" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="折扣率">
              <el-input-number v-model="form.disc" :min="0" :max="1" :step="0.05" :precision="2" :controls="false" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="提成比例">
              <el-input-number v-model="form.emplperc" :min="0" :max="1" :step="0.05" :precision="2" :controls="false" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="活动组编号">
              <el-input
                :model-value="isGroupActivity ? groupForm.pgroupid : form.mainpgroupid"
                :placeholder="isGroupActivity ? '自动取自活动分组' : '不适用'"
                disabled
                maxlength="16"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div v-if="isGroupActivity" class="detail-section group-section">
        <el-form :model="groupForm" label-width="90px" size="small">
          <el-row :gutter="12">
            <el-col :span="6">
              <el-form-item label="分组编号" required>
                <el-input v-model="groupForm.pgroupid" placeholder="如 G001" maxlength="16" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="分组名称">
                <el-input v-model="groupForm.pgroupname" placeholder="分组名称" maxlength="128" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="分组类型">
                <el-select v-model="groupForm.pgrouptype" style="width:100%" placeholder="购买/赠送">
                  <el-option label="购买" value="BUY" />
                  <el-option label="赠送" value="SEND" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="状态">
                <el-input v-model="groupForm.status" placeholder="可选" maxlength="8" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="12">
            <el-col :span="6">
              <el-form-item label="开始日期">
                <el-date-picker v-model="groupForm.fromdate" type="date" value-format="YYYYMMDD" placeholder="开始日期" style="width:100%" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="结束日期">
                <el-date-picker v-model="groupForm.todate" type="date" value-format="YYYYMMDD" placeholder="结束日期" style="width:100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        <div class="detail-head">
          <span class="detail-title">分组明细</span>
          <span class="detail-hint">特价/特殊折扣活动通过活动分组生效</span>
          <el-button size="small" type="primary" :icon="Plus" @click="openItemPicker('group', true)">添加项目</el-button>
        </div>
        <el-table :data="groupRows" size="small" border>
          <el-table-column label="#" width="48" align="center">
            <template #default="{ $index }">{{ $index + 1 }}</template>
          </el-table-column>
          <el-table-column label="项目类型" width="90" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ ttypeLabel(row.ttype) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="项目" min-width="220">
            <template #default="{ row }">
              <div class="item-cell">
                <span class="item-cell-name" :class="{ empty: !row.pgcode }">
                  {{ row.pgcode ? itemName(row.pgcode, row.ttype) + ' (' + row.pgcode + ')' : '未选择项目' }}
                </span>
                <el-button size="small" text type="primary" @click="openItemPicker('group', false, row)">选择</el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="条件" width="120">
            <template #default="{ row }">
              <el-input v-model="row.pgroupcondition" size="small" placeholder="可选" />
            </template>
          </el-table-column>
          <el-table-column label="数量" width="80" align="center">
            <template #default="{ row }">
              <el-input-number v-model="row.qty1" :min="0" :precision="0" size="small" :controls="false" style="width:70px" @change="computeGroupAmount(row)" />
            </template>
          </el-table-column>
          <el-table-column label="活动价" width="100" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.price1" :min="0" :precision="2" size="small" :controls="false" style="width:80px" @change="computeGroupAmount(row)" />
            </template>
          </el-table-column>
          <el-table-column label="折扣" width="90" align="center">
            <template #default="{ row }">
              <el-input-number v-model="row.disc" :min="0" :max="1" :step="0.05" :precision="2" size="small" :controls="false" style="width:80px" />
            </template>
          </el-table-column>
          <el-table-column label="金额" width="100" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.amount1" :min="0" :precision="2" size="small" :controls="false" style="width:80px" />
            </template>
          </el-table-column>
          <el-table-column label="原价" width="100" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.oriprice" :min="0" :precision="2" size="small" :controls="false" style="width:80px" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button size="small" type="danger" :icon="Delete" circle @click="groupRows.splice($index, 1)" />
            </template>
          </el-table-column>
        </el-table>
        <div class="detail-summary">
          <span>分组总金额：<b>¥{{ groupTotal.toFixed(2) }}</b></span>
        </div>
      </div>

      <div v-else class="detail-section">
        <div class="detail-head">
          <span class="detail-title">活动明细</span>
          <span class="detail-hint">组合销售至少一条；特价/折扣明细会展示在手工开单的活动选择中</span>
          <el-button size="small" type="primary" :icon="Plus" @click="openItemPicker('detail', true)">添加项目</el-button>
        </div>
        <el-table :data="detailRows" size="small" border>
          <el-table-column label="#" width="48" align="center">
            <template #default="{ $index }">{{ $index + 1 }}</template>
          </el-table-column>
          <el-table-column label="项目类型" width="90" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">{{ ttypeLabel(row.ttype) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="项目" min-width="220">
            <template #default="{ row }">
              <div class="item-cell">
                <span class="item-cell-name" :class="{ empty: !row.sgcode }">
                  {{ row.sgcode ? itemName(row.sgcode, row.ttype) + ' (' + row.sgcode + ')' : '未选择项目' }}
                </span>
                <el-button size="small" text type="primary" @click="openItemPicker('detail', false, row)">选择</el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="数量" width="90" align="center">
            <template #default="{ row }">
              <el-input-number v-model="row.s_qty" :min="0" :precision="0" size="small" :controls="false" style="width:70px" @change="computeAmount(row)" />
            </template>
          </el-table-column>
          <el-table-column label="原价" width="100" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.s_price" :min="0" :precision="2" size="small" :controls="false" style="width:80px" @change="computeAmount(row)" />
            </template>
          </el-table-column>
          <el-table-column label="活动数量" width="100" align="center">
            <template #default="{ row }">
              <el-input-number v-model="row.promotionsqty" :min="0" :precision="0" size="small" :controls="false" style="width:80px" @change="computeAmount(row)" />
            </template>
          </el-table-column>
          <el-table-column label="活动价" width="100" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.promotionsprice" :min="0" :precision="2" size="small" :controls="false" style="width:80px" @change="computeAmount(row)" />
            </template>
          </el-table-column>
          <el-table-column label="活动金额" width="110" align="right">
            <template #default="{ row }">
              <el-input-number v-model="row.promotionsamount" :min="0" :precision="2" size="small" :controls="false" style="width:90px" />
            </template>
          </el-table-column>
          <el-table-column label="属性" width="80" align="center">
            <template #default="{ row }">
              <el-select v-model="row.stype" size="small" style="width:100%">
                <el-option label="正常" value="N" />
                <el-option label="赠送" value="P" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="60" align="center">
            <template #default="{ $index }">
              <el-button size="small" type="danger" :icon="Delete" circle @click="detailRows.splice($index, 1)" />
            </template>
          </el-table-column>
        </el-table>
        <div class="detail-summary">
          <span v-if="form.mainttype === '30'">组合总价：<b>¥{{ comboTotal.toFixed(2) }}</b></span>
          <span v-else>共 {{ detailRows.length }} 条明细</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveActivity">保存</el-button>
      </template>
    </el-dialog>

    <!-- 活动预览 -->
    <el-dialog v-model="previewVisible" title="活动预览" width="720px" top="6vh">
      <template v-if="previewData">
        <div class="preview-header">
          <div>
            <div class="preview-name">{{ previewData.promotionsname }}</div>
            <div class="preview-meta">{{ previewData.promotionsid }} · {{ mainttypeName(previewData.mainttype) }}</div>
          </div>
          <div class="preview-right">
            <el-tag :type="previewData.promotionsstatus === 'active' ? 'success' : 'info'" size="small">
              {{ previewData.promotionsstatus === 'active' ? '启用' : '停用' }}
            </el-tag>
          </div>
        </div>
        <div class="preview-info">
          <span>生效日期：{{ fmtDate(previewData.fromdate) }} ~ {{ fmtDate(previewData.todate) }}</span>
          <span v-if="previewData.s_price != null">活动售价：¥{{ Number(previewData.s_price).toFixed(2) }}</span>
          <span v-if="previewData.disc != null">折扣率：{{ Number(previewData.disc).toFixed(2) }}</span>
        </div>
        <el-table :data="previewItems" size="small" border>
          <el-table-column label="项目" min-width="180">
            <template #default="{ row }">{{ row.name }}</template>
          </el-table-column>
          <el-table-column label="类型" width="70" align="center">
            <template #default="{ row }">{{ ttypeLabel(row.ttype) }}</template>
          </el-table-column>
          <el-table-column label="数量" width="80" align="center">
            <template #default="{ row }">{{ row.qty }}</template>
          </el-table-column>
          <el-table-column label="活动价" width="100" align="right">
            <template #default="{ row }">¥{{ Number(row.price).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="金额" width="110" align="right">
            <template #default="{ row }">¥{{ Number(row.amount).toFixed(2) }}</template>
          </el-table-column>
        </el-table>
        <div class="preview-total" v-if="previewData.mainttype === '30'">
          组合总价：<b>¥{{ previewTotal.toFixed(2) }}</b>
        </div>
      </template>
    </el-dialog>

    <ItemPickerDialog v-model="itemPickerVisible" :multi="itemPickerMulti" @confirm="onItemPickerConfirm" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete, View } from '@element-plus/icons-vue'
import { getModelData, deleteModelData, getPromotionSetup, savePromotionSetup } from '@/api/sysadmin'
import ItemPickerDialog from '@/components/ItemPickerDialog.vue'

const mainttypeOptions = [
  { value: '10', label: '特价活动' },
  { value: '20', label: '特殊折扣活动' },
  { value: '30', label: '组合销售活动' },
]

const typeFilter = ref('')
const statusFilter = ref('')
const keyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const allRows = ref<any[]>([])
const loading = ref(false)

const dialogVisible = ref(false)
const saving = ref(false)
const form = ref<Record<string, any>>({})
const detailRows = ref<any[]>([])
const groupForm = ref<Record<string, any>>({})
const groupRows = ref<any[]>([])
const itemPickerVisible = ref(false)
const itemPickerMulti = ref(false)
const itemPickerTarget = ref<'detail' | 'group'>('detail')
const itemPickerRow = ref<any>(null)

const previewVisible = ref(false)
const previewData = ref<any>(null)
const previewItems = ref<any[]>([])

const itemPool = ref<Record<string, any[]>>({ S: [], G: [], C: [] })
const itemSearchOptions = ref<Record<string, any[]>>({ S: [], G: [], C: [] })
const itemSearching = ref(false)

const serverTotal = ref(0)
const enabledTotal = ref(0)
const comboTotalCount = ref(0)
const total = computed(() => serverTotal.value)
const enabledCount = computed(() => enabledTotal.value)
const comboCount = computed(() => comboTotalCount.value)

const comboTotal = computed(() => {
  return detailRows.value.reduce((s: number, r: any) => {
    const amt = Number(r.promotionsamount) || 0
    const qty = Number(r.promotionsqty) || Number(r.s_qty) || 0
    const price = Number(r.promotionsprice) || Number(r.s_price) || 0
    return s + (amt || qty * price)
  }, 0)
})

const isGroupActivity = computed(() => form.value.mainttype === '10' || form.value.mainttype === '20')

const groupTotal = computed(() => {
  return groupRows.value.reduce((s: number, r: any) => {
    const amt = Number(r.amount1) || 0
    const qty = Number(r.qty1) || 0
    const price = Number(r.price1) || 0
    return s + (amt || qty * price)
  }, 0)
})

const previewTotal = computed(() => {
  return previewItems.value.reduce((s: number, r: any) => s + (Number(r.amount) || 0), 0)
})

watch(() => form.value.mainttype, (v) => {
  if (v === '10' || v === '20') {
    if (!groupForm.value.pgrouptype) groupForm.value.pgrouptype = 'BUY'
    form.value.mainpgroupid = groupForm.value.pgroupid || ''
    if (!groupRows.value.length) addGroupRow()
  } else {
    form.value.mainpgroupid = ''
  }
})

function mainttypeName(v: string) {
  return mainttypeOptions.find(t => t.value === v)?.label || v || '-'
}

function mainttypeTag(v: string) {
  return ({ '10': 'success', '20': 'warning', '30': 'danger' } as Record<string, any>)[v || ''] || 'info'
}

function fmtDate(d: string) {
  return d && d.length === 8 ? `${d.slice(0, 4)}-${d.slice(4, 6)}-${d.slice(6, 8)}` : (d || '--')
}

function ttypeLabel(t: string) {
  return ({ S: '服务', G: '商品', C: '售卡', I: '充值' } as Record<string, string>)[t || ''] || t || '-'
}

async function fetchActivities() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value,
      ordering: '-create_time',
    }
    if (typeFilter.value) params.mainttype = typeFilter.value
    if (statusFilter.value === 'active') params.promotionsstatus = 'active'
    else if (statusFilter.value === 'inactive') params.promotionsstatus = '__blank__'
    if (keyword.value.trim()) params.search = keyword.value.trim()

    const [res, activeRes, comboRes] = await Promise.all([
      getModelData('baseinfo', 'promotions', params),
      getModelData('baseinfo', 'promotions', {
        page: 1, page_size: 1, promotionsstatus: 'active',
      }),
      getModelData('baseinfo', 'promotions', {
        page: 1, page_size: 1, mainttype: '30',
      }),
    ])
    allRows.value = res.data.rows || []
    serverTotal.value = res.data.total || 0
    enabledTotal.value = activeRes.data.total || 0
    comboTotalCount.value = comboRes.data.total || 0
  } catch {
    ElMessage.error('加载活动列表失败')
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  currentPage.value = 1
  fetchActivities()
}

function resetDialog() {
  form.value = {}
  detailRows.value = []
  groupForm.value = {}
  groupRows.value = []
}

function openCreate() {
  resetDialog()
  form.value = {
    __pk: '', promotionsid: '', promotionsname: '', mainttype: '30',
    promotionsstatus: 'active', fromdate: '', todate: '',
    s_price: 0, disc: 1, emplperc: 1, mainpgroupid: '', mainqty: 1, sendqty: 0,
  }
  addDetailRow()
  dialogVisible.value = true
}

async function openEdit(row: any) {
  resetDialog()
  form.value = {
    __pk: row.uuid || row.pk,
    promotionsid: row.promotionsid || '',
    promotionsname: row.promotionsname || '',
    mainttype: row.mainttype || '30',
    promotionsstatus: row.promotionsstatus || '',
    fromdate: row.fromdate || '',
    todate: row.todate || '',
    s_price: row.s_price != null ? Number(row.s_price) : 0,
    disc: row.disc != null ? Number(row.disc) : 1,
    emplperc: row.emplperc != null ? Number(row.emplperc) : 1,
    mainpgroupid: row.mainpgroupid || '',
    mainqty: row.mainqty != null ? Number(row.mainqty) : 1,
    sendqty: row.sendqty != null ? Number(row.sendqty) : 0,
  }
  try {
    const res = await getPromotionSetup(row.uuid)
    const data = res.data
    if (!data?.ok) throw new Error(data?.error || '活动配置加载失败')
    const p = data.promotion || {}
    form.value = {
      __pk: p.uuid || row.uuid,
      promotionsid: p.promotionsid || '',
      promotionsname: p.promotionsname || '',
      mainttype: p.mainttype || '30',
      promotionsstatus: p.promotionsstatus || '',
      fromdate: p.fromdate || '',
      todate: p.todate || '',
      s_price: p.s_price != null ? Number(p.s_price) : 0,
      disc: p.disc != null ? Number(p.disc) : 1,
      emplperc: p.emplperc != null ? Number(p.emplperc) : 1,
      mainpgroupid: p.mainpgroupid || '',
      mainqty: p.mainqty != null ? Number(p.mainqty) : 1,
      sendqty: p.sendqty != null ? Number(p.sendqty) : 0,
    }
    detailRows.value = (data.items || []).map((d: any) => ({
      __pk: '',
      ttype: d.ttype || 'S',
      sgcode: d.sgcode || '',
      s_qty: d.s_qty != null ? Number(d.s_qty) : 1,
      s_price: d.s_price != null ? Number(d.s_price) : 0,
      promotionsqty: d.promotionsqty != null ? Number(d.promotionsqty) : 1,
      promotionsprice: d.promotionsprice != null ? Number(d.promotionsprice) : 0,
      promotionsamount: d.promotionsamount != null ? Number(d.promotionsamount) : 0,
      stype: d.stype || 'N',
    }))
    if (data.group) {
      groupForm.value = {
        pgroupid: data.group.pgroupid || '',
        pgroupname: data.group.pgroupname || '',
        pgrouptype: data.group.pgrouptype || '',
        fromdate: data.group.fromdate || '',
        todate: data.group.todate || '',
        status: data.group.status || '',
      }
      form.value.mainpgroupid = data.group.pgroupid || ''
      groupRows.value = (data.group_items || []).map((d: any) => ({
        ttype: d.ttype || 'S',
        pgcode: d.pgcode || '',
        pgroupcondition: d.pgroupcondition || '',
        qty1: d.qty1 != null ? Number(d.qty1) : 1,
        price1: d.price1 != null ? Number(d.price1) : 0,
        disc: d.disc != null ? Number(d.disc) : null,
        amount1: d.amount1 != null ? Number(d.amount1) : 0,
        oriprice: d.oriprice != null ? Number(d.oriprice) : 0,
      }))
    }
    await Promise.all(
      detailRows.value.map((r: any) => ensureItemOption(r.ttype || 'S', r.sgcode || ''))
        .concat(groupRows.value.map((r: any) => ensureItemOption(r.ttype || 'S', r.pgcode || '')))
    )
  } catch {
    ElMessage.warning('活动配置加载失败')
  }
  if (isGroupActivity.value && !groupRows.value.length) addGroupRow()
  if (!isGroupActivity.value && !detailRows.value.length) addDetailRow()
  dialogVisible.value = true
}

function addDetailRow() {
  detailRows.value.push({
    __pk: '', ttype: 'S', sgcode: '',
    s_qty: 1, s_price: 0, promotionsqty: 1, promotionsprice: 0,
    promotionsamount: 0, stype: 'N',
  })
}

function addGroupRow() {
  groupRows.value.push({
    ttype: 'S', pgcode: '', pgroupcondition: '',
    qty1: 1, price1: 0, disc: null, amount1: 0, oriprice: 0,
  })
}

function onDetailTtypeChange(row: any) {
  if (row.sgcode && !itemPool.value[row.ttype]?.some((i: any) => i.code === row.sgcode)) {
    row.sgcode = ''
  }
  searchItems(row.ttype, '')
}

function onDetailItemChange(row: any, code: string) {
  const it = itemPool.value[row.ttype]?.find((i: any) => i.code === code)
  if (it) {
    row.s_price = it.price || row.s_price
    row.promotionsprice = it.price || row.promotionsprice
  }
  computeAmount(row)
}

function onGroupTtypeChange(row: any) {
  if (row.pgcode && !itemPool.value[row.ttype]?.some((i: any) => i.code === row.pgcode)) {
    row.pgcode = ''
  }
  searchItems(row.ttype, '')
}

function onGroupItemChange(row: any, code: string) {
  const it = itemPool.value[row.ttype]?.find((i: any) => i.code === code)
  if (it) {
    row.oriprice = it.price || row.oriprice
    if (!row.price1) row.price1 = it.price
  }
  computeGroupAmount(row)
}

function computeAmount(row: any) {
  const qty = Number(row.promotionsqty) || Number(row.s_qty) || 0
  const price = Number(row.promotionsprice) || Number(row.s_price) || 0
  row.promotionsamount = Math.round(qty * price * 100) / 100
}

function computeGroupAmount(row: any) {
  const qty = Number(row.qty1) || 0
  const price = Number(row.price1) || 0
  row.amount1 = Math.round(qty * price * 100) / 100
}

async function ensureItemOption(kind: string, code: string) {
  if (!code) return
  const pool = itemPool.value[kind]
  if (!pool || pool.some((i: any) => i.code === code)) return
  const model = kind === 'G' ? 'goods' : kind === 'C' ? 'cardtype' : 'serviece'
  const codeKey = kind === 'G' ? 'gcode' : kind === 'C' ? 'cardtype' : 'svrcdoe'
  const nameKey = kind === 'G' ? 'gname' : kind === 'C' ? 'cardname' : 'svrname'
  try {
    const res = await getModelData('baseinfo', model, {
      [codeKey]: code, page: 1, page_size: 5,
    })
    const row = res.data.rows?.[0]
    pool.push({
      code: row?.[codeKey] || code,
      name: row?.[nameKey] || code,
      price: Number(row?.price || 0),
    })
  } catch {
    pool.push({ code, name: code, price: 0 })
  }
}

function itemOptionsFor(kind: string) {
  const opts = itemSearchOptions.value[kind] && itemSearchOptions.value[kind].length
    ? [...itemSearchOptions.value[kind]]
    : [...itemPool.value[kind]]
  const selected = [
    ...detailRows.value
      .filter((r: any) => r.ttype === kind && r.sgcode)
      .map((r: any) => r.sgcode),
    ...groupRows.value
      .filter((r: any) => r.ttype === kind && r.pgcode)
      .map((r: any) => r.pgcode),
  ]
  for (const code of selected) {
    const it = itemPool.value[kind]?.find((i: any) => i.code === code)
    if (it && !opts.some((o: any) => o.code === code)) opts.push(it)
  }
  return opts
}

function openItemPicker(target: 'detail' | 'group', multi: boolean, row?: any) {
  itemPickerTarget.value = target
  itemPickerMulti.value = multi
  itemPickerRow.value = row || null
  itemPickerVisible.value = true
}

function ensurePoolItem(it: { ttype: string; code: string; name: string; price: number }) {
  const pool = itemPool.value[it.ttype] || []
  if (!pool.some((i: any) => i.code === it.code)) {
    pool.push({ code: it.code, name: it.name, price: it.price })
    itemPool.value[it.ttype] = pool
  }
}

function replaceGroupItem(row: any, it: { ttype: string; code: string; price: number }) {
  row.ttype = it.ttype
  row.pgcode = it.code
  row.oriprice = it.price || row.oriprice
  if (!row.price1) row.price1 = it.price
  computeGroupAmount(row)
}

function replaceDetailItem(row: any, it: { ttype: string; code: string; price: number }) {
  row.ttype = it.ttype
  row.sgcode = it.code
  row.s_price = it.price || row.s_price
  row.promotionsprice = it.price || row.promotionsprice
  computeAmount(row)
}

function onItemPickerConfirm(items: Array<{ ttype: string; code: string; name: string; price: number }>) {
  if (!items.length) return
  for (const it of items) ensurePoolItem(it)
  if (itemPickerRow.value) {
    const row = itemPickerRow.value
    if (itemPickerTarget.value === 'group') replaceGroupItem(row, items[0])
    else replaceDetailItem(row, items[0])
    itemPickerRow.value = null
    return
  }
  if (itemPickerTarget.value === 'group') {
    for (const it of items) {
      groupRows.value.push({
        ttype: it.ttype, pgcode: it.code, pgroupcondition: '',
        qty1: 1, price1: it.price, disc: null, amount1: it.price, oriprice: it.price,
      })
    }
  } else {
    for (const it of items) {
      detailRows.value.push({
        __pk: '', ttype: it.ttype, sgcode: it.code,
        s_qty: 1, s_price: it.price, promotionsqty: 1,
        promotionsprice: it.price, promotionsamount: it.price, stype: 'N',
      })
    }
  }
}

async function searchItems(kind: string, q: string) {
  const model = kind === 'G' ? 'goods' : kind === 'C' ? 'cardtype' : 'serviece'
  const codeKey = kind === 'G' ? 'gcode' : kind === 'C' ? 'cardtype' : 'svrcdoe'
  const nameKey = kind === 'G' ? 'gname' : kind === 'C' ? 'cardname' : 'svrname'
  itemSearching.value = true
  try {
    const params: Record<string, any> = { page: 1, page_size: q ? 50 : 200, ordering: codeKey }
    if (q) params.search = q
    const res = await getModelData('baseinfo', model, params)
    const rows = (res.data.rows || []).map((r: any) => ({
      code: r[codeKey] || '',
      name: r[nameKey] || r[codeKey] || '',
      price: Number(r.price || 0),
    }))
    const pool = itemPool.value[kind]
    const seen = new Set(pool.map((i: any) => i.code))
    for (const it of rows) {
      if (!seen.has(it.code)) {
        pool.push(it)
        seen.add(it.code)
      }
    }
    itemSearchOptions.value[kind] = rows
  } catch {
    itemSearchOptions.value[kind] = []
  } finally {
    itemSearching.value = false
  }
}

async function saveActivity() {
  const f = form.value
  if (!f.promotionsid?.trim() || !f.promotionsname?.trim() || !f.mainttype) {
    ElMessage.warning('请填写活动编号、名称和大类')
    return
  }
  if (isGroupActivity.value) {
    if (!groupForm.value.pgroupid?.trim()) {
      ElMessage.warning('请填写活动分组编号')
      return
    }
    if (!groupForm.value.pgrouptype) {
      ElMessage.warning('请选择活动分组类型（购买/赠送）')
      return
    }
    if (!groupRows.value.some((r: any) => r.pgcode)) {
      ElMessage.warning('活动分组至少需要一条明细')
      return
    }
  } else if (!detailRows.value.some((r: any) => r.sgcode)) {
    ElMessage.warning('组合销售活动至少需要一条明细')
    return
  }
  saving.value = true
  try {
    const payload: Record<string, any> = {
      uuid: f.__pk || '',
      promotionsid: f.promotionsid.trim(),
      promotionsname: f.promotionsname.trim(),
      mainttype: f.mainttype,
      promotionsstatus: f.promotionsstatus || '',
      fromdate: f.fromdate || '',
      todate: f.todate || '',
      s_price: f.s_price,
      disc: f.disc,
      emplperc: f.emplperc,
      mainqty: f.mainqty,
      sendqty: f.sendqty,
    }
    if (isGroupActivity.value) {
      payload.group = {
        pgroupid: groupForm.value.pgroupid.trim(),
        pgroupname: groupForm.value.pgroupname || '',
        pgrouptype: groupForm.value.pgrouptype || '',
        fromdate: groupForm.value.fromdate || '',
        todate: groupForm.value.todate || '',
        status: groupForm.value.status || '',
        items: groupRows.value
          .filter((r: any) => r.pgcode)
          .map((r: any, i: number) => ({
            pgroupitem: i + 1,
            pgroupcondition: r.pgroupcondition || '',
            ttype: r.ttype || 'S',
            pgcode: r.pgcode,
            qty1: r.qty1 ?? 1,
            price1: r.price1 ?? 0,
            disc: r.disc ?? null,
            amount1: r.amount1 ?? 0,
            oriprice: r.oriprice ?? 0,
          })),
      }
    } else {
      payload.items = detailRows.value
        .filter((r: any) => r.sgcode)
        .map((r: any, i: number) => ({
          ttype: r.ttype || 'S',
          sgcode: r.sgcode,
          s_qty: r.s_qty ?? 1,
          s_price: r.s_price ?? 0,
          promotionsqty: r.promotionsqty ?? 1,
          promotionsprice: r.promotionsprice ?? 0,
          promotionsamount: r.promotionsamount ?? 0,
          stype: r.stype || 'N',
          promotionsseq: String(i + 1).padStart(4, '0'),
        }))
    }
    const res = await savePromotionSetup(payload)
    if (!res.data?.ok) throw new Error(res.data?.message || '保存失败')
    ElMessage.success('活动已保存')
    dialogVisible.value = false
    await fetchActivities()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: any) {
  const pk = row.uuid || row.pk
  if (!pk) return
  try {
    await ElMessageBox.confirm(`确定删除活动「${row.promotionsname || row.promotionsid}」？`, '确认删除', { type: 'warning' })
    const detailRes = await getModelData('baseinfo', 'promotionsdetail', {
      promotionsuuid: pk, page: 1, page_size: 200,
    })
    for (const d of detailRes.data.rows || []) {
      await deleteModelData('baseinfo', 'promotionsdetail', d.uuid)
    }
    await deleteModelData('baseinfo', 'promotions', pk)
    ElMessage.success('已删除')
    await fetchActivities()
  } catch (e: any) {
    if (e !== 'cancel' && e !== 'close') {
      ElMessage.error(e?.response?.data?.error || e?.message || '删除失败')
    }
  }
}

async function openPreview(row: any) {
  previewData.value = row
  previewItems.value = []
  previewVisible.value = true
  try {
    const res = await getPromotionSetup(row.uuid)
    const data = res.data
    if (!data?.ok) throw new Error(data?.error || '活动配置加载失败')
    const groupItems = (data.group_items || []).map((d: any) => {
      const qty = Number(d.qty1) || 1
      const price = Number(d.price1) || 0
      const amt = Number(d.amount1) || qty * price
      return {
        name: itemName(d.pgcode || '', d.ttype || 'S'),
        ttype: d.ttype || 'S',
        qty,
        price,
        amount: amt,
      }
    })
    const detailItems = (data.items || []).map((d: any) => {
      const qty = Number(d.promotionsqty) || Number(d.s_qty) || 1
      const price = Number(d.promotionsprice) || Number(d.s_price) || 0
      const amt = Number(d.promotionsamount) || qty * price
      return {
        name: itemName(d.sgcode || '', d.ttype || 'S'),
        ttype: d.ttype || 'S',
        qty,
        price,
        amount: amt,
      }
    })
    previewItems.value = groupItems.length ? groupItems : detailItems
  } catch {
    previewItems.value = []
  }
}

function itemName(code: string, ttype: string) {
  const it = itemPool.value[ttype]?.find((i: any) => i.code === code)
  return it?.name || code || '--'
}

onMounted(async () => {
  await Promise.all([
    searchItems('S', ''),
    searchItems('G', ''),
    searchItems('C', ''),
  ])
  await fetchActivities()
})
</script>

<style scoped>
.campaign-page { height: 100%; display: flex; flex-direction: column; gap: 10px; }
.campaign-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; flex-shrink: 0; }
.campaign-title h3 { margin: 0; font-size: 16px; font-weight: 600; color: var(--g-color-text); }
.campaign-sub { margin-left: 10px; font-size: 12px; color: var(--g-color-text-muted); }
.campaign-filters { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.campaign-stats { display: flex; gap: 12px; flex-shrink: 0; }
.stat-item { flex: 1; min-width: 120px; padding: 10px 14px; background: var(--g-color-surface); border: 1px solid var(--g-color-border); border-radius: 6px; display: flex; flex-direction: column; gap: 2px; }
.stat-value { font-size: 20px; font-weight: 700; color: var(--g-color-text); }
.stat-value.enabled { color: var(--g-color-success); }
.stat-value.combo { color: var(--g-color-primary); }
.stat-label { font-size: 12px; color: var(--g-color-text-muted); }
.campaign-card { flex: 1; min-height: 0; }
.campaign-card :deep(.el-card__body) { padding: 10px; display: flex; flex-direction: column; }
.code-link { color: var(--g-color-primary); cursor: pointer; }
.code-link:hover { text-decoration: underline; }
.muted { color: var(--g-color-text-muted); }
.campaign-pagination { display: flex; justify-content: flex-end; padding-top: 10px; }
.detail-section { margin-top: 6px; border: 1px solid var(--g-color-border); border-radius: 6px; padding: 8px; background: var(--g-color-surface-muted); }
.detail-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.detail-title { font-size: 13px; font-weight: 600; color: var(--g-color-text); }
.detail-hint { flex: 1; font-size: 12px; color: var(--g-color-text-muted); }
.detail-summary { margin-top: 8px; text-align: right; font-size: 13px; color: var(--g-color-text-secondary); }
.detail-summary b { color: var(--g-color-money); }
.item-cell { display: flex; align-items: center; gap: 8px; min-width: 0; }
.item-cell-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: 13px; color: var(--g-color-text); }
.item-cell-name.empty { color: var(--g-color-text-muted); }
.preview-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 10px; }
.preview-name { font-size: 16px; font-weight: 600; color: var(--g-color-text); }
.preview-meta { margin-top: 4px; font-size: 12px; color: var(--g-color-text-muted); }
.preview-info { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 10px; font-size: 13px; color: var(--g-color-text-secondary); }
.preview-total { margin-top: 10px; text-align: right; font-size: 14px; color: var(--g-color-text-secondary); }
.preview-total b { color: var(--g-color-money); }
</style>
