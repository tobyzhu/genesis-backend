<template>
  <el-drawer v-model="drawerVisible" :title="title" size="500px" @close="closeProfile">
    <div v-loading="loading" style="min-height:200px">
      <template v-if="basicInfo">
        <template v-if="!basicInfo.uuid && !basicInfo.vname">
          <div style="padding:40px;text-align:center;color:#c0c4cc">暂无数据（API 返回空）</div>
        </template>
        <template v-else>
        <!-- 基本信息 -->
        <el-descriptions :column="2" border size="small" style="margin-bottom:16px">
          <el-descriptions-item label="姓名">{{ basicInfo.vname }}</el-descriptions-item>
          <el-descriptions-item label="会员号">{{ basicInfo.vcode }}</el-descriptions-item>
          <el-descriptions-item label="手机">{{ basicInfo.mtcode }}</el-descriptions-item>
          <el-descriptions-item label="等级">{{ basicInfo.viplevel || '--' }}</el-descriptions-item>
          <el-descriptions-item label="顾问">{{ empName(basicInfo.ecode) }}</el-descriptions-item>
          <el-descriptions-item label="美疗师">{{ empName(basicInfo.ecode2) }}</el-descriptions-item>
        </el-descriptions>

        </template>
        <!-- Tab 切换 -->
        <el-tabs v-model="activeTab">
          <el-tab-pane label="名下卡项" name="cards">
            <div v-if="cards.length" class="profile-cards">
              <div v-for="card in cards" :key="card.uuid" class="profile-card"
                :class="{ 'status-p': card.status === 'P' }">
                <div class="pc-left">
                  <div class="pc-name">{{ card.cardname }}</div>
                  <div class="pc-code">{{ card.ccode }}</div>
                </div>
                <div class="pc-right">
                  <span v-if="card.comptype === 'times'" class="pc-bal">{{ card.leftqty ?? 0 }} 次</span>
                  <span v-else class="pc-bal">¥{{ parseFloat(card.leftmoney ?? 0).toFixed(0) }}</span>
                  <span v-if="card.valdate" class="pc-expire">{{ card.valdate.replace(/^(\d{4})(\d{2})(\d{2})$/, '$1-$2-$3') }}</span>
                </div>
                <el-tag v-if="card.stype === 'P'" size="small" type="warning">赠送</el-tag>
                <el-tag v-if="card.status === 'P'" size="small" type="warning">挂账</el-tag>
              </div>
            </div>
            <el-empty v-else description="无名下卡片" :image-size="50" />
          </el-tab-pane>

          <el-tab-pane label="消费记录" name="consumption">
            <div v-if="consumption.length" class="profile-list">
              <div v-for="(c, i) in consumption" :key="i" class="profile-list-item">
                <span class="pli-date">{{ c.vsdate || '--' }}</span>
                <span class="pli-name">{{ c.srvname || c.srvcode || '--' }}</span>
                <span class="pli-amount">¥{{ (c.s_amount || 0).toFixed(0) }}</span>
                <el-tag size="small" :type="c.psstatus === '70' ? 'success' : 'warning'">
                  {{ c.psstatus === '70' ? '已结账' : '挂账' }}
                </el-tag>
              </div>
            </div>
            <el-empty v-else description="无消费记录" :image-size="50" />
          </el-tab-pane>

          <el-tab-pane label="沟通回访" name="communications">
            <div v-if="communications.length" class="profile-list">
              <div v-for="(c, i) in communications" :key="i" class="profile-list-item comm-item">
                <span class="pli-date">{{ c.cdate || c.create_time || '--' }}</span>
                <span class="pli-type">
                  <el-tag size="small" :type="commTypeTag(c.casetype)">{{ c.casetype_name || c.casetype || '沟通' }}</el-tag>
                </span>
                <span class="pli-content">{{ c.detail || c.detaildescription || '' }}</span>
                <span class="pli-emp">{{ c.ecode || '--' }}</span>
              </div>
            </div>
            <el-empty v-else description="无沟通记录" :image-size="50" />
          </el-tab-pane>
        </el-tabs>
      </template>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useVipProfile } from '@/composables/useVipProfile'

const props = defineProps<{
  profile: ReturnType<typeof useVipProfile>
}>()

const { drawerVisible, loading, basicInfo, cards, consumption, communications, closeProfile } = props.profile

const activeTab = ref('cards')

const title = computed(() => {
  const v = basicInfo.value
  return v ? `${v.vname} (${v.vcode})` : '客户详情'
})

function empName(ecode: string): string {
  return ecode || '--'
}

function commTypeTag(t: string): string {
  const map: Record<string, string> = { '10': 'info', '20': 'warning', '30': 'success' }
  return map[t] || 'info'
}
</script>

<style scoped>
.profile-cards { display:flex; flex-direction:column; gap:6px; }
.profile-card {
  display:flex; align-items:center; gap:10px; padding:8px 10px;
  border:1px solid #ebeef5; border-radius:6px; flex-wrap:wrap;
}
.profile-card.status-p { background:#fef7e0; }
.pc-left { flex:1; }
.pc-name { font-size:13px; font-weight:500; }
.pc-code { font-size:11px; color:#909399; }
.pc-right { text-align:right; }
.pc-bal { font-size:14px; font-weight:600; color:#e6a23c; display:block; }
.pc-expire { font-size:10px; color:#c0c4cc; }

.profile-list { display:flex; flex-direction:column; gap:4px; }
.profile-list-item {
  display:flex; align-items:center; gap:8px; padding:6px 8px;
  border-bottom:1px solid #f5f5f5; font-size:12px;
}
.pli-date { width:90px; color:#909399; flex-shrink:0; }
.pli-name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.pli-amount { width:80px; text-align:right; font-weight:600; }
.pli-type { width:60px; flex-shrink:0; }
.pli-content { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#606266; }
.pli-emp { width:60px; color:#909399; }
</style>
