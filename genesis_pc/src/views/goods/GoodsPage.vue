<template>
  <div class="goods-page">
    <div class="page-header" style="margin-bottom:12px">
      <h3 class="page-title">商品管理</h3>
    </div>
    <!-- 搜索工具栏 -->
    <div class="section filter-section">
      <div class="section-body">
        <el-form :inline="true" :model="query" size="default">
          <el-form-item label="关键字">
            <el-input
              v-model="query.keyword"
              placeholder="编码 / 名称 / 条码"
              clearable
              style="width: 200px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="品牌">
            <el-select v-model="query.brand" placeholder="全部品牌" clearable style="width: 140px" @change="handleSearch">
              <el-option v-for="b in brandOptions" :key="b.code" :label="b.name" :value="b.code" />
            </el-select>
          </el-form-item>
          <el-form-item label="分类">
            <el-select v-model="query.displayclass1" placeholder="全部分类" clearable style="width: 140px" @change="handleSearch">
              <el-option v-for="d in displayClassOptions" :key="d.code" :label="d.name" :value="d.code" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetQuery">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="section table-section">
      <div class="section-head">
        <span>商品列表</span>
        <el-button type="primary" size="small" @click="openAddDialog">新增商品</el-button>
      </div>

      <el-table :data="list" v-loading="loading" stripe highlight-current-row class="goods-table">
        <el-table-column prop="gcode" label="编码" width="120" />
        <el-table-column prop="gname" label="名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="brand" label="品牌" width="100" />
        <el-table-column prop="spec" label="规格" width="100" show-overflow-tooltip />
        <el-table-column label="售价" width="100">
          <template #default="{ row }">¥{{ Number(row.price ?? 0).toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="qty" label="库存" width="80" />
        <el-table-column prop="unit" label="单位" width="60" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <span class="status-dot" :class="row.saleflag === 'Y' ? 'dot-ok' : 'dot-muted'"></span>
            <el-tag :type="row.saleflag === 'Y' ? 'success' : 'info'" size="small">
              {{ row.saleflag === 'Y' ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
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
      :title="isEdit ? '编辑商品' : '新增商品'"
      width="720px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="90px"
        size="default"
      >
        <el-tabs type="border-card">
          <el-tab-pane label="基本信息">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="商品编码" prop="gcode">
                  <el-input v-model="form.gcode" placeholder="必填" :disabled="isEdit" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="商品名称" prop="gname">
                  <el-input v-model="form.gname" placeholder="必填" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="品牌">
                  <el-select v-model="form.brand" placeholder="选择品牌" clearable style="width: 100%" @change="onBrandChange">
                    <el-option v-for="b in brandOptions" :key="b.code" :label="b.name" :value="b.code" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="规格">
                  <el-input v-model="form.spec" placeholder="如 100ml" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="条码">
                  <el-input v-model="form.barcode" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="单位">
                  <el-select v-model="form.unit" placeholder="选择单位" clearable style="width: 100%">
                    <el-option label="个" value="10" />
                    <el-option label="瓶" value="20" />
                    <el-option label="盒" value="30" />
                    <el-option label="包" value="40" />
                    <el-option label="支" value="50" />
                    <el-option label="套" value="60" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="描述">
              <el-input v-model="form.desc1" placeholder="商品描述" />
            </el-form-item>
          </el-tab-pane>

          <el-tab-pane label="价格库存">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="售价">
                  <el-input-number v-model="form.price" :precision="2" :min="0" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="售价2">
                  <el-input-number v-model="form.price2" :precision="2" :min="0" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="售价3">
                  <el-input-number v-model="form.price3" :precision="2" :min="0" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="进价">
                  <el-input-number v-model="form.buyprc" :precision="2" :min="0" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="成本">
                  <el-input-number v-model="form.costprc" :precision="2" :min="0" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="数量">
                  <el-input-number v-model="form.qty" :precision="0" :min="0" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="最低库存">
                  <el-input-number v-model="form.minivalues" :precision="0" :min="0" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="最高库存">
                  <el-input-number v-model="form.maxvalues" :precision="0" :min="0" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="库位">
                  <el-input v-model="form.location" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="分类属性">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="显示分类1">
                  <el-select v-model="form.displayclass1" placeholder="选择" clearable style="width:100%">
                    <el-option v-for="d in displayClassOptions" :key="d.code" :label="d.name" :value="d.code" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="显示分类2">
                  <el-select v-model="form.displayclass2" placeholder="选择" clearable style="width:100%">
                    <el-option v-for="d in displayClass2Options" :key="d.code" :label="d.name" :value="d.code" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="营销分类1">
                  <el-input v-model="form.marketclass1" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="营销分类2">
                  <el-input v-model="form.marketclass2" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="折扣分类">
                  <el-input v-model="form.discountclass" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="商品分类">
                  <el-input v-model="form.goodsct" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="供应商">
                  <el-input v-model="form.supplierid" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>

          <el-tab-pane label="状态">
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="是否销售">
                  <el-switch v-model="saleflagVal" active-text="上架" inactive-text="下架" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="是否有效">
                  <el-switch v-model="valiflagVal" active-text="有效" inactive-text="无效" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-tab-pane>
        </el-tabs>
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
import { ref, reactive, computed, onMounted } from 'vue'
import {
  getGoodsList, createGoods, updateGoods, deleteGoods,
  getGoodsBrands, getGoodsDisplayClasses, getAppoptionBySeg,
} from '@/api/goods'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { Goods } from '@/types'

// ---- 列表数据 ----
const list = ref<Goods[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)

const query = reactive({
  keyword: '',
  brand: '',
  displayclass1: '',
})

// ---- 筛选选项 ----
const brandOptions = ref<Array<{ code: string; name: string }>>([])
const displayClassOptions = ref<Array<{ code: string; name: string }>>([])
const displayClass2Options = ref<Array<{ code: string; name: string }>>([])

async function fetchFilterOptions() {
  try {
    const brandRes = await getGoodsBrands()
    brandOptions.value = brandRes.data as any
  } catch { brandOptions.value = [] }
  try {
    const dc2Res = await getAppoptionBySeg('displayclass2')
    displayClass2Options.value = dc2Res.data.map(d => ({ code: d.itemname, name: d.itemvalues }))
  } catch { displayClass2Options.value = [] }
  try {
    const dc1Res = await getAppoptionBySeg('displayclass1')
    if (dc1Res.data.length > 0) {
      displayClassOptions.value = dc1Res.data.map(d => ({ code: d.itemname, name: d.itemvalues }))
    }
  } catch { /* ignore */ }
}

function onBrandChange(brand: string) {
  if (brand) {
    getGoodsDisplayClasses(brand).then(res => {
      if ((res.data as any).length > 0) displayClassOptions.value = res.data as any
    }).catch(() => {})
  }
}

// ---- 对话框 ----
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingUuid = ref('')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()
const saleflagVal = ref(true)
const valiflagVal = ref(true)

const emptyForm = () => ({
  gcode: '',
  gname: '',
  brand: '',
  spec: '',
  barcode: '',
  unit: '10',
  price: 0,
  price2: 0,
  price3: 0,
  buyprc: 0,
  costprc: 0,
  qty: 1,
  minivalues: 0,
  maxvalues: 10,
  displayclass1: '',
  displayclass2: '',
  marketclass1: '',
  marketclass2: '',
  discountclass: '',
  goodsct: '',
  saleflag: 'Y',
  valiflag: 'Y',
  supplierid: '',
  location: '',
  desc1: '',
})

const form = reactive<Record<string, any>>(emptyForm())

const formRules: FormRules = {
  gcode: [{ required: true, message: '请输入商品编码', trigger: 'blur' }],
  gname: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
}

// ---- 生命周期 ----
onMounted(() => {
  fetchList()
  fetchFilterOptions()
})

// ---- 方法 ----
function buildParams(): Record<string, any> {
  const params: Record<string, any> = { page: page.value, page_size: pageSize }
  if (query.keyword) params.search = query.keyword
  if (query.brand) params.brand = query.brand
  if (query.displayclass1) params.displayclass1 = query.displayclass1
  return params
}

async function fetchList() {
  loading.value = true
  try {
    const res = await getGoodsList(buildParams())
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
  query.brand = ''
  query.displayclass1 = ''
  page.value = 1
  fetchList()
}

// ---- 新增 ----
function openAddDialog() {
  isEdit.value = false
  editingUuid.value = ''
  saleflagVal.value = true
  valiflagVal.value = true
  Object.assign(form, emptyForm())
  formRef.value?.resetFields()
  dialogVisible.value = true
}

// ---- 编辑 ----
function openEditDialog(row: Goods) {
  isEdit.value = true
  editingUuid.value = row.uuid
  saleflagVal.value = row.saleflag === 'Y'
  valiflagVal.value = row.valiflag === 'Y'
  Object.assign(form, {
    gcode: row.gcode,
    gname: row.gname,
    brand: row.brand || '',
    spec: row.spec || '',
    barcode: row.barcode || '',
    unit: row.unit || '10',
    price: row.price ?? 0,
    price2: row.price2 ?? 0,
    price3: row.price3 ?? 0,
    buyprc: row.buyprc ?? 0,
    costprc: row.costprc ?? 0,
    qty: row.qty ?? 1,
    minivalues: row.minivalues ?? 0,
    maxvalues: row.maxvalues ?? 10,
    displayclass1: row.displayclass1 || '',
    displayclass2: row.displayclass2 || '',
    marketclass1: row.marketclass1 || '',
    marketclass2: row.marketclass2 || '',
    discountclass: row.discountclass || '',
    goodsct: row.goodsct || '',
    saleflag: 'Y',
    valiflag: 'Y',
    supplierid: row.supplierid || '',
    location: row.location || '',
    desc1: row.desc1 || '',
  })
  formRef.value?.clearValidate()
  dialogVisible.value = true
}

// ---- 提交 ----
async function handleSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const data = { ...form, saleflag: saleflagVal.value ? 'Y' : 'N', valiflag: valiflagVal.value ? 'Y' : 'N' }
    if (isEdit.value) {
      await updateGoods(editingUuid.value, data)
      ElMessage.success('保存成功')
    } else {
      await createGoods(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchList()
  } catch {
    // 拦截器已处理
  } finally {
    submitLoading.value = false
  }
}

// ---- 删除 ----
function handleDelete(row: Goods) {
  ElMessageBox.confirm(`确定删除商品「${row.gname}」吗？`, '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    await deleteGoods(row.uuid)
    ElMessage.success('已删除')
    if (list.value.length === 1 && page.value > 1) {
      page.value--
    }
    fetchList()
  }).catch(() => {})
}
</script>

<style scoped>
.goods-page { padding: 0; }
.filter-section { margin-bottom: 12px; }
.filter-section .section-body { padding: 10px 14px; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.goods-table { height: calc(100vh - 360px); width: 100%; }
.pagination-wrap {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
.status-dot.dot-ok { background: var(--g-color-success); }
.status-dot.dot-muted { background: var(--g-color-text-muted); }
</style>
