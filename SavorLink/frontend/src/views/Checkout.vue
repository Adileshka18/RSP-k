<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

const isLoading = ref(false)
const isSubmitting = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const cartItems = computed(() => store.state.cartItems)

const cartTotal = computed(() =>
  cartItems.value.reduce((sum, item) => sum + Number(item.product.price) * item.quantity, 0),
)

const groupedSuppliers = computed(() => {
  const map = new Map<number, { id: number; name: string; amount: number }>()

  for (const item of cartItems.value) {
    const supplier = item.product.enterprise
    if (!supplier) continue

    const current = map.get(supplier.id) ?? { id: supplier.id, name: supplier.short_name, amount: 0 }
    current.amount += Number(item.product.price) * item.quantity
    map.set(supplier.id, current)
  }

  return Array.from(map.values())
})

const orderType = ref('Обычный заказ')
const deliveryNote = ref('Доставить в рабочие часы')

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  isLoading.value = true
  try {
    await Promise.all([store.fetchCart(), store.fetchProducts()])
  } finally {
    isLoading.value = false
  }
})

const submitCheckout = async () => {
  if (isSubmitting.value) return
  isSubmitting.value = true
  errorMessage.value = ''

  try {
    const result = await store.checkoutCart()
    if (result.orders.length === 0) {
      errorMessage.value = 'В корзине нет товаров для оформления.'
      return
    }

    successMessage.value = `Заказ оформлен. Создано заказов: ${result.orders.length}.`
    setTimeout(() => router.push('/my-orders'), 1600)
  } catch (error: any) {
    errorMessage.value = error?.message || 'Не удалось оформить заказ.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="checkout-page">
    <section class="hero-card">
      <div>
        <p class="eyebrow">Проверка заказа</p>
        <h1 class="page-title">Оформление заказа</h1>
        <p class="page-text">Проверьте состав, поставщиков и сумму перед отправкой заказа.</p>
      </div>
      <div class="hero-total">
        <span>К оплате</span>
        <strong>{{ cartTotal.toFixed(0) }} ₽</strong>
      </div>
    </section>

    <div v-if="isLoading" class="state-box">Загрузка корзины...</div>

    <div v-else-if="cartItems.length === 0" class="state-box">
      <p>Корзина пуста. Сначала добавьте товары в каталоге.</p>
      <router-link to="/catalog" class="primary-link">Перейти в каталог</router-link>
    </div>

    <div v-else class="checkout-layout">
      <section class="card-list">
        <div v-for="item in cartItems" :key="item.id" class="order-row">
          <div>
            <h2>{{ item.product.name }}</h2>
            <p>{{ item.product.enterprise?.short_name }} · {{ item.product.category?.name }}</p>
          </div>
          <div class="row-meta">
            <span>{{ item.quantity }} кг</span>
            <strong>{{ (Number(item.product.price) * item.quantity).toFixed(0) }} ₽</strong>
          </div>
        </div>
      </section>

      <aside class="summary-card">
        <div class="field">
          <label>Тип заказа</label>
          <input v-model="orderType" type="text" />
        </div>

        <div class="field">
          <label>Комментарий к доставке</label>
          <textarea v-model="deliveryNote" rows="4"></textarea>
        </div>

        <div class="summary-list">
          <div v-for="supplier in groupedSuppliers" :key="supplier.id" class="summary-line">
            <span>{{ supplier.name }}</span>
            <strong>{{ supplier.amount.toFixed(0) }} ₽</strong>
          </div>
        </div>

        <div v-if="errorMessage" class="message message--error">{{ errorMessage }}</div>
        <div v-if="successMessage" class="message message--success">{{ successMessage }}</div>

        <button class="checkout-btn" :disabled="isSubmitting" @click="submitCheckout">
          {{ isSubmitting ? 'Оформляем...' : 'Подтвердить заказ' }}
        </button>
        <router-link to="/cart" class="secondary-link">Вернуться в корзину</router-link>
      </aside>
    </div>
  </main>
</template>

<style scoped>
.checkout-page {
  display: grid;
  gap: 1.25rem;
  padding-bottom: 2rem;
}

.hero-card,
.summary-card,
.card-list,
.state-box {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(76, 124, 42, 0.14);
  border-radius: 1.5rem;
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.1);
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem;
}

.eyebrow {
  margin: 0 0 0.35rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
  color: #5d6b52;
}

.page-title {
  margin: 0;
  font-size: 1.9rem;
}

.page-text {
  margin: 0.5rem 0 0;
  color: #5d6b52;
}

.hero-total {
  min-width: 180px;
  display: grid;
  align-content: center;
  justify-items: end;
  text-align: right;
}

.hero-total strong {
  font-size: 1.8rem;
  color: #4c7c2a;
}

.checkout-layout {
  display: grid;
  grid-template-columns: 1.5fr 0.9fr;
  gap: 1rem;
}

.card-list,
.summary-card,
.state-box {
  padding: 1.25rem;
}

.order-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(76, 124, 42, 0.12);
}

.order-row:last-child {
  border-bottom: none;
}

.order-row h2 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
}

.order-row p {
  margin: 0;
  color: #5d6b52;
}

.row-meta {
  display: grid;
  justify-items: end;
  gap: 0.2rem;
  white-space: nowrap;
}

.row-meta strong {
  color: #3f5f2a;
}

.field {
  display: grid;
  gap: 0.45rem;
  margin-bottom: 1rem;
}

.field label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #5d6b52;
}

.field textarea {
  resize: vertical;
}

.summary-list {
  display: grid;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.summary-line {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.message {
  padding: 0.9rem 1rem;
  border-radius: 1rem;
  margin-bottom: 0.75rem;
}

.message--error {
  background: #fee2e2;
  color: #991b1b;
}

.message--success {
  background: #dcfce7;
  color: #166534;
}

.checkout-btn {
  width: 100%;
  border: none;
  border-radius: 999px;
  padding: 0.95rem 1.2rem;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  margin-bottom: 0.75rem;
}

.secondary-link,
.primary-link {
  display: inline-flex;
  justify-content: center;
  width: 100%;
  border-radius: 999px;
  padding: 0.8rem 1rem;
}

.secondary-link {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(76, 124, 42, 0.16);
  color: #3f4a2f;
}

.primary-link {
  background: linear-gradient(135deg, #bfe59e, #a5db74);
  color: #20311c;
  font-weight: 700;
}

@media (max-width: 900px) {
  .checkout-layout,
  .hero-card {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hero-total {
    justify-items: start;
    text-align: left;
  }
}
</style>
