<template>
  <div class="goods-admin">
    <el-container style="height:100%">
      <!-- 左侧分类树 -->
      <el-aside width="240px" class="tree-sidebar">
        <div class="sidebar-header">
          <span>商品大类</span>
          <el-button size="small" :icon="Plus" circle @click="openCategoryDialog()" />
        </div>
        <el-input
          v-model="treeFilter"
          placeholder="搜索分类..."
          clearable
          size="small"
          style="margin:8px 10px;width:calc(100% - 20px)"
        />
        <el-tree
          ref="treeRef"
          :data="treeData"
          :props="{ label: 'goodsctname', children: 'children' }"
          :filter-node-method="filterTreeNode"
          node-key="goodsct"
          highlight-current
          default-expand-all
          @node-click="onNodeClick"
          style="padding:0 8px"
        >
          <template #default="{ data }">
            <div class="tree-node-row">
              <span class="tree-node-label">{{ data.goodsctname || data.goodsct || '(未命名)' }}</span>
              <span class="tree-node-actions">
                <el-button size="small" :icon="Edit" circle @click.stop="openCategoryDialog(data)" />
                <el-button size="small" type="danger" :icon="Delete" circle @click.stop="handleDeleteCategory(data)" />
              </span>
            </div>
          </template>
        </el-tree>
      </el-aside>

      <!-- 右侧商品列表 -->
      <el-main class="list-main">
        <div class="list-toolbar">
          <h3 style="margin:0;font-size:15px;font-weight:600">
            {{ selectedCategory || '全部' }} <span style="font-size:12px;color:#909399;font-weight:400">商品</span>
            <span style="font-weight:400;color:#909399;font-size:13px;margin-left:8px">共 {{ total }} 项</span>
          </h3>
          <div style="display:flex;gap:8px;align-items:center">
            <el-select v-model="brandFilter" placeholder="品牌" clearable size="default" style="width:130px" @change="() => fetchItems(true)">
              <el-option v-for="b in brandOptions" :key="b.value" :label="b.label" :value="b.value" />
            </el-select>
            <el-select v-model="displayClassFilter" placeholder="显示分类" clearable size="default" style="width:120px" @change="() => fetchItems(true)">
              <el-option v-for="d in displayClassOptions" :key="d.value" :label="d.label" :value="d.value" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="状态" clearable size="default" style="width:90px" @change="() => fetchItems()">
              <el-option label="有效" value="Y" />
              <el-option label="无效" value="N" />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索编码/名称..."
              clearable
              style="width:180px"
              @clear="() => fetchItems()"
              @keyup.enter="() => fetchItems()"
            />
            <el-button type="primary" :icon="Plus" @click="openGoodsDialog()">新增</el-button>
            <el-button @click="() => fetchItems(true)" :icon="Refresh">刷新</el-button>
          </div>
        </div>

        <el-table :data="items" stripe border size="small" v-loading="loading" style="width:100%">
          <el-table-column label="分类" width="100" show-overflow-tooltip>
            <template #default="{row}">{{ categoryNameMap[row.goodsct] || '-' }}</template>
          </el-table-column>
          <el-table-column label="编码" width="90">
            <template #default="{row}">
              <span class="code-link" @click="openGoodsDialog(row)">{{ row.gcode }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="gname" label="名称" min-width="150" show-overflow-tooltip />
          <el-table-column prop="spec" label="规格" width="80" show-overflow-tooltip />
          <el-table-column label="品牌" width="90" show-overflow-tooltip>
            <template #default="{row}">{{ brandNameMap[row.brand] || row.brand || '-' }}</template>
          </el-table-column>
          <el-table-column label="售价" width="90" align="right">
            <template #default="{row}">¥{{ (row.price || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="进价" width="80" align="right">
            <template #default="{row}">¥{{ (row.buyprc || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="qty" label="库存" width="70" align="center" />
          <el-table-column label="可销售" width="65" align="center">
            <template #default="{row}">{{ row.saleflag === 'Y' ? '✅' : '❌' }}</template>
          </el-table-column>
          <el-table-column label="有效" width="65" align="center">
            <template #default="{row}">{{ row.valiflag === 'Y' ? '✅' : '❌' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{row}">
              <el-button size="small" :icon="Edit" @click="openGoodsDialog(row)" circle />
              <el-button size="small" type="danger" :icon="Delete" @click="handleDeleteGoods(row)" circle />
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-if="total > 0"
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="() => fetchItems()"
          style="margin-top:12px;justify-content:flex-end"
        />
      </el-main>
    </el-container>

    <!-- 分类编辑弹窗 -->
    <el-dialog v-model="categoryVisible" :title="categoryForm.pk ? '编辑分类' : '新增分类'" width="420px">
      <el-form :model="categoryForm" label-width="80px" size="small">
        <el-form-item label="分类编号" required>
          <el-input v-model="categoryForm.goodsct" :disabled="!!categoryForm.pk" placeholder="如 01, 02" />
        </el-form-item>
        <el-form-item label="分类名称" required>
          <el-input v-model="categoryForm.goodsctname" placeholder="如 护肤品" />
        </el-form-item>
        <el-form-item label="上级分类">
          <el-select v-model="categoryForm.parent" clearable placeholder="无（一级分类）" style="width:100%">
            <el-option v-for="c in flatCategories" :key="c.goodsct" :label="c.goodsctname" :value="c.goodsct" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryVisible = false">取消</el-button>
        <el-button type="danger" v-if="categoryForm.pk" @click="handleDeleteCategory()">删除</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>

    <!-- 商品编辑弹窗 -->
    <el-dialog v-model="goodsVisible" :title="goodsForm.gcode ? '编辑商品' : '新增商品'" width="700px" top="5vh">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="goodsForm" label-width="100px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="编码" required>
                  <el-input v-model="goodsForm.gcode" placeholder="商品编码" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="名称" required>
                  <el-input v-model="goodsForm.gname" placeholder="商品名称" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="商品大类" required>
                  <el-select v-model="goodsForm.goodsct" placeholder="选择分类" style="width:100%">
                    <el-option v-for="c in flatCategories" :key="c.goodsct" :label="c.goodsctname" :value="c.goodsct" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="品牌">
                  <el-select v-model="goodsForm.brand" clearable placeholder="选择品牌" style="width:100%">
                    <el-option v-for="b in brandOptions" :key="b.value" :label="b.label" :value="b.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="规格">
                  <el-input v-model="goodsForm.spec" placeholder="如 30ml, 500g" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="单位">
                  <el-input v-model="goodsForm.unit" placeholder="如 瓶, 盒" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="售价">
                  <el-input-number v-model="goodsForm.price" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="进价">
                  <el-input-number v-model="goodsForm.buyprc" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="条码">
                  <el-input v-model="goodsForm.barcode" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="库存数量">
                  <el-input-number v-model="goodsForm.qty" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="最低库存">
                  <el-input-number v-model="goodsForm.minivalues" :min="0" :precision="0" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="最高库存">
                  <el-input-number v-model="goodsForm.maxvalues" :min="0" :precision="0" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="价格设定" name="prices">
          <el-form :model="goodsForm" label-width="100px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="第二价格">
                  <el-input-number v-model="goodsForm.price2" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="第三价格">
                  <el-input-number v-model="goodsForm.price3" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="第四价格">
                  <el-input-number v-model="goodsForm.price4" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="币别">
                  <el-select v-model="goodsForm.pricecurrency" style="width:100%">
                    <el-option label="RMB" value="RMB" />
                    <el-option label="USD" value="USD" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="分类设定" name="categories">
          <el-form :model="goodsForm" label-width="110px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="显示分类1">
                  <el-select v-model="goodsForm.displayclass1" clearable style="width:100%">
                    <el-option v-for="d in displayClassOptions" :key="d.value" :label="d.label" :value="d.value" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="显示分类2">
                  <el-select v-model="goodsForm.displayclass2" clearable style="width:100%">
                    <el-option v-for="d in displayClassOptions" :key="d.value" :label="d.label" :value="d.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="折扣分类">
                  <el-select v-model="goodsForm.discountclass" clearable style="width:100%">
                    <el-option label="标准折扣" value="A" />
                    <el-option label="特殊折扣" value="B" />
                    <el-option label="无折扣" value="C" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="销售渠道">
                  <el-input v-model="goodsForm.saleschannels" placeholder="如 10,20" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="营销分类1">
                  <el-input v-model="goodsForm.marketclass1" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="营销分类2">
                  <el-input v-model="goodsForm.marketclass2" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="提成设定" name="commission">
          <el-form :model="goodsForm" label-width="140px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="顾问提成率">
                  <el-input-number v-model="goodsForm.pmperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="顾问拆分率">
                  <el-input-number v-model="goodsForm.pmguideperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="美疗师1提成率">
                  <el-input-number v-model="goodsForm.secperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="美疗师1拆分率">
                  <el-input-number v-model="goodsForm.secguideperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="业绩固定成本扣除">
              <el-input-number v-model="goodsForm.achivementcost" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="控制设定" name="controls">
          <el-form :model="goodsForm" label-width="110px" size="small">
            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item label="可销售">
                  <el-switch v-model="goodsForm.saleflag" active-value="Y" inactive-value="N" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="有效">
                  <el-switch v-model="goodsForm.valiflag" active-value="Y" inactive-value="N" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="可改价格">
                  <el-switch v-model="goodsForm.pricechangeable" active-value="Y" inactive-value="N" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="估计使用天数">
              <el-input-number v-model="goodsForm.intervalday" :min="0" :precision="0" style="width:100%" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="goodsVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingGoods" @click="saveGoods">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import {
  getGoodsctTree, saveGoodsct, deleteGoodsct, getGoodsFastList, getAppOptionList
} from '@/api/goods-admin'
import { createModelData, updateModelData } from '@/api/sysadmin'

// ====== 分类树 ======
const treeData = ref<Array<Record<string, any>>>([])
const treeFilter = ref('')
const treeRef = ref<any>(null)
const selectedCategory = ref('')
const selectedGoodsct = ref('')
const uncategorizedOnly = ref(false)

// ====== 列表 ======
const items = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const brandFilter = ref('')
const displayClassFilter = ref('')
const statusFilter = ref('')
const listCache = new Map<string, any>()

// ====== 选项 ======
const brandOptions = ref<Array<{value: string; label: string}>>([])
const displayClassOptions = ref<Array<{value: string; label: string}>>([])

// ====== 分类弹窗 ======
const categoryVisible = ref(false)
const categoryForm = ref<Record<string, any>>({})

// ====== 商品弹窗 ======
const goodsVisible = ref(false)
const goodsForm = ref<Record<string, any>>({})
const activeTab = ref('basic')
const savingGoods = ref(false)

// ====== 计算 ======
const flatCategories = computed(() => {
  const result: Array<Record<string, any>> = []
  const walk = (nodes: Array<Record<string, any>>) => {
    for (const n of nodes) {
      result.push(n)
      if (n.children) walk(n.children)
    }
  }
  walk(treeData.value)
  return result
})

const categoryNameMap = computed(() => {
  const map: Record<string, string> = {}
  for (const c of flatCategories.value) map[c.goodsct] = c.goodsctname
  return map
})

const brandNameMap = computed(() => {
  const map: Record<string, string> = {}
  for (const b of brandOptions.value) map[b.value] = b.label
  return map
})

// ====== 分类树 ======
watch(treeFilter, (val) => treeRef.value?.filter(val))

function filterTreeNode(value: string, data: any) {
  if (!value) return true
  return data.goodsctname?.includes(value) || data.goodsct?.includes(value)
}

async function loadTree() {
  try {
    const res = await getGoodsctTree()
    treeData.value = [
      { goodsct: '__uncategorized__', goodsctname: '未分类', children: [] },
      ...(res.data.tree || []),
    ]
  } catch { ElMessage.error('加载分类树失败') }
}

async function onNodeClick(data: any) {
  if (data.goodsct === '__uncategorized__') {
    selectedCategory.value = '未分类'
    selectedGoodsct.value = ''
    uncategorizedOnly.value = true
  } else {
    selectedCategory.value = data.goodsctname || ''
    selectedGoodsct.value = data.goodsct || ''
    uncategorizedOnly.value = false
  }
  currentPage.value = 1
  await fetchItems()
}

function openCategoryDialog(data?: Record<string, any>) {
  categoryForm.value = data
    ? { pk: data.pk || '', goodsct: data.goodsct || '', goodsctname: data.goodsctname || '', parent: data.parent || data.parentcode || '' }
    : { pk: '', goodsct: '', goodsctname: '', parent: '' }
  categoryVisible.value = true
}

async function saveCategory() {
  const f = categoryForm.value
  if (!f.goodsct || !f.goodsctname) {
    ElMessage.warning('请填写分类编号和名称')
    return
  }
  try {
    await saveGoodsct({
      pk: f.pk || '', goodsct: f.goodsct, goodsctname: f.goodsctname, parent: f.parent || '',
    })
    ElMessage.success(f.pk ? '分类已更新' : '分类已创建')
    categoryVisible.value = false
    await loadTree()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '保存失败')
  }
}

