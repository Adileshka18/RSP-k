<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useShopStore } from '@/stores/shopStore'

const authStore = useAuthStore()
const shopStore = useShopStore()
const router = useRouter()
const route = useRoute()

const favoritesCount = computed(
  () => shopStore.state.favoriteProducts.length + shopStore.state.favoriteSuppliers.length,
)

const cartCount = computed(() => shopStore.state.cartItems.length)

const isGuest = computed(() => !authStore.token)
const isSupplier = computed(() => authStore.user?.role === 'SUPPLIER')

const isActive = (path: string) => {
  if (path === '/cabinet') {
    return route.path.startsWith('/cabinet')
  }

  return route.path === path
}

const handleLogout = () => {
  authStore.logout()
  shopStore.state.cartItems = []
  shopStore.state.favoriteProducts = []
  shopStore.state.favoriteProductIds = []
  shopStore.state.favoriteSuppliers = []
  router.push('/')
}

onMounted(async () => {
  if (!authStore.token) return

  await Promise.all([
    shopStore.fetchCart(),
    shopStore.fetchFavoriteProducts(),
    shopStore.fetchFavoriteSuppliers(),
  ])
})
</script>

<template>
  <header class="common-header">
    <nav class="common-nav">
      <router-link to="/" class="logo">
        <span class="logo-mark">S</span>
        <span class="logo-text">SavorLink</span>
      </router-link>

      <div class="nav-links">
        <router-link to="/" class="nav-link" :class="{ active: isActive('/') }">Главная</router-link>
        <router-link to="/catalog" class="nav-link" :class="{ active: isActive('/catalog') }">Каталог</router-link>

        <template v-if="isGuest">
          <router-link to="/features" class="nav-link">Возможности</router-link>
          <router-link to="/reviews" class="nav-link">Отзывы</router-link>
          <router-link :to="{ path: '/auth', query: { mode: 'register' } }" class="nav-link nav-link--cta">
            Регистрация
          </router-link>
          <router-link to="/auth" class="nav-link">Вход</router-link>
        </template>

        <template v-else>
          <router-link to="/cabinet/profile" class="nav-link" :class="{ active: isActive('/cabinet') }">Кабинет</router-link>
          <router-link v-if="!isSupplier" to="/favorites" class="nav-link" :class="{ active: isActive('/favorites') }">
            Избранное{{ favoritesCount > 0 ? ` (${favoritesCount})` : '' }}
          </router-link>
          <router-link v-if="!isSupplier" to="/cart" class="nav-link" :class="{ active: isActive('/cart') }">
            Корзина{{ cartCount > 0 ? ` (${cartCount})` : '' }}
          </router-link>
          <button type="button" class="btn-logout" @click="handleLogout">Выйти</button>
        </template>
      </div>
    </nav>
  </header>
</template>

<style scoped>
.common-header {
  padding: 0.7rem 1rem 0;
}

.common-nav {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 1.35rem;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(76, 124, 42, 0.14);
  box-shadow: 0 18px 48px rgba(38, 66, 18, 0.1);
  backdrop-filter: blur(18px);
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  white-space: nowrap;
}

.logo-mark {
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--sl-green-1), var(--sl-green-2));
  color: #20311c;
  font-weight: 900;
  box-shadow: 0 10px 24px rgba(109, 161, 61, 0.22);
}

.logo-text {
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: 0.01em;
  color: #20311c;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.55rem;
  flex-wrap: wrap;
}

.nav-link {
  color: #4d5e42;
  font-size: 0.94rem;
  transition: all 0.2s ease;
  white-space: nowrap;
  padding: 0.55rem 0.9rem;
  border-radius: 999px;
}

.nav-link:hover,
.nav-link.active {
  color: #20311c;
  background: rgba(165, 219, 116, 0.18);
}

.nav-link--cta {
  background: linear-gradient(135deg, var(--sl-green-1), var(--sl-green-2));
  color: #20311c;
  box-shadow: 0 10px 24px rgba(109, 161, 61, 0.16);
}

.nav-link--cta:hover {
  background: linear-gradient(135deg, #b7e58a, #d6f1bf);
}

.btn-logout {
  background: linear-gradient(135deg, #ffffff, #f2fbeb);
  border: 1px solid rgba(76, 124, 42, 0.14);
  color: #304125;
  padding: 0.55rem 1rem;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-logout:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(82, 112, 34, 0.14);
}

@media (max-width: 1024px) {
  .common-nav {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .common-header {
    padding-inline: 0.7rem;
  }

  .common-nav {
    padding: 0.85rem;
  }

  .nav-links {
    gap: 0.4rem;
  }

  .nav-link {
    font-size: 0.82rem;
    padding: 0.45rem 0.72rem;
  }
}
</style>

