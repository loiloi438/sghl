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
          <RouterLink class="btn-public-primary" :to="{ name: 'login' }">{{ t('nav.login') }}</RouterLink>
          <RouterLink
            class="btn-public-secondary"
            :to="{ name: 'login', query: { mode: 'register' } }"
          >
            {{ t('nav.register') }}
          </RouterLink>
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
          <div>
            <strong>{{ t('footer.contact') }}</strong>
            <p>📞 01 23 45 67 89</p>
            <p><a href="mailto:info@sghl-sante.com">info@sghl-sante.com</a></p>
            <p><RouterLink to="/contact">{{ t('nav.contact') }}</RouterLink></p>
          </div>
          <div>
            <strong>{{ t('footer.links') }}</strong>
            <p><RouterLink to="/a-propos">{{ t('footer.about') }}</RouterLink></p>
            <p><RouterLink to="/nos-services">{{ t('nav.services') }}</RouterLink></p>
            <p><RouterLink to="/securite">{{ t('nav.security') }}</RouterLink></p>
            <p><RouterLink to="/blog">{{ t('nav.blog') }}</RouterLink></p>
            <p><RouterLink to="/faq">{{ t('nav.faq') }}</RouterLink></p>
          </div>
          <div>
            <strong>{{ t('footer.support') }}</strong>
            <p><RouterLink to="/mentions-legales">{{ t('footer.legal') }}</RouterLink></p>
            <p><RouterLink to="/confidentialite">{{ t('footer.privacy') }}</RouterLink></p>
            <p><RouterLink to="/login">{{ t('nav.login') }}</RouterLink></p>
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
  { to: '/a-propos', labelKey: 'nav.about' },
  { to: '/presentation', labelKey: 'nav.presentation' },
  { to: '/nos-services', labelKey: 'nav.services' },
  { to: '/securite', labelKey: 'nav.security' },
  { to: '/faq', labelKey: 'nav.faq' },
  { to: '/blog', labelKey: 'nav.blog' },
  { to: '/contact', labelKey: 'nav.contact' },
])

watch(
  () => route.fullPath,
  () => {
    navOpen.value = false
  },
)
</script>
