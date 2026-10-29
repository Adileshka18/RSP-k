<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

const search = ref('')
const selectedCategoryId = ref<number | null>(null)
const selectedRegion = ref('all')
const selectedCity = ref('all')

onMounted(async () => {
  await store.fetchSuppliers()
  if (authStore.token) {
    await Promise.all([
      store.fetchFavoriteProducts(),
      store.fetchFavoriteSuppliers(),
    ])
  }
})

const categories = computed(() => {
  const map = new Map<number, string>()

  for (const supplier of store.state.suppliers) {
    for (const product of supplier.products) {
      if (product.category?.id) {
        map.set(product.category.id, product.category.name)
      }
    }
  }

  return Array.from(map.entries()).map(([id, name]) => ({ id, name }))
})

const regions = computed(() =>
  Array.from(new Set(store.state.suppliers.map((s) => s.region).filter(Boolean) as string[]))
)

const availableCities = computed(() => {
  const list =
    selectedRegion.value === 'all'
      ? store.state.suppliers
      : store.state.suppliers.filter(s => s.region === selectedRegion.value)

  return Array.from(new Set(list.map((s) => s.city).filter(Boolean) as string[]))
})

watch(selectedRegion, () => {
  if (!availableCities.value.includes(selectedCity.value)) {
    selectedCity.value = 'all'
  }
})

const filteredSuppliers = computed(() => {
  const term = search.value.toLowerCase()

  return store.state.suppliers.filter(s => {
    const matchSearch =
      !term ||
      s.name.toLowerCase().includes(term) ||
      s.products.some(p => p.name.toLowerCase().includes(term))

    const matchCategory =
      selectedCategoryId.value === null ||
      s.products.some(p => p.category?.id === selectedCategoryId.value)

    const matchRegion =
      selectedRegion.value === 'all' || s.region === selectedRegion.value

    const matchCity =
      selectedCity.value === 'all' || s.city === selectedCity.value

    return matchSearch && matchCategory && matchRegion && matchCity
  })
})

const hasActiveFilters = computed(
  () =>
    search.value ||
    selectedCategoryId.value !== null ||
    selectedRegion.value !== 'all' ||
    selectedCity.value !== 'all'
)

const resetFilters = () => {
  search.value = ''
  selectedCategoryId.value = null
  selectedRegion.value = 'all'
  selectedCity.value = 'all'
}
</script>

<template>
  <main class="catalog-page">

    <!-- КНОПКИ -->
    <div class="top-bar">
      <router-link to="/compare" class="compare-link">
        Сравнить ({{ store.state.comparisonSupplierIds.length }})
      </router-link>

      <button
        class="reset-btn"
        @click="resetFilters"
        :disabled="!hasActiveFilters"
      >
        Сбросить
      </button>
    </div>

    <!-- ФИЛЬТРЫ -->
    <section class="filters">
      <input v-model="search" placeholder="Поиск..." />

      <select v-model="selectedCategoryId">
        <option :value="null">Категории</option>
        <option v-for="c in categories" :key="c.id" :value="c.id">
          {{ c.name }}
        </option>
      </select>

      <select v-model="selectedRegion">
        <option value="all">Регион</option>
        <option v-for="r in regions" :key="r">
          {{ r }}
        </option>
      </select>

      <select v-model="selectedCity">
        <option value="all">Город</option>
        <option v-for="c in availableCities" :key="c">
          {{ c }}
        </option>
      </select>
    </section>

    <!-- КАРТОЧКИ -->
    <section class="catalog-grid">
      <article
        v-for="supplier in filteredSuppliers"
        :key="supplier.id"
        class="card"
      >

        <!-- ❤️ -->
        <button
          class="fav"
          @click="store.toggleFavoriteSupplier(supplier)"
        >
          {{ store.isSupplierFavorite(supplier.id) ? '❤️' : '🤍' }}
        </button>

        <div class="body" @click="router.push(`/suppliers/${supplier.id}`)">
          <div class="avatar">
            {{ supplier.name[0] }}
          </div>

          <h3>{{ supplier.name }}</h3>

          <div class="rating">
            ⭐ {{ supplier.rating.toFixed(1) }}
          </div>
        </div>

        <button
          class="btn"
          @click="router.push(`/suppliers/${supplier.id}`)"
        >
          Подробнее
        </button>
      </article>
    </section>

  </main>
</template>

<style scoped>
.catalog-page {
  display: grid;
  gap: 1rem;
}

/* TOP */
.top-bar {
  display: flex;
  justify-content: space-between;
}

.compare-link {
  padding: 0.6rem 1rem;
  border-radius: 999px;
  background: #6da13d;
  color: white;
}

.reset-btn {
  padding: 0.6rem 1rem;
  border-radius: 999px;
  border: 1px solid #ccc;
}

/* FILTERS */
.filters {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.filters input,
.filters select {
  padding: 0.6rem;
  border-radius: 10px;
  border: 1px solid #ddd;
}

/* GRID */
.catalog-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

/* CARD */
.card {
  position: relative;
  padding: 1rem;
  border-radius: 16px;
  background: white;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);

  display: flex;
  flex-direction: column;
  justify-content: space-between;

  transition: 0.25s;
}

.card:hover {
  transform: translateY(-5px);
}

/* FAV */
.fav {
  position: absolute;
  top: 10px;
  right: 10px;
  border: none;
  background: white;
  border-radius: 50%;
  width: 35px;
  height: 35px;
  cursor: pointer;
}

/* BODY */
.body {
  text-align: center;
  cursor: pointer;
}

.avatar {
  width: 70px;
  height: 70px;
  margin: auto;
  border-radius: 12px;
  background: #a5db74;
  display: grid;
  place-items: center;
  font-weight: bold;
  font-size: 20px;
}

h3 {
  margin: 10px 0;
}

.rating {
  color: #666;
}

/* BTN */
.btn {
  margin-top: 10px;
  padding: 0.6rem;
  border-radius: 999px;
  border: none;
  background: #4c7c2a;
  color: white;
  cursor: pointer;
}
</style>
