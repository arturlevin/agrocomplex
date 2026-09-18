<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()

const executions = ref([])
const openTasks = ref([]) // planned tasks with no execution yet
const resources = ref([])

const dialogVisible = ref(false)
const activeTask = ref(null)
const form = ref({ actual_date: '', harvest_volume_kg: null, notes: '', resources_used: [] })

const workTypeLabels = {
  sowing: 'Посев',
  watering: 'Полив',
  fertilizing: 'Удобрение',
  harvesting: 'Сбор урожая',
}

const availableTasks = computed(() => {
  const isChief = auth.isChief
  return openTasks.value.filter((t) => isChief || t.assigned_to_id === auth.user?.id)
})

async function load() {
  const [execRes, taskRes, resRes] = await Promise.all([
    http.get('/work-executions'),
    http.get('/schedules', { params: { status_filter: 'planned' } }),
    http.get('/resources'),
  ])
  executions.value = execRes.data
  openTasks.value = taskRes.data
  resources.value = resRes.data
}

function openDialog(task) {
  activeTask.value = task
  form.value = {
    actual_date: new Date().toISOString().slice(0, 10),
    harvest_volume_kg: null,
    notes: '',
    resources_used: [],
  }
  dialogVisible.value = true
}

function addResourceRow() {
  form.value.resources_used.push({ resource_id: null, quantity: null })
}

function removeResourceRow(index) {
  form.value.resources_used.splice(index, 1)
}

async function submit() {
  try {
    const payload = { ...form.value, resources_used: form.value.resources_used.filter((r) => r.resource_id) }
    await http.post(`/work-executions/tasks/${activeTask.value.id}`, payload)
    ElMessage.success('Выполнение внесено')
    dialogVisible.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Ошибка сохранения')
  }
}

async function remove(row) {
  await ElMessageBox.confirm('Удалить запись о выполнении? Задача снова станет запланированной.', 'Подтверждение', { type: 'warning' })
  await http.delete(`/work-executions/${row.id}`)
  ElMessage.success('Удалено')
  load()
}

function resourceName(id) {
  return resources.value.find((r) => r.id === id)?.name || ''
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Фактическое выполнение работ</h2>
    </div>

    <el-card style="margin-bottom: 20px">
      <template #header>Задачи, ожидающие отметки о выполнении</template>
      <el-table :data="availableTasks" stripe>
        <el-table-column prop="planned_date" label="Плановая дата" width="140" />
        <el-table-column label="Вид работы" width="150">
          <template #default="{ row }">{{ workTypeLabels[row.work_type] }}</template>
        </el-table-column>
        <el-table-column label="Теплица">
          <template #default="{ row }">{{ row.greenhouse.name }}</template>
        </el-table-column>
        <el-table-column label="" width="140">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openDialog(row)">Внести выполнение</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card>
      <template #header>История выполненных работ</template>
      <el-table :data="executions" stripe>
        <el-table-column prop="actual_date" label="Дата" width="120" />
        <el-table-column label="Теплица">
          <template #default="{ row }">{{ row.task.greenhouse.name }}</template>
        </el-table-column>
        <el-table-column label="Вид работы" width="150">
          <template #default="{ row }">{{ workTypeLabels[row.task.work_type] }}</template>
        </el-table-column>
        <el-table-column label="Исполнитель">
          <template #default="{ row }">{{ row.executor.full_name }}</template>
        </el-table-column>
        <el-table-column label="Урожай, кг" width="120">
          <template #default="{ row }">{{ row.harvest_volume_kg ?? '—' }}</template>
        </el-table-column>
        <el-table-column label="Ресурсы">
          <template #default="{ row }">
            <span v-if="!row.resource_usages.length">—</span>
            <span v-for="(u, i) in row.resource_usages" :key="u.resource_id">
              {{ u.resource.name }}: {{ u.quantity }} {{ u.resource.unit }}<span v-if="i < row.resource_usages.length - 1">, </span>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="" width="100">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="remove(row)">Удалить</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="Отметить выполнение" width="520">
      <el-form :model="form" label-position="top">
        <el-form-item label="Фактическая дата">
          <el-date-picker v-model="form.actual_date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item v-if="activeTask?.work_type === 'harvesting'" label="Объём урожая, кг">
          <el-input-number v-model="form.harvest_volume_kg" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Затраченные ресурсы">
          <div v-for="(row, i) in form.resources_used" :key="i" class="resource-row">
            <el-select v-model="row.resource_id" placeholder="Ресурс" style="width: 55%">
              <el-option v-for="r in resources" :key="r.id" :label="`${r.name} (${r.unit})`" :value="r.id" />
            </el-select>
            <el-input-number v-model="row.quantity" :min="0" style="width: 30%" />
            <el-button text type="danger" @click="removeResourceRow(i)">✕</el-button>
          </div>
          <el-button size="small" @click="addResourceRow">+ Добавить ресурс</el-button>
        </el-form-item>
        <el-form-item label="Примечание">
          <el-input v-model="form.notes" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Отмена</el-button>
        <el-button type="primary" @click="submit">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.resource-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 8px;
}
</style>
