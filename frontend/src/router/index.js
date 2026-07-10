import { createRouter, createWebHistory } from 'vue-router'

import {
  ASSURANCE,
  AUDIT,
  DOCUMENTS,
  FACTURATION_READ,
  FORMATION_RH,
  HOSPITALISATION_READ,
  INVENTAIRE,
  LABO_READ,
  LOCALISATION_READ,
  NOTIFICATIONS,
  PARAMETRES,
  PATIENT_ROLE,
  PATIENTS_READ,
  PERSONNEL_INFIRMIERS,
  PERSONNEL_MEDECINS,
  PHARMACIE_READ,
  PRESCRIPTIONS_READ,
  RDV_READ,
  SERVICES_MEDICAUX,
  SOINS_WRITE,
  STATISTIQUES,
  STAFF_ROLES,
  TELECONSULTATION,
  URGENCES,
} from '../permissions.js'
import { useAuthStore } from '../stores/auth.js'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { public: true, title: 'Connexion' },
    },
    {
      path: '/validate-account',
      name: 'validate-account',
      component: () => import('../views/ValidateAccountView.vue'),
      meta: { public: true, title: 'Validation du compte' },
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('../views/LocalisationView.vue'),
      meta: { public: true, title: 'Contact & Localisation' },
    },
    {
      path: '/patient',
      component: () => import('../layouts/PatientLayout.vue'),
      meta: { patientOnly: true },
      children: [
        {
          path: '',
          name: 'patient-home',
          component: () => import('../views/patient/PatientHomeView.vue'),
          meta: { title: 'Mon espace', patientOnly: true },
        },
        {
          path: 'rendez-vous',
          name: 'patient-rendez-vous',
          component: () => import('../views/patient/PatientRendezVousView.vue'),
          meta: { title: 'Mes rendez-vous', patientOnly: true },
        },
        {
          path: 'soins',
          name: 'patient-soins',
          component: () => import('../views/patient/PatientSoinsView.vue'),
          meta: { title: 'Suivi des soins', patientOnly: true },
        },
        {
          path: 'prescriptions',
          name: 'patient-prescriptions',
          component: () => import('../views/patient/PatientPrescriptionsView.vue'),
          meta: { title: 'Mes prescriptions', patientOnly: true },
        },
        {
          path: 'laboratoire',
          name: 'patient-laboratoire',
          component: () => import('../views/patient/PatientLaboratoireView.vue'),
          meta: { title: 'Résultats laboratoire', patientOnly: true },
        },
        {
          path: 'factures',
          name: 'patient-factures',
          component: () => import('../views/patient/PatientFacturesView.vue'),
          meta: { title: 'Mes factures', patientOnly: true },
        },
        {
          path: 'notifications',
          name: 'patient-notifications',
          component: () => import('../views/patient/PatientNotificationsView.vue'),
          meta: { title: 'Notifications', patientOnly: true },
        },
        {
          path: 'profil',
          name: 'patient-profil',
          component: () => import('../views/patient/PatientProfilView.vue'),
          meta: { title: 'Mon profil', patientOnly: true },
        },
      ],
    },
    {
      path: '/',
      component: () => import('../layouts/AppLayout.vue'),
      meta: { staffOnly: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
          meta: { title: 'Tableau de bord', roles: STAFF_ROLES },
        },
        {
          path: 'patients',
          name: 'patients',
          component: () => import('../views/PatientsView.vue'),
          meta: { title: 'Patients', roles: PATIENTS_READ },
        },
        {
          path: 'rendez-vous',
          name: 'rendez-vous',
          component: () => import('../views/RendezVousView.vue'),
          meta: { title: 'Rendez-vous', roles: RDV_READ },
        },
        {
          path: 'hospitalisations',
          name: 'hospitalisations',
          component: () => import('../views/HospitalisationsView.vue'),
          meta: { title: 'Hospitalisations', roles: HOSPITALISATION_READ },
        },
        {
          path: 'prescriptions',
          name: 'prescriptions',
          component: () => import('../views/PrescriptionsView.vue'),
          meta: { title: 'Prescriptions', roles: PRESCRIPTIONS_READ },
        },
        {
          path: 'resultats-medicaux',
          name: 'resultats-medicaux',
          component: () => import('../views/LaboratoireView.vue'),
          meta: { title: 'Résultats médicaux', roles: LABO_READ },
        },
        {
          path: 'laboratoire',
          redirect: { name: 'resultats-medicaux' },
        },
        {
          path: 'soins',
          name: 'soins',
          component: () => import('../views/SoinsView.vue'),
          meta: { title: 'Soins infirmiers', roles: SOINS_WRITE },
        },
        {
          path: 'pharmacie',
          name: 'pharmacie',
          component: () => import('../views/PharmacieView.vue'),
          meta: { title: 'Pharmacie', roles: PHARMACIE_READ },
        },
        {
          path: 'facturation',
          name: 'facturation',
          component: () => import('../views/FacturationView.vue'),
          meta: { title: 'Facturation', roles: FACTURATION_READ },
        },
        {
          path: 'audit',
          name: 'audit',
          component: () => import('../views/AuditView.vue'),
          meta: { title: "Journal d'audit", roles: AUDIT },
        },
        {
          path: 'statistiques',
          name: 'statistiques',
          component: () => import('../views/StatistiquesView.vue'),
          meta: {
            title: 'Statistiques & Rapports',
            subtitle: 'Tableaux de bord analytiques et exports',
            icon: 'dashboard',
            roles: STATISTIQUES,
          },
        },
        {
          path: 'assurance',
          name: 'assurance',
          component: () => import('../views/AssuranceView.vue'),
          meta: {
            title: 'Assurance & Mutuelles',
            subtitle: 'Tiers payant et conventions',
            icon: 'billing',
            roles: ASSURANCE,
          },
        },
        {
          path: 'services',
          name: 'services',
          component: () => import('../views/ServicesView.vue'),
          meta: {
            title: 'Services médicaux',
            subtitle: 'Organisation des pôles et unités',
            icon: 'hospital',
            roles: SERVICES_MEDICAUX,
          },
        },
        {
          path: 'personnel/medecins',
          name: 'personnel-medecins',
          component: () => import('../views/PersonnelView.vue'),
          meta: {
            title: 'Personnel — Médecins',
            subtitle: 'Annuaire et affectations médicales',
            icon: 'prescription',
            roles: PERSONNEL_MEDECINS,
          },
        },
        {
          path: 'personnel/infirmiers',
          name: 'personnel-infirmiers',
          component: () => import('../views/PersonnelView.vue'),
          meta: {
            title: 'Personnel — Infirmiers',
            subtitle: 'Planning et équipes de soins',
            icon: 'care',
            roles: PERSONNEL_INFIRMIERS,
          },
        },
        {
          path: 'localisation',
          name: 'localisation',
          component: () => import('../views/LocalisationView.vue'),
          meta: {
            title: 'Contact & Localisation',
            subtitle: 'Carte, coordonnées et itinéraire',
            icon: 'location',
            roles: LOCALISATION_READ,
          },
        },
        {
          path: 'documents',
          name: 'documents',
          component: () => import('../views/DocumentsView.vue'),
          meta: {
            title: 'Documents médicaux',
            subtitle: 'Archivage et partage sécurisé',
            icon: 'billing',
            roles: DOCUMENTS,
          },
        },
        {
          path: 'notifications',
          name: 'notifications',
          component: () => import('../views/NotificationsView.vue'),
          meta: {
            title: 'Notifications',
            subtitle: 'Alertes staff et rappels',
            icon: 'dashboard',
            roles: NOTIFICATIONS,
          },
        },
        {
          path: 'urgences',
          name: 'urgences',
          component: () => import('../views/UrgencesView.vue'),
          meta: {
            title: 'Urgences',
            subtitle: 'Flux triage et prise en charge',
            icon: 'hospital',
            roles: URGENCES,
          },
        },
        {
          path: 'teleconsultation',
          name: 'teleconsultation',
          component: () => import('../views/TeleconsultationView.vue'),
          meta: {
            title: 'Téléconsultation',
            subtitle: 'Consultations à distance',
            icon: 'calendar',
            roles: TELECONSULTATION,
          },
        },
        {
          path: 'inventaire',
          name: 'inventaire',
          component: () => import('../views/InventaireView.vue'),
          meta: {
            title: 'Inventaire',
            subtitle: 'Stocks consommables et équipements',
            icon: 'pharmacy',
            roles: INVENTAIRE,
          },
        },
        {
          path: 'formation',
          name: 'formation',
          component: () => import('../views/FormationView.vue'),
          meta: {
            title: 'Formation & RH',
            subtitle: 'Compétences et formations internes',
            icon: 'care',
            roles: FORMATION_RH,
          },
        },
        {
          path: 'parametres',
          name: 'parametres',
          component: () => import('../views/ParametresView.vue'),
          meta: {
            title: 'Paramètres',
            subtitle: 'Configuration système et sécurité',
            icon: 'dashboard',
            roles: PARAMETRES,
          },
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  if (!auth.user && !to.meta.public) {
    const ok = await auth.restoreSession()
    if (!ok && !to.meta.public) return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: auth.homeRoute }
  }

  if (auth.isPatient && to.meta.staffOnly) {
    return { name: 'patient-home' }
  }

  if (auth.isStaff && to.meta.patientOnly) {
    return { name: 'dashboard' }
  }

  if (to.meta.roles && auth.user && !to.meta.roles.includes(auth.user.role)) {
    return auth.isPatient ? { name: 'patient-home' } : { name: 'dashboard' }
  }

  return true
})

export default router
