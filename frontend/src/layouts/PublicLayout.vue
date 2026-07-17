<template>
  <div class="public-layout">
    <a href="#contenu-public" class="skip-link">Aller au contenu</a>
    <header class="public-header">
      <div class="public-header-inner">
        <RouterLink to="/accueil" class="public-brand">
          <span class="public-brand-icon" aria-hidden="true">+</span>
          <span>
            <strong>SGHL</strong>
            <small>Pour votre santé et bien-être</small>
          </span>
        </RouterLink>

        <button
          type="button"
          class="public-nav-toggle"
          :aria-expanded="navOpen"
          aria-controls="public-nav"
          @click="navOpen = !navOpen"
        >
          {{ navOpen ? 'Fermer' : 'Menu' }}
        </button>

        <nav
          id="public-nav"
          class="public-nav"
          :class="{ 'is-open': navOpen }"
          aria-label="Navigation publique"
        >
          <RouterLink
            v-for="link in navLinks"
            :key="link.to"
            :to="link.to"
            @click="navOpen = false"
          >
            {{ t(link.labelKey) }}
          </RouterLink>
        </nav>

        <div class="public-header-actions">
          <button
            type="button"
            class="public-lang"
            :aria-label="locale === 'fr' ? 'Switch to English' : 'Passer en français'"
            @click="toggleLocale"
          >
            <span :class="{ 'is-active': locale === 'fr' }">FR</span>
            |
            <span :class="{ 'is-active': locale === 'en' }">EN</span>
          </button>
          <RouterLink
            class="btn-public-secondary"
            :to="{ name: 'login', query: { mode: 'register' } }"
          >
            {{ t('nav.register') }}
          </RouterLink>
          <RouterLink class="btn-public-primary" :to="{ name: 'login' }">{{ t('nav.login') }}</RouterLink>
        </div>
      </div>
    </header>

    <main id="contenu-public" class="public-main">
      <RouterView v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </RouterView>
    </main>

    <footer class="public-footer">
      <div class="public-footer-inner">
        <div class="public-footer-grid">
          <div class="public-footer-brand">
            <RouterLink to="/accueil" class="public-brand public-brand--footer">
              <span class="public-brand-icon" aria-hidden="true">+</span>
              <span>
                <strong>SGHL</strong>
                <small>Centre Hospitalier · Nkayi</small>
              </span>
            </RouterLink>
            <p>Des soins humains, accessibles et sécurisés pour toute la famille.</p>
          </div>
          <div>
            <strong>Coordonnées</strong>
            <p>📍 Nkayi, Rue Houmba Makosso, N°36</p>
            <p>📞 <a href="tel:+242061234567">+242 06 123 45 67</a></p>
            <p>✉️ <a href="mailto:contact@sghl-nkayi.cg">contact@sghl-nkayi.cg</a></p>
          </div>
          <div>
            <strong>Navigation</strong>
            <p><RouterLink to="/a-propos">{{ t('footer.about') }}</RouterLink></p>
            <p><RouterLink to="/nos-services">{{ t('nav.services') }}</RouterLink></p>
            <p><RouterLink to="/presentation">Notre établissement</RouterLink></p>
            <p><RouterLink to="/contact">{{ t('nav.contact') }}</RouterLink></p>
          </div>
          <div>
            <strong>Informations</strong>
            <p><RouterLink to="/mentions-legales">{{ t('footer.legal') }}</RouterLink></p>
            <p><RouterLink to="/confidentialite">{{ t('footer.privacy') }}</RouterLink></p>
            <p><RouterLink to="/securite">{{ t('nav.security') }}</RouterLink></p>
            <p><RouterLink to="/faq">{{ t('nav.faq') }}</RouterLink></p>
          </div>
          <div>
            <strong>Horaires</strong>
            <p>Urgences : 24h/24 · 7j/7</p>
            <p>Consultations :<br />Lun–Ven · 07h00–18h00</p>
            <p>Samedi · 07h00–13h00</p>
          </div>
        </div>
        <p class="public-footer-copy">
          © {{ year }} SGHL — {{ t('footer.rights') }}
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useI18n } from '../composables/useI18n.js'

const route = useRoute()
const navOpen = ref(false)
const year = new Date().getFullYear()
const { t, locale, toggleLocale } = useI18n()

const navLinks = computed(() => [
  { to: '/accueil', labelKey: 'nav.home' },
  { to: '/presentation', labelKey: 'nav.presentation' },
  { to: '/nos-services', labelKey: 'nav.services' },
  { to: '/a-propos', labelKey: 'nav.about' },
  { to: '/contact', labelKey: 'nav.contact' },
])

watch(
  () => route.fullPath,
  () => {
    navOpen.value = false
  },
)
</script>
