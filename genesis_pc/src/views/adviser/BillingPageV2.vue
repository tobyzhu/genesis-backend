<template>
  <div class="billing-v2">
    <div class="header-bar">
      <h2 class="page-title">手工开单</h2>
      <div style="display:flex;align-items:center;gap:8px">
        <el-radio-group v-model="billingMode" size="small" @change="switchBillingMode">
          <el-radio-button value="normal">正常开单</el-radio-button>
          <el-radio-button value="refund">退款开单</el-radio-button>
        </el-radio-group>
      </div>
      <span v-if="selectedVip" class="header-vip">{{ selectedVip.vname }} <span class="header-vip-code">({{ selectedVip.vcode }})</span></span>
    </div>

    <div class="v2-layout">
      <!-- LEFT -->
      <div class="v2-left">
        <el-card shadow="never" class="section-card search-card">
          <el-input v-model="vipKeyword" placeholder="姓名 / 手机号 / 会员号" clearable @keyup.enter="searchVip">
            <template #append><el-button @click="searchVip">搜索</el-button></template>
          </el-input>
          <div v-if="searchResults.length > 1" class="search-results">
            <div v-for="vip in searchResults" :key="vip.uuid" class="sr-item" @click="selectVip(vip)">
              <div class="sr-name">{{ vip.vname }}<el-tag size="small" type="info">{{ vip.viplevel || '--' }}</el-tag></div>
              <div class="sr-detail"><span>{{ vip.vcode }}</span><span>{{ vip.mtcode }}</span></div>
            </div>
          </div>
          <div v-if="selectedVip" class="vip-card">
            <div class="vip-card-name">{{ selectedVip.vname }}
              <el-tag size="small" type="info">{{ selectedVip.viplevel || '无' }}</el-tag>
              <el-tag size="small">{{ selectedVip.viptype === '10' ? '会员' : '散客' }}</el-tag>
              <el-button text type="primary" size="small" style="margin-left:auto" @click="openVipProfile(selectedVip.uuid)">查看详情</el-button>
            </div>
            <div class="vip-card-info"><span>会员号: {{ selectedVip.vcode }}</span><span>手机: {{ selectedVip.mtcode }}</span></div>
            <div v-if="selectedVip.ecode || selectedVip.ecode2" class="vip-card-emp">
              <span v-if="selectedVip.ecode">顾问: {{ empName(selectedVip.ecode) }}</span>
              <span v-if="selectedVip.ecode2">美疗师: {{ empName(selectedVip.ecode2) }}</span>
            </div>
          </div>
        </el-card>
        <el-card v-if="selectedVip && vipCards.length" shadow="never" class="section-card card-list-card">
          <template #header>名下卡片 <span style="color:#909399;font-weight:400;font-size:12px">({{ vipCards.length }})</span></template>
          <el-collapse v-model="activeCardGroups" class="card-collapse">
            <el-collapse-item v-for="(g, pi) in cardGroups" :key="pi" :title="g.promotionName" :name="pi">
              <div v-for="(ctg, ci) in g.comptypeGroups" :key="ci">
                <div class="cg-sub-title">{{ ctg.typeName }}</div>
                <div v-for="card in ctg.cards" :key="card.uuid" draggable="true" class="cg-card"
                  :class="{ selected: selectedCard?.uuid === card.uuid, 'status-p': card.status === 'P' }"
                  @click="selectCard(card)" @dblclick="autoAddCardItems(card)"
                  @dragstart="onCardDragStart(card)" @contextmenu="showCardMenu($event, card)">
                  <div class="cg-card-left">
                    <div class="cg-card-code">{{ card.ccode }}</div>
                    <div class="cg-card-name">{{ card.cardname }}
                      <el-tag v-if="card.stype === 'P'" size="small" type="warning">赠送</el-tag>
                      <el-tag v-if="card.status === 'P'" size="small" type="warning">挂账</el-tag>
                    </div>
                  </div>
                  <div class="cg-card-right">
                    <div class="cg-card-amount">{{ card.comptype === 'times' ? (card.leftqty ?? 0) + '次' : '¥' + parseFloat(card.leftmoney ?? 0).toFixed(0) }}</div>
                    <div v-if="card.valdate" class="cg-card-expire">{{ String(card.valdate).replace(/^(\d{4})(\d{2})(\d{2})$/, '$1-$2-$3') }}</div>
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>
      </div>
      <!-- RIGHT -->
      <div class="v2-right">

        <el-card shadow="never" class="section-card">
          <template #header>
            <div class="item-selector-header">
              <el-radio-group v-model="itemTab" size="small">
                <el-radio-button value="S">服务</el-radio-button>
                <el-radio-button value="G">商品</el-radio-button>
                <el-radio-button value="C">售卡</el-radio-button>
                <el-radio-button value="I">充值</el-radio-button>
                <el-radio-button value="P">🎯 活动</el-radio-button>
              </el-radio-group>
              <template v-if="itemTab === 'C'">
                <el-radio-group v-model="cardSaleMode" size="small">
                  <el-radio-button value="amount">储值卡</el-radio-button>
                  <el-radio-button value="times">疗程卡</el-radio-button>
                </el-radio-group>
              </template>
              <el-input v-model="itemKeyword" placeholder="搜索项目" clearable size="small" style="width:200px" />
              <span v-if="itemTab !== 'P' && itemTab !== 'I'" class="item-count">{{ filteredItems.length }} 项</span>
            </div>
          </template>
          <!-- S/G/C tabs -->
          <template v-if="itemTab !== 'P'">
            <template v-if="itemTab !== 'I'">
              <div class="item-selector-body">
                <div class="category-tree-panel">
                  <div class="cat-node" :class="{ active: selectedCategory === '' }" @click="selectedCategory = ''">📂 全部</div>
                  <template v-for="cat in categories" :key="cat.code">
                    <div class="cat-node" :class="{ active: selectedCategory === cat.code }" @click="selectedCategory = cat.code">📁 {{ cat.name }}</div>
                    <div v-if="cat.children && cat.children.length" class="cat-children">
                      <div v-for="child in cat.children" :key="child.code" class="cat-node cat-child" :class="{ active: selectedCategory === child.code }" @click="selectedCategory = child.code">📁 {{ child.name }}</div>
                    </div>
                  </template>
                </div>
                <div class="item-grid-panel">
                  <div class="item-grid">
                    <div v-for="item in filteredItems" :key="item.code" class="item-card" @click="itemTab === 'C' ? addCardSale(item) : addToCart(item)">
                      <div class="item-name">{{ item.name }}</div>
                      <div class="item-price">¥{{ parseFloat(item.price ?? 0) }}</div>
                    </div>
                    <el-empty v-if="!filteredItems.length" :description="itemsLoading ? '加载中...' : '无匹配项目'" />
                  </div>
                </div>
              </div>
            </template>
            <!-- I tab -->
            <template v-else>
              <div class="recharge-panel">
                <div style="display:flex;gap:8px;margin-bottom:10px">
                  <el-radio-group v-model="rechargeMode" size="small">
                    <el-radio-button value="recharge">充值</el-radio-button>
                    <el-radio-button value="refund">退卡</el-radio-button>
                  </el-radio-group>
                </div>
                <div class="recharge-grid">
                  <div v-for="card in refundableCards" :key="card.ccode" class="recharge-card">
                    <div class="rc-name">{{ card.cardname }}</div>
                    <div class="rc-code">{{ card.ccode }}</div>
                    <div class="rc-balance">
                      <template v-if="card.comptype === 'times'">余次: {{ card.leftqty ?? 0 }} 次</template>
                      <template v-else>余额: ¥{{ parseFloat(card.leftmoney ?? 0).toFixed(0) }}</template>
                    </div>
                    <div class="rc-actions">
                      <el-input-number v-model="rechargeAmounts[card.ccode]" :min="0" :step="rechargeMode === 'refund' && card.comptype === 'times' ? 1 : 100" size="small" :controls="false" style="width:80px" />
                      <el-button v-if="rechargeMode === 'recharge'" size="small" type="primary" @click="addRecharge(card)">充值</el-button>
                      <el-button v-else size="small" type="danger" @click="addCardRefund(card)">退款</el-button>
                    </div>
                  </div>
                  <el-empty v-if="!refundableCards.length" :description="rechargeMode === 'recharge' ? '无可用储值卡' : '无可用退卡'" :image-size="50" />
                </div>
              </div>
            </template>
          </template>
          <!-- P tab -->
          <template v-else>
            <div class="promo-selector-body">
              <div class="promo-list-panel">
                <template v-for="(group, gidx) in promoGroups" :key="gidx">
                  <div class="promo-group-title">{{ group.name }}</div>
                  <div v-for="p in group.items" :key="p.uuid" class="promo-card"
                    :class="{ selected: selectedPromotion?.uuid === p.uuid }" @click="selectAndLoadPromotion(p)">
                    <div class="promo-card-name">{{ p.promotionsname }}</div>
                    <div class="promo-card-meta">
                      <el-tag size="small" :type="promoTypeTag(p.mainttype)">{{ p.mainttype_name }}</el-tag>
                      <span class="promo-card-date">{{ (p.fromdate || '').slice(0,4) }}/{{ (p.fromdate || '').slice(4,6) }}/{{ (p.fromdate || '').slice(6,8) }}</span>
                    </div>
                    <div v-if="p.mainttype === '30'" class="promo-card-price">套餐价 ¥{{ comboTotal(p).toFixed(0) }}</div>
                    <div v-else-if="p.disc" class="promo-card-price">{{ Math.round((1 - p.disc) * 100) }}% OFF</div>
                  </div>
                </template>
                <el-empty v-if="!promotions.length && !promotionsLoading" description="暂无有效活动" :image-size="50" />
                <div v-if="promotionsLoading" style="text-align:center;padding:12px;color:#909399;font-size:13px">加载中...</div>
              </div>
              <div class="promo-item-panel">
                <template v-if="selectedPromotion">
                  <template v-if="selectedPromotion.mainttype !== '30'">
                    <div v-for="item in selectedPromotion.items" :key="item.sgcode" class="promo-item-card" @click="addPromotionItem(selectedPromotion, item)">
                      <div class="pi-name">{{ item.itemname }}</div>
                      <div class="pi-price">
                        <span v-if="item.promotionsprice" class="pi-original">¥{{ (item.s_price || 0).toFixed(0) }}</span>
                        <span class="pi-promo">¥{{ (item.promotionsprice || item.s_price || 0).toFixed(0) }}</span>
                        <span v-if="selectedPromotion.disc && selectedPromotion.disc < 1" class="pi-disc">{{ Math.round((1 - selectedPromotion.disc) * 100) }}%OFF</span>
                      </div>
                    </div>
                  </template>
                  <template v-else>
                    <div class="combo-card">
                      <div class="combo-header">
                        <span class="combo-name">{{ selectedPromotion.promotionsname }}</span>
                        <span class="combo-total">¥{{ comboTotal(selectedPromotion).toFixed(0) }}</span>
                      </div>
                      <div class="combo-items" @click="addComboToCart(selectedPromotion)">
                        <div v-for="gi in selectedPromotion.group_items" :key="gi.sgcode" class="combo-item">
                          <span class="ci-code">{{ gi.ttype === 'S' ? '💆' : '🧴' }}</span>
                          <span class="ci-name">{{ gi.itemname }}</span>
                          <span class="ci-qty">×{{ gi.qty }}</span>
                          <span class="ci-price">¥{{ (gi.price || 0).toFixed(0) }}</span>
                        </div>
                      </div>
                      <div class="combo-hint">点击任意项目添加到开单明细</div>
                    </div>
                    <el-empty v-if="!selectedPromotion.group_items?.length" description="套餐无明细" :image-size="50" />
                  </template>
                </template>
                <div v-else class="promo-placeholder">请从左侧选择一个活动</div>
              </div>
            </div>
          </template>
        </el-card>
        
        <!-- 购物车 -->
        <el-card shadow="never" class="section-card">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-weight:600">开单明细</span>
              <div style="display:flex;align-items:center;gap:10px">
                <span v-if="selectedCard" class="selected-card-chip">已选: {{ selectedCard.cardname }}({{ selectedCard.ccode }})</span>
                <span style="font-size:13px;color:#606266">合计: </span>
                <span style="font-size:18px;font-weight:700;color:#e6a23c">¥{{ cartTotal.toFixed(2) }}</span>
                <el-button type="primary" size="small" :loading="saving" :disabled="!cart.length" @click="saveHung">保存挂账</el-button>
                <el-button text type="danger" size="small" :disabled="!cart.length" @click="clearCart">清空</el-button>
              </div>
            </div>
          </template>
          <div v-if="cartGroups.length" class="cart-tree">
            <div v-for="group in cartGroups" :key="group.ttype" class="cart-group">
              <div class="cart-group-header">
                <span>{{ group.label }} ({{ group.items.length }})</span>
              </div>
              <div class="cart-header-row">
                <span class="ci-name">项目</span>
                <span class="ci-stype">属性</span>
                <span class="ci-qty">数量</span>
                <span class="ci-price">单价</span>
                <span class="ci-disc">折扣率</span>
                <span class="ci-mondisc">金额折扣</span>
                <span class="ci-subtotal">小计</span>
                <span class="ci-pay">扣款方式</span>
                <span class="ci-cardno">付款卡号</span>
                <span class="ci-pmcode">开单</span>
                <span class="ci-ass1">美疗师1</span>
                <span class="ci-ass2">美疗师2</span>
              </div>
              <div v-for="(row, idx) in group.items" :key="row.code + '-' + idx" class="cart-item-row" :class="{ 'refund-row': row.qty < 0 }">
                <div class="ci-name">{{ row.name }}</div>
                <div class="ci-stype"><el-select v-model="row.stype" size="small"><el-option label="正常" value="N" /><el-option label="赠送" value="P" /></el-select></div>
                <div class="ci-qty">{{ row.qty }}</div>
                <div class="ci-price">¥{{ row.price.toFixed(2) }}</div>
                <div class="ci-disc">
                  <el-input-number v-model="row.secdisc" :min="0" :max="1" :step="0.05" size="small" :controls="false" style="width:55px"
                    :formatter="(val) => Math.round(val * 100) + '%'"
                    :parser="(val) => parseInt(val.replace('%', '')) / 100" />
                </div>
                <div class="ci-mondisc"><el-input-number v-model="row.srvmondisc" :min="0" :step="1" size="small" :controls="false" style="width:65px" /></div>
                <div class="ci-subtotal">¥{{ (row.price * row.qty * row.secdisc - row.srvmondisc).toFixed(2) }}</div>
                <div class="ci-pay">
                  <el-select v-model="row.payMethod" size="small">
                    <el-option label="现金" value="cash" />
                    <el-option v-for="c in row.availableCards" :key="c.ccode"
                      :label="c.cardname + '(' + c.ccode + ')' + (c.comptype==='times'?'('+c.leftqty+'次)':'')"
                      :value="'card:'+c.ccode" />
                    <el-option label="储值卡余额" value="balance" />
                  </el-select>
                </div>
                <div class="ci-cardno"><template v-if="row.payMethod?.startsWith('card:')">{{ row.payMethod.slice(5) }}</template><span v-else style="color:#c0c4cc">--</span></div>
                <div class="ci-pmcode"><el-select v-model="row.pmcode" size="small" filterable><el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" /></el-select></div>
                <div class="ci-ass1"><el-select v-model="row.asscode1" size="small" filterable><el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" /></el-select></div>
                <div class="ci-ass2"><el-select v-model="row.asscode2" size="small" filterable><el-option v-for="emp in employees" :key="emp.ecode" :label="emp.ename" :value="emp.ecode" /></el-select></div>
              </div>
            </div>
          </div>
          <el-empty v-if="!cartGroups.length" description="从左侧选品区添加项目" :image-size="60" />
        </el-card>
      </div>
    </div>
    
    <!-- 客户360°抽屉 -->
    <el-drawer v-model="showVipDrawer" :title="vipProfileTitle" size="500px" @close="closeVipDrawer">
      <div style="min-height:200px"><div v-if="profileLoading" style="text-align:center;padding:30px;color:#909399">加载中...</div>
        <template v-if="profileBasicInfo">
          <el-descriptions :column="2" border size="small" style="margin-bottom:16px">
            <el-descriptions-item label="姓名">{{ profileBasicInfo.vname }}</el-descriptions-item>
            <el-descriptions-item label="会员号">{{ profileBasicInfo.vcode }}</el-descriptions-item>
            <el-descriptions-item label="手机">{{ profileBasicInfo.mtcode }}</el-descriptions-item>
            <el-descriptions-item label="等级">{{ profileBasicInfo.viplevel || '--' }}</el-descriptions-item>
            <el-descriptions-item label="顾问">{{ profileBasicInfo.ecode || '--' }}</el-descriptions-item>
            <el-descriptions-item label="美疗师">{{ profileBasicInfo.ecode2 || '--' }}</el-descriptions-item>
          </el-descriptions>
          <el-tabs v-model="profileTab">
            <el-tab-pane label="名下卡项" name="cards">
              <el-empty v-if="!vipCards.length" description="无名下卡片" :image-size="50" />
              <div v-else class="profile-cards">
                <div v-for="card in vipCards" :key="card.uuid" class="profile-card"
                  :class="{ 'status-p': card.status === 'P' }">
                  <div class="pc-left"><div class="pc-name">{{ card.cardname }}</div><div class="pc-code">{{ card.ccode }}</div></div>
                  <div class="pc-right">
                    <span v-if="card.comptype === 'times'" class="pc-bal">{{ card.leftqty ?? 0 }} 次</span>
                    <span v-else class="pc-bal">¥{{ parseFloat(card.leftmoney ?? 0).toFixed(0) }}</span>
                    <span v-if="card.valdate" class="pc-expire">{{ String(card.valdate).replace(/^(\d{4})(\d{2})(\d{2})$/, '$1-$2-$3') }}</span>
                  </div>
                  <el-tag v-if="card.stype === 'P'" size="small" type="warning">赠送</el-tag>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="消费记录" name="consumption">
              <el-empty v-if="!profileConsumption.length" description="无消费记录" :image-size="50" />
              <div v-else class="profile-list">
                <div v-for="(c, i) in profileConsumption" :key="i" class="profile-list-item">
                  <span class="pli-date">{{ c.vsdate || '--' }}</span>
                  <span class="pli-name">{{ c.itemname || '--' }}</span>
                  <span class="pli-amount">¥{{ (parseFloat(c.amount) || 0).toFixed(0) }}</span>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="沟通回访" name="communications">
              <el-empty v-if="!profileCommunications.length" description="无沟通记录" :image-size="50" />
              <div v-else class="profile-list">
                <div v-for="(c, i) in profileCommunications" :key="i" class="profile-list-item">
                  <span class="pli-date">{{ c.created_date || '--' }}</span>
                  <span class="pli-type"><el-tag size="small">{{ c.casetype || '沟通' }}</el-tag></span>
                  <span class="pli-content">{{ c.detail || '' }}</span>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </template>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useBillingEngine } from '@/composables/useBillingEngine'
