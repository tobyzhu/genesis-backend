<template>
  <div class="login-page">
    <div class="login-card">
      <h2 class="login-title">Genesis 美业管理系统</h2>

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

        <el-form-item prop="storecode">
          <el-input v-model="form.storecode" placeholder="门店编码（可选，不填自动选择）">
            <template #prefix><el-icon><Shop /></el-icon></template>
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
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/store/app'
import { login } from '@/api/common'
import { OfficeBuilding, Shop, User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const errorMsg = ref('')

const form = reactive({
  company: (route.query.company as string) || '',
  storecode: (route.query.storecode as string) || '',
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
    if (form.storecode) {
      params.storecode = form.storecode
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.login-card {
  width: 400px;
  padding: 40px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}
.login-title {
  text-align: center;
  margin-bottom: 28px;
  font-weight: 600;
  color: #303133;
}
.login-btn {
  width: 100%;
}
.login-error {
  margin-top: 12px;
  color: #f56c6c;
  font-size: 13px;
  text-align: center;
}
</style>
