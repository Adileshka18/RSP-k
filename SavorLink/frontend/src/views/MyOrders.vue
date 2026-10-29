<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import { CalendarIcon, CloseIcon, DeleteIcon, DoneIcon, DocumentIcon, TruckIcon } from '@/assets/icons/png'

import NotificationBell from '@/components/NotificationBell.vue'

const router = useRouter()
const store = useShopStore()
const authStore = useAuthStore()

const orders = computed(() => store.state.myOrders)
const isLoading = computed(() => store.state.ordersLoading)

const unreadCount = computed(() => 
  orders.value.filter(o => o.id > store.state.lastSeenOrderId && o.status !== 'CREATED').length
)

const updatingOrderId = ref<number | null>(null)
const successMsg = ref<string | null>(null)
const errorMsg = ref<string | null>(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }
  if (authStore.user?.role !== 'BUYER') {
    router.push('/')
    return
  }
  store.state.ordersLoading = true
  await Promise.all([
    store.fetchMyOrders(),
    store.fetchProducts()
  ])
  store.markOrdersSeen('BUYER')
})

const showTemplateModal = ref(false)
const isCheckingOut = ref(false)

const templateItems = computed(() => {
  if (!store.state.orderTemplate) return []
  return store.state.orderTemplate.map(item => {
    const product = store.state.products.find(p => p.id === item.product_id)
    return {
      ...item,
      product
    }
  }).filter(item => !!item.product)
})

const templateTotal = computed(() => {
  return templateItems.value.reduce((sum, item) => {
    return sum + (item.product?.price || 0) * item.quantity
  }, 0)
})

const handleCheckoutTemplate = async () => {
  if (isCheckingOut.value) return
  isCheckingOut.value = true
  try {
    const result = await store.checkoutWithItems(store.state.orderTemplate || [])
    if (result.orders.length > 0) {
      successMsg.value = `Шаблон успешно оформлен! Создано заказов: ${result.orders.length}`
      showTemplateModal.value = false
      setTimeout(() => { successMsg.value = null }, 5000)
    }
  } catch (err: any) {
    errorMsg.value = err.message || 'Ошибка при оформлении шаблона'
  } finally {
    isCheckingOut.value = false
  }
}

const handleDeleteTemplate = () => {
  if (confirm('Вы уверены, что хотите удалить этот шаблон?')) {
    store.deleteOrderTemplate()
    showTemplateModal.value = false
  }
}

const statusLabel: Record<string, { text: string; icon: string; class: string }> = {
  CREATED: { text: 'На рассмотрении', icon: 'calendar', class: 'status-created' },
  CONFIRMED: { text: 'Принят в работу', icon: 'done', class: 'status-confirmed' },
  IN_PROGRESS: { text: 'В пути', icon: 'truck', class: 'status-inprogress' },
  COMPLETED: { text: 'Доставлен', icon: 'done', class: 'status-completed' },
  CANCELLED: { text: 'Отклонён поставщиком', icon: 'close', class: 'status-cancelled' },
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
    case 'document':
    default:
      return DocumentIcon
  }
}

