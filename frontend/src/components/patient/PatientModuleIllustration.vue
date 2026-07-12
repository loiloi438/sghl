<template>
  <div class="hc-module-ill" aria-hidden="true">
    <svg viewBox="0 0 120 96" fill="none" xmlns="http://www.w3.org/2000/svg" class="hc-module-ill-svg">
      <ellipse cx="60" cy="88" rx="44" ry="6" fill="#99f6e4" opacity="0.45" />

      <!-- Hospital -->
      <template v-if="variant === 'hospital'">
        <rect x="28" y="28" width="64" height="52" rx="10" fill="#fff" stroke="#2dd4bf" stroke-width="2" />
        <rect x="52" y="18" width="16" height="14" rx="4" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.5" />
        <path d="M58 40v16M50 48h16" stroke="#0d9488" stroke-width="2.5" stroke-linecap="round" />
        <rect x="38" y="56" width="12" height="12" rx="2" fill="#bae6fd" />
        <rect x="54" y="56" width="12" height="12" rx="2" fill="#bae6fd" />
        <rect x="70" y="56" width="12" height="12" rx="2" fill="#bae6fd" />
      </template>

      <!-- Pharmacy -->
      <template v-else-if="variant === 'pharmacy'">
        <rect x="42" y="22" width="36" height="58" rx="8" fill="#fff" stroke="#2dd4bf" stroke-width="2" />
        <rect x="48" y="14" width="24" height="12" rx="6" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.5" />
        <rect x="50" y="38" width="20" height="28" rx="4" fill="#fde68a" stroke="#fbbf24" stroke-width="1.5" />
        <path d="M60 46v12M54 52h12" stroke="#0d9488" stroke-width="2" stroke-linecap="round" />
        <circle cx="34" cy="52" r="10" fill="#bae6fd" stroke="#38bdf8" stroke-width="1.5" />
        <circle cx="34" cy="52" r="4" fill="#fff" />
      </template>

      <!-- Care -->
      <template v-else-if="variant === 'care'">
        <circle cx="42" cy="44" r="16" fill="#fde68a" stroke="#fbbf24" stroke-width="2" />
        <path d="M42 60c-12 0-22 8-22 18v6h44v-6c0-10-10-18-22-18z" fill="#bae6fd" stroke="#38bdf8" stroke-width="2" />
        <path d="M72 50c8 0 14 6 14 14v10H58V64c0-8 6-14 14-14z" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2" />
        <path d="M66 58c4 3 8 3 12 0" stroke="#0d9488" stroke-width="2" stroke-linecap="round" />
        <path d="M78 46c0-6 8-8 12-2" stroke="#ef4444" stroke-width="2" stroke-linecap="round" fill="none" />
      </template>

      <!-- Lab -->
      <template v-else-if="variant === 'lab'">
        <path d="M48 24h24l-8 36c-2 8-14 8-16 0L48 24z" fill="#fff" stroke="#2dd4bf" stroke-width="2" />
        <ellipse cx="60" cy="24" rx="12" ry="4" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="1.5" />
        <circle cx="56" cy="48" r="4" fill="#fde68a" />
        <circle cx="64" cy="54" r="3" fill="#bae6fd" />
        <rect x="78" y="40" width="18" height="24" rx="4" fill="#fff" stroke="#38bdf8" stroke-width="1.5" />
        <path d="M82 52h10M82 58h6" stroke="#0ea5e9" stroke-width="1.5" stroke-linecap="round" />
      </template>

      <!-- Invoice -->
      <template v-else-if="variant === 'invoice'">
        <rect x="34" y="18" width="52" height="62" rx="8" fill="#fff" stroke="#2dd4bf" stroke-width="2" />
        <path d="M44 34h32M44 46h24M44 58h28" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" />
        <circle cx="78" cy="62" r="14" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2" />
        <path d="M72 62l4 4 8-8" stroke="#0d9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </template>

      <!-- Calendar -->
      <template v-else-if="variant === 'calendar'">
        <rect x="30" y="26" width="60" height="52" rx="10" fill="#fff" stroke="#2dd4bf" stroke-width="2" />
        <path d="M30 40h60" stroke="#6ee7b7" stroke-width="2" />
        <path d="M46 22v10M74 22v10" stroke="#0d9488" stroke-width="2" stroke-linecap="round" />
        <rect x="40" y="50" width="10" height="10" rx="2" fill="#bae6fd" />
        <rect x="55" y="50" width="10" height="10" rx="2" fill="#ecfdf5" />
        <rect x="70" y="50" width="10" height="10" rx="2" fill="#ecfdf5" />
        <circle cx="60" cy="68" r="8" fill="#34d399" />
        <path d="M56 68l3 3 6-6" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </template>

      <!-- Message -->
      <template v-else-if="variant === 'message'">
        <rect x="22" y="30" width="52" height="36" rx="10" fill="#fff" stroke="#2dd4bf" stroke-width="2" />
        <path d="M34 66l10-10h30" fill="#fff" stroke="#2dd4bf" stroke-width="2" stroke-linejoin="round" />
        <path d="M32 44h32M32 52h20" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" />
        <rect x="62" y="18" width="36" height="28" rx="8" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2" />
        <circle cx="80" cy="32" r="8" fill="#fde68a" stroke="#fbbf24" stroke-width="1.5" />
      </template>

      <!-- Notification -->
      <template v-else-if="variant === 'notification'">
        <path d="M60 20c-14 0-22 10-22 22v14l-6 10h56l-6-10V42c0-12-8-22-22-22z" fill="#fff" stroke="#2dd4bf" stroke-width="2" />
        <path d="M48 76c4 6 10 8 12 8s8-2 12-8" stroke="#6ee7b7" stroke-width="2" stroke-linecap="round" />
        <circle cx="76" cy="28" r="10" fill="#fde68a" stroke="#fbbf24" stroke-width="2" />
        <path d="M76 24v8M72 28h8" stroke="#0d9488" stroke-width="2" stroke-linecap="round" />
      </template>

      <!-- Profile -->
      <template v-else-if="variant === 'profile'">
        <circle cx="60" cy="38" r="18" fill="#fde68a" stroke="#fbbf24" stroke-width="2" />
        <path d="M60 56c-18 0-32 10-32 22v6h64v-6c0-12-14-22-32-22z" fill="#bae6fd" stroke="#38bdf8" stroke-width="2" />
        <circle cx="82" cy="34" r="12" fill="#ecfdf5" stroke="#6ee7b7" stroke-width="2" />
        <path d="M78 34l3 3 6-6" stroke="#0d9488" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </template>

      <!-- Default (home-style) -->
      <template v-else>
        <circle cx="44" cy="46" r="14" fill="#fde68a" stroke="#fbbf24" stroke-width="2" />
        <path d="M44 60c-10 0-18 6-18 14v8h36v-8c0-8-8-14-18-14z" fill="#bae6fd" stroke="#38bdf8" stroke-width="2" />
        <rect x="68" y="36" width="28" height="40" rx="8" fill="#fff" stroke="#2dd4bf" stroke-width="2" />
        <path d="M82 50v10M76 55h12" stroke="#0d9488" stroke-width="2" stroke-linecap="round" />
      </template>
    </svg>
  </div>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (v) =>
      ['default', 'hospital', 'pharmacy', 'care', 'lab', 'invoice', 'calendar', 'message', 'notification', 'profile'].includes(v),
  },
})
</script>

<style scoped>
.hc-module-ill {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
}

.hc-module-ill-svg {
  width: 110px;
  max-width: 100%;
  height: auto;
}
</style>
