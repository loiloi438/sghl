import secrets
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from django.conf import settings
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.pagination import paginate

from accounts.models import Role, User
from api.v1.auth_backend import JWTAuth
from facturation.models import Facture, StatutFacture
from hospitalisation.models import Hospitalisation, StatutHospitalisation
from patients.models import Patient
from laboratoire.models import CommandeAnalyse, StatutCommandeAnalyse
from prescriptions.models import Prescription, StatutPrescription
from rendezvous.models import RendezVous, TypeConsultation
from notifications.push_service import (
    compter_non_lues,
    desactiver_appareil,
    enregistrer_appareil,
    marquer_lu,
)
from notifications.models import NotificationInbox
from rendezvous.services import RendezVousError, annuler_rendez_vous, creer_rendez_vous, get_rendez_vous
from soins.models import ConstanteVitale, DosePlanifiee, PlanSoins, StatutDose, StatutPlanSoins

router = Router(tags=['Portail patient'])
jwt_auth = JWTAuth()


def _require_patient(user: User) -> Patient:
    if user.role != Role.PATIENT:
        raise HttpError(403, 'Réservé aux comptes patient.')
    patient = Patient.objects.filter(compte_utilisateur=user).first()
    if patient is None:
        raise HttpError(404, 'Profil patient non rattaché à ce compte.')
    return patient


class PatientProfilOut(Schema):
    id: UUID
    numero_dossier: str
    nom: str
    prenom: str
    date_naissance: date
    sexe: str
    telephone: str
    email: str
    adresse: str


class PatientProfilUpdateIn(Schema):
    telephone: Optional[str] = None
    email: Optional[str] = None
    adresse: Optional[str] = None


class HospitalisationResumeOut(Schema):
    id: UUID
    motif_admission: str
    date_admission: datetime
    date_sortie_prevue: Optional[date]
    date_sortie_effective: Optional[datetime] = None
    statut: str
    lit_numero: str
    chambre_numero: str
    service_code: str
    service_nom: str = ''
    batiment_code: str
    medecin_nom: str = ''


class ConstanteVitaleOut(Schema):
    id: UUID
    temperature: Optional[float]
    tension_systolique: Optional[int]
    tension_diastolique: Optional[int]
    frequence_cardiaque: Optional[int]
    saturation_o2: Optional[int]
    glycemie: Optional[float] = None
    mesure_le: datetime
    infirmier_nom: str = ''


class PlanSoinsOut(Schema):
    id: UUID
    titre: str
    description: str
    statut: str
    date_debut: datetime
    infirmier_nom: str = ''


class DoseOut(Schema):
    id: UUID
    medicament: str
    posologie: str
    heure_prevue: datetime
    statut: str
    est_en_retard: bool
    infirmier_nom: str = ''


class PrescriptionPatientOut(Schema):
    id: UUID
    statut: str
    statut_pharmacie: str = 'en_attente'
    medecin_nom: str
    validee_le: Optional[datetime]
    diagnostics: list[str]
    medicaments: list[str]


class ResultatLaboPatientOut(Schema):
    id: UUID
    statut: str
    medecin_nom: str
    publiee_le: Optional[datetime]
    analyses: list[str]


class FacturePatientOut(Schema):
    id: UUID
    numero_facture: Optional[str]
    statut: str
    montant_total: Decimal
    montant_paye: Decimal
    montant_restant: Decimal
    version: int
    validee_le: Optional[datetime]
    payee_le: Optional[datetime]
    payable_en_ligne: bool


class InitierPaiementFactureIn(Schema):
    provider: str
    version: int


class PaiementFactureOut(Schema):
    reference: str
    provider: str
    amount_cents: int
    currency: str
    status: str
    client_secret: Optional[str] = None
    redirect_url: Optional[str] = None
    facture_settled: bool = False
    settlement_error: Optional[str] = None


class RendezVousPatientOut(Schema):
    id: UUID
    medecin_nom: str
    date_heure: datetime
    duree_minutes: int
    motif: str
    statut: str
    version: int
    type_consultation: str = TypeConsultation.PRESENTIEL
    lien_visio: Optional[str] = None


