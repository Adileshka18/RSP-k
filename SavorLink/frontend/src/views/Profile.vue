<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'

type UserProfile = {
  id: number
  email: string
  phone?: string | null
  first_name?: string | null
  last_name?: string | null
  role: string
  enterprise_id: number | null
  created_at: string
  enterprise?: { id: number; short_name: string } | null
}

type EnterpriseProfile = {
  id: number
  short_name: string
  inn: string
  region: string
  city?: string | null
  phone?: string | null
  email?: string | null
}

type NoticeType = 'success' | 'error'

const authStore = useAuthStore()

const user = ref<UserProfile | null>(null)
const enterprise = ref<EnterpriseProfile | null>(null)
const loading = ref(true)
const error = ref('')

const notice = ref<{ text: string; type: NoticeType } | null>(null)
let noticeTimer: number | null = null

const isEditingAccount = ref(false)
const savingAccount = ref(false)
const accountForm = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  old_password: '',
  password: '',
  password_confirm: '',
})

const isEditingEnterprise = ref(false)
const isCreatingEnterprise = ref(false)
const isJoiningEnterprise = ref(false)
const savingEnterprise = ref(false)
const joinableEnterprises = ref<EnterpriseProfile[]>([])
const loadingEnterprises = ref(false)

const createForm = ref({
  short_name: '',
  inn: '',
  region: '',
  city: '',
  phone: '',
  email: '',
})

const editForm = ref<EnterpriseProfile>({
  id: 0,
  short_name: '',
  inn: '',
  region: '',
  city: '',
  phone: '',
  email: '',
})

const showNotice = (text: string, type: NoticeType = 'success') => {
  notice.value = { text, type }
  if (noticeTimer) {
    clearTimeout(noticeTimer)
  }
  noticeTimer = window.setTimeout(() => {
    notice.value = null
  }, 5000)
}

const createdAt = computed(() => {
  if (!user.value?.created_at) return '—'
  return new Date(user.value.created_at).toLocaleDateString('ru-RU')
})

const startEditAccount = () => {
  if (!user.value) return
  accountForm.value = {
    first_name: user.value.first_name || '',
    last_name: user.value.last_name || '',
    email: user.value.email || '',
    phone: user.value.phone || '',
    old_password: '',
    password: '',
    password_confirm: '',
  }
  isEditingAccount.value = true
}

const cancelEditAccount = () => {
  isEditingAccount.value = false
  accountForm.value.old_password = ''
  accountForm.value.password = ''
  accountForm.value.password_confirm = ''
}

const saveAccount = async () => {
  if (!user.value || savingAccount.value) return

  const wantsPasswordUpdate = !!accountForm.value.password || !!accountForm.value.old_password
  if (wantsPasswordUpdate && accountForm.value.password !== accountForm.value.password_confirm) {
    showNotice('Новый пароль и подтверждение не совпадают', 'error')
    return
  }

  savingAccount.value = true
  try {
    const payload: Record<string, string | null> = {
      first_name: accountForm.value.first_name.trim() || null,
      last_name: accountForm.value.last_name.trim() || null,
      email: accountForm.value.email.trim(),
      phone: accountForm.value.phone.trim() || null,
    }

    if (wantsPasswordUpdate) {
      payload.old_password = accountForm.value.old_password
      payload.password = accountForm.value.password
    }

    const res = await api.patch('/users/me', payload)
    user.value = res.data

    if (authStore.token) {
      authStore.setAuth(authStore.token, { ...(authStore.user ?? {}), ...res.data })
    }

    isEditingAccount.value = false
    accountForm.value.old_password = ''
    accountForm.value.password = ''
    accountForm.value.password_confirm = ''
    showNotice('Данные аккаунта успешно сохранены')
  } catch (e: any) {
    showNotice(e.response?.data?.detail || 'Ошибка при сохранении профиля', 'error')
  } finally {
    savingAccount.value = false
  }
}

const startEditEnterprise = () => {
  if (enterprise.value) {
    editForm.value = { ...enterprise.value }
    isEditingEnterprise.value = true
  }
}

const createEnterprise = async () => {
  savingEnterprise.value = true
  try {
    const res = await api.post('/enterprises', createForm.value)
    enterprise.value = res.data
    isCreatingEnterprise.value = false
    if (user.value) user.value.enterprise_id = res.data.id
    showNotice('Предприятие создано и привязано к аккаунту')
  } catch (e: any) {
    showNotice(e.response?.data?.detail || 'Ошибка при создании предприятия', 'error')
  } finally {
    savingEnterprise.value = false
  }
}

