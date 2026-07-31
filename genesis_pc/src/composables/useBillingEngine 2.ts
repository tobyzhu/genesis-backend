// ============================================================
// useBillingEngine — 开单业务逻辑引擎（可复用、可测试）
// 纯响应式状态 + 方法，不依赖具体组件
// ============================================================
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Vip, VipCard, CartableItem, CardGroup } from '@/types'
import request from '@/api/request'
import { searchVip as apiSearchVip, getVipCards } from '@/api/vip'
import { getServiceItems, getGoodsItems, getCardtypeItems, getCategorizedItems, getHungByVipUuid, getHungDetail, getCardtypeServiceItems, getCheckedOutOrders, getActivePromotions, getCardtypePrices } from '@/api/cashier'

// ====== 类型定义 ======
export interface CartItem {
  code: string
  name: string
  price: number
  qty: number
  ttype: 'S' | 'G' | 'C' | 'I'
  stype: 'N' | 'P'
  secdisc: number        // 折扣率 0~1.0
  srvmondisc: number     // 金额折扣（元）
  payMethod: string      // 'cash' | 'card:ccode' | 'balance'
  pmcode: string         // 开单员工
  asscode1: string       // 美疗师1
  asscode2: string       // 美疗师2
  availableCards: VipCard[]
  /** 来源活动编号（如为活动项目） */
  promotionsid?: string
}

export interface CategoryNode {
  code: string
  name: string
  children?: CategoryNode[]
}

export interface Employee {
  ecode: string
  ename: string
}

