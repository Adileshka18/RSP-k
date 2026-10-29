<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useShopStore } from '@/stores/shopStore'
import { useAuthStore } from '@/stores/authStore'
import api from '@/services/apiClient'
import { AddIcon, CloseIcon, DeleteIcon, DocumentIcon } from '@/assets/icons/png'

const router = useRouter()
const shopStore = useShopStore()
const authStore = useAuthStore()

const products = computed(() => shopStore.state.products)
const isLoading = computed(() => shopStore.state.loading)
const error = computed(() => shopStore.state.error)

const showModal = ref(false)
const isEditing = ref(false)
const currentProduct = ref<any>({
  name: '',
  description: '',
  price: 0,
  min_order_qty: 1,
  quantity_in_stock: 0,
  category_id: null as number | null
})

const categories = ref<{ id: number; name: string }[]>([])

onMounted(async () => {
  if (authStore.user?.role !== 'SUPPLIER') {
    router.push('/')
    return
  }
  await shopStore.fetchMyProducts()
  await fetchCategories()
})

const fetchCategories = async () => {
  try {
    const res = await api.get('/products/categories')
    categories.value = res.data
  } catch (err) {
    console.error('Ошибка при получении категорий:', err)
    // Запасной вариант — категории из БД
    categories.value = [
      { id: 1, name: 'Овощи и зелень' },
      { id: 2, name: 'Мясо и птица' },
      { id: 3, name: 'Молочные продукты' },
      { id: 4, name: 'Бакалея' },
      { id: 5, name: 'Напитки' },
    ]
  }
}

const openCreateModal = () => {
  isEditing.value = false
  currentProduct.value = {
    name: '',
    description: '',
    price: 0,
    min_order_qty: 1,
    quantity_in_stock: 0,
    category_id: categories.value[0]?.id || null
  }
  showModal.value = true
}

const openEditModal = (product: any) => {
  isEditing.value = true
  currentProduct.value = { ...product, category_id: product.category?.id || product.category_id }
  showModal.value = true
}

const handleSave = async () => {
  try {
    if (isEditing.value) {
      await shopStore.updateProduct(currentProduct.value.id, {
        name: currentProduct.value.name,
        description: currentProduct.value.description,
        price: currentProduct.value.price,
        min_order_qty: currentProduct.value.min_order_qty,
        quantity_in_stock: currentProduct.value.quantity_in_stock,
        category_id: currentProduct.value.category_id,
      })
    } else {
      await shopStore.createProduct({
        name: currentProduct.value.name,
        description: currentProduct.value.description,
        price: currentProduct.value.price,
        min_order_qty: currentProduct.value.min_order_qty,
        quantity_in_stock: currentProduct.value.quantity_in_stock,
        category_id: currentProduct.value.category_id,
      })
    }
    showModal.value = false
    // Обновляем список товаров
    await shopStore.fetchMyProducts()
  } catch (err) {
    // Ошибка уже в сторе
    console.error(err)
  }
}

const handleDelete = async (id: number) => {
  if (confirm('Вы уверены, что хотите удалить этот товар?')) {
    await shopStore.deleteProduct(id)
  }
}

</script>

