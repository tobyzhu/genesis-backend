<template>
  <div class="cardtype-admin">
    <div class="list-toolbar">
      <h3 style="margin:0;font-size:15px;font-weight:600">卡类管理</h3>
      <div style="display:flex;gap:8px;align-items:center">
        <el-select v-model="comptypeFilter" placeholder="消费模式" clearable size="default" style="width:120px" @change="fetchCardtypes">
          <el-option label="计费卡" value="amount" />
          <el-option label="计次卡" value="times" />
          <el-option label="时效卡" value="period" />
        </el-select>
        <el-input
          v-model="searchQuery"
          placeholder="搜索编号/名称..."
          clearable
          style="width:200px"
          @keyup.enter="fetchCardtypes()"
          @clear="fetchCardtypes()"
        />
        <el-button type="primary" :icon="Plus" @click="openDialog()">新增</el-button>
        <el-button :icon="Refresh" @click="fetchCardtypes()">刷新</el-button>
      </div>
    </div>

    <el-table :data="cardtypes" stripe border size="small" v-loading="loading" style="width:100%">
      <el-table-column label="编号" width="110">
        <template #default="{row}">
          <span class="code-link" @click="openDialog(row)">{{ row.cardtype }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="cardname" label="名称" min-width="160" show-overflow-tooltip />
      <el-table-column label="消费模式" width="90" align="center">
        <template #default="{row}">{{ comptypeName(row.comptype) }}</template>
      </el-table-column>
      <el-table-column label="卡大类" width="100">
        <template #default="{row}">{{ suptypeNameMap[row.suptype] || row.suptype || '-' }}</template>
      </el-table-column>
      <el-table-column label="面值" width="90" align="right">
        <template #default="{row}">¥{{ parseFloat(row.price || 0).toFixed(2) }}</template>
      </el-table-column>
      <el-table-column label="有效期(天)" width="90" align="center">
        <template #default="{row}">{{ row.validays ?? '-' }}</template>
      </el-table-column>
      <el-table-column label="可销售" width="70" align="center">
        <template #default="{row}">{{ row.saleflag === 'Y' ? '✅' : '❌' }}</template>
      </el-table-column>
      <el-table-column label="有效" width="65" align="center">
        <template #default="{row}">{{ row.valiflag === 'Y' ? '✅' : '❌' }}</template>
      </el-table-column>
      <el-table-column label="操作" width="110" fixed="right">
        <template #default="{row}">
          <el-button size="small" :icon="Edit" @click="openDialog(row)" circle />
          <el-button size="small" type="danger" :icon="Delete" @click="handleDelete(row)" circle />
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="total > 0"
      v-model:current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="fetchCardtypes()"
      style="margin-top:12px;justify-content:flex-end"
    />

    <!-- 卡类编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="form.cardtype ? '编辑卡类' : '新增卡类'" width="760px" top="4vh">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form :model="form" label-width="110px" size="small">
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="卡类编号" required>
                  <el-input v-model="form.cardtype" :disabled="!!originalCardtype" placeholder="如 CT001 / 计次卡默认=项目编号" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="卡类名称" required>
                  <el-input v-model="form.cardname" placeholder="卡类名称" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="卡大类">
                  <el-select v-model="form.suptype" clearable placeholder="选择卡大类" style="width:100%">
                    <el-option v-for="s in suptypes" :key="s.code" :label="s.name" :value="s.code" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="消费模式" required>
                  <el-select v-model="form.comptype" style="width:100%" @change="onComptypeChange">
                    <el-option label="计费卡（储值）" value="amount" />
                    <el-option label="计次卡" value="times" />
                    <el-option label="时效卡" value="period" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row v-if="form.comptype === 'amount'" :gutter="12">
              <el-col :span="12">
                <el-form-item label="逻辑卡">
                  <el-switch v-model="isLogicCard" active-text="按 Ruler 阶梯价" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="面值">
                  <el-input-number v-model="form.price" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="可用金额">
                  <el-input-number v-model="form.leftmoney" :min="0" :precision="2" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="有效期计算">
                  <el-select v-model="form.valdatetype" style="width:100%">
                    <el-option label="第一次使用日期" value="10" />
                    <el-option label="销售日期" value="20" />
                    <el-option label="手动输入" value="90" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="有效天数">
                  <el-input-number v-model="form.validays" :min="0" :precision="0" style="width:100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="备注">
              <el-input v-model="form.cardnote" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="关联项目" name="item">
          <el-form :model="form" label-width="110px" size="small">
            <el-alert
              v-if="form.comptype !== 'amount' || isLogicCard"
              type="info"
              :closable="false"
              show-icon
              title="计次卡/时效卡/逻辑卡需绑定具体服务或商品项目"
              style="margin-bottom:12px"
            />
            <el-row :gutter="12">
              <el-col :span="12">
                <el-form-item label="项目类型">
                  <el-select v-model="form.ttype" style="width:100%">
                    <el-option label="服务" value="S" />
                    <el-option label="商品" value="G" />
                    <el-option label="卡" value="C" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="绑定项目">
                  <el-select
                    v-model="form.sguuid"
                    filterable
                    remote
                    :remote-method="searchItems"
                    :loading="itemLoading"
                    placeholder="输入编号/名称搜索"
                    style="width:100%"
                    @change="onItemSelected"
                  >
                    <el-option
                      v-for="it in itemOptions"
                      :key="it.uuid"
                      :label="`${it.code} - ${it.name}`"
                      :value="it.uuid"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item v-if="boundCode" label="绑定编号">
              <el-tag>{{ boundCode }}</el-tag>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane v-if="isLogicCard" label="逻辑规则" name="ruler">
          <el-form label-width="110px" size="small">
            <el-form-item label="选择规则" required>
              <el-select v-model="form.ruler" filterable placeholder="选择 Ruler 规则" style="width:100%" @change="onRulerChange">
                <el-option
                  v-for="r in rulers"
                  :key="r.id"
                  :label="r.rulername"
                  :value="r.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="规则文本">
              <el-input :model-value="selectedRulerText" type="textarea" :rows="4" readonly />
            </el-form-item>
            <el-form-item label="新增规则">
              <el-button :icon="Plus" @click="openRulerDialog()">管理规则</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane v-if="form.comptype === 'amount'" label="折扣设定" name="discount">
          <div class="rule-toolbar">
            <span>按折扣分类设定折扣率/固定价，并控制是否可用此卡消费</span>
            <div>
              <el-button size="small" :icon="Plus" @click="addDiscountRule">新增行</el-button>
              <el-button size="small" type="primary" :loading="savingRules" @click="saveDiscountRules">保存规则</el-button>
            </div>
          </div>
          <el-table :data="discountRules" size="small" border>
            <el-table-column label="项目类型" width="90" align="center">
              <template #default="{row}">
                <el-select v-model="row.ttype" size="small">
                  <el-option label="服务" value="S" />
                  <el-option label="商品" value="G" />
                  <el-option label="卡" value="C" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="折扣分类" min-width="130">
              <template #default="{row}">
                <el-select v-model="row.discountclass" filterable clearable size="small" style="width:100%">
                  <el-option v-for="d in discountClassOptions" :key="d.value" :label="d.label" :value="d.value" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="折扣方式" width="110" align="center">
              <template #default="{row}">
                <el-select v-model="row.discounttype" size="small">
                  <el-option label="按折扣率" value="DISC" />
                  <el-option label="按固定价" value="PRICE" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="折扣率" width="100" align="right">
              <template #default="{row}">
                <el-input-number v-model="row.disc" :min="0" :max="1" :step="0.05" :precision="2" size="small" style="width:90px" />
              </template>
            </el-table-column>
            <el-table-column label="固定价" width="100" align="right">
              <template #default="{row}">
                <el-input-number v-model="row.price" :min="0" :precision="2" size="small" style="width:90px" />
              </template>
            </el-table-column>
            <el-table-column label="可消费" width="80" align="center">
              <template #default="{row}">
                <el-switch v-model="row.consume_flag" active-value="Y" inactive-value="N" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="70" align="center">
              <template #default="{ $index }">
                <el-button size="small" type="danger" :icon="Delete" circle @click="discountRules.splice($index, 1)" />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="控制设定" name="controls">
          <el-form :model="form" label-width="110px" size="small">
            <el-row :gutter="12">
              <el-col :span="8">
                <el-form-item label="可销售">
                  <el-switch v-model="form.saleflag" active-value="Y" inactive-value="N" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="有效">
                  <el-switch v-model="form.valiflag" active-value="Y" inactive-value="N" />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveCardtype">保存</el-button>
      </template>
    </el-dialog>

    <!-- 规则编辑弹窗 -->
    <el-dialog v-model="rulerDialogVisible" title="逻辑卡规则" width="520px">
      <el-form label-width="90px" size="small">
        <el-form-item label="规则名称" required>
          <el-input v-model="rulerForm.rulername" placeholder="如 拓客卡" />
        </el-form-item>
        <el-form-item label="规则文本" required>
          <el-input
            v-model="rulerForm.ruler"
            type="textarea"
            :rows="4"
            placeholder="#ttype=S#srvcode=105001#1sttimes=1260#2ndtimes=960#others=720#"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rulerDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingRuler" @click="saveRulerRow">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import {
  getRulerList, saveRuler,
  getCardtypeDiscountRules, saveCardtypeDiscountRules,
} from '@/api/card-admin'
import { getAppOptionList } from '@/api/serviece-admin'
import { getServieceFastList } from '@/api/serviece-admin'
import { getGoodsFastList } from '@/api/goods-admin'
import { getModelData, createModelData, updateModelData } from '@/api/sysadmin'