class RendezVousPatientIn(Schema):
    medecin_id: int
    date_heure: datetime
    motif: str
    duree_minutes: int = 30
    type_consultation: str = TypeConsultation.PRESENTIEL
    email: str = ''
    email_confirm: str = ''
    telephone: str = ''
    adresse: str = ''


class MedecinDispoOut(Schema):
    id: int
    nom: str


class AnnulationPatientIn(Schema):
    version: int
    motif_annulation: str = ''


class TableauBordOut(Schema):
    profil: PatientProfilOut
    hospitalisation_active: Optional[HospitalisationResumeOut]
    prochaines_doses: list[DoseOut]
    constantes_recentes: list[ConstanteVitaleOut]
    prochains_rdv: list[RendezVousPatientOut] = []
    message_bienveillance: str = ''


def _pharmacie_statut(prescription: Prescription) -> str:
    if prescription.statut == StatutPrescription.BROUILLON:
        return 'en_attente'
    if prescription.statut == StatutPrescription.ANNULEE:
        return 'annulee'
    ordre = getattr(prescription, 'ordre_dispensation', None)
    if ordre is not None:
        if ordre.statut == 'dispense':
            return 'retiree'
        return 'validee'
    if prescription.statut == StatutPrescription.VALIDEE:
        return 'validee'
    return 'en_attente'


def _user_label(user) -> str:
    if user is None:
        return '—'
    return f'{user.first_name} {user.last_name}'.strip() or user.username


def _serialize_profil(p: Patient) -> PatientProfilOut:
    return PatientProfilOut(
        id=p.id,
        numero_dossier=p.numero_dossier,
        nom=p.nom,
        prenom=p.prenom,
        date_naissance=p.date_naissance,
        sexe=p.sexe,
        telephone=p.telephone,
        email=p.email,
        adresse=p.adresse,
    )


def _apply_coordonnees_patient(patient: Patient, *, email: str, email_confirm: str, telephone: str, adresse: str):
    email = email.strip()
    email_confirm = email_confirm.strip()
    if email_confirm and email != email_confirm:
        raise HttpError(400, 'Les adresses e-mail ne correspondent pas.')
    if email and '@' not in email:
        raise HttpError(400, 'Adresse e-mail invalide.')
    if not email:
        raise HttpError(400, 'L\'adresse e-mail est obligatoire pour les confirmations de rendez-vous.')

    update_fields = ['updated_at']
    patient.email = email
    update_fields.append('email')
    tel = telephone.strip()
    if not tel:
        raise HttpError(400, 'Le numéro de téléphone est obligatoire.')
    patient.telephone = tel
    update_fields.append('telephone')
    addr = adresse.strip()
    if addr:
        patient.adresse = addr
        update_fields.append('adresse')
    patient.save(update_fields=list(dict.fromkeys(update_fields)))


def _serialize_hospitalisation(h: Hospitalisation) -> HospitalisationResumeOut:
    lit = h.lit
    service = lit.chambre.service
    return HospitalisationResumeOut(
        id=h.id,
        motif_admission=h.motif_admission,
        date_admission=h.date_admission,
        date_sortie_prevue=h.date_sortie_prevue,
        date_sortie_effective=h.date_sortie_effective,
        statut=h.statut,
        lit_numero=lit.numero,
        chambre_numero=lit.chambre.numero,
        service_code=service.code,
        service_nom=service.nom,
        batiment_code=service.batiment.code,
        medecin_nom=_user_label(h.medecin_referent),
    )


def _serialize_constante(c: ConstanteVitale) -> ConstanteVitaleOut:
    return ConstanteVitaleOut(
        id=c.id,
        temperature=float(c.temperature) if c.temperature is not None else None,
        tension_systolique=c.tension_systolique,
        tension_diastolique=c.tension_diastolique,
        frequence_cardiaque=c.frequence_cardiaque,
        saturation_o2=c.saturation_o2,
        glycemie=float(c.glycemie) if c.glycemie is not None else None,
        mesure_le=c.mesure_le,
        infirmier_nom=_user_label(c.infirmier),
    )


def _serialize_dose(d: DosePlanifiee) -> DoseOut:
    return DoseOut(
        id=d.id,
        medicament=d.medicament,
        posologie=d.posologie,
        heure_prevue=d.heure_prevue,
        statut=d.statut,
        est_en_retard=d.est_en_retard,
        infirmier_nom=_user_label(d.infirmier),
    )


