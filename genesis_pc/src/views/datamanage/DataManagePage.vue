<template>
  <div class="data-admin-page">
    <el-container style="height:100%">
      <!-- 左侧模块树 -->
      <el-aside width="220px" class="admin-sidebar">
        <div class="sidebar-title">数据管理</div>
        <el-menu
          :default-active="activeModelId"
          @select="onSelectModel"
          style="border-right: none"
        >
          <template v-for="group in modelGroups" :key="group.name">
            <el-sub-menu :index="group.name">
              <template #title>
                <span>{{ group.name }}</span>
              </template>
              <el-menu-item
                v-for="m in group.models"
                :key="m.id"
                :index="m.id"
              >
                <span>{{ m.verbose_name }}</span>
              </el-menu-item>
            </el-sub-menu>
          </template>
        </el-menu>
      </el-aside>

      <!-- 右侧内容区 -->
      <el-main class="admin-main">
        <template v-if="activeModelMeta">
          <!-- 表头 -->
          <div class="admin-toolbar">
            <h3 class="admin-title">{{ activeModelMeta.verbose_name_plural || activeModelMeta.verbose_name }}</h3>
            <div class="admin-toolbar-right">
              <el-input
                v-model="searchQuery"
                placeholder="搜索..."
                clearable
                style="width:200px"
                @clear="fetchData"
                @keyup.enter="fetchData"
              />
              <el-button type="primary" @click="openCreateDialog" :icon="Plus">新增</el-button>
              <el-button @click="fetchData" :icon="Refresh">刷新</el-button>
            </div>
          </div>

          <!-- 表格 -->
          <el-table :data="tableData" stripe border size="small" v-loading="loading" style="width:100%">
            <el-table-column
              v-for="col in visibleColumns"
              :key="col.name"
              :prop="col.name"
              :label="col.verbose_name"
              :width="getColumnWidth(col)"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <template v-if="col.type === 'BooleanField' || col.type === 'NullBooleanField'">
                  <el-tag :type="row[col.name] ? 'success' : 'info'" size="small">
                    {{ row[col.name] ? '是' : '否' }}
                  </el-tag>
                </template>
                <template v-else-if="col.choices">
                  {{ getChoiceLabel(col, row[col.name]) }}
                </template>
                <template v-else-if="col.type === 'DateField' || col.type === 'DateTimeField'">
                  {{ row[col.name] || '' }}
                </template>
                <template v-else>
                  {{ row[col.name] }}
                </template>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="openEditDialog(row)" :icon="Edit">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDelete(row)" :icon="Delete">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="admin-pagination" v-if="total > 0">
            <el-pagination
              v-model:current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              layout="total, prev, pager, next"
              @current-change="fetchData"
            />
          </div>
        </template>

        <!-- 未选择模块 -->
        <el-empty v-else description="请从左侧选择一个模块" />
      </el-main>
    </el-container>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="editingRow ? '编辑' : '新增' + ' - ' + (activeModelMeta?.verbose_name || '')"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" label-width="100px" size="small" v-loading="formLoading">
        <el-form-item
          v-for="field in formFields"
          :key="field.name"
          :label="field.verbose_name"
          :required="field.required"
          :prop="field.name"
        >
          <!-- 只读字段 -->
          <span v-if="field.read_only" style="color:#909399">{{ form[field.name] || '--' }}</span>

          <!-- Boolean -->
          <el-switch
            v-else-if="field.type === 'BooleanField' || field.type === 'NullBooleanField'"
            v-model="form[field.name]"
          />

          <!-- 枚举 -->
          <el-select
            v-else-if="field.choices"
            v-model="form[field.name]"
            placeholder="请选择"
            clearable
            style="width:100%"
          >
            <el-option
              v-for="c in field.choices"
              :key="c.value"
              :label="c.label"
              :value="c.value"
            />
          </el-select>

          <!-- 外键 -->
          <el-select
            v-else-if="field.related_model"
            v-model="form[field.name]"
            :placeholder="'选择' + (field.related_verbose || '')"
            filterable
            remote
            :remote-method="(q:string) => searchFk(field, q)"
            clearable
            style="width:100%"
            @focus="searchFk(field, '')"
          >
            <el-option
              v-for="opt in fkOptions[field.name] || []"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>

          <!-- Date -->
          <el-date-picker
            v-else-if="field.type === 'DateField'"
            v-model="form[field.name]"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width:100%"
          />

          <!-- DateTime -->
          <el-date-picker
            v-else-if="field.type === 'DateTimeField'"
            v-model="form[field.name]"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="选择日期时间"
            style="width:100%"
          />

          <!-- Text -->
          <el-input
            v-else-if="field.type === 'TextField' || (field.max_length && field.max_length > 200)"
            v-model="form[field.name]"
            type="textarea"
            :rows="3"
            :maxlength="field.max_length"
          />

          <!-- 数字 -->
          <el-input-number
            v-else-if="field.type === 'IntegerField' || field.type === 'DecimalField' || field.type === 'FloatField'"
            v-model="form[field.name]"
            :precision="field.type === 'IntegerField' ? 0 : 2"
            :min="0"
            style="width:100%"
          />

          <!-- 默认文本 -->
          <el-input
            v-else
            v-model="form[field.name]"
            :maxlength="field.max_length"
            :placeholder="'请输入' + field.verbose_name"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="saving">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { getModelGroups, getModelMeta, getModelData, createModelData, updateModelData, deleteModelData, searchRelated } from '@/api/sysadmin'

