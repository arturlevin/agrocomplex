<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const items = ref([])
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({ name: '', description: '' })

async function load() {
  const { data } = await http.get('/cultures')
  items.value = data
}

function openCreate() {
  editing.value = null
  form.value = { name: '', description: '' }
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = row
  form.value = { name: row.name, description: row.description }
  dialogVisible.value = true
}

async function save() {
  try {
    if (editing.value) {
      await http.put(`/cultures/${editing.value.id}`, form.value)
      ElMessage.success('Культура обновлена')
    } else {
      await http.post('/cultures', form.value)
      ElMessage.success('Культура добавлена')
    }
    dialogVisible.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Ошибка сохранения')
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`Удалить культуру "${row.name}"?`, 'Подтверждение', { type: 'warning' })
  await http.delete(`/cultures/${row.id}`)
  ElMessage.success('Удалено')
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Овощные культуры</h2>
      <el-button v-if="auth.isChief" type="primary" @click="openCreate">+ Добавить культуру</el-button>
    </div>

    <el-card>
      <el-table :data="items" stripe>
        <el-table-column prop="name" label="Название" width="220" />
        <el-table-column prop="description" label="Описание" />
        <el-table-column v-if="auth.isChief" label="" width="140">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">Изменить</el-button>
            <el-button size="small" type="danger" @click="remove(row)">Удалить</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? 'Редактировать культуру' : 'Новая культура'" width="420">
      <el-form :model="form" label-position="top">
        <el-form-item label="Название">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Описание">
          <el-input v-model="form.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Отмена</el-button>
        <el-button type="primary" @click="save">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>
