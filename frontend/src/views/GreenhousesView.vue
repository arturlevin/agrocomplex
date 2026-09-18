<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../api/http'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const items = ref([])
const cultures = ref([])
const dialogVisible = ref(false)
const editing = ref(null)
const form = ref({ name: '', culture_id: null, area_m2: null })

async function load() {
  const [gh, cu] = await Promise.all([http.get('/greenhouses'), http.get('/cultures')])
  items.value = gh.data
  cultures.value = cu.data
}

function openCreate() {
  editing.value = null
  form.value = { name: '', culture_id: null, area_m2: null }
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = row
  form.value = { name: row.name, culture_id: row.culture_id, area_m2: row.area_m2 }
  dialogVisible.value = true
}

async function save() {
  try {
    if (editing.value) {
      await http.put(`/greenhouses/${editing.value.id}`, form.value)
      ElMessage.success('Теплица обновлена')
    } else {
      await http.post('/greenhouses', form.value)
      ElMessage.success('Теплица добавлена')
    }
    dialogVisible.value = false
    load()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || 'Ошибка сохранения')
  }
}

async function remove(row) {
  await ElMessageBox.confirm(`Удалить теплицу "${row.name}"?`, 'Подтверждение', { type: 'warning' })
  await http.delete(`/greenhouses/${row.id}`)
  ElMessage.success('Удалено')
  load()
}

onMounted(load)
</script>

<template>
  <div>
    <div class="page-header">
      <h2>Теплицы</h2>
      <el-button v-if="auth.isChief" type="primary" @click="openCreate">+ Добавить теплицу</el-button>
    </div>

    <el-card>
      <el-table :data="items" stripe>
        <el-table-column prop="name" label="Название" width="200" />
        <el-table-column label="Культура" width="200">
          <template #default="{ row }">{{ row.culture.name }}</template>
        </el-table-column>
        <el-table-column label="Площадь, м²" width="140">
          <template #default="{ row }">{{ row.area_m2 ?? '—' }}</template>
        </el-table-column>
        <el-table-column v-if="auth.isChief" label="" width="140">
          <template #default="{ row }">
            <el-button size="small" @click="openEdit(row)">Изменить</el-button>
            <el-button size="small" type="danger" @click="remove(row)">Удалить</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="editing ? 'Редактировать теплицу' : 'Новая теплица'" width="420">
      <el-form :model="form" label-position="top">
        <el-form-item label="Название">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="Культура">
          <el-select v-model="form.culture_id" style="width: 100%">
            <el-option v-for="c in cultures" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Площадь, м²">
          <el-input-number v-model="form.area_m2" :min="0" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Отмена</el-button>
        <el-button type="primary" @click="save">Сохранить</el-button>
      </template>
    </el-dialog>
  </div>
</template>
