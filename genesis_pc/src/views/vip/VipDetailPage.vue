<template>
  <div class="vip-detail">
    <div class="page-header">
      <h2>会员详情</h2>
      <el-button @click="$router.push('/vip')">返回列表</el-button>
    </div>

    <el-card shadow="never">
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="基本信息" name="basic">
          <el-descriptions :column="2" border v-loading="loading">
            <el-descriptions-item label="会员号">{{ vip.vcode }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ vip.vname }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ vip.mtcode }}</el-descriptions-item>
            <el-descriptions-item label="等级">{{ vip.viplevel }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ vip.sex }}</el-descriptions-item>
            <el-descriptions-item label="生日">{{ vip.birth }}</el-descriptions-item>
            <el-descriptions-item label="入会日期">{{ vip.indate }}</el-descriptions-item>
            <el-descriptions-item label="状态">{{ vip.status }}</el-descriptions-item>
            <el-descriptions-item label="会员类型">{{ vip.viptype }}</el-descriptions-item>
            <el-descriptions-item label="电话">{{ vip.telph }}</el-descriptions-item>
            <el-descriptions-item label="微信">{{ vip.wechat }}</el-descriptions-item>
            <el-descriptions-item label="地址">{{ vip.addr }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ vip.email }}</el-descriptions-item>
            <el-descriptions-item label="来源">{{ vip.sourceName || vip.source }}</el-descriptions-item>
            <el-descriptions-item label="职业">{{ vip.occupation }}</el-descriptions-item>
            <el-descriptions-item label="负责顾问">{{ vip.ecode }}</el-descriptions-item>
            <el-descriptions-item label="指定美疗师">{{ vip.ecode2 }}</el-descriptions-item>
            <el-descriptions-item label="备注" :span="2">{{ vip.vdesc }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

                <el-tab-pane label="会员卡" name="cards">
          <template v-if="cards.length">
            <el-tree :data="treeData" node-key="id" default-expand-all highlight-current
              :indent="20"
              @node-click="handleCardNodeClick">
              <template #default="{ data }">
                <span v-if="data.level === 'promotions'" style="font-weight:700;font-size:14px;padding:4px 0;color:#303133">{{ data.label }}</span>
                <span v-else-if="data.level === 'comptype'" style="font-weight:500;font-size:13px;padding:3px 0;color:#606266">{{ data.label }}</span>
                <div v-else style="display:flex;align-items:center;gap:16px;font-size:13px;padding:6px 0;width:100%">
                  <span style="min-width:100px;font-weight:500">{{ data.card.ccode }}</span>
                  <span style="min-width:120px">{{ data.card.cardname }}</span>
                  <span style="min-width:60px">{{ getStypeLabel(data.card.stype) }}</span>
                  <span style="min-width:100px;text-align:right">¥{{ parseFloat(data.card.leftmoney ?? 0).toFixed(2) }}</span>
                  <span style="min-width:80px;text-align:right">{{ data.card.leftqty ?? 0 }}</span>
                  <span style="min-width:90px">{{ data.card.valdate ? formatDate(data.card.valdate) : '' }}</span>
                  <span style="min-width:60px">{{ getStatusLabel(data.card.status) }}</span>
                  <span style="min-width:80px;text-align:right">¥{{ parseFloat(data.card.s_price ?? 0).toFixed(2) }}</span>
                  <span style="min-width:200px;color:#909399;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{{ data.card.carddesc || '' }}</span>
                </div>
              </template>
            </el-tree>

            <div v-if="selectedCard" style="margin-top:16px;border-top:1px solid #ebeef5;padding-top:16px">
              <h4 style="margin:0 0 12px 0;font-size:15px;font-weight:600">{{ selectedCard.ccode }} - {{ selectedCard.cardname }} 消费记录</h4>
              <el-table :data="cardConsumptions" v-loading="cardConsLoading" stripe max-height="400"
>
                <el-table-column label="日期" width="110">
                  <template #default="{ row }">
                    {{ row.vsdate ? formatDate(row.vsdate) : '' }}
                  </template>
                </el-table-column>
                <el-table-column prop="itemname" label="项目名称" min-width="140" />
                <el-table-column prop="storecode" label="店铺" width="70" />
                <el-table-column prop="ccode" label="付款卡号" min-width="130" />
                <el-table-column prop="exptxserno" label="流水号" width="80" />
                <el-table-column prop="ttype" label="类型" width="70" />
                <el-table-column prop="stype" label="属性" width="60" />
                <el-table-column prop="s_qty" label="数量" width="60" align="right" />
                <el-table-column prop="s_price" label="单价" width="80" align="right">
                  <template #default="{ row }">
                    ¥{{ parseFloat(row.s_price ?? 0).toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column prop="amount" label="金额" width="100" align="right">
                  <template #default="{ row }">
                    ¥{{ parseFloat(row.amount ?? 0).toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column prop="pmname" label="操作人" width="100" />
                <el-table-column prop="secname" label="协助人" width="100" />
              </el-table>
              <el-empty v-if="!cardConsLoading && cardConsumptions.length === 0" description="该卡无消费记录" />
            </div>
          </template>
          <el-empty v-else v-loading="cardsLoading" description="暂无会员卡" />
        </el-tab-pane>

        <el-tab-pane label="消费记录" name="consumption">
          <el-table
            v-if="consumptions.length"
            :data="consumptions"
            v-loading="consumptionLoading"
            stripe
            :span-method="hideDupExptxserno"
          >
            <el-table-column label="日期" width="120">
              <template #default="{ row }">
                {{ row.vsdate ? row.vsdate.replace(/^(\d{4})(\d{2})(\d{2})$/, '$1-$2-$3') : '' }}
              </template>
            </el-table-column>
            <el-table-column prop="storecode" label="店铺" width="65" />
            <el-table-column prop="exptxserno" label="流水号" width="80" />
            <el-table-column prop="ccode" label="付款卡号" min-width="130" />
            <el-table-column prop="itemname" label="项目名称" min-width="160" />
            <el-table-column prop="ttype" label="类型" width="80" />
            <el-table-column prop="stype" label="属性" width="70" />
            <el-table-column prop="s_qty" label="数量" width="70" align="right" />
            <el-table-column prop="s_price" label="单价" width="90" align="right">
              <template #default="{ row }">
                ¥{{ parseFloat(row.s_price ?? 0).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="100" align="right">
              <template #default="{ row }">
                ¥{{ parseFloat(row.amount ?? 0).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="pmname" label="操作人" width="100" />
            <el-table-column prop="secname" label="协助人" width="100" />
          </el-table>
          <el-empty v-else v-loading="consumptionLoading" description="暂无消费记录" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-backtop target=".vip-detail" :right="40" :bottom="40" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getVipDetail, getVipCards, getVipConsumption, getAppoptionBySeg } from '@/api/vip'
import type { Vip } from '@/types'
import { ElMessage } from 'element-plus'

const route = useRoute()
const vipUuid = route.params.id as string

const activeTab = ref('basic')
const loading = ref(false)

const vip = ref<Vip>({
  uuid: '',
  vcode: '',
  vname: '',
  mtcode: '',
  viplevel: '',
  sex: '',
  birth: '',
  indate: '',
  status: '',
  viptype: '',
  telph: '',
  wechat: '',
  addr: '',
  email: '',
  qq: '',
  source: '',
  occupation: '',
  ecode: '',
  ecode2: '',
  company: '',
  storecode: '',
  vdesc: '',
})

const cards = ref<any[]>([])
function getComptypeLabel(ct: string): string {
  const labels: Record<string, string> = {"amount": "储值卡", "times": "计次卡", "period": "计时卡"}
  return labels[ct] || ct
}

function getStypeLabel(stype: string): string {
  return stype === 'N' ? '正常' : stype === 'P' ? '赠送' : stype || ''
}

function getStatusLabel(status: string): string {
  return status === 'O' ? '正常' : status === 'P' ? '挂账' : status || ''
}

function formatDate(d: string): string {
  return d ? d.replace(/^(\d{4})(\d{2})(\d{2})$/, '$1-$2-$3') : ''
}

const selectedCard = ref<any>(null)
const cardConsumptions = ref<any[]>([])
const cardConsLoading = ref(false)

function handleCardNodeClick(data: any) {
  if (data.level === 'card') {
    selectedCard.value = data.card
    fetchCardConsumptions(data.card.ccode)
  }
}

async function fetchCardConsumptions(ccode: string) {
  cardConsLoading.value = true
  try {
    const res = await getVipConsumption(vipUuid)
    const list = Array.isArray(res.data) ? res.data : res.data?.results ?? []
    cardConsumptions.value = list
      .filter((r: any) => (r.ccode || '') === ccode)
      .sort((a: any, b: any) => (b.vsdate || '').localeCompare(a.vsdate || ''))
  } catch {
    cardConsumptions.value = []
  } finally {
    cardConsLoading.value = false
  }
}

const treeData = computed(() => {
  // 第一层: promotionsid, 第二层: comptype
  const pidGroups: Record<string, Record<string, any[]>> = {}
  for (const card of cards.value) {
    const pid = card.promotionsid || '0'
    const ct = card.comptype || 'other'
    if (!pidGroups[pid]) pidGroups[pid] = {}
    if (!pidGroups[pid][ct]) pidGroups[pid][ct] = []
    pidGroups[pid][ct].push(card)
  }
  const result: any[] = []
  for (const [pid, ctGroups] of Object.entries(pidGroups)) {
    // 从该分组中第一张卡取 promotionname
    const firstCard = Object.values(ctGroups).flat()[0]
    const pidLabel = pid === '0' ? '正常销售' : (firstCard.promotionname || '活动:' + pid)
    const total = Object.values(ctGroups).flat().length
    const children: any[] = []
    for (const [ct, cardList] of Object.entries(ctGroups)) {
      children.push({
        id: 'pid-' + pid + '-ct-' + ct,
        label: getComptypeLabel(ct) + ' (' + cardList.length + '张)',
        level: 'comptype',
        children: cardList.map((card: any) => ({
          id: card.uuid,
          card,
          level: 'card'
        }))
      })
    }
    result.push({
      id: 'pid-' + pid,
      label: pidLabel + ' (' + total + '张)',
      level: 'promotions',
      children
    })
  }
  return result
})
const cardsLoading = ref(false)

const consumptions = ref<any[]>([])
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


const consumptionLoading = ref(false)

onMounted(() => {
  fetchSourceOptions()
  fetchVipDetail()
})

async function fetchVipDetail() {
  loading.value = true
  try {
    const res = await getVipDetail(vipUuid)
    vip.value = res.data
    // 来源名称映射
    if (vip.value.source && sourceOptions.value.length) {
      const found = sourceOptions.value.find(o => o.itemname === vip.value.source)
      if (found) vip.value.sourceName = found.itemvalues
    }
  } catch {
    // 错误已在拦截器中统一处理
  } finally {
    loading.value = false
  }
}

async function fetchCards() {
  if (cards.value.length || cardsLoading.value) return
  cardsLoading.value = true
  try {
    const res = await getVipCards(vipUuid)
    cards.value = Array.isArray(res.data) ? res.data : res.data?.results ?? []
  } catch {
    // 错误已在拦截器中统一处理
  } finally {
    cardsLoading.value = false
  }
}

async function fetchConsumptions() {
  if (consumptions.value.length || consumptionLoading.value) return
  consumptionLoading.value = true
  try {
    const res = await getVipConsumption(vipUuid)
    consumptions.value = Array.isArray(res.data) ? res.data : res.data?.results ?? []

  } catch {
    // 错误已在拦截器中统一处理
  } finally {
    consumptionLoading.value = false
  }
}

/** 同一流水号合并单元格 */
const consumeSpanMap = ref<number[]>([])

function buildConsumeSpanMap() {
  const data = consumptions.value
  const map: number[] = []
  if (!data.length) { consumeSpanMap.value = map; return }
  let i = 0
  while (i < data.length) {
    const exptx = data[i].exptxserno || ''
    let j = i + 1
    while (j < data.length && (data[j].exptxserno || '') === exptx) j++
    const count = j - i
    for (let k = i; k < j; k++) {
      map[k] = k === i ? count : 0
    }
    i = j
  }
  consumeSpanMap.value = map
}

function consumeSpanMethod({ rowIndex, columnIndex }: { rowIndex: number, columnIndex: number }): [number, number] {
  // 合并列: 日期(0), 店铺(1), 流水号(2), 付款卡号(3)
  if (columnIndex <= 3 && consumeSpanMap.value[rowIndex]) {
    return [consumeSpanMap.value[rowIndex], 1]
  }
  return [1, 1]
}

function handleConsumeSort() {
  buildConsumeSpanMap()
}

function handleTabChange(name: string) {
  if (name === 'cards') fetchCards()
  if (name === 'consumption') fetchConsumptions()
}
</script>

<style scoped>
.vip-detail {
  padding: 16px;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}
</style>
