<template>
  <div class="min-h-screen bg-slate-50 p-4 sm:p-6 lg:p-8">
    <div class="mx-auto max-w-7xl space-y-6">
      <header class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Formation & RH</h1>
            <p class="mt-1 text-sm text-slate-600">Formations, certifications, conformité et planning de gardes</p>
          </div>
          <button class="inline-flex items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100" type="button" @click="loadAll">Actualiser</button>
        </div>
      </header>

      <div v-if="message" class="rounded-3xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ message }}</div>
      <div v-if="error" class="rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{{ error }}</div>

      <section class="grid gap-4 md:grid-cols-4">
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Formations actives</span>
          <strong class="mt-4 block text-3xl font-semibold text-slate-900">{{ stats.formations_actives }}</strong>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Personnel qualifié</span>
          <strong class="mt-4 block text-3xl font-semibold text-slate-900">{{ stats.personnel_qualifie_pct }}%</strong>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Certifications à renouveler</span>
          <strong class="mt-4 block text-3xl font-semibold text-amber-600">{{ stats.certifications_a_renouveler }}</strong>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
          <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Gardes cette semaine</span>
          <strong class="mt-4 block text-3xl font-semibold text-slate-900">{{ stats.gardes_semaine }}</strong>
        </article>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex flex-wrap gap-3 rounded-3xl bg-slate-50 p-2">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="rounded-2xl px-4 py-2 text-sm font-semibold transition"
            :class="activeTab === tab.id ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>

        <div v-if="loading" class="mt-6 rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Chargement…</div>

        <!-- Formations -->
        <div v-else-if="activeTab === 'formations'" class="mt-6 space-y-6">
          <form class="grid gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-5 md:grid-cols-2" @submit.prevent="createFormation">
            <h2 class="md:col-span-2 text-lg font-semibold text-slate-900">Nouvelle formation</h2>
            <input v-model="formationForm.titre" required placeholder="Titre" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <input v-model="formationForm.formateur" required placeholder="Formateur" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <input v-model="formationForm.date_debut" required type="date" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <input v-model="formationForm.date_fin" required type="date" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <input v-model.number="formationForm.capacite_max" required type="number" min="1" placeholder="Capacité max" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <button class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800" type="submit" :disabled="saving">Créer</button>
          </form>

          <div v-if="formations.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Aucune formation.</div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold">Titre</th>
                  <th class="px-4 py-3 text-left font-semibold">Formateur</th>
                  <th class="px-4 py-3 text-left font-semibold">Dates</th>
                  <th class="px-4 py-3 text-left font-semibold">Participants</th>
                  <th class="px-4 py-3 text-left font-semibold">Statut</th>
                  <th class="px-4 py-3 text-left font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-for="training in formations" :key="training.id" class="hover:bg-slate-50">
                  <td class="px-4 py-4 font-semibold text-slate-900">{{ training.titre }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ training.formateur }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ training.date_debut }} → {{ training.date_fin }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ training.participants_count }}/{{ training.capacite_max }}</td>
                  <td class="px-4 py-4"><span :class="trainingStatusClass(training.statut)">{{ training.statut_label }}</span></td>
                  <td class="px-4 py-4">
                    <div class="flex flex-wrap items-center gap-2">
                      <select
                        class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm"
                        :value="training.statut"
                        @change="updateFormationStatut(training, $event.target.value)"
                      >
                        <option value="programmee">Programmée</option>
                        <option value="en_cours">En cours</option>
                        <option value="terminee">Terminée</option>
                        <option value="annulee">Annulée</option>
                      </select>
                      <button class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="toggleInscriptions(training)">
                        {{ expandedFormationId === training.id ? 'Masquer' : 'Inscriptions' }}
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="expandedFormationId === training.id" :key="`${training.id}-ins`">
                  <td colspan="6" class="bg-slate-50 px-4 py-4">
                    <div class="space-y-4">
                      <form class="flex flex-wrap items-end gap-3" @submit.prevent="inscrireFormation(training)">
                        <select v-model="inscriptionForm.personnel_id" required class="min-w-[200px] rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm">
                          <option value="">— Personnel —</option>
                          <option v-for="s in staffOptions" :key="s.id" :value="s.id">{{ s.full_name }}</option>
                        </select>
                        <button type="submit" class="rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800" :disabled="saving">Inscrire</button>
                      </form>
                      <div v-if="formationInscriptions.length === 0" class="text-sm text-slate-500">Aucune inscription.</div>
                      <table v-else class="min-w-full text-sm">
                        <thead>
                          <tr class="text-left text-slate-500">
                            <th class="py-2 pr-4 font-semibold">Personnel</th>
                            <th class="py-2 pr-4 font-semibold">Statut</th>
                            <th class="py-2 font-semibold">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="ins in formationInscriptions" :key="ins.id" class="border-t border-slate-200">
                            <td class="py-2 pr-4 text-slate-700">{{ ins.personnel_nom }}</td>
                            <td class="py-2 pr-4 text-slate-700">{{ ins.statut }}</td>
                            <td class="py-2">
                              <button
                                v-if="ins.statut !== 'valide'"
                                class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-100"
                                @click="validerInscription(training, ins)"
                              >
                                Valider
                              </button>
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Certifications -->
        <div v-else-if="activeTab === 'certifications'" class="mt-6 space-y-6">
          <form class="grid gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-5 md:grid-cols-2" @submit.prevent="createCertCatalogue">
            <h2 class="md:col-span-2 text-lg font-semibold text-slate-900">Ajouter au catalogue</h2>
            <input v-model="certCatalogueForm.nom" required placeholder="Nom de la certification" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <select v-model="certCatalogueForm.type_certification" required class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option value="obligatoire">Obligatoire</option>
              <option value="recommandee">Recommandée</option>
              <option value="specialite">Spécialité</option>
            </select>
            <input v-model.number="certCatalogueForm.duree_validite_mois" type="number" min="1" placeholder="Durée validité (mois)" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <button class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800" type="submit" :disabled="saving">Ajouter</button>
          </form>

          <form class="grid gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-5 md:grid-cols-2" @submit.prevent="assignCertification">
            <h2 class="md:col-span-2 text-lg font-semibold text-slate-900">Attribuer une certification</h2>
            <select v-model="assignCertForm.certification_id" required class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option value="">— Certification —</option>
              <option v-for="c in certifications" :key="c.id" :value="c.id">{{ c.nom }}</option>
            </select>
            <select v-model="assignCertForm.personnel_id" required class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option value="">— Personnel —</option>
              <option v-for="s in staffOptions" :key="s.id" :value="s.id">{{ s.full_name }}</option>
            </select>
            <input v-model="assignCertForm.date_obtention" required type="date" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <input v-model="assignCertForm.date_expiration" required type="date" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <input v-model="assignCertForm.numero_certificat" placeholder="N° certificat (optionnel)" class="md:col-span-2 rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <button class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800" type="submit" :disabled="saving">Attribuer</button>
          </form>

          <div v-if="certifications.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Aucune certification.</div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold">Nom</th>
                  <th class="px-4 py-3 text-left font-semibold">Type</th>
                  <th class="px-4 py-3 text-left font-semibold">Détenteurs</th>
                  <th class="px-4 py-3 text-left font-semibold">Expiration moyenne</th>
                  <th class="px-4 py-3 text-left font-semibold">Renouvellement</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-for="cert in certifications" :key="cert.id" class="hover:bg-slate-50">
                  <td class="px-4 py-4 font-semibold text-slate-900">{{ cert.nom }}</td>
                  <td class="px-4 py-4"><span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase text-slate-600">{{ cert.type_certification }}</span></td>
                  <td class="px-4 py-4 text-slate-700">{{ cert.holders_count }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ cert.expiration_moyenne || '—' }}</td>
                  <td class="px-4 py-4"><span :class="certStatusClass(cert.renewal_status)">{{ cert.renewal_status }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="certPersonnel.length" class="overflow-x-auto">
            <h3 class="mb-3 text-base font-semibold text-slate-900">Certifications du personnel</h3>
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold">Personnel</th>
                  <th class="px-4 py-3 text-left font-semibold">Certification</th>
                  <th class="px-4 py-3 text-left font-semibold">Expiration</th>
                  <th class="px-4 py-3 text-left font-semibold">Statut</th>
                  <th class="px-4 py-3 text-left font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-for="cp in certPersonnel" :key="cp.id" class="hover:bg-slate-50">
                  <td class="px-4 py-4 text-slate-700">{{ cp.personnel_nom }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ cp.certification_nom }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ cp.date_expiration }}</td>
                  <td class="px-4 py-4"><span :class="certRenewalClass(cp.statut_renouvellement)">{{ cp.statut_renouvellement }}</span></td>
                  <td class="px-4 py-4">
                    <button
                      v-if="cp.statut_renouvellement !== 'valide'"
                      class="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                      @click="renewCertification(cp)"
                    >
                      Renouveler
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Personnel conformité -->
        <div v-else-if="activeTab === 'staff'" class="mt-6">
          <div v-if="staff.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Aucun personnel.</div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold">Nom</th>
                  <th class="px-4 py-3 text-left font-semibold">Poste</th>
                  <th class="px-4 py-3 text-left font-semibold">Formations complétées</th>
                  <th class="px-4 py-3 text-left font-semibold">Certifications actives</th>
                  <th class="px-4 py-3 text-left font-semibold">Conformité</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-for="member in staff" :key="member.id" class="hover:bg-slate-50">
                  <td class="px-4 py-4">
                    <div class="flex items-center gap-3">
                      <img :src="member.photo_url" :alt="member.full_name" class="h-10 w-10 rounded-full object-cover" />
                      <strong class="text-slate-900">{{ member.full_name }}</strong>
                    </div>
                  </td>
                  <td class="px-4 py-4 text-slate-700">{{ member.role_label }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ member.trainings_completed }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ member.active_certs }}</td>
                  <td class="px-4 py-4"><span :class="staffStatusClass(member.compliant)">{{ member.compliant ? 'Conforme' : 'À mettre à jour' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Planning gardes -->
        <div v-else-if="activeTab === 'gardes'" class="mt-6 space-y-6">
          <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-7">
            <button
              v-for="day in weekDays"
              :key="day.date"
              type="button"
              class="flex flex-col items-center rounded-3xl border border-slate-200 bg-slate-50 px-3 py-4 text-sm transition hover:border-blue-400"
              :class="filterDate === day.date ? 'border-blue-500 bg-blue-50' : ''"
              @click="selectDay(day.date)"
            >
              <span class="text-xs uppercase tracking-[0.2em] text-slate-500">{{ day.label }}</span>
              <span class="mt-2 text-xl font-semibold text-slate-900">{{ day.num }}</span>
              <span v-if="day.count" class="mt-2 rounded-full bg-blue-600 px-2.5 py-1 text-[11px] font-semibold text-white">{{ day.count }}</span>
            </button>
          </div>

          <form class="grid gap-4 rounded-3xl border border-slate-200 bg-slate-50 p-5 md:grid-cols-2" @submit.prevent="createGarde">
            <h2 class="md:col-span-2 text-lg font-semibold text-slate-900">Planifier une garde</h2>
            <select v-model="gardeForm.personnel_id" required class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option value="">— Personnel —</option>
              <option v-for="s in staffOptions" :key="s.id" :value="s.id">{{ s.full_name }} ({{ s.role_label }})</option>
            </select>
            <select v-model="gardeForm.type_garde" required class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500">
              <option value="jour">Jour</option>
              <option value="nuit">Nuit</option>
              <option value="week_end">Week-end</option>
              <option value="urgence">Urgence</option>
            </select>
            <input v-model="gardeForm.date_debut" required type="datetime-local" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <input v-model="gardeForm.date_fin" required type="datetime-local" class="rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <input v-model="gardeForm.notes" placeholder="Notes (optionnel)" class="md:col-span-2 rounded-2xl border border-slate-200 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500" />
            <button class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800" type="submit" :disabled="saving">Planifier</button>
          </form>

          <div v-if="gardes.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">Aucune garde pour cette période.</div>
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-slate-500">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold">Personnel</th>
                  <th class="px-4 py-3 text-left font-semibold">Type</th>
                  <th class="px-4 py-3 text-left font-semibold">Début</th>
                  <th class="px-4 py-3 text-left font-semibold">Fin</th>
                  <th class="px-4 py-3 text-left font-semibold">Service</th>
                  <th class="px-4 py-3 text-left font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-200 bg-white">
                <tr v-for="garde in gardes" :key="garde.id" class="hover:bg-slate-50">
                  <td class="px-4 py-4 text-slate-700">{{ garde.personnel_nom }}</td>
                  <td class="px-4 py-4"><span class="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">{{ garde.type_garde_label }}</span></td>
                  <td class="px-4 py-4 text-slate-700">{{ formatDateTime(garde.date_debut) }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ formatDateTime(garde.date_fin) }}</td>
                  <td class="px-4 py-4 text-slate-700">{{ garde.service_nom || '—' }}</td>
                  <td class="px-4 py-4">
                    <button class="rounded-2xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700 hover:bg-rose-100" @click="deleteGarde(garde)">Supprimer</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <div v-if="showRenewModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="closeRenewModal">
        <form class="w-full max-w-md space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-xl" @submit.prevent="submitRenew">
          <h2 class="text-lg font-semibold text-slate-900">Renouveler la certification</h2>
          <p class="text-sm text-slate-600">{{ renewTarget?.personnel_nom }} — {{ renewTarget?.certification_nom }}</p>
          <input v-model="renewForm.date_obtention" required type="date" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
          <input v-model="renewForm.date_expiration" required type="date" class="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none focus:border-slate-400" />
          <div class="flex justify-end gap-2 pt-2">
            <button type="button" class="rounded-2xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50" @click="closeRenewModal">Annuler</button>
            <button type="submit" class="rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800" :disabled="saving">Renouveler</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import api, { getErrorMessage, unwrapList } from '../api/client.js'

const tabs = [
  { id: 'formations', label: 'Formations' },
  { id: 'certifications', label: 'Certifications' },
  { id: 'staff', label: 'Personnel' },
  { id: 'gardes', label: 'Planning gardes' },
]

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const message = ref('')
const activeTab = ref('formations')

const stats = ref({
  formations_actives: 0,
  personnel_qualifie_pct: 0,
  certifications_a_renouveler: 0,
  gardes_semaine: 0,
})

const formations = ref([])
const certifications = ref([])
const certPersonnel = ref([])
const staff = ref([])
const gardes = ref([])
const staffOptions = ref([])
const weekDaysRaw = ref([])
const expandedFormationId = ref(null)
const formationInscriptions = ref([])
const showRenewModal = ref(false)
const renewTarget = ref(null)

const filterDate = ref('')
const formationForm = ref({
  titre: '',
  formateur: '',
  date_debut: '',
  date_fin: '',
  capacite_max: 20,
})
const inscriptionForm = ref({ personnel_id: '' })
const certCatalogueForm = ref({ nom: '', type_certification: 'obligatoire', duree_validite_mois: 12 })
const assignCertForm = ref({
  certification_id: '',
  personnel_id: '',
  date_obtention: new Date().toISOString().slice(0, 10),
  date_expiration: '',
  numero_certificat: '',
})
const renewForm = ref({ date_obtention: '', date_expiration: '' })
const gardeForm = ref({
  personnel_id: '',
  type_garde: 'jour',
  date_debut: '',
  date_fin: '',
  notes: '',
})

const weekDays = computed(() => {
  const labels = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
  return weekDaysRaw.value.map((day, i) => ({
    ...day,
    label: labels[i] || '',
    num: day.date.slice(8, 10),
  }))
})

function trainingStatusClass(status) {
  const map = {
    programmee: 'inline-flex rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700',
    en_cours: 'inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700',
    terminee: 'inline-flex rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700',
    annulee: 'inline-flex rounded-full bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-700',
  }
  return map[status] || map.terminee
}

function certStatusClass(status) {
  return status === 'À renouveler'
    ? 'inline-flex rounded-full bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-700'
    : 'inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700'
}

function certRenewalClass(status) {
  if (status === 'expirée' || status === 'à renouveler') {
    return 'inline-flex rounded-full bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-700'
  }
  return 'inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700'
}

function staffStatusClass(compliant) {
  return compliant
    ? 'inline-flex rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700'
    : 'inline-flex rounded-full bg-rose-100 px-2.5 py-1 text-xs font-semibold text-rose-700'
}

function formatDateTime(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('fr-FR', { dateStyle: 'short', timeStyle: 'short' })
}

function toIsoLocal(value) {
  if (!value) return null
  const d = new Date(value)
  return d.toISOString()
}

async function loadStats() {
  const { data } = await api.get('/rh/stats/')
  stats.value = data
}

async function loadFormations() {
  const { data } = await api.get('/rh/formations/')
  formations.value = unwrapList(data)
}

async function loadCertifications() {
  const { data } = await api.get('/rh/certifications/')
  certifications.value = unwrapList(data)
  const res = await api.get('/rh/certifications/personnel/')
  certPersonnel.value = unwrapList(res.data)
}

async function loadStaff() {
  const { data } = await api.get('/rh/personnel/')
  staff.value = unwrapList(data)
}

async function loadStaffOptions() {
  const { data } = await api.get('/rh/staff/')
  staffOptions.value = unwrapList(data)
}

async function loadWeekDays() {
  const { data } = await api.get('/rh/gardes/semaine/')
  weekDaysRaw.value = unwrapList(data)
  if (!filterDate.value && data.length) {
    filterDate.value = data[0].date
  }
}

async function loadGardes() {
  const params = new URLSearchParams()
  if (filterDate.value) {
    params.set('date_debut', filterDate.value)
    params.set('date_fin', filterDate.value)
  }
  const { data } = await api.get(`/rh/gardes/${params.toString() ? `?${params.toString()}` : ''}`)
  gardes.value = unwrapList(data)
}

async function loadAll() {
  loading.value = true
  error.value = ''
  try {
    await Promise.all([
      loadStats(),
      loadFormations(),
      loadCertifications(),
      loadStaff(),
      loadStaffOptions(),
      loadWeekDays(),
      loadGardes(),
    ])
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    loading.value = false
  }
}

async function createFormation() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await api.post('/rh/formations/', formationForm.value)
    message.value = 'Formation créée.'
    formationForm.value = { titre: '', formateur: '', date_debut: '', date_fin: '', capacite_max: 20 }
    await loadFormations()
    await loadStats()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function updateFormationStatut(training, statut) {
  try {
    await api.post(`/rh/formations/${training.id}/statut/`, { version: training.version, statut })
    message.value = 'Statut mis à jour.'
    await loadFormations()
    await loadStats()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function loadFormationInscriptions(formationId) {
  const { data } = await api.get(`/rh/formations/${formationId}/inscriptions/`)
  formationInscriptions.value = unwrapList(data)
}

async function toggleInscriptions(training) {
  if (expandedFormationId.value === training.id) {
    expandedFormationId.value = null
    formationInscriptions.value = []
    return
  }
  expandedFormationId.value = training.id
  inscriptionForm.value.personnel_id = ''
  try {
    await loadFormationInscriptions(training.id)
  } catch (e) {
    error.value = getErrorMessage(e)
    formationInscriptions.value = []
  }
}

async function inscrireFormation(training) {
  saving.value = true
  error.value = ''
  try {
    await api.post(`/rh/formations/${training.id}/inscriptions/`, {
      personnel_id: Number(inscriptionForm.value.personnel_id),
    })
    message.value = 'Personnel inscrit.'
    inscriptionForm.value.personnel_id = ''
    await loadFormationInscriptions(training.id)
    await loadFormations()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function validerInscription(training, ins) {
  try {
    await api.post(`/rh/formations/${training.id}/inscriptions/${ins.id}/valider/`)
    message.value = 'Inscription validée.'
    await loadFormationInscriptions(training.id)
    await loadStaff()
    await loadStats()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

async function createCertCatalogue() {
  saving.value = true
  error.value = ''
  try {
    await api.post('/rh/certifications/', certCatalogueForm.value)
    message.value = 'Certification ajoutée au catalogue.'
    certCatalogueForm.value = { nom: '', type_certification: 'obligatoire', duree_validite_mois: 12 }
    await loadCertifications()
    await loadStats()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function assignCertification() {
  saving.value = true
  error.value = ''
  try {
    await api.post('/rh/certifications/personnel/', {
      certification_id: assignCertForm.value.certification_id,
      personnel_id: Number(assignCertForm.value.personnel_id),
      date_obtention: assignCertForm.value.date_obtention,
      date_expiration: assignCertForm.value.date_expiration,
      numero_certificat: assignCertForm.value.numero_certificat,
    })
    message.value = 'Certification attribuée.'
    assignCertForm.value = {
      certification_id: '',
      personnel_id: '',
      date_obtention: new Date().toISOString().slice(0, 10),
      date_expiration: '',
      numero_certificat: '',
    }
    await loadCertifications()
    await loadStaff()
    await loadStats()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

function openRenewModal(cp) {
  renewTarget.value = cp
  renewForm.value = {
    date_obtention: new Date().toISOString().slice(0, 10),
    date_expiration: cp.date_expiration,
  }
  showRenewModal.value = true
}

function closeRenewModal() {
  showRenewModal.value = false
  renewTarget.value = null
}

async function submitRenew() {
  if (!renewTarget.value) return
  saving.value = true
  error.value = ''
  try {
    await api.post(`/rh/certifications/personnel/${renewTarget.value.id}/renouveler/`, {
      version: renewTarget.value.version,
      date_obtention: renewForm.value.date_obtention,
      date_expiration: renewForm.value.date_expiration,
    })
    message.value = 'Certification renouvelée.'
    closeRenewModal()
    await loadCertifications()
    await loadStaff()
    await loadStats()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function renewCertification(cp) {
  openRenewModal(cp)
}

async function createGarde() {
  saving.value = true
  error.value = ''
  message.value = ''
  try {
    await api.post('/rh/gardes/', {
      personnel_id: Number(gardeForm.value.personnel_id),
      type_garde: gardeForm.value.type_garde,
      date_debut: toIsoLocal(gardeForm.value.date_debut),
      date_fin: toIsoLocal(gardeForm.value.date_fin),
      notes: gardeForm.value.notes,
    })
    message.value = 'Garde planifiée.'
    gardeForm.value = { personnel_id: '', type_garde: 'jour', date_debut: '', date_fin: '', notes: '' }
    await loadGardes()
    await loadWeekDays()
    await loadStats()
  } catch (e) {
    error.value = getErrorMessage(e)
  } finally {
    saving.value = false
  }
}

async function deleteGarde(garde) {
  if (!confirm(`Supprimer la garde de ${garde.personnel_nom} ?`)) return
  try {
    await api.delete(`/rh/gardes/${garde.id}/?version=${garde.version}`)
    message.value = 'Garde supprimée.'
    await loadGardes()
    await loadWeekDays()
    await loadStats()
  } catch (e) {
    error.value = getErrorMessage(e)
  }
}

function selectDay(date) {
  filterDate.value = date
  loadGardes()
}

watch(activeTab, (tab) => {
  if (tab === 'gardes') loadGardes()
})

onMounted(loadAll)
</script>