const formatDate = (dt: string) => {
  const d = new Date(dt)
  return d.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatAmount = (amount: number | null) => {
  if (amount === null) return '—'
  return amount.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽'
}

const markDelivered = async (orderId: number) => {
  if (updatingOrderId.value) return
  updatingOrderId.value = orderId
  errorMsg.value = null
  try {
    const updated = await store.updateOrderStatus(orderId, 'COMPLETED')
    if (updated) {
      const idx = store.state.myOrders.findIndex(o => o.id === orderId)
      if (idx !== -1) store.state.myOrders[idx] = updated
      successMsg.value = `Заказ #${orderId} успешно получен! Спасибо за покупку.`
      setTimeout(() => { successMsg.value = null }, 5000)
    }
  } catch (err: any) {
    errorMsg.value = err?.response?.data?.detail || 'Ошибка при обновлении статуса'
  } finally {
    updatingOrderId.value = null
  }
}
</script>

<template>
  <div class="page">
    <main class="page-main">
      <div class="page-header">
        <div class="title-wrapper">
          <h1 class="page-title">Мои заказы</h1>
          <NotificationBell :count="unreadCount" />
        </div>
        <div class="header-actions">
          <button 
            v-if="store.state.orderTemplate" 
            class="btn-use-template" 
            @click="showTemplateModal = true"
          >
            <img :src="DocumentIcon" alt="" class="btn-icon" aria-hidden="true" />
            Использовать шаблон
          </button>
          <p class="page-count" v-if="!isLoading">Всего заказов: {{ orders.length }}</p>
        </div>
      </div>

      <!-- Toast -->
      <TransitionGroup name="toast">
        <div v-if="successMsg" key="success" class="toast toast-success">
          <img :src="DoneIcon" alt="" class="t-icon" aria-hidden="true" />
          {{ successMsg }}
        </div>
        <div v-if="errorMsg" key="error" class="toast toast-error">
          <img :src="CloseIcon" alt="" class="t-icon" aria-hidden="true" />
          {{ errorMsg }}
        </div>
      </TransitionGroup>

      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>Загрузка вашей истории заказов...</p>
      </div>

      <div v-else-if="orders.length === 0" class="empty-state">
        <div class="empty-illustration">
          <img :src="DocumentIcon" alt="" class="empty-icon" aria-hidden="true" />
        </div>
        <h2>У вас пока нет заказов</h2>
        <p>Время наполнить корзину свежими продуктами!</p>
        <router-link to="/catalog" class="btn-catalog">В каталог</router-link>
      </div>

      <div v-else class="orders-grid">
        <div
          v-for="order in orders"
          :key="order.id"
          class="order-card"
          :class="{ 
            'order-card--cancelled': order.status === 'CANCELLED', 
            'order-card--completed': order.status === 'COMPLETED' 
          }"
        >
          <div class="card-header">
            <div class="order-meta">
              <span class="order-number">Заказ #{{ order.id }}</span>
              <span class="order-date">{{ formatDate(order.created_at) }}</span>
            </div>
            <div class="status-badge" :class="getStatusInfo(order.status).class">
              <img :src="statusIcon(getStatusInfo(order.status).icon)" alt="" class="badge-icon" aria-hidden="true" />
              {{ getStatusInfo(order.status).text }}
            </div>
          </div>

          <div class="card-body">
            <div class="supplier-info">
              <span class="info-label">Поставщик</span>
              <span class="info-value">{{ order.seller_enterprise?.short_name }}</span>
            </div>

            <!-- Items list -->
            <div class="order-content">
              <div v-for="item in order.items" :key="item.id" class="item-row">
                <span class="item-name">{{ item.product?.name || `Товар #${item.product_id}` }}</span>
                <span class="item-dots"></span>
                <span class="item-vals">
                  <span class="item-qty">{{ item.quantity }} кг</span>
                  <span class="item-price">{{ (item.price * item.quantity).toFixed(0) }} ₽</span>
                </span>
              </div>
            </div>

            <div class="order-total">
              <span class="total-label">Итоговая сумма</span>
              <span class="total-value">{{ formatAmount(order.total_amount) }}</span>
            </div>
          </div>

          <div class="card-footer">
            <template v-if="order.status === 'CONFIRMED' || order.status === 'IN_PROGRESS'">
              <button
                class="btn-delivered"
                @click="markDelivered(order.id)"
                :disabled="updatingOrderId === order.id"
              >
                <span v-if="updatingOrderId === order.id" class="loading-sm"></span>
                {{ updatingOrderId === order.id ? 'Обновляем...' : 'Заказ получен' }}
              </button>
              <p class="footer-hint" v-if="order.status === 'CONFIRMED'">
                Нажмите, когда товар будет у вас
              </p>
            </template>
            
            <div v-else-if="order.status === 'COMPLETED'" class="note-success">
              Сделка успешно завершена
            </div>
            <div v-else-if="order.status === 'CANCELLED'" class="note-error">
              Заказ был отменён
            </div>
            <div v-else class="note-pending">
              Ожидайте подтверждения от поставщика
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Template Modal -->
    <Transition name="modal">
      <div v-if="showTemplateModal" class="modal-overlay" @click.self="showTemplateModal = false">
        <div class="modal-template">
          <button class="btn-close-modal" @click="showTemplateModal = false">
            <img :src="CloseIcon" alt="" class="btn-icon" aria-hidden="true" />
          </button>
          <h2 class="modal-title">Ваш шаблон заказа</h2>
          
          <div class="template-items-list">
            <div v-for="item in templateItems" :key="item.product_id" class="template-item-card">
              <div class="t-item-icon">
                <img :src="DocumentIcon" alt="" class="item-icon-img" aria-hidden="true" />
              </div>
              <div class="t-item-main">
                <div class="t-item-top">
                  <span class="t-item-name">{{ item.product?.name }}</span>
                  <span class="t-item-category" v-if="item.product?.category">{{ item.product.category.name }}</span>
                </div>
                <div class="t-item-details">
                  <span class="t-item-supplier" v-if="item.product?.enterprise">{{ item.product.enterprise.short_name }}</span>
                  <span class="t-item-qty">{{ item.quantity }} кг × {{ item.product?.price }} ₽</span>
                </div>
              </div>
              <div class="t-item-subtotal">
                {{ ((item.product?.price || 0) * item.quantity).toFixed(0) }} ₽
              </div>
            </div>
          </div>

          <div class="template-footer">
            <div class="template-total">
              <span>Итого по шаблону</span>
              <span class="t-total-val">{{ templateTotal.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ' ') }} ₽</span>
            </div>
            
            <div class="template-actions">
              <button class="btn-checkout-template" @click="handleCheckoutTemplate" :disabled="isCheckingOut">
                <span v-if="isCheckingOut" class="spinner-sm"></span>
                {{ isCheckingOut ? 'Оформление...' : 'Оформить по шаблону' }}
              </button>
              <button class="btn-delete-template" @click="handleDeleteTemplate">
                <img :src="DeleteIcon" alt="" class="btn-icon" aria-hidden="true" />
                Удалить шаблон
              </button>
            </div>
            <p class="template-hint">* Цены соответствуют текущим в каталоге</p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background-color: #f8f6f0;
  color: #2e3524;
  font-family: 'Inter', system-ui, sans-serif;
}

