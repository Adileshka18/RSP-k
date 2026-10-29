<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'outline'
  type?: 'button' | 'submit'
  href?: string
  to?: string
}>()
</script>

<template>
  <component
    :is="href ? 'a' : to ? 'router-link' : 'button'"
    :href="href"
    :to="to"
    :type="!href && !to ? (type ?? 'button') : undefined"
    class="btn"
    :class="[variant === 'primary' ? 'btn--primary' : 'btn--outline']"
  >
    <slot />
  </component>
</template>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.8rem 1.45rem;
  font-size: 0.98rem;
  font-weight: 700;
  border-radius: 999px;
  text-decoration: none;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  white-space: nowrap;
  border: 1px solid transparent;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn--outline {
  background: rgba(255, 255, 255, 0.54);
  border-color: rgba(76, 124, 42, 0.14);
  color: #304125;
}

.btn--outline:hover {
  background: rgba(255, 255, 255, 0.78);
  box-shadow: 0 10px 20px rgba(64, 92, 24, 0.1);
}

.btn--primary {
  background: linear-gradient(135deg, var(--sl-green-1), var(--sl-green-2));
  color: #213117;
  box-shadow: 0 14px 28px rgba(109, 161, 61, 0.18);
}

.btn--primary:hover {
  box-shadow: 0 16px 30px rgba(109, 161, 61, 0.24);
}
</style>
