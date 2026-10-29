<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'
import { StarIcon } from '@/assets/icons/png'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  if (store.state.suppliers.length === 0) {
    await store.fetchSuppliers()
  }
})

const selectedSuppliers = computed(() =>
  store.state.suppliers.filter((supplier) => store.state.comparisonSupplierIds.includes(supplier.id)),
)

const allSuppliers = computed(() => store.state.suppliers)

const comparisonRows = computed(() => [
  { label: 'Рейтинг', getValue: (supplier: any) => supplier.rating.toFixed(1) },
  { label: 'Регион', getValue: (supplier: any) => supplier.region || 'Не указан' },
  { label: 'Город', getValue: (supplier: any) => supplier.city || 'Не указан' },
  { label: 'Товаров', getValue: (supplier: any) => String(supplier.products.length) },
  { label: 'Отзывы', getValue: (supplier: any) => String(supplier.reviews) },
  { label: 'Описание', getValue: (supplier: any) => supplier.description },
])
</script>

<template>
  <main class="compare-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Сравнение поставщиков</p>
        <h1>Сравните поставщиков по ключевым параметрам</h1>
        <p>Выбранные поставщики подтягиваются из каталога. Можно быстро снять или добавить новых.</p>
      </div>
      <button class="ghost-btn" @click="store.clearComparison()">Очистить сравнение</button>
    </section>

    <div v-if="selectedSuppliers.length === 0" class="empty-card">
      <p>Пока нет выбранных поставщиков. Откройте каталог и нажмите «Сравнить».</p>
      <router-link to="/catalog" class="primary-btn">Перейти в каталог</router-link>
    </div>

    <template v-else>
      <div class="supplier-strip">
        <article v-for="supplier in selectedSuppliers" :key="supplier.id" class="supplier-card">
          <div class="supplier-top">
            <div>
              <h2>{{ supplier.name }}</h2>
              <p>{{ supplier.locations || 'Локация не указана' }}</p>
            </div>
            <button class="remove-btn" @click="store.toggleComparison(supplier.id)">Удалить</button>
          </div>
          <div class="supplier-meta">
            <span class="rating">
              <img :src="StarIcon" alt="" class="rating-icon" aria-hidden="true" />
              {{ supplier.rating.toFixed(1) }}
            </span>
            <span>{{ supplier.products.length }} товаров</span>
          </div>
        </article>
      </div>

      <section class="compare-table">
        <div class="table-head">
          <div>Параметр</div>
          <div v-for="supplier in selectedSuppliers" :key="supplier.id">{{ supplier.name }}</div>
        </div>

        <div v-for="row in comparisonRows" :key="row.label" class="table-row">
          <div class="label-cell">{{ row.label }}</div>
          <div v-for="supplier in selectedSuppliers" :key="`${row.label}-${supplier.id}`" class="value-cell">
            {{ row.getValue(supplier) }}
          </div>
        </div>
      </section>
    </template>

    <aside class="picker-card">
      <h2>Каталог для сравнения</h2>
      <div class="picker-list">
        <button
          v-for="supplier in allSuppliers"
          :key="supplier.id"
          class="picker-item"
          :class="{ active: store.state.comparisonSupplierIds.includes(supplier.id) }"
          @click="store.toggleComparison(supplier.id)"
        >
          <span>{{ supplier.name }}</span>
          <span>{{ supplier.region }}</span>
        </button>
      </div>
    </aside>
  </main>
</template>

<style scoped>
.compare-page {
  display: grid;
  gap: 1rem;
  padding-bottom: 2rem;
}

.hero,
.supplier-card,
.compare-table,
.picker-card,
.empty-card {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(76, 124, 42, 0.14);
  border-radius: 1.5rem;
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.1);
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem;
}

.eyebrow {
  margin: 0 0 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #5d6b52;
  font-size: 0.75rem;
}

h1,
h2 {
  margin: 0;
}

.hero p,
.supplier-card p {
  color: #5d6b52;
}

.ghost-btn,
.remove-btn,
.primary-btn {
  border-radius: 999px;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(76, 124, 42, 0.16);
  background: rgba(255, 255, 255, 0.9);
  color: #3f4a2f;
  cursor: pointer;
}

.primary-btn {
  display: inline-flex;
  justify-content: center;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  border: none;
}

.supplier-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.supplier-card {
  padding: 1rem;
}

.supplier-top {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.supplier-meta {
  display: flex;
  gap: 1rem;
  color: #3f4a2f;
  font-weight: 700;
}

.rating {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.rating-icon {
  width: 16px;
  height: 16px;
  object-fit: contain;
  display: block;
}

.compare-table {
  overflow: hidden;
}

.table-head,
.table-row {
  display: grid;
  grid-template-columns: 180px repeat(auto-fit, minmax(140px, 1fr));
}

.table-head > div,
.table-row > div {
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(76, 124, 42, 0.1);
}

.table-head {
  background: rgba(236, 243, 230, 0.8);
  font-weight: 800;
}

.label-cell {
  font-weight: 700;
  color: #3f4a2f;
}

.value-cell {
  color: #20311c;
}

.picker-card {
  padding: 1rem;
}

.picker-list {
  display: grid;
  gap: 0.5rem;
  margin-top: 1rem;
}

.picker-item {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(76, 124, 42, 0.14);
  background: rgba(255, 255, 255, 0.85);
  cursor: pointer;
}

.picker-item.active {
  background: rgba(191, 229, 158, 0.4);
  border-color: rgba(76, 124, 42, 0.3);
}

.empty-card {
  padding: 2rem;
  text-align: center;
}

@media (max-width: 900px) {
  .hero,
  .supplier-top {
    display: grid;
  }

  .table-head,
  .table-row {
    grid-template-columns: 1fr;
  }
}
</style>
