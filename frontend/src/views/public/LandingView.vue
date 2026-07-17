<template>
  <div class="observer-home">
    <section class="observer-hero" aria-labelledby="observer-title">
      <div class="observer-hero-inner">
        <div class="observer-hero-copy">
          <p class="observer-location">
            <span aria-hidden="true">●</span>
            Centre Hospitalier SGHL · Nkayi
          </p>
          <h1 id="observer-title">
            Votre santé,<br />
            notre engagement<br />
            <span>au quotidien</span>
          </h1>
          <p class="observer-lead">
            Découvrez notre établissement et nos services — sans compte.
            Une équipe bienveillante vous accompagne à chaque étape.
          </p>
          <div class="observer-actions">
            <RouterLink class="btn-public-primary btn-public-large" to="/nos-services">
              Découvrir nos services <span aria-hidden="true">→</span>
            </RouterLink>
            <button class="btn-public-secondary btn-public-large" type="button" @click="gateTo('/patient/rendez-vous')">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M7 3v3m10-3v3M4 9h16M5 5h14a1 1 0 0 1 1 1v14H4V6a1 1 0 0 1 1-1Z" />
              </svg>
              Prendre rendez-vous
            </button>
          </div>
          <ul class="observer-trust" aria-label="Points forts">
            <li>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" /></svg>
              Ouvert 24h/24
            </li>
            <li>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m7-10a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm13 10v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" /></svg>
              Équipe qualifiée
            </li>
            <li>
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Zm-3-10 2 2 4-4" /></svg>
              Données protégées
            </li>
          </ul>
        </div>

        <div class="observer-hero-media">
          <img
            src="/images/visitor/infra.jpg"
            alt="Centre hospitalier SGHL moderne et accueillant"
            width="720"
            height="560"
            loading="eager"
          />
          <div class="observer-float-card observer-float-card--top">
            <span class="observer-float-icon">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11h18M12 2v18m-8-4h16v5H4v-5Zm2-9h12l2 4H4l2-4Z" /></svg>
            </span>
            <span><strong>Urgences 24/7</strong><small>Prise en charge rapide et efficace</small></span>
          </div>
          <div class="observer-float-card observer-float-card--bottom">
            <span class="observer-float-icon observer-float-icon--blue">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m3 11 9-8 9 8v10H3V11Zm6 10v-6h6v6" /></svg>
            </span>
            <span><strong>Soins de proximité</strong><small>Un accompagnement humain et attentif</small></span>
          </div>
        </div>
      </div>
    </section>

    <section class="observer-services" aria-labelledby="services-title">
      <div class="observer-section-heading">
        <p class="pub-eyebrow">Un parcours de soins complet</p>
        <h2 id="services-title">Des services pensés pour vous</h2>
      </div>
      <div class="observer-service-grid">
        <article v-for="service in services" :key="service.title" class="observer-service-card">
          <span class="observer-service-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path :d="service.path" /></svg>
          </span>
          <div>
            <h3>{{ service.title }}</h3>
            <p>{{ service.text }}</p>
            <button type="button" class="observer-text-link" @click="service.redirect ? gateTo(service.redirect) : goToServices()">
              En savoir plus <span aria-hidden="true">→</span>
            </button>
          </div>
        </article>
      </div>
    </section>

    <section class="observer-commitments" aria-labelledby="commitments-title">
      <div class="observer-section-heading observer-section-heading--center">
        <p class="pub-eyebrow">La confiance avant tout</p>
        <h2 id="commitments-title">Nos engagements</h2>
        <p>Votre bien-être et votre confiance sont au cœur de nos priorités.</p>
      </div>
      <div class="observer-commitment-grid">
        <article v-for="item in commitments" :key="item.title" class="observer-commitment-card">
          <span class="observer-commitment-icon">
            <svg viewBox="0 0 24 24" aria-hidden="true"><path :d="item.path" /></svg>
          </span>
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ item.text }}</p>
          </div>
        </article>
      </div>
    </section>

    <section class="observer-nearby" aria-labelledby="nearby-title">
      <div class="observer-nearby-images">
        <img src="/images/visitor/equipe.jpg" alt="Équipe médicale SGHL" width="520" height="340" loading="lazy" />
        <img src="/images/visitor/labo.jpg" alt="Laboratoire moderne SGHL" width="420" height="340" loading="lazy" />
      </div>
      <div class="observer-nearby-copy">
        <p class="pub-eyebrow">SGHL à vos côtés</p>
        <h2 id="nearby-title">Un établissement proche de vous</h2>
        <p>
          Le Centre Hospitalier SGHL met à votre disposition des infrastructures modernes,
          une équipe dévouée et des services de qualité dans un environnement humain et chaleureux.
        </p>
        <RouterLink class="btn-public-primary" to="/presentation">
          Découvrir SGHL <span aria-hidden="true">→</span>
        </RouterLink>
      </div>
    </section>

    <section class="observer-final-cta">
      <div>
        <p class="pub-eyebrow">Votre espace santé</p>
        <h2>Prêt à prendre soin de vous avec SGHL ?</h2>
        <p>Créez gratuitement votre compte patient ou connectez-vous à votre espace sécurisé.</p>
      </div>
      <div class="observer-actions">
        <RouterLink class="btn-public-primary btn-public-large" :to="{ name: 'login', query: { mode: 'register' } }">
          Créer mon compte
        </RouterLink>
        <RouterLink class="btn-public-secondary btn-public-large" :to="{ name: 'login' }">
          Se connecter
        </RouterLink>
      </div>
    </section>
  </div>