// ====== 状态 ======
const modelGroups = ref<Array<{name: string; models: Array<{id: string; verbose_name: string; icon: string}>}>>([])
const activeModelId = ref('')
const activeModelMeta = ref<any>(null)
const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')

// Form dialog
const formVisible = ref(false)
const editingRow = ref<any>(null)
const form = ref<Record<string, any>>({})
const saving = ref(false)
const formLoading = ref(false)
const fkOptions = ref<Record<string, Array<{value: string; label: string}>>>({})

// ====== 计算 ======
const visibleColumns = computed(() => {
  if (!activeModelMeta.value) return []
  const meta = activeModelMeta.value
  const skipFields = ['id', 'uuid', 'company', 'storecode', 'password', 'flag', 'status', 'create_time', 'last_modified', 'creater']
  return (meta.fields || []).filter((f: any) => !skipFields.includes(f.name) && !f.read_only && f.type !== 'AutoField' && f.type !== 'BigAutoField')
})

const formFields = computed(() => {
  if (!activeModelMeta.value) return []
  return (activeModelMeta.value.fields || []).filter((f: any) => !f.read_only && f.type !== 'AutoField' && f.type !== 'BigAutoField' && f.name !== 'company' && f.name !== 'storecode' && f.name !== 'create_time' && f.name !== 'last_modified' && f.name !== 'creater' && f.name !== 'flag')
})

// ====== 方法 ======
async function loadModels() {
  try {
    const res = await getModelGroups()
    console.log('[DataAdmin] models response:', res.data)
    modelGroups.value = res.data.groups || []
    console.log('[DataAdmin] modelGroups:', modelGroups.value.length, 'groups')
  } catch (e: any) {
    console.error('[DataAdmin] loadModels error:', e)
    ElMessage.error('加载模块列表失败')
  }
}

async function onSelectModel(id: string) {
  console.log('[DataAdmin] selectModel:', id)
  activeModelId.value = id
  const [appLabel, modelName] = id.split('.')
  try {
    const res = await getModelMeta(appLabel, modelName)
    console.log('[DataAdmin] meta response:', res.data)
    activeModelMeta.value = res.data
  } catch (e: any) {
    console.error('[DataAdmin] meta error:', e)
    ElMessage.error('加载字段元数据失败'); return
  }
  currentPage.value = 1
  searchQuery.value = ''
  console.log('[DataAdmin] fetching data...')
  await fetchData()
}

