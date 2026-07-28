<template>
  <div class="vip-list">
    <!-- 搜索区域 -->
    <el-card shadow="never" class="search-card">
      <el-form :inline="true" :model="query" size="default">
        <el-form-item label="关键字">
          <el-input
            v-model="query.keyword"
            placeholder="姓名 / 手机号 / 会员号"
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
              :key="lv"
              :label="lv"
              :value="lv"
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
            <el-option label="会员" value="10" />
            <el-option label="散客" value="20" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 表格区域 -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span>会员列表</span>
          <el-button type="primary" size="small" @click="openAddDialog">新增会员</el-button>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" stripe highlight-current-row>
        <el-table-column prop="vcode" label="会员号" width="120" />
        <el-table-column prop="vname" label="姓名" min-width="100" show-overflow-tooltip />
        <el-table-column prop="mtcode" label="手机号" width="130" />
        <el-table-column prop="viplevel" label="等级" width="80" />
        <el-table-column prop="sex" label="性别" width="60" />
        <el-table-column label="来源" width="100">
          <template #default="{ row }">
            {{ getSourceName(row.source) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80" />
        <el-table-column prop="indate" label="入会日期" width="110" />
        <el-table-column prop="birth" label="生日" width="70" />
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

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="fetchList"
        />
      </div>
    </el-card>

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
import { getVipList, createVip, updateVip, deleteVip, getVipFilterOptions, getAppoptionBySeg } from '@/api/vip'
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
})

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
  fetchTagOptions()
})

// ---- 方法 ----
function buildParams(): Record<string, any> {
  const params: Record<string, any> = { page: page.value, page_size: pageSize }
  if (query.keyword) params.search = query.keyword
  if (query.viplevel) params.viplevel = query.viplevel
  if (query.viptype) params.viptype = query.viptype
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

.search-card {
  margin-bottom: 12px;
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
</style>