@router.get('/patient/profil/', response=PatientProfilOut, auth=jwt_auth)
def profil_patient(request):
    patient = _require_patient(request.auth)
    return _serialize_profil(patient)


@router.patch('/patient/profil/', response=PatientProfilOut, auth=jwt_auth)
def maj_profil_patient(request, payload: PatientProfilUpdateIn):
    patient = _require_patient(request.auth)
    update_fields = ['updated_at']
    if payload.email is not None:
        email = payload.email.strip()
        if email and '@' not in email:
            raise HttpError(400, 'Adresse e-mail invalide.')
        patient.email = email
        update_fields.append('email')
    if payload.telephone is not None:
        patient.telephone = payload.telephone.strip()
        update_fields.append('telephone')
    if payload.adresse is not None:
        patient.adresse = payload.adresse.strip()
        update_fields.append('adresse')
    patient.save(update_fields=list(dict.fromkeys(update_fields)))
    return _serialize_profil(patient)


@router.get('/patient/tableau-de-bord/', response=TableauBordOut, auth=jwt_auth)
def tableau_de_bord(request):
    patient = _require_patient(request.auth)

    hospitalisation = (
        Hospitalisation.objects.filter(patient=patient, statut=StatutHospitalisation.ACTIVE)
        .select_related('lit__chambre__service__batiment', 'medecin_referent')
        .first()
    )

    hosp_out = _serialize_hospitalisation(hospitalisation) if hospitalisation else None

    constantes = []
    prochaines_doses = []
    prochains_rdv = list(
        RendezVous.objects.filter(patient=patient)
        .select_related('medecin')
        .order_by('date_heure')[:3]
    )
    if hospitalisation:
        constantes = [
            _serialize_constante(c)
            for c in ConstanteVitale.objects.filter(hospitalisation=hospitalisation).order_by('-mesure_le')[:5]
        ]
        prochaines_doses = [
            _serialize_dose(d)
            for d in DosePlanifiee.objects.filter(
                plan_soins__hospitalisation=hospitalisation,
                plan_soins__statut=StatutPlanSoins.ACTIF,
                statut=StatutDose.PLANIFIEE,
            ).order_by('heure_prevue')[:10]
        ]

    if hospitalisation:
        message = 'Nous veillons sur vous avec attention 💙'
    elif prochains_rdv:
        pending = any(
            r.statut in {'en_attente', 'planifie'} for r in prochains_rdv
        )
        if pending:
            message = 'Votre demande de rendez-vous est en attente de validation 💙'
        else:
            message = 'Votre prochain rendez-vous est confirmé — vous êtes entre de bonnes mains 💙'
    else:
        message = 'Vous êtes en bonne santé 💙 — prenez soin de vous au quotidien.'

    return TableauBordOut(
        profil=_serialize_profil(patient),
        hospitalisation_active=hosp_out,
        prochaines_doses=prochaines_doses,
        constantes_recentes=constantes,
        prochains_rdv=[_serialize_rdv_patient(r) for r in prochains_rdv],
        message_bienveillance=message,
    )


@router.get('/patient/hospitalisations/', response=list[HospitalisationResumeOut], auth=jwt_auth)
def hospitalisations_patient(request):
    patient = _require_patient(request.auth)
    qs = (
        Hospitalisation.objects.filter(patient=patient)
        .select_related('lit__chambre__service__batiment', 'medecin_referent')
        .order_by('-date_admission')
    )
    return [_serialize_hospitalisation(h) for h in qs]


@router.get('/patient/constantes-vitales/', response=list[ConstanteVitaleOut], auth=jwt_auth)
@paginate
def historique_constantes(request):
    patient = _require_patient(request.auth)
    qs = ConstanteVitale.objects.filter(hospitalisation__patient=patient).select_related('infirmier').order_by('-mesure_le')
    return [_serialize_constante(c) for c in qs]


