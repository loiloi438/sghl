import { defineStore } from 'pinia'

import api from '../api/client.js'

import {
  AUDIT,
  DASHBOARD,
  FACTURATION_READ,
  FACTURATION_WRITE,
  CAISSE_READ,
  hasRole,
  HOSPITALISATION_ADMIT,
  HOSPITALISATION_READ,
  HOSPITALISATION_SORTIE,
  LABO_COMMANDE,
  LABO_PRELEVEMENT,
  LABO_READ,
  LABO_WORKFLOW,
  PATIENT_ROLE,
  PATIENTS_WRITE,
  PHARMACIE_READ,
  PHARMACIE_WRITE,
  PRESCRIPTIONS_READ,
  PRESCRIPTIONS_WRITE,
  RDV_GESTION,
  RDV_READ,
  SOINS_READ,
  SOINS_WRITE,
  WEB_PORTAL_ROLES,
} from '../permissions.js'

const PORTAL_ROLE_SET = new Set(WEB_PORTAL_ROLES)
const HOME_ROUTE_BY_ROLE = {
  admin: 'dashboard',
  medecin: 'rendez-vous',
  infirmier: 'rendez-vous',
  pharmacien: 'pharmacie',
  comptable: 'facturation',
  secretaire: 'secretariat',
  biologiste: 'resultats-medicaux',
  patient: 'patient-home',
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
    error: null,
    pendingMfa: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    role: (state) => state.user?.role,
    isPatient: (state) => state.user?.role === PATIENT_ROLE,
    isStaff: (state) => state.user?.role && state.user.role !== PATIENT_ROLE,
    homeRoute: (state) => HOME_ROUTE_BY_ROLE[state.user?.role] || 'login',
    mfaEnabled: (state) => state.user?.mfa_enabled ?? false,

    fullName: (state) => {
      if (!state.user) return ''
      const name = `${state.user.first_name} ${state.user.last_name}`.trim()
      return name || state.user.username
    },

    canDashboard: (state) => hasRole(state.user?.role, DASHBOARD),
    canPatientsWrite: (state) => hasRole(state.user?.role, PATIENTS_WRITE),
    canHospitalisation: (state) => hasRole(state.user?.role, HOSPITALISATION_READ),
    canHospitalisationAdmit: (state) => hasRole(state.user?.role, HOSPITALISATION_ADMIT),
    canHospitalisationSortie: (state) => hasRole(state.user?.role, HOSPITALISATION_SORTIE),
    canPrescrire: (state) => hasRole(state.user?.role, PRESCRIPTIONS_WRITE),
    canPrescriptionsRead: (state) => hasRole(state.user?.role, PRESCRIPTIONS_READ),
    canSoins: (state) => hasRole(state.user?.role, SOINS_WRITE),
    canSoinsRead: (state) => hasRole(state.user?.role, SOINS_READ),
    canLaboRead: (state) => hasRole(state.user?.role, LABO_READ),
    canLaboCommande: (state) => hasRole(state.user?.role, LABO_COMMANDE),
    canLaboPrelever: (state) => hasRole(state.user?.role, LABO_PRELEVEMENT),
    canLabo: (state) => hasRole(state.user?.role, LABO_WORKFLOW),
    canPharmacieRead: (state) => hasRole(state.user?.role, PHARMACIE_READ),
    canPharmacie: (state) => hasRole(state.user?.role, PHARMACIE_WRITE),
    canFacturationRead: (state) => hasRole(state.user?.role, FACTURATION_READ),
    canCaisse: (state) => hasRole(state.user?.role, CAISSE_READ),
    canFacturation: (state) => hasRole(state.user?.role, FACTURATION_WRITE),
    canRdvRead: (state) => hasRole(state.user?.role, RDV_READ),
    canRdv: (state) => hasRole(state.user?.role, RDV_GESTION),
    isAdmin: (state) => state.user?.role === 'admin',
    canAudit: (state) => hasRole(state.user?.role, AUDIT),
  },

  actions: {
    async restoreSession() {
      const token = localStorage.getItem('sghl_access_token')
      if (!token) return false

      try {
        const { data } = await api.get('/auth/me/')
        if (!PORTAL_ROLE_SET.has(data.role)) {
          await this.logout()
          return false
        }
        this.user = data
        return true
      } catch {
        await this.logout()
        return false
      }
    },

    async login(username, password, totpCode = null) {
      this.loading = true
      this.error = null
      try {
        const body = { username, password }
        if (totpCode) body.totp_code = totpCode
        const response = await api.post('/auth/login/', body)
        if (response.status === 202) {
          this.pendingMfa = { username }
          this.loading = false
          return 'mfa_required'
        }
        const { data } = response
        return await this.applyTokens(data.access_token, data.refresh_token)
      } catch (error) {
        // handle MFA required (202) for unusual axios config or server behavior
        if (error.response?.status === 202) {
          this.pendingMfa = { username }
          this.loading = false
          return 'mfa_required'
        }
        const detail = error.response?.data?.detail
        if (error.response?.status === 401) {
          if (detail === 'Code MFA requis ou invalide.') {
            this.error = 'Code MFA requis ou invalide (Google Authenticator).'
          } else if (
            detail === 'MFA obligatoire pour le personnel. Activez MFA avant de vous connecter.'
          ) {
            this.error = 'Connexion refusée : MFA obligatoire pour le personnel. Activez MFA.'
          } else {
            this.error = 'Identifiants invalides.'
          }
        } else {
          this.error = detail || 'Connexion impossible.'
        }
        return false
      } finally {
        this.loading = false
      }
    },

    async loginMfa(code) {
      if (!this.pendingMfa?.username) return false
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/auth/login/mfa/', {
          username: this.pendingMfa.username,
          code,
        })
        this.pendingMfa = null
        return await this.applyTokens(data.access_token, data.refresh_token)
      } catch (error) {
        const detail = error.response?.data?.detail
        this.error = detail || 'Code MFA invalide.'
        return false
      } finally {
        this.loading = false
      }
    },

    async applyTokens(accessToken, refreshToken) {
      localStorage.setItem('sghl_access_token', accessToken)
      localStorage.setItem('sghl_refresh_token', refreshToken)
      const me = await api.get('/auth/me/')
      if (!PORTAL_ROLE_SET.has(me.data.role)) {
        await this.logout()
        this.error = 'Ce compte n\'a pas accès au portail.'
        return false
      }
      this.user = me.data
      return true
    },

    async refreshUser() {
      const { data } = await api.get('/auth/me/')
      if (!PORTAL_ROLE_SET.has(data.role)) {
        await this.logout()
        return false
      }
      this.user = data
      return true
    },

    async logout() {
      const refresh = localStorage.getItem('sghl_refresh_token')
      if (refresh) {
        try {
          await api.post('/auth/logout/', { refresh_token: refresh })
        } catch {
          /* ignore */
        }
      }
      localStorage.removeItem('sghl_access_token')
      localStorage.removeItem('sghl_refresh_token')
      this.user = null
    },
  },
})
