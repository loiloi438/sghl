import {
  ASSURANCE,
  AUDIT,
  CAISSE_READ,
  DASHBOARD,
  DOCUMENTS,
  FACTURATION_READ,
  FORMATION_RH,
  HOSPITALISATION_READ,
  INVENTAIRE,
  LABO_READ,
  LOCALISATION_READ,
  NOTIFICATIONS,
  PARAMETRES,
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
  hasRole,
} from '../permissions.js'

export const NAV_SECTIONS = [
  {
    id: 'home',
    label: 'Accueil',
    items: [
      {
        to: '/secretariat',
        name: 'secretariat',
        label: 'Secrétariat',
        icon: 'calendar',
        roles: ['admin', 'secretaire'],
      },
      {
        to: '/',
        name: 'dashboard',
        label: 'Tableau de bord',
        icon: 'dashboard',
        roles: DASHBOARD,
      },
      {
        to: '/profil',
        name: 'profil',
        label: 'Mon compte',
        icon: 'patients',
        roles: STAFF_ROLES,
      },
    ],
  },
  {
    id: 'clinical',
    label: 'Cliniques',
    items: [
      { to: '/patients', name: 'patients', label: 'Patients', icon: 'patients', roles: PATIENTS_READ },
      { to: '/rendez-vous', name: 'rendez-vous', label: 'Rendez-vous', icon: 'calendar', roles: RDV_READ },
      { to: '/prescriptions', name: 'prescriptions', label: 'Prescriptions', icon: 'prescription', roles: PRESCRIPTIONS_READ },
      { to: '/resultats-medicaux', name: 'resultats-medicaux', label: 'Résultats', icon: 'lab', roles: LABO_READ },
    ],
  },
  {
    id: 'operations',
    label: 'Opérations',
    items: [
      { to: '/hospitalisations', name: 'hospitalisations', label: 'Hospitalisations', icon: 'hospital', roles: HOSPITALISATION_READ },
      { to: '/soins', name: 'soins', label: 'Soins infirmiers', icon: 'care', roles: SOINS_WRITE },
      { to: '/pharmacie', name: 'pharmacie', label: 'Pharmacie', icon: 'pharmacy', roles: PHARMACIE_READ },
    ],
  },
  {
    id: 'administration',
    label: 'Administration',
    items: [
      { to: '/caisse', name: 'caisse', label: 'Caisse & Secrétariat', icon: 'billing', roles: CAISSE_READ },
      { to: '/facturation', name: 'facturation', label: 'Facturation', icon: 'billing', roles: FACTURATION_READ },
      { to: '/statistiques', name: 'statistiques', label: 'Statistiques & Rapports', icon: 'dashboard', roles: STATISTIQUES },
      { to: '/assurance', name: 'assurance', label: 'Assurance & Mutuelles', icon: 'billing', roles: ASSURANCE },
      { to: '/audit', name: 'audit', label: "Journal d'audit", icon: 'dashboard', roles: AUDIT },
    ],
  },
  {
    id: 'resources',
    label: 'Ressources',
    items: [
      { to: '/services', name: 'services', label: 'Services médicaux', icon: 'hospital', roles: SERVICES_MEDICAUX },
      {
        id: 'personnel',
        label: 'Personnel hospitalier',
        icon: 'patients',
        roles: [...new Set([...PERSONNEL_MEDECINS, ...PERSONNEL_INFIRMIERS])],
        children: [
          { to: '/personnel/medecins', name: 'personnel-medecins', label: 'Médecins', icon: 'prescription', roles: PERSONNEL_MEDECINS },
          { to: '/personnel/infirmiers', name: 'personnel-infirmiers', label: 'Infirmiers', icon: 'care', roles: PERSONNEL_INFIRMIERS },
        ],
      },
      { to: '/documents', name: 'documents', label: 'Documents médicaux', icon: 'billing', roles: DOCUMENTS },
    ],
  },
  {
    id: 'complementary',
    label: 'Complémentaires',
    items: [
      { to: '/messagerie', name: 'messagerie', label: 'Messagerie', icon: 'care', roles: STAFF_ROLES },
      { to: '/notifications', name: 'notifications', label: 'Notifications', icon: 'dashboard', roles: NOTIFICATIONS },
      { to: '/urgences', name: 'urgences', label: 'Urgences', icon: 'hospital', roles: URGENCES },
      { to: '/localisation', name: 'localisation', label: 'Contact & Localisation', icon: 'location', roles: LOCALISATION_READ },
      { to: '/teleconsultation', name: 'teleconsultation', label: 'Téléconsultation', icon: 'calendar', roles: TELECONSULTATION },
      { to: '/inventaire', name: 'inventaire', label: 'Inventaire', icon: 'pharmacy', roles: INVENTAIRE },
      { to: '/formation', name: 'formation', label: 'Formation & RH', icon: 'care', roles: FORMATION_RH },
      { to: '/parametres', name: 'parametres', label: 'Paramètres', icon: 'dashboard', roles: PARAMETRES },
    ],
  },
]

