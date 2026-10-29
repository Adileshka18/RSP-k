<script setup lang="ts">
import CommonFooter from '@/components/CommonFooter.vue'
import CommonNavbar from '@/components/CommonNavbar.vue'
</script>

<template>
  <div class="app-shell">
    <CommonNavbar />

    <main class="app-main">
      <router-view />
    </main>

    <CommonFooter />
  </div>
</template>

<style>
:root {
  --sl-green-1: #bfe59e;
  --sl-green-2: #a5db74;
  --sl-green-3: #6f9f43;
  --sl-green-4: #3f5f2a;
  --sl-green-soft: #e8f5da;
  --sl-surface: rgba(255, 255, 255, 0.75);
  --sl-surface-strong: rgba(255, 255, 255, 0.9);
  --sl-border: rgba(63, 95, 42, 0.14);
  --sl-text: #1f2f1a;
  --sl-muted: #5c6f57;
  --sl-shadow: 0 20px 50px rgba(40, 80, 20, 0.12);
}

html,
body,
#app {
  min-height: 100%;
}

html {
  background: linear-gradient(135deg, var(--sl-green-1), var(--sl-green-2));
}

body {
  margin: 0;
  font-family: 'Manrope', 'Segoe UI', system-ui, sans-serif;
  color: var(--sl-text);
  line-height: 1.5;
  background:
    radial-gradient(circle at 15% 20%, rgba(255, 255, 255, 0.35), transparent 35%),
    radial-gradient(circle at 85% 10%, rgba(255, 255, 255, 0.2), transparent 30%),
    radial-gradient(circle at 20% 90%, rgba(111, 159, 67, 0.2), transparent 40%),
    linear-gradient(135deg, var(--sl-green-1), var(--sl-green-2));
  background-attachment: fixed;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

* {
  box-sizing: border-box;
}

button,
input,
select,
textarea {
  font: inherit;
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  max-width: 100%;
  display: block;
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 1rem 0;
}

.glass-card {
  background: var(--sl-surface);
  border: 1px solid var(--sl-border);
  border-radius: 16px;
  backdrop-filter: blur(14px);
  box-shadow: var(--sl-shadow);
}

.surface-panel {
  background: var(--sl-surface-strong);
  border: 1px solid var(--sl-border);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: var(--sl-shadow);
}

.soft-button {
  border: none;
  border-radius: 999px;
  padding: 0.65rem 1.4rem;
  background: linear-gradient(135deg, var(--sl-green-2), var(--sl-green-1));
  color: var(--sl-green-4);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.soft-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 25px rgba(80, 120, 40, 0.2);
}

.page-title,
.screen-title,
.section-title,
.hero-headline {
  color: var(--sl-green-4);
}

.text-muted {
  color: var(--sl-muted);
}

input,
.search-input,
.field-input {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--sl-border);
  border-radius: 12px;
  padding: 0.7rem 0.9rem;
  color: var(--sl-text);
}

.card {
  background: var(--sl-surface);
  border-radius: 14px;
  padding: 1rem;
  box-shadow: var(--sl-shadow);
}

@media (max-width: 768px) {
  .app-main {
    padding-inline: 0.75rem;
  }
}
</style>
