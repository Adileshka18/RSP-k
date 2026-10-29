<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore, type Product, type Supplier } from '@/stores/shopStore'
import { AddIcon, DeleteIcon, DocumentIcon, MinusIcon, StarIcon } from '@/assets/icons/png'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

const activeTab = ref<'products' | 'suppliers'>('products')
const selectedProduct = ref<Product | null>(null)
const quantity = ref(1)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  await Promise.all([store.fetchFavoriteProducts(), store.fetchFavoriteSuppliers()])
})

const suppliers = computed(() => store.state.favoriteSuppliers)
const products = computed(() => store.state.favoriteProducts)

const openProduct = (product: Product) => {
  selectedProduct.value = product
  quantity.value = product.min_order_qty || 1
}

const closeProduct = () => {
  selectedProduct.value = null
}

const addProductToCart = async () => {
  if (!selectedProduct.value) return
  await store.addToCart(selectedProduct.value, quantity.value)
  closeProduct()
}

const removeSupplier = async (supplier: Supplier) => {
  await store.toggleFavoriteSupplier(supplier)
}
</script>

<template>
  <main class="favorites-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Избранное</p>
        <h1>Избранные товары и поставщики</h1>
        <p>Товары и поставщики собраны в одном месте, с быстрым переходом в карточку и удалением.</p>
      </div>
    </section>

    <div class="tabs">
      <button class="tab" :class="{ active: activeTab === 'products' }" @click="activeTab = 'products'">
        Избранные товары
      </button>
      <button class="tab" :class="{ active: activeTab === 'suppliers' }" @click="activeTab = 'suppliers'">
        Избранные поставщики
      </button>
    </div>

    <section v-if="activeTab === 'products'" class="section">
      <div v-if="products.length === 0" class="empty-card">
        Пока нет избранных товаров.
        <router-link to="/catalog" class="primary-btn">Перейти в каталог</router-link>
      </div>

      <div v-else class="products-grid">
        <article v-for="product in products" :key="product.id" class="product-card">
          <div class="product-image" @click="openProduct(product)">
            <img :src="DocumentIcon" alt="" class="product-image-icon" aria-hidden="true" />
            <span v-if="product.category" class="badge">{{ product.category.name }}</span>
          </div>
          <div class="product-body">
            <h2 @click="openProduct(product)">{{ product.name }}</h2>
            <p class="supplier" v-if="product.enterprise" @click="router.push(`/suppliers/${product.enterprise.id}`)">
              {{ product.enterprise.short_name }}
            </p>
            <p class="description">{{ product.description }}</p>
            <div class="price-row">
              <strong>{{ Number(product.price).toFixed(0) }} ₽/кг</strong>
              <span>На складе: {{ product.quantity_in_stock ?? 0 }} кг</span>
            </div>
            <div class="actions">
              <button class="primary-btn" @click="openProduct(product)">В корзину</button>
              <button class="secondary-btn" @click="store.toggleFavoriteProduct(product)">Убрать</button>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section v-else class="section">
      <div v-if="suppliers.length === 0" class="empty-card">
        Пока нет избранных поставщиков.
        <router-link to="/catalog" class="primary-btn">Перейти в каталог</router-link>
      </div>

      <div v-else class="suppliers-grid">
        <article v-for="supplier in suppliers" :key="supplier.id" class="supplier-card">
          <div class="supplier-head" @click="router.push(`/suppliers/${supplier.id}`)">
            <div class="avatar">{{ supplier.name.charAt(0) }}</div>
            <div>
              <h2>{{ supplier.name }}</h2>
              <p>{{ supplier.region }}{{ supplier.city ? ` · ${supplier.city}` : '' }}</p>
            </div>
          </div>
          <div class="supplier-meta">
            <span class="rating">
              <img :src="StarIcon" alt="" class="rating-icon" aria-hidden="true" />
              {{ supplier.rating.toFixed(1) }}
            </span>
            <span>{{ supplier.products.length }} товаров</span>
          </div>
          <div class="supplier-actions">
            <button class="primary-btn" @click="router.push(`/suppliers/${supplier.id}`)">Открыть</button>
            <button class="secondary-btn" @click="removeSupplier(supplier)">
              <img :src="DeleteIcon" alt="" class="action-icon" aria-hidden="true" />
              Удалить
            </button>
          </div>
        </article>
      </div>
    </section>
  </main>

  <teleport to="body">
    <div v-if="selectedProduct" class="modal-backdrop" @click.self="closeProduct">
      <div class="modal-card">
        <h2>{{ selectedProduct.name }}</h2>
        <p>{{ selectedProduct.description || 'Описание отсутствует' }}</p>
        <div class="qty-row">
          <button class="qty-btn" @click="quantity = Math.max(1, quantity - 1)">
            <img :src="MinusIcon" alt="" class="qty-icon" aria-hidden="true" />
          </button>
          <span>{{ quantity }} кг</span>
          <button class="qty-btn" @click="quantity += 1">
            <img :src="AddIcon" alt="" class="qty-icon" aria-hidden="true" />
          </button>
        </div>
        <div class="modal-total">
          {{ (Number(selectedProduct.price) * quantity).toFixed(0) }} ₽
        </div>
        <div class="actions">
          <button class="primary-btn" @click="addProductToCart">Добавить</button>
          <button class="secondary-btn" @click="closeProduct">Отмена</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
