<script setup>
import { ref, onMounted } from 'vue'
import http from '../api/http'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const stats = ref({ greenhouses: 0, cultures: 0, plannedTasks: 0, myTasks: 0 })
const upcoming = ref([])
const workTypeLabels = {
  sowing: 'Посев',
  watering: 'Полив',
  fertilizing: 'Удобрение',
  harvesting: 'Сбор урожая',
}

async function load() {
  const [greenhouses, cultures, tasks, myTasks] = await Promise.all([
    http.get('/greenhouses'),
    http.get('/cultures'),
    http.get('/schedules', { params: { status_filter: 'planned' } }),
    http.get('/schedules', { params: { my_tasks: true, status_filter: 'planned' } }),
  ])
  stats.value = {
    greenhouses: greenhouses.data.length,
    cultures: cultures.data.length,
    plannedTasks: tasks.data.length,
    myTasks: myTasks.data.length,
  }
  upcoming.value = tasks.data.slice(0, 8)
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Добро пожаловать, {{ auth.user?.full_name }}</h2>
    </div>

    <el-row :gutter="16">
      <el-col :span="6">
        <el-card><div class="stat"><div class="stat__value">{{ stats.greenhouses }}</div><div class="stat__label">Теплиц</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><div class="stat"><div class="stat__value">{{ stats.cultures }}</div><div class="stat__label">Культур</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><div class="stat"><div class="stat__value">{{ stats.plannedTasks }}</div><div class="stat__label">Запланировано работ</div></div></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><div class="stat"><div class="stat__value">{{ stats.myTasks }}</div><div class="stat__label">Моих задач</div></div></el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 20px">
      <template #header>Ближайшие запланированные работы</template>
      <el-table :data="upcoming" stripe>
        <el-table-column prop="planned_date" label="Дата" width="120" />
        <el-table-column label="Вид работы" width="150">
          <template #default="{ row }">{{ workTypeLabels[row.work_type] }}</template>
        </el-table-column>
        <el-table-column label="Теплица">
          <template #default="{ row }">{{ row.greenhouse.name }} ({{ row.greenhouse.culture.name }})</template>
        </el-table-column>
        <el-table-column label="Исполнитель">
          <template #default="{ row }">{{ row.assignee?.full_name || '—' }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.stat {
  text-align: center;
}
.stat__value {
  font-size: 32px;
  font-weight: 700;
  color: #2f5233;
}
.stat__label {
  color: #888;
  font-size: 13px;
  margin-top: 4px;
}
</style>
