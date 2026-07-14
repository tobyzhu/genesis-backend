<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="appStore.sidebarCollapsed ? '64px' : '220px'" class="layout-aside">
      <div class="logo-area">
        <span v-if="!appStore.sidebarCollapsed" class="logo-text">Genesis 管理系统</span>
        <span v-else class="logo-mini">G</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="appStore.sidebarCollapsed"
        :collapse-transition="false"
        router
        class="layout-menu"
      >
        <template v-for="item in menuItems" :key="item.path">
          <el-menu-item v-if="!item.meta?.hidden" :index="item.path">
            <el-icon v-if="item.meta?.icon">
              <component :is="item.meta.icon" />
            </el-icon>
            <template #title>{{ item.meta?.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <!-- 主区域 -->
    <el-container class="layout-main">
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="appStore.toggleSidebar" :size="20">
            <Fold v-if="!appStore.sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title">{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag v-if="appStore.currentCompany" size="small" type="info" class="store-tag">
            {{ appStore.currentCompany }} / {{ appStore.currentStoreName || appStore.currentStorecode }}
          </el-tag>
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-avatar :size="28" icon="UserFilled" />
              <span class="user-name">{{ appStore.displayName }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="appStore.allowedStores.length > 1" @click="showStoreSelector">
                  切换门店
                </el-dropdown-item>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/store/app'
import { logout as logoutApi } from '@/api/common'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const menuItems = router
  .getRoutes()
  .find((r) => r.path === '/')
  ?.children?.filter((c) => !c.meta?.hidden) ?? []

function handleLogout() {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' }).then(async () => {
    try {
      await logoutApi()
    } catch {
      // 即使注销接口失败也清除本地状态
    }
    appStore.logout()
    router.push('/login')
  })
}

function showStoreSelector() {
  router.push('/select-store')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.layout-aside {
  background: #304156;
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.25s;
}
.logo-area {
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.logo-mini {
  font-size: 22px;
}
.layout-menu {
  border-right: none;
}
.layout-main {
  display: flex;
  flex-direction: column;
}
.layout-header {
  height: 50px !important;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.collapse-btn {
  cursor: pointer;
  color: #606266;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.user-name {
  font-size: 14px;
  color: #303133;
}
.store-tag {
  margin-right: 4px;
}
.layout-content {
  background: #f0f2f5;
  padding: 16px;
  overflow-y: auto;
  flex: 1;
}
</style>
