<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api, { getApiErrorMessage } from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const shopStore = useShopStore()

const mode = computed<'login' | 'register'>(() =>
  route.query.mode === 'register' ? 'register' : 'login'
)

/* ✅ СНАЧАЛА объявляем */
const regRole = ref<'BUYER' | 'SUPPLIER'>(
  route.query.role === 'supplier' ? 'SUPPLIER' : 'BUYER'
)

/* ✅ потом watch */
watch(
  () => route.fullPath,
  () => {
    regRole.value = route.query.role === 'supplier' ? 'SUPPLIER' : 'BUYER'
  }
)

/* LOGIN */
const loginEmail = ref('')
const loginPassword = ref('')
const loginError = ref('')
const loginLoading = ref(false)

/* REGISTER */
const regEmail = ref('')
const regPassword = ref('')
const regAgree = ref(false)
const regError = ref('')
const regLoading = ref(false)

const openLogin = () => router.push('/auth')

const submitLogin = async () => {
  loginError.value = ''
  loginLoading.value = true

  try {
    const { data } = await api.post('/auth/login', {
      email: loginEmail.value,
      password: loginPassword.value,
    })

    authStore.setAuth(data.token, data.user)

    await Promise.all([
      shopStore.fetchCart(),
      shopStore.fetchFavoriteProducts(),
      shopStore.fetchFavoriteSuppliers(),
    ])

    router.push('/catalog')
  } catch (e) {
    loginError.value = getApiErrorMessage(e, 'Ошибка входа')
  } finally {
    loginLoading.value = false
  }
}

const submitRegister = async () => {
  if (!regAgree.value) return

  regError.value = ''
  regLoading.value = true

  try {
    await api.post('/auth/register', {
      email: regEmail.value,
      password: regPassword.value,
      role: regRole.value,
      enterprise_ids: [],
    })

    router.push('/auth')
  } catch (e) {
    regError.value = getApiErrorMessage(e, 'Ошибка регистрации')
  } finally {
    regLoading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div v-if="mode === 'login'">
        <h1 class="title">Вход</h1>

        <form class="form" @submit.prevent="submitLogin">
          <input v-model="loginEmail" type="email" required placeholder="Email" class="input" />
          <input v-model="loginPassword" type="password" required placeholder="Пароль" class="input" />

          <p v-if="loginError" class="error">{{ loginError }}</p>

          <button class="btn" type="submit" :disabled="loginLoading">
            {{ loginLoading ? '...' : 'Войти' }}
          </button>
        </form>

        <p class="switch">
          Нет аккаунта?
          <router-link to="/auth?mode=register" class="switch-link">Регистрация</router-link>
        </p>
      </div>
    </div>

    <Transition name="fade">
      <div v-if="mode === 'register'" class="modal-overlay" @click.self="openLogin">
        <div class="modal-card">
          <h1 class="title">Регистрация</h1>

          <div class="role">
            <button type="button" @click="regRole = 'BUYER'" :class="{ active: regRole === 'BUYER' }">
              Покупатель
            </button>
            <button type="button" @click="regRole = 'SUPPLIER'" :class="{ active: regRole === 'SUPPLIER' }">
              Поставщик
            </button>
          </div>

          <form class="form" @submit.prevent="submitRegister">
            <input v-model="regEmail" type="email" required placeholder="Email" class="input" />
            <input v-model="regPassword" type="password" required placeholder="Пароль" class="input" />

            <label class="check">
              <input v-model="regAgree" type="checkbox" />
              Я согласен с условиями
            </label>

            <p v-if="regError" class="error">{{ regError }}</p>

            <button class="btn" type="submit" :disabled="regLoading || !regAgree">
              {{ regLoading ? '...' : 'Создать аккаунт' }}
            </button>
          </form>

          <p class="switch">
            Уже есть аккаунт?
            <router-link to="/auth" class="switch-link">Войти</router-link>
          </p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* твои стили без изменений */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Manrope', sans-serif;
  background: transparent;
}

.auth-card {
  width: 420px;
  padding: 2rem;
  border-radius: 1.7rem;
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(76,124,42,0.16);
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54,87,21,0.14);
}

.title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #20311c;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.input {
  padding: 0.7rem;
  border-radius: 0.7rem;
  border: 1px solid rgba(76,124,42,0.2);
}

.btn {
  border-radius: 999px;
  padding: 0.7rem;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
  border: none;
  cursor: pointer;
}

.error {
  color: #991b1b;
  font-size: 0.85rem;
}

.switch {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: #5d6b52;
}

.switch-link {
  color: #4c7c2a;
  font-weight: 600;
  text-decoration: underline;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-card {
  width: 450px;
  padding: 2rem;
  border-radius: 1.7rem;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(18px);
  border: 1px solid rgba(76,124,42,0.16);
}

.role {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.role button {
  flex: 1;
  padding: 0.6rem;
  border-radius: 999px;
  border: 1px solid rgba(76,124,42,0.2);
  background: white;
  cursor: pointer;
}

.role .active {
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
}

.check {
  font-size: 0.8rem;
  color: #5d6b52;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity .2s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>