.page-main {
  max-width: 800px;
  margin: 0 auto;
  padding: 3rem 1.5rem 6rem;
}

.page-header {
  margin-bottom: 2.5rem;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.page-title {
  font-size: 2rem;
  font-weight: 800;
  color: #3f4a2f;
  margin: 0;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.page-count {
  color: #6b7280;
  font-weight: 500;
  font-size: 0.9rem;
}

/* Toast */
.toast {
  position: fixed;
  top: 90px;
  right: 2rem;
  background: white;
  padding: 1rem 1.75rem;
  border-radius: 16px;
  box-shadow: 0 12px 30px rgba(0,0,0,0.12);
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
  border: 1px solid rgba(0,0,0,0.05);
}

.t-icon,
.btn-icon,
.badge-icon,
.empty-icon,
.item-icon-img {
  display: block;
  object-fit: contain;
}

.t-icon {
  width: 18px;
  height: 18px;
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.badge-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.empty-icon {
  width: 72px;
  height: 72px;
  margin: 0 auto;
}

.item-icon-img {
  width: 30px;
  height: 30px;
}

.toast-success { color: #059669; border-left: 5px solid #10b981; }
.toast-error { color: #dc2626; border-left: 5px solid #ef4444; }

.toast-enter-active, .toast-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.toast-enter-from { opacity: 0; transform: translateX(30px); }
.toast-leave-to { opacity: 0; transform: scale(0.95); }

/* Grid */
.orders-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.order-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.06);
}

.order-card--cancelled { opacity: 0.8; border-color: #fee2e2; }
.order-card--completed { background: #fdfdfd; border-color: #d1fae5; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.order-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.order-number {
  font-size: 1.1rem;
  font-weight: 800;
  color: #111827;
}

.order-date {
  font-size: 0.82rem;
  color: #9ca3af;
  font-weight: 500;
}

.status-badge {
  padding: 0.4rem 0.85rem;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  white-space: nowrap;
}

.status-created { background: #fef3c7; color: #92400e; }
.status-confirmed { background: #d1fae5; color: #065f46; }
.status-inprogress { background: #dbeafe; color: #1e40af; }
.status-completed { background: #d1fae5; color: #065f46; }
.status-cancelled { background: #fee2e2; color: #991b1b; }

.card-body {
  border-top: 1px solid #f3f4f6;
  padding-top: 1.25rem;
}

.supplier-info {
  margin-bottom: 1.25rem;
}

.info-label {
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.info-value {
  font-weight: 700;
  color: #374151;
}

.order-content {
  background: #f9fafb;
  border-radius: 14px;
  padding: 1rem;
  margin-bottom: 1.25rem;
}

.item-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.item-row:last-child { margin-bottom: 0; }

.item-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #4b5563;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex-shrink: 1;
}

.item-dots {
  flex-grow: 1;
  border-bottom: 1px dashed #d1d5db;
  height: 10px;
}

.item-vals {
  display: flex;
  gap: 1rem;
  flex-shrink: 0;
}

.item-qty { font-size: 0.85rem; color: #6b7280; font-weight: 500; }
.item-price { font-size: 0.9rem; font-weight: 700; color: #3f4a2f; }

.order-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 0.5rem;
}

.total-label { font-size: 0.9rem; font-weight: 600; color: #6b7280; }
.total-value { font-size: 1.35rem; font-weight: 900; color: #059669; }

.card-footer {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid #f3f4f6;
  text-align: right;
}

.btn-delivered {
  background: #3f4a2f;
  color: white;
  border: none;
  padding: 0.75rem 1.75rem;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-delivered:hover:not(:disabled) {
  background: #4a5638;
  box-shadow: 0 4px 15px rgba(63, 74, 47, 0.25);
}

.footer-hint {
  font-size: 0.75rem;
  color: #9ca3af;
  margin-top: 0.5rem;
}

.note-success { color: #059669; font-weight: 700; font-size: 0.9rem; }
.note-error { color: #dc2626; font-weight: 600; font-size: 0.9rem; }
.note-pending { color: #92400e; font-size: 0.9rem; font-weight: 500; font-style: italic; }

/* Empty state */
.empty-state {
  text-align: center;
  padding: 5rem 2rem;
  background: white;
  border-radius: 30px;
  border: 1px solid #e5e7eb;
}

.empty-illustration { font-size: 4rem; margin-bottom: 2rem; }
.empty-state h2 { font-weight: 800; color: #3f4a2f; }
.empty-state p { color: #6b7280; margin-bottom: 2.5rem; }

.btn-catalog {
  background: #3f4a2f;
  color: white;
  text-decoration: none;
  padding: 0.85rem 2.5rem;
  border-radius: 999px;
  font-weight: 700;
  transition: all 0.2s;
}

.btn-catalog:hover { background: #4a5638; }

/* Loading */
.loading-state {
  text-align: center;
  padding: 4rem 0;
  color: #9ca3af;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f4f6;
  border-top-color: #3f4a2f;
  border-radius: 50%;
  animation: spin 1s infinite linear;
  margin: 0 auto 1.5rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Template Styling */
.btn-use-template {
  background: white;
  color: #3f4a2f;
  border: 1px solid #e5e7eb;
  padding: 0.6rem 1.25rem;
  border-radius: 12px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

.btn-use-template .btn-icon,
.btn-delete-template .btn-icon {
  width: 18px;
  height: 18px;
}

.btn-use-template:hover {
  background: #fdfdfd;
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(0,0,0,0.08);
  border-color: #3f4a2f;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(30, 25, 15, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 1rem;
}

.modal-template {
  background: #fdfaf3;
  border-radius: 32px;
  padding: 3rem 2.5rem;
  max-width: 600px;
  width: 100%;
  box-shadow: 0 30px 70px rgba(0,0,0,0.25);
  position: relative;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
}

.btn-close-modal {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: #f1f5f9;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  cursor: pointer;
  color: #64748b;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-close-modal .btn-icon {
  width: 18px;
  height: 18px;
}

.btn-close-modal:hover {
  background: #e2e8f0;
  color: #0f172a;
  transform: rotate(90deg);
}

.modal-title {
  font-size: 1.85rem;
  font-weight: 900;
  color: #3f4a2f;
  margin-bottom: 2rem;
  text-align: center;
}

.template-items-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
  overflow-y: auto;
  padding: 0.5rem;
}

.template-item-card {
  background: white;
  border-radius: 18px;
  padding: 1.25rem;
  display: grid;
  grid-template-columns: 48px 1fr auto;
  gap: 1rem;
  align-items: center;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.t-item-icon {
  width: 48px;
  height: 48px;
  background: #f1f5f9;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.t-item-main {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.t-item-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.t-item-name {
  font-weight: 800;
  color: #111827;
  font-size: 1rem;
}

.t-item-category {
  font-size: 0.75rem;
  color: #3f4a2f;
  background: #ecf3e6;
  padding: 0.1rem 0.5rem;
  border-radius: 4px;
  font-weight: 700;
}

.t-item-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  color: #6b7280;
}

.t-item-supplier { font-weight: 600; }
.t-item-qty { font-weight: 500; }

.t-item-subtotal {
  font-weight: 900;
  color: #3f4a2f;
  font-size: 1.1rem;
}

.template-footer {
  border-top: 1px solid #e2e8f0;
  padding-top: 1.5rem;
}

.template-total {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1.5rem;
}

.template-total span:first-child {
  font-weight: 700;
  color: #6b7280;
}

.t-total-val {
  font-size: 1.75rem;
  font-weight: 900;
  color: #059669;
}

.template-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.btn-checkout-template {
  background: #3f4a2f;
  color: #fff;
  border: none;
  padding: 1.15rem;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(63, 74, 47, 0.2);
}

.btn-checkout-template:hover:not(:disabled) {
  background: #4a5638;
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(63, 74, 47, 0.3);
}

.btn-delete-template {
  background: #fee2e2;
  color: #991b1b;
  border: none;
  padding: 1.15rem;
  border-radius: 16px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-delete-template:hover {
  background: #fecaca;
  color: #7f1d1d;
}

.template-hint {
  font-size: 0.8rem;
  color: #94a3b8;
  text-align: center;
  margin: 0;
  font-weight: 500;
}

.modal-enter-active { animation: pop-in 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-leave-active { transition: opacity 0.3s, transform 0.3s; }
.modal-leave-to { opacity: 0; transform: scale(0.9); }

@keyframes pop-in {
  from { opacity: 0; transform: scale(0.6) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.spinner-sm {
  width: 18px;
  height: 18px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}
</style>

<style scoped>
.page {
  min-height: 100vh;
  font-family: 'Manrope', sans-serif;
  background: transparent;
  color: #20311c;
}

/* MAIN LAYOUT */
.page-main {
  max-width: 850px;
  margin: 0 auto;
  padding: 3rem 1.5rem 6rem;
}

/* HEADER */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #20311c;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
}

.page-count {
  font-size: 0.85rem;
  color: #5d6b52;
}

/* BUTTON (template) */
.btn-use-template {
  border-radius: 999px;
  padding: 0.65rem 1.2rem;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
  border: none;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(76,124,42,0.25);
  transition: 0.2s ease;
}

.btn-use-template:hover {
  transform: translateY(-2px);
}

/* TOAST */
.toast {
  position: fixed;
  top: 90px;
  right: 2rem;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(18px);
  border: 1px solid rgba(76,124,42,0.15);
  padding: 1rem 1.5rem;
  border-radius: 1.2rem;
  box-shadow: 0 20px 50px rgba(54,87,21,0.12);
  display: flex;
  gap: 0.6rem;
  font-weight: 600;
}

.toast-success { color: #4c7c2a; }
.toast-error { color: #991b1b; }

/* ORDERS GRID */
.orders-grid {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

/* ORDER CARD (GLASS STYLE) */
.order-card {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(76,124,42,0.12);
  backdrop-filter: blur(18px);
  border-radius: 1.7rem;
  padding: 1.5rem;
  transition: 0.25s ease;
  box-shadow: 0 18px 50px rgba(54,87,21,0.08);
}

.order-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 24px 60px rgba(54,87,21,0.12);
}

.order-card--cancelled {
  opacity: 0.8;
}

.order-card--completed {
  border-color: rgba(76,124,42,0.25);
}

/* HEADER INSIDE CARD */
.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.2rem;
}

.order-number {
  font-weight: 800;
}

.order-date {
  font-size: 0.8rem;
  color: #5d6b52;
}

/* STATUS */
.status-badge {
  border-radius: 999px;
  padding: 0.35rem 0.8rem;
  font-size: 0.75rem;
  font-weight: 800;
  display: flex;
  gap: 0.4rem;
  align-items: center;
  background: rgba(255,255,255,0.7);
  border: 1px solid rgba(76,124,42,0.15);
}

.status-created { color: #92400e; }
.status-confirmed { color: #4c7c2a; }
.status-inprogress { color: #1e40af; }
.status-completed { color: #065f46; }
.status-cancelled { color: #991b1b; }

/* CONTENT */
.card-body {
  border-top: 1px solid rgba(76,124,42,0.12);
  padding-top: 1rem;
}

.order-content {
  background: rgba(249,250,251,0.6);
  border-radius: 1rem;
  padding: 1rem;
}

/* ITEMS */
.item-row {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}

.item-name {
  font-weight: 600;
  color: #2f3b2a;
}

.item-price {
  font-weight: 800;
  color: #3f4a2f;
}

/* TOTAL */
.total-value {
  font-size: 1.2rem;
  font-weight: 900;
  color: #4c7c2a;
}

/* FOOTER */
.card-footer {
  margin-top: 1.2rem;
  text-align: right;
}

/* BUTTON */
.btn-delivered {
  border-radius: 999px;
  padding: 0.7rem 1.4rem;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
  border: none;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(76,124,42,0.25);
}

/* EMPTY STATE */
.empty-state {
  background: rgba(255,255,255,0.78);
  backdrop-filter: blur(18px);
  border: 1px solid rgba(76,124,42,0.12);
  border-radius: 1.7rem;
  padding: 4rem 2rem;
  text-align: center;
}

/* LOADING */
.loading-spinner {
  border: 3px solid rgba(76,124,42,0.2);
  border-top-color: #4c7c2a;
  border-radius: 50%;
}

/* MODAL */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-template {
  width: 600px;
  border-radius: 1.7rem;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(18px);
  border: 1px solid rgba(76,124,42,0.15);
  padding: 2.5rem;
}

/* TEMPLATE BUTTONS */
.btn-checkout-template {
  border-radius: 999px;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
  border: none;
  font-weight: 800;
}

.btn-delete-template {
  border-radius: 999px;
  background: #fee2e2;
  color: #991b1b;
  border: none;
}

/* ANIMATION */
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