const cardtypes = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const comptypeFilter = ref('')

const suptypes = ref<any[]>([])
const rulers = ref<any[]>([])
const discountClassOptions = ref<Array<{value: string; label: string}>>([])

const dialogVisible = ref(false)
const activeTab = ref('basic')
const form = ref<Record<string, any>>({})
const originalCardtype = ref('')
const isLogicCard = ref(false)
const saving = ref(false)

const itemOptions = ref<Array<{uuid: string; code: string; name: string}>>([])
const itemLoading = ref(false)
const boundCode = ref('')

const discountRules = ref<Array<Record<string, any>>>([])
const savingRules = ref(false)

const rulerDialogVisible = ref(false)
const rulerForm = ref<Record<string, any>>({})
const savingRuler = ref(false)

const selectedRulerText = computed(() => {
  const r = rulers.value.find(x => x.id === form.value.ruler)
  return r?.ruler || ''
})

const suptypeNameMap = computed(() => {
  const map: Record<string, string> = {}
  for (const s of suptypes.value) map[s.code] = s.name
  return map
})

function comptypeName(v: string) {
  return ({ amount: '计费', times: '计次', period: '时效' } as Record<string, string>)[v || ''] || v || '-'
}

async function fetchCardtypes() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: currentPage.value, page_size: pageSize.value, ordering: 'cardtype' }
    if (comptypeFilter.value) params.comptype = comptypeFilter.value
    if (searchQuery.value) params.search = searchQuery.value
    const res = await getModelData('baseinfo', 'cardtype', params)
    cardtypes.value = res.data.rows || []
    total.value = res.data.total || 0
  } catch { ElMessage.error('加载卡类失败') }
  finally { loading.value = false }
}

