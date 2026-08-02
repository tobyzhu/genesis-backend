<template>
  <el-drawer v-model="visible" :size="550" title="客户详情" @close="handleClose">
    <template #title>
      <span style="font-size:16px;font-weight:600">
        {{ data?.vname || '客户详情' }}
        <el-tag v-if="data?.vcode" size="small" style="margin-left:8px">{{ data.vcode }}</el-tag>
      </span>
    </template>

    <div v-loading="loading">
      <div v-if="data" style="padding:0 4px">
        <el-card shadow="never" style="margin-bottom:12px">
          <el-descriptions :column="2" size="small" border>
            <el-descriptions-item label="手机号">{{ data.mtcode || '\u2014' }}</el-descriptions-item>
            <el-descriptions-item label="等级">{{ data.viplevel || '\u2014' }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ data.sex || '\u2014' }}</el-descriptions-item>
            <el-descriptions-item label="生日">{{ data.birth || '\u2014' }}</el-descriptions-item>
            <el-descriptions-item label="入会日期">{{ data.indate || '\u2014' }}</el-descriptions-item>
            <el-descriptions-item label="顾问">{{ data.ecode || '\u2014' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-tabs>
          <el-tab-pane label="卡套餐" name="cards">
            <div v-if="cards.length">
              <div v-for="c in cards" :key="c.ccode" style="padding:8px 0;border-bottom:1px solid var(--g-color-border);font-size:13px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                  <span style="font-weight:500">{{ c.cardname || c.cardtype }}</span>
                  <el-tag :type="c.status === 'Y' ? 'success' : 'danger'" size="small">{{ c.status === 'Y' ? '\u6709\u6548' : '\u65e0\u6548' }}</el-tag>
                </div>
                <div style="color:var(--g-color-text-muted);margin-top:4px">\u5361\u53f7\uff1a{{ c.ccode }} \uff5c \u4f59\u989d\uff1a\u00a5{{ Number(c.leftmoney ?? 0).toFixed(2) }} \uff5c \u6b21\u6570\uff1a{{ c.leftqty ?? 0 }}</div>
              </div>
            </div>
            <el-empty v-else v-loading="loading" description="\u6682\u65e0\u5361\u5957\u9910" />
          </el-tab-pane>

          <el-tab-pane label="\u6d88\u8d39\u8bb0\u5f55" name="consumption">
            <el-table :data="consumptions" stripe size="small" max-height="360">
              <el-table-column label="\u65e5\u671f" width="90">
                <template #default="{row}">{{ row.vsdate ? (''+row.vsdate).replace(/^(\\d{4})(\\d{2})(\\d{2})$/, '$1-$2-$3') : '\u2014' }}</template>
              </el-table-column>
              <el-table-column prop="itemname" label="\u9879\u76ee" min-width="120" show-overflow-tooltip />
              <el-table-column label="\u91d1\u989d" width="80" align="right">
                <template #default="{row}">\u00a5{{ Number(row.s_price ?? 0).toFixed(2) }}</template>
              </el-table-column>
              <el-table-column prop="pmname" label="\u64cd\u4f5c\u4eba" width="80" />
            </el-table>
            <el-empty v-if="!consumptions.length && !loading" description="\u6682\u65e0\u6d88\u8d39\u8bb0\u5f55" />
          </el-tab-pane>
        </el-tabs>
      </div>
      <el-empty v-else-if="!loading" description="\u6682\u65e0\u6570\u636e" />
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { getVipDetail, getVipCards, getVipConsumption } from '@/api/vip'
import type { Vip } from '@/types'

const props = defineProps<{
  profile: any
  employees?: any[]
  vipuuid?: string
}>()

const visible = ref(false)
const loading = ref(false)
const data = ref<Partial<Vip> | null>(null)
const cards = ref<any[]>([])
const consumptions = ref<any[]>([])

// React to drawer visibility & uuid changes
watch(visible, (val) => {
  if (!val && props.profile?.drawerVisible) props.profile.drawerVisible = false
})
watch(() => props.vipuuid, (uuid) => {
  if (uuid) { visible.value = true; loadData(uuid) }
}, { immediate: false })

function handleClose() {
  visible.value = false
  if (props.profile?.closeProfile) props.profile.closeProfile()
}

async function loadData(vipUuid: string) {
  if (!vipUuid) return
  loading.value = true
  data.value = null
  cards.value = []
  consumptions.value = []
  try {
    const [detailRes, cardsRes, consRes] = await Promise.all([
      getVipDetail(vipUuid).catch(() => null),
      getVipCards(vipUuid).catch(() => null),
      getVipConsumption(vipUuid).catch(() => null),
    ])
    if (detailRes?.data) data.value = detailRes.data
    if (cardsRes?.data) cards.value = Array.isArray(cardsRes.data) ? cardsRes.data : (cardsRes.data?.results ?? [])
    if (consRes?.data) consumptions.value = Array.isArray(consRes.data) ? consRes.data : (consRes.data?.results ?? [])
  } catch { /* ignore */ }
  finally { loading.value = false }
}

// Expose loadData so the parent can trigger it
defineExpose({ loadData })
</script>