</template>

<script setup>
import { RouterLink, useRouter } from 'vue-router'

const router = useRouter()

const services = [
  {
    title: 'Consultations',
    text: 'Des consultations médicales générales et spécialisées, pour toute la famille.',
    redirect: '/patient/rendez-vous',
    path: 'M4 14a4 4 0 0 0 8 0V5a3 3 0 0 0-6 0v5m10-2v5a4 4 0 0 1-4 4m7-12a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z',
  },
  {
    title: 'Laboratoire',
    text: 'Des analyses médicales fiables et rapides pour un diagnostic précis.',
    redirect: '/patient/laboratoire',
    path: 'M9 3h6M10 3v6l-5 9a2 2 0 0 0 2 3h10a2 2 0 0 0 2-3l-5-9V3M8 15h8',
  },
  {
    title: 'Hospitalisation',
    text: 'Des chambres confortables et des soins adaptés à chaque situation.',
    redirect: '/patient/hospitalisations',
    path: 'M3 5v16m0-5h18v5m-2-5v-4a2 2 0 0 0-2-2H9v6M6 10h3v6',
  },
  {
    title: 'Pharmacie',
    text: 'Des médicaments de qualité et des conseils personnalisés par nos pharmaciens.',
    redirect: '/patient/prescriptions',
    path: 'm8 4 12 12m-3.5 3.5a5 5 0 0 1-7 0l-5-5a5 5 0 0 1 0-7l2-2a5 5 0 0 1 7 0l5 5a5 5 0 0 1 0 7l-2 2Z',
  },
]

const commitments = [
  {
    title: 'Sécurité des soins',
    text: 'Des protocoles rigoureux et des équipements modernes pour des soins sûrs et de qualité.',
    path: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Zm0-14v8m-4-4h8',
  },
  {
    title: 'Confidentialité',
    text: 'Vos informations personnelles sont protégées avec le plus haut niveau de confidentialité.',
    path: 'M7 10V7a5 5 0 0 1 10 0v3m-11 0h12v11H6V10Zm6 4v3',
  },
  {
    title: 'Disponible 24/7',
    text: 'Notre équipe reste à votre écoute à tout moment, pour vos urgences et vos besoins quotidiens.',
    path: 'M12 7v5l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z',
  },
]

function gateTo(redirect) {
  router.push({
    name: 'login',
    query: { reason: 'personal', redirect },
  })
}

function goToServices() {
  router.push('/nos-services')
}
</script>