async function loadOptions() {
  try {
    const [suptypeRes, discRes, srvDiscRes, goodsDiscRes, rulerRes] = await Promise.all([
      getModelData('baseinfo', 'cardsupertype', { page: 1, page_size: 200 }),
      getAppOptionList('discountclass'),
      getAppOptionList('srvdiscountclass'),
      getAppOptionList('goodsdiscountclass'),
      getRulerList(),
    ])
    suptypes.value = suptypeRes.data.rows || []
    const toOption = (rows: any[]) => (rows || []).map((o: any) => ({
      value: o.code || o.value || '',
      label: o.name || o.label || '',
    }))
    const merged = [
      ...toOption(discRes.data.results),
      ...toOption(srvDiscRes.data.results),
      ...toOption(goodsDiscRes.data.results),
    ]
    const seen = new Set<string>()
    discountClassOptions.value = merged.filter((o: any) => {
      if (!o.value || seen.has(o.value)) return false
      seen.add(o.value)
      return true
    })
    rulers.value = rulerRes.data.results || []
  } catch {}
}

function resetForm() {
  form.value = {
    cardtype: '', cardname: '', suptype: '', comptype: 'amount',
    price: 0, leftmoney: 0, valdatetype: '10', validays: 9999,
    cardnote: '', ttype: 'S', sguuid: '', ruler: '',
    saleflag: 'Y', valiflag: 'Y',
  }
  originalCardtype.value = ''
  isLogicCard.value = false
  boundCode.value = ''
  itemOptions.value = []
  discountRules.value = []
}

