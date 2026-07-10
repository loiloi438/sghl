from datetime import date

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.mfa_service import generate_secret
from accounts.models import Role, User
from documents.services import obtenir_pdf_labo, obtenir_pdf_ordonnance, obtenir_pdf_facture
from facturation.services import generer_facture, valider_facture
from logistics.models import Batiment, Chambre, Lit, Service
from notifications.models import NotificationInbox
from patients.models import Patient, Sexe
from prescriptions.services import ajouter_ligne, creer_prescription, valider_prescription
from hospitalisation.services import admettre_patient


class Command(BaseCommand):
    help = 'Crée des données de démonstration (logistique + patient test).'

    def handle(self, *args, **options):
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

        medecin, created_med = User.objects.get_or_create(
            username='medecin',
            defaults={
                'email': 'medecin@sghl.local',
                'role': Role.MEDECIN,
                'first_name': 'Jean',
                'last_name': 'Okemba',
            },
        )
        if created_med:
            medecin.set_password('Medecin@SGHL2026')
            medecin.save()
            self.stdout.write(self.style.SUCCESS('Médecin créé : medecin / Medecin@SGHL2026'))

        medecin2, created_med2 = User.objects.get_or_create(
            username='medecin2',
            defaults={
                'email': 'medecin2@sghl.local',
                'role': Role.MEDECIN,
                'first_name': 'Nadia',
                'last_name': 'Mbemba',
            },
        )
        if created_med2:
            medecin2.set_password('Medecin@SGHL2026')
            medecin2.save()
            self.stdout.write(self.style.SUCCESS('Médecin créé : medecin2 / Medecin@SGHL2026'))

        medecin3, created_med3 = User.objects.get_or_create(
            username='medecin3',
            defaults={
                'email': 'medecin3@sghl.local',
                'role': Role.MEDECIN,
                'first_name': 'Olivier',
                'last_name': 'Kanza',
            },
        )
        if created_med3:
            medecin3.set_password('Medecin@SGHL2026')
            medecin3.save()
            self.stdout.write(self.style.SUCCESS('Médecin créé : medecin3 / Medecin@SGHL2026'))

        infirmier, created_inf = User.objects.get_or_create(
            username='infirmier',
            defaults={
                'email': 'infirmier@sghl.local',
                'role': Role.INFIRMIER,
                'first_name': 'Claire',
                'last_name': 'Mavoungou',
            },
        )
        if created_inf:
            infirmier.set_password('Infirmier@SGHL2026')
            infirmier.save()
            self.stdout.write(self.style.SUCCESS('Infirmier créé : infirmier / Infirmier@SGHL2026'))

        infirmier2, created_inf2 = User.objects.get_or_create(
            username='infirmier2',
            defaults={
                'email': 'infirmier2@sghl.local',
                'role': Role.INFIRMIER,
                'first_name': 'Sophie',
                'last_name': 'Banza',
            },
        )
        if created_inf2:
            infirmier2.set_password('Infirmier@SGHL2026')
            infirmier2.save()
            self.stdout.write(self.style.SUCCESS('Infirmier créé : infirmier2 / Infirmier@SGHL2026'))

        infirmier3, created_inf3 = User.objects.get_or_create(
            username='infirmier3',
            defaults={
                'email': 'infirmier3@sghl.local',
                'role': Role.INFIRMIER,
                'first_name': 'Jean-Pierre',
                'last_name': 'Oko',
            },
        )
        if created_inf3:
            infirmier3.set_password('Infirmier@SGHL2026')
            infirmier3.save()
            self.stdout.write(self.style.SUCCESS('Infirmier créé : infirmier3 / Infirmier@SGHL2026'))

        biologiste, created_bio = User.objects.get_or_create(
            username='biologiste',
            defaults={
                'email': 'biologiste@sghl.local',
                'role': Role.BIOLOGISTE,
                'first_name': 'Marie',
                'last_name': 'Nkounkou',
            },
        )
        if created_bio:
            biologiste.set_password('Biologiste@SGHL2026')
            biologiste.save()
            self.stdout.write(self.style.SUCCESS('Biologiste créé : biologiste / Biologiste@SGHL2026'))

        pharmacien, created_pharma = User.objects.get_or_create(
            username='pharmacien',
            defaults={
                'email': 'pharmacien@sghl.local',
                'role': Role.PHARMACIEN,
                'first_name': 'Paul',
                'last_name': 'Mabiala',
            },
        )
        if created_pharma:
            pharmacien.set_password('Pharmacien@SGHL2026')
            pharmacien.save()
            self.stdout.write(self.style.SUCCESS('Pharmacien créé : pharmacien / Pharmacien@SGHL2026'))

        comptable, created_comptable = User.objects.get_or_create(
            username='comptable',
            defaults={
                'email': 'comptable@sghl.local',
                'role': Role.COMPTABLE,
                'first_name': 'Sylvie',
                'last_name': 'Ngoma',
            },
        )
        if created_comptable:
            comptable.set_password('Comptable@SGHL2026')
            comptable.save()
            self.stdout.write(self.style.SUCCESS('Comptable créé : comptable / Comptable@SGHL2026'))

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
                'corps': 'Vous avez été affecté(e) à la prise en charge de P-2026-001 demain.',
                'categorie': 'Soins',
                'donnees': {'patient': 'P-2026-001', 'service': 'Médecine interne'},
                'lu': False,
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Infrastructure prête : {batiment.code}/{service.code} — Ch.{chambre.numero} Lit {lit.numero}'
            )
        )
