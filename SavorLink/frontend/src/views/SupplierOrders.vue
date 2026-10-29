<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import { CalendarIcon, CloseIcon, DocumentIcon, DoneIcon, OrganizationIcon, TruckIcon } from '@/assets/icons/png'

import NotificationBell from '@/components/NotificationBell.vue'

const router = useRouter()
const store = useShopStore()
const authStore = useAuthStore()

const orders = computed(() => store.state.supplierOrders)
const isLoading = computed(() => store.state.ordersLoading)

const unreadCount = computed(() => 
  orders.value.filter(o => o.id > store.state.lastSeenOrderId).length
)

const updatingOrderId = ref<number | null>(null)
const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }
  if (authStore.user?.role !== 'SUPPLIER') {
    router.push('/')
    return
  }
  await store.fetchSupplierOrders()
  // Mark as seen once loaded
  store.markOrdersSeen('SUPPLIER')
})

const pendingOrders = computed(() =>
  orders.value.filter(o => o.status === 'CREATED')
)
const activeOrders = computed(() =>
  orders.value.filter(o => o.status === 'CONFIRMED' || o.status === 'IN_PROGRESS')
)
const historyOrders = computed(() =>
  orders.value.filter(o => o.status === 'COMPLETED' || o.status === 'CANCELLED')
)

const statusLabel: Record<string, { text: string; icon: string; class: string }> = {
  CREATED: { text: 'Новый запрос', icon: 'calendar', class: 'status-created' },
  CONFIRMED: { text: 'Подтверждён', icon: 'done', class: 'status-confirmed' },
  IN_PROGRESS: { text: 'В процессе', icon: 'truck', class: 'status-inprogress' },
  COMPLETED: { text: 'Завершён успешно', icon: 'done', class: 'status-completed' },
  CANCELLED: { text: 'Отклонён', icon: 'close', class: 'status-cancelled' },
}

const getStatusInfo = (status: string) =>
  statusLabel[status] || { text: status, icon: 'document', class: 'status-created' }

const statusIcon = (icon: string) => {
  switch (icon) {
    case 'calendar':
      return CalendarIcon
    case 'done':
      return DoneIcon
    case 'close':
      return CloseIcon
    case 'truck':
      return TruckIcon
    default:
      return DocumentIcon
  }
}