@router.get('/patient/plans-soins/', response=list[PlanSoinsOut], auth=jwt_auth)
@paginate
def plans_soins_patient(request):
    patient = _require_patient(request.auth)
    qs = PlanSoins.objects.filter(hospitalisation__patient=patient).select_related('cree_par').order_by('-date_debut')
    return [
        PlanSoinsOut(
            id=p.id,
            titre=p.titre,
            description=p.description,
            statut=p.statut,
            date_debut=p.date_debut,
            infirmier_nom=_user_label(p.cree_par),
        )
        for p in qs
    ]


@router.get('/patient/doses/', response=list[DoseOut], auth=jwt_auth)
@paginate
def doses_patient(request):
    patient = _require_patient(request.auth)
    qs = DosePlanifiee.objects.filter(
        plan_soins__hospitalisation__patient=patient,
    ).select_related('infirmier', 'plan_soins').order_by('heure_prevue')
    return [_serialize_dose(d) for d in qs]


@router.get('/patient/prescriptions/', response=list[PrescriptionPatientOut], auth=jwt_auth)
@paginate
def prescriptions_patient(request):
    patient = _require_patient(request.auth)
    qs = Prescription.objects.filter(
        hospitalisation__patient=patient,
    ).select_related('medecin', 'ordre_dispensation').prefetch_related('diagnostics', 'lignes').order_by('-created_at')
    results = []
    for p in qs:
        medecin = p.medecin
        results.append(
            PrescriptionPatientOut(
                id=p.id,
                statut=p.statut,
                statut_pharmacie=_pharmacie_statut(p),
                medecin_nom=f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username,
                validee_le=p.validee_le,
                diagnostics=[f'{d.code_cim10} — {d.libelle}' for d in p.diagnostics.all()],
                medicaments=[f'{l.medicament} ({l.posologie})' for l in p.lignes.all()],
            )
        )
    return results


@router.get('/patient/resultats-laboratoire/', response=list[ResultatLaboPatientOut], auth=jwt_auth)
@paginate
def resultats_laboratoire_patient(request):
    patient = _require_patient(request.auth)
    qs = CommandeAnalyse.objects.filter(
        hospitalisation__patient=patient,
        statut=StatutCommandeAnalyse.PUBLIEE,
    ).select_related('medecin').prefetch_related('lignes__resultat').order_by('-publiee_le')
    results = []
    for c in qs:
        medecin = c.medecin
        analyses = []
        for ligne in c.lignes.all():
            try:
                r = ligne.resultat
                ref = f' (ref. {ligne.valeur_reference})' if ligne.valeur_reference else ''
                analyses.append(
                    f'{ligne.code_analyse} — {ligne.libelle} : {r.valeur} {r.unite}{ref}'.strip()
                )
            except Exception:
                analyses.append(f'{ligne.code_analyse} — {ligne.libelle}')
        results.append(
            ResultatLaboPatientOut(
                id=c.id,
                statut=c.statut,
                medecin_nom=f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username,
                publiee_le=c.publiee_le,
                analyses=analyses,
            )
        )
    return results


@router.get('/patient/factures/', response=list[FacturePatientOut], auth=jwt_auth)
@paginate
def factures_patient(request):
    patient = _require_patient(request.auth)
    qs = Facture.objects.filter(
        hospitalisation__patient=patient,
        statut__in={
            StatutFacture.VALIDEE,
            StatutFacture.PARTIELLEMENT_PAYEE,
            StatutFacture.PAYEE,
        },
    ).order_by('-validee_le')
    return [_serialize_facture_patient(f) for f in qs]


def _serialize_facture_patient(f: Facture) -> FacturePatientOut:
    payable = f.statut in {StatutFacture.VALIDEE, StatutFacture.PARTIELLEMENT_PAYEE} and f.montant_restant > 0
    return FacturePatientOut(
        id=f.id,
        numero_facture=f.numero_facture,
        statut=f.statut,
        montant_total=f.montant_total,
        montant_paye=f.montant_paye,
        montant_restant=f.montant_restant,
        version=f.version,
        validee_le=f.validee_le,
        payee_le=f.payee_le,
        payable_en_ligne=payable,
    )