import type { VipCard, CartableItem } from '@/types'
import { getCardtypeServiceItems } from '@/api/cashier'
import { getVipDetail, getVipConsumption, getVipCommunication } from '@/api/vip'

const {
  company, storecode,
  vipKeyword, searchResults, noResults,
  selectedVip, selectedCard, vipCards, activeCardGroups, cardGroups,
  itemTab, itemKeyword, filteredItems, itemsLoading,
  categories, selectedCategory,
  employees, cart, cartGroups, cartTotal, saving,
  searchVip, selectVip, fetchVipCards, fetchPromotions,
  selectCard, addToCart, removeFromCart, toggleRefund, autoAddCardItems,
  updateCartItem, clearCart, saveHung,
  ttypeLabel, formatDate, empName,
  billingMode, switchBillingMode,
  refundDateRange, checkedOutOrders, checkedOutSelections, checkedOutLoading,
  fetchCheckedOutOrders, addRefundToCart,
  voidPanelOpen, voidOrders, voidOrderItems, voidLoading, voidSelections, voidItems,
  openVoidPanel, fetchVoidOrders, fetchVoidDetail, toggleVoidItem, confirmVoid,
  promotions, selectedPromotion, promotionsLoading, promotionDetails,
  selectAndLoadPromotion, addPromotionItem, addComboToCart,
  cardSaleMode, cardSaleItems, showPriceSelector,
  editQty, editAmount, editDiscountPct, editDiscountAmt, editUnitPrice, editSubtotal,
  addCardSale, confirmCardSale,
  rechargeMode, rechargeAmounts, refundableCards, addRecharge, addCardRefund,
  draggedCard, onCardDragStart, onCardDrop,
  cardMenuVisible, cardMenuPos, cardMenuCard, showCardMenu, closeCardMenu,
  menuViewCard, menuUseCard, menuConsumeItems, menuRecharge,
} = useBillingEngine()

