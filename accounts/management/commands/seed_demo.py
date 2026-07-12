from datetime import date

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from accounts.mfa_service import generate_secret
from accounts.models import Role, User
from core.env_utils import env_flag
from documents.services import obtenir_pdf_labo, obtenir_pdf_ordonnance, obtenir_pdf_facture
from facturation.services import generer_facture, valider_facture
from logistics.models import Batiment, Chambre, Lit, Service
from notifications.models import NotificationInbox
from patients.models import Patient, Sexe
from prescriptions.services import ajouter_ligne, creer_prescription, valider_prescription
from hospitalisation.services import admettre_patient


class Command(BaseCommand):
    help = 'Crée des données de démonstration (logistique + patient test).'

    STAFF_PASSWORDS = {
        Role.MEDECIN: 'Medecin@SGHL2026',
        Role.INFIRMIER: 'Infirmier@SGHL2026',
        Role.BIOLOGISTE: 'Biologiste@SGHL2026',
        Role.PHARMACIEN: 'Pharmacien@SGHL2026',
        Role.COMPTABLE: 'Comptable@SGHL2026',
        Role.SECRETAIRE: 'Secretaire@SGHL2026',
    }

    DEMO_MEDECINS = [
        ('medecin', 'Jean-Philippe', 'Martin', 'medecin@sghl.local'),
        ('medecin2', 'Nadia', 'Mbemba', 'nadia.mbemba@sghl.local'),
        ('medecin3', 'Olivier', 'Kanza', 'olivier.kanza@sghl.local'),
        ('medecin4', 'André', 'Moukoko', 'andre.moukoko@sghl.local'),
        ('medecin5', 'Sylvie', 'Ngouabi', 'sylvie.ngouabi@sghl.local'),
        ('medecin6', 'Patrick', 'Kimpwanza', 'patrick.kimpwanza@sghl.local'),
        ('medecin7', 'Élodie', 'Makaya', 'elodie.makaya@sghl.local'),
        ('medecin8', 'Bernard', 'Itoua', 'bernard.itoua@sghl.local'),
        ('medecin9', 'Carine', 'Loumou', 'carine.loumou@sghl.local'),
        ('medecin10', 'Fabrice', 'Ndongo', 'fabrice.ndongo@sghl.local'),
    ]

    DEMO_INFIRMIERS = [
        ('infirmier', 'Antoinette', 'Bouity', 'infirmier@sghl.local'),
        ('infirmier2', 'Sophie', 'Banza', 'sophie.banza@sghl.local'),
        ('infirmier3', 'Jean-Pierre', 'Oko', 'jeanpierre.oko@sghl.local'),
        ('infirmier4', 'Grace', 'Mavoungou', 'grace.mavoungou@sghl.local'),
        ('infirmier5', 'Christian', 'Loemba', 'christian.loemba@sghl.local'),
        ('infirmier6', 'Patricia', 'Nzouba', 'patricia.nzouba@sghl.local'),
        ('infirmier7', 'Rodrigue', 'Massamba', 'rodrigue.massamba@sghl.local'),
        ('infirmier8', 'Chantal', 'Bounkassa', 'chantal.bounkassa@sghl.local'),
        ('infirmier9', 'Serge', 'Makaya', 'serge.makaya@sghl.local'),
        ('infirmier10', 'Hortense', 'Mounguengui', 'hortense.mounguengui@sghl.local'),
    ]

    DEMO_BIOLOGISTES = [
        ('biologiste', 'Marie', 'Nkounkou', 'biologiste@sghl.local'),
        ('biologiste2', 'Joseph', 'Mboussi', 'joseph.mboussi@sghl.local'),
        ('biologiste3', 'Alice', 'Kombo', 'alice.kombo@sghl.local'),
    ]

    DEMO_PHARMACIENS = [
        ('pharmacien', 'Paul', 'Mabiala', 'pharmacien@sghl.local'),
        ('pharmacien2', 'Diane', 'Okoko', 'diane.okoko@sghl.local'),
        ('pharmacien3', 'Samuel', "N'Goma", 'samuel.ngoma@sghl.local'),
    ]

    DEMO_COMPTABLES = [
        ('comptable', 'Sylvie', 'Ngoma', 'comptable@sghl.local'),
        ('comptable2', 'Mélanie', 'Bakala', 'melanie.bakala@sghl.local'),
        ('comptable3', 'Roger', 'Itou', 'roger.itou@sghl.local'),
    ]

    DEMO_SECRETAIRES = [
        ('samantha', 'Samantha', 'Turner', 'galoisturner@gmail.com'),
    ]

    def _ensure_staff(self, role: str, entries: list[tuple[str, str, str, str]]) -> list[User]:
        password = self.STAFF_PASSWORDS[role]
        created_count = 0
        users: list[User] = []
        for username, first_name, last_name, email in entries:
            user, created = User.objects.update_or_create(
                username=username,
                defaults={
                    'email': email,
                    'role': role,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                    'mfa_enabled': True,
                },
            )
            if created:
                user.set_password(password)
                user.save()
                created_count += 1
            users.append(user)
        role_label = dict(Role.choices).get(role, role)
        self.stdout.write(
            self.style.SUCCESS(
                f'{len(entries)} {role_label.lower()}(s) démo — {created_count} créé(s), '
                f'{len(entries) - created_count} mis à jour.'
            )
        )
        return users

    def handle(self, *args, **options):
        if not settings.DEBUG and not env_flag('SGHL_SEED_DEMO'):
            raise CommandError(
                'seed_demo est désactivé en production. '
                'Définissez SGHL_SEED_DEMO=true uniquement pour un environnement de démonstration.'
            )

        batiment, _ = Batiment.objects.get_or_create(
            code='A',
            defaults={'nom': 'Bâtiment principal'},
        )
        service, _ = Service.objects.get_or_create(
            batiment=batiment,
            code='MED',
            defaults={'nom': 'Médecine interne'},
        )
        chambre, _ = Chambre.objects.get_or_create(
            service=service,
            numero='101',
        )
        lit, created_lit = Lit.objects.get_or_create(
            chambre=chambre,
            numero='1',
        )
        if created_lit:
            self.stdout.write(self.style.SUCCESS('Lit de démonstration créé (101/1).'))
        else:
            self.stdout.write('Lit de démonstration déjà présent.')

        patient, created_patient = Patient.objects.get_or_create(
            numero_dossier='P-2026-001',
            defaults={
                'nom': 'MOUANGA',
                'prenom': 'Patient',
                'date_naissance': date(1990, 5, 15),
                'sexe': Sexe.MASCULIN,
                'telephone': '+242060000000',
                'consentement_donnees': True,
            },
        )
        if created_patient:
            self.stdout.write(self.style.SUCCESS('Patient test créé : P-2026-001'))

        compte_patient, created_compte = User.objects.get_or_create(
            username='patient',
            defaults={
                'email': 'patient@sghl.local',
                'role': Role.PATIENT,
                'first_name': 'Patient',
                'last_name': 'MOUANGA',
            },
        )
        if created_compte:
            compte_patient.set_password('Patient@SGHL2026')
            compte_patient.save()
            self.stdout.write(self.style.SUCCESS('Compte patient : patient / Patient@SGHL2026'))

        if patient.compte_utilisateur_id != compte_patient.id:
            patient.compte_utilisateur = compte_patient
            patient.save(update_fields=['compte_utilisateur'])
            self.stdout.write(self.style.SUCCESS('Profil patient rattaché au compte mobile.'))

        medecins = self._ensure_staff(Role.MEDECIN, self.DEMO_MEDECINS)
        medecin = medecins[0]

        infirmiers = self._ensure_staff(Role.INFIRMIER, self.DEMO_INFIRMIERS)
        infirmier = infirmiers[0]

        biologistes = self._ensure_staff(Role.BIOLOGISTE, self.DEMO_BIOLOGISTES)
        biologiste = biologistes[0]

        self._ensure_staff(Role.PHARMACIEN, self.DEMO_PHARMACIENS)

        comptables = self._ensure_staff(Role.COMPTABLE, self.DEMO_COMPTABLES)
        comptable = comptables[0]

        secretaires = self._ensure_staff(Role.SECRETAIRE, self.DEMO_SECRETAIRES)
        secretaire = secretaires[0]

        staff_ready = User.objects.exclude(role=Role.PATIENT).update(
            mfa_enabled=True,
            is_active=True,
        )
        if staff_ready:
            self.stdout.write(
                self.style.SUCCESS(
                    f'{staff_ready} compte(s) personnel prêts (MFA e-mail activée, comptes actifs).'
                )
            )

        call_command('seed_cim10', verbosity=0)
        call_command('seed_analyses', verbosity=0)
        call_command('seed_medicaments', verbosity=0)
        call_command('seed_tarifs', verbosity=0)
        call_command('seed_rendezvous', verbosity=0)

        from hospitalisation.models import Hospitalisation, StatutHospitalisation

        hosp = Hospitalisation.objects.filter(
            patient=patient,
            statut=StatutHospitalisation.ACTIVE,
        ).first()
        if hosp is None:
            try:
                lit.refresh_from_db()
                hosp = admettre_patient(
                    patient=patient,
                    lit=lit,
                    motif_admission='Infection respiratoire',
                    lit_version=lit.version,
                )
                self.stdout.write(self.style.SUCCESS('Patient P-2026-001 admis (Ch.101 Lit 1).'))
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'Admission démo ignorée : {exc}'))
                hosp = None

        if hosp is not None and not hosp.prescriptions.filter(statut='validee').exists():
            prescription = creer_prescription(
                hospitalisation=hosp,
                medecin=medecin,
                observations='Repos et hydratation',
                codes_cim10=['J06.9'],
            )
            ajouter_ligne(
                prescription=prescription,
                medicament='Amoxicilline',
                posologie='500 mg x3/j',
                duree_traitement='7 jours',
            )
            valider_prescription(
                prescription=prescription,
                medecin=medecin,
                version=prescription.version,
            )
            self.stdout.write(self.style.SUCCESS('Prescription validée de démonstration créée.'))
            try:
                obtenir_pdf_ordonnance(prescription=prescription, demandeur=medecin)
                self.stdout.write(self.style.SUCCESS('Ordonnance PDF de démonstration générée.'))
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'Ordonnance PDF non générée : {exc}'))

        if hosp is not None and not hosp.prescriptions.filter(statut='brouillon').exists():
            creer_prescription(
                hospitalisation=hosp,
                medecin=medecin,
                observations='Contrôle post-traitement — à valider',
                codes_cim10=['J06.9'],
            )
            self.stdout.write(self.style.SUCCESS('Prescription brouillon de démonstration créée.'))

        from laboratoire.models import CommandeAnalyse, StatutCommandeAnalyse
        from laboratoire.services import (
            creer_commande,
            enregistrer_affectation,
            enregistrer_prelevement,
            publier_commande,
            saisir_resultats,
            valider_commande,
        )

        if hosp is not None and not CommandeAnalyse.objects.filter(
            hospitalisation=hosp,
            statut=StatutCommandeAnalyse.PUBLIEE,
        ).exists():
            commande = creer_commande(
                hospitalisation=hosp,
                medecin=medecin,
                codes_analyses=['NFS', 'GLY'],
                observations='Bilan infectieux',
            )
            enregistrer_prelevement(
                commande=commande,
                preleveur=medecin,
                type_echantillon='Sang veineux',
                reference_echantillon='DEMO-LAB-001',
            )
            commande.refresh_from_db()
            enregistrer_affectation(
                commande=commande,
                affectee_a=biologiste,
                affectee_par=biologiste,
            )
            commande.refresh_from_db()
            lignes = list(commande.lignes.all())
            saisir_resultats(
                commande=commande,
                saisi_par=biologiste,
                resultats=[
                    {'ligne_id': lignes[0].id, 'valeur': 'Normal', 'unite': ''},
                    {'ligne_id': lignes[1].id, 'valeur': '0,92', 'unite': 'g/L'},
                ],
            )
            commande.refresh_from_db()
            valider_commande(
                commande=commande,
                biologiste=biologiste,
                version=commande.version,
            )
            commande.refresh_from_db()
            publier_commande(
                commande=commande,
                biologiste=biologiste,
                version=commande.version,
            )
            self.stdout.write(self.style.SUCCESS('Commande labo publiée de démonstration créée.'))
            try:
                obtenir_pdf_labo(commande=commande, demandeur=biologiste)
                self.stdout.write(self.style.SUCCESS('Compte-rendu labo PDF généré.'))
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f'Compte-rendu labo PDF non généré : {exc}'))

        if hosp is not None:
            from facturation.models import Facture, StatutFacture

            facture = Facture.objects.filter(hospitalisation=hosp).first()
            if facture is not None and facture.statut != StatutFacture.BROUILLON:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Facture démo existante : {facture.numero_facture} ({facture.statut})'
                    )
                )
            else:
                try:
                    facture = generer_facture(hospitalisation=hosp, comptable=comptable)
                    facture = valider_facture(facture=facture, comptable=comptable, version=facture.version)
                    self.stdout.write(self.style.SUCCESS(f'Facture démo validée : {facture.numero_facture}'))
                    obtenir_pdf_facture(facture=facture, demandeur=comptable)
                    self.stdout.write(self.style.SUCCESS('Facture PDF de démonstration générée.'))
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(f'Facture de démonstration non générée : {exc}'))

        NotificationInbox.objects.get_or_create(
            utilisateur=medecin,
            titre='Rendez-vous patient confirmé',
            defaults={
                'corps': 'Un nouveau rendez-vous a été confirmé pour le patient P-2026-001.',
                'categorie': 'Rendez-vous',
                'donnees': {'patient': 'P-2026-001', 'type': 'rdv'},
                'lu': False,
            },
        )

        NotificationInbox.objects.get_or_create(
            utilisateur=infirmier,
            titre='Nouvelle affectation de soins',
            defaults={
                'corps': 'Vous avez été affectée à la prise en charge de P-2026-001 demain.',
                'categorie': 'Soins',
                'donnees': {'patient': 'P-2026-001', 'service': 'Médecine interne'},
                'lu': False,
            },
        )

        NotificationInbox.objects.get_or_create(
            utilisateur=medecin,
            titre='Alerte médicale — constantes',
            defaults={
                'corps': 'Patient P-2026-001 : fièvre 38,2°C. Surveillance renforcée recommandée.',
                'categorie': 'Alerte médicale',
                'donnees': {'patient': 'P-2026-001', 'niveau': 'urgent'},
                'lu': False,
            },
        )

        NotificationInbox.objects.get_or_create(
            utilisateur=compte_patient,
            titre='Rappel de rendez-vous',
            defaults={
                'corps': 'Votre rendez-vous avec le Dr Jean-Philippe Martin est prévu demain à 10h00.',
                'categorie': 'Rendez-vous',
                'donnees': {'type': 'rappel', 'medecin': 'Jean-Philippe Martin'},
                'lu': False,
            },
        )

        from messagerie.models import MessageInterne

        MessageInterne.objects.get_or_create(
            expediteur=compte_patient,
            destinataire=secretaire,
            sujet='Question facture hospitalisation',
            defaults={
                'corps': 'Bonjour, pourriez-vous m’indiquer le montant restant sur ma dernière facture ?',
                'lu': False,
            },
        )
        MessageInterne.objects.get_or_create(
            expediteur=secretaire,
            destinataire=compte_patient,
            sujet='Réponse secrétariat — facture',
            defaults={
                'corps': 'Bonjour, votre facture P-2026-001 est validée. Le solde sera visible dans votre espace patient.',
                'lu': False,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Infrastructure prête : {batiment.code}/{service.code} — Ch.{chambre.numero} Lit {lit.numero}'
            )
        )