const startJoinEnterprise = async () => {
  isJoiningEnterprise.value = true
  loadingEnterprises.value = true
  try {
    const res = await api.get('/enterprises')
    joinableEnterprises.value = res.data
  } catch {
    showNotice('Ошибка при загрузке списка предприятий', 'error')
  } finally {
    loadingEnterprises.value = false
  }
}

const joinEnterprise = async (id: number) => {
  savingEnterprise.value = true
  try {
    const res = await api.post(`/enterprises/${id}/join`)
    enterprise.value = res.data
    isJoiningEnterprise.value = false
    if (user.value) user.value.enterprise_id = res.data.id
    showNotice('Предприятие успешно привязано')
  } catch (e: any) {
    showNotice(e.response?.data?.detail || 'Ошибка при присоединении к предприятию', 'error')
  } finally {
    savingEnterprise.value = false
  }
}

const saveEnterprise = async () => {
  if (!enterprise.value) return
  savingEnterprise.value = true
  try {
    const res = await api.patch(`/enterprises/${enterprise.value.id}`, editForm.value)
    enterprise.value = res.data
    isEditingEnterprise.value = false
    showNotice('Данные предприятия обновлены')
  } catch (e: any) {
    showNotice(e.response?.data?.detail || 'Ошибка при сохранении предприятия', 'error')
  } finally {
    savingEnterprise.value = false
  }
}