const formatDate = (dt: string) => {
  const d = new Date(dt)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatAmount = (amount: number | null) => {
  if (amount === null) return '—'
  return amount.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽'
}

const showToast = (msg: string, isError = false) => {
  if (isError) {
    errorMsg.value = msg
    setTimeout(() => { errorMsg.value = null }, 5000)
  } else {
    successMsg.value = msg
    setTimeout(() => { successMsg.value = null }, 5000)
  }
}

const confirmOrder = async (orderId: number) => {
  if (updatingOrderId.value) return
  updatingOrderId.value = orderId
  try {
    const updated = await store.updateOrderStatus(orderId, 'CONFIRMED')
    if (updated) {
      const idx = store.state.supplierOrders.findIndex(o => o.id === orderId)
      if (idx !== -1) store.state.supplierOrders[idx] = updated
      showToast(`Заказ #${orderId} принят в работу. Остатки на складе обновлены.`)
    }
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Ошибка при подтверждении', true)
  } finally {
    updatingOrderId.value = null
  }
}

const rejectOrder = async (orderId: number) => {
  if (!confirm(`Вы уверены, что хотите отклонить заказ #${orderId}?`)) return
  if (updatingOrderId.value) return
  updatingOrderId.value = orderId
  try {
    const updated = await store.updateOrderStatus(orderId, 'CANCELLED')
    if (updated) {
      const idx = store.state.supplierOrders.findIndex(o => o.id === orderId)
      if (idx !== -1) store.state.supplierOrders[idx] = updated
      showToast(`Заказ #${orderId} отклонён.`)
    }
  } catch (err: any) {
    showToast(err?.response?.data?.detail || 'Ошибка при отклонении', true)
  } finally {
    updatingOrderId.value = null
  }
}
</script>

<template>
  <div class="page">
    <main class="page-main">
      <div class="glass-header">
        <div class="header-content">
          <div class="title-with-bell">
            <h1 class="page-title">Управление заказами</h1>
            <NotificationBell :count="unreadCount" />
          </div>
          <p class="page-subtitle">Контролируйте свои продажи и остатки в реальном времени</p>
        </div>
        <div class="header-stats">
          <div class="stat-card" :class="{ 'stat-card--active': pendingOrders.length > 0 }">
            <span class="stat-val">{{ pendingOrders.length }}</span>
            <span class="stat-lab">Новых</span>
          </div>
          <div class="stat-card">
            <span class="stat-val">{{ activeOrders.length }}</span>
            <span class="stat-lab">В работе</span>
          </div>
          <div class="stat-card">
            <span class="stat-val">{{ historyOrders.length }}</span>
            <span class="stat-lab">Всего</span>
          </div>
        </div>
      </div>

      <!-- Toasts -->
      <TransitionGroup name="toast">
        <div v-if="successMsg" key="success" class="toast toast-success">
          <img :src="DoneIcon" alt="" class="toast-icon" aria-hidden="true" />
          <div class="toast-body">{{ successMsg }}</div>
        </div>
        <div v-if="errorMsg" key="error" class="toast toast-error">
          <img :src="CloseIcon" alt="" class="toast-icon" aria-hidden="true" />
          <div class="toast-body">{{ errorMsg }}</div>
        </div>
      </TransitionGroup>

      <!-- Loading -->
      <div v-if="isLoading" class="loading-container">
        <div class="loader"></div>
        <p>Синхронизация данных...</p>
      </div>

      <div v-else-if="orders.length === 0" class="empty-hero">
        <div class="hero-icon">
          <img :src="DocumentIcon" alt="" class="hero-icon-img" aria-hidden="true" />
        </div>
        <h2>Заказов пока нет</h2>
        <p>Ваши товары ждут своих покупателей. Как только кто-то оформит заказ, он появится здесь.</p>
      </div>

      <div v-else class="sections-grid">
        <!-- НОВЫЕ ЗАПРОСЫ -->
        <section v-if="pendingOrders.length > 0" class="order-section">
          <h2 class="section-heading">
            <span class="pulse-dot"></span>
            Новые поступления
          </h2>
          <div class="cards-stack">
            <div
              v-for="order in pendingOrders"
              :key="order.id"
              class="premium-card premium-card--new"
            >
              <div class="card-header">
                <div class="id-badge">Order #{{ order.id }}</div>
                <div class="date-tag">{{ formatDate(order.created_at) }}</div>
              </div>

              <div class="card-body">
                <div class="client-info">
                  <div class="avatar">
                    <img :src="OrganizationIcon" alt="" class="avatar-icon" aria-hidden="true" />
                  </div>
                  <div class="client-details">
                    <span class="client-name">{{ order.buyer_enterprise?.short_name || 'Покупатель' }}</span>
                    <span class="client-region">{{ order.buyer_enterprise?.region || 'Регион не указан' }}</span>
                  </div>
                </div>

                <div class="products-mini">
                  <div v-for="item in order.items" :key="item.id" class="mini-item">
                    <span class="m-name">{{ item.product?.name }}</span>
                    <div class="m-dots"></div>
                    <span class="m-qty">{{ item.quantity }} кг</span>
                  </div>
                </div>

                <div class="total-bar">
                  <span class="t-label">К оплате:</span>
                  <span class="t-value">{{ formatAmount(order.total_amount) }}</span>
                </div>
              </div>

              <div class="card-actions">
                <button
                  class="btn-action btn-action--confirm"
                  @click="confirmOrder(order.id)"
                  :disabled="updatingOrderId === order.id"
                >
                  <span v-if="updatingOrderId === order.id" class="spin">⌛</span>
                  <span v-else>Принять и списать со склада</span>
                </button>
                <button
                  class="btn-action btn-action--reject"
                  @click="rejectOrder(order.id)"
                  :disabled="updatingOrderId === order.id"
                >
                  Отклонить
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- АКТИВНЫЕ -->
        <section v-if="activeOrders.length > 0" class="order-section">
          <h2 class="section-heading">Активные сделки</h2>
          <div class="cards-grid">
            <div
              v-for="order in activeOrders"
              :key="order.id"
              class="premium-card"
            >
              <div class="card-header">
                <div class="status-chip" :class="getStatusInfo(order.status).class">
                  <img :src="statusIcon(getStatusInfo(order.status).icon)" alt="" class="chip-icon" aria-hidden="true" />
                  {{ getStatusInfo(order.status).text }}
                </div>
                <div class="id-badge">#{{ order.id }}</div>
              </div>
              
              <div class="card-body">
                <div class="client-info">
                  <div class="avatar avatar--sm">
                    <img :src="OrganizationIcon" alt="" class="avatar-icon" aria-hidden="true" />
                  </div>
                  <div class="client-details">
                    <span class="client-name">{{ order.buyer_enterprise?.short_name }}</span>
                    <span class="client-region">{{ order.buyer_enterprise?.region }}</span>
                  </div>
                </div>

                <div class="products-mini products-mini--compact">
                  <div v-for="item in order.items" :key="item.id" class="mini-item">
                    <span class="m-name">{{ item.product?.name }}</span>
                    <div class="m-dots"></div>
                    <span class="m-qty">{{ item.quantity }} кг</span>
                  </div>
                </div>

                <div class="total-bar compact">
                  <span class="t-value">{{ formatAmount(order.total_amount) }}</span>
                </div>
              </div>
              
              <div class="card-footer">
                <div class="wait-status">
                  <span class="dots-loader"></span>
                  Ожидание подтверждения от покупателя
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ИСТОРИЯ -->
        <section v-if="historyOrders.length > 0" class="order-section">
          <h2 class="section-heading">Завершенные</h2>
          <div class="history-table-wrapper">
            <table class="history-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Дата</th>
                  <th>Клиент</th>
                  <th>Состав</th>
                  <th>Сумма</th>
                  <th>Статус</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="order in historyOrders" :key="order.id" :class="order.status.toLowerCase()">
                  <td class="td-id">#{{ order.id }}</td>
                  <td class="td-date">{{ formatDate(order.created_at) }}</td>
                  <td class="td-client">
                    <div class="client-cell">
                      <strong>{{ order.buyer_enterprise?.short_name }}</strong>
                      <small>{{ order.buyer_enterprise?.region }}</small>
                    </div>
                  </td>
                  <td class="td-items">
                    <div class="items-cell">
                      <span v-for="item in order.items" :key="item.id">
                        {{ item.product?.name }} ({{ item.quantity }} кг)
                      </span>
                    </div>
                  </td>
                  <td class="td-amount">{{ formatAmount(order.total_amount) }}</td>
                  <td>
                    <span class="small-badge" :class="getStatusInfo(order.status).class">
                      {{ getStatusInfo(order.status).text }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  font-family: 'Manrope', sans-serif;
  background: transparent;
  color: #20311c;
}

/* MAIN */
.page-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 3rem 1.5rem 6rem;
}

