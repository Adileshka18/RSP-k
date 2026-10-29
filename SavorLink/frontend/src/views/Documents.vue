<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

const router = useRouter()
const authStore = useAuthStore()
const store = useShopStore()

const documentType = ref('Счёт')
const selectedOrderId = ref<number | null>(null)

onMounted(async () => {
  if (!authStore.token) {
    router.push('/auth')
    return
  }

  if (authStore.user?.role === 'SUPPLIER') {
    await store.fetchSupplierOrders()
  } else {
    await store.fetchMyOrders()
  }
})

const orders = computed(() =>
  authStore.user?.role === 'SUPPLIER' ? store.state.supplierOrders : store.state.myOrders,
)

const selectedOrder = computed(() => orders.value.find((order) => order.id === selectedOrderId.value) ?? null)

const previewText = computed(() => {
  if (!selectedOrder.value) return 'Выберите заказ для генерации документа.'

  const lines = [
    `${documentType.value} по заказу #${selectedOrder.value.id}`,
    `Статус: ${selectedOrder.value.status}`,
    `Поставщик: ${selectedOrder.value.seller_enterprise.short_name}`,
    `Покупатель: ${selectedOrder.value.buyer_enterprise?.short_name || 'Не указан'}`,
    `Сумма: ${selectedOrder.value.total_amount ?? 0} ₽`,
    '',
    'Позиции:',
    ...selectedOrder.value.items.map(
      (item) => `- ${item.product?.name || `Товар #${item.product_id}`} — ${item.quantity} кг`,
    ),
  ]

  return lines.join('\n')
})

const downloadDocument = () => {
  const blob = new Blob([previewText.value], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `document-order-${selectedOrder.value?.id || 'draft'}.txt`
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <main class="documents-page">
    <section class="hero">
      <div>
        <p class="eyebrow">Документы</p>
        <h1>Генератор документов для заказа</h1>
        <p>Пока используем быстрый шаблон. Позже его можно заменить на PDF-генерацию с бэка.</p>
      </div>
      <button class="primary-btn" @click="downloadDocument" :disabled="!selectedOrder">
        Скачать документ
      </button>
    </section>

    <div class="layout">
      <section class="panel">
        <div class="field">
          <label>Заказ</label>
          <select v-model="selectedOrderId">
            <option :value="null">Выберите заказ</option>
            <option v-for="order in orders" :key="order.id" :value="order.id">Заказ #{{ order.id }}</option>
          </select>
        </div>

        <div class="field">
          <label>Тип документа</label>
          <select v-model="documentType">
            <option>Счёт</option>
            <option>Договор</option>
            <option>Акт</option>
          </select>
        </div>

        <div class="preview">
          <pre>{{ previewText }}</pre>
        </div>
      </section>

      <aside class="panel hint">
        <h2>Что дальше</h2>
        <p>
          Когда на бэке появится генерация файлов, сюда можно подключить настоящий PDF и выгрузку из
          сохранённых документов заказа.
        </p>
      </aside>
    </div>
  </main>
</template>

<style scoped>
.documents-page {
  display: grid;
  gap: 1rem;
  padding-bottom: 2rem;
}

.hero,
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

.layout {
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: 1rem;
}

.panel {
  padding: 1.25rem;
}

.field {
  display: grid;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.field label {
  font-size: 0.8rem;
  font-weight: 700;
  color: #5d6b52;
}

select {
  padding: 0.75rem 0.9rem;
}

.preview {
  background: rgba(249, 250, 251, 0.7);
  border-radius: 1rem;
  padding: 1rem;
  overflow: auto;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  color: #20311c;
}

.hint p {
  color: #5d6b52;
}

.primary-btn {
  border: none;
  border-radius: 999px;
  padding: 0.85rem 1.2rem;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  align-self: center;
}

@media (max-width: 900px) {
  .hero,
  .layout {
    display: grid;
    grid-template-columns: 1fr;
  }
}
</style>