.favorites-page {
  display: grid;
  gap: 1rem;
  padding-bottom: 2rem;
}

.hero,
.section,
.empty-card,
.product-card,
.supplier-card {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(76, 124, 42, 0.14);
  border-radius: 1.5rem;
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.1);
}

.product-image-icon,
.qty-icon,
.action-icon {
  display: block;
  object-fit: contain;
}

.product-image-icon {
  width: 40px;
  height: 40px;
}

.qty-icon,
.action-icon {
  width: 18px;
  height: 18px;
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

.hero {
  padding: 1.5rem;
}

.eyebrow {
  margin: 0 0 0.3rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #5d6b52;
  font-size: 0.75rem;
}

.hero h1,
.section h2 {
  margin: 0;
}

.hero p {
  margin: 0.5rem 0 0;
  color: #5d6b52;
}

.tabs {
  display: flex;
  gap: 0.75rem;
}

.tab {
  border: 1px solid rgba(76, 124, 42, 0.16);
  background: rgba(255, 255, 255, 0.9);
  border-radius: 999px;
  padding: 0.8rem 1rem;
  cursor: pointer;
  font-weight: 700;
}

.tab.active {
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  border-color: transparent;
}

.section {
  padding: 1rem;
}

.empty-card {
  padding: 2rem;
  text-align: center;
  color: #5d6b52;
  display: grid;
  gap: 0.75rem;
}

.products-grid,
.suppliers-grid {
  display: grid;
  gap: 1rem;
}

.products-grid {
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
}

.suppliers-grid {
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
}

.product-card {
  overflow: hidden;
}

.product-image {
  min-height: 160px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #dcefd0, #bedfbe);
  position: relative;
  cursor: pointer;
}

.product-image span:first-child {
  font-size: 2.4rem;
}

.badge {
  position: absolute;
  right: 0.75rem;
  bottom: 0.75rem;
  padding: 0.3rem 0.6rem;
  border-radius: 999px;
  background: rgba(76, 124, 42, 0.85);
  color: #fff;
  font-size: 0.75rem;
}

.product-body {
  padding: 1rem;
}

.product-body h2 {
  margin: 0;
  font-size: 1.05rem;
  cursor: pointer;
}

.supplier,
.description,
.price-row span,
.supplier-head p {
  color: #5d6b52;
}

.supplier {
  cursor: pointer;
}

.description {
  margin: 0.5rem 0;
}

.price-row {
  display: grid;
  gap: 0.3rem;
}

.actions,
.supplier-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.85rem;
}

.supplier-card {
  padding: 1rem;
}

.supplier-head {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 0.8rem;
  align-items: center;
  cursor: pointer;
}

.avatar {
  width: 56px;
  height: 56px;
  border-radius: 1rem;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #bfe59e, #a5db74);
  color: #20311c;
  font-weight: 900;
}

.supplier-head h2 {
  margin: 0;
  font-size: 1rem;
}

.supplier-meta {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.85rem;
  color: #3f4a2f;
  font-weight: 700;
}

.primary-btn,
.secondary-btn,
.qty-btn {
  border-radius: 999px;
  border: 1px solid rgba(76, 124, 42, 0.16);
  font-weight: 700;
  cursor: pointer;
}

.primary-btn {
  flex: 1;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  padding: 0.8rem 1rem;
}

.secondary-btn {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  color: #3f4a2f;
  padding: 0.8rem 1rem;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(14, 25, 9, 0.45);
  display: grid;
  place-items: center;
  padding: 1rem;
  z-index: 2000;
}

.modal-card {
  width: min(520px, 100%);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1.5rem;
  padding: 1.4rem;
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.2);
}

.qty-row,
.modal-total {
  margin-top: 1rem;
}

.qty-row {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.qty-btn {
  width: 40px;
  height: 40px;
}

.modal-total {
  font-size: 1.4rem;
  font-weight: 900;
  color: #4c7c2a;
}

@media (max-width: 900px) {
  .tabs,
  .actions,
  .supplier-actions {
    display: grid;
  }

  .supplier-head {
    grid-template-columns: 1fr;
  }
}
</style>
