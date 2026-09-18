<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)

async function submit() {
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Неверный email или пароль')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-screen">
    <el-card class="login-card">
      <h2>Агрокомплекс</h2>
      <p class="hint">Вход для агрономов теплицы</p>
      <el-form label-position="top" @submit.prevent="submit">
        <el-form-item label="Email">
          <el-input v-model="email" placeholder="chief@agrocomplex.ru" />
        </el-form-item>
        <el-form-item label="Пароль">
          <el-input v-model="password" type="password" show-password @keyup.enter="submit" />
        </el-form-item>
        <el-button type="primary" :loading="loading" style="width: 100%" @click="submit">Войти</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped>
.login-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7f5;
}

.login-card {
  width: 360px;
}

.hint {
  color: #888;
  margin-top: -8px;
  margin-bottom: 16px;
  font-size: 13px;
}
</style>
