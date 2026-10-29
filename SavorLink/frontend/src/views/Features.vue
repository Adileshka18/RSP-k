<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
const goHome = () => router.push('/')
</script>

<template>
  <div class="placeholder-page">
    <div class="content-card">
      <h1>Возможности</h1>
      <p>Этот раздел находится в разработке. Здесь будет описание всех функций системы SavorLink.</p>
      <button @click="goHome" class="back-btn">На главную</button>
    </div>
  </div>
</template>

<style scoped>
.placeholder-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top left, #5a6641 0%, #343d27 100%);
  color: #f9fafb;
  font-family: sans-serif;
  text-align: center;
}

.content-card {
  background: rgba(52, 46, 36, 0.9);
  padding: 3rem;
  border-radius: 1.5rem;
  border: 1px solid rgba(224, 200, 163, 0.3);
  max-width: 500px;
}

h1 {
  margin-top: 0;
  color: #d8bf98;
}

p {
  line-height: 1.6;
  margin-bottom: 2rem;
}

.back-btn {
  background: #d8bf98;
  color: #2e2a23;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
}
</style>
