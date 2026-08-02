<template>
  <div class="login-page">
    <div class="login-shell">
      <div class="login-brand">
        <div class="brand-mark">G</div>
        <h1 class="brand-title">Genesis 美业管理系统</h1>
        <p class="brand-desc">会员、开单、收银、报表一站式门店管理</p>
        <div class="brand-features">
          <div class="feature"><el-icon><User /></el-icon><span>会员档案与卡项管理</span></div>
          <div class="feature"><el-icon><Ticket /></el-icon><span>手工开单与收银结账</span></div>
          <div class="feature"><el-icon><DataAnalysis /></el-icon><span>经营业绩与卡余额报表</span></div>
        </div>
      </div>
      <div class="login-panel">
        <h2 class="login-title">登录系统</h2>
        <p class="login-sub">使用门店 WiFi 环境下的员工账号</p>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="0"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="company">
            <el-input v-model="form.company" placeholder="公司编码">
              <template #prefix><el-icon><OfficeBuilding /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-form-item prop="usercode">
            <el-input v-model="form.usercode" placeholder="用户名">
              <template #prefix><el-icon><User /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="密码" show-password>
              <template #prefix><el-icon><Lock /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" class="login-btn" @click="handleLogin">
              登 录
            </el-button>
          </el-form-item>
        </el-form>
        <div v-if="errorMsg" class="login-error">{{ errorMsg }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/store/app'
import { login } from '@/api/common'
import { OfficeBuilding, User, Lock, Ticket, DataAnalysis } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  company: (route.query.company as string) || '',
  usercode: '',
  password: '',
})

const rules: FormRules = {
  company: [{ required: true, message: '请输入公司编码', trigger: 'blur' }],
  usercode: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  errorMsg.value = ''

  try {
    const params: Record<string, string> = {
      company: form.company,
      usercode: form.usercode,
      password: form.password,
    }

    const res = await login(params)
    const data = res.data
    appStore.loginSuccess(data.token || `django_${data.django_user_id}`, data)

    // 如果用户已有可用门店且唯一，直接进工作台
    const stores = data.stores ?? []
    if (stores.length > 1) {
      // 多门店：如果登录时指定了门店且通过验证，直接进入
      if (form.storecode) {
        router.push('/')
      } else {
        router.push('/select-store')
      }
    } else {
      router.push('/')
    }
  } catch (err: any) {
    if (err.code === 'ERR_NETWORK') {
      errorMsg.value = '无法连接服务器，请检查后端服务是否启动'
    } else if (err.response?.status === 401) {
      errorMsg.value = '公司编码、用户名或密码错误'
    } else if (err.response?.data?.msg) {
      errorMsg.value = err.response.data.msg
    } else {
      errorMsg.value = '登录失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  background: linear-gradient(135deg, var(--g-color-auth-grad-from) 0%, var(--g-color-auth-grad-to) 100%);
}
.login-shell {
  width: 100%;
  max-width: 960px;
  min-height: 520px;
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  background: var(--g-color-surface);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: var(--g-shadow-pop);
}
.login-brand {
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 16px;
  padding: 48px 40px;
  color: #fff;
  background: linear-gradient(160deg, var(--g-color-auth-grad-from) 0%, var(--g-color-auth-grad-to) 100%);
}
.brand-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.18);
  font-size: 26px;
  font-weight: 800;
}
.brand-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  line-height: 1.3;
}
.brand-desc {
  margin: 0;
  font-size: 14px;
  opacity: 0.85;
}
.brand-features {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}
.feature {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  opacity: 0.92;
}
.feature .el-icon {
  font-size: 18px;
}
.login-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 48px 44px;
  background: var(--g-color-surface);
}
.login-title {
  margin: 0 0 6px;
  font-size: 24px;
  font-weight: 700;
  color: var(--g-color-text);
}
.login-sub {
  margin: 0 0 24px;
  font-size: 13px;
  color: var(--g-color-text-muted);
}
.login-btn {
  width: 100%;
}
.login-error {
  margin-top: 12px;
  color: var(--g-color-danger);
  font-size: 13px;
  text-align: center;
}
@media (max-width: 860px) {
  .login-shell {
    grid-template-columns: 1fr;
    max-width: 440px;
  }
  .login-brand {
    display: none;
  }
}
</style>