const loadProfile = async () => {
  loading.value = true
  error.value = ''

  try {
    const userRes = await api.get('/users/me')
    const userData: UserProfile = userRes.data
    user.value = userData

    if (userData.enterprise_id) {
      const entRes = await api.get(`/enterprises/${userData.enterprise_id}`)
      enterprise.value = entRes.data
    } else {
      enterprise.value = null
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || 'Ошибка загрузки профиля'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<template>
  <div class="profile-page">
    <main class="profile-main">
      <Transition name="profile-toast">
        <div v-if="notice" class="notice" :class="notice.type === 'success' ? 'notice--success' : 'notice--error'">
          {{ notice.text }}
        </div>
      </Transition>

      <section class="profile-card">
        <div class="profile-card-head">
          <h1 class="profile-title">Профиль</h1>
          <button type="button" class="refresh-btn" @click="loadProfile">Обновить</button>
        </div>

        <p v-if="loading" class="state-text">Загрузка данных...</p>
        <p v-else-if="error" class="state-text state-text--error">{{ error }}</p>

        <div v-else-if="user" class="profile-grid">
          <article class="info-card">
            <div class="card-header">
              <h2 class="info-title">Аккаунт</h2>
              <button v-if="!isEditingAccount" type="button" class="edit-btn" @click="startEditAccount">
                Изменить
              </button>
            </div>

            <form v-if="isEditingAccount" class="edit-form" @submit.prevent="saveAccount">
              <div class="form-group">
                <label>Имя</label>
                <input v-model="accountForm.first_name" type="text" placeholder="Иван" />
              </div>
              <div class="form-group">
                <label>Фамилия</label>
                <input v-model="accountForm.last_name" type="text" placeholder="Иванов" />
              </div>
              <div class="form-group">
                <label>Email</label>
                <input v-model="accountForm.email" type="email" required />
              </div>
              <div class="form-group">
                <label>Телефон</label>
                <input v-model="accountForm.phone" type="text" placeholder="+7 (999) 123-45-67" />
              </div>
              <div class="form-group">
                <label>Текущий пароль (если меняете пароль)</label>
                <input v-model="accountForm.old_password" type="password" autocomplete="current-password" />
              </div>
              <div class="form-group">
                <label>Новый пароль</label>
                <input v-model="accountForm.password" type="password" autocomplete="new-password" />
              </div>
              <div class="form-group">
                <label>Подтверждение нового пароля</label>
                <input v-model="accountForm.password_confirm" type="password" autocomplete="new-password" />
              </div>

              <div class="edit-actions">
                <button type="button" class="cancel-btn" @click="cancelEditAccount">Отмена</button>
                <button type="submit" class="save-btn" :disabled="savingAccount">
                  {{ savingAccount ? 'Сохранение...' : 'Сохранить' }}
                </button>
              </div>
            </form>

            <dl v-else class="info-list">
              <div class="info-row"><dt>ID</dt><dd>{{ user.id }}</dd></div>
              <div class="info-row"><dt>Имя</dt><dd>{{ user.first_name || '—' }}</dd></div>
              <div class="info-row"><dt>Фамилия</dt><dd>{{ user.last_name || '—' }}</dd></div>
              <div class="info-row"><dt>Email</dt><dd>{{ user.email }}</dd></div>
              <div class="info-row"><dt>Телефон</dt><dd>{{ user.phone || '—' }}</dd></div>
              <div class="info-row"><dt>Роль</dt><dd>{{ user.role }}</dd></div>
              <div class="info-row"><dt>Дата регистрации</dt><dd>{{ createdAt }}</dd></div>
            </dl>
          </article>

          <article class="info-card">
            <div class="card-header">
              <h2 class="info-title">Предприятие</h2>
              <button
                v-if="user.role === 'SUPPLIER' && enterprise && !isEditingEnterprise"
                type="button"
                class="edit-btn"
                @click="startEditEnterprise"
              >
                Изменить
              </button>
            </div>

            <div v-if="enterprise">
              <form v-if="isEditingEnterprise" @submit.prevent="saveEnterprise" class="edit-form">
                <div class="form-group">
                  <label>Название</label>
                  <input v-model="editForm.short_name" type="text" required />
                </div>
                <div class="form-group">
                  <label>ИНН</label>
                  <input v-model="editForm.inn" type="text" required />
                </div>
                <div class="form-group">
                  <label>Регион</label>
                  <input v-model="editForm.region" type="text" required />
                </div>
                <div class="form-group">
                  <label>Город</label>
                  <input v-model="editForm.city" type="text" placeholder="Если нужно, укажите город" />
                </div>
                <div class="form-group">
                  <label>Телефон</label>
                  <input v-model="editForm.phone" type="text" />
                </div>
                <div class="form-group">
                  <label>Email</label>
                  <input v-model="editForm.email" type="email" />
                </div>
                <div class="edit-actions">
                  <button type="button" @click="isEditingEnterprise = false" class="cancel-btn">Отмена</button>
                  <button type="submit" class="save-btn" :disabled="savingEnterprise">
                    {{ savingEnterprise ? 'Сохранение...' : 'Сохранить' }}
                  </button>
                </div>
              </form>

              <dl v-else class="info-list">
                <div class="info-row"><dt>Название</dt><dd>{{ enterprise.short_name }}</dd></div>
                <div class="info-row"><dt>ИНН</dt><dd>{{ enterprise.inn }}</dd></div>
                <div class="info-row"><dt>Регион</dt><dd>{{ enterprise.region }}</dd></div>
                <div class="info-row"><dt>Город</dt><dd>{{ enterprise.city || '—' }}</dd></div>
                <div class="info-row"><dt>Телефон</dt><dd>{{ enterprise.phone || '—' }}</dd></div>
                <div class="info-row"><dt>Email</dt><dd>{{ enterprise.email || '—' }}</dd></div>
              </dl>
            </div>

            <div v-else>
              <div v-if="isCreatingEnterprise">
                <form @submit.prevent="createEnterprise" class="edit-form">
                  <div class="form-group">
                    <label>Название</label>
                    <input v-model="createForm.short_name" required />
                  </div>
                  <div class="form-group">
                    <label>ИНН</label>
                    <input v-model="createForm.inn" required />
                  </div>
                  <div class="form-group">
                    <label>Регион</label>
                    <input v-model="createForm.region" required />
                  </div>
                  <div class="form-group">
                    <label>Город</label>
                    <input v-model="createForm.city" placeholder="Необязательно" />
                  </div>
                  <div class="form-group">
                    <label>Телефон</label>
                    <input v-model="createForm.phone" />
                  </div>
                  <div class="form-group">
                    <label>Email</label>
                    <input v-model="createForm.email" type="email" />
                  </div>
                  <div class="edit-actions">
                    <button type="button" @click="isCreatingEnterprise = false" class="cancel-btn">Отмена</button>
                    <button type="submit" class="save-btn" :disabled="savingEnterprise">
                      {{ savingEnterprise ? 'Создание...' : 'Создать предприятие' }}
                    </button>
                  </div>
                </form>
              </div>

              <div v-else-if="isJoiningEnterprise">
                <div class="join-list">
                  <p v-if="loadingEnterprises">Загрузка списка...</p>
                  <div v-else class="enterprise-items">
                    <div v-for="ent in joinableEnterprises" :key="ent.id" class="enterprise-item">
                      <div class="ent-info">
                        <strong>{{ ent.short_name }}</strong>
                        <span>ИНН: {{ ent.inn }}</span>
                      </div>
                      <button @click="joinEnterprise(ent.id)" class="join-btn-small">Выбрать</button>
                    </div>
                  </div>
                  <button @click="isJoiningEnterprise = false" class="cancel-btn mt-2">Назад</button>
                </div>
              </div>

              <div v-else class="no-enterprise-actions">
                <p class="state-text">Вы пока не привязаны к предприятию</p>
                <div class="action-buttons">
                  <button @click="isCreatingEnterprise = true" class="primary-btn">Создать</button>
                  <button @click="startJoinEnterprise" class="secondary-btn">Присоединиться</button>
                </div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.profile-page {
  min-height: 100vh;
  font-family: 'Manrope', sans-serif;
  background: transparent;
}

.profile-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.notice {
  position: fixed;
  top: 84px;
  right: 1.5rem;
  z-index: 1000;
  max-width: min(420px, calc(100vw - 3rem));
  border-radius: 1rem;
  padding: 0.85rem 1rem;
  font-weight: 700;
  backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.35);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.14);
}

.notice--success {
  background: rgba(220, 252, 231, 0.92);
  color: #166534;
}

.notice--error {
  background: rgba(254, 226, 226, 0.92);
  color: #991b1b;
}

.profile-toast-enter-active,
.profile-toast-leave-active {
  transition: all 0.24s ease;
}

.profile-toast-enter-from,
.profile-toast-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.profile-card {
  border-radius: 1.7rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(76, 124, 42, 0.16);
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.14);
}

