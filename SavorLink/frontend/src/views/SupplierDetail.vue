<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore, type Product } from '@/stores/shopStore'
import {
  AddIcon,
  CalendarIcon,
  CloseIcon,
  DocumentIcon,
  LocationIcon,
  MinusIcon,
  NotificationIcon,
  StarIcon,
} from '@/assets/icons/png'

const route = useRoute()
const router = useRouter()
const store = useShopStore()
const authStore = useAuthStore()

const supplierId = computed(() => Number(route.params.id))
const supplier = computed(() => store.state.currentSupplier)

const showReviews = ref(true)
const showReviewModal = ref(false)
const selectedProduct = ref<Product | null>(null)
const quantity = ref(1)
const ratingValue = ref(5)
const reviewComment = ref('')
const isSubmittingReview = ref(false)

const isBuyer = computed(() => authStore.user?.role === 'BUYER')

onMounted(async () => {
  if (supplierId.value) {
    await Promise.all([store.fetchSupplierDetail(supplierId.value), store.fetchSupplierReviews(supplierId.value)])
  }
})

const openProductModal = (product: Product) => {
  selectedProduct.value = product
  quantity.value = product.min_order_qty || 1
}

const closeProductModal = () => {
  selectedProduct.value = null
}

const totalForProduct = computed(() =>
  selectedProduct.value ? Number(selectedProduct.value.price) * quantity.value : 0,
)

const addToCart = async () => {
  if (!selectedProduct.value) return
  await store.addToCart(selectedProduct.value, quantity.value)
  closeProductModal()
}

const submitReview = async () => {
  if (!supplier.value || isSubmittingReview.value) return

  isSubmittingReview.value = true
  try {
    await store.submitReview(supplier.value.id, ratingValue.value, reviewComment.value)
    reviewComment.value = ''
    ratingValue.value = 5
    showReviewModal.value = false
    showReviews.value = true
  } catch (error: any) {
    alert(error?.response?.data?.detail || error?.message || 'Не удалось отправить отзыв')
  } finally {
    isSubmittingReview.value = false
  }
}

const formatDate = (value: string) =>
  new Date(value).toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
</script>

