<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'
import { AddIcon, BagIcon, CloseIcon, DeleteIcon, DocumentIcon, DoneIcon, MinusIcon, OrganizationIcon } from '@/assets/icons/png'

const store = useShopStore()
const authStore = useAuthStore()
const router = useRouter()

const isLoading = ref(false)
const isCheckingOut = ref(false)
const orderError = ref<string | null>(null)
const successMsg = ref<string | null>(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }
  isLoading.value = true
  await Promise.all([
    store.fetchCart(),
    store.fetchProducts()
  ])
  isLoading.value = false
})

const cartItems = computed(() => store.state.cartItems)

const cartTotal = computed(() =>
  cartItems.value.reduce(
    (sum, item) => sum + Number(item.product.price) * item.quantity,
    0,
  ),
)

const showOrderSentAndRedirect = () => {
  successMsg.value = 'Ваш заказ отправлен'
  setTimeout(() => {
    successMsg.value = null
    router.push('/my-orders')
  }, 1200)
}

const handleDecrease = async (item: any) => {
  const newQty = item.quantity - 1
  if (newQty <= 0) {
    await store.removeFromCart(item.product_id)
  } else {
    await store.setCartQuantity(item.product_id, newQty)
  }
}

const handleIncrease = async (item: any) => {
  await store.setCartQuantity(item.product_id, item.quantity + 1)
}

const handleRemove = async (productId: number) => {
  await store.removeFromCart(productId)
}

const handleCheckout = async () => {
  if (isCheckingOut.value) return
  orderError.value = null
  isCheckingOut.value = true
  try {
    const result = await store.checkoutCart()
    const firstOrder = result.orders[0]
    if (firstOrder) {
      showOrderSentAndRedirect()
    } else {
      orderError.value = 'Не удалось оформить заказ. Проверьте товары в корзине.'
    }
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    orderError.value = detail || 'Произошла ошибка при оформлении заказа'
  } finally {
    isCheckingOut.value = false
  }
}

const handleCreateTemplate = () => {
  store.saveOrderTemplate()
  successMsg.value = 'Ваш шаблон создан, вы можете использовать его на странице «Мои заказы»'
  setTimeout(() => { successMsg.value = null }, 6000)
}

</script>

<template>
  <div class="page">
    <main class="page-main">
      <h1 class="page-title">Корзина</h1>

      <Transition name="toast">
        <div v-if="successMsg" class="template-toast">
          <img :src="DoneIcon" alt="" class="t-icon" aria-hidden="true" />
          <div class="t-content">
            <p>{{ successMsg }}</p>
            <router-link to="/my-orders" class="t-link">Перейти к заказам →</router-link>
          </div>
          <button @click="successMsg = null" class="t-close">
            <img :src="CloseIcon" alt="" class="close-icon" aria-hidden="true" />
          </button>
        </div>
      </Transition>

      <div v-if="isLoading" class="status-msg">Загрузка корзины...</div>

      <div v-else-if="cartItems.length === 0" class="empty-state">
        <div class="empty-icon">
          <img :src="BagIcon" alt="" class="empty-icon-img" aria-hidden="true" />
        </div>
        <p>Ваша корзина пуста</p>
        <router-link to="/catalog" class="btn-go-catalog">Перейти в каталог</router-link>
      </div>

      <div v-else class="cart-layout">
        <div class="cart-items">
          <div v-for="item in cartItems" :key="item.id" class="cart-item-card">
            <div class="cart-item-image">
              <img :src="DocumentIcon" alt="" class="item-icon" aria-hidden="true" />
            </div>

            <div class="cart-item-info">
              <h3 class="item-name">{{ item.product.name }}</h3>
              <p class="item-category" v-if="item.product.category">{{ item.product.category.name }}</p>
              <p class="item-supplier" v-if="item.product.enterprise">
                <img :src="OrganizationIcon" alt="" class="supplier-icon" aria-hidden="true" />
                {{ item.product.enterprise.short_name }}
              </p>
              <p class="item-desc" v-if="item.product.description">{{ item.product.description }}</p>
            </div>

            <div class="cart-item-controls">
              <p class="item-price-unit">{{ item.product.price }} ₽/кг</p>

              <div class="qty-control">
                <button class="qty-btn" @click="handleDecrease(item)">
                  <img :src="MinusIcon" alt="" class="qty-icon" aria-hidden="true" />
                </button>
                <span class="qty-val">{{ item.quantity }} кг</span>
                <button class="qty-btn" @click="handleIncrease(item)">
                  <img :src="AddIcon" alt="" class="qty-icon" aria-hidden="true" />
                </button>
              </div>

              <p class="item-subtotal">
                {{ (Number(item.product.price) * item.quantity).toFixed(0) }} ₽
              </p>

              <button class="btn-remove" @click="handleRemove(item.product_id)">
                <img :src="DeleteIcon" alt="" class="remove-icon" aria-hidden="true" />
              </button>
            </div>
          </div>
        </div>

        <div class="order-summary">
          <h2 class="summary-title">Итог заказа</h2>

          <div class="summary-rows">
            <div class="summary-row" v-for="item in cartItems" :key="item.id">
              <span>{{ item.product.name }}</span>
              <span class="summary-row-val">
                {{ (Number(item.product.price) * item.quantity).toFixed(0) }} ₽
              </span>
            </div>
          </div>

          <div class="summary-divider"></div>

          <div class="summary-total">
            <span>Итого</span>
            <span class="total-amount">
              {{ cartTotal.toFixed(0) }} ₽
            </span>
          </div>

          <div v-if="orderError" class="order-error">{{ orderError }}</div>

          <div class="checkout-actions">
            <button class="btn-checkout" @click="handleCheckout" :disabled="isCheckingOut">
              {{ isCheckingOut ? 'Оформление...' : 'Оформить заказ' }}
            </button>
            <router-link to="/checkout" class="btn-checkout-secondary">Перейти к проверке</router-link>
          </div>

          <button class="btn-checkout-secondary btn-save-template" @click="handleCreateTemplate">
            <img :src="DocumentIcon" alt="" class="btn-icon" aria-hidden="true" />
            Создать шаблон заказа
          </button>

          <router-link to="/catalog" class="btn-continue">
            ← Продолжить покупки
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(135deg, #bfe59e 0%, #a5db74 100%);
  font-family: 'Inter', system-ui, sans-serif;
  color: #1f2a1a;
}

