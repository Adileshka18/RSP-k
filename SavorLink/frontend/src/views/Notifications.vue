<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/apiClient'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

type NotificationItem = {
  id: string
  title: string
  text: string
  kind: 'order' | 'message' | 'system'
  date: string
}

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()
const notifications = ref<NotificationItem[]>([])
const loading = ref(false)

const formatDate = (value: string) =>
  new Date(value).toLocaleString('ru-RU', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })

const buildOrderNotifications = () => {
  const source = authStore.user?.role === 'SUPPLIER' ? store.state.supplierOrders : store.state.myOrders

  return source.slice(0, 8).map((order) => ({
    id: `order-${order.id}`,
    title: `Заказ #${order.id}`,
    text: `Статус: ${order.status}. Сумма: ${order.total_amount ?? 0} ₽.`,
    kind: 'order' as const,
    date: order.created_at,
  }))
}

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  loading.value = true
  try {
    if (authStore.user?.role === 'SUPPLIER') {
      await store.fetchSupplierOrders()
    } else {
      await store.fetchMyOrders()
    }

    const chatsResponse = await api.get('/chats')
    const chatNotifications = (chatsResponse.data || []).slice(0, 4).map((chat: any) => ({
      id: `chat-${chat.id}`,
      title: `Чат #${chat.id}`,
      text: chat.last_message?.content ? `Последнее сообщение: ${chat.last_message.content}` : 'В чате пока нет сообщений.',
      kind: 'message' as const,
      date: chat.last_message?.created_at || chat.created_at,
    }))

    notifications.value = [
      {
        id: 'system-1',
        title: 'Система',
        text: 'Все основные уведомления теперь собираются в одном месте.',
        kind: 'system',
        date: new Date().toISOString(),
      },
      ...buildOrderNotifications(),
      ...chatNotifications,
    ].sort((a, b) => +new Date(b.date) - +new Date(a.date))
  } finally {
    loading.value = false
  }
})

const badgeLabel = {
  order: 'Заказ',
  message: 'Чат',
  system: 'Система',
}
</script>

<template>
  <main class="notifications-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Уведомления</p>
        <h1>Лента событий</h1>
        <p>Здесь собраны заказы, новые сообщения и системные подсказки.</p>
      </div>
      <router-link to="/chat" class="primary-btn">Перейти в чат</router-link>
    </section>

    <div v-if="loading" class="state-box">Загрузка уведомлений...</div>

    <div v-else-if="notifications.length === 0" class="state-box">
      У вас пока нет уведомлений.
    </div>

    <div v-else class="list">
      <article v-for="item in notifications" :key="item.id" class="notify-card">
        <div class="notify-head">
          <span class="badge" :class="item.kind">{{ badgeLabel[item.kind] }}</span>
          <time>{{ formatDate(item.date) }}</time>
        </div>
        <h2>{{ item.title }}</h2>
        <p>{{ item.text }}</p>
      </article>
    </div>
  </main>
</template>

<style scoped>
.notifications-page {
  display: grid;
  gap: 1rem;
  padding-bottom: 2rem;
}

.hero,
.notify-card,
.state-box {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(76, 124, 42, 0.14);
  border-radius: 1.5rem;
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.1);
}

.hero {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.eyebrow {
  margin: 0 0 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #5d6b52;
  font-size: 0.75rem;
}

.primary-btn {
  display: inline-flex;
  align-self: center;
  justify-content: center;
  border-radius: 999px;
  padding: 0.85rem 1.2rem;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  font-weight: 800;
}

.state-box {
  padding: 1.25rem;
}

.list {
  display: grid;
  gap: 0.85rem;
}

.notify-card {
  padding: 1.1rem 1.2rem;
}

.notify-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  color: #5d6b52;
  font-size: 0.85rem;
}

.badge {
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  font-weight: 700;
}

.badge.order {
  background: #ecfdf5;
  color: #166534;
}

.badge.message {
  background: #eff6ff;
  color: #1d4ed8;
}

.badge.system {
  background: #fef3c7;
  color: #92400e;
}

.notify-card h2 {
  margin: 0.65rem 0 0.3rem;
  font-size: 1rem;
}

.notify-card p {
  margin: 0;
  color: #5d6b52;
}

@media (max-width: 900px) {
  .hero {
    display: grid;
  }
}
</style>
