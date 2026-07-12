from datetime import datetime
from decimal import Decimal
from io import BytesIO

from django.conf import settings
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ETABLISSEMENT = getattr(settings, 'SGHL_ETABLISSEMENT', 'SGHL — Centre Hospitalaire')


def _fmt_date(dt) -> str:
    if dt is None:
        return '—'
    if isinstance(dt, datetime):
        local = timezone.localtime(dt) if timezone.is_aware(dt) else dt
        return local.strftime('%d/%m/%Y %H:%M')
    return dt.strftime('%d/%m/%Y')


def _fmt_montant(value) -> str:
    if value is None:
        return '—'
    n = Decimal(str(value))
    return f'{n:,.2f}'.replace(',', ' ').replace('.', ',') + ' FCFA'


def _styles():
    base = getSampleStyleSheet()
    return {
        'title': ParagraphStyle(
            'DocTitle',
            parent=base['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#0f766e'),
        ),
        'subtitle': ParagraphStyle(
            'DocSubtitle',
            parent=base['Normal'],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=16,
        ),
        'section': ParagraphStyle(
            'DocSection',
            parent=base['Heading2'],
            fontSize=12,
            spaceBefore=12,
            spaceAfter=6,
        ),
        'normal': base['Normal'],
        'small': ParagraphStyle(
            'DocSmall',
            parent=base['Normal'],
            fontSize=9,
            textColor=colors.grey,
        ),
    }


