<template>
  <ReportShell :definition="cardBalanceDef" :extras="extras">
    <template #filters>
      <span class="filter-label">卡类型：</span>
      <el-select v-model="extras.comptype" size="small" clearable placeholder="全部" style="width: 110px">
        <el-option label="储值卡" value="amount" />
        <el-option label="疗程卡" value="times" />
      </el-select>

      <span class="filter-label">属性：</span>
      <el-select v-model="extras.nature" size="small" clearable placeholder="全部" style="width: 100px">
        <el-option label="正常" value="正常" />
        <el-option label="赠送" value="赠送" />
      </el-select>

      <el-input
        v-model="extras.keyword"
        placeholder="卡号/会员号/卡类"
        clearable
        size="small"
        style="width: 180px"
      />

      <el-checkbox v-model="extras.only_with_balance" size="small">仅显示有余额</el-checkbox>
    </template>
  </ReportShell>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import ReportShell from '@/components/report/ReportShell.vue'
import { cardBalanceDef } from '@/views/report/definitions/cardBalance'

const extras = reactive({
  comptype: '',
  nature: '',
  keyword: '',
  only_with_balance: true,
})
</script>

<style scoped>
.filter-label {
  font-size: 13px;
  color: var(--g-color-text-secondary);
  white-space: nowrap;
}
</style>
