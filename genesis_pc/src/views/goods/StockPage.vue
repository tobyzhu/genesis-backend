<template>
  <div class="stock-page">
    <!-- 商品选择器弹窗 -->
    <el-dialog v-model="productPickerVisible" title="选择商品" width="700px" :close-on-click-modal="false" destroy-on-close @open="loadProductPickerProducts">
      <el-form :inline="true" size="small">
        <el-form-item label="搜索">
          <el-input v-model="productPickerSearch" placeholder="编码/名称/条码" style="width:200px" clearable @keyup.enter="loadProductPickerProducts" />
        </el-form-item>
        <el-form-item label="默认数量">
          <el-input-number v-model="productPickerQty" :min="1" :precision="0" style="width:100px" size="small" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadProductPickerProducts">查询</el-button>
        </el-form-item>
      </el-form>
      <el-table ref="pickerTableRef" :data="productPickerItems" v-loading="productPickerLoading" stripe size="small" max-height="400" @selection-change="onPickerSelection">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="gcode" label="编码" width="110" />
        <el-table-column prop="gname" label="名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="brand" label="品牌" width="90" />
        <el-table-column prop="spec" label="规格" width="80" />
        <el-table-column label="售价" width="80" align="right">
          <template #default="{row}">¥{{ Number(row.price ?? 0).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="productPickerPage"
          :page-size="20"
          :total="productPickerTotal"
          layout="total, prev, pager, next"
          size="small"
          @current-change="loadProductPickerProducts"
        />
      </div>
      <template #footer>
        <el-button @click="productPickerVisible = false">取消</el-button>
        <el-button type="primary" :loading="productPickerLoading" @click="confirmProductPicker">确认选择 ({{ productPickerSelected.length }})</el-button>
      </template>
    </el-dialog>
    <el-tabs v-model="activeTab" type="border-card">
      <!-- ===== Tab 1: 单据列表 ===== -->
      <el-tab-pane label="单据列表" name="documents">
        <div class="tab-pane">
          <el-form :inline="true" :model="docFilter" size="default">
            <el-form-item label="类型">
              <el-select v-model="docFilter.doc_type" placeholder="全部" clearable style="width:100px">
                <el-option label="入库" value="I" />
                <el-option label="出库" value="O" />
                <el-option label="调拨" value="TO" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="docFilter.status" placeholder="全部" clearable style="width:100px">
                <el-option label="草稿" value="10" />
                <el-option label="已确认" value="20" />
                <el-option label="已作废" value="90" />
              </el-select>
            </el-form-item>
            <el-form-item label="日期">
              <el-date-picker v-model="docFilter.date_from" type="date" value-format="YYYYMMDD" style="width:130px" placeholder="开始" />
              <span style="margin:0 4px">~</span>
              <el-date-picker v-model="docFilter.date_to" type="date" value-format="YYYYMMDD" style="width:130px" placeholder="结束" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadDocuments">查询</el-button>
              <el-button @click="resetDocFilter">重置</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="docList" v-loading="docLoading" stripe size="small" max-height="480">
            <el-table-column label="类型" width="70">
              <template #default="{row}">
                <el-tag :type="row.doc_type==='I'?'success':row.doc_type==='TO'?'warning':'danger'" size="small">
                  {{ {I:'入库',O:'出库',U:'领用',F:'退货',TO:'调拨'}[row.doc_type] || row.doc_type }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="sukid" label="单号" width="200" show-overflow-tooltip />
            <el-table-column prop="vdate" label="日期" width="90" />
            <el-table-column label="门店/仓库" width="130">
              <template #default="{row}">
                {{ row.storecode }}/{{ row.whcode }}
              </template>
            </el-table-column>
            <el-table-column label="对方" width="100">
              <template #default="{row}">
                <span v-if="row.other_storecode">{{ row.other_storecode }}/{{ row.other_whcode }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="item_count" label="品项" width="60" align="center" />
            <el-table-column prop="note" label="备注" width="120" show-overflow-tooltip />
            <el-table-column label="状态" width="80">
              <template #default="{row}">
                <el-tag :type="row.status==='20'?'success':row.status==='90'?'danger':'info'" size="small">
                  {{ {10:'草稿',20:'已确认',90:'已作废'}[row.status] || row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{row}">
                <el-button v-if="row.status==='10'" type="primary" link size="small" @click="handleConfirm(row)">确认</el-button>
                <el-button v-if="row.status==='10'" type="warning" link size="small" @click="openEditDocument(row)">编辑</el-button>
                <el-button link type="primary" size="small" @click="openDetail(row)">查看</el-button>
                <el-button v-if="row.status!=='90'" type="danger" link size="small" @click="handleCancel(row)">作废</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-bar">
            <el-pagination
              v-model:current-page="docPage"
              :page-size="docPageSize"
              :total="docTotal"
              layout="total, prev, pager, next"
              size="small"
              @current-change="loadDocuments"
            />
          </div>

          <el-dialog v-model="detailVisible" :title="detailTitle" width="600px" :close-on-click-modal="false" destroy-on-close>
            <el-table :data="detailItems" stripe size="small" max-height="400">
              <el-table-column prop="gcode" label="编码" width="120" />
              <el-table-column prop="gname" label="名称" min-width="160" show-overflow-tooltip />
              <el-table-column label="数量" width="80" align="right">
                <template #default="{row}">{{ row.qty }}</template>
              </el-table-column>
              <el-table-column label="单价" width="90" align="right">
                <template #default="{row}">{{ row.price }}</template>
              </el-table-column>
              <el-table-column label="金额" width="100" align="right">
                <template #default="{row}">{{ row.amount }}</template>
              </el-table-column>
              <el-table-column prop="goodsvaldate" label="有效期" width="100" />
            </el-table>
          </el-dialog>
    <!-- 编辑单据明细弹窗 -->
    <el-dialog v-model="editVisible" :title="editTitle" width="650px" :close-on-click-modal="false" destroy-on-close>
      <el-form :inline="true" size="small">
        <el-form-item label="备注">
          <el-input v-model="editNote" style="width:300px" />
        </el-form-item>
      </el-form>
      <el-table :data="editItems" stripe size="small" max-height="360">
        <el-table-column prop="gcode" label="编码" width="110" />
        <el-table-column prop="gname" label="名称" min-width="130" show-overflow-tooltip />
        <el-table-column label="数量" width="100">
          <template #default="{row}">
            <el-input-number v-model="row.qty" :min="0.01" :precision="0" style="width:90px" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="单价" width="100">
          <template #default="{row}">
            <el-input-number v-model="row.price" :min="0" :precision="2" style="width:90px" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="有效期" width="110">
          <template #default="{row}">
            <el-date-picker v-model="row.goodsvaldate" type="date" value-format="YYYYMMDD" style="width:100px" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="60">
          <template #default="{ $index }">
            <el-button link type="danger" size="small" @click="editItems.splice($index,1)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top:8px">
        <el-button size="small" @click="openEditProductPicker">选择商品</el-button>
      </div>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="saveEditDocument">保存修改</el-button>
      </template>
    </el-dialog>
        </div>
      </el-tab-pane>
      <!-- ===== Tab 2: 库存查询 ===== -->
      <el-tab-pane label="库存查询" name="query">
        <div class="tab-pane">
          <el-form :inline="true" :model="qFilter" size="default">
            <el-form-item label="门店">
              <el-select v-model="qFilter.storecode" placeholder="全部门店" clearable style="width:140px" @change="loadWharehouses('q')">
                <el-option v-for="s in storeOptions" :key="s.storecode" :label="s.storename" :value="s.storecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="仓库">
              <el-select v-model="qFilter.whcode" placeholder="全部仓库" clearable style="width:140px">
                <el-option v-for="w in whOptions_q" :key="w.wharehousecode" :label="w.wharehousename" :value="w.wharehousecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="关键字">
              <el-input v-model="qFilter.search" placeholder="编码/名称" clearable style="width:160px" @keyup.enter="loadStock" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadStock">查询</el-button>
              <el-button @click="resetStockFilter">重置</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="stockList" v-loading="stockLoading" stripe size="small" max-height="520">
            <el-table-column prop="gcode" label="编码" width="110" />
            <el-table-column prop="gname" label="名称" min-width="130" show-overflow-tooltip />
            <el-table-column prop="spec" label="规格" width="90" show-overflow-tooltip />
            <el-table-column prop="brand" label="品牌" width="90" />
            <el-table-column prop="whcode" label="仓库" width="90" />
            <el-table-column label="库存" width="80" align="right">
              <template #default="{row}">
                <span :class="alertClass(row)">{{ row.qty }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="unit" label="单位" width="60" />
            <el-table-column label="预警" width="70">
              <template #default="{row}">
                <el-tag v-if="row.alert==='low'" type="danger" size="small">偏低</el-tag>
                <el-tag v-else-if="row.alert==='high'" type="warning" size="small">偏高</el-tag>
                <el-tag v-else type="success" size="small">正常</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="vdate" label="最后变动" width="100" />
          </el-table>
        </div>
      </el-tab-pane>

      <!-- ===== Tab 3: 入库单 ===== -->
      <el-tab-pane label="入库单" name="inbound">
        <div class="tab-pane">
          <el-form :inline="true" :model="inForm" size="default">
            <el-form-item label="日期">
              <el-date-picker v-model="inForm.vdate" type="date" value-format="YYYYMMDD" style="width:140px" />
            </el-form-item>
            <el-form-item label="门店">
              <el-select v-model="inForm.storecode" placeholder="必选" style="width:120px" @change="s => loadWharehouses('in', s)">
                <el-option v-for="s in storeOptions" :key="s.storecode" :label="s.storename" :value="s.storecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="仓库">
              <el-select v-model="inForm.whcode" placeholder="必选" style="width:120px">
                <el-option v-for="w in whOptions_in" :key="w.wharehousecode" :label="w.wharehousename" :value="w.wharehousecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="供应商">
              <el-select v-model="inForm.supplierid" filterable clearable placeholder="选择供应商" style="width:180px"><el-option v-for="s in supplierOptions" :key="s.supplierid" :label="s.suppliername" :value="s.supplierid" /></el-select>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="inForm.note" style="width:160px" />
            </el-form-item>
          </el-form>

          <div class="items-header">
            <span class="items-title">入库明细</span>
            <el-button size="small" @click="openProductPicker('inbound')">选择商品</el-button>
          </div>
          <el-table :data="inItems" stripe size="small" max-height="360">
            <el-table-column label="商品" min-width="200">
              <template #default="{row,$index}">
                <span>{{ row.gcode }}{{ row.gname ? ' - ' + row.gname : '' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="数量" width="100">
              <template #default="{row}">
                <el-input-number v-model="row.qty" :min="0.01" :precision="0" style="width:90px" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="100">
              <template #default="{row}">
                <el-input-number v-model="row.price" :min="0" :precision="2" style="width:90px" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="有效期" width="120">
              <template #default="{row}">
                <el-date-picker v-model="row.goodsvaldate" type="date" value-format="YYYYMMDD" style="width:110px" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ $index }">
                <el-button link type="danger" size="small" @click="inItems.splice($index,1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="submit-bar">
            <el-button type="primary" :loading="inLoading" @click="submitInbound">确认入库</el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- ===== Tab 4: 出库单 ===== -->
      <el-tab-pane label="出库单" name="outbound">
        <div class="tab-pane">
          <el-form :inline="true" :model="outForm" size="default">
            <el-form-item label="日期">
              <el-date-picker v-model="outForm.vdate" type="date" value-format="YYYYMMDD" style="width:140px" />
            </el-form-item>
            <el-form-item label="门店">
              <el-select v-model="outForm.storecode" placeholder="必选" style="width:120px" @change="s => loadWharehouses('out', s)">
                <el-option v-for="s in storeOptions" :key="s.storecode" :label="s.storename" :value="s.storecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="仓库">
              <el-select v-model="outForm.whcode" placeholder="必选" style="width:120px">
                <el-option v-for="w in whOptions_out" :key="w.wharehousecode" :label="w.wharehousename" :value="w.wharehousecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="类型">
              <el-radio-group v-model="outForm.out_type">
                <el-radio value="O">报损</el-radio>
                <el-radio value="U">领用</el-radio>
                <el-radio value="F">退货</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="outForm.note" style="width:140px" />
            <el-form-item label="供应商" v-if="outForm.out_type === 'F'">
              <el-select v-model="outForm.supplierid" filterable clearable placeholder="选择供应商" style="width:180px">
                <el-option v-for="s in supplierOptions" :key="s.supplierid" :label="s.suppliername" :value="s.supplierid" />
              </el-select>
            </el-form-item>
            </el-form-item>
          </el-form>

          <div class="items-header">
            <span class="items-title">出库明细</span>
            <el-button size="small" @click="openProductPicker('outbound')">选择商品</el-button>
          </div>
          <el-table :data="outItems" stripe size="small" max-height="360">
            <el-table-column label="商品" min-width="200">
              <template #default="{row}">
                <span>{{ row.gcode }}{{ row.gname ? ' - ' + row.gname : '' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="数量" width="100">
              <template #default="{row}">
                <el-input-number v-model="row.qty" :min="0.01" :precision="0" style="width:90px" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="单价" width="100">
              <template #default="{row}">
                <el-input-number v-model="row.price" :min="0" :precision="2" style="width:90px" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ $index }">
                <el-button link type="danger" size="small" @click="outItems.splice($index,1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="submit-bar">
            <el-button type="primary" :loading="outLoading" @click="submitOutbound">确认出库</el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- ===== Tab 5: 调拨单 ===== -->
      <el-tab-pane label="调拨单" name="transfer">
        <div class="tab-pane">
          <el-form :inline="true" :model="trForm" size="default">
            <el-form-item label="日期">
              <el-date-picker v-model="trForm.vdate" type="date" value-format="YYYYMMDD" style="width:140px" />
            </el-form-item>
            <el-form-item label="调出门店">
              <el-select v-model="trForm.out_storecode" placeholder="必选" style="width:130px" @change="loadWh('trOut',trForm.out_storecode)">
                <el-option v-for="s in storeOptions" :key="s.storecode" :label="s.storename" :value="s.storecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="调出仓库">
              <el-select v-model="trForm.out_whcode" placeholder="必选" style="width:120px">
                <el-option v-for="w in whOptions_trOut" :key="w.wharehousecode" :label="w.wharehousename" :value="w.wharehousecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="调入门店">
              <el-select v-model="trForm.in_storecode" placeholder="必选" style="width:130px" @change="loadWh('trIn',trForm.in_storecode)">
                <el-option v-for="s in storeOptions" :key="s.storecode" :label="s.storename" :value="s.storecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="调入仓库">
              <el-select v-model="trForm.in_whcode" placeholder="必选" style="width:120px">
                <el-option v-for="w in whOptions_trIn" :key="w.wharehousecode" :label="w.wharehousename" :value="w.wharehousecode" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="trForm.note" style="width:140px" />
            </el-form-item>
          </el-form>

          <div class="items-header">
            <span class="items-title">调拨明细</span>
            <el-button size="small" @click="openProductPicker('transfer')">选择商品</el-button>
          </div>
          <el-table :data="trItems" stripe size="small" max-height="340">
            <el-table-column label="商品" min-width="200">
              <template #default="{row}">
                <span>{{ row.gcode }}{{ row.gname ? ' - ' + row.gname : '' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="数量" width="100">
              <template #default="{row}">
                <el-input-number v-model="row.qty" :min="0.01" :precision="0" style="width:90px" size="small" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="60">
              <template #default="{ $index }">
                <el-button link type="danger" size="small" @click="trItems.splice($index,1)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="submit-bar">
            <el-button type="primary" :loading="trLoading" @click="submitTransfer">确认调拨</el-button>
          </div>
        </div>
      </el-tab-pane>

      <!-- ===== Tab 6: 库存流水 ===== -->
      <el-tab-pane label="库存流水" name="translog">
        <div class="tab-pane">
          <el-form :inline="true" :model="tlFilter" size="default">
            <el-form-item label="日期从">
              <el-date-picker v-model="tlFilter.date_from" type="date" value-format="YYYYMMDD" style="width:140px" />
            </el-form-item>
            <el-form-item label="至">
              <el-date-picker v-model="tlFilter.date_to" type="date" value-format="YYYYMMDD" style="width:140px" />
            </el-form-item>
            <el-form-item label="类型">
              <el-select v-model="tlFilter.saleatr" placeholder="全部" clearable style="width:100px">
                <el-option label="进货" value="I" />
                <el-option label="销售" value="G" />
                <el-option label="报损" value="O" />
                <el-option label="领用" value="U" />
                <el-option label="退货" value="F" />
                <el-option label="调出" value="TO" />
                <el-option label="调入" value="TI" />
              </el-select>
            </el-form-item>
            <el-form-item label="商品">
              <el-input v-model="tlFilter.gcode" placeholder="编码" style="width:120px" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadTranslog">查询</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="translogList" v-loading="tlLoading" stripe size="small" max-height="480">
            <el-table-column prop="vdate" label="日期" width="90" />
            <el-table-column label="类型" width="70">
              <template #default="{row}">
                <el-tag :type="tlTagType(row.saleatr)" size="small">{{ row.saleatr_name }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="sukid" label="单号" width="180" show-overflow-tooltip />
            <el-table-column prop="gcode" label="编码" width="100" />
            <el-table-column prop="gname" label="名称" min-width="120" show-overflow-tooltip />
            <el-table-column prop="storecode" label="门店" width="60" />
            <el-table-column prop="whcode" label="仓库" width="70" />
            <el-table-column label="数量" width="80" align="right">
              <template #default="{row}">
                <span :class="row.qty > 0 ? 'qty-in' : 'qty-out'">
                  {{ row.qty > 0 ? '+' : '' }}{{ row.qty }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="结存" width="80" align="right">
              <template #default="{row}">{{ row.qty2 }}</template>
            </el-table-column>
            <el-table-column prop="price" label="单价" width="80" align="right" />
            <el-table-column prop="amount" label="金额" width="90" align="right" />
            <el-table-column prop="gnote" label="备注" width="140" show-overflow-tooltip />
          </el-table>

          <div class="pagination-bar">
            <el-pagination
              v-model:current-page="tlPage"
              :page-size="tlPageSize"
              :total="tlTotal"
              layout="total, prev, pager, next"
              size="small"
              @current-change="loadTranslog"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  getStockQuery, createInbound, createOutbound, createTransfer, getTranslog,
  getWharehouses, getStores, getGoodsList,
  confirmDocument, cancelDocument, getDocumentList, getDocumentDetail, updateDocument,
  getSuppliers,
} from '@/api/goods'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { StockItem, TranslogItem, Warehouse, StoreOption, Goods } from '@/types'

// ---- 公用选项 ----
const storeOptions = ref<StoreOption[]>([])
const whCache = ref<Record<string, Warehouse[]>>({})
const supplierOptions = ref<Array<{supplierid: string; suppliername: string}>>([])

async function loadSuppliers() {
  try {
    const res = await getSuppliers()
    supplierOptions.value = res.data
  } catch { supplierOptions.value = [] }
}

async function loadStores() {
  try {
    const res = await getStores()
    storeOptions.value = res.data
  } catch { storeOptions.value = [] }
}

function whKey(prefix: string, storecode: string) {
  return prefix + '_' + storecode
}

async function loadWharehouses(prefix: string, storecode?: string) {
  if (!storecode) return
  const key = whKey(prefix, storecode)
  if (whCache.value[key]) {
    setWhOptions(prefix, whCache.value[key])
    return
  }
  try {
    const res = await getWharehouses(storecode)
    whCache.value[key] = res.data
    setWhOptions(prefix, res.data)
  } catch { setWhOptions(prefix, []) }
}

function setWhOptions(prefix: string, list: Warehouse[]) {
  if (prefix === 'q') whOptions_q.value = list
  else if (prefix === 'in') whOptions_in.value = list
  else if (prefix === 'out') whOptions_out.value = list
  else if (prefix === 'trOut') whOptions_trOut.value = list
  else if (prefix === 'trIn') whOptions_trIn.value = list
}

function loadWh(prefix: string, storecode: string) { loadWharehouses(prefix, storecode) }

// ---- 商品搜索 + 选项缓存 ----
const goodsSearchCache = ref<Record<string, Goods[]>>({})

async function searchGoods(kw: string, prefix: string, idx: number) {
  if (!kw || kw.length < 1) return
  const key = prefix + '_' + idx
  if (goodsSearchCache.value[kw]) {
    assignGoodsOptions(prefix, idx, goodsSearchCache.value[kw])
    return
  }
  try {
    const res = await getGoodsList({ search: kw, page_size: 20 })
    goodsSearchCache.value[kw] = res.data.results
    assignGoodsOptions(prefix, idx, res.data.results)
  } catch { /* ignore */ }
}

function assignGoodsOptions(prefix: string, idx: number, list: Goods[]) {
  if (prefix === 'in' && inItems[idx]) inItems[idx].goodsOptions = list
  else if (prefix === 'out' && outItems[idx]) outItems[idx].goodsOptions = list
  else if (prefix === 'tr' && trItems[idx]) trItems[idx].goodsOptions = list
}

function onInGcodeChange(idx: number) {
  // auto-fill price from selected goods
}

// ========== Tab 1: 单据列表 ==========
const docFilter = reactive({ doc_type: "", status: "10", date_from: "", date_to: "" })
const docList = ref<any[]>([])
const docLoading = ref(false)
const docPage = ref(1)
const docPageSize = 20
const docTotal = ref(0)
const detailVisible = ref(false)
const detailItems = ref<any[]>([])
const detailTitle = ref("")

async function loadDocuments() {
  docLoading.value = true
  try {
    const res = await getDocumentList({
      page: docPage.value,
      page_size: docPageSize,
      doc_type: docFilter.doc_type,
      status: docFilter.status,
      date_from: docFilter.date_from,
      date_to: docFilter.date_to,
    })
    docList.value = res.data.results
    docTotal.value = res.data.count
  } finally { docLoading.value = false }
}

function resetDocFilter() {
  docPage.value = 1
  docFilter.doc_type = ''
  docFilter.status = ''
  docFilter.date_from = ''
  docFilter.date_to = ''
  loadDocuments()
}

function handleConfirm(row: any) {
  ElMessageBox.confirm(`确认单据「${row.sukid}」吗？确认后库存将立即变动。`, '确认单据', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    await confirmDocument(row.sukid)
    ElMessage.success('单据已确认')
    loadDocuments()
  }).catch(() => {})
}

function openDetail(row: any) {
  detailTitle.value = `单据明细 - ${row.sukid}`
  detailItems.value = []
  detailVisible.value = true
  getDocumentDetail(row.sukid).then(res => {
    detailItems.value = res.data.items || []
  }).catch(() => {})
}

function handleCancel(row: any) {
  ElMessageBox.confirm(`作废单据「${row.sukid}」吗？`, '作废单据', {
    confirmButtonText: '作废',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    await cancelDocument(row.sukid)
    ElMessage.success('单据已作废')
    loadDocuments()
  }).catch(() => {})
}
const pickerTableRef = ref()
const productPickerVisible = ref(false)
const productPickerTarget = ref('inbound')
const productPickerItems = ref<any[]>([])
const productPickerLoading = ref(false)
const productPickerQty = ref(1)
const productPickerSelected = ref<string[]>([])
const productPickerSearch = ref('')
const productPickerPage = ref(1)
const productPickerTotal = ref(0)
const editVisible = ref(false)
const editSukid = ref('')
const editTitle = ref('')
const editItems = ref<any[]>([])
const editNote = ref('')
const editLoading = ref(false)
const editMode = ref(false)


function openEditDocument(row: any) {
  editSukid.value = row.sukid
  editTitle.value = `编辑单据 - ${row.sukid}`
  editItems.value = []
  editNote.value = ''
  editVisible.value = true
  getDocumentDetail(row.sukid).then(res => {
    editItems.value = res.data.items || []
    editNote.value = res.data.header?.note || ''
  }).catch(() => {})
}

function openEditProductPicker() {
  editMode.value = true
  productPickerSelected.value = []
  productPickerSearch.value = ''
  productPickerPage.value = 1
  productPickerQty.value = 1
  productPickerVisible.value = true
  loadProductPickerProducts()
}

async function saveEditDocument() {
  editLoading.value = true
  try {
    const items = editItems.value.map(it => ({
      gcode: it.gcode,
      qty: Number(it.qty) || 0,
      price: Number(it.price) || 0,
      goodsvaldate: it.goodsvaldate || undefined,
    }))
    await updateDocument(editSukid.value, { note: editNote.value, items })
    ElMessage.success('单据已更新')
    editVisible.value = false
    loadDocuments()
  } catch {} finally { editLoading.value = false }
}

function openProductPicker(target: string) {
  productPickerTarget.value = target
  productPickerSelected.value = []
  productPickerSearch.value = ""
  productPickerPage.value = 1
  productPickerQty.value = 1
  productPickerVisible.value = true
  loadProductPickerProducts()
}

async function loadProductPickerProducts() {
  productPickerLoading.value = true
  try {
    const res = await getGoodsList({ search: productPickerSearch.value, page: productPickerPage.value, page_size: 20 })
    productPickerItems.value = res.data.results
    productPickerTotal.value = res.data.count
  } finally { productPickerLoading.value = false }
}

function onPickerSelection(val: any[]) {
  productPickerSelected.value = val.map(v => v.gcode)
}

function confirmProductPicker() {
  const qty = productPickerQty.value
  if (editMode.value) {
    for (const g of productPickerItems.value) {
      if (productPickerSelected.value.includes(g.gcode)) {
        editItems.value.push({ gcode: g.gcode, gname: g.gname || "", qty: Number(qty), price: Number(g.price) || 0, goodsvaldate: "" })
      }
    }
    editMode.value = false
    productPickerVisible.value = false
    return
  }
  const target = productPickerTarget.value === "inbound" ? inItems :
                 productPickerTarget.value === "outbound" ? outItems : trItems
  for (const g of productPickerItems.value) {
    if (productPickerSelected.value.includes(g.gcode)) {
      target.push({ gcode: g.gcode, gname: g.gname || "", qty, price: Number(g.price) || 0, goodsvaldate: "" })
    }
  }
  productPickerVisible.value = false
}

// ========== Tab 2: 库存查询 ==========
const activeTab = ref("documents")
const qFilter = reactive({ storecode: '', whcode: '', search: '' })
const whOptions_q = ref<Warehouse[]>([])
const stockList = ref<StockItem[]>([])
const stockLoading = ref(false)

function alertClass(row: StockItem) {
  if (row.alert === 'low') return 'alert-low'
  if (row.alert === 'high') return 'alert-high'
  return ''
}

async function loadStock() {
  stockLoading.value = true
  try {
    const res = await getStockQuery({
      storecode: qFilter.storecode,
      whcode: qFilter.whcode,
      search: qFilter.search,
    })
    stockList.value = res.data
  } finally { stockLoading.value = false }
}

function resetStockFilter() {
  qFilter.storecode = ''
  qFilter.whcode = ''
  qFilter.search = ''
  loadStock()
}

// ========== Tab 3: 入库单 ==========
const whOptions_in = ref<Warehouse[]>([])
const inForm = reactive({ vdate: '', storecode: '', whcode: '', supplierid: '', note: '' })
const inItems = reactive<Array<{ gcode: string; qty: number; price: number; goodsvaldate: string; goodsOptions: Goods[] }>>([])
const inLoading = ref(false)

function addInItem() {
  inItems.push({ gcode: '', qty: 1, price: 0, goodsvaldate: '', goodsOptions: [] })
}

async function submitInbound() {
  if (!inForm.storecode || !inForm.whcode) { ElMessage.warning('请选择门店和仓库'); return }
  if (inItems.length === 0) { ElMessage.warning('请添加入库商品'); return }
  inLoading.value = true
  try {
    const res = await createInbound({
      storecode: inForm.storecode,
      whcode: inForm.whcode,
      vdate: inForm.vdate || undefined,
      note: inForm.note,
      supplierid: inForm.supplierid,
      items: inItems.map(it => ({ gcode: it.gcode, qty: it.qty, price: it.price, goodsvaldate: it.goodsvaldate || undefined })),
    })
    ElMessage.success(`入库成功，单号：${res.data.sukid}`)
    inItems.splice(0)
    inForm.note = ''
    inForm.supplierid = ''
  } catch { /* handled by interceptor */ }
  finally { inLoading.value = false }
}

// ========== Tab 4: 出库单 ==========
const whOptions_out = ref<Warehouse[]>([])
const outForm = reactive({ vdate: '', storecode: '', whcode: '', out_type: 'O' as 'O'|'U'|'F', note: '', supplierid: '' })
const outItems = reactive<Array<{ gcode: string; qty: number; price: number; goodsOptions: Goods[] }>>([])
const outLoading = ref(false)

function addOutItem() {
  outItems.push({ gcode: '', qty: 1, price: 0, goodsOptions: [] })
}

async function submitOutbound() {
  if (!outForm.storecode || !outForm.whcode) { ElMessage.warning('请选择门店和仓库'); return }
  if (outItems.length === 0) { ElMessage.warning('请添加入库商品'); return }
  outLoading.value = true
  try {
    const res = await createOutbound({
      storecode: outForm.storecode,
      supplierid: outForm.supplierid || undefined,
      whcode: outForm.whcode,
      out_type: outForm.out_type,
      vdate: outForm.vdate || undefined,
      note: outForm.note,
      items: outItems.map(it => ({ gcode: it.gcode, qty: it.qty, price: it.price })),
    })
    ElMessage.success(`出库成功，单号：${res.data.sukid}`)
    outItems.splice(0)
    outForm.note = ''
  } catch {
    // 库存不足等错误由后端返回，拦截器已展示
  } finally { outLoading.value = false }
}

// ========== Tab 5: 调拨单 ==========
const whOptions_trOut = ref<Warehouse[]>([])
const whOptions_trIn = ref<Warehouse[]>([])
const trForm = reactive({
  vdate: '', out_storecode: '', out_whcode: '',
  in_storecode: '', in_whcode: '', note: '',
})
const trItems = reactive<Array<{ gcode: string; qty: number; goodsOptions: Goods[] }>>([])
const trLoading = ref(false)

function addTrItem() {
  trItems.push({ gcode: '', qty: 1, goodsOptions: [] })
}

async function submitTransfer() {
  if (!trForm.out_storecode || !trForm.out_whcode || !trForm.in_storecode || !trForm.in_whcode) {
    ElMessage.warning('请完善调出/调入信息')
    return
  }
  if (trItems.length === 0) { ElMessage.warning('请添加调拨商品'); return }
  trLoading.value = true
  try {
    const res = await createTransfer({
      out_storecode: trForm.out_storecode,
      out_whcode: trForm.out_whcode,
      in_storecode: trForm.in_storecode,
      in_whcode: trForm.in_whcode,
      vdate: trForm.vdate || undefined,
      note: trForm.note,
      items: trItems.map(it => ({ gcode: it.gcode, qty: it.qty })),
    })
    ElMessage.success(`调拨成功，单号：${res.data.sukid}`)
    trItems.splice(0)
    trForm.note = ''
  } catch { /* handled */ }
  finally { trLoading.value = false }
}

// ========== Tab 6: 库存流水 ==========
const tlFilter = reactive({ date_from: '', date_to: '', saleatr: '', gcode: '' })
const translogList = ref<TranslogItem[]>([])
const tlLoading = ref(false)
const tlPage = ref(1)
const tlPageSize = 50
const tlTotal = ref(0)

function tlTagType(saleatr: string): string {
  if (['I','TI','IS','AD'].includes(saleatr)) return 'success'
  if (['G','O','U','F','TO'].includes(saleatr)) return 'danger'
  return 'info'
}

async function loadTranslog() {
  tlLoading.value = true
  try {
    const res = await getTranslog({
      date_from: tlFilter.date_from,
      date_to: tlFilter.date_to,
      saleatr: tlFilter.saleatr,
      gcode: tlFilter.gcode,
      page: tlPage.value,
      page_size: tlPageSize,
    })
    translogList.value = res.data.results
    tlTotal.value = res.data.count
  } finally { tlLoading.value = false }
}

// ---- 初始化 ----
onMounted(() => {
  loadStores()
  loadSuppliers()
  loadStock()
  loadTranslog()
  loadDocuments()
})
</script>

<style scoped>
.stock-page { padding: 0; }
.tab-pane { min-height: 400px; }
.items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 8px 0;
}
.items-title { font-weight: 600; font-size: 14px; }
.submit-bar { margin-top: 12px; display: flex; justify-content: flex-end; }
.pagination-wrap { margin-top: 12px; display: flex; justify-content: flex-end; }
.alert-low { color: var(--g-color-danger); font-weight: 700; }
.alert-high { color: var(--g-color-money); font-weight: 700; }
.qty-in { color: var(--g-color-success); font-weight: 600; }
.qty-out { color: var(--g-color-danger); font-weight: 600; }
</style>
