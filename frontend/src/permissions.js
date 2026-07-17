/** Aligné sur les ROLES_* des modules `api/v1/*.py` */

export const PATIENT_ROLE = 'patient'

export const STAFF_ROLES = [
  'admin',
  'medecin',
  'infirmier',
  'biologiste',
  'pharmacien',
  'comptable',
  'secretaire',
]

export const WEB_PORTAL_ROLES = [...STAFF_ROLES, PATIENT_ROLE]

/** Secrétaire : pas d’accès fiche patient ni tableau de bord clinique */
export const PATIENTS_READ = STAFF_ROLES.filter((r) => r !== 'secretaire')
export const PATIENTS_WRITE = ['admin', 'medecin', 'infirmier']

export const HOSPITALISATION_READ = ['admin', 'medecin', 'infirmier', 'biologiste']
export const HOSPITALISATION_ADMIT = ['admin', 'medecin', 'infirmier']
export const HOSPITALISATION_SORTIE = ['admin', 'medecin']

export const RDV_READ = ['admin', 'medecin', 'infirmier', 'comptable', 'secretaire']
export const RDV_GESTION = ['admin', 'medecin', 'infirmier', 'secretaire']

/** Infirmier : consultation ; pharmacien : module Pharmacie uniquement */
export const PRESCRIPTIONS_READ = ['admin', 'medecin', 'infirmier']
export const PRESCRIPTIONS_WRITE = ['admin', 'medecin']

/** Pharmacien : pas de liste hosp. côté API — pas d’écran LIS dédié */
export const LABO_READ = ['admin', 'medecin', 'infirmier', 'biologiste']
export const LABO_COMMANDE = ['admin', 'medecin']
export const LABO_WORKFLOW = ['admin', 'biologiste']
export const LABO_PRELEVEMENT = ['admin', 'medecin', 'infirmier']

export const SOINS_READ = ['admin', 'medecin', 'infirmier', 'biologiste']
export const SOINS_WRITE = ['admin', 'medecin', 'infirmier']

export const PHARMACIE_READ = ['admin', 'medecin', 'infirmier', 'pharmacien', 'biologiste']
export const PHARMACIE_WRITE = ['admin', 'pharmacien']

export const FACTURATION_READ = ['admin', 'comptable', 'medecin']
export const FACTURATION_WRITE = ['admin', 'comptable', 'secretaire']
export const CAISSE_READ = ['admin', 'comptable', 'secretaire']

export const DASHBOARD = STAFF_ROLES.filter((r) => r !== 'secretaire')
export const AUDIT = ['admin']
export const COMPTES = ['admin']
export const STATISTIQUES = ['admin', 'comptable', 'medecin']
export const ASSURANCE = ['admin', 'comptable']
export const DOCUMENTS = ['admin', 'medecin', 'infirmier']
export const SERVICES_MEDICAUX = ['admin', 'medecin']
export const PERSONNEL_MEDECINS = ['admin']
export const PERSONNEL_INFIRMIERS = ['admin']
export const NOTIFICATIONS = STAFF_ROLES
export const URGENCES = ['admin', 'medecin', 'infirmier']
export const TELECONSULTATION = ['admin', 'medecin']
export const INVENTAIRE = ['admin', 'pharmacien']
export const FORMATION_RH = ['admin']
export const PARAMETRES = ['admin']
export const LOCALISATION_READ = STAFF_ROLES

export function hasRole(role, allowed) {
  return role && allowed.includes(role)
}
