import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Catalog from '@/views/Catalog.vue'
import SupplierDetail from '@/views/SupplierDetail.vue'
import Auth from '@/views/Auth.vue'
import Favorites from '@/views/Favorites.vue'
import Cart from '@/views/Cart.vue'
import Profile from '@/views/Profile.vue'
import Features from '@/views/Features.vue'
import Reviews from '@/views/Reviews.vue'
import MyProducts from '@/views/MyProducts.vue'
import Chat from '@/views/Chat.vue'
import Analytics from '@/views/Analytics.vue'
import Checkout from '@/views/Checkout.vue'
import Compare from '@/views/Compare.vue'
import Documents from '@/views/Documents.vue'
import Notifications from '@/views/Notifications.vue'
import Admin from '@/views/Admin.vue'
import CabinetLayout from '@/components/CabinetLayout.vue'
import CabinetOrders from '@/views/CabinetOrders.vue'
import { useAuthStore } from '@/stores/authStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'Home', component: Home },
    { path: '/catalog', name: 'Catalog', component: Catalog },
    { path: '/suppliers/:id', name: 'SupplierDetail', component: SupplierDetail },
    { path: '/auth', name: 'Auth', component: Auth },
    { path: '/login', redirect: '/auth' },
    { path: '/register', redirect: '/auth?mode=register' },
    { path: '/favorites', name: 'Favorites', component: Favorites },
    { path: '/cart', name: 'Cart', component: Cart },
    { path: '/checkout', name: 'Checkout', component: Checkout },
    { path: '/features', name: 'Features', component: Features },
    { path: '/reviews', name: 'Reviews', component: Reviews },
    { path: '/compare', name: 'Compare', component: Compare },
    { path: '/profile', redirect: '/cabinet/profile' },
    { path: '/chat', redirect: '/cabinet/chat' },
    { path: '/analytics', redirect: '/cabinet/analytics' },
    { path: '/documents', redirect: '/cabinet/documents' },
    { path: '/notifications', redirect: '/cabinet/notifications' },
    { path: '/my-products', redirect: '/cabinet/my-products' },
    { path: '/my-orders', redirect: '/cabinet/orders' },
    { path: '/supplier-orders', redirect: '/cabinet/orders' },
    { path: '/admin', redirect: '/cabinet/admin' },
    {
      path: '/cabinet',
      component: CabinetLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/cabinet/profile' },
        { path: 'profile', name: 'CabinetProfile', component: Profile },
        { path: 'orders', name: 'CabinetOrders', component: CabinetOrders },
        {
          path: 'my-products',
          name: 'CabinetMyProducts',
          component: MyProducts,
          meta: { requiresRole: 'SUPPLIER' },
        },
        { path: 'chat', name: 'CabinetChat', component: Chat },
        { path: 'analytics', name: 'CabinetAnalytics', component: Analytics },
        { path: 'documents', name: 'CabinetDocuments', component: Documents },
        { path: 'notifications', name: 'CabinetNotifications', component: Notifications },
        { path: 'admin', name: 'CabinetAdmin', component: Admin, meta: { requiresRole: 'ADMIN' } },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const authStore = useAuthStore()

  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!authStore.token) {
      return '/auth'
    }
  }

  if (to.meta.requiresRole) {
    if (!authStore.token) {
      return '/auth'
    }
    if (authStore.user?.role !== to.meta.requiresRole) {
      return '/'
    }
  }
})

export default router
