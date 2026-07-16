<template>
  <div class="cashier-page">
    <h2 style="margin:0 0 12px;font-size:18px;font-weight:600">手工开单</h2>
    <div class="main-layout">
      <div class="layout-left">
        <el-card shadow="never" class="section-card flex-1">
          <template #header>
            <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
              <span>选择项目</span>
              <el-radio-group v-model="itemTab" size="small">
                <el-radio-button value="S">服务</el-radio-button>
                <el-radio-button value="G">商品</el-radio-button>
                <el-radio-button value="C">卡类</el-radio-button>
              </el-radio-group>
              <el-input v-model="itemKeyword" placeholder="搜索" clearable size="small" style="width:130px" />
            </div>
          </template>
          <div class="item-grid">
            <div v-for="item in filteredItems" :key="item.code" class="item-card" @click="addToCart(item)">
              <div class="item-name">{{ item.name }}</div>
              <div class="item-price">¥{{ parseFloat(item.price ?? 0).toFixed(0) }}</div>
            </div>
            <el-empty v-if="!filteredItems.length" description="无匹配项目" />
          </div>
        </el-card>
      </div>
      <div class="layout-right">
        <el-card shadow="never" class="section-card">
          <template #header><span>选择客户</span></template>
          <el-input v-model="vipKeyword" placeholder="姓名/手机号/会员号" clearable @keyup.enter="searchVip">
            <template #append><el-button @click="searchVip">搜索</el-button></template>
          </el-input>
          <div v-if="searchResults.length" class="search-results">
            <div v-for="vip in searchResults" :key="vip.uuid" class="result-item" @click="selectVip(vip)">
              <span style="font-weight:500">{{ vip.vname }}</span>
              <el-tag size="small" type="info">{{ vip.viplevel }}</el-tag>
              <span style="font-size:12px;color:#909399;margin-left:8px">#{{ vip.vcode }}</span>
            </div>
          </div>
          <div v-if="noResults" style="font-size:13px;color:#909399;padding:8px;text-align:center">未找到</div>
          <div v-if="selectedVip" style="margin-top:8px;padding:8px;background:#f5f7fa;border-radius:4px">
            <div style="font-weight:500;font-size:14px">{{ selectedVip.vname }}
              <el-tag size="small">{{ selectedVip.viptype === "10" ? "会员" : "散客" }}</el-tag>
            </div>
            <div style="font-size:12px;color:#909399">{{ selectedVip.vcode }} | {{ selectedVip.mtcode }}</div>
          </div>
        </el-card>
        <el-card v-if="selectedVip && vipCards.length" shadow="never" class="section-card card-scroll" style="margin-top:0">
          <template #header>名下卡片 ({{ vipCards.length }})</template>
          <el-collapse v-model="activeCardGroups">
            <el-collapse-item v-for="(g, pi) in cardGroups" :key="pi" :title="g.title" :name="pi">
              <div v-for="card in g.cards" :key="card.uuid" class="cg-card" @click="selectCard(card)">
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <div><span style="font-weight:500;font-size:13px">{{ card.ccode }}</span>
                    <span style="font-size:12px;color:#909399;margin-left:6px">{{ card.cardname }}</span></div>
                  <div style="text-align:right;flex-shrink:0">
                    <div style="font-size:13px;font-weight:600;color:#e6a23c">{{ card.comptype === "times" ? (card.leftqty ?? 0) + "次" : "¥" + parseFloat(card.leftmoney ?? 0).toFixed(0) }}</div>
                    <div style="font-size:11px;color:#c0c4cc">¥{{ parseFloat(card.s_price ?? 0).toFixed(2) }}/次</div>
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
        <el-card shadow="never" class="section-card flex-1" style="margin-top:0">
          <template #header><span>开单明细</span><el-button text type="danger" size="small" @click="clearCart">清空</el-button></template>
          <el-table :data="cart" size="small" stripe max-height="260">
            <el-table-column label="项目" min-width="100"><template #default="{ row }">{{ row.name }}</template></el-table-column>
            <el-table-column label="类型" width="50"><template #default="{ row }">{{ ttypeLabel(row.ttype) }}</template></el-table-column>
            <el-table-column label="数量" width="60" align="right"><template #default="{ row }">{{ row.qty }}</template></el-table-column>
            <el-table-column label="单价" width="60" align="right"><template #default="{ row }">¥{{ parseFloat(row.price ?? 0).toFixed(2) }}</template></el-table-column>
            <el-table-column label="操作" width="40"><template #default="{ $index }"><el-button text type="danger" size="small" @click="cart.splice($index,1)">×</el-button></template></el-table-column>
          </el-table>
          <el-empty v-if="!cart.length" description="请从左侧选择项目" />
          <div v-if="cart.length" style="margin-top:8px;display:flex;justify-content:space-between;align-items:center">
            <span style="font-size:16px;font-weight:700;color:#e6a23c">¥{{ cartTotal.toFixed(2) }}</span>
            <el-button type="primary" size="default" :loading="saving" @click="saveHung">保存挂账</el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue"
import { ElMessage } from "element-plus"
import { searchVip as apiSearchVip, getVipCards } from "@/api/vip"
import { getServiceItems, getGoodsItems, getCardtypeItems, saveHungOrder } from "@/api/cashier"

const company = localStorage.getItem("genesis_pc_company") || ""
const vipKeyword = ref("")
const selectedVip = ref<any>(null)
const searchResults = ref<any[]>([])
const noResults = ref(false)
const vipCards = ref<any[]>([])
const selectedCard = ref<any>(null)
const activeCardGroups = ref<any[]>([])
const itemTab = ref("S")
const itemKeyword = ref("")
const allItems = ref<any[]>([])
const cart = ref<any[]>([])
const saving = ref(false)