<template>
  <main class="supplier-page">
    <div v-if="store.state.loading" class="status-box">Загрузка данных поставщика...</div>
    <div v-else-if="store.state.error" class="status-box status-box--error">{{ store.state.error }}</div>

    <template v-else-if="supplier">
      <section class="hero-card">
        <div class="hero-main">
          <div class="avatar">{{ supplier.name.charAt(0) }}</div>
          <div>
            <p class="eyebrow">Поставщик</p>
            <h1>{{ supplier.name }}</h1>
            <p class="subline">{{ supplier.company }}</p>
            <p class="supplier-desc" v-if="supplier.description">{{ supplier.description }}</p>
            <div class="meta">
              <span class="meta-item">
                <img :src="StarIcon" alt="" class="meta-icon" aria-hidden="true" />
                {{ supplier.rating.toFixed(1) }} ({{ supplier.reviews }})
              </span>
              <span class="meta-item">
                <img :src="LocationIcon" alt="" class="meta-icon" aria-hidden="true" />
                {{ supplier.locations }}
              </span>
              <span class="meta-item">
                <img :src="CalendarIcon" alt="" class="meta-icon" aria-hidden="true" />
                с {{ supplier.since }}
              </span>
            </div>
          </div>
        </div>

        <div class="hero-actions">
          <button 
            v-if="authStore.user && supplier.users?.[0] && supplier.users[0].id !== authStore.user.id" 
            class="action-btn action-btn--chat" 
            @click="router.push(`/chat?userId=${supplier.users[0].id}`)"
          >
            <img :src="NotificationIcon" alt="" class="btn-icon-chat" />
            Написать
          </button>
          <button v-if="isBuyer" class="action-btn action-btn--primary" @click="showReviewModal = true">
            Оценить
          </button>
          <button class="action-btn" @click="store.toggleFavoriteSupplier(supplier)">
            {{ store.isSupplierFavorite(supplier.id) ? 'В избранном' : 'В избранное' }}
          </button>
        </div>
      </section>

      <section class="panel">
        <div class="panel-head">
          <h2>Продукция</h2>
          <button class="link-btn" @click="showReviews = !showReviews">
            {{ showReviews ? 'Скрыть отзывы' : 'Показать отзывы' }}
          </button>
        </div>

        <div class="products-grid">
          <article v-for="product in supplier.products" :key="product.id" class="product-card">
            <div class="product-image">
              <img :src="DocumentIcon" alt="" class="product-image-icon" aria-hidden="true" />
            </div>
            <div class="product-body">
              <h3>{{ product.name }}</h3>
              <p>{{ product.category?.name || 'Без категории' }}</p>
              <div class="product-meta">
                <strong>{{ Number(product.price).toFixed(0) }} ₽/кг</strong>
                <span>Остаток: {{ product.quantity_in_stock ?? 0 }} кг</span>
              </div>
              <div class="product-actions">
                <button class="action-btn action-btn--primary" @click="openProductModal(product)">В корзину</button>
                <button class="action-btn" @click="store.toggleFavoriteProduct(product)">
                  {{ store.isProductFavorite(product.id) ? 'В избранном' : 'В избранное' }}
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section v-if="showReviews" class="panel">
        <h2>Отзывы</h2>
        <div v-if="store.state.supplierReviews.length === 0" class="empty-inline">
          Отзывов пока нет.
        </div>
        <article v-for="review in store.state.supplierReviews" :key="review.id" class="review-card">
          <div class="review-head">
            <div>
              <strong>Покупатель #{{ review.author_user_id }}</strong>
              <div class="review-date">{{ formatDate(review.created_at) }}</div>
            </div>
            <div class="stars">
              <span v-for="index in 5" :key="index" :class="{ active: index <= review.rating }">
                <img :src="StarIcon" alt="" class="star-icon" aria-hidden="true" />
              </span>
            </div>
          </div>
          <p>{{ review.comment || 'Без комментария' }}</p>
        </article>
      </section>
    </template>
  </main>

  <teleport to="body">
    <div v-if="selectedProduct" class="modal-backdrop" @click.self="closeProductModal">
      <div class="modal-card">
        <button class="modal-close" @click="closeProductModal">
          <img :src="CloseIcon" alt="" class="close-icon" aria-hidden="true" />
        </button>
        <h2>{{ selectedProduct.name }}</h2>
        <p>{{ selectedProduct.description || 'Описание отсутствует' }}</p>
        <div class="modal-meta">
          <span>{{ Number(selectedProduct.price).toFixed(0) }} ₽/кг</span>
          <span>Мин. заказ: {{ selectedProduct.min_order_qty || 1 }} кг</span>
        </div>

        <div class="qty-row">
          <button class="qty-btn" @click="quantity = Math.max(1, quantity - 1)">
            <img :src="MinusIcon" alt="" class="qty-icon" aria-hidden="true" />
          </button>
          <span>{{ quantity }} кг</span>
          <button class="qty-btn" @click="quantity += 1">
            <img :src="AddIcon" alt="" class="qty-icon" aria-hidden="true" />
          </button>
        </div>

        <div class="modal-total">{{ totalForProduct.toFixed(0) }} ₽</div>

        <div class="modal-actions">
          <button class="action-btn action-btn--primary" @click="addToCart">Добавить</button>
          <button class="action-btn" @click="closeProductModal">Отмена</button>
        </div>
      </div>
    </div>

    <div v-if="showReviewModal" class="modal-backdrop" @click.self="showReviewModal = false">
      <div class="modal-card">
        <button class="modal-close" @click="showReviewModal = false">
          <img :src="CloseIcon" alt="" class="close-icon" aria-hidden="true" />
        </button>
        <h2>Оставить отзыв</h2>
        <div class="field">
          <label>Оценка</label>
          <select v-model="ratingValue">
            <option :value="5">5</option>
            <option :value="4">4</option>
            <option :value="3">3</option>
            <option :value="2">2</option>
            <option :value="1">1</option>
          </select>
        </div>
        <div class="field">
          <label>Комментарий</label>
          <textarea v-model="reviewComment" rows="4" placeholder="Поделитесь впечатлением"></textarea>
        </div>
        <div class="modal-actions">
          <button class="action-btn action-btn--primary" :disabled="isSubmittingReview" @click="submitReview">
            {{ isSubmittingReview ? 'Отправка...' : 'Отправить' }}
          </button>
          <button class="action-btn" @click="showReviewModal = false">Отмена</button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
.supplier-page {
  display: grid;
  gap: 1rem;
  padding-bottom: 2rem;
}

