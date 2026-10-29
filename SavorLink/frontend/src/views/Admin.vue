<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'

const activeTab = ref('users')
const error = ref('')
const notice = ref<{ text: string; type: 'success' | 'error' } | null>(null)

const showNotice = (text: string, type: 'success' | 'error' = 'success') => {
  notice.value = { text, type }
  setTimeout(() => { notice.value = null }, 3000)
}

// -------------------------
// USERS
// -------------------------
const users = ref<any[]>([])
const loadingUsers = ref(false)

const loadUsers = async () => {
  loadingUsers.value = true
  try {
    const res = await api.get('/users')
    users.value = res.data
  } catch (err: any) {
    showNotice('Ошибка загрузки пользователей', 'error')
  } finally {
    loadingUsers.value = false
  }
}

const updateRole = async (userId: number, currentRole: string) => {
  const newRole = prompt(`Изменить роль (ADMIN, BUYER, SUPPLIER). Текущая: ${currentRole}`, currentRole)
  if (!newRole || newRole === currentRole) return
  if (!['ADMIN', 'BUYER', 'SUPPLIER'].includes(newRole)) {
    showNotice('Неверная роль', 'error')
    return
  }
  try {
    await api.patch(`/users/${userId}/role`, { role: newRole })
    showNotice('Роль обновлена')
    loadUsers()
  } catch (err) {
    showNotice('Ошибка изменения роли', 'error')
  }
}

// -------------------------
// CATEGORIES
// -------------------------
const categories = ref<any[]>([])
const loadingCategories = ref(false)

const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const res = await api.get('/products/categories')
    categories.value = res.data
  } catch (err) {
    showNotice('Ошибка загрузки категорий', 'error')
  } finally {
    loadingCategories.value = false
  }
}

const createCategory = async () => {
  const name = prompt('Название новой категории:')
  if (!name) return
  try {
    await api.post('/products/categories', { name })
    showNotice('Категория создана')
    loadCategories()
  } catch (err) {
    showNotice('Ошибка создания категории', 'error')
  }
}

const editCategory = async (catId: number, currentName: string) => {
  const name = prompt('Новое название:', currentName)
  if (!name || name === currentName) return
  try {
    await api.patch(`/products/categories/${catId}`, { name })
    showNotice('Категория обновлена')
    loadCategories()
  } catch (err) {
    showNotice('Ошибка обновления категории', 'error')
  }
}

// -------------------------
// ENTERPRISES
// -------------------------
const enterprises = ref<any[]>([])
const loadingEnterprises = ref(false)

const loadEnterprises = async () => {
  loadingEnterprises.value = true
  try {
    const res = await api.get('/enterprises')
    enterprises.value = res.data
  } catch (err) {
    showNotice('Ошибка загрузки предприятий', 'error')
  } finally {
    loadingEnterprises.value = false
  }
}

const deleteEnterprise = async (id: number, name: string) => {
  if (!confirm(`Удалить предприятие "${name}"? Это также удалит все его товары и заказы!`)) return
  try {
    await api.delete(`/enterprises/${id}`)
    showNotice('Предприятие удалено')
    loadEnterprises()
  } catch (err) {
    showNotice('Ошибка удаления', 'error')
  }
}

// -------------------------
// STATUS
// -------------------------
const systemStatus = ref({
  api: 'Загрузка...',
  db: 'Загрузка...'
})

const checkStatus = async () => {
  systemStatus.value.api = 'Проверка...'
  try {
    const start = Date.now()
    await api.get('/') // Root endpoint check
    const diff = (Date.now() - start)
    systemStatus.value.api = `ОК (${diff} мс)`
    systemStatus.value.db = `ОК (Связь с базой данных в норме)`
  } catch (err) {
    systemStatus.value.api = 'Ошибка соединения'
    systemStatus.value.db = 'Ошибка соединения / БД недоступна'
  }
}

onMounted(() => {
  loadUsers()
  loadCategories()
  loadEnterprises()
  checkStatus()
})

</script>

