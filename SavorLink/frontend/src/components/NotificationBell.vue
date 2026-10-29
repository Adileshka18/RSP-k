<script setup lang="ts">
import { NotificationIcon } from '@/assets/icons/png'

defineProps<{
  count: number
}>()
</script>

<template>
  <div class="bell-container" :class="{ 'has-unread': count > 0 }">
    <img :src="NotificationIcon" alt="" class="bell-icon" aria-hidden="true" />
    <div v-if="count > 0" class="badge">
      {{ count > 9 ? '9+' : count }}
    </div>
  </div>
</template>

<style scoped>
.bell-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ffffff, #eef7e7);
  border: 1px solid rgba(76, 124, 42, 0.14);
  font-size: 1.25rem;
  transition: all 0.25s ease;
  cursor: pointer;
  color: #395127;
}

.bell-container:hover {
  transform: translateY(-1px) scale(1.04);
  box-shadow: 0 8px 20px rgba(62, 94, 29, 0.12);
}

.bell-icon {
  width: 22px;
  height: 22px;
  object-fit: contain;
}

.has-unread .bell-icon {
  animation: ring 2.2s infinite ease-in-out;
}

.badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: linear-gradient(135deg, #ef4444, #f97316);
  color: white;
  font-size: 0.66rem;
  font-weight: 800;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.25);
}

@keyframes ring {
  0% { transform: rotate(0); }
  5% { transform: rotate(18deg); }
  10% { transform: rotate(-16deg); }
  15% { transform: rotate(12deg); }
  20% { transform: rotate(-8deg); }
  25% { transform: rotate(4deg); }
  30% { transform: rotate(-2deg); }
  35% { transform: rotate(0); }
  100% { transform: rotate(0); }
}
</style>