@router.post(
    '/patient/factures/{facture_id}/initier-paiement/',
    response=PaiementFactureOut,
    auth=jwt_auth,
)
def initier_paiement_facture(request, facture_id: UUID, payload: InitierPaiementFactureIn):
    patient = _require_patient(request.auth)
    provider = (payload.provider or '').lower()
    if provider not in {'stripe', 'mtn', 'airtel'}:
        raise HttpError(400, 'Prestataire invalide (stripe, mtn, airtel).')

    try:
        facture = Facture.objects.select_related('hospitalisation__patient').get(
            id=facture_id,
            hospitalisation__patient=patient,
        )
    except Facture.DoesNotExist:
        raise HttpError(404, 'Facture introuvable.')

    if facture.version != payload.version:
        raise HttpError(409, 'Conflit de version : actualisez la facture.')
    if facture.statut not in {StatutFacture.VALIDEE, StatutFacture.PARTIELLEMENT_PAYEE}:
        raise HttpError(400, 'Cette facture ne peut pas être payée en ligne.')
    if facture.montant_restant <= Decimal('0'):
        raise HttpError(400, 'Facture déjà soldée.')

    from payments.invoice_settlement import has_pending_facture_payment, try_settle_payment_for_facture
    from payments.services import initiate_payment

    if has_pending_facture_payment(facture.id):
        raise HttpError(409, 'Un paiement est déjà en cours pour cette facture.')

    amount_cents = int(facture.montant_restant * 100)
    if amount_cents < 1:
        raise HttpError(400, 'Montant trop faible pour un paiement en ligne.')

    try:
        payment = initiate_payment(
            provider=provider,
            amount_cents=amount_cents,
            currency='XAF',
            user=request.auth,
            metadata={
                'facture_id': str(facture.id),
                'facture_version': facture.version,
                'numero_facture': facture.numero_facture or '',
                'type': 'facture',
            },
        )
    except Exception as exc:
        raise HttpError(400, str(exc)) from exc

    if payment.status == 'success':
        payment = try_settle_payment_for_facture(payment)

    provider_raw = (payment.metadata or {}).get('provider_raw') or {}
    meta = payment.metadata or {}
    client_secret = provider_raw.get('client_secret') if isinstance(provider_raw, dict) else None
    redirect_url = provider_raw.get('redirect_url') if isinstance(provider_raw, dict) else None

    return PaiementFactureOut(
        reference=payment.reference,
        provider=payment.provider,
        amount_cents=payment.amount_cents,
        currency=payment.currency,
        status=payment.status,
        client_secret=client_secret,
        redirect_url=redirect_url,
        facture_settled=bool(meta.get('facture_settled')),
        settlement_error=meta.get('settlement_error'),
    )


def _serialize_rdv_patient(r: RendezVous) -> RendezVousPatientOut:
    medecin = r.medecin
    return RendezVousPatientOut(
        id=r.id,
        medecin_nom=f'{medecin.first_name} {medecin.last_name}'.strip() or medecin.username,
        date_heure=r.date_heure,
        duree_minutes=r.duree_minutes,
        motif=r.motif,
        statut=r.statut,
        version=r.version,
        type_consultation=r.type_consultation,
        lien_visio=r.lien_visio or None,
    )


@router.get('/patient/rendez-vous/medecins/', response=list[MedecinDispoOut], auth=jwt_auth)
def medecins_patient(request):
    _require_patient(request.auth)
    return [
        MedecinDispoOut(
            id=u.id,
            nom=f'{u.first_name} {u.last_name}'.strip() or u.username,
        )
        for u in User.objects.filter(role=Role.MEDECIN, is_active=True).order_by('last_name')
    ]


@router.get('/patient/rendez-vous/', response=list[RendezVousPatientOut], auth=jwt_auth)
@paginate
def rendez_vous_patient(request):
    patient = _require_patient(request.auth)
    qs = RendezVous.objects.filter(patient=patient).select_related('medecin').order_by('date_heure')
    return [_serialize_rdv_patient(r) for r in qs]