async function handleDeleteCategory(data?: Record<string, any>) {
  const pk = data?.pk || categoryForm.value.pk
  if (!pk) return
  try {
    await ElMessageBox.confirm('确定删除此分类？其下的商品不会被删除。', '确认', { type: 'warning' })
    await deleteGoodsct(pk)
    ElMessage.success('分类已删除')
    categoryVisible.value = false
    if (selectedGoodsct.value === (data?.goodsct || categoryForm.value.goodsct)) {
      selectedGoodsct.value = ''
      selectedCategory.value = ''
    }
    await loadTree()
    await fetchItems(true)
  } catch {}
}

// ====== 列表 ======
async function fetchItems(force = false) {
  loading.value = true
  try {
    const params: Record<string, any> = { page: currentPage.value, page_size: pageSize.value }
    if (uncategorizedOnly.value) params.uncategorized = '1'
    else if (selectedGoodsct.value) params.goodsct = selectedGoodsct.value
    if (searchQuery.value) params.search = searchQuery.value
    if (brandFilter.value) params.brand = brandFilter.value
    if (displayClassFilter.value) params.displayclass1 = displayClassFilter.value
    if (statusFilter.value) params.valiflag = statusFilter.value

    const cacheKey = `${selectedGoodsct.value}|${uncategorizedOnly.value ? 'uncat' : ''}|${currentPage.value}`
    const canCache = !searchQuery.value && !brandFilter.value && !statusFilter.value && !displayClassFilter.value
    if (canCache && listCache.has(cacheKey) && !force) {
      const cached = listCache.get(cacheKey)
      items.value = cached.rows
      total.value = cached.total
      return
    }

    const res = await getGoodsFastList(params)
    items.value = res.data.rows || []
    total.value = res.data.total || 0
    if (canCache) {
      listCache.set(cacheKey, { rows: items.value, total: total.value })
      if (listCache.size > 20) {
        const firstKey = listCache.keys().next().value
        if (firstKey) listCache.delete(firstKey)
      }
    }
  } catch { ElMessage.error('加载商品列表失败') }
  finally { loading.value = false }
}

