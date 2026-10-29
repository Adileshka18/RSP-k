<script setup lang="ts">
import { useRouter } from 'vue-router'
import BasketIcon from '@/assets/icons/basket.svg'
import TruckIcon from '@/assets/icons/grusovik.svg'
import DocsIcon from '@/assets/icons/docs.svg'
import QuestionIcon from '@/assets/icons/questionn.svg'
import HeroImage from '@/assets/images/home-hero.jpg'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const steps = [
  { title: 'Выбираете поставщика и товары в каталоге', icon: BasketIcon },
  { title: 'Оформляете заказ и отслеживаете статусы', icon: TruckIcon },
  { title: 'Получаете документы и аналитику в одном месте', icon: DocsIcon },
]

const advantages = [
  'Работа без посредников и скрытых наценок',
  'Карточки поставщиков и товаров в едином стиле',
  'Чат, документы и уведомления доступны из одного интерфейса',
]

const goRegisterBuyer = () => router.push({ path: '/auth', query: { mode: 'register', role: 'buyer' } })
const goRegisterSupplier = () => router.push({ path: '/auth', query: { mode: 'register', role: 'supplier' } })
const goCatalog = () => router.push('/catalog')
</script>

<template>
  <main class="home-page">
    <section class="hero">
      <img :src="HeroImage" alt="" class="hero-bg" aria-hidden="true" />
      <div class="hero-overlay"></div>

      <div class="hero-copy">
        <p class="eyebrow">SavorLink</p>
        <h1>Поставщики и рестораны находят друг друга быстрее</h1>

        <div class="hero-actions">
          <button class="primary-btn" @click="goRegisterBuyer">Я покупатель</button>
          <button class="secondary-btn" @click="goRegisterSupplier">Я поставщик</button>
        </div>
      </div>
    </section>

    <section class="section">
      <div class="steps-shell">
        <div class="section-heading">
          <h2>Как это работает</h2>
          <p>Покупка и работа с поставщиками проходят в несколько простых шагов без лишних переходов и путаницы.</p>
        </div>

        <div class="steps-grid">
          <article v-for="step in steps" :key="step.title" class="step-card">
            <div class="step-icon-wrap">
              <img :src="step.icon" alt="" aria-hidden="true" class="step-icon" />
            </div>
            <h3>{{ step.title }}</h3>
          </article>
        </div>
      </div>
    </section>

    <section class="section section--split">
      <div class="info-panel">
        <img :src="QuestionIcon" alt="" aria-hidden="true" class="info-icon" />
        <div>
          <h2>Почему это удобно</h2>
          <ul>
            <li v-for="item in advantages" :key="item">{{ item }}</li>
          </ul>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.home-page {
  display: grid;
  gap: 1rem;
  padding-bottom: 2rem;
}

/* ОБЩИЕ КАРТОЧКИ */
.hero,
.section,
.info-panel {
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(76, 124, 42, 0.14);
  border-radius: 1.5rem;
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.1);
}

/* HERO */
.hero {
  position: relative;
  min-height: min(78vh, 760px);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.hero-bg,
.hero-overlay {
  position: absolute;
  inset: 0;
}

.hero-bg {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero-overlay {
  background:
    linear-gradient(180deg, rgba(10, 18, 10, 0.35), rgba(10, 18, 10, 0.2)),
    radial-gradient(circle at center, rgba(10, 18, 10, 0.06), rgba(10, 18, 10, 0.25));
}

.hero-copy {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 820px;
  color: #fff;
}

.hero-copy h1 {
  margin-bottom: 0.8rem;
  font-size: clamp(2.2rem, 5vw, 4rem);
}

.lead {
  color: rgba(255, 255, 255, 0.9);
}

/* КНОПКИ */
.primary-btn {
  border-radius: 999px;
  padding: 0.9rem 1.3rem;
  font-weight: 700;
  background: linear-gradient(135deg, #6da13d, #4c7c2a);
  color: white;
  border: none;
  cursor: pointer;
}

.secondary-btn {
  border-radius: 999px;
  padding: 0.9rem 1.3rem;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* SECTION */
.section {
  padding: 1.25rem;
}

/* ===== ШАГИ ===== */
.steps-shell {
  padding: 3rem 1.5rem;
  border-radius: 1.5rem;

  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(18px);

  border: 1px solid rgba(76, 124, 42, 0.14);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.12);

  color: #20311c;
}

/* ЗАГОЛОВОК */
.section-heading {
  max-width: 860px;
  margin: 0 auto 2.5rem;
  text-align: center;
}

.section-heading h2 {
  margin-bottom: 0.6rem;
  font-size: clamp(2rem, 4vw, 3rem);
  color: #20311c;
}

.section-heading p {
  color: #5d6b52;
  max-width: 720px;
  margin: 0 auto;
}

/* GRID */
.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 2rem;
}

/* КАРТОЧКА ШАГА */
.step-card {
  text-align: center;
  display: grid;
  gap: 1rem;
  justify-items: center;

  background: transparent;
  border: none;
  box-shadow: none;

  transition: transform 0.25s ease;
}

.step-card:hover {
  transform: translateY(-4px);
}

/* ИКОНКА */
.step-icon-wrap {
  width: 90px;
  height: 90px;
  border-radius: 50%;

  background: rgba(109, 161, 61, 0.12);
  border: 1px solid rgba(76, 124, 42, 0.18);

  display: grid;
  place-items: center;
}

.step-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

/* ТЕКСТ */
.step-card h3 {
  margin: 0;
  font-size: 1.4rem;
  color: #20311c;
}

.step-card p {
  color: #5d6b52;
  font-size: 0.95rem;
}

/* ===== БЛОК "ПОЧЕМУ ЭТО УДОБНО" ===== */
.section--split {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* КАРТОЧКА */
.info-panel {
  max-width: 720px;
  width: 100%;

  padding: 2rem;
  border-radius: 1.5rem;

  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 1.2rem;

  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(18px);

  border: 1px solid rgba(76, 124, 42, 0.14);
  box-shadow: 0 24px 60px rgba(54, 87, 21, 0.12);

  transition: transform 0.25s ease;
}

.info-panel:hover {
  transform: translateY(-4px);
}

/* ИКОНКА */
.info-icon {
  width: 64px;
  height: 64px;

  padding: 0.9rem;
  border-radius: 50%;

  background: rgba(109, 161, 61, 0.12);
  border: 1px solid rgba(76, 124, 42, 0.18);
}

/* ЗАГОЛОВОК */
.info-panel h2 {
  margin: 0;
  font-size: 1.8rem;
  color: #20311c;
}

/* СПИСОК */
.info-panel ul {
  list-style: none;
  padding: 0;
  margin: 0;

  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

/* ПУНКТЫ */
.info-panel li {
  position: relative;
  padding-left: 1.4rem;

  color: #5d6b52;
  font-size: 0.95rem;
}

/* КАСТОМНЫЕ ТОЧКИ */
.info-panel li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.5rem;

  width: 6px;
  height: 6px;
  border-radius: 50%;

  background: #6da13d;
}

/* ADAPTIVE */
@media (max-width: 900px) {
  .steps-grid {
    grid-template-columns: 1fr;
  }

  .hero {
    min-height: 60vh;
    padding: 1.25rem;
  }

  .info-panel {
    padding: 1.5rem;
  }

  .info-panel h2 {
    font-size: 1.5rem;
  }
}
</style>
