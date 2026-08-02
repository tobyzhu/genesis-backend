<template>
  <div class="vip-list">
    <!-- 搜索工具栏 -->
    <div class="section filter-section">
      <div class="filter-row">
        <h3 class="filter-title">会员管理</h3>
        <el-form :inline="true" :model="query" size="small">
          <el-form-item label="关键字">
            <el-input
              v-model="query.keyword"
              placeholder="姓名 / 手机号 / 会员号 / 拼音"
              clearable
              style="width: 220px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="等级">
            <el-select
              v-model="query.viplevel"
              placeholder="全部等级"
              clearable
              style="width: 140px"
            >
              <el-option
                v-for="opt in viplevelSelectOptions"
                :key="opt.itemname"
                :label="opt.itemvalues"
                :value="opt.itemname"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="类型">
            <el-select
              v-model="query.viptype"
              placeholder="全部"
              clearable
              style="width: 120px"
            >
              <el-option v-for="opt in viptypeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="primary" size="small" @click="openAddDialog">新增会员</el-button>
      </div>
      <div class="section-body letter-wrap">
        <div class="letter-bar">
          <span class="letter-label">拼音</span>
          <button
            v-for="l in letters"
            :key="l"
            class="letter-btn"
            :class="{ active: query.pinyin === l }"
            @click="pickLetter(l)"
          >{{ l }}</button>
        </div>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="section table-section">
      <div class="section-head">
        <span>会员列表</span>
        <span class="section-hint">{{ total }} 位会员</span>
      </div>

      <el-table :data="list" v-loading="loading" stripe highlight-current-row height="calc(100vh - 300px)">
        <el-table-column label="会员" width="120">
          <template #default="{ row }">
            <div class="member-cell">
              <div class="member-avatar">{{ (row.vname || '?').slice(0, 1) }}</div>
              <div class="member-info">
                <div class="member-name">
                  {{ row.vname || '--' }}
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="vcode" label="会员号" width="110" show-overflow-tooltip />
        <el-table-column prop="mtcode" label="手机号" width="130" show-overflow-tooltip />
        <el-table-column label="类型" width="70">
          <template #default="{ row }">{{ typeLabel(row) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" show-overflow-tooltip>
          <template #default="{ row }">{{ statusLabel(row) }}</template>
        </el-table-column>
        <el-table-column label="等级" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="levelType(row.viplevel)" effect="plain">{{ row.viplevel || '--' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="indate" label="入会日期" width="110" />
        <el-table-column prop="ecode" label="负责顾问" width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="$router.push(`/vip/${row.uuid}`)">
              详情
            </el-button>
            <el-button link type="primary" size="small" @click="openEditDialog(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchList"
        />
      </div>
    </div>

    <!-- 新增 / 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑会员' : '新增会员'"
      width="600px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="80px"
        size="default"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名" prop="vname">
              <el-input v-model="form.vname" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="mtcode">
              <el-input v-model="form.mtcode" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="sex">
              <el-radio-group v-model="form.sex">
                <el-radio value="男">男</el-radio>
                <el-radio value="女">女</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生日" prop="birth">
              <el-date-picker
                v-model="form.birth"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="会员等级" prop="viplevel">
              <el-select v-model="form.viplevel" placeholder="请选择等级" clearable style="width: 100%">
                <el-option v-for="opt in viplevelSelectOptions" :key="opt.itemname" :label="opt.itemvalues" :value="opt.itemname" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="会员类型" prop="viptype">
              <el-select v-model="form.viptype" placeholder="请选择" style="width: 100%">
                <el-option label="会员" value="10" />
                <el-option label="散客" value="20" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电话" prop="telph">
              <el-input v-model="form.telph" placeholder="座机号码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="微信" prop="wechat">
              <el-input v-model="form.wechat" placeholder="微信号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="地址" prop="addr">
          <el-input v-model="form.addr" placeholder="请输入地址" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="来源" prop="source">
              <el-select v-model="form.source" placeholder="请选择来店渠道" clearable style="width: 100%">
                <el-option v-for="opt in sourceOptions" :key="opt.itemname" :label="opt.itemvalues" :value="opt.itemname" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职业" prop="occupation">
              <el-input v-model="form.occupation" placeholder="职业" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="vdesc">
          <el-input
            v-model="form.vdesc"
            type="textarea"
            :rows="3"
            placeholder="备注信息"
          />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="formTags" multiple filterable allow-create clearable placeholder="选择或输入标签" style="width:100%">
            <el-option v-for="t in tagOptions" :key="t.itemname" :label="t.itemvalues" :value="t.itemname" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getVipList, createVip, updateVip, deleteVip, getVipFilterOptions, getAppoptionBySeg, getAppoptionBySegFor } from '@/api/vip'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { Vip } from '@/types'

// ---- 列表数据 ----
const list = ref<Vip[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)

const query = reactive({
  keyword: '',
  viplevel: '',
  viptype: '',
  pinyin: '',
})

const letters = ['全部', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')]

function pickLetter(l: string) {
  query.pinyin = l === '全部' ? '' : l
  page.value = 1
  fetchList()
}

function levelType(level: string) {
  const map: Record<string, any> = { A: 'success', B: 'primary', C: 'warning', D: 'info' }
  return map[level] || 'info'
}

function typeLabel(row: any) {
  return row.viptype_name || row.viptype || '--'
}

function statusLabel(row: any) {
  return row.status_name || row.status || '--'
}

// ---- 来源渠道选项 ----
const sourceOptions = ref<Array<{itemname: string, itemvalues: string}>>([])
async function fetchSourceOptions() {
  try {
    const res = await getAppoptionBySeg('source')
    sourceOptions.value = res.data
  } catch {
    sourceOptions.value = []
  }
}
function getSourceName(code: string): string {
  const found = sourceOptions.value.find(o => o.itemname === code)
  return found ? found.itemvalues : code
}

// ---- 会员等级选项 ----
const viplevelSelectOptions = ref<Array<{itemname: string, itemvalues: string}>>([])
const viptypeOptions = ref<Array<{label: string, value: string}>>([])
const tagOptions = ref<Array<{itemname: string, itemvalues: string}>>([])
const formTags = ref<string[]>([])
async function fetchViplevelSelectOptions() {
  try {
    const res = await getAppoptionBySeg('viplevel')
    viplevelSelectOptions.value = res.data
  } catch {
    viplevelSelectOptions.value = []
  }
}
async function fetchViptypeOptions() {
  try {
    const res = await getAppoptionBySegFor('common', 'viptype')
    viptypeOptions.value = (Array.isArray(res.data) ? res.data : []).map((o: any) => ({
      label: o.itemvalues,
      value: o.itemname,
    }))
  } catch {
    viptypeOptions.value = []
  }
}
async function fetchTagOptions() {
  try {
    const res = await getAppoptionBySeg('viptags')
    tagOptions.value = res.data
  } catch {
    tagOptions.value = []
  }
}

// ---- 对话框 ----
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingUuid = ref('')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const emptyForm = (): Partial<Vip> => ({
  vname: '',
  mtcode: '',
  sex: '男',
  birth: '',
  indate: '',
  viplevel: '',
  viptype: '10',
  telph: '',
  wechat: '',
  addr: '',
  source: '',
  occupation: '',
  vdesc: '',
  tags: '',
})

const form = reactive<Partial<Vip>>(emptyForm())

const formRules: FormRules = {
  vname: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  mtcode: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
}

// ---- 生命周期 ----
onMounted(() => {
  fetchList()
  fetchSourceOptions()
  fetchViplevelSelectOptions()
  fetchViptypeOptions()
  fetchTagOptions()
})

// ---- 方法 ----
function buildParams(): Record<string, any> {
  const params: Record<string, any> = { page: page.value, page_size: pageSize }
  if (query.keyword) params.search = query.keyword
  if (query.viplevel) params.viplevel = query.viplevel
  if (query.viptype) params.viptype = query.viptype
  if (query.pinyin) params.pinyin = query.pinyin
  return params
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getVipList(buildParams())
    list.value = res.data.results
    total.value = res.data.count
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchList()
}

function resetQuery() {
  query.keyword = ''
  query.viplevel = ''
  query.viptype = ''
  query.pinyin = ''
  page.value = 1
  fetchList()
}

// ---- 新增 ----
function openAddDialog() {
  isEdit.value = false
  editingUuid.value = ''
  Object.assign(form, emptyForm())
  formRef.value?.resetFields()
  dialogVisible.value = true
}

// ---- 编辑 ----
function openEditDialog(row: Vip) {
  isEdit.value = true
  editingUuid.value = row.uuid
  Object.assign(form, {
    vname: row.vname,
    mtcode: row.mtcode,
    sex: row.sex || '男',
    birth: row.birth || '',
    indate: row.indate || '',
    viplevel: row.viplevel,
    viptype: String(row.viptype || '10'),
    telph: row.telph || '',
    wechat: row.wechat || '',
    addr: row.addr || '',
    source: row.source || '',
    occupation: row.occupation || '',
    vdesc: row.vdesc || '',
  })
  formTags.value = (row.tags || '').split(',').filter(Boolean)
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

// ---- 提交 ----
async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const data = { ...form }
    if (isEdit.value) {
      data.tags = formTags.value.join(',')
      await updateVip(editingUuid.value, data)
      ElMessage.success('编辑成功')
    } else {
      data.tags = formTags.value.join(',')
      await createVip(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchList()
  } catch {
    // 错误已由拦截器统一提示
  } finally {
    submitLoading.value = false
  }
}

// ---- 删除 ----
function handleDelete(row: Vip) {
  ElMessageBox.confirm(`确定删除会员「${row.vname}」吗？`, '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    await deleteVip(row.uuid)
    ElMessage.success('已删除')
    // 如果当前页删空且非首页，回退一页
    if (list.value.length === 1 && page.value > 1) {
      page.value--
    }
    fetchList()
  }).catch(() => {
    // 用户取消
  })
}
</script>

<style scoped>
.vip-list {
  padding: 0;
}

.filter-section {
  margin-bottom: 8px;
}
.filter-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  padding: 8px 12px;
  border-bottom: 1px solid var(--g-color-border);
}
.filter-row .el-form {
  margin-bottom: 0;
}
.filter-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: var(--g-color-text);
}
.letter-wrap {
  padding: 6px 12px 10px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
.status-dot.dot-ok { background: var(--g-color-success); }
.status-dot.dot-muted { background: var(--g-color-text-muted); }
.letter-bar { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; }
.letter-label { font-size: 12px; color: var(--g-color-text-muted); margin-right: 4px; }
.letter-btn { min-width: 26px; height: 24px; padding: 0 6px; border: 1px solid var(--g-color-border); border-radius: var(--g-radius-sm); background: var(--g-color-surface); color: var(--g-color-text-secondary); font-size: 12px; cursor: pointer; transition: all 0.15s; }
.letter-btn:hover { border-color: var(--g-color-primary-border); color: var(--g-color-primary); }
.letter-btn.active { background: var(--g-color-primary); border-color: var(--g-color-primary); color: #fff; font-weight: 600; }
.member-cell { display: flex; align-items: center; gap: 8px; }
.member-avatar { width: 28px; height: 28px; border-radius: 50%; background: var(--g-color-primary-soft); color: var(--g-color-primary); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; flex-shrink: 0; }
.member-info { min-width: 0; }
.member-name { font-weight: 600; color: var(--g-color-text); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.table-section .section-head { padding: 8px 12px; }
.section-hint { font-size: 12px; font-weight: 400; color: var(--g-color-text-muted); }
.vip-list :deep(.el-table) { font-size: 12.5px; }
.vip-list :deep(.el-table .cell) { padding: 0 6px; }
</style>
