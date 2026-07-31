<template>
  <div class="serviece-admin">
    <el-container style="height:100%">
      <!-- 左侧分类树 -->
      <el-aside width="260px" class="tree-sidebar">
        <div class="sidebar-header">
          <span>服务大类</span>
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
          :props="{ label: 'ttname', children: 'children' }"
          :filter-node-method="filterTreeNode"
          node-key="topcode"
          highlight-current
          default-expand-all
          @node-click="onNodeClick"
          style="padding:0 8px"
        >
          <template #default="{ data }">
            <div class="tree-node-row">
              <span class="tree-node-label">{{ data.ttname || data.topcode || '(未命名)' }}</span>
              <span class="tree-node-actions">
                <el-button size="small" :icon="Edit" circle @click.stop="openCategoryDialog(data)" />
                <el-button size="small" type="danger" :icon="Delete" circle @click.stop="handleDeleteCategory(data)" />
              </span>
            </div>
          </template>
        </el-tree>
      </el-aside>

      <!-- 右侧项目列表 -->
      <el-main class="list-main">
        <div class="list-toolbar">
          <h3 style="margin:0;font-size:15px;font-weight:600">
            {{ selectedCategory || '全部' }} <span style="font-size:12px;color:#909399;font-weight:400">服务项目</span>
            <span style="font-weight:400;color:#909399;font-size:13px;margin-left:8px">共 {{ total }} 项</span>
          </h3>
          <div style="display:flex;gap:8px;align-items:center">
            <el-select v-model="brandFilter" placeholder="品牌" clearable size="default" style="width:130px" @change="() => fetchItems(true)">
              <el-option v-for="b in brandOptions" :key="b.value" :label="b.label" :value="b.value" />
            </el-select>
            <el-select v-model="displayClassFilter" placeholder="显示分类" clearable size="default" style="width:120px" @change="() => fetchItems(true)">
              <el-option v-for="d in displayClassOptions" :key="d.value" :label="d.label" :value="d.value" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="状态" clearable size="default" style="width:90px" @change="fetchItems">
              <el-option label="有效" value="Y" />
              <el-option label="无效" value="N" />
            </el-select>
            <el-input
              v-model="searchQuery"
              placeholder="搜索编号/名称..."
              clearable
              style="width:180px"
              @clear="() => fetchItems()"
              @keyup.enter="() => fetchItems()"
            />
            <el-button type="primary" :icon="Plus" @click="openServiceDialog()">新增</el-button>
            <el-button @click="() => fetchItems(true)" :icon="Refresh">刷新</el-button>
          </div>
        </div>

        <el-table :data="items" stripe border size="small" v-loading="loading" style="width:100%">
          <el-table-column label="分类" width="100" show-overflow-tooltip>
            <template #default="{row}">{{ topcodeNameMap[row.topcode] || '-' }}</template>
          </el-table-column>
          <el-table-column prop="svrcdoe" label="编号" width="90">
            <template #default="{row}">
              <span class="code-link" @click="openServiceDialog(row)">{{ row.svrcdoe }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="svrname" label="名称" min-width="150" show-overflow-tooltip />
          <el-table-column label="品牌" width="90" show-overflow-tooltip>
            <template #default="{row}">{{ brandNameMap[row.brand] || row.brand || '-' }}</template>
          </el-table-column>
          <el-table-column label="显示分类" width="90" show-overflow-tooltip>
            <template #default="{row}">{{ displayClassMap[row.displayclass1] || row.displayclass1 || '-' }}</template>
          </el-table-column>
          <el-table-column label="价格" width="90" align="right">
            <template #default="{row}">¥{{ (row.price || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="成本" width="80" align="right">
            <template #default="{row}">¥{{ (row.costamount || 0).toFixed(2) }}</template>
          </el-table-column>
          <el-table-column label="时长" width="60" align="center">
            <template #default="{row}">{{ row.stdmins || '-' }}</template>
          </el-table-column>
          <el-table-column label="项次" width="60" align="center">
            <template #default="{row}">{{ row.qty || '-' }}</template>
          </el-table-column>
          <el-table-column label="可销售" width="65" align="center">
            <template #default="{row}">{{ row.saleflag === 'Y' ? '✅' : '❌' }}</template>
          </el-table-column>
          <el-table-column label="有效" width="65" align="center">
            <template #default="{row}">{{ row.valiflag === 'Y' ? '✅' : '❌' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{row}">
              <el-button size="small" :icon="Edit" @click="openServiceDialog(row)" circle />
              <el-button size="small" type="danger" :icon="Delete" @click="handleDeleteService(row)" circle />
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
          <el-input v-model="categoryForm.topcode" :disabled="!!categoryForm.pk" placeholder="如 100, 200" />
        </el-form-item>
        <el-form-item label="分类名称" required>
          <el-input v-model="categoryForm.ttname" placeholder="如 面部护理" />
        </el-form-item>
        <el-form-item label="上级分类">
          <el-select v-model="categoryForm.parentcode" clearable placeholder="无（一级分类）" style="width:100%">
            <el-option v-for="c in flatCategories" :key="c.topcode" :label="c.ttname" :value="c.topcode" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryVisible = false">取消</el-button>
        <el-button type="danger" v-if="categoryForm.pk" @click="handleDeleteCategory()">删除</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>

    <!-- 服务项目编辑弹窗 -->
    <el-dialog v-model="serviceVisible" :title="serviceForm.svrcdoe ? '编辑服务项目' : '新增服务项目'" width="760px" top="4vh">
      <el-tabs v-model="activeTab">
        <!-- Tab 1: 基本信息 -->
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="serviceForm" label-width="100px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="编号" required>
                  <el-input v-model="serviceForm.svrcdoe" placeholder="服务编号" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="名称" required>
                  <el-input v-model="serviceForm.svrname" placeholder="服务名称" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="服务大类" required>
                  <el-select v-model="serviceForm.topcode" placeholder="选择分类" style="width:100%">
                    <el-option v-for="c in flatCategories" :key="c.topcode" :label="c.ttname" :value="c.topcode" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="品牌">
                  <el-select v-model="serviceForm.brand" clearable placeholder="选择品牌" style="width:100%">
                    <el-option v-for="b in brandOptions" :key="b.value" :label="b.label" :value="b.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="价格">
                  <el-input-number v-model="serviceForm.price" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="成本">
                  <el-input-number v-model="serviceForm.costamount" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="时长(分)">
                  <el-input-number v-model="serviceForm.stdmins" :min="0" :precision="0" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="项次">
                  <el-input-number v-model="serviceForm.qty" :min="0" :precision="0" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="积分">
              <el-input-number v-model="serviceForm.cpoint" :min="0" :precision="0" style="width:100%" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Tab 2: 价格设定 -->
        <el-tab-pane label="价格设定" name="prices">
          <el-form :model="serviceForm" label-width="100px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="第二价格">
                  <el-input-number v-model="serviceForm.price2" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="第三价格">
                  <el-input-number v-model="serviceForm.price3" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="第四价格">
                  <el-input-number v-model="serviceForm.price4" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="币别">
                  <el-select v-model="serviceForm.pricecurrency" style="width:100%">
                    <el-option label="RMB" value="RMB" />
                    <el-option label="USD" value="USD" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <!-- Tab 3: 多档价位 -->
        <el-tab-pane label="疗程价" name="tiers">
          <div style="margin-bottom:8px;display:flex;justify-content:space-between;align-items:center">
            <span style="font-size:13px;color:#909399">不同购买次数的价格设定</span>
            <el-button size="small" type="primary" :icon="Plus" @click="addPriceTier">添加价位</el-button>
          </div>
          <el-table :data="priceTiers" border size="small">
            <el-table-column label="次数" width="70" align="center">
              <template #default="{row}">
                <el-input-number v-model="row.qty" :min="1" :precision="0" size="small" controls-position="right" @change="updateTierAmount(row)" />
              </template>
            </el-table-column>
            <el-table-column label="单次价格" width="100" align="center">
              <template #default="{row}">
                <el-input-number v-model="row.price" :min="0" :precision="2" size="small" controls-position="right" @change="updateTierAmount(row)" />
              </template>
            </el-table-column>
            <el-table-column label="总价" width="100" align="right">
              <template #default="{row}">¥{{ (row.amount || 0).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="销售提成" width="80" align="center">
              <template #default="{row}">
                <el-input-number v-model="row.commission" :min="0" :max="1" :step="0.05" :precision="2" size="small" controls-position="right" />
              </template>
            </el-table-column>
            <el-table-column label="销售业绩" width="80" align="center">
              <template #default="{row}">
                <el-input-number v-model="row.achivement" :min="0" :max="2" :step="0.1" :precision="2" size="small" controls-position="right" />
              </template>
            </el-table-column>
            <el-table-column label="生效起止" min-width="220">
              <template #default="{row}">
                <el-date-picker v-model="row.fromdate" type="date" value-format="YYYY-MM-DD" placeholder="开始" size="small" style="width:100px" />
                <span style="margin:0 3px">~</span>
                <el-date-picker v-model="row.todate" type="date" value-format="YYYY-MM-DD" placeholder="结束" size="small" style="width:100px" />
              </template>
            </el-table-column>
            <el-table-column label="可销售" width="60" align="center">
              <template #default="{row}">
                <el-switch v-model="row.saleflag" active-value="Y" inactive-value="N" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="赠送" width="70" align="center">
              <template #default="{row}">
                <el-select v-model="row.stype" size="small" style="width:55px">
                  <el-option label="正常" value="N" />
                  <el-option label="赠送" value="P" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="45" align="center">
              <template #default="{ $index }">
                <el-button size="small" type="danger" :icon="Delete" circle @click="removePriceTier($index)" />
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!priceTiers.length" description="暂无价位，点击上方添加" :image-size="50" />
        </el-tab-pane>

        <!-- Tab 4: 分类设定 -->
        <el-tab-pane label="分类设定" name="categories">
          <el-form :model="serviceForm" label-width="110px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="显示分类1">
                  <el-select v-model="serviceForm.displayclass1" clearable placeholder="选择显示分类" style="width:100%">
                    <el-option v-for="d in displayClassOptions" :key="d.value" :label="d.label" :value="d.value" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="显示分类2">
                  <el-select v-model="serviceForm.displayclass2" clearable placeholder="选择显示分类" style="width:100%">
                    <el-option v-for="d in displayClassOptions" :key="d.value" :label="d.label" :value="d.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="报表分类">
                  <el-input v-model="serviceForm.srvrptypecode" placeholder="报表分类编码" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="折扣分类">
                  <el-select v-model="serviceForm.discountclass" clearable placeholder="选择折扣分类" style="width:100%">
                    <el-option v-for="d in discountOptions" :key="d.value" :label="d.label" :value="d.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="营销分类1">
                  <el-input v-model="serviceForm.marketclass1" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="营销分类2">
                  <el-input v-model="serviceForm.marketclass2" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="营销分类3">
                  <el-input v-model="serviceForm.marketclass3" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="营销分类4">
                  <el-input v-model="serviceForm.marketclass4" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="财务分类1">
                  <el-input v-model="serviceForm.financeclass1" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="财务分类2">
                  <el-input v-model="serviceForm.financeclass2" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="业绩分类1">
                  <el-input v-model="serviceForm.archivementclass1" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="业绩分类2">
                  <el-input v-model="serviceForm.archivementclass2" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <!-- Tab 5: 提成设定 -->
        <el-tab-pane label="提成设定" name="commission">
          <el-form :model="serviceForm" label-width="140px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="顾问提成率">
                  <el-input-number v-model="serviceForm.pmperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="顾问营业额拆分率">
                  <el-input-number v-model="serviceForm.pmguideperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="美疗师1提成率">
                  <el-input-number v-model="serviceForm.secperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="美疗师1拆分率">
                  <el-input-number v-model="serviceForm.secguideperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="美疗师2提成率">
                  <el-input-number v-model="serviceForm.thrperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="美疗师2拆分率">
                  <el-input-number v-model="serviceForm.thrguideperc" :min="0" :max="1" :step="0.05" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="业绩固定成本扣除">
              <el-input-number v-model="serviceForm.achivementcost" :min="0" :precision="2" style="width:100%" />
            </el-form-item>
            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item label="顾问基数">
                  <el-input-number v-model="serviceForm.basenum" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="美疗师1基数">
                  <el-input-number v-model="serviceForm.secbasenum" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="美疗师2基数">
                  <el-input-number v-model="serviceForm.thrbasenum" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>

        <!-- Tab 6: 控制设定 -->
        <el-tab-pane label="控制设定" name="controls">
          <el-form :model="serviceForm" label-width="110px" size="small">
            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item label="可销售">
                  <el-switch v-model="serviceForm.saleflag" active-value="Y" inactive-value="N" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="有效">
                  <el-switch v-model="serviceForm.valiflag" active-value="Y" inactive-value="N" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="可改价格">
                  <el-switch v-model="serviceForm.pricechangeable" active-value="Y" inactive-value="N" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="建议间隔天数">
                  <el-input-number v-model="serviceForm.intervalday" :min="0" :precision="0" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="助记码">
                  <el-input v-model="serviceForm.mnemoniccode" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="身体部位">
              <el-select v-model="serviceForm.bodyparts1" multiple clearable placeholder="选择部位" style="width:100%">
                <el-option v-for="b in bodyPartOptions" :key="b.value" :label="b.label" :value="b.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="标签">
              <el-select v-model="serviceForm.tags" multiple clearable placeholder="选择标签" style="width:100%">
                <el-option v-for="t in tagOptions" :key="t.value" :label="t.label" :value="t.value" />
              </el-select>
            </el-form-item>
            <el-form-item label="可用门店">
              <el-select v-model="serviceForm.storelist" multiple clearable placeholder="选择门店" style="width:100%">
                <el-option v-for="s in storeOptions" :key="s.value" :label="s.label" :value="s.value" />
              </el-select>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="serviceVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingService" @click="saveService">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import {
  getSrvtoptyTree, getServieceList, getServieceMeta,
  saveSrvtopty, deleteSrvtopty, getAppOptionList,
  getServiecePrices, saveServiecePrices, getServieceFastList
} from '@/api/serviece-admin'
import { createModelData, updateModelData } from '@/api/sysadmin'

// ====== 分类树 ======
const treeData = ref<Array<Record<string, any>>>([])
const treeFilter = ref('')
const treeRef = ref<any>(null)
const selectedCategory = ref('')
const selectedTopcode = ref('')
const uncategorizedOnly = ref(false)

// ====== 列表 ======
const items = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const listCache = new Map<string, any>()
const brandFilter = ref('')
const displayClassFilter = ref('')
const statusFilter = ref('')

// ====== 选项数据 ======
const brandOptions = ref<Array<{value: string; label: string}>>([])
const displayClassOptions = ref<Array<{value: string; label: string}>>([])

// ====== 分类弹窗 ======
const categoryVisible = ref(false)
const categoryForm = ref<Record<string, any>>({})

// ====== 服务弹窗 ======
const serviceVisible = ref(false)
const serviceForm = ref<Record<string, any>>({})
const activeTab = ref('basic')
const savingService = ref(false)
const priceTiers = ref<Array<Record<string, any>>>([])
const discountOptions = [
  { value: '', label: '默认' },
  { value: 'A', label: '标准折扣' },
  { value: 'B', label: '特殊折扣' },
  { value: 'C', label: '无折扣' },
]
const bodyPartOptions = [
  { value: '01', label: '面部' }, { value: '02', label: '颈部' },
  { value: '03', label: '肩部' }, { value: '04', label: '背部' },
  { value: '05', label: '腰部' }, { value: '06', label: '手部' },
  { value: '07', label: '腿部' }, { value: '08', label: '足部' },
  { value: '09', label: '全身' },
]
const tagOptions = [
  { value: 'HOT', label: '热门' }, { value: 'NEW', label: '新品' },
  { value: 'VIP', label: '会员专享' }, { value: 'SALE', label: '促销' },
  { value: 'TIME', label: '疗程' },
]
const storeOptions = [
  { value: '01', label: '01 店' }, { value: '02', label: '02 店' },
  { value: '03', label: '03 店' },
]

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

const topcodeNameMap = computed(() => {
  const map: Record<string, string> = {}
  for (const c of flatCategories.value) {
    map[c.topcode] = c.ttname
  }
  return map
})

const displayClassMap = computed(() => {
  const map: Record<string, string> = {}
  for (const d of displayClassOptions.value) {
    map[d.value] = d.label
  }
  return map
})

const brandNameMap = computed(() => {
  const map: Record<string, string> = {}
  for (const b of brandOptions.value) {
    map[b.value] = b.label
  }
  return map
})

// ====== 分类树方法 ======
watch(treeFilter, (val) => treeRef.value?.filter(val))

function filterTreeNode(value: string, data: any) {
  if (!value) return true
  return data.ttname?.includes(value) || data.topcode?.includes(value)
}

async function loadTree() {
  try {
    const res = await getSrvtoptyTree()
    treeData.value = [
      { topcode: '__uncategorized__', ttname: '未分类', children: [] },
      ...(res.data.tree || []),
    ]
  } catch { ElMessage.error('加载分类树失败') }
}

async function onNodeClick(data: any) {
  if (data.topcode === '__uncategorized__') {
    selectedCategory.value = '未分类'
    selectedTopcode.value = ''
    uncategorizedOnly.value = true
  } else {
    selectedCategory.value = data.ttname || ''
    selectedTopcode.value = data.topcode || ''
    uncategorizedOnly.value = false
  }
  currentPage.value = 1
  await fetchItems()
}



// ====== 分类弹窗 ======
function openCategoryDialog(data?: Record<string, any>) {
  categoryForm.value = data
    ? { pk: data.pk || '', topcode: data.topcode || '', ttname: data.ttname || '', parentcode: data.parentcode || '' }
    : { pk: '', topcode: '', ttname: '', parentcode: '' }
  categoryVisible.value = true
}

async function saveCategory() {
  const form = categoryForm.value
  if (!form.topcode || !form.ttname) {
    ElMessage.warning('请填写分类编号和名称')
    return
  }
  try {
    const res = await saveSrvtopty({
      pk: form.pk || '',
      topcode: form.topcode,
      ttname: form.ttname,
      parentcode: form.parentcode || '',
    })
    ElMessage.success(form.pk ? '分类已更新' : '分类已创建')
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
    await ElMessageBox.confirm('确定删除此分类？其下的服务项目不会被删除。', '确认', { type: 'warning' })
    await deleteSrvtopty(pk)
    ElMessage.success('分类已删除')
    categoryVisible.value = false
    if (selectedTopcode.value === (data?.topcode || categoryForm.value.topcode)) {
      selectedTopcode.value = ''
      selectedCategory.value = ''
    }
    await loadTree()
    await fetchItems()
  } catch {}
}

// ====== 列表方法 ======
async function fetchItems(force = false) {
  loading.value = true
  try {
    const params: Record<string, any> = { page: currentPage.value, page_size: pageSize.value }
    if (uncategorizedOnly.value) {
      params.uncategorized = '1'
    } else if (selectedTopcode.value) {
      params.topcode = selectedTopcode.value
    }
    if (searchQuery.value) params.search = searchQuery.value
    if (brandFilter.value) params.brand = brandFilter.value
    if (displayClassFilter.value) params.displayclass1 = displayClassFilter.value
    if (statusFilter.value) params.valiflag = statusFilter.value

    // 缓存：无搜索/无筛选时按分类缓存，加速切换分类
    const cacheKey = `${selectedTopcode.value}|${uncategorizedOnly.value ? 'uncat' : ''}|${displayClassFilter.value}|${currentPage.value}`
    const canCache = !searchQuery.value && !brandFilter.value && !statusFilter.value && !displayClassFilter.value
    if (canCache && listCache.has(cacheKey) && !force) {
      const cached = listCache.get(cacheKey)
      items.value = cached.rows
      total.value = cached.total
      return
    }

    const res = await getServieceFastList(params)
    const data = res.data
    items.value = data.rows || []
    total.value = data.total || 0
    if (canCache) {
      listCache.set(cacheKey, { rows: items.value, total: total.value })
      // 限制缓存大小
      if (listCache.size > 20) {
        const firstKey = listCache.keys().next().value
        if (firstKey) listCache.delete(firstKey)
      }
    }
  } catch { ElMessage.error('加载项目列表失败') }
  finally { loading.value = false }
}

// ====== 服务弹窗 ======
function openServiceDialog(row?: any) {
  if (row) {
    serviceForm.value = {
      svrcdoe: row.svrcdoe || '', svrname: row.svrname || '',
      topcode: row.topcode || '', brand: row.brand || '',
      price: row.price || 0, costamount: row.costamount || 0,
      stdmins: row.stdmins || 0, qty: row.qty || 1, cpoint: row.cpoint || 0,
      price2: row.price2 || 0, price3: row.price3 || 0, price4: row.price4 || 0,
      pricecurrency: row.pricecurrency || 'RMB',
      displayclass1: row.displayclass1 || '', displayclass2: row.displayclass2 || '',
      srvrptypecode: row.srvrptypecode || '', discountclass: row.discountclass || '',
      marketclass1: row.marketclass1 || '', marketclass2: row.marketclass2 || '',
      marketclass3: row.marketclass3 || '', marketclass4: row.marketclass4 || '',
      financeclass1: row.financeclass1 || '', financeclass2: row.financeclass2 || '',
      archivementclass1: row.archivementclass1 || '', archivementclass2: row.archivementclass2 || '',
      intervalday: row.intervalday || 7,
      bodyparts1: row.bodyparts1 || '', tags: row.tags || '',
      mnemoniccode: row.mnemoniccode || '', storelist: row.storelist || '',
      pmperc: row.pmperc || 0, pmguideperc: row.pmguideperc || 0,
      secperc: row.secperc || 0, secguideperc: row.secguideperc || 0,
      thrperc: row.thrperc || 0, thrguideperc: row.thrguideperc || 0,
      achivementcost: row.achivementcost || 0,
      basenum: row.basenum || 0, secbasenum: row.secbasenum || 0, thrbasenum: row.thrbasenum || 0,
      saleflag: row.saleflag || 'Y', valiflag: row.valiflag || 'Y',
      pricechangeable: row.pricechangeable || 'Y',
      __pk: row.id || row.pk,
    }
    // 加载多档价位
    loadPriceTiers(row.svrcdoe || '')
  } else {
    serviceForm.value = {
      svrcdoe: '', svrname: '', topcode: selectedTopcode.value, brand: '',
      price: 0, costamount: 0, stdmins: 60, qty: 1, cpoint: 0,
      price2: 0, price3: 0, price4: 0, pricecurrency: 'RMB',
      displayclass1: '', displayclass2: '', srvrptypecode: '',
      discountclass: '', marketclass1: '', marketclass2: '',
      marketclass3: '', marketclass4: '', financeclass1: '', financeclass2: '',
      archivementclass1: '', archivementclass2: '',
      intervalday: 7, bodyparts1: '', tags: '', mnemoniccode: '', storelist: '',
      pmperc: 0, pmguideperc: 0, secperc: 0, secguideperc: 0,
      thrperc: 0, thrguideperc: 0, achivementcost: 0,
      basenum: 0, secbasenum: 0, thrbasenum: 0,
      saleflag: 'Y', valiflag: 'Y', pricechangeable: 'Y', __pk: null,
    }
    priceTiers.value = []
  }
  activeTab.value = 'basic'
  serviceVisible.value = true
}

async function loadPriceTiers(srvcode: string) {
  if (!srvcode) { priceTiers.value = []; return }
  try {
    const res = await getServiecePrices(srvcode)
    priceTiers.value = res.data.results || []
  } catch { priceTiers.value = [] }
}

function addPriceTier() {
  priceTiers.value.push({ qty: 1, price: 0, amount: 0, commission: 0, achivement: 1, fromdate: '', todate: '', saleflag: 'Y', stype: 'N' })
}

function removePriceTier(index: number) {
  priceTiers.value.splice(index, 1)
}

function updateTierAmount(tier: Record<string, any>) {
  tier.amount = (tier.qty || 0) * (tier.price || 0)
}

async function saveService() {
  const f = serviceForm.value
  if (!f.svrcdoe || !f.svrname || !f.topcode) {
    ElMessage.warning('请填写编号、名称和分类')
    return
  }
  savingService.value = true
  try {
    const payload = {
      svrcdoe: f.svrcdoe, svrname: f.svrname, topcode: f.topcode, brand: f.brand,
      price: f.price, costamount: f.costamount, stdmins: f.stdmins, qty: f.qty,
      cpoint: f.cpoint,
      displayclass1: f.displayclass1, displayclass2: f.displayclass2,
      srvrptypecode: f.srvrptypecode, discountclass: f.discountclass,
      marketclass1: f.marketclass1, marketclass2: f.marketclass2,
      marketclass3: f.marketclass3, marketclass4: f.marketclass4,
      financeclass1: f.financeclass1, financeclass2: f.financeclass2,
      archivementclass1: f.archivementclass1, archivementclass2: f.archivementclass2,
      price2: f.price2, price3: f.price3, price4: f.price4,
      pricecurrency: f.pricecurrency || 'RMB',
      intervalday: f.intervalday || 7,
      bodyparts1: f.bodyparts1 || '', tags: f.tags || '',
      mnemoniccode: f.mnemoniccode || '', storelist: f.storelist || '',
      pmperc: f.pmperc || 0, pmguideperc: f.pmguideperc || 0,
      secperc: f.secperc || 0, secguideperc: f.secguideperc || 0,
      thrperc: f.thrperc || 0, thrguideperc: f.thrguideperc || 0,
      achivementcost: f.achivementcost || 0,
      basenum: f.basenum || 0, secbasenum: f.secbasenum || 0, thrbasenum: f.thrbasenum || 0,
      saleflag: f.saleflag || 'Y', valiflag: f.valiflag || 'Y',
      pricechangeable: f.pricechangeable || 'Y',
    }
    let savedPk = f.__pk
    if (savedPk) {
      await updateModelData('baseinfo', 'serviece', savedPk, payload)
    } else {
      const created = await createModelData('baseinfo', 'serviece', payload)
      savedPk = created.data?.pk || created.data?.id
    }
    // 保存多档价位
    if (savedPk) {
      const validTiers = priceTiers.value.filter(t => (t.qty || 0) > 0 && (t.price || 0) > 0)
      if (validTiers.length) {
        await saveServiecePrices(f.svrcdoe, validTiers)
      } else {
        await saveServiecePrices(f.svrcdoe, [])
      }
    }
    ElMessage.success('保存成功')
    serviceVisible.value = false
    await fetchItems()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally { savingService.value = false }
}

async function handleDeleteService(row: any) {
  const pk = row.id || row.pk
  if (!pk) return
  try {
    await ElMessageBox.confirm(
      `确定删除服务项目「${row.svrname || row.svrcdoe}」？\n删除后该项目将不再显示（flag 设为 N）。`,
      '确认删除',
      { type: 'warning' }
    )
    await updateModelData('baseinfo', 'serviece', pk, { flag: 'N' })
    ElMessage.success('项目已删除')
    await fetchItems(true)
  } catch {}
}

// ====== 选项加载 ======
async function loadOptions() {
  try {
    const [brandRes, displayRes] = await Promise.all([
      getAppOptionList('brand'),
      getAppOptionList('srvdisplayclass1'),
    ])
    // 后端返回 {value, label, code, name}，统一映射
    brandOptions.value = (brandRes.data.results || []).map((o: any) => ({
      value: o.code || o.value || o.name || o.label || '',
      label: o.name || o.label || o.code || o.value || '',
    }))
    displayClassOptions.value = (displayRes.data.results || []).map((o: any) => ({
      value: o.code || o.value || o.name || o.label || '',
      label: o.name || o.label || o.code || o.value || '',
    }))
    console.log('[Serviece] brandOptions:', brandOptions.value.slice(0, 5))
    console.log('[Serviece] displayClassOptions:', displayClassOptions.value.slice(0, 5))
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
.serviece-admin { height: 100%; display: flex; }
.tree-sidebar { background: #fff; border-right: 1px solid #ebeef5; overflow-y: auto; }
.sidebar-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 10px 0; font-size: 14px; font-weight: 600; color: #303133; }
.list-main { background: #f5f7fa; display: flex; flex-direction: column; }
.list-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-shrink: 0; flex-wrap: wrap; gap: 8px; }
.tree-node-row { display: flex; justify-content: space-between; align-items: center; width: 100%; padding-right: 4px; flex: 1; }
.code-link { color: #409EFF; cursor: pointer; text-decoration: none; }
.code-link:hover { text-decoration: underline; }
.tree-node-label { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.tree-node-actions { display: flex; gap: 2px; }
</style>