const showVipDrawer = ref(false)
const profileTab = ref('cards')
const profileLoading = ref(false)
const profileBasicInfo = ref<any>(null)
const profileConsumption = ref<any[]>([])
const profileCommunications = ref<any[]>([])

const vipProfileTitle = computed(() => {
  const v = profileBasicInfo.value
  return v ? v.vname + ' (' + v.vcode + ')' : '客户详情'
})

function openVipProfile(uuid: string) {
  showVipDrawer.value = true
  profileLoading.value = true
  profileBasicInfo.value = null
  profileConsumption.value = []
  profileCommunications.value = []
  Promise.allSettled([
    getVipDetail(uuid),
    getVipConsumption(uuid),
    getVipCommunication(uuid),
  ]).then(function(rs) {
    rs.forEach(function(r, i) {
      if (r.status === 'fulfilled') {
        var d = r.value.data
        if (i === 0) { profileBasicInfo.value = d }
        else if (i === 1) { profileConsumption.value = Array.isArray(d) ? d : d?.results ?? [] }
        else if (i === 2) { profileCommunications.value = Array.isArray(d) ? d : d?.results ?? [] }
      }
    })
    profileLoading.value = false
  }).catch(function() { profileLoading.value = false })
}
function closeVipDrawer() {
  showVipDrawer.value = false
}
</script>
<style scoped>