/* HEADER (GLASS) */
.glass-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 2rem;
  margin-bottom: 3rem;

  border-radius: 1.7rem;
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(76,124,42,0.16);
  backdrop-filter: blur(18px);

  box-shadow: 0 24px 60px rgba(54,87,21,0.12);
}

.page-title {
  font-size: 1.7rem;
  font-weight: 800;
  color: #20311c;
  margin: 0;
}

.page-subtitle {
  font-size: 0.9rem;
  color: #5d6b52;
  margin: 0;
}

.title-with-bell {
  display: flex;
  align-items: center;
  gap: 1rem;
}

/* STATS */
.header-stats {
  display: flex;
  gap: 1rem;
}

.stat-card {
  width: 90px;
  padding: 1rem;

  display: flex;
  flex-direction: column;
  align-items: center;

  border-radius: 1.2rem;
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(76,124,42,0.16);
  backdrop-filter: blur(18px);

  transition: 0.2s ease;
}

.stat-card--active {
  border-color: #6da13d;
  box-shadow: 0 10px 25px rgba(76,124,42,0.15);
}

.stat-val {
  font-size: 1.4rem;
  font-weight: 800;
  color: #20311c;
}

.stat-lab {
  font-size: 0.75rem;
  color: #5d6b52;
}

/* TOAST */
.toast {
  position: fixed;
  top: 90px;
  right: 2rem;

  display: flex;
  align-items: center;
  gap: 1rem;

  padding: 1rem 1.5rem;
  border-radius: 1.5rem;

  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(76,124,42,0.16);
  backdrop-filter: blur(18px);

  box-shadow: 0 24px 60px rgba(54,87,21,0.15);
}

.toast-icon,
.chip-icon,
.hero-icon-img {
  display: block;
  object-fit: contain;
}

.toast-icon {
  width: 18px;
  height: 18px;
}

