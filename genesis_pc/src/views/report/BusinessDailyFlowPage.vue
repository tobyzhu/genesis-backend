<template>
  <ReportShell :definition="businessDailyFlowDef" />
</template>

<script setup lang="ts">
import ReportShell from '@/components/report/ReportShell.vue'
import { businessDailyFlowDef } from '@/views/report/definitions/businessDailyFlow'
</script>
