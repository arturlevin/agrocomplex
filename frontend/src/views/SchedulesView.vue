<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()

const items = ref([])
const greenhouses = ref([])
const users = ref([])
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({ greenhouse_id: null, work_type: 'watering', planned_date: '', assigned_to_id: null, notes: '' })

const workTypeLabels = {
  sowing: 'Посев',
  watering: 'Полив',
  fertilizing: 'Удобрение',
  harvesting: 'Сбор урожая',
}
const statusLabels = { planned: 'Запланировано', done: 'Выполнено', cancelled: 'Отменено' }
const statusTagType = { planned: 'info', done: 'success', cancelled: 'danger' }

async function load() {
  const [tasks, gh, us] = await Promise.all([
    http.get('/schedules'),
    http.get('/greenhouses'),
    http.get('/users'),
  ])
  items.value = tasks.data
  greenhouses.value = gh.data
  users.value = us.data
}

function openCreate() {
  editing.value = null
  form.value = { greenhouse_id: null, work_type: 'watering', planned_date: '', assigned_to_id: null, notes: '' }
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = row
  form.value = {
    greenhouse_id: row.greenhouse_id,
    work_type: row.work_type,
    planned_date: row.planned_date,
    assigned_to_id: row.assigned_to_id,
    notes: row.notes,
  }
  dialogVisible.value = true
}

async function save() {
  try {
    if (editing.value) {
      await http.put(`/schedules/${editing.value.id}`, form.value)
      ElMessage.success('Задача обновлена')
    } else {
      await http.post('/schedules', form.value)
      ElMessage.success('Задача добавлена в график')
    }
    dialogVisible.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Ошибка сохранения')
  }
}

async function remove(row) {
  await ElMessageBox.confirm('Удалить задачу из графика?', 'Подтверждение', { type: 'warning' })
  await http.delete(`/schedules/${row.id}`)
  ElMessage.success('Удалено')
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>График работ</h2>
      <el-button v-if="auth.isChief" type="primary" @click="openCreate">+ Добавить задачу</el-button>
    </div>

    <el-card>
      <el-table :data="items" stripe>
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
        <el-table-column label="Статус" width="140">
          <template #default="{ row }">
            <el-tag :type="statusTagType[row.status]">{{ statusLabels[row.status] }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="auth.isChief" label="" width="140">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">Изменить</el-button>
            <el-button size="small" type="danger" @click="remove(row)">Удалить</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? 'Редактировать задачу' : 'Новая задача графика'" width="480">
      <el-form :model="form" label-position="top">
        <el-form-item label="Теплица">
          <el-select v-model="form.greenhouse_id" style="width: 100%">
            <el-option v-for="g in greenhouses" :key="g.id" :label="g.name" :value="g.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Вид работы">
          <el-select v-model="form.work_type" style="width: 100%">
            <el-option v-for="(label, key) in workTypeLabels" :key="key" :label="label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="Плановая дата">
          <el-date-picker v-model="form.planned_date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Исполнитель">
          <el-select v-model="form.assigned_to_id" clearable style="width: 100%">
            <el-option v-for="u in users" :key="u.id" :label="u.full_name" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Примечание">
          <el-input v-model="form.notes" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Отмена</el-button>
        <el-button type="primary" @click="save">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>
