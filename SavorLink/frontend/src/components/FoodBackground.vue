<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useShopStore } from '@/stores/shopStore'

type FoodType =
  | 'tomato'
  | 'carrot'
  | 'pepper'
  | 'apple'
  | 'fish'
  | 'shrimp'
  | 'chicken'
  | 'avocado'
  | 'cheese'
  | 'egg'
  | 'banana'
  | 'corn'
  | 'cherry'

type FoodIcon = {
  type: FoodType
  left: string
  top: string
  size: number
  duration: string
  delay: string
  opacity: number
}

const shopStore = useShopStore()
const icons = ref<FoodIcon[]>([])

const ALL_TYPES: FoodType[] = [
  'tomato','carrot','pepper','apple','fish','shrimp',
  'chicken','avocado','cheese','egg','banana','corn','cherry'
]

// 🔍 маппинг продуктов → иконки
const productMap: Record<string, FoodType> = {
  помидор: 'tomato',
  tomato: 'tomato',
  морковь: 'carrot',
  carrot: 'carrot',
  перец: 'pepper',
  pepper: 'pepper',
  яблоко: 'apple',
  apple: 'apple',
  рыба: 'fish',
  fish: 'fish',
  креветк: 'shrimp',
  shrimp: 'shrimp',
  курица: 'chicken',
  chicken: 'chicken',
  авокадо: 'avocado',
  avocado: 'avocado',
  сыр: 'cheese',
  cheese: 'cheese',
  яйц: 'egg',
  egg: 'egg',
  банан: 'banana',
  banana: 'banana',
  кукуруз: 'corn',
  corn: 'corn',
  вишн: 'cherry',
  cherry: 'cherry',
}

// 📦 типы из поставщика
const supplierTypes = computed<FoodType[]>(() => {
  const products = shopStore.state.currentSupplier?.products ?? []

  const found = products
    .flatMap(p => {
      const text = `${p.name} ${p.description ?? ''}`.toLowerCase()
      const match = Object.entries(productMap).find(([k]) => text.includes(k))
      return match ? [match[1]] : []
    })

  const unique = [...new Set(found)]
  return unique.length ? unique : ALL_TYPES
})

function random(min: number, max: number) {
  return Math.random() * (max - min) + min
}

function randomItem<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)] as T
}

// 📱 адаптивное количество
function getCount() {
  const w = window.innerWidth
  if (w < 640) return 12
  if (w < 1024) return 18
  return 28
}

// 🎯 генерация
function generateIcons(): FoodIcon[] {
  const types = supplierTypes.value
  const count = getCount()

  return Array.from({ length: count }).map((_, i) => ({
    type: randomItem(types),
    left: `${random(0, 100)}%`,
    top: `${random(0, 100)}%`,
    size: random(40, 85),
    duration: `${random(20, 40)}s`,
    delay: `-${random(0, 30)}s`,
    opacity: random(0.12, 0.24),
  }))
}

function regenerate() {
  icons.value = generateIcons()
}

onMounted(() => {
  regenerate()
  window.addEventListener('resize', regenerate)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', regenerate)
})

// 🎨 SVG
const svgMap: Record<FoodType, string> = {
  tomato: `<circle cx="40" cy="40" r="18"/>`,
  carrot: `<path d="M20 60c20-25 30-35 40-45"/>`,
  pepper: `<path d="M40 20c10 0 15 10 10 20-5 10-10 15-10 25"/>`,
  apple: `<circle cx="40" cy="45" r="18"/>`,
  fish: `<path d="M20 40c10-10 30-10 40 0-10 10-30 10-40 0z"/>`,
  shrimp: `<path d="M30 50c15-25 35-10 20 10"/>`,
  chicken: `<circle cx="40" cy="40" r="20"/>`,
  avocado: `<ellipse cx="40" cy="40" rx="18" ry="22"/>`,
  cheese: `<path d="M20 55l30-25 10 30z"/>`,
  egg: `<ellipse cx="40" cy="42" rx="14" ry="18"/>`,
  banana: `<path d="M20 50c15-25 45-15 40 5"/>`,
  corn: `<ellipse cx="40" cy="40" rx="10" ry="20"/>`,
  cherry: `<circle cx="35" cy="45" r="6"/><circle cx="48" cy="45" r="6"/>`,
}
</script>

<template>
  <div class="food-bg">
    <div
      v-for="(icon, index) in icons"
      :key="index"
      class="food-item"
      :style="{
        left: icon.left,
        top: icon.top,
        width: `${icon.size}px`,
        height: `${icon.size}px`,
        opacity: icon.opacity,
        animationDuration: icon.duration,
        animationDelay: icon.delay,
      }"
    >
      <svg viewBox="0 0 80 80">
        <g class="food-svg" v-html="svgMap[icon.type]" />
      </svg>
    </div>
  </div>
</template>

<style scoped>
.food-bg {
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.food-item {
  position: absolute;
  animation: float linear infinite;
  will-change: transform;
}

.food-item svg {
  width: 100%;
  height: 100%;
}

.food-svg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.42);
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.12));
}

/* 🌊 более "телеграмный" флоу */
@keyframes float {
  0% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(30px, -50px);
  }
  100% {
    transform: translate(0, 0);
  }
}
</style>
