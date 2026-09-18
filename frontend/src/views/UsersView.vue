<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const items = ref([])
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({ full_name: '', email: '', role: 'agronomist', password: '' })

const roleLabels = { chief_agronomist: 'Главный агроном', agronomist: 'Агроном' }

async function load() {
  const { data } = await http.get('/users')
  items.value = data
}

function openCreate() {
  editing.value = null
  form.value = { full_name: '', email: '', role: 'agronomist', password: '' }
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = row
  form.value = { full_name: row.full_name, email: row.email, role: row.role, password: '' }
  dialogVisible.value = true
}

async function save() {
  try {
    if (editing.value) {
      const payload = { ...form.value }
      if (!payload.password) delete payload.password
      await http.put(`/users/${editing.value.id}`, payload)
      ElMessage.success('Сотрудник обновлён')
    } else {
      await http.post('/users', form.value)
      ElMessage.success('Сотрудник добавлен')
    }
    dialogVisible.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Ошибка сохранения')
  }
}

async function toggleActive(row) {
  await http.put(`/users/${row.id}`, { is_active: !row.is_active })
  load()
}

async function remove(row) {
  await ElMessageBox.confirm(`Удалить сотрудника "${row.full_name}"?`, 'Подтверждение', { type: 'warning' })
  await http.delete(`/users/${row.id}`)
  ElMessage.success('Удалено')
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Сотрудники</h2>
      <el-button v-if="auth.isChief" type="primary" @click="openCreate">+ Добавить сотрудника</el-button>
    </div>

    <el-card>
      <el-table :data="items" stripe>
        <el-table-column prop="full_name" label="ФИО" width="220" />
        <el-table-column prop="email" label="Email" width="220" />
        <el-table-column label="Роль" width="180">
          <template #default="{ row }">{{ roleLabels[row.role] }}</template>
        </el-table-column>
        <el-table-column label="Статус" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? 'Активен' : 'Отключён' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="auth.isChief" label="">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">Изменить</el-button>
            <el-button size="small" @click="toggleActive(row)">{{ row.is_active ? 'Отключить' : 'Включить' }}</el-button>
            <el-button size="small" type="danger" @click="remove(row)">Удалить</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? 'Редактировать сотрудника' : 'Новый сотрудник'" width="420">
      <el-form :model="form" label-position="top">
        <el-form-item label="ФИО">
          <el-input v-model="form.full_name" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="Роль">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="Главный агроном" value="chief_agronomist" />
            <el-option label="Агроном" value="agronomist" />
          </el-select>
        </el-form-item>
        <el-form-item :label="editing ? 'Новый пароль (оставьте пустым, если без изменений)' : 'Пароль'">
          <el-input v-model="form.password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Отмена</el-button>
        <el-button type="primary" @click="save">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>
