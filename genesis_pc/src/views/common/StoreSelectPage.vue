<template>
  <div class="store-page">
    <div class="store-card">
      <h2 class="store-title">选择门店</h2>
      <p class="store-hint">你拥有多个门店的访问权限，请选择要进入的门店</p>
      <div class="store-list">
        <div
          v-for="s in appStore.allowedStores"
          :key="s.storecode"
          class="store-item"
          :class="{ active: appStore.currentStorecode === s.storecode }"
          @click="handleSelect(s.storecode, s.storename)"
        >
          <span class="store-name">{{ s.storename || s.storecode }}</span>
          <span class="store-code">{{ s.storecode }}</span>
        </div>
      </div>
      <div v-if="appStore.allowedStores.length === 0" class="empty-hint">
        暂无可访问的门店，请联系管理员
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAppStore } from '@/store/app'
import { ElMessage } from 'element-plus'

const router = useRouter()
const appStore = useAppStore()

function handleSelect(storecode: string, storename: string) {
  appStore.selectStore(storecode, storename)
  ElMessage.success(`已切换至 ${storename || storecode}`)
  router.push('/')
}
</script>

<style scoped>
.store-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.store-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}
.store-title {
  text-align: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #303133;
}
.store-hint {
  text-align: center;
  font-size: 13px;
  color: #909399;
  margin-bottom: 24px;
}
.store-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.store-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.store-item:hover {
  border-color: #409eff;
  background: #ecf5ff;
}
.store-item.active {
  border-color: #409eff;
  background: #ecf5ff;
}
.store-name {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
}
.store-code {
  font-size: 12px;
  color: #909399;
}
.empty-hint {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}
</style>
