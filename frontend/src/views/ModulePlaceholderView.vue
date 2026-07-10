<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-4xl space-y-6">
      <div class="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center gap-4">
            <div class="grid h-14 w-14 place-items-center rounded-3xl bg-slate-950 text-white">
              <NavIcon :name="module.icon" class="h-6 w-6" />
            </div>
            <div>
              <p class="text-xs uppercase tracking-[0.24em] text-emerald-600">Bientôt disponible</p>
              <h1 class="mt-3 text-3xl font-semibold tracking-tight text-slate-950">{{ module.title }}</h1>
            </div>
          </div>
          <span class="rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-700">Coming soon</span>
        </div>

        <p class="mt-6 text-sm leading-7 text-slate-600">{{ module.subtitle }}</p>
        <div class="mt-6 rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5 text-sm leading-7 text-slate-700">
          Ce module est prévu dans la feuille de route SGHL. La navigation et les droits d’accès sont déjà configurés pour votre rôle — l’interface métier arrive prochainement.
        </div>
      </div>

      <section class="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
        <h2 id="features-title" class="text-lg font-semibold text-slate-900">Fonctionnalités prévues</h2>
        <ul class="mt-5 grid gap-3 text-sm text-slate-600 sm:grid-cols-2">
          <li v-for="(feature, index) in module.features" :key="index" class="flex items-start gap-3 rounded-3xl border border-slate-200 bg-slate-50 p-4">
            <span class="mt-1 inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
            {{ feature }}
          </li>
        </ul>
      </section>

      <section class="grid gap-4 lg:grid-cols-2">
        <article class="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
          <h3 class="text-base font-semibold text-slate-900">Personnel hospitalier</h3>
          <p class="mt-3 text-sm leading-7 text-slate-600">Les comptes médecin, infirmier, pharmacien, etc. sont créés par l’administration — pas d’auto-inscription sur ce portail staff.</p>
        </article>
        <article class="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm">
          <h3 class="text-base font-semibold text-slate-900">Besoin d’accès anticipé ?</h3>
          <p class="mt-3 text-sm leading-7 text-slate-600">Contactez l’équipe SI pour prioriser ce module ou obtenir une démo interne.</p>
          <a href="mailto:support@sghl.local" class="mt-5 inline-flex rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800">support@sghl.local</a>
        </article>
      </section>

      <div class="rounded-[2rem] border border-slate-200 bg-white p-6 text-center shadow-sm">
        <RouterLink to="/" class="inline-flex rounded-full bg-slate-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800">Retour au tableau de bord</RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import NavIcon from '../components/NavIcon.vue'
import { getPlaceholderModule } from '../config/placeholderModules.js'

const route = useRoute()
</script>