.status-box,
.hero-card,
.panel,
.review-card {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(76, 124, 42, 0.14);
  border-radius: 1.5rem;
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.1);
}

.status-box {
  padding: 1rem 1.15rem;
}

.status-box--error {
  color: #991b1b;
  background: #fee2e2;
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem;
}

.hero-main {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.avatar {
  width: 76px;
  height: 76px;
  border-radius: 1.25rem;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  font-weight: 900;
  font-size: 1.5rem;
}

.eyebrow,
.subline,
.supplier-desc,
.review-date {
  color: #5d6b52;
}

.supplier-desc {
  margin: 0.5rem 0 0;
  max-width: 600px;
  line-height: 1.4;
}

.eyebrow {
  margin: 0 0 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.75rem;
}

.hero-card h1,
.panel h2 {
  margin: 0;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem 1rem;
  margin-top: 0.6rem;
  color: #3f4a2f;
  font-weight: 700;
}

.meta-item {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.meta-icon,
.close-icon,
.product-image-icon,
.star-icon,
.qty-icon {
  display: block;
  object-fit: contain;
}

.meta-icon {
  width: 16px;
  height: 16px;
}

.close-icon {
  width: 14px;
  height: 14px;
}

.hero-actions {
  display: grid;
  gap: 0.75rem;
  align-content: center;
}

.action-btn,
.link-btn,
.qty-btn {
  border-radius: 999px;
  border: 1px solid rgba(76, 124, 42, 0.16);
  background: rgba(255, 255, 255, 0.92);
  color: #3f4a2f;
  cursor: pointer;
  font-weight: 700;
}

.action-btn {
  padding: 0.8rem 1rem;
}

.action-btn--primary {
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  border: none;
}

.action-btn--chat {
  background: #f0f7eb;
  border-color: rgba(76, 124, 42, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.action-btn--chat:hover {
  background: #e6f0e0;
  border-color: #4c7c2a;
}

.btn-icon-chat {
  width: 18px;
  height: 18px;
  opacity: 0.8;
}

.panel {
  padding: 1.25rem;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.link-btn {
  padding: 0.65rem 1rem;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.product-card {
  overflow: hidden;
  border-radius: 1.3rem;
  border: 1px solid rgba(76, 124, 42, 0.12);
  background: rgba(255, 255, 255, 0.86);
}

.product-image {
  min-height: 150px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #dcefd0, #bedfbe);
  font-size: 2.5rem;
}

.product-image-icon {
  width: 40px;
  height: 40px;
}

.star-icon {
  width: 14px;
  height: 14px;
}

.qty-icon {
  width: 18px;
  height: 18px;
}

.product-body {
  padding: 1rem;
}

.product-body h3 {
  margin: 0 0 0.35rem;
}

.product-body p {
  margin: 0;
  color: #5d6b52;
}

.product-meta {
  display: grid;
  gap: 0.25rem;
  margin-top: 0.75rem;
}

.product-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.85rem;
}

.review-card {
  padding: 1rem;
  margin-top: 0.85rem;
}

.review-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.stars span {
  color: #d1d5db;
}

.stars .active {
  color: #f59e0b;
}

.empty-inline {
  color: #5d6b52;
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
  width: min(560px, 100%);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1.5rem;
  padding: 1.4rem;
  box-shadow: 0 30px 70px rgba(0, 0, 0, 0.2);
  position: relative;
}

.modal-close {
  position: absolute;
  top: 0.9rem;
  right: 0.9rem;
  border: none;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 999px;
  width: 30px;
  height: 30px;
  padding: 0;
  display: grid;
  place-items: center;
  cursor: pointer;
}

.modal-meta,
.qty-row,
.modal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.qty-row {
  align-items: center;
}

.qty-btn {
  width: 40px;
  height: 40px;
}

.modal-total {
  margin-top: 0.75rem;
  font-size: 1.4rem;
  font-weight: 900;
  color: #4c7c2a;
}

.field {
  display: grid;
  gap: 0.35rem;
  margin-top: 0.85rem;
}

select,
textarea {
  width: 100%;
  border-radius: 1rem;
  border: 1px solid rgba(76, 124, 42, 0.16);
  padding: 0.8rem 0.9rem;
}

@media (max-width: 900px) {
  .hero-card,
  .review-head,
  .panel-head {
    display: grid;
  }

  .hero-main {
    display: grid;
  }
}
</style>