function getActiveIds() {
  if (!activeModelId.value) return { appLabel: '', modelName: '' }
  const [appLabel, modelName] = activeModelId.value.split('.')
  return { appLabel, modelName }
}

async function fetchData() {
  const { appLabel, modelName } = getActiveIds()
  if (!appLabel) { console.log('[DataAdmin] fetchData: no active model'); return }
  loading.value = true
  try {
    const params: Record<string, any> = { page: currentPage.value, page_size: pageSize.value }
    if (searchQuery.value) params.search = searchQuery.value
    console.log('[DataAdmin] fetchData:', appLabel, modelName, params)
    const res = await getModelData(appLabel, modelName, params)
    console.log('[DataAdmin] data response:', res.data)
    tableData.value = res.data.rows || []
    total.value = res.data.total || 0
  } catch (e: any) {
    console.error('[DataAdmin] data error:', e)
    ElMessage.error('加载数据失败')
  }
  finally { loading.value = false }
}

function getChoiceLabel(field: any, value: any) {
  if (!value && value !== false) return ''
  const choice = field.choices?.find((c: any) => c.value === String(value))
  return choice ? choice.label : value
}

function getColumnWidth(col: any) {
  if (col.type === 'BooleanField' || col.type === 'NullBooleanField') return 70
  if (col.type === 'IntegerField') return 80
  if (col.type === 'DecimalField' || col.type === 'FloatField') return 100
  if (col.type === 'DateTimeField' || col.type === 'DateField') return 120
  if (col.choices) return 100
  if (col.max_length && col.max_length > 50) return 150
  return 120
}

// ====== Form ======
function openCreateDialog() {
  editingRow.value = null
  form.value = {}
  formVisible.value = true
}

function openEditDialog(row: any) {
  editingRow.value = row
  form.value = { ...row }
  formVisible.value = true
}

function resetForm() {
  editingRow.value = null
  form.value = {}
  fkOptions.value = {}
}

async function searchFk(field: any, q: string) {
  if (!field.related_model) return
  try {
    const res = await searchRelated(field.related_model, q)
    fkOptions.value[field.name] = res.data.results || []
  } catch { fkOptions.value[field.name] = [] }
}

async function submitForm() {
  const { appLabel, modelName } = getActiveIds()
  if (!appLabel) return
  saving.value = true
  try {
    // 清理空字符串和 null
    const data: Record<string, any> = {}
    for (const [k, v] of Object.entries(form.value)) {
      if (v !== null && v !== undefined && v !== '') data[k] = v
    }
    if (editingRow.value) {
      await updateModelData(appLabel, modelName, editingRow.value.id || editingRow.value.pk, data)
      ElMessage.success('更新成功')
    } else {
      await createModelData(appLabel, modelName, data)
      ElMessage.success('新增成功')
    }
    formVisible.value = false
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.error || '操作失败')
  } finally { saving.value = false }
}

async function handleDelete(row: any) {
  const { appLabel, modelName } = getActiveIds()
  if (!appLabel) return
  try {
    await ElMessageBox.confirm('确定删除此记录？', '确认', { type: 'warning' })
    await deleteModelData(appLabel, modelName, row.id || row.pk)
    ElMessage.success('已删除')
    await fetchData()
  } catch {}
}

// ====== 生命周期 ======
onMounted(() => {
  loadModels()
})
</script>

<style scoped>
.data-admin-page { height: 100%; display: flex; }
.admin-sidebar { background: #fff; border-right: 1px solid #ebeef5; overflow-y: auto; }
.sidebar-title { padding: 16px; font-size: 15px; font-weight: 600; color: #303133; border-bottom: 1px solid #ebeef5; }
.admin-main { background: #f5f7fa; display: flex; flex-direction: column; }
.admin-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-shrink: 0; }
.admin-title { font-size: 16px; font-weight: 600; color: #303133; margin: 0; }
.admin-toolbar-right { display: flex; gap: 8px; }
.admin-pagination { display: flex; justify-content: flex-end; padding: 12px 0; flex-shrink: 0; }
</style>