.page-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.5rem 1rem 4rem;
}

/* TITLE */
.page-title {
  font-size: 2rem;
  font-weight: 800;
  margin-bottom: 2rem;
  color: #20311c;
}

/* EMPTY */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: rgba(255,255,255,0.6);
  border-radius: 20px;
}

.btn-go-catalog {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.8rem 1.4rem;
  border-radius: 999px;
  background: #4c7c2a;
  color: white;
  text-decoration: none;
}

/* LAYOUT */
.cart-layout {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

/* ITEMS */
.cart-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* CARD */
.cart-item-card {
  display: grid;
  grid-template-columns: 70px 1fr auto;
  gap: 1.5rem;
  align-items: center;

  background: rgba(255,255,255,0.92);
  border-radius: 16px;
  padding: 1.25rem;

  box-shadow: 0 8px 20px rgba(0,0,0,0.05);
  transition: 0.2s ease;
}

.cart-item-card:hover {
  transform: translateY(-2px);
}

/* IMAGE */
.cart-item-image {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: #eef5e8;
  display: grid;
  place-items: center;
}

/* INFO */
.cart-item-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.item-name {
  font-size: 1.1rem;
  font-weight: 800;
  color: #1a2a16;
}

.item-category,
.item-supplier,
.item-desc {
  font-size: 0.85rem;
  color: #5d6b52;
}

/* CONTROLS */
.cart-item-controls {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

/* PRICE */
.item-price-unit {
  font-size: 0.85rem;
  color: #5d6b52;
}

/* QTY */
.qty-control {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: #f4f7f1;
  border-radius: 999px;
  padding: 0.3rem;
}

.qty-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: white;
  cursor: pointer;
  display: grid;
  place-items: center;
  transition: 0.2s;
}

.qty-btn:hover {
  background: #e8f2dc;
}

.qty-val {
  min-width: 60px;
  text-align: center;
  font-size: 0.9rem;
}

/* SUBTOTAL */
.item-subtotal {
  font-weight: 700;
  color: #20311c;
}

/* REMOVE */
.btn-remove {
  border: none;
  background: transparent;
  cursor: pointer;
}

/* SUMMARY */
.order-summary {
  position: sticky;
  top: 1rem;

  background: rgba(255,255,255,0.95);
  border-radius: 20px;
  padding: 1.5rem;

  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  height: fit-content;
}

.summary-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

/* ROWS */
.summary-rows {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #5d6b52;
}

.summary-divider {
  height: 1px;
  background: #e5eadf;
  margin: 1rem 0;
}

/* TOTAL */
.summary-total {
  display: flex;
  justify-content: space-between;
  font-weight: 700;
}

.total-amount {
  color: #2e7d32;
  font-size: 1.5rem;
}

/* BUTTONS */
.checkout-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-checkout {
  padding: 0.9rem;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
  cursor: pointer;
  font-weight: 700;
  transition: 0.2s;
}

.btn-checkout:hover {
  transform: translateY(-2px);
}

/* ВСЕ ВТОРИЧНЫЕ КНОПКИ В ОДНОМ СТИЛЕ */
.btn-checkout-secondary,
.btn-save-template {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  padding: 0.9rem;
  border-radius: 12px;

  background: rgba(255, 255, 255, 0.95);
  color: #3f4a2f;

  border: 1px solid rgba(76, 124, 42, 0.16);

  font-weight: 700;
  cursor: pointer;
  text-align: center;

  transition: 0.2s ease;
}

.btn-save-template {
  margin-top: 0.8rem;
}

.btn-checkout-secondary:hover,
.btn-save-template:hover {
  background: #ffffff;
  box-shadow: 0 6px 18px rgba(76, 124, 42, 0.12);
  transform: translateY(-1px);
}

/* CONTINUE */
.btn-continue {
  display: block;
  margin-top: 1rem;
  text-align: center;
  color: #3f4a2f;
}

/* TOAST */
.template-toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;

  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 1.25rem 1.5rem;
  border: 1px solid rgba(76, 124, 42, 0.2);

  box-shadow: 0 16px 40px rgba(0,0,0,0.12);

  display: flex;
  gap: 1rem;
  align-items: center;
}

.t-content p {
  margin: 0 0 0.4rem 0;
  font-weight: 700;
  color: #2e7d32;
}

.t-content .t-link {
  font-size: 0.9rem;
  color: #4c7c2a;
  text-decoration: underline;
}


/* ICONS */
.t-icon,
.close-icon,
.empty-icon-img,
.item-icon,
.qty-icon,
.remove-icon,
.btn-icon {
  object-fit: contain;
}

.t-icon,
.close-icon,
.qty-icon,
.remove-icon,
.btn-icon {
  width: 18px;
  height: 18px;
}

.empty-icon-img {
  width: 70px;
}

.item-icon {
  width: 28px;
}

.supplier-icon {
  width: 14px;
  margin-right: 4px;
}

/* MOBILE */
@media (max-width: 900px) {
  .cart-layout {
    grid-template-columns: 1fr;
  }

  .order-summary {
    position: static;
  }
}
</style>