// ====== 商品弹窗 ======
function openGoodsDialog(row?: any) {
  if (row) {
    goodsForm.value = {
      gcode: row.gcode || '', gname: row.gname || '', goodsct: row.goodsct || '',
      spec: row.spec || '', brand: row.brand || '', unit: row.unit || '',
      price: row.price || 0, buyprc: row.buyprc || 0, qty: row.qty || 0,
      barcode: row.barcode || '', minivalues: row.minivalues || 1, maxvalues: row.maxvalues || 10,
      price2: row.price2 || 0, price3: row.price3 || 0, price4: row.price4 || 0,
      pricecurrency: row.pricecurrency || 'RMB',
      displayclass1: row.displayclass1 || '', displayclass2: row.displayclass2 || '',
      discountclass: row.discountclass || '', saleschannels: row.saleschannels || '',
      marketclass1: row.marketclass1 || '', marketclass2: row.marketclass2 || '',
      pmperc: row.pmperc || 0, pmguideperc: row.pmguideperc || 0,
      secperc: row.secperc || 0, secguideperc: row.secguideperc || 0,
      achivementcost: row.achivementcost || 0,
      intervalday: row.intervalday || 30,
      saleflag: row.saleflag || 'Y', valiflag: row.valiflag || 'Y',
      pricechangeable: row.pricechangeable || 'Y',
      __pk: row.id || row.pk,
    }
  } else {
    goodsForm.value = {
      gcode: '', gname: '', goodsct: selectedGoodsct.value, spec: '', brand: '',
      unit: '', price: 0, buyprc: 0, qty: 0, barcode: '', minivalues: 1, maxvalues: 10,
      price2: 0, price3: 0, price4: 0, pricecurrency: 'RMB',
      displayclass1: '', displayclass2: '', discountclass: '', saleschannels: '',
      marketclass1: '', marketclass2: '', pmperc: 0, pmguideperc: 0,
      secperc: 0, secguideperc: 0, achivementcost: 0,
      intervalday: 30, saleflag: 'Y', valiflag: 'Y', pricechangeable: 'Y', __pk: null,
    }
  }
  activeTab.value = 'basic'
  goodsVisible.value = true
}

