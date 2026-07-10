<template>
  <aside class="medical-banner" aria-label="Message institutionnel">
    <div class="banner-content">
      <span class="banner-kicker">SGHL · Qualité des soins</span>
      <p class="banner-text">
        Plateforme hospitalière unifiée — traçabilité, sécurité patient et coordination
        inter-services.
      </p>
    </div>
    <div class="banner-accent" aria-hidden="true" />
    <img class="banner-illu" src="/assets/dashboard-illustration.svg" alt="" aria-hidden="true" />
  </aside>
</template>

<style scoped>
.medical-banner {
  position: relative;
  margin-bottom: 1.75rem;
  padding: 1.15rem 1.35rem;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid #bfdbfe;
  background: linear-gradient(105deg, #eff6ff 0%, #f0fdf4 55%, #ffffff 100%);
}

.banner-kicker {
  display: block;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--color-primary-dark);
  margin-bottom: 0.35rem;
}

.banner-text {
  margin: 0;
  font-size: 0.92rem;
  color: var(--color-text-secondary);
  max-width: 52ch;
}

.banner-accent {
  position: absolute;
  right: -20px;
  top: -20px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(37, 99, 235, 0.12) 0%, transparent 70%);
  pointer-events: none;
}

.banner-illu {
  position: absolute;
  right: 12px;
  bottom: -18px;
  width: 220px;
  height: auto;
  opacity: 0.95;
  pointer-events: none;
  transform: translateZ(0);
}
</style>
