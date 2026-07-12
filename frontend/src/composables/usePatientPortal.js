export function formatPatientDate(iso) {

  if (!iso) return '—'

  try {

    return new Date(iso).toLocaleString('fr-FR', {

      day: '2-digit',

      month: '2-digit',

      year: 'numeric',

      hour: '2-digit',

      minute: '2-digit',

    })

  } catch {

    return iso

  }

}



export function formatPatientDateShort(iso) {

  if (!iso) return '—'

  try {

    return new Date(iso).toLocaleDateString('fr-FR', {

      day: '2-digit',

      month: 'short',

      year: 'numeric',

    })

  } catch {

    return iso

  }

}



export function formatMontant(value) {

  if (value == null || value === '') return '—'

  const n = Number(value)

  return Number.isNaN(n) ? value : n.toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })

}



export function prescriptionStatutLabel(statut) {

  const map = {

    validee: 'Validée',

    brouillon: 'Brouillon',

    annulee: 'Annulée',

  }

  return map[statut] || statut

}



export function pharmacieStatutMeta(statutPharmacie) {

  const map = {

    en_attente: { label: 'En attente', icon: '⏳', badge: 'pending' },

    validee: { label: 'Validée', icon: '💊', badge: 'ok' },

    retiree: { label: 'Retirée', icon: '✅', badge: 'done' },

    annulee: { label: 'Annulée', icon: '✕', badge: 'alert' },

  }

  return map[statutPharmacie] || { label: statutPharmacie, icon: '💊', badge: 'pending' }

}



export function doseStatutMeta(dose) {

  if (dose.est_en_retard) {

    return { label: 'En retard', icon: '⚠️', badge: 'alert' }

  }

  const map = {

    planifiee: { label: 'À venir', icon: '🕐', badge: 'pending' },

    administree: { label: 'Fait', icon: '✓', badge: 'done' },

    annulee: { label: 'Annulée', icon: '✕', badge: 'alert' },

  }

  return map[dose.statut] || { label: dose.statut, icon: '•', badge: 'pending' }

}



export function hospitalisationStatutLabel(statut) {

  const map = {

    active: 'En cours',

    terminee: 'Terminée',

    annulee: 'Annulée',

  }

  return map[statut] || statut

}



export function factureStatutLabel(statut) {

  const map = {

    payee: 'Payée',

    partiellement_payee: 'Partiellement payée',

    validee: 'En attente de paiement',

    brouillon: 'Brouillon',

    annulee: 'Annulée',

  }

  return map[statut] || statut

}



export function factureStatutMeta(statut) {

  if (statut === 'payee') return { badge: 'done', icon: '✓' }

  if (statut === 'partiellement_payee') return { badge: 'pending', icon: '◐' }

  if (statut === 'validee') return { badge: 'pending', icon: '⏳' }

  return { badge: 'alert', icon: '•' }

}



export function rdvStatutLabel(statut) {

  const map = {

    planifie: 'Planifié',

    confirme: 'Validé',

    termine: 'Terminé',

    annule: 'Annulé',

    absent: 'Absent',

  }

  return map[statut] || statut

}



export function typeConsultationLabel(type) {

  return type === 'teleconsultation' ? 'Téléconsultation' : 'Présentiel'

}



export function notificationCategorieMeta(categorie) {

  const map = {

    rendez_vous: { icon: '📅', label: 'Rendez-vous' },

    alerte: { icon: '🩺', label: 'Alerte médicale' },

    facturation: { icon: '🧾', label: 'Facturation' },

    general: { icon: '💌', label: 'Secrétariat' },

  }

  return map[categorie] || { icon: '🔔', label: categorie || 'Information' }

}



export function constanteSummary(c) {

  const parts = []

  if (c.temperature != null) parts.push(`T° ${c.temperature}°C`)

  if (c.tension_systolique != null) {

    parts.push(`TA ${c.tension_systolique}/${c.tension_diastolique ?? '—'}`)

  }

  if (c.glycemie != null) parts.push(`Glycémie ${c.glycemie} g/L`)

  if (c.frequence_cardiaque != null) parts.push(`FC ${c.frequence_cardiaque}`)

  if (c.saturation_o2 != null) parts.push(`SpO₂ ${c.saturation_o2}%`)

  return parts.length ? parts.join(' · ') : 'Mesure enregistrée'

}



export const patientNavLinks = [

  { to: '/patient', label: 'Accueil', exact: true },

  { to: '/patient/hospitalisations', label: 'Hospitalisation' },

  { to: '/patient/rendez-vous', label: 'Rendez-vous' },

  { to: '/patient/soins', label: 'Soins infirmiers' },

  { to: '/patient/prescriptions', label: 'Pharmacie' },

  { to: '/patient/laboratoire', label: 'Laboratoire' },

  { to: '/patient/factures', label: 'Factures' },

  { to: '/patient/notifications', label: 'Notifications', badge: true },

  { to: '/patient/messages', label: 'Messagerie' },

  { to: '/patient/profil', label: 'Profil' },

]