async function saveGoods() {
  const f = goodsForm.value
  if (!f.gcode || !f.gname || !f.goodsct) {
    ElMessage.warning('请填写编码、名称和商品大类')
    return
  }
  savingGoods.value = true
  try {
    const payload = {
      gcode: f.gcode, gname: f.gname, goodsct: f.goodsct, spec: f.spec, brand: f.brand,
      unit: f.unit, price: f.price, buyprc: f.buyprc, qty: f.qty, barcode: f.barcode,
      minivalues: f.minivalues, maxvalues: f.maxvalues,
      price2: f.price2, price3: f.price3, price4: f.price4, pricecurrency: f.pricecurrency || 'RMB',
      displayclass1: f.displayclass1, displayclass2: f.displayclass2,
      discountclass: f.discountclass, saleschannels: f.saleschannels,
      marketclass1: f.marketclass1, marketclass2: f.marketclass2,
      pmperc: f.pmperc || 0, pmguideperc: f.pmguideperc || 0,
      secperc: f.secperc || 0, secguideperc: f.secguideperc || 0,
      achivementcost: f.achivementcost || 0,
      intervalday: f.intervalday || 30,
      saleflag: f.saleflag || 'Y', valiflag: f.valiflag || 'Y',
      pricechangeable: f.pricechangeable || 'Y',
    }
    if (f.__pk) {
      await updateModelData('baseinfo', 'goods', f.__pk, payload)
    } else {
      await createModelData('baseinfo', 'goods', payload)
    }
    ElMessage.success('保存成功')
    goodsVisible.value = false
    await fetchItems(true)
  } catch (e: any) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally { savingGoods.value = false }
}

