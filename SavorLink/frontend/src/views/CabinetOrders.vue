<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import MyOrders from '@/views/MyOrders.vue'
import SupplierOrders from '@/views/SupplierOrders.vue'

const authStore = useAuthStore()

const ordersComponent = computed(() => (authStore.user?.role === 'SUPPLIER' ? SupplierOrders : MyOrders))
</script>

<template>
  <component :is="ordersComponent" />
</template>