def _build_pdf(title: str, subtitle: str, sections: list[tuple[str, list]], signature: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = _styles()
    story = [
        Paragraph(ETABLISSEMENT, styles['small']),
        Spacer(1, 0.2 * cm),
        Paragraph(title, styles['title']),
        Paragraph(subtitle, styles['subtitle']),
    ]

    for heading, rows in sections:
        story.append(Paragraph(heading, styles['section']))
        if not rows:
            story.append(Paragraph('—', styles['normal']))
            continue
        table = Table(rows, hAlign='LEFT')
        table.setStyle(
            TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecfdf5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#134e4a')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ])
        )
        story.append(table)
        story.append(Spacer(1, 0.3 * cm))

    story.extend([
        Spacer(1, 0.5 * cm),
        Paragraph('Signature électronique SGHL', styles['section']),
        Paragraph(
            f"Signé par : <b>{signature['nom']}</b> ({signature['role']})<br/>"
            f"Date : {_fmt_date(signature['date'])}<br/>"
            f"Réf. document : {signature['doc_ref']}<br/>"
            f"Empreinte SHA-256 : {signature.get('empreinte', '—')[:16]}…",
            styles['normal'],
        ),
        Spacer(1, 0.3 * cm),
        Paragraph(
            'Document généré automatiquement par SGHL. '
            'Vérifiez l’authenticité via GET /api/v1/documents/verifier/{code}/ '
            '(code communiqué séparément après archivage).',
            styles['small'],
        ),
    ])

    doc.build(story)
    return buffer.getvalue()


def build_facture_pdf(facture, *, doc_ref: str) -> bytes:
    patient = facture.hospitalisation.patient
    hospi = facture.hospitalisation
    signataire = facture.validee_par
    nom_signataire = (
        f'{signataire.first_name} {signataire.last_name}'.strip() or signataire.username
        if signataire else 'Comptable SGHL'
    )

    lignes = [['Acte', 'Libellé', 'Qté', 'P.U.', 'Montant']]
    for ligne in facture.lignes.all():
        lignes.append([
            ligne.code_acte,
            ligne.libelle,
            str(ligne.quantite),
            _fmt_montant(ligne.prix_unitaire),
            _fmt_montant(ligne.montant_ligne),
        ])

    info = [
        ['N° facture', facture.numero_facture or '—'],
        ['Patient', f'{patient.prenom} {patient.nom} ({patient.numero_dossier})'],
        ['Hospitalisation', f'{hospi.motif_admission} — adm. {_fmt_date(hospi.date_admission)}'],
        ['Statut', facture.get_statut_display()],
        ['Montant total', _fmt_montant(facture.montant_total)],
    ]
    if facture.statut == 'payee':
        info.extend([
            ['Paiement', facture.mode_paiement or '—'],
            ['Référence', facture.reference_paiement or '—'],
            ['Payée le', _fmt_date(facture.payee_le)],
        ])

    return _build_pdf(
        title=f'Facture {facture.numero_facture}',
        subtitle=f'Établi le {_fmt_date(facture.validee_le)}',
        sections=[
            ('Informations', info),
            ('Détail des actes', lignes),
        ],
        signature={
            'nom': nom_signataire,
            'role': signataire.get_role_display() if signataire else 'Comptable',
            'date': facture.validee_le or timezone.now(),
            'doc_ref': doc_ref,
            'empreinte': doc_ref,
        },
    )


def build_recu_pdf(facture, *, doc_ref: str) -> bytes:
    patient = facture.hospitalisation.patient
    signataire = facture.validee_par
    nom_signataire = (
        f'{signataire.first_name} {signataire.last_name}'.strip() or signataire.username
        if signataire else 'Caisse SGHL'
    )
    info = [
        ['N° facture', facture.numero_facture or '—'],
        ['Patient', f'{patient.prenom} {patient.nom} ({patient.numero_dossier})'],
        ['Montant total', _fmt_montant(facture.montant_total)],
        ['Montant payé', _fmt_montant(facture.montant_paye)],
        ['Reste dû', _fmt_montant(facture.montant_restant)],
        ['Mode de paiement', facture.mode_paiement or '—'],
        ['Référence', facture.reference_paiement or '—'],
        ['Statut', facture.get_statut_display()],
        ['Payé le', _fmt_date(facture.payee_le)],
    ]
    return _build_pdf(
        title='Reçu de paiement',
        subtitle=f'Établi le {_fmt_date(facture.payee_le or timezone.now())}',
        sections=[('Détails du règlement', info)],
        signature={
            'nom': nom_signataire,
            'role': signataire.get_role_display() if signataire else 'Secrétariat / Caisse',
            'date': facture.payee_le or timezone.now(),
            'doc_ref': doc_ref,
            'empreinte': doc_ref,
        },
    )


def build_labo_pdf(commande, *, doc_ref: str) -> bytes:
    patient = commande.hospitalisation.patient
    signataire = commande.publiee_par or commande.validee_par
    nom_signataire = (
        f'{signataire.first_name} {signataire.last_name}'.strip() or signataire.username
        if signataire else 'Biologiste SGHL'
    )

    resultats = [['Analyse', 'Résultat', 'Unité', 'Référence']]
    for ligne in commande.lignes.all():
        res = getattr(ligne, 'resultat', None)
        resultats.append([
            f'{ligne.code_analyse} — {ligne.libelle}',
            res.valeur if res else '—',
            res.unite if res else ligne.unite_reference or '—',
            ligne.valeur_reference or '—',
        ])

    info = [
        ['Patient', f'{patient.prenom} {patient.nom} ({patient.numero_dossier})'],
        ['Commande', str(commande.id)[:8].upper()],
        ['Médecin prescripteur', commande.medecin.get_full_name() or commande.medecin.username],
        ['Prélèvement', _fmt_date(commande.preleve_le)],
        ['Validée le', _fmt_date(commande.validee_le)],
        ['Publiée le', _fmt_date(commande.publiee_le)],
    ]

    return _build_pdf(
        title='Compte-rendu de biologie médicale',
        subtitle=f'Résultats publiés le {_fmt_date(commande.publiee_le)}',
        sections=[
            ('Informations patient', info),
            ('Résultats', resultats),
        ],
        signature={
            'nom': nom_signataire,
            'role': signataire.get_role_display() if signataire else 'Biologiste',
            'date': commande.publiee_le or timezone.now(),
            'doc_ref': doc_ref,
            'empreinte': doc_ref,
        },
    )


def build_ordonnance_pdf(prescription, *, doc_ref: str) -> bytes:
    patient = prescription.hospitalisation.patient
    signataire = prescription.validee_par or prescription.medecin
    nom_signataire = (
        f'{signataire.first_name} {signataire.last_name}'.strip() or signataire.username
        if signataire else 'Médecin SGHL'
    )

    diagnostics = prescription.diagnostics.all()
    diag_rows = [['Code CIM-10', 'Libellé']]
    for d in diagnostics:
        diag_rows.append([d.code_cim10, d.libelle])

    medicaments = [['Médicament', 'Posologie', 'Durée', 'Voie']]
    for ligne in prescription.lignes.all():
        medicaments.append([
            ligne.medicament,
            ligne.posologie,
            ligne.duree_traitement or '—',
            ligne.voie_administration,
        ])

    info = [
        ['Patient', f'{patient.prenom} {patient.nom} ({patient.numero_dossier})'],
        ['Prescription', str(prescription.id)[:8].upper()],
        ['Médecin', prescription.medecin.get_full_name() or prescription.medecin.username],
        ['Validée le', _fmt_date(prescription.validee_le)],
    ]

    return _build_pdf(
        title='Ordonnance électronique',
        subtitle=f'Prescription validée le {_fmt_date(prescription.validee_le)}',
        sections=[
            ('Informations', info),
            ('Diagnostics', diag_rows),
            ('Traitement', medicaments),
        ],
        signature={
            'nom': nom_signataire,
            'role': signataire.get_role_display() if signataire else 'Médecin',
            'date': prescription.validee_le or timezone.now(),
            'doc_ref': doc_ref,
            'empreinte': doc_ref,
        },
    )


def build_rapport_statistiques_pdf(rapport: dict, *, demandeur) -> bytes:
    kpis = rapport['kpis']
    resume = [
        ['Indicateur', 'Valeur'],
        ['Période', f"{rapport['date_debut']:%d/%m/%Y} → {rapport['date_fin']:%d/%m/%Y}"],
        ['Admissions', str(kpis['admissions'])],
        ['Rendez-vous', str(kpis['rendez_vous'])],
        ['Prescriptions', str(kpis['prescriptions'])],
        ['Factures', str(kpis['factures'])],
        ['Lits actifs', str(kpis['lits_actifs'])],
        ['Lits occupés', str(kpis['lits_occupes'])],
        ['Taux occupation', f"{kpis['taux_occupation']} %"],
        ['Factures validées', str(kpis['factures_validees'])],
        ['Factures partiellement payées', str(kpis['factures_partiellement_payees'])],
        ['Factures payées', str(kpis['factures_payees'])],
    ]

    activite = [['Date', 'Admissions', 'RDV', 'Prescriptions', 'Factures']]
    for row in rapport['evolution_journaliere']:
        activite.append([
            row['date'].strftime('%d/%m/%Y'),
            str(row['admissions']),
            str(row['rendez_vous']),
            str(row['prescriptions']),
            str(row['factures']),
        ])

    services = [['Service', 'Code', 'Admissions']]
    for row in rapport['hospitalisations_par_service']:
        services.append([row['service'], row['code_service'], str(row['count'])])

    rdv_statuts = [['Statut', 'Nombre']]
    for row in rapport['rendez_vous_par_statut']:
        rdv_statuts.append([row['statut'], str(row['count'])])

    factures_statuts = [['Statut', 'Nombre']]
    for row in rapport['factures_par_statut']:
        factures_statuts.append([row['statut'], str(row['count'])])

    prescriptions_statuts = [['Statut', 'Nombre']]
    for row in rapport['prescriptions_par_statut']:
        prescriptions_statuts.append([row['statut'], str(row['count'])])

    return _build_pdf(
        title='Rapport statistiques SGHL',
        subtitle=f"Généré le {_fmt_date(timezone.now())}",
        sections=[
            ('Synthèse', resume),
            ('Activité journalière', activite),
            ('Admissions par service', services),
            ('Rendez-vous par statut', rdv_statuts),
            ('Factures par statut', factures_statuts),
            ('Prescriptions par statut', prescriptions_statuts),
        ],
        signature={
            'nom': f"{demandeur.first_name} {demandeur.last_name}".strip() or demandeur.username,
            'role': demandeur.get_role_display() if hasattr(demandeur, 'get_role_display') else getattr(demandeur, 'role', 'Utilisateur'),
            'date': timezone.now(),
            'doc_ref': f"STAT-{rapport['date_debut']:%Y%m%d}-{rapport['date_fin']:%Y%m%d}",
            'empreinte': f"STAT-{rapport['date_debut']:%Y%m%d}-{rapport['date_fin']:%Y%m%d}",
        },
    )