.profile-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.profile-title {
  font-size: 1.6rem;
  color: #20311c;
  margin: 0;
}

.refresh-btn,
.primary-btn,
.save-btn,
.join-btn-small {
  border-radius: 999px;
  padding: 0.62rem 1.18rem;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  border: none;
  cursor: pointer;
  font-weight: 700;
}

.secondary-btn,
.edit-btn,
.cancel-btn {
  border-radius: 999px;
  padding: 0.58rem 1.08rem;
  background: #fff;
  border: 1px solid rgba(76, 124, 42, 0.2);
  color: #30422a;
  cursor: pointer;
  font-weight: 700;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.info-card {
  border-radius: 1.2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid rgba(76, 124, 42, 0.12);
  backdrop-filter: blur(12px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.7rem;
}

.info-title {
  margin: 0;
  color: #20311c;
}

.info-list {
  margin: 0;
}

.info-row {
  display: flex;
  justify-content: space-between;
  gap: 0.8rem;
  padding: 0.55rem 0;
  border-bottom: 1px solid rgba(76, 124, 42, 0.1);
}

.info-row dt {
  color: #5d6b52;
}

.info-row dd {
  margin: 0;
  text-align: right;
  font-weight: 700;
  color: #24361f;
  word-break: break-word;
}

.edit-form {
  display: grid;
  gap: 0.75rem;
}

.form-group {
  display: grid;
  gap: 0.3rem;
}

.form-group label {
  font-size: 0.84rem;
  color: #4f5f48;
}

.form-group input {
  padding: 0.62rem 0.72rem;
  border-radius: 0.7rem;
  border: 1px solid rgba(76, 124, 42, 0.2);
  background: rgba(255, 255, 255, 0.95);
}

.form-group input:focus {
  outline: none;
  border-color: #4c7c2a;
  box-shadow: 0 0 0 3px rgba(76, 124, 42, 0.12);
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.6rem;
  margin-top: 0.3rem;
}

.state-text {
  color: #5d6b52;
}

.state-text--error {
  color: #991b1b;
}

.action-buttons {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.join-list {
  display: grid;
  gap: 0.7rem;
}

.enterprise-items {
  display: grid;
  gap: 0.65rem;
  max-height: 260px;
  overflow: auto;
  padding-right: 0.3rem;
}

.enterprise-item {
  display: flex;
  justify-content: space-between;
  gap: 0.7rem;
  align-items: center;
  border: 1px solid rgba(76, 124, 42, 0.16);
  background: rgba(255, 255, 255, 0.92);
  border-radius: 0.8rem;
  padding: 0.6rem 0.72rem;
}

.ent-info {
  display: grid;
  gap: 0.16rem;
}

.ent-info span {
  font-size: 0.83rem;
  color: #5d6b52;
}

.mt-2 {
  margin-top: 0.35rem;
}

@media (max-width: 900px) {
  .profile-main {
    padding: 1.3rem 0.85rem;
  }

  .profile-card {
    padding: 1.25rem;
  }

  .profile-card-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .info-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .info-row dd {
    text-align: left;
  }

  .edit-actions {
    justify-content: stretch;
    flex-direction: column-reverse;
  }

  .edit-actions button {
    width: 100%;
  }
}
</style>