// ====== 引擎状态 ======
export function useBillingEngine() {
  const company = localStorage.getItem('genesis_pc_company') || ''
  const storecode = localStorage.getItem('genesis_pc_storecode') || ''

  // ── VIP 相关 ──
  const vipKeyword = ref('')
  const searchResults = ref<Vip[]>([])
  const noResults = ref(false)
  const selectedVip = ref<Vip | null>(null)
  const selectedCard = ref<VipCard | null>(null)
  const vipCards = ref<VipCard[]>([])
  const activeCardGroups = ref<number[]>([])

  // ── 选品 ──
  const itemTab = ref<'S' | 'G' | 'C' | 'I' | 'P'>('S')
  const itemKeyword = ref('')
  const allItems = ref<CartableItem[]>([])
  const itemsLoading = ref(false)
  const categories = ref<CategoryNode[]>([])
  const selectedCategory = ref('')
  const promotions = ref<any[]>([])
  const selectedPromotion = ref<any>(null)
  const promotionsLoading = ref(false)
  const promotionDetails = ref<Record<string, any>>({})

  // ── 员工 ──
  const employees = ref<Employee[]>([])

  // ── 购物车 ──
  const cart = ref<CartItem[]>([])

  // ── 保存状态 ──
  const saving = ref(false)

  // ── 作废 ──
  const billingMode = ref<'normal' | 'refund'>('normal')
  const checkedOutOrders = ref<any[]>([])
  const checkedOutSelections = ref<Record<string, Record<string, boolean>>>({})
  const checkedOutLoading = ref(false)
  const refundDateRange = ref<[Date, Date]>([new Date(Date.now() - 30 * 86400000), new Date()])

  const voidPanelOpen = ref(false)

  // ── 售卡模式 ──
  const cardSaleMode = ref<'amount'|'times'>('amount')
  const showPriceSelector = ref(false)
  const itemCode = ref('')
  const itemName = ref('')
  const editQty = ref(1)
  const editAmount = ref(0)
  const editDiscountPct = ref(100)
  const editDiscountAmt = ref(0)
  const editUnitPrice = computed(() => editQty.value > 0 ? Math.round(editAmount.value / editQty.value * 100) / 100 : 0)
  const editSubtotal = computed(() => editQty.value * editUnitPrice.value * (editDiscountPct.value / 100) - editDiscountAmt.value)

  // ── 充值 ──
  const rechargeMode = ref<'recharge'|'refund'>('recharge')
  const rechargeAmounts = ref<Record<string, number>>({})
  const voidOrders = ref<any[]>([])
  const voidOrderItems = ref<Record<string, any[]>>({})
  const voidLoading = ref(false)
  const voidSelections = ref<Record<string, Record<string, boolean>>>({})
  const voidItems = ref<CartItem[]>([])

  // ── 拖拽 ──
  const draggedCard = ref<VipCard | null>(null)

  // ── 右键菜单 ──
  const cardMenuVisible = ref(false)
  const cardMenuPos = ref({ x: 0, y: 0 })
  const cardMenuCard = ref<VipCard | null>(null)

  // ====== 计算属性 ======

  const filteredItems = computed(() => {
    const kw = itemKeyword.value.trim().toLowerCase()
    let cats = allItems.value
    // Filter by selected category (include all subcategories)
    if (selectedCategory.value) {
      const catCodes = collectCategoryCodes(categories.value, selectedCategory.value)
      cats = cats.filter((i) => catCodes.includes((i as any).category || ''))
    }
    if (!kw) return cats
    return cats.filter((i) =>
      (i.name || '').toLowerCase().includes(kw) || (i.code || '').toLowerCase().includes(kw)
    )
  })

  const cartTotal = computed(() =>
    cart.value.reduce((s, i) => s + i.price * i.qty * i.secdisc - i.srvmondisc, 0)
  )

  /** 购物车按 ttype 分组，用于 tree 展示 */
  const cartGroups = computed(() => {
    const groups: Array<{ ttype: 'S' | 'G' | 'C' | 'I'; label: string; items: CartItem[] }> = []
    const order = ['S', 'G', 'C', 'I'] as const
    const labels: Record<string, string> = { S: '服务', G: '商品', C: '售卡', I: '充值' }
    for (const t of order) {
      const items = cart.value.filter((i) => i.ttype === t)
      if (items.length) {
        groups.push({ ttype: t, label: labels[t] || t, items })
      }
    }
    return groups
  })

  /** 名下卡片分组 */
  const cardSaleItems = computed(() =>
    allItems.value.filter((i: any) => {
      if (cardSaleMode.value === 'amount') return i.comptype === 'amount'
      if (cardSaleMode.value === 'times') return i.comptype === 'times'
      return true
    })
  )

  const refundableCards = computed(() =>
    vipCards.value.filter((c: VipCard) =>
      c.status !== 'P' && (rechargeMode.value === 'recharge'
        ? c.comptype === 'amount'
        : ['amount', 'times'].includes(c.comptype || ''))
    )
  )

  const cardGroups = computed(() => {
    const data = vipCards.value
    const pidMap: Record<string, Record<string, VipCard[]>> = {}
    for (const card of data) {
      const pid = card.promotionsid || '0'
      const ct = card.comptype || 'other'
      if (!pidMap[pid]) pidMap[pid] = {}
      if (!pidMap[pid][ct]) pidMap[pid][ct] = []
      pidMap[pid][ct].push(card)
    }
    const result: CardGroup[] = []
    for (const [pid, ctGroups] of Object.entries(pidMap)) {
      const firstCard = ctGroups[Object.keys(ctGroups)[0]]?.[0]
      const promotionName = pid === '0' ? '正常销售' : firstCard?.promotionname || '活动:' + pid
      const comptypeGroups: CardGroup['comptypeGroups'] = []
      for (const [ct, cards] of Object.entries(ctGroups)) {
        const ctName = ct === 'amount' ? '储值卡' : ct === 'times' ? '计次卡' : ct === 'period' ? '计时卡' : ct
        comptypeGroups.push({ typeName: ctName + ' (' + cards.length + '张)', cards })
      }
      result.push({ promotionName, comptypeGroups })
    }
    return result
  })

  // ====== 方法 ======

  async function searchVip() {
    const kw = vipKeyword.value.trim()
    if (!kw) return
    selectedVip.value = null
    noResults.value = false
    try {
      const res = await apiSearchVip(kw)
      const list = res.data?.results ?? (Array.isArray(res.data) ? res.data : [])
      if (list.length === 1) {
        await selectVip(list[0])
        searchResults.value = []
      } else if (list.length > 1) {
        searchResults.value = list
        noResults.value = false
      } else {
        searchResults.value = []
        noResults.value = true
        vipCards.value = []
      }
    } catch {
      searchResults.value = []
      noResults.value = true
    }
  }

  async function selectVip(vip: Vip) {
    selectedVip.value = vip
    selectedCard.value = null
    cart.value = []
    searchResults.value = []
    activeCardGroups.value = []
    await Promise.all([
      fetchVipCards(vip.uuid),
      fetchItems(),
      fetchEmployees(),
    ])
    const count = new Set(vipCards.value.map(c => c.promotionsid || '0')).size
    activeCardGroups.value = Array.from({ length: count }, (_, i) => i)
  }

  async function fetchVipCards(uuid: string) {
    try {
      const res = await getVipCards(uuid)
      const raw = (Array.isArray(res.data) ? res.data : res.data?.results ?? []) as VipCard[]
      const filtered = raw.filter((card: VipCard) => {
        if (card.status === 'P') return true
        if (card.comptype === 'times' && (card.leftqty ?? 0) <= 0) return false
        if (card.comptype === 'amount' && card.stype === 'P' && (card.leftmoney ?? 0) <= 0) return false
        return true
      })
      vipCards.value = filtered
    } catch {
      vipCards.value = []
    }
  }

  async function selectAndLoadPromotion(promo: any) {
    if (!promo) return
    selectedPromotion.value = promo
    if (!promotionDetails.value[promo.uuid]) {
      try {
        const res = await getActivePromotions(promo.uuid)
        if (res.data?.uuid) {
          promotionDetails.value[promo.uuid] = res.data
          selectedPromotion.value = promotionDetails.value[promo.uuid]
        }
      } catch {}
    } else {
      selectedPromotion.value = promotionDetails.value[promo.uuid]
    }
  }

  async function fetchPromotions() {
    promotionsLoading.value = true
    promotions.value = []
    selectedPromotion.value = null
    console.log('[BillingV2] fetchPromotions company:', company)
    try {
      const res = await getActivePromotions()
      promotions.value = Array.isArray(res.data) ? res.data : []
      console.log('[BillingV2] fetchPromotions result:', promotions.value.length, 'promotions')
      if (promotions.value.length > 0) {
        promotions.value.forEach((p: any) => console.log('  -', p.promotionsname, p.mainttype_name, p.items?.length, 'items'))
      }
    } catch (e) {
      console.log('[BillingV2] fetchPromotions error:', e)
      promotions.value = []
    }
    finally { promotionsLoading.value = false }
  }

  async function addPromotionItem(promo: any, item: any) {
    if (cart.value.length > 0) {
      const allSamePromo = cart.value.every((ci: CartItem) => ci.promotionsid === (promo.promotionsid || ''))
      if (!allSamePromo) {
        try {
          await ElMessageBox.confirm(
            '开单明细中有不同活动的项目，加入将清空现有明细。是否继续？',
            '提示', { confirmButtonText: '继续', cancelButtonText: '取消', type: 'warning' }
          )
        } catch { return }
        cart.value = []
      }
    }
    let price = item.s_price || 0
    let secdisc = 1
    if (promo.mainttype === '10') {
      price = item.promotionsprice || item.s_price || 0
    } else if (promo.mainttype === '20') {
      secdisc = promo.disc || 1
      price = item.s_price || 0
    }
    const existing = cart.value.find((ci: CartItem) => ci.code === item.sgcode && ci.ttype === item.ttype)
    if (existing) {
      existing.qty++
    } else {
      cart.value.push({
        code: item.sgcode || '',
        name: item.itemname || item.sgcode || '',
        price: price,
        qty: item.s_qty || 1,
        ttype: item.ttype || 'S',
        stype: item.stype || 'N',
        secdisc: secdisc,
        srvmondisc: 0,
        payMethod: selectedCard.value ? 'card:' + selectedCard.value.ccode : 'cash',
        pmcode: selectedVip.value?.ecode || '',
        asscode1: selectedVip.value?.ecode2 || '',
        asscode2: '',
        availableCards: selectedCard.value ? [selectedCard.value] : [],
        promotionsid: promo.promotionsid || '',
      })
    }
  }

  async function fetchCardPrices(cardtype: string): Promise<Array<{qty: number, price: number, amount: number}>> {
    try {
      const res = await getCardtypePrices(cardtype)
      const data = Array.isArray(res.data) ? res.data : []
      return data.map((d: any) => ({ qty: d.qty || 1, price: d.price || 0, amount: d.amount || 0 }))
    } catch { return [] }
  }

  function addCardSale(item: any) {
    if (cardSaleMode.value === 'amount') {
      // 储值卡：直接加入
      addToCart(item)
    } else {
      // 疗程卡：显示价格对话框
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
    const secdisc = editDiscountPct.value / 100
    const srvmondisc = editDiscountAmt.value
    const code = itemCode.value
    const name = itemName.value + ' (' + qty + '次)'
    const defaultEmp = getDefaultEmployees()
    cart.value.push({
      code, name, price: unitPrice, qty, ttype: 'C', stype: 'N',
      secdisc, srvmondisc, payMethod: selectedCard.value ? 'card:' + selectedCard.value.ccode : 'cash',
      pmcode: defaultEmp.pmcode, asscode1: defaultEmp.asscode1, asscode2: defaultEmp.asscode2,
      availableCards: selectedCard.value ? [selectedCard.value] : [],
    })
    showPriceSelector.value = false
  }

  function addRecharge(card: VipCard) {
    const amount = rechargeAmounts.value[card.ccode] || 0
    if (amount <= 0) { ElMessage.warning('请输入金额'); return }
    const defaultEmp = getDefaultEmployees()
    cart.value.push({
      code: card.ccode, name: card.cardname + ' 充值', price: amount, qty: 1,
      ttype: 'I', stype: 'N', secdisc: 1, srvmondisc: 0,
      payMethod: 'cash', pmcode: defaultEmp.pmcode, asscode1: defaultEmp.asscode1, asscode2: defaultEmp.asscode2,
      availableCards: [],
    })
    rechargeAmounts.value[card.ccode] = 0
  }

 function addCardRefund(card: VipCard) {
   const qtyOrAmt = rechargeAmounts.value[card.ccode] || 0
   if (qtyOrAmt <= 0) {
     ElMessage.warning(card.comptype === 'times' ? '请输入退卡次数' : '请输入金额');
     return
   }
    const isTimes = card.comptype === 'times'
    const unitPrice = isTimes ? parseFloat(card.s_price ?? 0) : qtyOrAmt
    const refundQty = isTimes ? -qtyOrAmt : -1
    const defaultEmp = getDefaultEmployees()
    cart.value.push({
      code: card.ccode, name: card.cardname + ' 退款', price: unitPrice, qty: refundQty,
      ttype: 'I', stype: 'N', secdisc: 1, srvmondisc: 0,
      payMethod: 'cash', pmcode: defaultEmp.pmcode, asscode1: defaultEmp.asscode1, asscode2: defaultEmp.asscode2,
      availableCards: [],
    })
    rechargeAmounts.value[card.ccode] = 0
  }

  async function addComboToCart(promo: any) {
    if (cart.value.length > 0) {
      const allSamePromo = cart.value.every((ci: CartItem) => ci.promotionsid === (promo.promotionsid || ''))
      if (!allSamePromo) {
        try {
          await ElMessageBox.confirm(
            '开单明细中已有不同活动的项目，加入套餐将清空现有明细。是否继续？',
            '提示', { confirmButtonText: '继续', cancelButtonText: '取消', type: 'warning' }
          )
        } catch { return }
        cart.value = []
      }
    }
    for (const gi of (promo.group_items || [])) {
      const existing = cart.value.find((ci: CartItem) => ci.code === gi.sgcode && ci.ttype === gi.ttype)
      if (existing) {
        existing.qty += gi.qty || 1
      } else {
        cart.value.push({
          code: gi.sgcode || '',
          name: gi.itemname || gi.sgcode || '',
          price: gi.price || 0,
          qty: gi.qty || 1,
          ttype: gi.ttype || 'S',
          stype: 'N',
          secdisc: gi.disc || 1,
          srvmondisc: 0,
          payMethod: selectedCard.value ? 'card:' + selectedCard.value.ccode : 'cash',
          pmcode: selectedVip.value?.ecode || '',
          asscode1: selectedVip.value?.ecode2 || '',
          asscode2: '',
          availableCards: selectedCard.value ? [selectedCard.value] : [],
          promotionsid: promo.promotionsid || '',
        })
      }
    }
  }

  async function fetchItems() {
    itemsLoading.value = true
    try {
      const res = await getCategorizedItems(itemTab.value)
      const data = res.data || {}
      categories.value = (data.categories || []) as CategoryNode[]
      allItems.value = (data.items || []) as CartableItem[]
      selectedCategory.value = ''
    } catch {
      categories.value = []
      allItems.value = []
    } finally {
      itemsLoading.value = false
    }
  }

  async function fetchEmployees() {
    try {
      const res = await request.get('/adviser/get_bookingable_empllist/', {
        params: { company, storecode },
      })
      const list = Array.isArray(res.data) ? res.data : res.data?.results ?? []
      employees.value = list.map((e: any) => ({ ecode: e.ecode || '', ename: e.ename || '' }))
    } catch {
      employees.value = []
    }
  }

  function switchBillingMode(mode: 'normal' | 'refund') {
    billingMode.value = mode
    console.log('[BillingV2] switchBillingMode:', mode, 'selectedVip:', selectedVip.value?.vcode)
    if (mode === 'refund' && selectedVip.value) {
      fetchCheckedOutOrders(selectedVip.value.uuid)
    }
  }

  async function fetchCheckedOutOrders(vipuuid: string) {
    checkedOutLoading.value = true
    checkedOutOrders.value = []
    checkedOutSelections.value = {}
    const df = formatDateStr(refundDateRange.value[0])
    const dt = formatDateStr(refundDateRange.value[1])
    console.log('[BillingV2] fetchCheckedOutOrders:', vipuuid, 'range:', df, '-', dt)
    try {
      const res = await getCheckedOutOrders(vipuuid, df, dt)
      checkedOutOrders.value = Array.isArray(res.data) ? res.data : []
      console.log('[BillingV2] checkedOutOrders result:', checkedOutOrders.value.length, 'items')
      if (checkedOutOrders.value.length > 0) {
        console.log('[BillingV2] first order:', checkedOutOrders.value[0].exptxserno)
      }
    } catch (e) {
      console.log('[BillingV2] fetchCheckedOutOrders error:', e)
      checkedOutOrders.value = []
    }
    finally { checkedOutLoading.value = false }
  }

  async function addRefundToCart() {
    let added = 0
    // 先预加载所有需要的订单明细
    const needFetch = checkedOutOrders.value.filter(o => {
      const sels = checkedOutSelections.value[o.uuid] || {}
      return Object.values(sels).some(v => v)
    })
    for (const order of needFetch) {
      if (!voidOrderItems.value[order.uuid]) {
        await fetchVoidDetail(order.uuid)
      }
    }
    // 再同步处理选中项
    for (const order of needFetch) {
      const sels = checkedOutSelections.value[order.uuid] || {}
      const items = voidOrderItems.value[order.uuid] || []
      for (const [ditem, selected] of Object.entries(sels)) {
        if (!selected) continue
        const item = items.find((i: any) => i.ditem === ditem)
        if (!item) continue
        const existing = cart.value.find((ci: CartItem) => ci.code === item.srvcode && ci.ttype === item.ttype)
        if (existing) {
          existing.qty -= Math.abs(item.qty || 1)
        } else {
          cart.value.push({
            code: item.srvcode || '',
            name: item.itemname || item.srvcode || '',
            price: item.price || 0,
            qty: -Math.abs(item.qty || 1),
            ttype: item.ttype || 'S',
            stype: item.stype || 'N',
            secdisc: item.secdisc || 1,
            srvmondisc: 0,
            payMethod: 'cash',
            pmcode: item.pmcode || '',
            asscode1: item.asscode1 || '',
            asscode2: item.asscode2 || '',
            availableCards: [],
          })
        }
        added++
      }
    }
    if (added) ElMessage.success(`已添加 ${added} 项退款（员工信息已保留）`)
  }

  async function autoAddCardItems(card: VipCard) {
    if (card.comptype !== 'times') return
    if (!card.cardtypeuuid && !card.cardtype) return
    try {
      const res = await getCardtypeServiceItems(card.cardtypeuuid || '', card.cardtype || '')
      const items = (Array.isArray(res.data) ? res.data : res.data?.results ?? []) as CartableItem[]
      for (const item of items) {
        const existing = cart.value.find((c: CartItem) => c.code === item.code && c.ttype === (item.ttype || 'S'))
        if (!existing) {
          addToCart(item)
        }
      }
    } catch { /* ignore */ }
  }

  // ── 卡片交互 ──
 function selectCard(card: VipCard) {
   selectedCard.value = card
   cart.value.forEach((item) => {
     if (!item.availableCards.find((c) => c.ccode === card.ccode)) {
       item.availableCards.unshift(card)
     }
   })
    if (card.comptype === 'times') {
      setTimeout(() => autoAddCardItems(card), 100)
    }
 }

  // ── 购物车操作 ──
  const clickGuard = new Map<string, number>()

  function addToCart(item: CartableItem) {
    const now = Date.now()
    const last = clickGuard.get(item.code)
    if (last && now - last < 300) return
    clickGuard.set(item.code, now)

    const existing = cart.value.find((c) => c.code === item.code && c.ttype === (item.ttype || itemTab.value))
    if (existing) {
      existing.qty++
      return
    }

    const def = getDefaultEmployees()
    cart.value.push({
      code: item.code,
      name: item.name,
      price: parseFloat(item.price as unknown as string) || 0,
      qty: 1,
      ttype: (item.ttype || itemTab.value) as CartItem['ttype'],
      stype: itemTab.value === 'C' ? 'N' : 'N',
      secdisc: 1,
      srvmondisc: 0,
      payMethod: selectedCard.value ? 'card:' + selectedCard.value.ccode : 'cash',
      pmcode: def.pmcode,
      asscode1: def.asscode1,
      asscode2: def.asscode2,
      availableCards: selectedCard.value ? [selectedCard.value] : [],
    })
  }

  function getDefaultEmployees() {
    const vip = selectedVip.value
    return {
      pmcode: vip?.ecode || '',
      asscode1: vip?.ecode2 || '',
      asscode2: '',
    }
  }

  function removeFromCart(index: number) {
    cart.value.splice(index, 1)
  }

  function toggleRefund(index: number) {
    const item = cart.value[index]
    if (item.qty >= 0) item.qty = -Math.abs(item.qty || 1)
    else item.qty = Math.abs(item.qty || 1)
  }

  function updateCartItem(index: number, field: keyof CartItem, value: any) {
    const item = cart.value[index]
    if (item) (item as any)[field] = value
  }

  function clearCart() { cart.value = []; voidItems.value = [] }

  // ── 作废 ──
  function openVoidPanel() {
    voidPanelOpen.value = !voidPanelOpen.value
    if (voidPanelOpen.value && selectedVip.value) {
      fetchVoidOrders(selectedVip.value.uuid)
    }
  }

  async function fetchVoidOrders(vipuuid: string) {
    voidLoading.value = true
    voidOrders.value = []
    voidOrderItems.value = {}
    voidSelections.value = {}
    try {
      const res = await getHungByVipUuid(vipuuid)
      voidOrders.value = Array.isArray(res.data) ? res.data : []
    } catch {
      voidOrders.value = []
    } finally {
      voidLoading.value = false
    }
  }

  async function fetchVoidDetail(hunguuid: string) {
    if (voidOrderItems.value[hunguuid]) return
    try {
      const res = await getHungDetail(hunguuid)
      voidOrderItems.value[hunguuid] = Array.isArray(res.data) ? res.data : []
    } catch {
      voidOrderItems.value[hunguuid] = []
    }
  }

  function toggleVoidItem(hunguuid: string, ditem: string) {
    if (!voidSelections.value[hunguuid]) voidSelections.value[hunguuid] = {}
    voidSelections.value[hunguuid][ditem] = !voidSelections.value[hunguuid][ditem]
  }

  function confirmVoid() {
    let added = 0
    for (const [hunguuid, items] of Object.entries(voidOrderItems.value)) {
      const sels = voidSelections.value[hunguuid] || {}
      for (const [ditem, selected] of Object.entries(sels)) {
        if (!selected) continue
        const item = items.find((i: any) => i.ditem === ditem)
        if (!item) continue
        const existing = voidItems.value.find(i => i.code === item.srvcode && i.ttype === item.ttype)
        if (existing) {
          existing.qty -= Math.abs(item.qty)
        } else {
          voidItems.value.push({
            code: item.srvcode || '',
            name: item.itemname || item.srvcode || '',
            price: item.price || 0,
            qty: -Math.abs(item.qty || 1),
            ttype: item.ttype || 'S',
            stype: 'N',
            secdisc: item.secdisc || 1,
            srvmondisc: 0,
            payMethod: 'cash',
            pmcode: '',
            asscode1: '',
            asscode2: '',
            availableCards: [],
          })
        }
        added++
      }
    }
    if (added) ElMessage.success(`已添加 ${added} 项作废`)
    else ElMessage.warning('请先勾选要作废的项目')
  }

  // ── 拖拽 ──
  function onCardDragStart(card: VipCard) {
    draggedCard.value = card
  }

  function onCardDrop() {
    const card = draggedCard.value
    if (!card) return
    selectCard(card)
    // 双击计次卡自动加项目
    if (card.comptype === 'times') {
      // 触发自动加载
      setTimeout(() => autoAddCardItems(card), 100)
    }
    draggedCard.value = null
  }

  // ── 右键菜单 ──
  function showCardMenu(e: MouseEvent, card: VipCard) {
    e.preventDefault()
    cardMenuPos.value = { x: e.clientX, y: e.clientY }
    cardMenuCard.value = card
    cardMenuVisible.value = true
  }

  function closeCardMenu() {
    cardMenuVisible.value = false
    cardMenuCard.value = null
  }

  function menuViewCard() { closeCardMenu(); ElMessage.info('卡详情（待实现）') }
  function menuUseCard() { if (cardMenuCard.value) selectCard(cardMenuCard.value); closeCardMenu() }
  function menuConsumeItems() { if (cardMenuCard.value) { selectCard(cardMenuCard.value); autoAddCardItems(cardMenuCard.value) }; closeCardMenu() }
  function menuRecharge() { if (cardMenuCard.value) { selectCard(cardMenuCard.value); itemTab.value = 'I' }; closeCardMenu() }

  // ── 保存挂账 ──
  async function saveHung(): Promise<boolean> {
    if (!selectedVip.value) return false
    saving.value = true
    try {
      const allItems = [...cart.value, ...voidItems.value]
      const items = allItems.map((i) => ({
        ttype: i.ttype,
        srvcode: i.code,
        s_qty: i.qty,
        s_price: i.price,
        stype: i.stype,
        secdisc: i.secdisc,
        srvmondisc: i.srvmondisc,
        pay_type: i.payMethod,
        card_ccode: i.payMethod?.startsWith('card:') ? i.payMethod.slice(5) : '',
        pmcode: i.pmcode || '',
        asscode1: i.asscode1 || '',
        asscode2: i.asscode2 || '',
        promotionsid: i.promotionsid || '',
      }))
      const payload = { company, storecode: storecode || '01', vipuuid: selectedVip.value.uuid, items }
      const res = await request.post('/adviser/save_hung/', payload)
      if ((res.data as any)?.ok === true) {
        ElMessage.success('挂账保存成功')
        clearCart()
        if (selectedVip.value) await fetchVipCards(selectedVip.value.uuid)
        return true
      } else {
        ElMessage.error((res.data as any)?.message || '保存失败')
        return false
      }
    } catch (err: any) {
      ElMessage.error('保存失败: ' + (err?.message || String(err)))
      return false
    } finally {
      saving.value = false
    }
  }

  function formatDateStr(d: any): string {
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    return '' + y + m + day
  }

  function collectCategoryCodes(nodes: CategoryNode[], targetCode: string): string[] {
    const result: string[] = [targetCode]
    for (const n of nodes) {
      if (n.code === targetCode && n.children) {
        for (const child of n.children) {
          result.push(child.code)
          if (child.children) {
            for (const gc of child.children) result.push(gc.code)
          }
        }
      }
      if (n.children) {
        for (const child of n.children) {
          if (child.code === targetCode && child.children) {
            for (const gc of child.children) result.push(gc.code)
          }
        }
      }
    }
    return result
  }

  // ====== 工具 ======
  function ttypeLabel(t: string): string {
    return { S: '服务', G: '商品', C: '售卡', I: '充值' }[t] || t
  }

  function formatDate(d: string): string {
    return d ? d.replace(/^(\d{4})(\d{2})(\d{2})$/, '$1-$2-$3') : ''
  }

  function empName(ecode: string): string {
    const emp = employees.value.find(e => e.ecode === ecode)
    return emp ? emp.ename + ' (' + ecode + ')' : ecode
  }

  // watch itemTab change → 刷新选品
  let _recalc = false
  watch(editQty, (newQty, oldQty) => {
    if (_recalc || !oldQty || !editAmount.value) return
    _recalc = true
    const unitPrice = editAmount.value / oldQty
    editAmount.value = Math.round(newQty * unitPrice * 100) / 100
    _recalc = false
  })
  watch([editQty, editAmount], () => {
    if (_recalc || !editQty.value || !editAmount.value) return
    editDiscountAmt.value = +(editQty.value * Math.round((editAmount.value / editQty.value) * 100) / 100 - editAmount.value).toFixed(2)
  })

  watch(itemTab, () => {
    itemKeyword.value = ''
    selectedPromotion.value = null
    if (itemTab.value === 'P') {
      fetchPromotions()
    } else {
      fetchItems()
    }
  })

  return {
    company, storecode,
    vipKeyword, searchResults, noResults,
    selectedVip, selectedCard, vipCards, activeCardGroups, cardGroups,
    itemTab, itemKeyword, allItems, filteredItems, itemsLoading,
    categories, selectedCategory,
    employees, cart, cartGroups, cartTotal, saving,
    searchVip, selectVip, fetchVipCards, fetchItems, fetchPromotions, fetchEmployees,
    selectCard, addToCart, removeFromCart, toggleRefund, autoAddCardItems,
    updateCartItem, clearCart, saveHung, getDefaultEmployees,
    ttypeLabel, formatDate, empName,
    // 模式
    billingMode, switchBillingMode,
    refundDateRange, checkedOutOrders, checkedOutSelections, checkedOutLoading,
    fetchCheckedOutOrders, addRefundToCart,
    // 作废
    voidPanelOpen, voidOrders, voidOrderItems, voidLoading, voidSelections, voidItems,
    openVoidPanel, fetchVoidOrders, fetchVoidDetail, toggleVoidItem, confirmVoid,
    // 活动
    promotions, selectedPromotion, promotionsLoading, promotionDetails,
    selectAndLoadPromotion, addPromotionItem, addComboToCart,
    // 拖拽
    draggedCard, onCardDragStart, onCardDrop,
    // 右键菜单
    cardMenuVisible, cardMenuPos, cardMenuCard, showCardMenu, closeCardMenu,
    menuViewCard, menuUseCard, menuConsumeItems, menuRecharge,
    // 售卡
    cardSaleMode, cardSaleItems, showPriceSelector,
    itemCode, itemName, editQty, editAmount, editDiscountPct, editDiscountAmt,
    editUnitPrice, editSubtotal,
    addCardSale, confirmCardSale, fetchCardPrices,
    // 充值
    rechargeMode, rechargeAmounts, refundableCards, addRecharge, addCardRefund,
  }
}