/** Navigation épurée — secrétaire : RDV, caisse, messagerie (sans modules cliniques). */
export const SECRETARIAT_NAV_SECTIONS = [
  {
    id: 'home',
    label: 'Accueil',
    items: [
      {
        to: '/secretariat',
        name: 'secretariat',
        label: 'Secrétariat',
        icon: 'calendar',
        roles: ['admin', 'secretaire'],
      },
      {
        to: '/profil',
        name: 'profil',
        label: 'Mon compte',
        icon: 'patients',
        roles: ['secretaire'],
      },
    ],
  },
  {
    id: 'secretariat',
    label: 'Secrétariat',
    items: [
      { to: '/rendez-vous', name: 'rendez-vous', label: 'Rendez-vous', icon: 'calendar', roles: ['secretaire'] },
      { to: '/caisse', name: 'caisse', label: 'Caisse', icon: 'billing', roles: ['secretaire'] },
      { to: '/messagerie', name: 'messagerie', label: 'Messagerie', icon: 'care', roles: ['secretaire'] },
    ],
  },
  {
    id: 'complementary',
    label: 'Complémentaires',
    items: [
      { to: '/notifications', name: 'notifications', label: 'Notifications', icon: 'dashboard', roles: ['secretaire'] },
      { to: '/localisation', name: 'localisation', label: 'Contact & Localisation', icon: 'location', roles: ['secretaire'] },
    ],
  },
]

function navSectionsForRole(role) {
  return role === 'secretaire' ? SECRETARIAT_NAV_SECTIONS : NAV_SECTIONS
}

const CATEGORY_LABELS = {
  clinical: 'Cliniques',
  operations: 'Opérations',
  administration: 'Administration',
  resources: 'Ressources',
  complementary: 'Complémentaires',
  secretariat: 'Secrétariat',
}

function filterItems(items, role) {
  const out = []
  for (const item of items) {
    if (item.children) {
      if (!hasRole(role, item.roles)) continue
      const children = item.children.filter((child) => hasRole(role, child.roles))
      if (children.length) out.push({ ...item, children })
    } else if (hasRole(role, item.roles)) {
      out.push(item)
    }
  }
  return out
}

function flattenItems(items, role) {
  const out = []
  for (const item of items) {
    if (item.children) {
      if (!hasRole(role, item.roles)) continue
      for (const child of item.children) {
        if (hasRole(role, child.roles)) out.push(child)
      }
    } else if (hasRole(role, item.roles)) {
      out.push(item)
    }
  }
  return out
}

export function filterNavigation(role) {
  return navSectionsForRole(role)
    .map((section) => ({
      ...section,
      items: filterItems(section.items, role),
    }))
    .filter((section) => section.items.length > 0)
}

export function modulesByCategory(role) {
  const map = {
    clinical: [],
    operations: [],
    administration: [],
    resources: [],
    complementary: [],
    secretariat: [],
  }

  for (const section of navSectionsForRole(role)) {
    if (section.id === 'home') continue
    const items = flattenItems(section.items, role).map((item) => ({
      to: item.to,
      label: item.label,
      icon: item.icon,
      desc: item.placeholder ? 'Module en déploiement' : 'Accès rapide',
      placeholder: !!item.placeholder,
    }))
    if (items.length && map[section.id]) {
      map[section.id] = items
    }
  }

  return Object.entries(map)
    .filter(([, modules]) => modules.length)
    .map(([id, modules]) => ({ id, label: CATEGORY_LABELS[id], modules }))
}

/** Registre des modules « Bientôt disponible » (clé = name de route). */
export const PLACEHOLDER_MODULES = {}

export function getPlaceholderModule(routeName) {
  return PLACEHOLDER_MODULES[routeName] || {
    title: 'Module',
    subtitle: 'Fonctionnalité à venir',
    icon: 'dashboard',
    features: ['Interface en cours de conception'],
  }
}

export function isPlaceholderRoute(routeName) {
  return routeName in PLACEHOLDER_MODULES
}