.chip-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.hero-icon-img {
  width: 72px;
  height: 72px;
  margin: 0 auto;
}

.avatar-icon {
  width: 24px;
  height: 24px;
  object-fit: contain;
  display: block;
}

.toast-success {
  color: #4c7c2a;
}

.toast-error {
  color: #991b1b;
}

/* SECTIONS */
.sections-grid {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.section-heading {
  font-size: 1.2rem;
  font-weight: 800;
  color: #20311c;
  margin-bottom: 1rem;
}

/* CARDS */
.premium-card {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(76,124,42,0.16);
  border-radius: 1.7rem;
  padding: 1.5rem;

  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54,87,21,0.08);

  transition: 0.25s ease;
}

.premium-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 30px 70px rgba(54,87,21,0.15);
}

.premium-card--new {
  border-left: 5px solid #fbbf24;
}

/* CLIENT */
.client-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1rem;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 1rem;

  display: flex;
  align-items: center;
  justify-content: center;

  background: rgba(241,245,249,0.8);
}

.client-name {
  font-weight: 800;
  color: #20311c;
}

.client-region {
  font-size: 0.8rem;
  color: #5d6b52;
}

/* ITEMS */
.products-mini {
  background: rgba(249,250,251,0.6);
  border-radius: 1.2rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.mini-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  margin-bottom: 0.3rem;
}

.m-name {
  font-weight: 600;
  color: #2f3b2a;
}

.m-qty {
  font-weight: 800;
  color: #3f4a2f;
}

/* TOTAL */
.t-value {
  font-size: 1.4rem;
  font-weight: 900;

  color: #4c7c2a;
}

/* BUTTONS */
.btn-action {
  border-radius: 999px;
  padding: 0.8rem 1.2rem;
  font-weight: 700;
  cursor: pointer;
  border: none;
}

.btn-action--confirm {
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
}

.btn-action--reject {
  background: rgba(254, 226, 226, 0.8);
  color: #991b1b;
}

/* STATUS CHIP */
.status-chip {
  padding: 0.4rem 0.8rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 800;
  background: rgba(255,255,255,0.7);
  border: 1px solid rgba(76,124,42,0.16);
}

/* TABLE */
.history-table-wrapper {
  background: rgba(255,255,255,0.78);
  border-radius: 1.7rem;
  border: 1px solid rgba(76,124,42,0.16);
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54,87,21,0.08);
  overflow-x: auto;
}

.history-table {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
  table-layout: fixed;
}

.history-table th,
.history-table td {
  padding: 0.85rem 1rem;
  text-align: left;
  vertical-align: top;
}

.history-table thead th {
  font-size: 1rem;
  font-weight: 800;
  color: #20311c;
  border-bottom: 1px solid rgba(76,124,42,0.16);
}

.history-table tbody tr + tr td {
  border-top: 1px solid rgba(76,124,42,0.1);
}

.history-table th:nth-child(1),
.history-table td:nth-child(1) {
  width: 72px;
}

.history-table th:nth-child(2),
.history-table td:nth-child(2) {
  width: 120px;
}

.history-table th:nth-child(5),
.history-table td:nth-child(5) {
  width: 120px;
}

.history-table th:nth-child(6),
.history-table td:nth-child(6) {
  width: 150px;
}

.td-id {
  font-weight: 800;
  color: #29451e;
}

.td-date,
.client-cell,
.items-cell {
  line-height: 1.35;
}

.client-cell,
.items-cell {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.client-cell small {
  color: #5d6b52;
}

.items-cell span {
  word-break: break-word;
}

.td-amount {
  font-weight: 800;
  color: #29451e;
  white-space: nowrap;
}

.small-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
}

.small-badge.status-completed {
  background: rgba(220, 252, 231, 0.9);
  color: #166534;
}

.small-badge.status-cancelled {
  background: rgba(254, 226, 226, 0.9);
  color: #991b1b;
}

/* LOADER */
.loader {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 4px solid rgba(76,124,42,0.2);
  border-top-color: #4c7c2a;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* EMPTY */
.empty-hero {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(76,124,42,0.16);
  border-radius: 1.7rem;
  padding: 4rem 2rem;
  text-align: center;
  backdrop-filter: blur(18px);
}

/* ANIMATIONS */
.toast-enter-active,
.toast-leave-active {
  transition: 0.2s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
