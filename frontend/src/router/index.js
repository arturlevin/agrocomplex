import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth'

const routes = [
  { path: '/login', name: 'login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
  { path: '/', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
  { path: '/greenhouses', name: 'greenhouses', component: () => import('../views/GreenhousesView.vue') },
  { path: '/cultures', name: 'cultures', component: () => import('../views/CulturesView.vue') },
  { path: '/resources', name: 'resources', component: () => import('../views/ResourcesView.vue') },
  { path: '/schedules', name: 'schedules', component: () => import('../views/SchedulesView.vue') },
  { path: '/work-executions', name: 'work-executions', component: () => import('../views/WorkExecutionsView.vue') },
  { path: '/users', name: 'users', component: () => import('../views/UsersView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
