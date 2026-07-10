<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-[28px] border border-slate-200 bg-gradient-to-r from-sky-50 to-white p-6 shadow-sm">
        <p class="text-xs uppercase tracking-[0.24em] text-cyan-600">Contact & Localisation</p>
        <h1 class="mt-3 text-3xl font-semibold text-slate-950">{{ etablissement.organization_name || 'Centre hospitalier SGHL' }}</h1>
        <p class="mt-3 max-w-2xl text-sm leading-7 text-slate-600">Itinéraire, coordonnées et accès rapide vers l'hôpital.</p>
      </header>

      <div v-if="loading" class="rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">Chargement des coordonnées…</div>
      <div v-else-if="loadError" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ loadError }}</div>

      <section v-else class="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Coordonnées</h2>
          <div class="mt-4 space-y-3 text-sm text-slate-600">
            <p>{{ etablissement.address || 'Adresse non renseignée' }}</p>
            <p v-if="etablissement.phone">Téléphone : <a :href="`tel:${etablissement.phone}`" class="font-medium text-cyan-600 hover:text-cyan-700">{{ etablissement.phone }}</a></p>
            <p v-if="etablissement.email">Email : <a :href="`mailto:${etablissement.email}`" class="font-medium text-cyan-600 hover:text-cyan-700">{{ etablissement.email }}</a></p>
            <p>Ouvert 24h / 24 · Urgences permanentes</p>
          </div>
        </div>

        <div class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="space-y-4">
            <div>
              <p class="text-sm font-semibold text-slate-900">Direction de l'hôpital</p>
              <p class="mt-2 text-sm leading-7 text-slate-600">Suivez la carte ci-dessous pour localiser le site et lancer votre itinéraire.</p>
            </div>

            <div class="flex flex-wrap gap-3">
              <a
                class="inline-flex items-center justify-center rounded-full bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800"
                :href="googleMapsUrl"
                target="_blank"
                rel="noreferrer noopener"
              >
                Ouvrir Google Maps
              </a>
              <a
                class="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-900 transition hover:bg-slate-50"
                :href="googleDirectionsUrl"
                target="_blank"
                rel="noreferrer noopener"
              >
                Itinéraire jusqu'à l'hôpital
              </a>
            </div>
          </div>

          <div class="mt-6 grid gap-3 sm:grid-cols-3">
            <div class="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-sm text-slate-500">Latitude</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">{{ hospitalCoords.lat.toFixed(4) }}</p>
            </div>
            <div class="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-sm text-slate-500">Longitude</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">{{ hospitalCoords.lon.toFixed(4) }}</p>
            </div>
            <div class="rounded-3xl border border-slate-200 bg-slate-50 p-4">
              <p class="text-sm text-slate-500">Accès</p>
              <p class="mt-2 text-lg font-semibold text-slate-900">24/7</p>
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div class="overflow-hidden rounded-[28px] border border-slate-200">
          <iframe
            title="Carte localisation SGHL"
            :src="osmEmbedUrl"
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
            class="h-[420px] w-full"
          ></iframe>
        </div>
      </section>

      <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
        <div class="space-y-4">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Votre position</h2>
            <p class="mt-2 text-sm leading-7 text-slate-600">Obtenez un aperçu de votre distance et du temps estimé vers SGHL.</p>
          </div>

          <div class="rounded-3xl bg-slate-50 p-5 text-sm text-slate-600">
            <p v-if="locationError" class="text-rose-600">{{ locationError }}</p>
            <p v-else-if="locationLoading">Demande de géolocalisation en cours…</p>
            <p v-else-if="locationDenied">Géolocalisation refusée. Autorisez l'accès au navigateur pour afficher l'itinéraire.</p>
            <p v-else-if="locationReady">Position détectée avec succès.</p>
            <p v-else>Autorisez la géolocalisation pour afficher la distance et le temps de trajet.</p>
          </div>

          <div v-if="locationReady" class="grid gap-4 sm:grid-cols-3">
            <div class="rounded-3xl border border-slate-200 bg-white p-4 text-sm text-slate-700 shadow-sm">
              <span class="text-sm text-slate-500">Distance</span>
              <p class="mt-3 text-2xl font-semibold text-slate-900">{{ distanceKm }} km</p>
            </div>
            <div class="rounded-3xl border border-slate-200 bg-white p-4 text-sm text-slate-700 shadow-sm">
              <span class="text-sm text-slate-500">À pied</span>
              <p class="mt-3 text-2xl font-semibold text-slate-900">{{ walkingTime }}</p>
            </div>
            <div class="rounded-3xl border border-slate-200 bg-white p-4 text-sm text-slate-700 shadow-sm">
              <span class="text-sm text-slate-500">En voiture</span>
              <p class="mt-3 text-2xl font-semibold text-slate-900">{{ drivingTime }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import api, { getErrorMessage } from '../api/client.js'

const hospitalCoords = {
  lat: -4.2839,
  lon: 12.9860,
}

const loading = ref(true)
const loadError = ref('')
const etablissement = ref({
  organization_name: '',
  address: '',
  phone: '',
  email: '',
})

const locationLoading = ref(false)
const locationError = ref('')
const locationDenied = ref(false)
const userCoords = ref(null)

const osmEmbedUrl = computed(() => {
  const left = hospitalCoords.lon - 0.006
  const right = hospitalCoords.lon + 0.006
  const top = hospitalCoords.lat + 0.005
  const bottom = hospitalCoords.lat - 0.005
  return `https://www.openstreetmap.org/export/embed.html?bbox=${left}%2C${bottom}%2C${right}%2C${top}&layer=mapnik&marker=${hospitalCoords.lat}%2C${hospitalCoords.lon}`
})

const googleMapsUrl = computed(
  () =>
    `https://www.google.com/maps/search/?api=1&query=${hospitalCoords.lat},${hospitalCoords.lon}`,
)

const googleDirectionsUrl = computed(
  () =>
    `https://www.google.com/maps/dir/?api=1&destination=${hospitalCoords.lat},${hospitalCoords.lon}&travelmode=driving`,
)

function getDistanceKm(a, b) {
  const toRad = (value) => (value * Math.PI) / 180
  const R = 6371
  const dLat = toRad(b.lat - a.lat)
  const dLon = toRad(b.lon - a.lon)
  const lat1 = toRad(a.lat)
  const lat2 = toRad(b.lat)
  const sinLat = Math.sin(dLat / 2)
  const sinLon = Math.sin(dLon / 2)
  const aVal = sinLat * sinLat + sinLon * sinLon * Math.cos(lat1) * Math.cos(lat2)
  const c = 2 * Math.atan2(Math.sqrt(aVal), Math.sqrt(1 - aVal))
  return R * c
}

const distanceKm = computed(() => {
  if (!userCoords.value) return '--'
  return getDistanceKm(userCoords.value, hospitalCoords).toFixed(1)
})

const walkingTime = computed(() => {
  if (!userCoords.value) return '--'
  const minutes = (distanceKm.value / 5) * 60
  return `${Math.max(5, Math.round(minutes))} min`
})

const drivingTime = computed(() => {
  if (!userCoords.value) return '--'
  const minutes = (distanceKm.value / 50) * 60
  return `${Math.max(5, Math.round(minutes))} min`
})

const locationReady = computed(() => !!userCoords.value && !locationLoading.value && !locationError.value)

function requestGeolocation() {
  if (!navigator.geolocation) {
    locationError.value = "Géolocalisation non prise en charge par ce navigateur."
    return
  }

  locationLoading.value = true
  locationError.value = ''
  locationDenied.value = false

  navigator.geolocation.getCurrentPosition(
    (position) => {
      userCoords.value = {
        lat: position.coords.latitude,
        lon: position.coords.longitude,
      }
      locationLoading.value = false
    },
    (error) => {
      locationLoading.value = false
      if (error.code === error.PERMISSION_DENIED) {
        locationDenied.value = true
      } else {
        locationError.value = "Impossible de récupérer votre position."
      }
    },
  )
}

onMounted(async () => {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await api.get('/parametres/public/')
    etablissement.value = data
  } catch (e) {
    loadError.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
  requestGeolocation()
})
</script>