async function openDialog(row?: any) {
  resetForm()
  if (row) {
    form.value = {
      cardtype: row.cardtype || '', cardname: row.cardname || '',
      suptype: row.suptype || '', comptype: row.comptype || 'amount',
      price: row.price || 0, leftmoney: row.leftmoney || 0,
      valdatetype: row.valdatetype || '10', validays: row.validays ?? 9999,
      cardnote: row.cardnote || '', ttype: row.ttype || 'S',
      sguuid: row.sguuid || '', ruler: row.ruler || '',
      saleflag: row.saleflag || 'Y', valiflag: row.valiflag || 'Y',
      __pk: row.uuid || row.pk,
    }
    originalCardtype.value = row.cardtype || ''
    isLogicCard.value = row.comptype === 'amount' && !!row.ruler
    if (row.sguuid) boundCode.value = String(row.sguuid)
    activeTab.value = 'basic'
    if (row.comptype === 'amount') await loadDiscountRules(row.cardtype)
    if (row.sguuid) {
      itemOptions.value = [{ uuid: row.sguuid, code: row.cardtype || '', name: row.cardname || '' }]
    }
  } else {
    activeTab.value = 'basic'
  }
  dialogVisible.value = true
}

function onComptypeChange() {
  if (form.value.comptype === 'times') {
    isLogicCard.value = false
  }
}

async function searchItems(query: string) {
  if (!query) { itemOptions.value = []; return }
  itemLoading.value = true
  try {
    const params = { search: query, page: 1, page_size: 20 }
    if (form.value.ttype === 'G') {
      const res = await getGoodsFastList(params)
      itemOptions.value = (res.data.rows || []).map((r: any) => ({ uuid: r.pk, code: r.gcode, name: r.gname }))
    } else {
      const res = await getServieceFastList(params)
      itemOptions.value = (res.data.rows || []).map((r: any) => ({ uuid: r.pk, code: r.svrcdoe, name: r.svrname }))
    }
  } catch { itemOptions.value = [] }
  finally { itemLoading.value = false }
}

function onItemSelected(uuid: string) {
  const it = itemOptions.value.find(x => x.uuid === uuid)
  if (!it) return
  boundCode.value = it.code
  if (form.value.comptype === 'times' && !form.value.cardtype) {
    form.value.cardtype = it.code
  }
}

