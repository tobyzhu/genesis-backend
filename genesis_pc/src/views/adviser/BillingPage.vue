<template>
  <div class="cashier-page">
    <h2 style="margin:0 0 16px 0;font-size:18px;font-weight:600">手工开单</h2>

    <div class="main-layout">
      <div class="layout-top">
      <!-- 左侧：选品区 -->
      <div class="layout-left">
        <!-- 客人搜索 -->
        <el-card shadow="never" class="section-card">
          <el-input
            v-model="vipKeyword"
            placeholder="输入姓名/手机号/会员号搜索"
            clearable
            @keyup.enter="searchVip"
          >
            <template #append>
              <el-button @click="searchVip">搜索</el-button>
            </template>
          </el-input>

          <!-- 搜索结果列表（多人匹配时显示） -->
          <div v-if="searchResults.length > 1" class="search-results">
            <div
              v-for="vip in searchResults"
              :key="vip.uuid"
              class="search-result-item"
              @click="selectVip(vip)"
            >
              <div class="sr-name">{{ vip.vname }}
                <el-tag size="small" type="info">{{ vip.viplevel || '--' }}</el-tag>
              </div>
             <div class="sr-detail">
               <span>会员号: {{ vip.vcode }}</span>
               <span>手机: {{ vip.mtcode }}</span>
                <span v-if="vip.ecode" style="margin-left:8px;color:#409eff">顾问:{{ vip.ecode }}</span>
             </div>
            </div>
          </div>
          <div v-if="noResults" class="no-results">未找到匹配会员</div>

          <div v-if="selectedVip" class="vip-info">
            <div class="vip-name">{{ selectedVip.vname }}
              <el-tag size="small" type="info">{{ selectedVip.viplevel || '无等级' }}</el-tag>
              <el-tag size="small">{{ selectedVip.viptype === '10' ? '会员' : '散客' }}</el-tag>
            </div>
           <div class="vip-detail">
             <span>会员号: {{ selectedVip.vcode }}</span>
             <span>手机: {{ selectedVip.mtcode }}</span>
            </div>
            <div v-if="selectedVip.ecode || selectedVip.ecode2" class="vip-detail" style="margin-top:4px">
              <span v-if="selectedVip.ecode">顾问: {{ empName(selectedVip.ecode) }}</span>
              <span v-if="selectedVip.ecode2">美疗师: {{ empName(selectedVip.ecode2) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 名下卡片 -->
        <el-card v-if="selectedVip && vipCards.length" shadow="never" class="section-card card-scroll">
          <template #header>名下卡片</template>
          <el-collapse v-model="activeCardGroups" class="card-collapse">
            <el-collapse-item v-for="(g, pi) in cardGroups" :key="pi" :title="g.promotionName + ' (' + totalCards(g) + '张)'" :name="pi">
              <div v-for="(ctg, ci) in g.comptypeGroups" :key="ci" class="cg-sub">
                <div class="cg-sub-title">{{ ctg.typeName }}</div>
                <div
                  v-for="card in ctg.cards"
                  :key="card.uuid"
                  class="cg-card"
                  :class="['cg-card', { selected: selectedCard?.uuid === card.uuid, 'status-p': card.status === 'P' }]"
                @click="selectCard(card)"
                  @dblclick="onCardDblClick(card)"
                >
                  <div class="cg-card-left">
                    <div class="cg-card-code">{{ card.ccode }}</div>
                    <div class="cg-card-name">{{ card.cardname }}
                      <el-tag v-if="card.stype === 'P'" size="small" type="warning" style="margin-left:4px">赠送</el-tag>
                      <el-tag v-if="card.status === 'P'" size="small" type="warning" style="margin-left:4px">挂账</el-tag>
                    </div>
                  </div>
                  <div class="cg-card-right">
                    <div class="cg-card-amount">
                      {{ card.comptype === 'times' ? (card.leftqty ?? 0) + '次' : '¥' + parseFloat(card.leftmoney ?? 0).toFixed(0) }}
                    </div>
                    <div v-if="card.valdate" class="cg-card-expire">{{ card.valdate ? formatCardDate(card.valdate) : '' }}</div>
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

      </div>
      <!-- 右侧：选品区 -->
      <div class="layout-right">
        <!-- 选品区 -->
        <el-card shadow="never" class="section-card flex-1">
          <template #header>
            <div style="display:flex;gap:12px;align-items:center">
              <span>选择项目</span>
              <el-radio-group v-model="itemTab" size="small">
                <el-radio-button value="S">服务</el-radio-button>
                <el-radio-button value="G">商品</el-radio-button>
                <el-radio-button value="C">售卡</el-radio-button>
                <el-radio-button value="I">充值</el-radio-button>
              </el-radio-group>
              <el-input
                v-model="itemKeyword"
                placeholder="搜索项目"
                clearable
                size="small"
                style="width:180px"
              />
            </div>
          </template>
          <template v-if="itemTab === 'I'">
            <div style="display:flex;gap:8px;margin-bottom:10px">
              <el-radio-group v-model="rechargeMode" size="small">
                <el-radio-button value="recharge">充值</el-radio-button>
                <el-radio-button value="refund">退卡</el-radio-button>
              </el-radio-group>
            </div>
            <div class="item-grid">
              <div v-for="card in refundableCards" :key="card.ccode" class="item-card" style="position:relative">
                <div class="item-name">{{ card.cardname }}</div>
                <div style="font-size:11px;color:#909399">{{ card.ccode }}</div>
                <div class="item-price" style="font-size:13px">
                  <template v-if="card.comptype === 'times'">余次: {{ card.leftqty ?? 0 }} 次</template>
                  <template v-else>余额: ¥{{ parseFloat(card.leftmoney ?? 0).toFixed(0) }}</template>
                </div>
                <div style="display:flex;gap:4px;margin-top:6px">
                  <el-input-number v-model="rechargeAmounts[card.ccode]" :min="0" :step="rechargeMode === 'refund' && card.comptype === 'times' ? 1 : 100" size="small" :controls="false" style="width:80px" />
                  <el-button v-if="rechargeMode === 'recharge'" size="small" type="primary" @click="addRecharge(card)">充值</el-button>
                  <el-button v-else size="small" type="danger" @click="addRefund(card)">退款</el-button>
                </div>
              </div>
              <el-empty v-if="!refundableCards.length" :description="rechargeMode === 'recharge' ? '无可用储值卡' : '无可用退卡'" />
            </div>
          </template>
          <template v-else>
            <template v-if="itemTab === 'C'">
              <div style="display:flex;gap:8px;margin-bottom:10px">
                <el-radio-group v-model="cardSaleMode" size="small">
                  <el-radio-button value="amount">储值卡</el-radio-button>
                  <el-radio-button value="times">疗程卡</el-radio-button>
                </el-radio-group>
              </div>
              <div class="item-grid">
                <div v-for="item in cardSaleItems" :key="item.code" class="item-card" @click="addCardSale(item)">
                  <div class="item-name">{{ item.name }}</div>
                  <div class="item-price">¥{{ parseFloat(item.price ?? 0) }}</div>
                </div>
                <el-empty v-if="!cardSaleItems.length" description="无匹配项目" />
              </div>
            </template>
            <template v-else>
              <div class="item-grid">
                <div v-for="item in filteredItems" :key="item.code" class="item-card" @click="addToCart(item)">
                  <div class="item-name">{{ item.name }}</div>
                  <div class="item-price">{{ itemTab === 'C' ? '' : '¥' + parseFloat(item.price ?? 0) }}</div>
                </div>
                <el-empty v-if="!filteredItems.length" description="无匹配项目" />
              </div>
            </template>
          </template>
        </el-card>
      </div>

      </div>
      <div class="layout-bottom">
        <el-card shadow="never" class="section-card flex-1">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-weight:600">开单明细</span>
              <div style="display:flex;align-items:center;gap:12px">
                <template v-if="cart.length">
                  <div v-if="selectedCard" class="selected-card-info" style="margin:0;font-size:12px">
                    已选卡: {{ selectedCard.cardname }} ({{ selectedCard.ccode }})
                  </div>
                  <span style="font-size:16px;font-weight:700;color:#e6a23c">¥{{ cartTotal.toFixed(2) }}</span>
                </template>
                <el-button type="primary" size="small" :loading="saving" :disabled="!cart.length" @click="saveHung">
                  保存挂账
                </el-button>
                <el-button text type="danger" size="small" @click="clearCart">清空</el-button>
              </div>
            </div>
          </template>

          <el-table :data="cart" size="small" stripe :row-class-name="tableRowClassName" max-height="400">
            <el-table-column label="项目" min-width="110">
              <template #default="{ row }">{{ row.name }}</template>
            </el-table-column>
            <el-table-column label="类型" width="50">
              <template #default="{ row }">{{ ttypeLabel(row.ttype) }}</template>
            </el-table-column>
            <el-table-column label="属性" width="65">
              <template #default="{ row }">
                <el-select v-model="row.stype" size="small">
                  <el-option label="正常" value="N" />
                  <el-option label="赠送" value="P" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="数量" width="55" align="right">
              <template #default="{ row }">{{ row.qty }}</template>
            </el-table-column>
            <el-table-column label="单价" width="95" align="right">
              <template #default="{ row }">¥{{ parseFloat(row.price ?? 0).toFixed(2) }}</template>
            </el-table-column>
            <el-table-column label="折扣率" width="75" align="right">
              <template #default="{ row }">
                <el-input-number v-model="row.secdisc" :min="0" :max="1" :step="0.05" size="small" :controls="false" style="width:65px" />
              </template>
            </el-table-column>
            <el-table-column label="金额折扣" width="80" align="right">
              <template #default="{ row }">
                <el-input-number v-model="row.srvmondisc" :min="0" :step="1" size="small" :controls="false" style="width:70px" />
              </template>
           </el-table-column>
           <el-table-column label="小计" width="115" align="right">
             <template #default="{ row }">¥{{ (parseFloat(row.price ?? 0) * (row.qty ?? 1) * (row.secdisc ?? 1) - (row.srvmondisc ?? 0)).toFixed(2) }}</template>
           </el-table-column>
            <el-table-column label="正/退" width="50" align="center">
              <template #default="{ row }">
                <template v-if="row.ttype === 'S' || row.ttype === 'G'">
                 <el-button v-if="(row.qty ?? 0) >= 0" size="small" type="primary" :icon="Check" circle @click.stop="toggleRefund(row)" />
                 <el-button v-else size="small" type="danger" :icon="Close" circle @click.stop="toggleRefund(row)" />
                </template>
                <span v-else style="color:#c0c4cc;font-size:12px">--</span>
              </template>
            </el-table-column>
            <el-table-column label="扣款方式" width="150">
              <template #default="{ row }">
                <el-select v-model="row.payMethod" size="small" @change="(v:any)=>onPayMethodChange(row,v)">
                  <el-option label="现金" value="cash" />
                  <el-option v-for="c in row.availableCards" :key="c.ccode"
                    :label="cardOptionLabel(c)"
                    :value="'card:'+c.ccode" />
                  <el-option label="储值卡余额" value="balance" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="付款卡号" width="110">
              <template #default="{ row }">
                <template v-if="row.payMethod?.startsWith('card:')">
                  {{ row.payMethod.slice(5) }}
                </template>
                <span v-else style="color:#c0c4cc;font-size:12px">--</span>
              </template>
            </el-table-column>
            <el-table-column label="开单" width="90">
              <template #default="{ row }">
                <el-select v-model="row.pmcode" size="small" filterable placeholder="选择">
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="美疗师1" width="95">
              <template #default="{ row }">
                <el-select v-model="row.asscode1" size="small" filterable placeholder="选择">
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="美疗师2" width="95">
              <template #default="{ row }">
                <el-select v-model="row.asscode2" size="small" filterable placeholder="选择">
                  <el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="45">
              <template #default="{ $index }">
                <el-button text type="danger" size="small" @click="cart.splice($index,1)">×</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty v-if="!cart.length" description="请从左侧添加项目" />

        </el-card>
      </div>


    </div>
</div>



<el-dialog v-model="showPriceSelector" title="疗程卡设置" width="380px">
  <el-form size="small" label-width="90px">
    <el-form-item label="数量（次）">
      <el-input-number v-model="editQty" :min="1" :step="1" size="small" style="width:100%" />
    </el-form-item>
    <el-form-item label="总金额（元）">
      <el-input-number v-model="editAmount" :min="0" :step="100" size="small" style="width:100%" />
    </el-form-item>
    <el-form-item label="单价（元）">
      <span style="font-weight:600;color:#e6a23c">¥{{ editUnitPrice.toFixed(2) }}</span>
    </el-form-item>
    <el-form-item label="折扣率（%）">
      <el-input-number v-model="editDiscountPct" :min="0" :max="100" :step="5" size="small" style="width:100%" />
    </el-form-item>
    <el-form-item label="金额折扣（元）">
      <el-input-number v-model="editDiscountAmt" :step="10" size="small" style="width:100%" />
    </el-form-item>
    <el-form-item label="小计（元）">
      <span style="font-size:16px;font-weight:700;color:#e6a23c">¥{{ editSubtotal.toFixed(2) }}</span>
    </el-form-item>
  </el-form>
  <template #footer>
    <el-button size="small" @click="showPriceSelector = false">取消</el-button>
    <el-button size="small" type="primary" @click="confirmCardSale">确认加入</el-button>
  </template>
</el-dialog>

</template>
<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { VipCard } from '@/types'
import { ElMessage } from 'element-plus'
import { searchVip as apiSearchVip, getVipCards } from '@/api/vip'
import request from '@/api/request'
import { getServiceItems, getGoodsItems, getCardtypeItems, saveHungOrder, getCardtypeServiceItems, getCardtypePrices } from '@/api/cashier'

const company = localStorage.getItem('genesis_pc_company') || ''

// ---- 客人 ----
const vipKeyword = ref('')
const selectedVip = ref<Vip | null>(null)
const searchResults = ref<Vip[]>([])
const activeCardGroups = ref<number[]>([])
const noResults = ref(false)
const vipCards = ref<VipCard[]>([])
const selectedCard = ref<VipCard | null>(null)

async function searchVip() {
  const kw = vipKeyword.value.trim()
  if (!kw) return
  selectedVip.value = null
  noResults.value = false
  try {
    const res = await apiSearchVip(kw)
    const list = res.data?.results ?? (Array.isArray(res.data) ? res.data : [])
    if (list.length === 1) {
      selectVip(list[0])
      searchResults.value = []
    } else if (list.length > 1) {
      searchResults.value = list
      noResults.value = false
    } else {
      searchResults.value = []
      noResults.value = true
      vipCards.value = []
    }
  } catch { searchResults.value = []; noResults.value = true }
}
const dblClickCard = ref<VipCard | null>(null)

function onCardDblClick(card: VipCard) {
  dblClickCard.value = card
  autoAddCardItems(card)
  // 300ms 后重置双击标记
  setTimeout(() => { dblClickCard.value = null }, 300)
}

function empName(ecode: string): string {
  const emp = employees.value.find(e => e.ecode === ecode)
  return emp ? emp.ename + ' (' + ecode + ')' : ecode
}

function selectCard(card: VipCard) {
  // 双击时第一个 click 会被 dblClickCard 拦截
  if (dblClickCard.value) return
  selectedCard.value = card
  cart.value.forEach((item: CartItem) => {
    if (!item.availableCards.find((c: VipCard) => c.ccode === card.ccode)) {
      item.availableCards.unshift(card)
    }
  })
}

function selectVip(vip: Vip) {
  selectedVip.value = vip
  selectedCard.value = null
  cart.value = []
  searchResults.value = []
  fetchVipCards(vip.uuid); fetchItems()
  // 加载门店员工列表
  const storecode = localStorage.getItem('genesis_pc_storecode') || ''
  getEmployeeList({ company, storecode }).then(res => {
    console.log("💼 getEmployeeList response:", res.data)

    const list = Array.isArray(res.data) ? res.data : res.data?.results ?? []
    employees.value = list.map((e: any) => ({ ecode: e.ecode || e.usercode || '', ename: e.ename || e.username || '' }))
    console.log("💼 employees updated:", employees.value.length, employees.value.slice(0, 3))
  }).catch(() => { employees.value = [] })
}

async function fetchVipCards(uuid: string) {
  try {
    const res = await getVipCards(uuid)
    const raw = (Array.isArray(res.data) ? res.data : res.data?.results ?? []) as VipCard[]
    // 过滤掉余额/余次为0的卡
    const filtered = raw.filter((card: VipCard) => {
      if (card.status === 'P') return true  // 挂账中的卡总是显示
      if (card.comptype === 'times' && (card.leftqty ?? 0) <= 0) return false
      if (card.comptype === 'amount' && card.stype === 'P' && (card.leftmoney ?? 0) <= 0) return false
      return true
    })
    vipCards.value = filtered
    const count = new Set(raw.map((c: VipCard) => c.promotionsid || '0')).size
    activeCardGroups.value = Array.from({ length: count }, (_, i) => i)
  } catch (err: unknown) { 
    vipCards.value = [] 
  }
}

const cardGroups = computed(() => {
  const data = vipCards.value
  const pidMap: Record<string, Record<string, any[]>> = {}
  for (const card of data) {
    const pid = card.promotionsid || '0'
    const ct = card.comptype || 'other'
    if (!pidMap[pid]) pidMap[pid] = {}
    if (!pidMap[pid][ct]) pidMap[pid][ct] = []
    pidMap[pid][ct].push(card)
  }
  const result: CardGroup[] = []
  for (const [pid, ctGroups] of Object.entries(pidMap)) {
    const promotionName = pid === '0' ? '正常销售' : ctGroups[Object.keys(ctGroups)[0]][0]?.promotionname || '活动:' + pid
    const comptypeGroups: Array<{ typeName: string; cards: VipCard[] }> = []
    for (const [ct, cards] of Object.entries(ctGroups)) {
      const ctName = ct === 'amount' ? '储值卡' : ct === 'times' ? '计次卡' : ct === 'period' ? '计时卡' : ct
      comptypeGroups.push({ typeName: ctName + ' (' + cards.length + '张)', cards })
    }
    result.push({ promotionName, comptypeGroups })
  }
  return result
})

function formatCardDate(d: string): string {
  return d ? d.replace(/^(\d{4})(\d{2})(\d{2})$/, '$1-$2-$3') : ''
}

function totalCards(g: CardGroup): number {
  let n = 0
  for (const ctg of g.comptypeGroups) n += ctg.cards.length
  return n
}

function cardOptionLabel(c: VipCard): string {
  return c.cardname + ' (' + c.ccode + ')' + (c.comptype === 'times' ? '(' + c.leftqty + '次)' : '')
}

async function autoAddCardItems(card: VipCard) {
  // 计次卡：自动加载卡类关联的服务项目
  console.log('autoAddCardItems:', card.ccode, 'comptype:', card.comptype, 'uuid:', card.cardtypeuuid, 'code:', card.cardtype)
  if (card.comptype !== 'times') return
  if (!card.cardtypeuuid && !card.cardtype) {
    console.log('autoAddCardItems: 卡无 cardtypeuuid 和 cardtype，跳过')
    return
  }
  try {
    const res = await getCardtypeServiceItems(card.cardtypeuuid || '', card.cardtype || '')
    const items = (Array.isArray(res.data) ? res.data : res.data?.results ?? []) as CartableItem[]
    console.log('autoAddCardItems: 返回项目数:', items.length, items)
    for (const item of items) {
      const existing = cart.value.find((c: CartItem) => c.code === item.code && c.ttype === item.ttype)
      if (!existing) {
        cart.value.push({
          code: item.code,
          name: item.name,
          price: parseFloat(item.price ?? 0),
          qty: 1,
          ttype: item.ttype,
          stype: card.stype || 'N',
         payMethod: 'card:' + card.ccode,
          pmcode: selectedVip.value?.ecode || '',
          asscode1: selectedVip.value?.ecode2 || '',
          asscode2: '',
         availableCards: [card],
        })
      }
    }
  } catch (err: unknown) {
    console.log('获取卡类服务项目失败:', err instanceof Error ? err.message : err)
  }
}

// ---- 选品 ----
const itemTab = ref<'S'|'G'|'C'|'I'>('S')
const employees = ref<Array<{ecode: string, ename: string}>>([])

// 组件初始化时加载本店员工列表
;(async () => {
    console.log("💼 fetchEmployees: company=", company, "storecode=", localStorage.getItem('genesis_pc_storecode'))
  try {
    const sc = localStorage.getItem('genesis_pc_storecode') || ''
    const res = await request.get('/adviser/get_bookingable_empllist/', { params: { company, storecode: sc } })
    const list = Array.isArray(res.data) ? res.data : res.data?.results ?? []
    employees.value = list.map((e: any) => ({ ecode: e.ecode || '', ename: e.ename || '' }))
  } catch { /* ignore */ }
})()
const itemCode = ref('')
const itemName = ref('')
const cardSaleMode = ref<'amount'|'times'>('amount')
const showPriceSelector = ref(false)
const editQty = ref(1)
const editAmount = ref(0)
const editDiscountPct = ref(100)
const editDiscountAmt = ref(0)

const editRawPrice = computed(() => editQty.value > 0 ? editAmount.value / editQty.value : 0)
const editUnitPrice = computed(() => editQty.value > 0 ? Math.round(editAmount.value / editQty.value * 100) / 100 : 0)
const editSubtotal = computed(() => editQty.value * editUnitPrice.value * (editDiscountPct.value / 100) - editDiscountAmt.value)

let _recalc = false

// 修改数量：保持单价不变，重新计算总金额
watch(editQty, (newQty, oldQty) => {
  if (_recalc || !oldQty || !editAmount.value) return
  _recalc = true
  const unitPrice = editAmount.value / oldQty
  editAmount.value = Math.round(newQty * unitPrice * 100) / 100
  _recalc = false
})

// 数量或总金额变化时自动计算金额折扣（补齐四舍五入差额）
watch([editQty, editAmount], () => {
  if (_recalc || !editQty.value || !editAmount.value) return
  const rp = Math.round((editAmount.value / editQty.value) * 100) / 100
  editDiscountAmt.value = +(editQty.value * rp - editAmount.value).toFixed(2)
})

const cardSaleItems = computed(() =>
  allItems.value.filter((i: CartableItem) => i.comptype === cardSaleMode.value)
)

function addCardSale(item: CartableItem) {
  if (cardSaleMode.value === 'amount') {
    // 储值卡：直接加入购物车
    addToCart(item)
  } else {
    // 疗程卡：获取价格选项并用第一个预填
    itemCode.value = item.code
    itemName.value = item.name
    fetchCardPrices(item.code).then(prices => {
      if (prices.length > 0) {
        const p = prices[0]
        editQty.value = p.qty
        editAmount.value = p.amount
        editDiscountPct.value = 100
        editDiscountAmt.value = 0
        showPriceSelector.value = true
      } else {
        addToCart(item)
      }
    })
  }
}

function confirmCardSale() {
  const qty = editQty.value
  const unitPrice = editUnitPrice.value
  const name = itemName.value + ' (' + qty + '次)'
  const secdisc = editDiscountPct.value / 100
  const srvmondisc = editDiscountAmt.value
  
  const cartItem = { 
    code: itemCode.value, 
    name, 
    price: unitPrice,
    qty, 
    ttype: 'C',
    secdisc,
    srvmondisc,
  }
  addToCart(cartItem)
  // 更新购物车项中的折扣信息
  const last = cart.value[cart.value.length - 1]
  if (last) {
    last.secdisc = secdisc
    last.srvmondisc = srvmondisc
    last.price = unitPrice
    last.qty = qty
  }
  showPriceSelector.value = false
}

async function fetchCardPrices(cardtype: string): Promise<Array<{qty: number, price: number, amount: number}>> {
  try {
    const res = await getCardtypePrices(cardtype)
    const data = Array.isArray(res.data) ? res.data : []
    return data.map((d: any) => ({ qty: d.qty || 1, price: d.price || 0, amount: d.amount || 0 }))
  } catch {
    return []
  }
}

const rechargeMode = ref<'recharge'|'refund'>('recharge')
const rechargeAmounts = ref<Record<string, number>>({})

const refundableCards = computed(() =>
  vipCards.value.filter((c: VipCard) =>
    c.status !== 'P' && (rechargeMode.value === 'recharge' ? c.comptype === 'amount' : ['amount', 'times'].includes(c.comptype || ''))
  )
)

function addRecharge(card: VipCard) {
  const amount = rechargeAmounts.value[card.ccode] || 0
  if (amount <= 0) return
  const item = { code: card.ccode, name: card.cardname + ' 充值', price: amount, ttype: 'I' }
  addToCart(item as CartableItem)
  rechargeAmounts.value[card.ccode] = 0
}

function addRefund(card: VipCard) {
  const amount = rechargeAmounts.value[card.ccode] || 0
  if (amount <= 0) return
  const item = { code: card.ccode, name: card.cardname + ' 退款', price: -amount, ttype: 'I' }
  addToCart(item as CartableItem)
  rechargeAmounts.value[card.ccode] = 0
}

const itemKeyword = ref('')
const allItems = ref<CartableItem[]>([])
const itemsLoading = ref(false)

watch(itemTab, () => { itemKeyword.value = ''; fetchItems() })

async function fetchItems() {
  itemsLoading.value = true
  try {
    const api = itemTab.value === 'S' ? getServiceItems : itemTab.value === 'G' ? getGoodsItems : getCardtypeItems
    const res = await api()
    allItems.value = (Array.isArray(res.data) ? res.data : res.data?.results ?? []) as CartableItem[]
  } catch { allItems.value = [] }
  finally { itemsLoading.value = false }
}

const filteredItems = computed(() => {
  const kw = itemKeyword.value.trim().toLowerCase()
  if (!kw) return allItems.value
  return allItems.value.filter((i: CartableItem) =>
    (i.name || '').toLowerCase().includes(kw) || (i.code || '').toLowerCase().includes(kw)
  )
})

// ---- 购物车 ----
interface CartItem {
  code: string
  name: string
  price: number
  qty: number
  ttype: string
  stype: string
  secdisc: number
  srvmondisc: number
  payMethod: string
  pmcode: string
  asscode1: string
  asscode2: string
  availableCards: VipCard[]
}

const cart = ref<CartItem[]>([])

const itemClickGuard = new Map<string, number>()

function addToCart(item: CartableItem) {
  const now = Date.now()
  const last = itemClickGuard.get(item.code)
  if (last && now - last < 300) return
  itemClickGuard.set(item.code, now)
  const existing = cart.value.find((c: CartItem) => c.code === item.code)
  if (existing) {
    existing.qty++
    return
  }
  cart.value.push({
    code: item.code,
    name: item.name,
    price: parseFloat(item.price ?? 0),
    qty: 1,
    ttype: item.ttype || itemTab.value,
    stype: 'N',
    secdisc: 1,
    srvmondisc: 0,
    pmcode: selectedVip.value?.ecode || '',
    asscode1: selectedVip.value?.ecode2 || '',
    asscode2: '',
    payMethod: selectedCard.value ? 'card:' + selectedCard.value.ccode : 'cash',
    availableCards: selectedCard.value ? [selectedCard.value] : [],
  })
}

function ttypeLabel(t: string): string {
  const map: Record<string, string> = {S: '服务', G: '商品', C: '售卡', I: '充值'}
  return map[t] || t
}

function onPayMethodChange(row: CartItem, val: string) {
  row.payMethod = val
}

function clearCart() { cart.value = [] }
function toggleRefund(row: CartItem) {
  if ((row.qty ?? 0) >= 0) { row.qty = -Math.abs(row.qty || 1) }
  else { row.qty = Math.abs(row.qty || 1) }
}


const cartTotal = computed(() =>
  cart.value.reduce((s: number, i: CartItem) => s + i.price * i.qty * (i.secdisc ?? 1) - (i.srvmondisc ?? 0), 0)
)

function tableRowClassName({ row }: { row: CartItem }): string {
  return (row.qty ?? 0) < 0 ? 'refund-row' : ''
}

// ---- 保存挂账 ----
const saving = ref(false)
async function saveHung() {
  if (!selectedVip.value) return
  saving.value = true
  try {
    const items = cart.value.map((i: CartItem) => ({
      ttype: i.ttype,
      srvcode: i.code,
      s_qty: i.qty,
      s_price: i.price,
      stype: i.stype,
      secdisc: i.secdisc ?? 1,
      srvmondisc: i.srvmondisc ?? 0,
      pay_type: i.payMethod,
      card_ccode: i.payMethod?.startsWith('card:') ? i.payMethod.slice(5) : '',
      pmcode: i.pmcode || '',
      asscode1: i.asscode1 || '',
      asscode2: i.asscode2 || '',
      cardtype: i.ttype === 'I' ? (vipCards.value.find(function(c: VipCard) { return c.ccode === i.code; })?.cardtype || '') : (i.payMethod?.startsWith('card:') ? i.availableCards.find(c => c.ccode === i.payMethod.slice(5))?.cardtype : '') || '',
    }))
    const res = await saveHungOrder({
      vipuuid: selectedVip.value.uuid,
      storecode: selectedVip.value.storecode || '01',
      items,
    })
    if ((res.data as Record<string, any>)?.ok === true) {
      ElMessage.success('挂账保存成功')
      cart.value = []
      // 刷新名下卡片（新售卡会出现在列表中）
      if (selectedVip.value) fetchVipCards(selectedVip.value.uuid)
    } else {
      ElMessage.error((res.data as Record<string, any>)?.message || '保存失败')
    }
  } catch (err: unknown) {
    ElMessage.error('保存失败: ' + (err instanceof Error ? err.message : String(err)))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.cashier-page { padding: 16px; height: calc(100vh - 60px); display:flex; flex-direction:column; }
.main-layout { display:flex; flex-direction:column; gap:16px; flex:1; min-height:0; }
.layout-left { width:480px; flex-shrink:0; display:flex; flex-direction:column; overflow-y:auto; min-height:0; }
.layout-right { flex:1; display:flex; flex-direction:column; gap:10px; min-width:0; min-height:0; overflow-y:auto; }
.layout-top { flex:11; display:flex; gap:16px; min-height:0; overflow:hidden; }
.layout-bottom { flex:8; display:flex; flex-direction:column; gap:16px; min-height:0; overflow:hidden; }
.section-card { display:flex; flex-direction:column; }
.section-card.flex-1 { flex:1; min-height:150px; }
.card-scroll { flex:1; min-height:0; overflow-y:auto; }
.card-scroll :deep(.el-card__body) { padding:6px 10px; }
.cg-card.status-p { border-color:#e6a23c; background:#fef7e0; }
.card-scroll :deep(.el-card__header) { padding:6px 10px; font-size:13px; }
.card-collapse { border-top:none; }
.card-collapse :deep(.el-collapse-item__header) { font-size:12px; font-weight:600; padding:4px 8px; height:auto; line-height:1.4; }
.card-collapse :deep(.el-collapse-item__content) { padding-bottom:2px; }
:deep(.section-card .el-card__body) { flex:1; overflow:auto; }

.vip-info { margin-top:6px; padding:6px 10px; background:#f5f7fa; border-radius:6px; }
.search-results { margin-top:8px; border:1px solid #ebeef5; border-radius:6px; max-height:260px; overflow-y:auto; }
.search-result-item { padding:8px 10px; cursor:pointer; border-bottom:1px solid #f0f0f0; transition:.1s; }
.search-result-item:last-child { border-bottom:none; }
.search-result-item:hover { background:#ecf5ff; }
.sr-name { font-weight:500; font-size:14px; display:flex; align-items:center; gap:6px; }
.sr-detail { font-size:12px; color:#909399; margin-top:2px; display:flex; gap:12px; }
.no-results { margin-top:8px; padding:12px; text-align:center; color:#909399; font-size:13px; background:#fafafa; border-radius:6px; }
.vip-name { font-weight:600; font-size:14px; margin-bottom:2px; display:flex; align-items:center; gap:8px; }
.vip-detail { font-size:12px; color:#666; display:flex; gap:12px; }

.item-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:8px; }
.item-card { padding:8px 6px; border:1px solid #ebeef5; border-radius:6px; cursor:pointer; text-align:center; transition:.15s; overflow:hidden; }
.item-card:hover { border-color:#409eff; background:#ecf5ff; }
.item-name { font-size:13px; margin-bottom:4px; }
.item-price { font-size:14px; font-weight:600; color:#e6a23c; }

.cart-total { margin-top:12px; padding-top:12px; border-top:1px solid #ebeef5; }
.selected-card-info { font-size:13px; color:#409eff; margin-bottom:6px; }
.total-line { display:flex; justify-content:flex-end; align-items:center; gap:8px; font-size:16px; }
.total-amount { font-size:22px; font-weight:700; color:#e6a23c; }

.action-bar { display:flex; justify-content:flex-end; }

/* 卡片分组 */
.card-group { margin-bottom:12px; }

.cg-sub-title { font-size:11px; font-weight:500; color:#606266; padding:2px 8px; margin-bottom:2px; background:#f5f7fa; border-radius:4px; }
.cg-card { display:flex; justify-content:space-between; align-items:center; padding:5px 8px; margin-bottom:3px; border:1px solid #ebeef5; border-radius:5px; cursor:pointer; transition:.15s; background:#fff; }
.cg-card:hover { border-color:#409eff; background:#ecf5ff; }
.cg-card.selected { border-color:#409eff; background:#d9ecff; }
.cg-card-left { flex:1; min-width:0; }
.cg-card-code { font-size:12px; font-weight:500; color:#303133; }
.cg-card-name { font-size:12px; color:#909399; margin-top:2px; }
.cg-card-right { text-align:right; flex-shrink:0; }
.cg-card-amount { font-size:13px; font-weight:600; color:#e6a23c; }
.cg-card-expire { font-size:11px; color:#c0c4cc; margin-top:2px; }

.el-table .refund-row { background: #fef0f0; }
</style>
