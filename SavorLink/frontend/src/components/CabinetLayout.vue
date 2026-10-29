<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { BagIcon, DocumentIcon, NotificationIcon, OrganizationIcon, TruckIcon } from '@/assets/icons/png'

const authStore = useAuthStore()

const displayName = computed(() => authStore.user?.name || authStore.user?.company || authStore.user?.email || 'Личный кабинет')
const isSupplier = computed(() => authStore.user?.role === 'SUPPLIER')

const navItems = computed(() => [
  { to: '/cabinet/profile', label: 'Профиль', icon: OrganizationIcon },
  {
    to: '/cabinet/orders',
    label: 'Заказы',
    icon: TruckIcon,
  },
  ...(isSupplier.value
    ? [
        { to: '/cabinet/my-products', label: 'Мои товары', icon: BagIcon },
      ]
    : []),
  { to: '/cabinet/chat', label: 'Чат', icon: NotificationIcon },
  { to: '/cabinet/analytics', label: 'Аналитика', icon: NotificationIcon },
  { to: '/cabinet/documents', label: 'Документы', icon: DocumentIcon },
  { to: '/cabinet/notifications', label: 'Уведомления', icon: NotificationIcon },
  ...(authStore.user?.role === 'ADMIN'
    ? [{ to: '/cabinet/admin', label: 'Администрирование', icon: DocumentIcon }]
    : []),
])
</script>

<template>
  <div class="cabinet-page">
    <div class="cabinet-layout">
      <aside class="cabinet-sidebar">
        <div class="cabinet-summary">
          <p class="cabinet-kicker">Кабинет</p>
          <h2>{{ displayName }}</h2>
          <p>
            {{ isSupplier ? 'Управление товарами, заказами и коммуникацией.' : 'Заказы, чат, документы и уведомления в одном месте.' }}
          </p>
        </div>

        <nav class="cabinet-nav">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="cabinet-link"
            active-class="cabinet-link--active"
          >
            <img :src="item.icon" alt="" aria-hidden="true" class="cabinet-link-icon" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </nav>

        <div class="cabinet-footer">
          <RouterLink to="/catalog" class="cabinet-catalog-link">Открыть каталог</RouterLink>
        </div>
      </aside>

      <main class="cabinet-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.cabinet-page {
  width: 100%;
  padding: 1rem 0 2rem;
}

.cabinet-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 1.5rem;
  align-items: start;
}

.cabinet-sidebar {
  position: sticky;
  top: 5.75rem;
  display: grid;
  gap: 1.25rem;
  padding: 1.25rem;
  border-radius: 1.5rem;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(76, 124, 42, 0.14);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.1);
  backdrop-filter: blur(18px);
}

.cabinet-summary {
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(76, 124, 42, 0.12);
}

.cabinet-kicker {
  margin: 0 0 0.35rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #5d6b52;
}

.cabinet-summary h2 {
  margin: 0;
  color: #20311c;
  font-size: 1.45rem;
}

.cabinet-summary p {
  margin: 0.45rem 0 0;
  color: #5d6b52;
}

.cabinet-nav {
  display: grid;
  gap: 0.55rem;
}

.cabinet-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.85rem 0.95rem;
  border-radius: 1rem;
  border: 1px solid rgba(76, 124, 42, 0.14);
  background: rgba(255, 255, 255, 0.82);
  color: #3f4a2f;
  font-weight: 700;
  transition: all 0.2s ease;
}

.cabinet-link:hover,
.cabinet-link--active {
  background: linear-gradient(135deg, #bfe59e, #e8f5da);
  color: #20311c;
  border-color: rgba(76, 124, 42, 0.22);
  transform: translateY(-1px);
}

.cabinet-link-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
  flex: 0 0 auto;
}

.cabinet-footer {
  border-top: 1px solid rgba(76, 124, 42, 0.12);
  padding-top: 1rem;
}

.cabinet-catalog-link {
  display: block;
  width: 100%;
  border-radius: 1rem;
  padding: 0.85rem 1rem;
  text-align: center;
  border: 1px solid rgba(76, 124, 42, 0.16);
  background: rgba(255, 255, 255, 0.86);
  color: #3f4a2f;
  font-weight: 700;
}

.cabinet-content {
  min-width: 0;
}

@media (max-width: 1024px) {
  .cabinet-layout {
    grid-template-columns: 1fr;
  }

  .cabinet-sidebar {
    position: static;
  }
}

@media (max-width: 768px) {
  .cabinet-page {
    padding-top: 0.5rem;
  }
}
</style>