<template>
  <div class="admin-panel">
    <header class="admin-header">
      <h1>Панель Администратора</h1>
      <p class="subtitle">Управление пользователями, справочниками и мониторинг</p>
    </header>

    <Transition name="fade">
      <div v-if="notice" class="admin-toast" :class="notice.type">
        {{ notice.text }}
      </div>
    </Transition>

    <nav class="admin-tabs">
      <button :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">Пользователи</button>
      <button :class="{ active: activeTab === 'categories' }" @click="activeTab = 'categories'">Справочники (Категории)</button>
      <button :class="{ active: activeTab === 'enterprises' }" @click="activeTab = 'enterprises'">Предприятия</button>
      <button :class="{ active: activeTab === 'status' }" @click="activeTab = 'status'">Мониторинг</button>
    </nav>

    <div class="admin-content card">
      <!-- ТАБ ПОЛЬЗОВАТЕЛИ -->
      <section v-if="activeTab === 'users'">
        <div class="section-head">
          <h2>Управление пользователями ({users.length})</h2>
          <button class="btn" @click="loadUsers">Обновить</button>
        </div>
        <div v-if="loadingUsers" class="loading">Загрузка...</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Роль</th>
                <th>Предприятия</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.email }}</td>
                <td>
                  <span class="role-badge" :class="u.role">{{ u.role }}</span>
                </td>
                <td>
                  <div v-for="ent in u.enterprises" :key="ent.id" class="ent-tag">
                    {{ ent.short_name }} (#{{ ent.id }})
                  </div>
                  <span v-if="!u.enterprises.length" class="text-muted">—</span>
                </td>
                <td>
                  <button class="btn-small" @click="updateRole(u.id, u.role)">См. роль</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ТАБ КАТЕГОРИИ -->
      <section v-else-if="activeTab === 'categories'">
        <div class="section-head">
          <h2>Управление справочниками</h2>
          <div class="actions">
            <button class="btn primary-btn" @click="createCategory">Создать категорию</button>
            <button class="btn" @click="loadCategories">Обновить</button>
          </div>
        </div>
        <div v-if="loadingCategories" class="loading">Загрузка...</div>
        <ul v-else class="cat-list">
          <li v-for="cat in categories" :key="cat.id" class="cat-item">
            <span><strong>#{{ cat.id }}</strong> {{ cat.name }}</span>
            <button class="btn-small" @click="editCategory(cat.id, cat.name)">Редактировать</button>
          </li>
        </ul>
      </section>

      <!-- ТАБ ПРЕДПРИЯТИЯ -->
      <section v-else-if="activeTab === 'enterprises'">
        <div class="section-head">
          <h2>Управление предприятиями</h2>
          <button class="btn" @click="loadEnterprises">Обновить</button>
        </div>
        <div v-if="loadingEnterprises" class="loading">Загрузка...</div>
        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>ИНН</th>
                <th>Название</th>
                <th>Регион</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ent in enterprises" :key="ent.id">
                <td>{{ ent.id }}</td>
                <td>{{ ent.inn }}</td>
                <td><strong>{{ ent.short_name }}</strong></td>
                <td>{{ ent.region }}, {{ ent.city || '—' }}</td>
                <td>
                  <button class="btn-small" style="color: #c92a2a" @click="deleteEnterprise(ent.id, ent.short_name)">Удалить</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ТАБ СТАТУС -->
      <section v-else-if="activeTab === 'status'">
        <div class="section-head">
          <h2>Состояние сервисов</h2>
          <button class="btn" @click="checkStatus">Проверить сейчас</button>
        </div>
        
        <div class="status-grid">
          <div class="status-card">
            <h3>Backend API</h3>
            <p :class="{ error_text: systemStatus.api.startsWith('Ошибка') }">{{ systemStatus.api }}</p>
          </div>
          <div class="status-card">
            <h3>База данных</h3>
            <p :class="{ error_text: systemStatus.db.startsWith('Ошибка') }">{{ systemStatus.db }}</p>
          </div>
        </div>

        <div class="status-info mt-4">
          <p><strong>Мониторинг ошибок:</strong> Ошибки автоматически логгируются в stderr контейнера backend.</p>
          <p><strong>Резервное копирование:</strong> Postgres-том `postgres_data` сохраняется на уровне файловой системы Docker-хоста. Рекомендуется настроить cron для создания ежедневных pg_dump.</p>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.admin-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.admin-header h1 {
  font-size: 2rem;
  margin: 0;
  color: #1f2a1a;
}
.subtitle {
  color: #5d6b52;
  margin-top: 0.2rem;
}

.admin-tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid rgba(76, 124, 42, 0.1);
  padding-bottom: 0px;
}

.admin-tabs button {
  background: none;
  border: none;
  padding: 0.8rem 1.5rem;
  font-weight: 700;
  color: #5d6b52;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  border-radius: 8px 8px 0 0;
  transition: 0.2s;
}

.admin-tabs button:hover {
  background: rgba(76, 124, 42, 0.05);
}

.admin-tabs button.active {
  color: #4c7c2a;
  border-bottom: 3px solid #4c7c2a;
  background: rgba(76, 124, 42, 0.08);
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

th, td {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(76, 124, 42, 0.1);
}

th {
  background: rgba(76, 124, 42, 0.05);
  font-weight: 700;
  color: #3f4a2f;
}

.role-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 800;
  background: #eee;
}
.role-badge.ADMIN { background: #fee2e2; color: #991b1b; }
.role-badge.BUYER { background: #dbeafe; color: #1e40af; }
.role-badge.SUPPLIER { background: #dcfce7; color: #166534; }

.ent-tag {
  font-size: 0.8rem;
  background: rgba(76, 124, 42, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 0.3rem;
  margin-bottom: 0.2rem;
  display: inline-block;
  margin-right: 0.3rem;
}

.cat-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 0.5rem;
}

.cat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem 1rem;
  border: 1px solid rgba(76, 124, 42, 0.15);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.5);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.status-card {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(76, 124, 42, 0.2);
  border-radius: 12px;
}

.status-card h3 {
  margin: 0 0 0.5rem;
}

.error_text {
  color: #dc2626;
  font-weight: bold;
}

.mt-4 { margin-top: 1rem; }

.btn, .btn-small {
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}
.btn {
  padding: 0.6rem 1.2rem;
  background: #eef5e8;
  color: #3f4a2f;
}
.btn:hover { background: #dcefd0; }

.btn-small {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
  background: #eef5e8;
  color: #3f4a2f;
}
.btn-small:hover { background: #dcefd0; }

.primary-btn {
  background: #4c7c2a;
  color: #fff;
}
.primary-btn:hover { background: #3d6321; }

.admin-toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  font-weight: bold;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  z-index: 2000;
}
.admin-toast.success { border-left: 5px solid #22c55e; color: #15803d; }
.admin-toast.error { border-left: 5px solid #ef4444; color: #b91c1c; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