function onRulerChange() {
  // 逻辑卡规则里的项目编号自动回填绑定项目（编号一致时）
  const text = selectedRulerText.value
  const m = text.match(/#(?:srvcode|gcode)=([^#]+)/)
  if (m) boundCode.value = m[1]
}

async function saveCardtype() {
  const f = form.value
  if (!f.cardtype || !f.cardname) {
    ElMessage.warning('请填写编号和名称')
    return
  }
  if ((f.comptype !== 'amount' || isLogicCard.value) && !f.sguuid) {
    ElMessage.warning('请先绑定项目')
    return
  }
  if (isLogicCard.value && !f.ruler) {
    ElMessage.warning('逻辑卡需要选择规则')
    return
  }
  saving.value = true
  try {
    const payload: Record<string, any> = {
      cardtype: f.cardtype, cardname: f.cardname, suptype: f.suptype,
      comptype: f.comptype, price: f.price, leftmoney: f.leftmoney,
      valdatetype: f.valdatetype, validays: f.validays, cardnote: f.cardnote,
      ttype: f.ttype, sguuid: f.sguuid || null,
      ruler: isLogicCard.value ? f.ruler : null,
      saleflag: f.saleflag, valiflag: f.valiflag,
    }
    if (f.__pk) {
      await updateModelData('baseinfo', 'cardtype', f.__pk, payload)
    } else {
      await createModelData('baseinfo', 'cardtype', payload)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    await fetchCardtypes()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.error || '保存失败')
  } finally { saving.value = false }
}

async function handleDelete(row: any) {
  const pk = row.uuid || row.pk
  if (!pk) return
  try {
    await ElMessageBox.confirm(`确定删除卡类「${row.cardname || row.cardtype}」？`, '确认', { type: 'warning' })
    await updateModelData('baseinfo', 'cardtype', pk, { flag: 'N' })
    ElMessage.success('已删除')
    await fetchCardtypes()
  } catch {}
}

async function loadDiscountRules(cardtype: string) {
  if (!cardtype) return
  try {
    const res = await getCardtypeDiscountRules(cardtype)
    discountRules.value = (res.data.results || []).map((r: any) => ({
      pk: r.pk, ttype: r.ttype, discountclass: r.discountclass,
      discounttype: r.discounttype, disc: r.disc, price: r.price,
      consume_flag: r.consume_flag,
    }))
  } catch { discountRules.value = [] }
}

function addDiscountRule() {
  discountRules.value.push({
    pk: '', ttype: 'S', discountclass: '', discounttype: 'DISC',
    disc: 1, price: 0, consume_flag: 'Y',
  })
}

async function saveDiscountRules() {
  const cardtype = form.value.cardtype
  if (!cardtype) { ElMessage.warning('请先保存卡类基本信息'); return }
  savingRules.value = true
  try {
    const rules = discountRules.value
      .filter(r => r.discountclass)
      .map(r => ({ ...r, disc: r.disc || 0, price: r.price || 0 }))
    await saveCardtypeDiscountRules(cardtype, rules)
    ElMessage.success('折扣规则已保存')
    await loadDiscountRules(cardtype)
  } catch { ElMessage.error('保存折扣规则失败') }
  finally { savingRules.value = false }
}

function openRulerDialog() {
  rulerForm.value = { id: '', rulername: '', ruler: '' }
  rulerDialogVisible.value = true
}

async function saveRulerRow() {
  if (!rulerForm.value.rulername || !rulerForm.value.ruler) {
    ElMessage.warning('请填写规则名称和规则文本')
    return
  }
  savingRuler.value = true
  try {
    await saveRuler(rulerForm.value)
    ElMessage.success('规则已保存')
    rulerDialogVisible.value = false
    const res = await getRulerList()
    rulers.value = res.data.results || []
  } catch (e: any) {
    ElMessage.error(e.response?.data?.message || '保存规则失败')
  } finally { savingRuler.value = false }
}

onMounted(async () => {
  await loadOptions()
  await fetchCardtypes()
})
</script>

<style scoped>
.cardtype-admin { padding: 4px; }
.list-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.rule-toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 13px; color: #606266; }
.code-link { color: #409EFF; cursor: pointer; }
.code-link:hover { text-decoration: underline; }
</style>