.billing-v2 { height:100%; display:flex; flex-direction:column; gap:8px; }
.header-bar { display:flex; align-items:center; gap:12px; flex-shrink:0; }
.page-title { margin:0; font-size:18px; font-weight:600; }
.header-vip { margin-left:auto; font-size:14px; color:#409eff; font-weight:500; }
.header-vip-code { color:#909399; font-weight:400; }
.v2-layout { display:flex; gap:12px; flex:1; min-height:0; }
.v2-left { width:380px; flex-shrink:0; display:flex; flex-direction:column; gap:10px; min-height:0; }
.v2-right { flex:1; display:flex; flex-direction:column; gap:10px; min-width:0; min-height:0; }
.v2-right > .section-card:first-of-type { flex:5.5; min-height:0; }
.v2-right > .section-card:last-of-type { flex:4.5; min-height:0; }
.section-card { display:flex; flex-direction:column; }
.section-card :deep(.el-card__body) { flex:1; overflow:auto; padding:8px 12px; }
.section-card :deep(.el-card__header) { padding:6px 12px; font-size:13px; font-weight:600; }
.search-card :deep(.el-card__body) { overflow:visible; }
.search-results { margin-top:8px; border:1px solid #ebeef5; border-radius:6px; max-height:260px; overflow-y:auto; }
.sr-item { padding:8px 10px; cursor:pointer; border-bottom:1px solid #f0f0f0; }
.sr-item:hover { background:#ecf5ff; }
.sr-name { font-weight:500; font-size:14px; display:flex; align-items:center; gap:6px; }
.sr-detail { font-size:12px; color:#909399; margin-top:2px; display:flex; gap:12px; }
.vip-card { margin-top:6px; padding:8px 10px; background:linear-gradient(135deg,#f0f9ff,#e6f7ff); border-radius:8px; }
.vip-card-name { font-weight:600; font-size:14px; margin-bottom:2px; display:flex; align-items:center; gap:8px; }
.vip-card-info { font-size:12px; color:#666; display:flex; gap:12px; }
.vip-card-emp { font-size:12px; color:#409eff; margin-top:4px; display:flex; gap:12px; }
.card-list-card { flex:1; min-height:0; }
.card-list-card :deep(.el-card__body) { padding:4px 8px; }
.card-collapse { border-top:none; }
.card-collapse :deep(.el-collapse-item__header) { font-size:12px; font-weight:600; padding:4px 8px; height:auto; line-height:1.4; }
.card-collapse :deep(.el-collapse-item__content) { padding-bottom:2px; }
.cg-sub-title { font-size:11px; font-weight:500; color:#606266; padding:2px 8px; margin-bottom:2px; background:#f5f7fa; border-radius:4px; }
.cg-card { display:flex; justify-content:space-between; align-items:center; padding:4px 8px; margin-bottom:3px; border:1px solid #ebeef5; border-radius:5px; cursor:pointer; transition:.1s; background:#fff; }
.cg-card:hover { border-color:#409eff; background:#ecf5ff; }
.cg-card.selected { border-color:#409eff; background:#d9ecff; }
.cg-card.status-p { border-color:#e6a23c; background:#fef7e0; }
.cg-card-left { flex:1; min-width:0; }
.cg-card-code { font-size:12px; font-weight:500; color:#303133; }
.cg-card-name { font-size:11px; color:#909399; margin-top:1px; }
.cg-card-right { text-align:right; flex-shrink:0; }
.cg-card-amount { font-size:13px; font-weight:600; color:#e6a23c; }
.cg-card-expire { font-size:10px; color:#c0c4cc; }
.item-selector-header { display:flex; gap:12px; align-items:center; }
.item-selector-body { display:flex; gap:8px; height:100%; min-height:0; }
.category-tree-panel { width:160px; flex-shrink:0; overflow-y:auto; border-right:1px solid #ebeef5; padding-right:8px; }
.cat-node { padding:6px 8px; font-size:12px; cursor:pointer; border-radius:4px; margin-bottom:2px; transition:.1s; }
.cat-node:hover { background:#ecf5ff; color:#409eff; }
.cat-node.active { background:#d9ecff; color:#409eff; font-weight:600; }
.cat-children { padding-left:16px; }
.cat-child { font-size:11px; }
.item-grid-panel { flex:1; overflow-y:auto; min-width:0; }
.item-count { font-size:12px; color:#909399; margin-left:auto; }
.item-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(120px,1fr)); gap:6px; }
.item-card { padding:8px 6px; border:1px solid #ebeef5; border-radius:6px; cursor:pointer; text-align:center; transition:.12s; }
.item-card:hover { border-color:#409eff; background:#ecf5ff; transform:translateY(-1px); }
.item-name { font-size:12px; margin-bottom:4px; }
.item-price { font-size:13px; font-weight:600; color:#e6a23c; }
.recharge-panel { padding:4px; height:100%; overflow-y:auto; }
.recharge-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:8px; }
.recharge-card { border:1px solid #ebeef5; border-radius:6px; padding:10px; background:#fff; }
.rc-name { font-size:13px; font-weight:600; }
.rc-code { font-size:11px; color:#909399; margin:2px 0; }
.rc-balance { font-size:13px; color:#e6a23c; font-weight:600; margin-bottom:6px; }
.rc-actions { display:flex; gap:4px; align-items:center; }
.promo-selector-body { display:flex; gap:8px; height:100%; min-height:0; }
.promo-list-panel { width:200px; flex-shrink:0; overflow-y:auto; border-right:1px solid #ebeef5; padding-right:8px; }
.promo-card { padding:8px 10px; border:1px solid #ebeef5; border-radius:6px; cursor:pointer; margin-bottom:6px; transition:.1s; }
.promo-card:hover { border-color:#409eff; background:#ecf5ff; }
.promo-card.selected { border-color:#409eff; background:#d9ecff; }
.promo-card-name { font-size:13px; font-weight:600; margin-bottom:4px; }
.promo-card-meta { display:flex; align-items:center; gap:6px; flex-wrap:wrap; }
.promo-card-date { font-size:10px; color:#909399; }
.promo-card-price { font-size:12px; color:#e6a23c; font-weight:600; margin-top:4px; }
.promo-group-title { font-size:11px; font-weight:600; color:#606266; padding:6px 2px 4px; border-bottom:1px solid #ebeef5; margin-bottom:6px; }
.promo-item-panel { flex:1; overflow-y:auto; min-width:0; }
.promo-placeholder { padding:40px; text-align:center; color:#c0c4cc; font-size:14px; }
.promo-item-card { display:flex; justify-content:space-between; align-items:center; padding:8px 10px; border:1px solid #ebeef5; border-radius:6px; cursor:pointer; margin-bottom:4px; transition:.1s; }
.promo-item-card:hover { border-color:#409eff; background:#ecf5ff; }
.pi-name { font-size:13px; }
.pi-price { display:flex; align-items:center; gap:6px; }
.pi-original { font-size:12px; color:#c0c4cc; text-decoration:line-through; }
.pi-promo { font-size:15px; font-weight:700; color:#f56c6c; }
.pi-disc { font-size:11px; color:#fff; background:#f56c6c; padding:1px 4px; border-radius:3px; }
.combo-card { border:2px solid #e6a23c; border-radius:8px; padding:12px; background:linear-gradient(135deg,#fffbf0,#fff8e1); }
.combo-header { display:flex; justify-content:space-between; align-items:center; padding-bottom:8px; border-bottom:1px dashed #e6a23c; margin-bottom:8px; }
.combo-name { font-size:15px; font-weight:700; color:#e6a23c; }
.combo-total { font-size:18px; font-weight:700; color:#f56c6c; }
.combo-items { display:flex; flex-direction:column; gap:4px; margin-bottom:10px; }
.combo-item { display:flex; align-items:center; gap:6px; font-size:12px; padding:3px 6px; background:rgba(255,255,255,0.7); border-radius:4px; }
.combo-item .ci-name { flex:1; }
.combo-item .ci-qty { color:#909399; }
.combo-item .ci-price { font-weight:600; color:#e6a23c; }
.combo-hint { text-align:center; font-size:11px; color:#c0c4cc; padding:6px 0 2px; }
.profile-cards { display:flex; flex-direction:column; gap:6px; }
.profile-card { display:flex; align-items:center; gap:10px; padding:8px 10px; border:1px solid #ebeef5; border-radius:6px; flex-wrap:wrap; }
.profile-card.status-p { background:#fef7e0; }
.pc-left { flex:1; }
.pc-name { font-size:13px; font-weight:500; }
.pc-code { font-size:11px; color:#909399; }
.pc-right { text-align:right; }
.pc-bal { font-size:14px; font-weight:600; color:#e6a23c; display:block; }
.pc-expire { font-size:10px; color:#c0c4cc; }
.profile-list { display:flex; flex-direction:column; gap:4px; }
.profile-list-item { display:flex; align-items:center; gap:8px; padding:6px 8px; border-bottom:1px solid #f5f5f5; font-size:12px; }
.pli-date { width:90px; color:#909399; flex-shrink:0; }
.pli-name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.pli-amount { width:80px; text-align:right; font-weight:600; }
.pli-type { width:60px; flex-shrink:0; }
.pli-content { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#606266; }
.selected-card-chip { font-size:12px; color:#409eff; background:#ecf5ff; padding:2px 8px; border-radius:4px; }


.cart-tree { display:flex; flex-direction:column; gap:4px; }
.cart-group { border:1px solid #ebeef5; border-radius:6px; overflow:hidden; }
.cart-group-header { display:flex; align-items:center; gap:6px; padding:4px 10px; background:#fafafa; font-size:13px; font-weight:600; border-bottom:1px solid #ebeef5; }
.cart-header-row { display:flex; align-items:center; padding:3px 8px; font-size:11px; font-weight:600; color:#909399; background:#fafafa; border-bottom:1px solid #ebeef5; }
.cart-item-row { display:flex; align-items:center; padding:4px 8px; border-bottom:1px solid #f5f5f5; font-size:12px; gap:4px; }
.cart-item-row.refund-row { background:#fef0f0; }
.cart-item-row:last-child { border-bottom:none; }
.cart-item-row :deep(.el-select .el-input__inner) { height:28px; font-size:12px; }
.cart-item-row :deep(.el-input-number .el-input__inner) { height:28px; font-size:12px; }
.ci-name { min-width:90px; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; font-size:12px; }
.ci-stype { width:60px; }
.ci-qty { width:40px; text-align:center; font-weight:500; }
.ci-price { width:90px; text-align:right; color:#606266; }
.ci-disc { width:60px; }
.ci-mondisc { width:65px; }
.ci-subtotal { width:95px; text-align:right; font-weight:600; color:#e6a23c; }
.ci-refund { width:40px; text-align:center; }
.ci-pay { width:130px; }
.ci-cardno { width:90px; color:#409eff; font-size:11px; }
.ci-pmcode { width:95px; }
.ci-ass1 { width:95px; }
.ci-ass2 { width:95px; }
.ci-action { width:35px; text-align:center; }
.ci-stype :deep(.el-select), .ci-disc :deep(.el-input-number), .ci-mondisc :deep(.el-input-number),
.ci-pay :deep(.el-select), .ci-pmcode :deep(.el-select), .ci-ass1 :deep(.el-select), .ci-ass2 :deep(.el-select) { width:100%; }

</style>