async function handleDeleteGoods(row: any) {
  const pk = row.id || row.pk
  if (!pk) return
  try {
    await ElMessageBox.confirm(`确定删除商品「${row.gname || row.gcode}」？`, '确认删除', { type: 'warning' })
    await updateModelData('baseinfo', 'goods', pk, { flag: 'N' })
    ElMessage.success('商品已删除')
    await fetchItems(true)
  } catch {}
}

// ====== 选项 ======
async function loadOptions() {
  try {
    const [brandRes, displayRes] = await Promise.all([
      getAppOptionList('brand'),
      getAppOptionList('goodsdisplayclass1'),
    ])
    brandOptions.value = (brandRes.data.results || []).map((o: any) => ({
      value: o.code || o.value || o.name || o.label || '',
      label: o.name || o.label || o.code || o.value || '',
    }))
    displayClassOptions.value = (displayRes.data.results || []).map((o: any) => ({
      value: o.code || o.value || o.name || o.label || '',
      label: o.name || o.label || o.code || o.value || '',
    }))
  } catch {}
}

// ====== 生命周期 ======
onMounted(async () => {
  await loadTree()
  await loadOptions()
  await fetchItems()
})
</script>

<style scoped>
.goods-admin { height: 100%; display: flex; }
.tree-sidebar { background: #fff; border-right: 1px solid #ebeef5; overflow-y: auto; }
.sidebar-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 10px 0; font-size: 14px; font-weight: 600; color: #303133; }
.list-main { background: #f5f7fa; display: flex; flex-direction: column; }
.list-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-shrink: 0; flex-wrap: wrap; gap: 8px; }
.tree-node-row { display: flex; justify-content: space-between; align-items: center; width: 100%; padding-right: 4px; flex: 1; }
.tree-node-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tree-node-actions { display: flex; gap: 2px; }
.code-link { color: #409EFF; cursor: pointer; text-decoration: none; }
.code-link:hover { text-decoration: underline; }
</style>
