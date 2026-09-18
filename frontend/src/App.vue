<script setup>
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const baseMenu = [
  { path: '/', label: 'Дашборд' },
  { path: '/greenhouses', label: 'Теплицы' },
  { path: '/cultures', label: 'Культуры' },
  { path: '/resources', label: 'Ресурсы' },
  { path: '/schedules', label: 'График работ' },
  { path: '/work-executions', label: 'Выполнение работ' },
]

const menu = computed(() => (auth.isChief ? [...baseMenu, { path: '/users', label: 'Сотрудники' }] : baseMenu))
const showLayout = computed(() => route.name !== 'login')

onMounted(async () => {
  if (auth.isAuthenticated && !auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      auth.logout()
      router.push({ name: 'login' })
    }
  }
})

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <router-view v-if="!showLayout" />

  <div v-else class="layout">
    <aside class="sidebar">
      <div class="sidebar__title">Агрокомплекс</div>
      <nav>
        <router-link v-for="item in menu" :key="item.path" :to="item.path" class="sidebar__link">
          {{ item.label }}
        </router-link>
      </nav>
      <div class="sidebar__user">
        <div>{{ auth.user?.full_name }}</div>
        <el-button size="small" text @click="logout">Выйти</el-button>
      </div>
    </aside>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #2f5233;
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 20px 0;
}

.sidebar__title {
  font-size: 20px;
  font-weight: 700;
  padding: 0 20px 20px;
}

.sidebar__link {
  display: block;
  padding: 10px 20px;
  color: #d9e6da;
  text-decoration: none;
}

.sidebar__link:hover,
.sidebar__link.router-link-exact-active {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.sidebar__user {
  margin-top: auto;
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  font-size: 14px;
}

.content {
  flex: 1;
  padding: 24px;
  background: #f5f7f5;
}
</style>