<template>
  <div class="my-products-page">
    <main class="main-content">
      <div class="content-header">
        <h1 class="title">Управление товарами</h1>
        <button @click="openCreateModal" class="btn-add">
          <img :src="AddIcon" alt="" class="btn-icon" aria-hidden="true" />
          Добавить товар
        </button>
      </div>

      <div v-if="isLoading && products.length === 0" class="status-msg">
        Загрузка ваших товаров...
      </div>
      <div v-else-if="error" class="status-msg error">
        {{ error }}
      </div>
      <div v-else-if="products.length === 0" class="empty-state">
        <div class="empty-icon">
          <img :src="DocumentIcon" alt="" class="empty-icon-img" aria-hidden="true" />
        </div>
        <p>У вас пока нет товаров. Самое время создать первый!</p>
        <button @click="openCreateModal" class="btn-add-large">Создать товар</button>
      </div>

      <div v-else class="products-grid">
        <div v-for="product in products" :key="product.id" class="product-card">
          <div class="card-image">
            <img :src="DocumentIcon" alt="" class="card-icon" aria-hidden="true" />
            <span class="card-cat" v-if="product.category">{{ product.category.name }}</span>
          </div>
          <div class="card-info">
            <h3 class="product-name">{{ product.name }}</h3>
            <p class="product-desc">{{ product.description || 'Описание не добавлено' }}</p>
            <div class="product-meta">
              <span class="price">{{ product.price }} ₽/кг</span>
              <span class="stock">На складе: {{ product.quantity_in_stock ?? 0 }} кг</span>
            </div>
            <p class="min-order" v-if="product.min_order_qty">Мин. заказ: {{ product.min_order_qty }} кг</p>
          </div>
          <div class="card-actions">
            <button @click="openEditModal(product)" class="btn-edit">Изменить</button>
            <button @click="handleDelete(product.id)" class="btn-delete">Удалить</button>
          </div>
        </div>
      </div>
    </main>

    <!-- Modal Form -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content">
          <button class="modal-close" @click="showModal = false">
            <img :src="CloseIcon" alt="" class="close-icon" aria-hidden="true" />
          </button>
          <h2 class="modal-title">{{ isEditing ? 'Редактировать товар' : 'Новый товар' }}</h2>
          <form @submit.prevent="handleSave" class="product-form">
            <div class="form-group">
              <label>Название *</label>
              <input v-model="currentProduct.name" type="text" required placeholder="Например: Помидоры Черри" />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Категория *</label>
                <select v-model="currentProduct.category_id" required>
                  <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                    {{ cat.name }}
                  </option>
                </select>
              </div>
              <div class="form-group">
                <label>Цена (₽/кг) *</label>
                <input v-model.number="currentProduct.price" type="number" step="0.01" min="0.01" required />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>Мин. заказ (кг)</label>
                <input v-model.number="currentProduct.min_order_qty" type="number" min="0" />
              </div>
              <div class="form-group">
                <label>В наличии (кг)</label>
                <input v-model.number="currentProduct.quantity_in_stock" type="number" min="0" />
              </div>
            </div>

            <div class="form-group">
              <label>Описание</label>
              <textarea v-model="currentProduct.description" rows="4" placeholder="Расскажите о качестве, происхождении и особенностях товара..."></textarea>
            </div>

            <div v-if="error" class="form-error">{{ error }}</div>

            <div class="modal-actions">
              <button type="button" @click="showModal = false" class="btn-cancel">Отмена</button>
              <button type="submit" class="btn-submit" :disabled="isLoading">
                {{ isLoading ? 'Сохранение...' : (isEditing ? 'Обновить' : 'Создать') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.my-products-page {
  min-height: 100vh;
  font-family: 'Manrope', sans-serif;
  background: transparent;
  color: #20311c;
}

/* MAIN */
.main-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 3rem 1.5rem 6rem;
}

/* HEADER (GLASS STYLE как в системе) */
.content-header {
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

.title {
  font-size: 1.7rem;
  font-weight: 800;
  color: #20311c;
  margin: 0;
}

/* ADD BUTTON (единый стиль) */
.btn-add {
  border-radius: 999px;
  padding: 0.8rem 1.4rem;

  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
  border: none;

  font-weight: 700;
  cursor: pointer;

  display: flex;
  align-items: center;
  gap: 0.5rem;

  box-shadow: 0 10px 25px rgba(76,124,42,0.2);
  transition: 0.2s ease;
}

.btn-icon,
.empty-icon-img,
.card-icon,
.close-icon {
  display: block;
  object-fit: contain;
}

.btn-icon,
.close-icon {
  width: 18px;
  height: 18px;
}

.empty-icon-img {
  width: 72px;
  height: 72px;
  margin: 0 auto;
}

.card-icon {
  width: 40px;
  height: 40px;
}

.btn-add:hover {
  transform: translateY(-2px);
}

/* GRID */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

/* PRODUCT CARD (GLASS SYSTEM) */
.product-card {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(76,124,42,0.16);
  border-radius: 1.7rem;

  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54,87,21,0.08);

  display: flex;
  flex-direction: column;

  transition: 0.25s ease;
}

.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 30px 70px rgba(54,87,21,0.15);
}

/* IMAGE */
.card-image {
  height: 130px;
  border-radius: 1.7rem 1.7rem 0 0;

  background: linear-gradient(135deg, #d4edda, #a8d5b5);

  display: flex;
  align-items: center;
  justify-content: center;

  position: relative;
}

.card-icon {
  font-size: 2.8rem;
}

/* CATEGORY BADGE */
.card-cat {
  position: absolute;
  bottom: 10px;
  right: 10px;

  font-size: 0.7rem;
  font-weight: 700;

  padding: 0.25rem 0.6rem;

  border-radius: 999px;

  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(76,124,42,0.16);
  color: #3f4a2f;
}

/* INFO */
.card-info {
  padding: 1.25rem;
}

.product-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: #20311c;
  margin: 0 0 0.4rem;
}

