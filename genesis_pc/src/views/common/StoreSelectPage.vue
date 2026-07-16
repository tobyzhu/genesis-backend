<template>
  <div class="select-store-page">
    <div class="select-card">
      <h2>选择门店</h2>
      <p class="subtitle">请选择要登录的门店</p>
      <div class="store-list">
        <div
          v-for="s in stores"
          :key="s.storecode"
          class="store-item"
          :class="{ active: selected === s.storecode }"
          @click="selected = s.storecode"
        >
          <div class="store-name">{{ s.storename }}</div>
          <div class="store-code">编码: {{ s.storecode }}</div>
        </div>
      </div>
      <el-button type="primary" size="large" class="confirm-btn" :disabled="!selected" @click="handleConfirm">
        确认
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/store/app'

const router = useRouter()
const appStore = useAppStore()

const stores = appStore.allowedStores
const selected = ref('')

function handleConfirm() {
  if (!selected.value) return
  const store = stores.find(s => s.storecode === selected.value)
  if (store) {
    appStore.selectStore(store.storecode, store.storename)
    router.push('/')
  }
}
</script>

<style scoped>
.select-store-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.select-card {
  width: 380px;
  padding: 32px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  text-align: center;
}
h2 { margin: 0 0 4px; font-weight:600; color:#303133; }
.subtitle { font-size:14px; color:#909399; margin:0 0 20px; }
.store-list { display:flex; flex-direction:column; gap:8px; margin-bottom:20px; }
.store-item { padding:12px; border:1px solid #ebeef5; border-radius:6px; cursor:pointer; text-align:left; transition:.15s; }
.store-item:hover { border-color:#409eff; background:#ecf5ff; }
.store-item.active { border-color:#409eff; background:#d9ecff; }
.store-name { font-size:15px; font-weight:500; }
.store-code { font-size:12px; color:#909399; margin-top:2px; }
.confirm-btn { width:100%; }
</style>
