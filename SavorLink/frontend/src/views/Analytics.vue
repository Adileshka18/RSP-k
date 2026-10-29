<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  if (authStore.user?.role === 'SUPPLIER') {
    await Promise.all([store.fetchSupplierOrders(), store.fetchMyProducts()])
  } else {
    await Promise.all([store.fetchMyOrders(), store.fetchFavoriteProducts(), store.fetchFavoriteSuppliers()])
  }
})

const orders = computed(() =>
  authStore.user?.role === 'SUPPLIER' ? store.state.supplierOrders : store.state.myOrders,
)

const totalRevenue = computed(() =>
  orders.value.reduce((sum, order) => sum + Number(order.total_amount || 0), 0),
)

const completedOrders = computed(() =>
  orders.value.filter((order) => order.status === 'COMPLETED').length,
)

const activeOrders = computed(() =>
  orders.value.filter((order) => ['CREATED', 'CONFIRMED', 'IN_PROGRESS'].includes(order.status)).length,
)

const favoriteSuppliers = computed(() => store.state.favoriteSuppliers.length)
const favoriteProducts = computed(() => store.state.favoriteProducts.length)

const topProducts = computed(() => {
  const map = new Map<string, { name: string; qty: number; amount: number }>()

  for (const order of orders.value) {
    for (const item of order.items) {
      const name = item.product?.name || `Товар #${item.product_id}`
      const current = map.get(name) ?? { name, qty: 0, amount: 0 }
      current.qty += item.quantity
      current.amount += Number(item.price) * item.quantity
      map.set(name, current)
    }
  }

  return Array.from(map.values())
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 5)
})
</script>

<template>
  <main class="analytics-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Аналитика</p>
        <h1>{{ authStore.user?.role === 'SUPPLIER' ? 'Показатели поставщика' : 'Показатели покупателя' }}</h1>
        <p>Ключевые цифры по заказам, позициям и избранному в одном дашборде.</p>
      </div>
      <div class="hero-card">
        <span>Всего заказов</span>
        <strong>{{ orders.length }}</strong>
      </div>
    </section>

    <section class="metrics">
      <article class="metric-card">
        <span>Оборот</span>
        <strong>{{ totalRevenue.toFixed(0) }} ₽</strong>
      </article>
      <article class="metric-card">
        <span>Завершено</span>
        <strong>{{ completedOrders }}</strong>
      </article>
      <article class="metric-card">
        <span>В работе</span>
        <strong>{{ activeOrders }}</strong>
      </article>
      <article class="metric-card">
        <span>Избранное</span>
        <strong>{{ favoriteSuppliers + favoriteProducts }}</strong>
      </article>
    </section>

    <div class="content-grid">
      <section class="panel">
        <h2>Топ позиций</h2>
        <div class="list">
          <div v-for="item in topProducts" :key="item.name" class="list-row">
            <span>{{ item.name }}</span>
            <strong>{{ item.amount.toFixed(0) }} ₽</strong>
          </div>
        </div>
      </section>

      <section class="panel">
        <h2>Краткая сводка</h2>
        <p v-if="authStore.user?.role === 'SUPPLIER'">
          У вас {{ orders.length }} заказов от покупателей. Следите за активными запросами и
          денежным потоком.
        </p>
        <p v-else>
          У вас {{ favoriteSuppliers }} избранных поставщиков и {{ favoriteProducts }} избранных
          товаров. Используйте аналитику, чтобы отслеживать самые нужные позиции.
        </p>
      </section>
    </div>
  </main>
</template>

<style scoped>
.analytics-page {
  display: grid;
  gap: 1rem;
  padding-bottom: 2rem;
}

.hero,
.metric-card,
.panel {
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

.hero-card {
  min-width: 170px;
  display: grid;
  align-content: center;
  justify-items: end;
}

.hero-card strong {
  font-size: 1.8rem;
  color: #4c7c2a;
}

.metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.metric-card {
  padding: 1rem;
  display: grid;
  gap: 0.35rem;
}

.metric-card span,
.panel p {
  color: #5d6b52;
}

.metric-card strong {
  font-size: 1.5rem;
  color: #20311c;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.panel {
  padding: 1.2rem;
}

.list {
  display: grid;
  gap: 0.6rem;
}

.list-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid rgba(76, 124, 42, 0.1);
}

.list-row:last-child {
  border-bottom: none;
}

@media (max-width: 900px) {
  .hero,
  .content-grid {
    display: grid;
    grid-template-columns: 1fr;
  }

  .metrics {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