async function searchVip() {
  const kw = vipKeyword.value.trim()
  if (!kw) return
  selectedVip.value = null; noResults.value = false; searchResults.value = []
  try {
    const res = await apiSearchVip(kw) as any
    const list = res.data?.results ?? (Array.isArray(res.data) ? res.data : [])
    if (list.length === 1) selectVip(list[0])
    else if (list.length > 1) searchResults.value = list
    else noResults.value = true
  } catch { noResults.value = true }
}

function selectVip(vip: any) {
  selectedVip.value = vip
  searchResults.value = []
  fetchVipCards(vip.uuid)
  fetchItems()
}

async function fetchVipCards(uuid: string) {
  try {
    const res = await getVipCards(uuid)
    const raw = Array.isArray(res.data) ? res.data : res.data?.results ?? []
    const filtered = raw.filter((c: any) => {
      if (c.comptype === "times" && (c.leftqty ?? 0) <= 0) return false
      if (c.comptype === "amount" && c.stype === "P" && (c.leftmoney ?? 0) <= 0) return false
      return true
    })
    vipCards.value = filtered
    const count = new Set(filtered.map((c: any) => c.promotionsid || "0")).size
    activeCardGroups.value = Array.from({length: count}, (_, i) => i)
  } catch { vipCards.value = [] }
}

const cardGroups = computed(() => {
  const pidMap: Record<string, any[]> = {}
  for (const card of vipCards.value) {
    const pid = card.promotionsid || "0"
    if (!pidMap[pid]) pidMap[pid] = []
    pidMap[pid].push(card)
  }
  const result: any[] = []
  for (const [pid, cards] of Object.entries(pidMap)) {
    const pidLabel = pid === "0" ? "正常销售" : cards[0]?.promotionname || "活动"
    result.push({title: pidLabel + " (" + cards.length + "张)", cards})
  }
  return result
})

function selectCard(card: any) { selectedCard.value = card }

watch(itemTab, () => { itemKeyword.value = ""; fetchItems() })

function fetchItems() {
  const api = itemTab.value === "S" ? getServiceItems : itemTab.value === "G" ? getGoodsItems : getCardtypeItems
  api().then(res => { allItems.value = Array.isArray(res.data) ? res.data : res.data?.results ?? [] }).catch(() => { allItems.value = [] })
}

const filteredItems = computed(() => {
  const kw = itemKeyword.value.trim().toLowerCase()
  if (!kw) return allItems.value
  return allItems.value.filter((i: any) => (i.name || "").toLowerCase().includes(kw))
})

function ttypeLabel(t: string): string {
  return {S: "服务", G: "商品", C: "售卡", I: "充值"}[t] || t
}

function addToCart(item: any) {
  const ex = cart.value.find((c: any) => c.code === item.code && c.ttype === (item.ttype || itemTab.value))
  if (ex) { ex.qty++; return }
  cart.value.push({code: item.code, name: item.name, price: parseFloat(item.price ?? 0), qty: 1, ttype: item.ttype || itemTab.value, stype: "N", payMethod: "cash", availableCards: [], pmcode: "", asscode1: ""})
}

function clearCart() { cart.value = [] }

const cartTotal = computed(() => cart.value.reduce((s: number, i: any) => s + i.price * i.qty, 0))

async function saveHung() {
  if (!selectedVip.value || !cart.value.length) return
  saving.value = true
  try {
    const items = cart.value.map((i: any) => ({ttype: i.ttype, srvcode: i.code, s_qty: i.qty, s_price: i.price, pay_type: i.payMethod}))
    await saveHungOrder({vipuuid: selectedVip.value.uuid, storecode: selectedVip.value.storecode || "01", items})
    ElMessage.success("挂账保存成功")
    cart.value = []
  } catch (e: any) { ElMessage.error("保存失败: " + (e.message || "")) }
  finally { saving.value = false }
}
</script>

<style scoped>
.cashier-page { padding:16px; height:calc(100vh - 60px); display:flex; flex-direction:column; }
.main-layout { display:flex; gap:16px; flex:1; min-height:0; }
.layout-left { width:420px; flex-shrink:0; display:flex; flex-direction:column; overflow-y:auto; }
.layout-right { flex:1; display:flex; flex-direction:column; gap:10px; min-width:0; overflow-y:auto; }
.section-card { display:flex; flex-direction:column; }
.section-card.flex-1 { flex:1; min-height:100px; }
:deep(.section-card .el-card__body) { flex:1; overflow:auto; }
.card-scroll { max-height:250px; overflow-y:auto; }
.item-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(110px,1fr)); gap:6px; }
.item-card { padding:6px; border:1px solid #ebeef5; border-radius:4px; cursor:pointer; text-align:center; }
.item-card:hover { border-color:#409eff; background:#ecf5ff; }
.item-name { font-size:12px; }
.item-price { font-size:13px; font-weight:600; color:#e6a23c; }
.cg-card { padding:6px 8px; margin-bottom:3px; border:1px solid #ebeef5; border-radius:4px; cursor:pointer; }
.cg-card:hover { border-color:#409eff; background:#ecf5ff; }
.search-results { margin-top:8px; border:1px solid #ebeef5; border-radius:4px; max-height:200px; overflow-y:auto; }
.result-item { padding:6px 8px; cursor:pointer; border-bottom:1px solid #f0f0f0; }
.result-item:hover { background:#ecf5ff; }
</style>