@router.post('/patient/rendez-vous/', response=RendezVousPatientOut, auth=jwt_auth)
def creer_rendez_vous_patient(request, payload: RendezVousPatientIn):
    patient = _require_patient(request.auth)
    _apply_coordonnees_patient(
        patient,
        email=payload.email or '',
        email_confirm=payload.email_confirm or '',
        telephone=payload.telephone or '',
        adresse=payload.adresse or '',
    )
    type_consultation = payload.type_consultation
    if type_consultation not in (TypeConsultation.PRESENTIEL, TypeConsultation.TELECONSULTATION):
        type_consultation = TypeConsultation.PRESENTIEL
    try:
        medecin = User.objects.get(id=payload.medecin_id, role=Role.MEDECIN)
        rdv = creer_rendez_vous(
            patient=patient,
            medecin=medecin,
            date_heure=payload.date_heure,
            motif=payload.motif,
            auteur=request.auth,
            duree_minutes=payload.duree_minutes,
            type_consultation=type_consultation,
        )
        if type_consultation == TypeConsultation.TELECONSULTATION:
            base = getattr(settings, 'SGHL_FRONTEND_URL', 'http://localhost:5173').rstrip('/')
            token = secrets.token_urlsafe(16)
            rdv.lien_visio = f'{base}/visio/{token}'
            rdv.save(update_fields=['lien_visio', 'updated_at'])
    except User.DoesNotExist:
        raise HttpError(404, 'Médecin introuvable.')
    except RendezVousError as exc:
        raise HttpError(409 if exc.code == 'creneau_indisponible' else 400, exc.message)

    return _serialize_rdv_patient(get_rendez_vous(rdv.id))


@router.post('/patient/rendez-vous/{rdv_id}/annuler/', response=RendezVousPatientOut, auth=jwt_auth)
def annuler_rendez_vous_patient(request, rdv_id: UUID, payload: AnnulationPatientIn):
    patient = _require_patient(request.auth)
    try:
        rdv = get_rendez_vous(rdv_id)
        if rdv.patient_id != patient.id:
            raise HttpError(403, 'Accès refusé.')
        rdv = annuler_rendez_vous(
            rdv=rdv,
            auteur=request.auth,
            version=payload.version,
            motif_annulation=payload.motif_annulation,
        )
    except RendezVousError as exc:
        raise HttpError(409 if exc.code == 'version_conflict' else 400, exc.message)

    return _serialize_rdv_patient(get_rendez_vous(rdv.id))


class AppareilPushIn(Schema):
    token: str
    plateforme: str = 'android'


class NotificationOut(Schema):
    id: UUID
    titre: str
    corps: str
    categorie: str
    lu: bool
    created_at: datetime


class NonLuesOut(Schema):
    count: int


@router.post('/patient/push/appareils/', auth=jwt_auth)
def enregistrer_appareil_push(request, payload: AppareilPushIn):
    user = request.auth
    _require_patient(user)
    try:
        enregistrer_appareil(
            utilisateur_id=user.id,
            token=payload.token,
            plateforme=payload.plateforme,
        )
    except ValueError as exc:
        raise HttpError(400, str(exc))
    return {'detail': 'Appareil enregistré.'}


@router.post('/patient/push/appareils/desactiver/', auth=jwt_auth)
def desactiver_appareil_push(request, payload: AppareilPushIn):
    user = request.auth
    _require_patient(user)
    desactiver_appareil(utilisateur_id=user.id, token=payload.token)
    return {'detail': 'Appareil désactivé.'}


@router.get('/patient/notifications/', response=list[NotificationOut], auth=jwt_auth)
@paginate
def list_notifications_patient(request):
    user = request.auth
    _require_patient(user)
    return [
        NotificationOut(
            id=n.id,
            titre=n.titre,
            corps=n.corps,
            categorie=n.categorie,
            lu=n.lu,
            created_at=n.created_at,
        )
        for n in NotificationInbox.objects.filter(utilisateur=user).order_by('-created_at')
    ]


@router.get('/patient/notifications/non-lues/', response=NonLuesOut, auth=jwt_auth)
def count_notifications_non_lues(request):
    user = request.auth
    _require_patient(user)
    return NonLuesOut(count=compter_non_lues(user.id))


@router.post('/patient/notifications/{notification_id}/lu/', auth=jwt_auth)
def marquer_notification_lue(request, notification_id: UUID):
    user = request.auth
    _require_patient(user)
    if not marquer_lu(notification_id, user.id):
        raise HttpError(404, 'Notification introuvable.')
    return {'detail': 'Notification lue.'}
