<template>
  <footer class="common-footer">
    <div class="footer-inner">
      <div class="brand-block">
        <div class="brand">
          <span class="brand-mark">S</span>
          <span class="brand-name">SavorLink</span>
        </div>
        <p class="brand-text">
          Платформа для удобной работы ресторанов, поставщиков и документов в одном месте.
        </p>
      </div>

      <div class="footer-col">
        <h3>Навигация</h3>
        <router-link to="/catalog">Каталог</router-link>
        <router-link to="/favorites">Избранное</router-link>
        <router-link to="/profile">Профиль</router-link>
      </div>

      <div class="footer-col">
        <h3>Сервисы</h3>
        <router-link to="/chat">Чат</router-link>
        <router-link to="/analytics">Аналитика</router-link>
        <router-link to="/documents">Документы</router-link>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.common-footer {
  margin-top: auto;
  padding: 1.25rem 1rem 1.75rem;
}

.footer-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.25rem 1.35rem;
  border-radius: 1.35rem;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(76, 124, 42, 0.14);
  backdrop-filter: blur(18px);
  box-shadow: 0 18px 48px rgba(38, 66, 18, 0.1);
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  gap: 1rem;
  color: #20311c;
}

.brand-block {
  max-width: 420px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 800;
  margin-bottom: 0.65rem;
}

.brand-mark {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.8rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--sl-green-1), var(--sl-green-2));
  color: #20311c;
}

.brand-text {
  margin: 0;
  color: #506046;
  line-height: 1.5;
}

.footer-col {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.footer-col h3 {
  margin: 0 0 0.35rem;
  font-size: 1rem;
  color: #20311c;
}

.footer-col a {
  color: #4d5e42;
  text-decoration: none;
}

.footer-col a:hover {
  color: #20311c;
}

@media (max-width: 860px) {
  .footer-inner {
    grid-template-columns: 1fr;
  }
}
</style>