.product-desc {
  font-size: 0.85rem;
  color: #5d6b52;
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

/* META */
.product-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.3rem;
}

.price {
  font-weight: 900;
  color: #4c7c2a;
}

.stock {
  font-size: 0.85rem;
  color: #5d6b52;
}

.min-order {
  font-size: 0.8rem;
  color: #6b7280;
}

/* ACTIONS */
.card-actions {
  display: flex;
  gap: 0.6rem;
  padding: 0 1.25rem 1.25rem;
}

/* EDIT BUTTON */
.btn-edit {
  flex: 1;

  border-radius: 999px;
  padding: 0.65rem;

  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(76,124,42,0.16);

  color: #3f4a2f;
  font-weight: 700;

  cursor: pointer;
}

/* DELETE */
.btn-delete {
  border-radius: 999px;
  padding: 0.65rem 1rem;

  background: rgba(254,226,226,0.8);
  color: #991b1b;
  border: none;

  font-weight: 700;
  cursor: pointer;
}

/* EMPTY STATE */
.empty-state {
  background: rgba(255,255,255,0.78);
  border: 1px solid rgba(76,124,42,0.16);

  backdrop-filter: blur(18px);

  border-radius: 1.7rem;
  padding: 4rem 2rem;

  text-align: center;
}

.empty-icon {
  font-size: 3.5rem;
}

/* LOADING / ERROR */
.status-msg {
  text-align: center;
  padding: 3rem;
  color: #5d6b52;
}

.status-msg.error {
  color: #991b1b;
}

/* BUTTON LARGE */
.btn-add-large {
  margin-top: 1.5rem;

  border-radius: 999px;
  padding: 1rem 2rem;

  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;

  border: none;
  font-weight: 800;
  cursor: pointer;
}

/* MODAL */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(32, 49, 28, 0.45);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.modal-content {
  width: 100%;
  max-width: 540px;
  position: relative;
  overflow: hidden;

  border-radius: 2.5rem;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow: 
    0 20px 50px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(76, 124, 42, 0.05);

  padding: 3rem 2.5rem 2.5rem;
  animation: modalScaleUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalScaleUp {
  from { opacity: 0; transform: scale(0.9) translateY(30px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.modal-close {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  
  width: 42px;
  height: 42px;
  
  display: flex;
  align-items: center;
  justify-content: center;
  
  background: white;
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 1rem;
  
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.modal-close:hover {
  transform: rotate(90deg);
  background: #fff1f1;
  border-color: #ffcfcf;
}

.modal-title {
  text-align: left;
  font-size: 1.8rem;
  font-weight: 900;
  margin-bottom: 2rem;
  color: #1a2a15;
  letter-spacing: -0.02em;
}

/* FORM */
.product-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 1.25rem;
}

label {
  font-size: 0.85rem;
  font-weight: 800;
  color: #4c6b3f;
  margin-left: 0.2rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

input, select, textarea {
  border-radius: 1.2rem;
  border: 2px solid transparent;
  background: #f4f7f2;
  padding: 1rem 1.25rem;
  font-family: 'Manrope', sans-serif;
  font-size: 1rem;
  color: #1a2a15;
  transition: all 0.3s ease;
}

input::placeholder, textarea::placeholder {
  color: #a0ac98;
}

input:hover, select:hover, textarea:hover {
  background: #ecf2e9;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  background: white;
  border-color: #6da13d;
  box-shadow: 0 10px 25px rgba(109, 161, 61, 0.12);
}

textarea {
  resize: none;
  min-height: 120px;
}

.form-error {
  color: #e53e3e;
  font-size: 0.9rem;
  font-weight: 700;
  padding: 1rem;
  background: #fff5f5;
  border-radius: 1rem;
  border-left: 4px solid #e53e3e;
}

/* BUTTONS */
.modal-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-top: 1rem;
}

.btn-submit {
  flex: 1;
  border-radius: 1.2rem;
  padding: 1.1rem;
  background: linear-gradient(135deg, #7db34d, #4c7c2a);
  color: white;
  border: none;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 0 15px 30px rgba(76, 124, 42, 0.25);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(76, 124, 42, 0.35);
}

.btn-submit:active:not(:disabled) {
  transform: translateY(-1px);
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(0.5);
}

.btn-cancel {
  background: none;
  border: none;
  color: #718063;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  padding: 0.5rem;
  transition: color 0.2s;
}

.btn-cancel:hover {
  color: #1a2a15;
  text-decoration: underline;
  text-underline-offset: 4px;
}

/* ANIMATION (Vue Transition) */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.4s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}


</style>
